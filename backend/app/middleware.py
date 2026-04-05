"""Middleware for API key authentication and rate limiting."""

import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.config import get_settings

# Paths that don't require authentication
PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Validates X-API-Key header on protected endpoints."""

    async def dispatch(self, request: Request, call_next):
        # Allow CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip auth for public paths
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        settings = get_settings()
        api_key = request.headers.get("X-API-Key", "")

        if api_key != settings.api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key. Provide X-API-Key header."},
            )

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory sliding window rate limiter per client IP."""

    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for public paths
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        settings = get_settings()
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = settings.rate_limit_window_seconds

        # Clean old entries
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if now - t < window
        ]

        if len(self._requests[client_ip]) >= settings.rate_limit_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
