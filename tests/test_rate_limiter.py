import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.rate_limiter import RateLimiterMiddleware

def test_rate_limiter_middleware():
    app = FastAPI()
    app.add_middleware(RateLimiterMiddleware, max_requests=3, window_seconds=2)

    @app.get("/test")
    def test_route():
        return {"status": "ok"}

    @app.get("/health")
    def health_route():
        return {"status": "ok"}

    client = TestClient(app)

    # First 3 requests should succeed
    for _ in range(3):
        res = client.get("/test")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}
        assert res.headers["X-RateLimit-Limit"] == "3"
        assert int(res.headers["X-RateLimit-Remaining"]) >= 0

    # 4th request should trigger rate limit (429)
    res = client.get("/test")
    assert res.status_code == 429
    assert res.json() == {"detail": "Rate limit exceeded. Please try again later."}

    # Exempt path /health should still work
    res = client.get("/health")
    assert res.status_code == 200


def test_role_based_rate_limiting(monkeypatch):
    # Override settings for rate limit tiers
    from app.config import settings
    monkeypatch.setattr(settings, "RATE_LIMIT_MAX_REQUESTS", 2)
    monkeypatch.setattr(settings, "RATE_LIMIT_PREMIUM_MAX_REQUESTS", 4)
    monkeypatch.setattr(settings, "RATE_LIMIT_ADMIN_MAX_REQUESTS", 6)
    
    app = FastAPI()
    app.add_middleware(
        RateLimiterMiddleware, 
        max_requests=2, 
        window_seconds=10
    )

    @app.get("/test")
    def test_route():
        return {"status": "ok"}

    from app.auth import create_access_token
    std_token = create_access_token({"sub": "std_user", "role": "standard"})
    prem_token = create_access_token({"sub": "prem_user", "role": "premium"})
    admin_token = create_access_token({"sub": "admin_user", "role": "admin"})

    client = TestClient(app)

    # 1. Standard user limit (limit 2)
    headers = {"Authorization": f"Bearer {std_token}"}
    for _ in range(2):
        res = client.get("/test", headers=headers)
        assert res.status_code == 200
        assert res.headers["X-RateLimit-Limit"] == "2"
    
    res = client.get("/test", headers=headers)
    assert res.status_code == 429

    # 2. Premium user limit (limit 4)
    headers = {"Authorization": f"Bearer {prem_token}"}
    for _ in range(4):
        res = client.get("/test", headers=headers)
        assert res.status_code == 200
        assert res.headers["X-RateLimit-Limit"] == "4"
    
    res = client.get("/test", headers=headers)
    assert res.status_code == 429

    # 3. Admin user limit (limit 6)
    headers = {"Authorization": f"Bearer {admin_token}"}
    for _ in range(6):
        res = client.get("/test", headers=headers)
        assert res.status_code == 200
        assert res.headers["X-RateLimit-Limit"] == "6"
    
    res = client.get("/test", headers=headers)
    assert res.status_code == 429
