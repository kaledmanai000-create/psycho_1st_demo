"""Cognitive Shield TN - FastAPI Backend Entry Point."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes.analyze import router as analyze_router
from app.routes.log import router as log_router
from app.routes.analytics import router as analytics_router
from app.routes.model import router as model_router


logger = logging.getLogger("cognitive_shield")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    init_db()
    # Pre-load AI models
    from app.ai_engine.pipeline import AnalysisPipeline
    app.state.pipeline = AnalysisPipeline()
    ml_classifier = app.state.pipeline.ml_classifier
    logger.info(
        "ML model ready | version=%s | samples=%s | label_distribution=%s | retrain_on_startup=%s",
        ml_classifier.metadata.get("model_version", "unknown"),
        ml_classifier.metadata.get("sample_count", "unknown"),
        ml_classifier.metadata.get("label_distribution", {}),
        ml_classifier.runtime_config.force_retrain_on_startup,
    )
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
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(model_router, prefix="/model", tags=["Model"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Cognitive Shield TN"}
