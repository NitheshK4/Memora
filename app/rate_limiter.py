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

    def _cleanup_window(self, client_ip: str) -> None:
        """Remove request timestamps outside the current window."""
        cutoff = time.time() - self.window_seconds
        self._request_log[client_ip] = [
            ts for ts in self._request_log[client_ip] if ts > cutoff
        ]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limiting for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        self._cleanup_window(client_ip)

        if len(self._request_log[client_ip]) >= self.max_requests:
            logger.warning(
                "Rate limit exceeded for client %s (%d requests in %ds)",
                client_ip,
                len(self._request_log[client_ip]),
                self.window_seconds,
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )

        self._request_log[client_ip].append(time.time())

        response = await call_next(request)
        # Attach rate limit headers for transparency
        remaining = self.max_requests - len(self._request_log[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining, 0))
        response.headers["X-RateLimit-Window"] = f"{self.window_seconds}s"
        return response
