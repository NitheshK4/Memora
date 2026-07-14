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

def test_export_graph_json(db_session):
    from app.auth import get_current_user
    from app.db import get_db
    from app.memory_db import MemoryDB
    from app.models import ExtractedFact
    from app.graph_store import GraphStore

    app.dependency_overrides[get_current_user] = lambda: "test_export_user"
    app.dependency_overrides[get_db] = lambda: db_session

    client = TestClient(app)
    
    # Pre-populate some facts and entities to build the graph
    gs = GraphStore(db_session)
    user_node = gs.get_or_create_entity("test_export_user", "self", "test_export_user")
    
    mdb = MemoryDB(db_session)
    fact = ExtractedFact(property_name="employer", value_raw="Google")
    mdb.store_fact("test_export_user", fact, "employer", "Google", status="active", db_entity_id=user_node.id)

    resp = client.get("/graph/export")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0

    app.dependency_overrides.clear()

def test_export_graph_rdf(db_session):
    from app.auth import get_current_user
    from app.db import get_db
    from app.memory_db import MemoryDB
    from app.models import ExtractedFact
    from app.graph_store import GraphStore

    app.dependency_overrides[get_current_user] = lambda: "test_export_user"
    app.dependency_overrides[get_db] = lambda: db_session

    client = TestClient(app)
    
    gs = GraphStore(db_session)
    user_node = gs.get_or_create_entity("test_export_user", "self", "test_export_user")
    org_node = gs.get_or_create_entity("test_export_user", "organization", "Google")
    gs.get_or_create_relationship("test_export_user", user_node.id, org_node.id, "works_at")
    
    mdb = MemoryDB(db_session)
    fact = ExtractedFact(property_name="employer", value_raw="Google")
    mdb.store_fact("test_export_user", fact, "employer", "Google", status="active", db_entity_id=user_node.id)

    resp = client.get("/graph/export?format=rdf")
    assert resp.status_code == 200
    assert "text/turtle" in resp.headers["content-type"]
    text = resp.text
    assert "@prefix memora:" in text
    assert "memora:entity_" in text
    assert "works_at" in text

    app.dependency_overrides.clear()



