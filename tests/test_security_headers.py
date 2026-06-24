import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.security_headers import SecurityHeadersMiddleware

def test_security_headers_middleware():
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/api/test")
    def api_route():
        return {"status": "ok"}

    @app.get("/docs")
    def docs_route():
        return {"status": "docs"}

    client = TestClient(app)

    # API request
    res = client.get("/api/test")
    assert res.status_code == 200
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["X-XSS-Protection"] == "1; mode=block"
    assert res.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in res.headers["Permissions-Policy"]
    assert res.headers["Cache-Control"] == "no-store, no-cache, must-revalidate"
    assert res.headers["Pragma"] == "no-cache"
    assert "max-age=31536000" in res.headers["Strict-Transport-Security"]

    # Docs request should not have cache-control: no-store, no-cache, must-revalidate or pragma: no-cache
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
    assert "Cache-Control" not in res_docs.headers or "no-store" not in res_docs.headers["Cache-Control"]
    assert "Pragma" not in res_docs.headers
