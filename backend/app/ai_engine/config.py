"""Configuration helpers for AI engine paths and startup behavior."""

import os
from dataclasses import dataclass


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_PATH = os.path.join(DATA_DIR, "ml_model.joblib")
TRAINING_DATA_PATH = os.path.join(DATA_DIR, "training_data.json")
TRAINING_REPORT_PATH = os.path.join(DATA_DIR, "ml_training_report.json")


def _read_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class MLRuntimeConfig:
    """Runtime settings for model startup behavior."""

    force_retrain_on_startup: bool = _read_bool_env("CS_FORCE_RETRAIN_ON_STARTUP", False)
    allow_train_on_missing_model: bool = _read_bool_env("CS_TRAIN_IF_MODEL_MISSING", True)
    model_version: str = os.getenv("CS_MODEL_VERSION", "2.0.0")
