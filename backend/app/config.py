"""Centralized configuration using pydantic BaseSettings."""

import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_prefix="CS_", env_file=".env", extra="ignore")

    # API Security
    api_key: str = "changeme-cognitive-shield-key"
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    # Database
    db_path: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "cognitive_shield.db"
    )

    # Model paths
    model_dir: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data"
    )
    model_path: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "ml_model.joblib"
    )
    training_data_path: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "training_data.json"
    )

    # Data paths
    phishing_patterns_path: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "phishing_patterns.json"
    )
    disinfo_patterns_path: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "disinfo_patterns.json"
    )

    # CORS
    cors_origins: str = "*"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
