"""
Security headers middleware for FastAPI.

Adds OWASP-recommended HTTP security headers to every response
to harden the application against common web vulnerabilities.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Attaches security headers to all HTTP responses.

    Headers applied:
        - X-Content-Type-Options: Prevents MIME-type sniffing
        - X-Frame-Options: Prevents clickjacking via iframes
        - X-XSS-Protection: Legacy XSS filter (still useful for older browsers)
        - Referrer-Policy: Controls referrer information leakage
        - Permissions-Policy: Restricts browser feature access
        - Cache-Control: Prevents caching of sensitive API responses
        - Strict-Transport-Security: Enforces HTTPS (effective when behind TLS)
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # Prevent caching of API responses (except static/docs)
        if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        # HSTS — only effective when served behind TLS termination
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response
