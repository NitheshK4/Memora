import os
import sys
from datetime import datetime

# Adjust path to find app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import SessionLocal, engine, Base
from app.models import DB_User, DB_Entity, DB_Relationship, DB_Memory, DB_AuditEvent
from app.auth import hash_password

def seed():
    print("====================================================")
    print("            Seeding Memora Graph Database           ")
    print("====================================================")
    
    # Initialize tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(DB_User).filter(DB_User.username == "seed_user").first()
        if existing:
            print("Database already seeded with 'seed_user'. Skipping.")
            return

        print("1. Creating User 'seed_user'...")
        user = DB_User(
            username="seed_user",
            hashed_password=hash_password("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print("2. Creating Graph Nodes (Entities)...")
        # Nodes
        user_node = DB_Entity(user_id="seed_user", entity_type="self", name="seed_user")
        google_node = DB_Entity(user_id="seed_user", entity_type="organization", name="Google")
        meta_node = DB_Entity(user_id="seed_user", entity_type="organization", name="Meta")
        sf_node = DB_Entity(user_id="seed_user", entity_type="location", name="San Francisco")
        ny_node = DB_Entity(user_id="seed_user", entity_type="location", name="New York")
        dog_node = DB_Entity(user_id="seed_user", entity_type="pet", name="Max")
        
        db.add_all([user_node, google_node, meta_node, sf_node, ny_node, dog_node])
        db.commit()
        db.refresh(user_node)
        db.refresh(google_node)
        db.refresh(meta_node)
        db.refresh(sf_node)
        db.refresh(ny_node)
        db.refresh(dog_node)

        print("3. Creating Graph Edges (Relationships)...")
        # Relations
        # Scenario A: Works at Google (superseded) -> Works at Meta (active)
        rel_work_1 = DB_Relationship(user_id="seed_user", source_entity_id=user_node.id, target_entity_id=google_node.id, predicate="works_at", status="superseded")
        rel_work_2 = DB_Relationship(user_id="seed_user", source_entity_id=user_node.id, target_entity_id=meta_node.id, predicate="works_at", status="active")
        
        # Scenario A: Lives in SF (superseded) -> Lives in NY (active)
        rel_live_1 = DB_Relationship(user_id="seed_user", source_entity_id=user_node.id, target_entity_id=sf_node.id, predicate="lives_in", status="superseded")
        rel_live_2 = DB_Relationship(user_id="seed_user", source_entity_id=user_node.id, target_entity_id=ny_node.id, predicate="lives_in", status="active")
        
        # Scenario B: Has pet Max (active)
        rel_pet = DB_Relationship(user_id="seed_user", source_entity_id=user_node.id, target_entity_id=dog_node.id, predicate="has_pet", status="active")
        
        db.add_all([rel_work_1, rel_work_2, rel_live_1, rel_live_2, rel_pet])
        db.commit()
        db.refresh(rel_work_1)
        db.refresh(rel_work_2)
        db.refresh(rel_live_1)
        db.refresh(rel_live_2)
        db.refresh(rel_pet)

        print("4. Inserting Memory Node/Edge Properties (Facts)...")
        # Employer properties
        mem_emp_1 = DB_Memory(
            user_id="seed_user", relationship_id=rel_work_1.id, property_name="employer", 
            canonical_property="employer", value_raw="Google", value_canonical="Google", 
            status="superseded", version=1
        )
        mem_emp_2 = DB_Memory(
            user_id="seed_user", relationship_id=rel_work_2.id, property_name="employer", 
            canonical_property="employer", value_raw="Meta", value_canonical="Meta", 
            status="active", version=2
        )
        
        # City properties
        mem_city_1 = DB_Memory(
            user_id="seed_user", relationship_id=rel_live_1.id, property_name="city", 
            canonical_property="city", value_raw="San Francisco", value_canonical="San Francisco", 
            status="superseded", version=1
        )
        mem_city_2 = DB_Memory(
            user_id="seed_user", relationship_id=rel_live_2.id, property_name="city", 
            canonical_property="city", value_raw="New York", value_canonical="New York", 
            status="active", version=2
        )
        
        # Pet property
        mem_pet = DB_Memory(
            user_id="seed_user", relationship_id=rel_pet.id, property_name="dog_name", 
            canonical_property="dog_name", value_raw="Max", value_canonical="Max", 
            status="active", version=1
        )
        
        # Scenario C: Birthday (active) + Conflicting Birthday (disputed)
        mem_bday_1 = DB_Memory(
            user_id="seed_user", entity_id=user_node.id, property_name="birthday", 
            canonical_property="birthday", value_raw="July 15th", value_canonical="July 15", 
            status="active", version=1
        )
        mem_bday_2 = DB_Memory(
            user_id="seed_user", entity_id=user_node.id, property_name="birthday", 
            canonical_property="birthday", value_raw="July 20th", value_canonical="July 20", 
            status="disputed", version=2, resolution_note="Conflict detected with existing value July 15."
        )

        db.add_all([mem_emp_1, mem_emp_2, mem_city_1, mem_city_2, mem_pet, mem_bday_1, mem_bday_2])
        db.commit()

        print("5. Recording Audit Events...")
        audit_events = [
            DB_AuditEvent(user_id="seed_user", event_type="created", new_value="Google", reason="Seeded Google employer.", resolver_type="seeder"),
            DB_AuditEvent(user_id="seed_user", event_type="created", new_value="San Francisco", reason="Seeded SF location.", resolver_type="seeder"),
            DB_AuditEvent(user_id="seed_user", event_type="superseded", previous_value="Google", new_value="Meta", reason="Seeded Meta job relocation.", resolver_type="seeder"),
            DB_AuditEvent(user_id="seed_user", event_type="superseded", previous_value="San Francisco", new_value="New York", reason="Seeded NYC relocation.", resolver_type="seeder"),
            DB_AuditEvent(user_id="seed_user", event_type="disputed", previous_value="July 15", new_value="July 20", reason="Seeded birthday stable contradiction.", resolver_type="seeder")
        ]
        db.add_all(audit_events)
        db.commit()

        print("====================================================")
        print("          Database Seeded Successfully! (100%)       ")
        print("          Credentials: seed_user / password123      ")
        print("====================================================")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed()
