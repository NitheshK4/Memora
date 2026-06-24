from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import DB_Entity, DB_Relationship, DB_Memory
from datetime import datetime, timezone

class GraphStore:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_entity(self, user_id: str, entity_type: str, name: str) -> DB_Entity:
        entity = self.db.query(DB_Entity).filter(
            DB_Entity.user_id == user_id,
            DB_Entity.entity_type == entity_type.strip().lower(),
            DB_Entity.name == name.strip()
        ).first()
        
        if not entity:
            entity = DB_Entity(
                user_id=user_id,
                entity_type=entity_type.strip().lower(),
                name=name.strip(),
                created_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
        return entity

    def get_or_create_relationship(
        self, 
        user_id: str, 
        source_id: int, 
        target_id: int, 
        predicate: str
    ) -> DB_Relationship:
        rel = self.db.query(DB_Relationship).filter(
            DB_Relationship.user_id == user_id,
            DB_Relationship.source_entity_id == source_id,
            DB_Relationship.target_entity_id == target_id,
            DB_Relationship.predicate == predicate.strip().lower(),
            DB_Relationship.status == "active"
        ).first()
        
        if not rel:
            rel = DB_Relationship(
                user_id=user_id,
                source_entity_id=source_id,
                target_entity_id=target_id,
                predicate=predicate.strip().lower(),
                status="active",
                created_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            self.db.add(rel)
            self.db.commit()
            self.db.refresh(rel)
            
        return rel

    def get_graph_snapshot(self, user_id: str) -> Dict[str, Any]:
        """
        Compiles the current active graph database snapshot into nodes and edges formats
        for visualization libraries.
        """
        entities = self.db.query(DB_Entity).filter(DB_Entity.user_id == user_id).all()
        relationships = self.db.query(DB_Relationship).filter(
            DB_Relationship.user_id == user_id,
            DB_Relationship.status == "active"
        ).all()
        
        nodes = []
        for e in entities:
            # Gather properties for each entity
            properties = self.db.query(DB_Memory).filter(
                DB_Memory.entity_id == e.id,
                DB_Memory.status == "active"
            ).all()
            prop_dict = {p.canonical_property: p.value_canonical for p in properties}
            
            nodes.append({
                "id": e.id,
                "label": f"{e.name} ({e.entity_type})",
                "type": e.entity_type,
                "name": e.name,
                "properties": prop_dict
            })
            
        edges = []
        for r in relationships:
            edges.append({
                "id": r.id,
                "source": r.source_entity_id,
                "target": r.target_entity_id,
                "label": r.predicate
            })
            
        return {
            "nodes": nodes,
            "edges": edges
        }
