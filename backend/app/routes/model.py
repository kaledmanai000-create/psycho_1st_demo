"""POST /model/retrain endpoint for dashboard-triggered retraining."""

import json
import os

from fastapi import APIRouter, HTTPException, Request

from app.ai_engine.config import TRAINING_DATA_PATH
from app.ai_engine.ml_classifier import LABEL_MAP, MLClassifier
from app.database import get_connection

router = APIRouter()


@router.post("/retrain")
async def retrain_model(request: Request):
    """Retrain model using user-confirmed logs, then hot-reload pipeline classifier."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT input_text, threat_type, user_decision FROM analysis_logs WHERE user_decision = 'mark_as_threat'"
    )
    threat_rows = cursor.fetchall()

    cursor.execute("SELECT input_text FROM analysis_logs WHERE user_decision = 'ignore'")
    safe_rows = cursor.fetchall()
    conn.close()

    if len(threat_rows) + len(safe_rows) < 5:
        raise HTTPException(
            status_code=400,
            detail="Not enough user decisions to retrain. Need at least 5 logged decisions.",
        )

    training_data = []
    if os.path.exists(TRAINING_DATA_PATH):
        with open(TRAINING_DATA_PATH, "r", encoding="utf-8") as f:
            training_data = json.load(f)

    existing_texts = {item.get("text", "") for item in training_data}
    added = 0

    for row in threat_rows:
        text = row["input_text"]
        label = row["threat_type"] if row["threat_type"] in LABEL_MAP else "phishing"
        if text and text not in existing_texts:
            training_data.append({"text": text, "label": label})
            existing_texts.add(text)
            added += 1

    for row in safe_rows:
        text = row["input_text"]
        if text and text not in existing_texts:
            training_data.append({"text": text, "label": "safe"})
            existing_texts.add(text)
            added += 1

    os.makedirs(os.path.dirname(TRAINING_DATA_PATH), exist_ok=True)
    with open(TRAINING_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)

    # Force fresh retrain for this request then restore env behavior.
    previous_force = os.getenv("CS_FORCE_RETRAIN_ON_STARTUP")
    os.environ["CS_FORCE_RETRAIN_ON_STARTUP"] = "1"
    try:
        fresh_classifier = MLClassifier()
    finally:
        if previous_force is None:
            os.environ.pop("CS_FORCE_RETRAIN_ON_STARTUP", None)
        else:
            os.environ["CS_FORCE_RETRAIN_ON_STARTUP"] = previous_force

    # Hot-swap classifier in running pipeline so new model is used immediately.
    request.app.state.pipeline.ml_classifier = fresh_classifier

    return {
        "status": "retrained",
        "new_samples_added": added,
        "total_training_samples": len(training_data),
        "model_version": fresh_classifier.metadata.get("model_version", "unknown"),
    }
