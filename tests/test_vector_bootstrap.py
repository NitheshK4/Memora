import pytest
from app.api import bootstrap_vector_store
from app.models import DB_Memory, ExtractedFact
from app.vector_store import vector_store
from app.memory_db import MemoryDB

def test_vector_bootstrap(db_session, monkeypatch):
    # 1. Add an active memory and a superseded memory to the database session
    mdb = MemoryDB(db_session)
    fact_active = ExtractedFact(property_name="city", value_raw="Berlin")
    mdb.store_fact("bootstrap_user", fact_active, "city", "Berlin", status="active")
    
    fact_super = ExtractedFact(property_name="city", value_raw="Munich")
    mdb.store_fact("bootstrap_user", fact_super, "city", "Munich", status="superseded")

    # 2. Clear any existing registry in the vector store, so that ONLY bootstrap_vector_store populates it
    vector_store.local_store.registry = []
    if hasattr(vector_store, "registry"):
        vector_store.registry = []
    
    # 3. Patch `get_db` in `app.api` to return our test database session
    def mock_get_db():
        yield db_session
        
    monkeypatch.setattr("app.api.get_db", mock_get_db)
    
    # 4. Trigger bootstrap
    bootstrap_vector_store()
    
    # 5. Check if the active memory is present in the vector store
    results = vector_store.search("Berlin", "bootstrap_user")
    assert len(results) > 0
    
    # Check that superseded one is NOT in the vector store
    results_super = vector_store.search("Munich", "bootstrap_user")
    assert len(results_super) == 0
