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
