"""POST /model/retrain endpoint - retrains ML model from user-confirmed decisions."""

import json
import os
from fastapi import APIRouter, HTTPException
from app.config import get_settings
from app.database import get_connection
from app.ai_engine.ml_classifier import MLClassifier, LABEL_MAP

router = APIRouter()


@router.post("/retrain")
async def retrain_model():
    """
    Retrain the ML classifier using user-confirmed decisions from the database.
    Appends confirmed threat decisions to training data and retrains.
    """
    settings = get_settings()

    # Get user-confirmed decisions from DB
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT input_text, threat_type, user_decision FROM analysis_logs WHERE user_decision = 'mark_as_threat'"
    )
    threat_rows = cursor.fetchall()

    cursor.execute(
        "SELECT input_text FROM analysis_logs WHERE user_decision = 'ignore'"
    )
    safe_rows = cursor.fetchall()
    conn.close()

    if len(threat_rows) + len(safe_rows) < 5:
        raise HTTPException(
            status_code=400,
            detail="Not enough user decisions to retrain. Need at least 5 logged decisions."
        )

    # Load existing training data
    training_data = []
    if os.path.exists(settings.training_data_path):
        with open(settings.training_data_path, "r", encoding="utf-8") as f:
            training_data = json.load(f)

    existing_texts = {item["text"] for item in training_data}

    # Add user-confirmed threats
    added = 0
    for row in threat_rows:
        text = row["input_text"]
        label = row["threat_type"] if row["threat_type"] in LABEL_MAP else "phishing"
        if text not in existing_texts:
            training_data.append({"text": text, "label": label})
            existing_texts.add(text)
            added += 1

    # Add user-confirmed safe content
    for row in safe_rows:
        text = row["input_text"]
        if text not in existing_texts:
            training_data.append({"text": text, "label": "safe"})
            existing_texts.add(text)
            added += 1

    # Save updated training data
    os.makedirs(os.path.dirname(settings.training_data_path), exist_ok=True)
    with open(settings.training_data_path, "w", encoding="utf-8") as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)

    # Delete old model to force retrain
    if os.path.exists(settings.model_path):
        os.remove(settings.model_path)

    # Retrain
    classifier = MLClassifier()

    return {
        "status": "retrained",
        "new_samples_added": added,
        "total_training_samples": len(training_data),
    }
