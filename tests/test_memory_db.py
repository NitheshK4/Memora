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

def test_get_active_memories_count(db_session):
    mdb = MemoryDB(db_session)
    assert mdb.get_active_memories_count("user3") == 0
    
    fact1 = ExtractedFact(property_name="city", value_raw="San Francisco")
    mdb.store_fact("user3", fact1, "city", "San Francisco")
    assert mdb.get_active_memories_count("user3") == 1
    
    fact2 = ExtractedFact(property_name="employer", value_raw="Google")
    mdb.store_fact("user3", fact2, "employer", "Google")
    assert mdb.get_active_memories_count("user3") == 2
    
    # Store another fact as non-active (e.g. superseded)
    fact3 = ExtractedFact(property_name="employer", value_raw="Meta")
    mem3 = mdb.store_fact("user3", fact3, "employer", "Meta", status="superseded")
    assert mdb.get_active_memories_count("user3") == 2

def test_get_user_memories_by_status(db_session):
    mdb = MemoryDB(db_session)
    user = "status_user"
    
    fact1 = ExtractedFact(property_name="city", value_raw="SF")
    mdb.store_fact(user, fact1, "city", "San Francisco", status="active")
    
    fact2 = ExtractedFact(property_name="employer", value_raw="Google")
    mdb.store_fact(user, fact2, "employer", "Google", status="superseded")
    
    fact3 = ExtractedFact(property_name="birthday", value_raw="July 15")
    mdb.store_fact(user, fact3, "birthday", "July 15", status="disputed")
    
    active_mems = mdb.get_user_memories_by_status(user, "active")
    assert len(active_mems) == 1
    assert active_mems[0].canonical_property == "city"
    
    superseded_mems = mdb.get_user_memories_by_status(user, "superseded")
    assert len(superseded_mems) == 1
    assert superseded_mems[0].canonical_property == "employer"
    
    disputed_mems = mdb.get_user_memories_by_status(user, "disputed")
    assert len(disputed_mems) == 1
    assert disputed_mems[0].canonical_property == "birthday"
    
    all_mems = mdb.get_user_memories_by_status(user, "all")
    assert len(all_mems) == 3

def test_get_user_memories_pagination_sorting(db_session):
    mdb = MemoryDB(db_session)
    user = "paginate_user"
    
    fact1 = ExtractedFact(property_name="city", value_raw="SF")
    mdb.store_fact(user, fact1, "city", "San Francisco", status="active")
    
    # Sleep/wait is not strictly needed if we just verify by values/sorting
    fact2 = ExtractedFact(property_name="employer", value_raw="Google")
    mdb.store_fact(user, fact2, "employer", "Google", status="active")
    
    # Test limit and offset
    mems_limit = mdb.get_user_memories_by_status(user, "active", limit=1)
    assert len(mems_limit) == 1
    
    # Test sorting by canonical_property ascending
    mems_asc = mdb.get_user_memories_by_status(user, "active", sort_by="canonical_property", sort_order="asc")
    assert len(mems_asc) == 2
    assert mems_asc[0].canonical_property == "city"
    assert mems_asc[1].canonical_property == "employer"
    
    # Test sorting by canonical_property descending
    mems_desc = mdb.get_user_memories_by_status(user, "active", sort_by="canonical_property", sort_order="desc")
    assert len(mems_desc) == 2
    assert mems_desc[0].canonical_property == "employer"
    assert mems_desc[1].canonical_property == "city"


