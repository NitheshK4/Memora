from datetime import datetime, timezone
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.models import DB_Memory, DB_AuditEvent, ExtractedFact
from app.embeddings import similarity_service
from app.utils import logger

class MemoryDB:
    def __init__(self, db: Session):
        self.db = db

    def store_fact(
        self,
        user_id: str,
        fact: ExtractedFact,
        canonical_property: str,
        value_canonical: str,
        status: str = "active",
        validation_status: str = "valid",
        resolution_note: Optional[str] = None,
        session_id: Optional[str] = None,
        db_entity_id: Optional[int] = None,
        db_relationship_id: Optional[int] = None
    ) -> DB_Memory:
        # Determine current version for this property
        latest_version = self.db.query(DB_Memory.version).filter(
            DB_Memory.user_id == user_id,
            DB_Memory.canonical_property == canonical_property,
            DB_Memory.entity_id == db_entity_id,
            DB_Memory.relationship_id == db_relationship_id
        ).order_by(desc(DB_Memory.version)).first()
        
        version = (latest_version[0] + 1) if latest_version else 1

        db_memory = DB_Memory(
            user_id=user_id,
            entity_id=db_entity_id,
            relationship_id=db_relationship_id,
            property_name=fact.property_name,
            canonical_property=canonical_property,
            value_raw=fact.value_raw,
            value_canonical=value_canonical,
            value_type="string",
            confidence=fact.confidence,
            source_text=fact.source_text,
            source_type="user_message",
            session_id=session_id,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            effective_from=datetime.now(timezone.utc).replace(tzinfo=None),
            effective_to=None,
            status=status,
            version=version,
            validation_status=validation_status,
            resolution_note=resolution_note
        )
        self.db.add(db_memory)
        self.db.commit()
        self.db.refresh(db_memory)

        # Sync to Vector Store
        try:
            from app.vector_store import vector_store
            vector_store.add_document(
                doc_id=db_memory.id,
                text=f"{canonical_property}: {value_canonical} ({fact.source_text or ''})",
                metadata={"user_id": user_id, "canonical_property": canonical_property}
            )
        except Exception as e:
            logger.warning("Failed to sync fact to vector store: %s", e)

        return db_memory

    def get_active_fact(
        self, 
        user_id: str, 
        canonical_property: str, 
        entity_id: Optional[int] = None
    ) -> Optional[DB_Memory]:
        return self.db.query(DB_Memory).filter(
            DB_Memory.user_id == user_id,
            DB_Memory.canonical_property == canonical_property,
            DB_Memory.entity_id == entity_id,
            DB_Memory.status == "active"
        ).first()

    def get_fact_history(self, user_id: str, canonical_property: str) -> List[DB_Memory]:
        return self.db.query(DB_Memory).filter(
            DB_Memory.user_id == user_id,
            DB_Memory.canonical_property == canonical_property
        ).order_by(desc(DB_Memory.version)).all()

    def get_related_facts(
        self, 
        user_id: str, 
        canonical_property: str, 
        entity_id: Optional[int] = None
    ) -> List[DB_Memory]:
        return self.db.query(DB_Memory).filter(
            DB_Memory.user_id == user_id,
            DB_Memory.canonical_property == canonical_property,
            DB_Memory.entity_id == entity_id
        ).all()

    def search_similar_facts(
        self, 
        user_id: str, 
        query: str, 
        threshold: float = 0.35
    ) -> List[DB_Memory]:
        active_facts = self.db.query(DB_Memory).filter(
            DB_Memory.user_id == user_id,
            DB_Memory.status == "active"
        ).all()
        
        results = []
        for fact in active_facts:
            sim_prop = similarity_service.calculate_similarity(query, fact.canonical_property)
            sim_val = similarity_service.calculate_similarity(query, fact.value_canonical)
            sim_src = similarity_service.calculate_similarity(query, fact.source_text or "")
            
            max_sim = max(sim_prop, sim_val, sim_src)
            if max_sim >= threshold:
                results.append((fact, max_sim))
                
        results.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in results]

    def get_user_profile(self, user_id: str) -> List[DB_Memory]:
        return self.db.query(DB_Memory).filter(
            DB_Memory.user_id == user_id,
            DB_Memory.status == "active"
        ).all()

    def update_fact_status(
        self,
        memory_id: int,
        status: str,
        validation_status: Optional[str] = None,
        resolution_note: Optional[str] = None,
        effective_to: Optional[datetime] = None
    ) -> Optional[DB_Memory]:
        memory = self.db.query(DB_Memory).filter(DB_Memory.id == memory_id).first()
        if memory:
            memory.status = status
            if validation_status:
                memory.validation_status = validation_status
            if resolution_note:
                memory.resolution_note = resolution_note
            if effective_to:
                memory.effective_to = effective_to
            elif status == "superseded" and not memory.effective_to:
                memory.effective_to = datetime.now(timezone.utc).replace(tzinfo=None)
                
            self.db.commit()
            self.db.refresh(memory)
        return memory

    def record_audit_event(
        self,
        user_id: str,
        memory_id: Optional[int],
        event_type: str,
        previous_value: Optional[str] = None,
        new_value: Optional[str] = None,
        reason: Optional[str] = None,
        resolver_type: Optional[str] = None
    ) -> DB_AuditEvent:
        db_event = DB_AuditEvent(
            user_id=user_id,
            memory_id=memory_id,
            event_type=event_type,
            previous_value=previous_value,
            new_value=new_value,
            reason=reason,
            resolver_type=resolver_type,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_audit_log(self, user_id: str) -> List[DB_AuditEvent]:
        return self.db.query(DB_AuditEvent).filter(
            DB_AuditEvent.user_id == user_id
        ).order_by(desc(DB_AuditEvent.created_at)).all()

    def clear_user_memory(self, user_id: str):
        self.record_audit_event(
            user_id=user_id,
            memory_id=None,
            event_type="cleared",
            reason="User explicitly requested clear memory"
        )
        self.db.query(DB_Memory).filter(DB_Memory.user_id == user_id).delete()
        from app.models import DB_Relationship, DB_Entity
        self.db.query(DB_Relationship).filter(DB_Relationship.user_id == user_id).delete()
        self.db.query(DB_Entity).filter(DB_Entity.user_id == user_id).delete()
        self.db.commit()

    def get_active_memories_count(self, user_id: str) -> int:
        """Returns the total number of active memories for a given user."""
        from sqlalchemy import func
        return self.db.query(func.count(DB_Memory.id)).filter(
            DB_Memory.user_id == user_id,
            DB_Memory.status == "active"
        ).scalar() or 0
