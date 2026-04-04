"""Cognitive Shield TN - FastAPI Backend Entry Point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes.analyze import router as analyze_router
from app.routes.log import router as log_router


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

# CORS - allow browser extension and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to extension origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/analyze", tags=["Analysis"])
app.include_router(log_router, prefix="/log", tags=["Logging"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Cognitive Shield TN"}
