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
