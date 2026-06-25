import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.config import settings
from app.models import (
    ExtractedFact, ConflictInfo, ValidationResult, ResolutionAction, 
    DB_Memory, DB_AuditEvent, ChatResponse, MemorySnapshot, AuditEventSchema
)
from app.memory_db import MemoryDB
from app.graph_store import GraphStore
from app.extractor import extractor
from app.normalizer import normalize_fact
from app.conflict_detector import conflict_detector
from app.resolver import resolver
from app.validator import validator
import requests
from app.utils import logger

class MemoryAgent:
    def __init__(self, db: Session):
        self.db = db
        self.memory_db = MemoryDB(db)
        self.graph_store = GraphStore(db)

    def process_message(self, user_id: str, message: str, session_id: str = "session_default") -> ChatResponse:
        is_question = self._is_question(message)
        
        extracted_facts: List[ExtractedFact] = []
        conflicts_detected: List[ConflictInfo] = []
        new_audit_logs: List[DB_AuditEvent] = []
        recent_updates: List[str] = []
        dispute_alerts: List[str] = []

        # Get all active memories
        active_memories = self.memory_db.get_user_profile(user_id)

        # 1. Create default user self-node in the graph
        user_node = self.graph_store.get_or_create_entity(user_id, "self", user_id)

        # 2. Extract facts if statement
        if not is_question:
            extracted_facts = extractor.extract_facts(message)
            
            for fact in extracted_facts:
                if not fact.source_text:
                    fact.source_text = message

                # Canonicalize
                canonical_prop, canonical_val = normalize_fact(fact.property_name, fact.value_raw)
                
                # Validate
                val_result = validator.validate_fact(fact, canonical_prop, canonical_val)
                if not val_result.is_valid:
                    evt = self.memory_db.record_audit_event(
                        user_id=user_id,
                        memory_id=None,
                        event_type="rejected",
                        new_value=fact.value_raw,
                        reason=f"Validation failed: {val_result.reason}",
                        resolver_type="validator"
                    )
                    new_audit_logs.append(evt)
                    recent_updates.append(f"Rejected invalid fact for '{canonical_prop}' ('{fact.value_raw}'): {val_result.reason}")
                    continue

                # Graph node/edge routing resolution
                db_entity_id = user_node.id
                db_relationship_id = None
                
                # If the fact describes an edge (e.g. employer, city, dog_name), create target node and link
                if canonical_prop == "employer":
                    org_node = self.graph_store.get_or_create_entity(user_id, "organization", canonical_val)
                    rel = self.graph_store.get_or_create_relationship(user_id, user_node.id, org_node.id, "works_at")
                    db_relationship_id = rel.id
                elif canonical_prop == "city":
                    loc_node = self.graph_store.get_or_create_entity(user_id, "location", canonical_val)
                    rel = self.graph_store.get_or_create_relationship(user_id, user_node.id, loc_node.id, "lives_in")
                    db_relationship_id = rel.id
                elif canonical_prop == "dog_name":
                    pet_node = self.graph_store.get_or_create_entity(user_id, "pet", canonical_val)
                    rel = self.graph_store.get_or_create_relationship(user_id, user_node.id, pet_node.id, "has_pet")
                    db_relationship_id = rel.id
                
                # Conflict detection on the resolved graph context level
                conflicts = conflict_detector.detect_conflicts(
                    fact, canonical_prop, canonical_val, active_memories,
                    db_entity_id=db_entity_id, db_relationship_id=db_relationship_id
                )
                
                if not conflicts:
                    # No conflict, store new active fact
                    existing_exact = [
                        m for m in active_memories 
                        if m.canonical_property == canonical_prop 
                        and m.value_canonical.lower() == canonical_val.lower()
                    ]
                    if existing_exact:
                        continue

                    db_memory = self.memory_db.store_fact(
                        user_id=user_id,
                        fact=fact,
                        canonical_property=canonical_prop,
                        value_canonical=canonical_val,
                        status="active",
                        validation_status="valid",
                        session_id=session_id,
                        db_entity_id=db_entity_id,
                        db_relationship_id=db_relationship_id
                    )
                    evt = self.memory_db.record_audit_event(
                        user_id=user_id,
                        memory_id=db_memory.id,
                        event_type="created",
                        new_value=canonical_val,
                        reason="Stored new graph fact.",
                        resolver_type="rules"
                    )
                    new_audit_logs.append(evt)
                    recent_updates.append(f"Remembered that your {canonical_prop.replace('_', ' ')} is {canonical_val}.")
                else:
                    # Conflict found!
                    for conflict in conflicts:
                        conflicts_detected.append(conflict)
                        resolution = resolver.resolve(conflict)
                        
                        existing_mem = self.db.query(DB_Memory).filter(DB_Memory.id == conflict.existing_memory_id).first()
                        
                        if resolution.action == "replace":
                            # Supersede old
                            self.memory_db.update_fact_status(
                                memory_id=existing_mem.id,
                                status="superseded",
                                resolution_note=resolution.reason
                            )
                            # Record audit
                            evt_super = self.memory_db.record_audit_event(
                                user_id=user_id,
                                memory_id=existing_mem.id,
                                event_type="superseded",
                                previous_value=existing_mem.value_canonical,
                                new_value=canonical_val,
                                reason=resolution.reason,
                                resolver_type=resolution.resolver_type
                            )
                            new_audit_logs.append(evt_super)
                            
                            # Store new active
                            db_memory = self.memory_db.store_fact(
                                user_id=user_id,
                                fact=fact,
                                canonical_property=canonical_prop,
                                value_canonical=canonical_val,
                                status="active",
                                session_id=session_id,
                                resolution_note=resolution.reason,
                                db_entity_id=db_entity_id,
                                db_relationship_id=db_relationship_id
                            )
                            evt_new = self.memory_db.record_audit_event(
                                user_id=user_id,
                                memory_id=db_memory.id,
                                event_type="created",
                                previous_value=existing_mem.value_canonical,
                                new_value=canonical_val,
                                reason=f"Replaced old graph fact. {resolution.reason}",
                                resolver_type=resolution.resolver_type
                            )
                            new_audit_logs.append(evt_new)
                            
                            # Mark old relationship as superseded in graph if relationship existed
                            if existing_mem.relationship_id:
                                from app.models import DB_Relationship
                                old_rel = self.db.query(DB_Relationship).filter(DB_Relationship.id == existing_mem.relationship_id).first()
                                if old_rel:
                                    old_rel.status = "superseded"
                                    self.db.commit()

                            recent_updates.append(f"Updated your {canonical_prop.replace('_', ' ')} from {existing_mem.value_canonical} to {canonical_val}.")
                            
                        elif resolution.action == "dispute":
                            # Store disputed fact
                            db_memory = self.memory_db.store_fact(
                                user_id=user_id,
                                fact=fact,
                                canonical_property=canonical_prop,
                                value_canonical=canonical_val,
                                status="disputed",
                                session_id=session_id,
                                resolution_note=resolution.reason,
                                db_entity_id=db_entity_id,
                                db_relationship_id=db_relationship_id
                            )
                            evt_disp = self.memory_db.record_audit_event(
                                user_id=user_id,
                                memory_id=db_memory.id,
                                event_type="disputed",
                                previous_value=existing_mem.value_canonical,
                                new_value=canonical_val,
                                reason=resolution.reason,
                                resolver_type=resolution.resolver_type
                            )
                            new_audit_logs.append(evt_disp)
                            
                            # Mark dispute status in relationship if relationship exists
                            if db_relationship_id:
                                from app.models import DB_Relationship
                                new_rel = self.db.query(DB_Relationship).filter(DB_Relationship.id == db_relationship_id).first()
                                if new_rel:
                                    new_rel.status = "disputed"
                                    self.db.commit()

                            dispute_alerts.append(f"Conflict on '{canonical_prop.replace('_', ' ')}': I have '{existing_mem.value_canonical}' but you said '{fact.value_raw}'.")
        
        # Load profile and return ChatResponse
        updated_active_memories = self.memory_db.get_user_profile(user_id)
        all_snapshots = [MemorySnapshot.model_validate(m) for m in self.db.query(DB_Memory).filter(DB_Memory.user_id == user_id).all()]
        
        response_text = self._generate_agent_response(
            message, is_question, updated_active_memories, all_snapshots, recent_updates, dispute_alerts
        )

        return ChatResponse(
            response=response_text,
            extracted_facts=extracted_facts,
            conflicts_detected=conflicts_detected,
            audit_logs=[AuditEventSchema.model_validate(e) for e in new_audit_logs],
            active_memories=[MemorySnapshot.model_validate(m) for m in updated_active_memories]
        )

    def _is_question(self, text: str) -> bool:
        cleaned = text.strip().lower()
        if cleaned.endswith("?"):
            return True
        question_words = ["what", "when", "where", "who", "why", "how", "do you know", "tell me"]
        return any(cleaned.startswith(w) for w in question_words)

    def _generate_agent_response(
        self, 
        message: str, 
        is_question: bool, 
        active_memories: List[DB_Memory], 
        all_memories: List[MemorySnapshot],
        recent_updates: List[str],
        dispute_alerts: List[str]
    ) -> str:
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
            try:
                return self._generate_llm_response(message, active_memories, all_memories, recent_updates, dispute_alerts)
            except Exception as e:
                logger.warning("LLM response generation failed, falling back to rules: %s", e)

        return self._generate_rules_response(message, is_question, active_memories, recent_updates, dispute_alerts)

    def _generate_llm_response(
        self, 
        message: str, 
        active_memories: List[DB_Memory], 
        all_memories: List[MemorySnapshot],
        recent_updates: List[str],
        dispute_alerts: List[str]
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }
        
        active_facts_str = "\n".join([f"- {m.canonical_property}: {m.value_canonical}" for m in active_memories])
        disputed_facts = [m for m in all_memories if m.status == "disputed"]
        disputed_str = "\n".join([f"- {m.canonical_property}: {m.value_canonical} (disputed)" for m in disputed_facts])
        
        system_prompt = (
            "You are a helpful AI assistant with a persistent memory graph. Answer the user based on their message and "
            "the provided active nodes/properties. Be natural, conversational, and direct.\n\n"
            f"Active Memories:\n{active_facts_str}\n\n"
            f"Disputed/Conflicting Memories:\n{disputed_str}\n\n"
            f"Recent Updates this session:\n{', '.join(recent_updates) if recent_updates else 'None'}\n"
            f"Disputes flagged this session:\n{', '.join(dispute_alerts) if dispute_alerts else 'None'}\n\n"
            "Guidelines:\n"
            "1. Answer using active memories. If not in memory, say you don't know.\n"
            "2. If there are active disputes related to their query, politely ask for clarification (e.g. 'Wait, I have conflicting records...').\n"
            "3. If facts were updated or added, briefly acknowledge them."
        )
        
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    def _generate_rules_response(
        self, 
        message: str, 
        is_question: bool, 
        active_memories: List[DB_Memory],
        recent_updates: List[str],
        dispute_alerts: List[str]
    ) -> str:
        mem_map = {m.canonical_property: m.value_canonical for m in active_memories}
        cleaned = message.lower()
        
        if is_question:
            if "birthday" in cleaned or "born" in cleaned:
                if "birthday" in mem_map:
                    return f"Your birthday is on {mem_map['birthday']}."
                return "I don't have your birthday on file. When is your birthday?"
                
            if "dog" in cleaned or "pet" in cleaned:
                if "dog_name" in mem_map:
                    return f"Your dog's name is {mem_map['dog_name']}."
                return "I don't know your dog's name. What is your dog's name?"
                
            if "work" in cleaned or "job" in cleaned or "employer" in cleaned or "company" in cleaned:
                if "employer" in mem_map:
                    return f"You work at {mem_map['employer']}."
                return "I don't have your employer stored. Where do you work?"
                
            if "live" in cleaned or "city" in cleaned or "location" in cleaned:
                if "city" in mem_map:
                    return f"You currently live in {mem_map['city']}."
                return "I don't know where you live. Which city do you live in?"
                
            if "name" in cleaned or "who am i" in cleaned:
                if "name" in mem_map:
                    return f"Your name is {mem_map['name']}."
                return "I don't know your name. What is your name?"

            if "hobby" in cleaned or "hobbies" in cleaned or "enjoy" in cleaned or "interest" in cleaned:
                hobbies = [m.value_canonical for m in active_memories if m.canonical_property == "hobby"]
                if hobbies:
                    return f"Based on my memories, your hobbies include: {', '.join(hobbies)}."
                return "I don't have any hobbies on file. What do you enjoy doing?"

            if "food" in cleaned or "like" in cleaned or "prefer" in cleaned or "hate" in cleaned:
                prefs = [m.value_canonical for m in active_memories if m.canonical_property == "preference"]
                if prefs:
                    return f"Based on my memories, you: {', '.join(prefs)}."
                return "I don't have any preferences on file. What foods do you like or hate?"

            return "I'm not sure about that. I only remember your name, birthday, dog's name, employer, city, hobbies, and food preferences."

        if dispute_alerts:
            alerts = []
            for alert in dispute_alerts:
                m_prop = re.search(r"on '([\w_]+)'", alert)
                prop = m_prop.group(1) if m_prop else "this"
                alerts.append(f"Wait, I have conflicting records for your {prop.replace('_', ' ')}. Could you clarify which one is correct?")
            return " ".join(alerts)
            
        if recent_updates:
            return "Got it! " + " ".join(recent_updates)
            
        return "I've noted that down!"
