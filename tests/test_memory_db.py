import pytest
from app.models import ExtractedFact
from app.memory_db import MemoryDB

def test_store_and_get_active_fact(db_session):
    mdb = MemoryDB(db_session)
    fact = ExtractedFact(
        entity_type="self",
        entity_id="self",
        property_name="employer",
        value_raw="Google Inc",
        confidence=0.9
    )
    
    # Store
    mem = mdb.store_fact("user1", fact, "employer", "Google")
    assert mem.id is not None
    assert mem.user_id == "user1"
    assert mem.canonical_property == "employer"
    assert mem.value_canonical == "Google"
    assert mem.status == "active"
    assert mem.version == 1

    # Get active
    active = mdb.get_active_fact("user1", "employer")
    assert active is not None
    assert active.id == mem.id
    assert active.value_canonical == "Google"

def test_retrieve_nonexistent_fact(db_session):
    mdb = MemoryDB(db_session)
    active = mdb.get_active_fact("user1", "nonexistent")
    assert active is None

def test_supersede_and_history(db_session):
    mdb = MemoryDB(db_session)
    
    # Store Google
    fact1 = ExtractedFact(property_name="employer", value_raw="Google")
    mem1 = mdb.store_fact("user1", fact1, "employer", "Google")
    
    # Store Meta (version 2)
    fact2 = ExtractedFact(property_name="employer", value_raw="Meta")
    mem2 = mdb.store_fact("user1", fact2, "employer", "Meta")
    
    assert mem2.version == 2
    
    # Update first to superseded
    mdb.update_fact_status(mem1.id, "superseded")
    
    active = mdb.get_active_fact("user1", "employer")
    assert active.value_canonical == "Meta"
    assert active.status == "active"
    
    history = mdb.get_fact_history("user1", "employer")
    assert len(history) == 2
    assert history[0].value_canonical == "Meta"
    assert history[1].value_canonical == "Google"

def test_multi_user_isolation(db_session):
    mdb = MemoryDB(db_session)
    
    fact1 = ExtractedFact(property_name="city", value_raw="San Francisco")
    mdb.store_fact("user1", fact1, "city", "San Francisco")
    
    fact2 = ExtractedFact(property_name="city", value_raw="New York")
    mdb.store_fact("user2", fact2, "city", "New York")
    
    act1 = mdb.get_active_fact("user1", "city")
    act2 = mdb.get_active_fact("user2", "city")
    
    assert act1.value_canonical == "San Francisco"
    assert act2.value_canonical == "New York"
