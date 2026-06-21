import pytest
from app.auth import hash_password, verify_password, create_access_token, verify_access_token
from app.models import DB_User
from app.graph_store import GraphStore
from app.reflection import reflection_engine

def test_password_hashing():
    pwd = "my-secure-password"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong-password", hashed) is False

def test_jwt_tokens():
    payload = {"sub": "test_user_jwt"}
    token = create_access_token(payload)
    assert token is not None
    
    verified = verify_access_token(token)
    assert verified is not None
    assert verified["sub"] == "test_user_jwt"

def test_graph_store_operations(db_session):
    gs = GraphStore(db_session)
    user_id = "test_graph_user"
    
    # Create nodes
    u_node = gs.get_or_create_entity(user_id, "self", user_id)
    org_node = gs.get_or_create_entity(user_id, "organization", "Google")
    
    assert u_node.id is not None
    assert org_node.name == "Google"
    
    # Create relationship
    rel = gs.get_or_create_relationship(user_id, u_node.id, org_node.id, "works_at")
    assert rel.id is not None
    assert rel.predicate == "works_at"
    
    # Check snapshot
    snap = gs.get_graph_snapshot(user_id)
    assert len(snap["nodes"]) == 2
    assert len(snap["edges"]) == 1
    assert snap["edges"][0]["label"] == "works_at"

def test_reflection_entity_merging(db_session):
    gs = GraphStore(db_session)
    user_id = "test_reflect_user"
    
    # Create duplicate entities
    u_node = gs.get_or_create_entity(user_id, "self", user_id)
    org1 = gs.get_or_create_entity(user_id, "organization", "Google Inc.")
    org2 = gs.get_or_create_entity(user_id, "organization", "Google")
    
    # Link them
    gs.get_or_create_relationship(user_id, u_node.id, org1.id, "works_at")
    gs.get_or_create_relationship(user_id, u_node.id, org2.id, "works_at")
    
    snap1 = gs.get_graph_snapshot(user_id)
    assert len(snap1["nodes"]) == 3
    
    # Run reflection engine node merging
    actions = reflection_engine.reflect_and_consolidate(user_id, db_session)
    assert len(actions) == 1
    assert "Merged duplicate entity" in actions[0]
    
    snap2 = gs.get_graph_snapshot(user_id)
    assert len(snap2["nodes"]) == 2 # "Google Inc." merged into "Google"
