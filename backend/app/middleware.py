"""Middleware for API key authentication, rate limiting, and request logging."""

import time
import json
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.config import get_settings
from app.database import log_request

# Paths that don't require authentication
PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Validates X-API-Key header on protected endpoints (disabled by default)."""

    async def dispatch(self, request: Request, call_next):
        # Auth disabled - allow all requests through
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


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every HTTP request with method, path, status, duration, and body summary."""

    # Paths to skip logging (high-frequency or internal)
    SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        # Read request body for POST/PUT
        body_text = ""
        if method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                body_text = body.decode("utf-8", errors="replace")[:2000]
            except Exception:
                body_text = "[could not read body]"

        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000

        # Build response summary
        resp_summary = f"status={response.status_code}"
        if path.startswith("/analyze") and method == "POST":
            # Try to extract risk_score from body_text for summary
            try:
                req_data = json.loads(body_text)
                text_preview = req_data.get("text", "")[:80]
                resp_summary += f" | input='{text_preview}...'"
            except Exception:
                pass

        try:
            log_request(
                method=method,
                path=path,
                status_code=response.status_code,
                client_ip=client_ip,
                duration_ms=duration_ms,
                request_body=body_text,
                response_summary=resp_summary,
            )
        except Exception:
            pass  # Don't break requests if logging fails

        return response
