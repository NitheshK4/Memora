import requests
import json
from typing import List
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models import DB_Memory, DB_Entity, DB_Relationship, DB_AuditEvent
from app.config import settings
from app.memory_db import MemoryDB

class ReflectionEngine:
    def reflect_and_consolidate(self, user_id: str, db: Session) -> List[str]:
        """
        Runs a consolidation cycle for a user's memory graph.
        Returns a list of summary actions performed.
        """
        actions_performed = []
        
        # 1. Resolve Disputed facts if LLM is active
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
            resolved_disputes = self._consolidate_disputes(user_id, db)
            actions_performed.extend(resolved_disputes)
            
        # 2. Merge Duplicate entities (e.g. Google Inc & Google)
        merged_entities = self._merge_redundant_entities(user_id, db)
        actions_performed.extend(merged_entities)
        
        return actions_performed

    def _consolidate_disputes(self, user_id: str, db: Session) -> List[str]:
        actions = []
        memory_db = MemoryDB(db)
        
        # Find disputed memories
        disputed = db.query(DB_Memory).filter(
            DB_Memory.user_id == user_id,
            DB_Memory.status == "disputed"
        ).all()
        
        for disp in disputed:
            # Find the active counterpart
            active = db.query(DB_Memory).filter(
                DB_Memory.user_id == user_id,
                DB_Memory.canonical_property == disp.canonical_property,
                DB_Memory.entity_id == disp.entity_id,
                DB_Memory.status == "active"
            ).first()
            
            if not active:
                # If no active one, just activate the disputed one
                memory_db.update_fact_status(disp.id, "active", resolution_note="Activated disputed fact as no active counterpart existed.")
                memory_db.record_audit_event(
                    user_id=user_id,
                    memory_id=disp.id,
                    event_type="resolved",
                    new_value=disp.value_canonical,
                    reason="Activated disputed fact: no active counterpart existed.",
                    resolver_type="reflection"
                )
                actions.append(f"Activated disputed {disp.canonical_property} ({disp.value_canonical})")
                continue
                
            # Ask LLM to resolve the dispute based on metadata/timestamps or source text
            try:
                resolved_val = self._ask_llm_to_resolve_dispute(active, disp)
                if resolved_val == "active":
                    # Keep active, reject disputed
                    memory_db.update_fact_status(disp.id, "rejected", resolution_note="Rejected disputed fact during reflection consolidation.")
                    memory_db.record_audit_event(
                        user_id=user_id,
                        memory_id=disp.id,
                        event_type="rejected",
                        previous_value=disp.value_canonical,
                        reason="Dispute resolved in favor of active memory.",
                        resolver_type="reflection"
                    )
                    actions.append(f"Rejected disputed {disp.canonical_property} ({disp.value_canonical}) in favor of {active.value_canonical}")
                elif resolved_val == "disputed":
                    # Replace active with disputed
                    memory_db.update_fact_status(active.id, "superseded", resolution_note="Superseded by disputed fact during reflection consolidation.")
                    memory_db.record_audit_event(
                        user_id=user_id,
                        memory_id=active.id,
                        event_type="superseded",
                        previous_value=active.value_canonical,
                        new_value=disp.value_canonical,
                        reason="Active memory superseded by resolved disputed memory.",
                        resolver_type="reflection"
                    )
                    
                    memory_db.update_fact_status(disp.id, "active", resolution_note="Activated disputed memory after reflection consolidation.")
                    memory_db.record_audit_event(
                        user_id=user_id,
                        memory_id=disp.id,
                        event_type="resolved",
                        previous_value=active.value_canonical,
                        new_value=disp.value_canonical,
                        reason="Dispute resolved and activated.",
                        resolver_type="reflection"
                    )
                    actions.append(f"Replaced {disp.canonical_property} with disputed value ({disp.value_canonical})")
            except Exception as e:
                print(f"Reflection dispute resolution failed: {e}")
                
        return actions

    def _ask_llm_to_resolve_dispute(self, active: DB_Memory, disputed: DB_Memory) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }
        
        prompt = (
            "You are an agent memory optimizer. Resolve a dispute between two conflicting records:\n"
            f"Property: {active.canonical_property}\n"
            f"Record A (Active): Value='{active.value_canonical}', source_text='{active.source_text or ''}', date_recorded='{active.created_at}'\n"
            f"Record B (Disputed): Value='{disputed.value_canonical}', source_text='{disputed.source_text or ''}', date_recorded='{disputed.created_at}'\n"
            "\n"
            "Return a JSON object containing:\n"
            "- winner: 'active' (A is correct) or 'disputed' (B is correct)\n"
            "- justification: brief reasoning"
        )
        
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": prompt}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }
        
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
        res.raise_for_status()
        winner = res.json()["choices"][0]["message"]["content"]
        parsed = json.loads(winner)
        return parsed.get("winner", "active")

    def _merge_redundant_entities(self, user_id: str, db: Session) -> List[str]:
        actions = []
        entities = db.query(DB_Entity).filter(DB_Entity.user_id == user_id).all()
        
        # Simple clustering: merge entities of same type with very similar names
        # e.g., "Google Inc." and "Google"
        merged_set = set()
        
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                e1 = entities[i]
                e2 = entities[j]
                
                if e1.id in merged_set or e2.id in merged_set:
                    continue
                    
                if e1.entity_type == e2.entity_type:
                    n1 = e1.name.lower().replace(".", "").strip()
                    n2 = e2.name.lower().replace(".", "").strip()
                    
                    # If one name contains another and they are of length > 3
                    if (n1 in n2 or n2 in n1) and min(len(n1), len(n2)) > 3:
                        # Keep the shorter name or cleaner one
                        keep_entity = e1 if len(e1.name) <= len(e2.name) else e2
                        delete_entity = e2 if keep_entity == e1 else e1
                        
                        # Re-route all relationships of delete_entity to keep_entity
                        relationships = db.query(DB_Relationship).filter(
                            or_(
                                DB_Relationship.source_entity_id == delete_entity.id,
                                DB_Relationship.target_entity_id == delete_entity.id
                            )
                        ).all()
                        
                        for rel in relationships:
                            if rel.source_entity_id == delete_entity.id:
                                rel.source_entity_id = keep_entity.id
                            if rel.target_entity_id == delete_entity.id:
                                rel.target_entity_id = keep_entity.id
                                
                        # Re-route all memories linked to delete_entity to keep_entity
                        memories = db.query(DB_Memory).filter(DB_Memory.entity_id == delete_entity.id).all()
                        for mem in memories:
                            mem.entity_id = keep_entity.id
                            
                        db.delete(delete_entity)
                        db.commit()
                        
                        merged_set.add(delete_entity.id)
                        actions.append(f"Merged duplicate entity '{delete_entity.name}' into '{keep_entity.name}'")
                        
        return actions

reflection_engine = ReflectionEngine()
