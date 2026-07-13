from fastapi.testclient import TestClient
from app.api import app

def test_api_health_check_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "memora-graph-api"
    assert data["database"] == "healthy"
    assert "uptime_seconds" in data
    assert "started_at" in data

def test_get_memories_filtering(db_session):
    from app.auth import get_current_user
    from app.db import get_db
    from app.memory_db import MemoryDB
    from app.models import ExtractedFact

    # Override get_current_user and get_db dependencies
    app.dependency_overrides[get_current_user] = lambda: "test_api_user"
    app.dependency_overrides[get_db] = lambda: db_session

    client = TestClient(app)
    
    # Store some memories using MemoryDB directly
    mdb = MemoryDB(db_session)
    fact_active = ExtractedFact(property_name="city", value_raw="San Francisco")
    mdb.store_fact("test_api_user", fact_active, "city", "San Francisco", status="active")

    fact_disputed = ExtractedFact(property_name="birthday", value_raw="July 15")
    mdb.store_fact("test_api_user", fact_disputed, "birthday", "July 15", status="disputed")
    
    # Query active (default status="active")
    resp = client.get("/memories")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["canonical_property"] == "city"
    assert data[0]["status"] == "active"
    
    # Query disputed
    resp = client.get("/memories?status=disputed")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["canonical_property"] == "birthday"
    assert data[0]["status"] == "disputed"

    # Query all
    resp = client.get("/memories?status=all")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2

    # Clean overrides
    app.dependency_overrides.clear()

