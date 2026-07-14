"""
Simple in-memory rate limiter middleware for FastAPI.

Uses a sliding window counter per client IP to prevent abuse.
Configurable via environment variables or defaults.
"""

import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from app.utils import logger


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Token-bucket style rate limiter.

    Defaults:
        - 60 requests per 60-second window per client IP.
        - Exempt paths: /health, /docs, /openapi.json
    """

    def __init__(
        self,
        app,
        max_requests: int = 60,
        window_seconds: int = 60,
        exempt_paths: Tuple[str, ...] = ("/health", "/docs", "/openapi.json", "/redoc"),
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exempt_paths = exempt_paths
        # {client_ip: [(timestamp, ...),]}
        self._request_log: Dict[str, List[float]] = defaultdict(list)

    def _cleanup_window(self, tracking_key: str) -> None:
        """Remove request timestamps outside the current window."""
        cutoff = time.time() - self.window_seconds
        self._request_log[tracking_key] = [
            ts for ts in self._request_log[tracking_key] if ts > cutoff
        ]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # Default tracking tracking_key (IP-based)
        client_ip = request.client.host if request.client else "unknown"
        tracking_key = f"ip:{client_ip}"
        
        # Default limit
        max_requests = self.max_requests
        
        # Check authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                from app.auth import verify_access_token
                payload = verify_access_token(token)
                if payload:
                    username = payload.get("sub")
                    if username:
                        tracking_key = f"user:{username}"
                        role = payload.get("role", "standard")
                        
                        # Load limits from settings dynamically
                        from app.config import settings
                        if role == "admin":
                            max_requests = settings.RATE_LIMIT_ADMIN_MAX_REQUESTS
                        elif role == "premium":
                            max_requests = settings.RATE_LIMIT_PREMIUM_MAX_REQUESTS
                        else:
                            max_requests = settings.RATE_LIMIT_MAX_REQUESTS
            except Exception:
                # Fall back to IP rate limiting silently if verification fails
                pass

        self._cleanup_window(tracking_key)

        if len(self._request_log[tracking_key]) >= max_requests:
            logger.warning(
                "Rate limit exceeded for %s (%d requests in %ds, limit %d)",
                tracking_key,
                len(self._request_log[tracking_key]),
                self.window_seconds,
                max_requests,
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )

        self._request_log[tracking_key].append(time.time())

        response = await call_next(request)
        # Attach rate limit headers for transparency
        remaining = max_requests - len(self._request_log[tracking_key])
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining, 0))
        response.headers["X-RateLimit-Window"] = f"{self.window_seconds}s"
        return response
