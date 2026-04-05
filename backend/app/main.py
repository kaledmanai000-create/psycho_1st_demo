"""Cognitive Shield TN - FastAPI Backend Entry Point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db
from app.middleware import APIKeyAuthMiddleware, RateLimitMiddleware, RequestLoggingMiddleware
from app.routes.analyze import router as analyze_router
from app.routes.log import router as log_router
from app.routes.model import router as model_router
from app.routes.analytics import router as analytics_router
from app.database import get_request_logs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    init_db()
    # Pre-load AI models
    from app.ai_engine.pipeline import AnalysisPipeline
    app.state.pipeline = AnalysisPipeline()
    yield


app = FastAPI(
    title="Cognitive Shield TN",
    description="AI-powered cybersecurity analysis API - AI assists, Humans decide.",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware (order matters: rate limit first, then auth, then CORS)
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(APIKeyAuthMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(analyze_router, prefix="/analyze", tags=["Analysis"])
app.include_router(log_router, prefix="/log", tags=["Logging"])
app.include_router(model_router, prefix="/model", tags=["Model"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Cognitive Shield TN"}


@app.get("/logs/requests")
async def get_request_log_entries(limit: int = 200):
    """Retrieve recent HTTP request logs."""
    if limit > 500:
        limit = 500
    return get_request_logs(limit)
