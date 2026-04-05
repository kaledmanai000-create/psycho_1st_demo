"""ML Classifier - local classical ML model with safe training/loading behavior."""

import json
import os
import re
import time
from collections import Counter

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from app.ai_engine.config import (
    DATA_DIR,
    MODEL_PATH,
    TRAINING_DATA_PATH,
    TRAINING_REPORT_PATH,
    MLRuntimeConfig,
)

LABEL_MAP = {
    "safe": 0,
    "phishing": 1,
    "manipulation": 2,
    "disinformation": 3,
}
REVERSE_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}


class MLClassifier:
    """Logistic Regression classifier trained on labeled threat data."""

    def __init__(self):
        self.model: Pipeline | None = None
        self.metadata: dict = {}
        self.runtime_config = MLRuntimeConfig()
        self._load_or_train()

    def _load_or_train(self):
        """Load existing model or train a new one based on runtime config."""
        if self.runtime_config.force_retrain_on_startup:
            if os.path.exists(TRAINING_DATA_PATH):
                self._train_from_data()
                return

        if os.path.exists(MODEL_PATH):
            try:
                payload = joblib.load(MODEL_PATH)
                if isinstance(payload, dict) and "model" in payload:
                    self.model = payload["model"]
                    self.metadata = payload.get("metadata", {})
                else:
                    # Backward compatibility with older artifact format (pipeline only).
                    self.model = payload
                    self.metadata = {"artifact_format": "legacy_pipeline_only"}
                return
            except Exception:
                pass

        if self.runtime_config.allow_train_on_missing_model and os.path.exists(TRAINING_DATA_PATH):
            self._train_from_data()
        else:
            self._train_default()

    def _normalize_for_training(self, text: str) -> str:
        """Lightweight normalization tuned for short multilingual scam messages."""
        text = (text or "").strip()
        text = re.sub(r"https?://\S+|www\.\S+", " [URL] ", text, flags=re.IGNORECASE)
        text = re.sub(r"\S+@\S+", " [EMAIL] ", text)
        text = re.sub(r"\b\d{6,}\b", " [LONG_NUMBER] ", text)
        text = re.sub(r"\s+", " ", text)
        return text.lower().strip()

    def _load_and_validate_training_data(self) -> tuple[list[str], list[int]]:
        with open(TRAINING_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list) or len(data) < 20:
            raise ValueError("Training data is missing or too small to train a reliable model")

        texts: list[str] = []
        labels: list[int] = []
        for item in data:
            raw_text = str(item.get("text", "")).strip()
            raw_label = str(item.get("label", "safe")).strip().lower()
            if not raw_text or raw_label not in LABEL_MAP:
                continue
            texts.append(self._normalize_for_training(raw_text))
            labels.append(LABEL_MAP[raw_label])

        if len(texts) < 20:
            raise ValueError("No valid samples found after data validation")

        return texts, labels

    def _build_model(self) -> Pipeline:
        # Mix word and character n-grams for robustness across spelling noise and multilingual text.
        vectorizer = FeatureUnion([
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    sublinear_tf=True,
                    strip_accents="unicode",
                    token_pattern=r"(?u)\b\w\w+\b",
                ),
            ),
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    max_features=40000,
                    sublinear_tf=True,
                ),
            ),
        ])

        clf = LogisticRegression(
            max_iter=3000,
            C=1.2,
            class_weight="balanced",
            solver="saga",
        )

        return Pipeline([
            ("tfidf", vectorizer),
            ("clf", clf),
        ])

    def _train_from_data(self):
        """Train model from validated training data and persist metadata/report."""
        start_time = time.time()
        texts, labels = self._load_and_validate_training_data()

        label_counts = Counter(labels)
        X_train, X_val, y_train, y_val = train_test_split(
            texts,
            labels,
            test_size=0.2,
            random_state=42,
            stratify=labels,
        )

        self.model = self._build_model()
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_val)
        val_acc = float(accuracy_score(y_val, y_pred))
        macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
            y_val,
            y_pred,
            average="macro",
            zero_division=0,
        )

        training_seconds = round(time.time() - start_time, 3)
        self.metadata = {
            "model_version": self.runtime_config.model_version,
            "training_seconds": training_seconds,
            "sample_count": len(texts),
            "label_distribution": {
                REVERSE_LABEL_MAP[k]: int(v) for k, v in label_counts.items()
            },
            "validation": {
                "accuracy": round(val_acc, 4),
                "macro_precision": round(float(macro_p), 4),
                "macro_recall": round(float(macro_r), 4),
                "macro_f1": round(float(macro_f1), 4),
            },
        }

        os.makedirs(DATA_DIR, exist_ok=True)
        payload = {
            "model": self.model,
            "metadata": self.metadata,
        }
        joblib.dump(payload, MODEL_PATH)
        with open(TRAINING_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def _train_default(self):
        """Train a minimal model with built-in examples."""
        texts = [
            "Click here to verify your bank account immediately",
            "Your account has been suspended, enter your password now",
            "Congratulations! You won a free iPhone, claim now",
            "URGENT: Your PayPal account needs verification",
            "Act now or your account will be permanently deleted",
            "They don't want you to know the truth about vaccines",
            "Mainstream media is hiding this shocking discovery",
            "Scientists baffled by this one weird trick",
            "The government is secretly controlling the weather",
            "Share this before it gets deleted! Truth exposed!",
            "Today's weather forecast calls for sunny skies",
            "The quarterly earnings report showed stable growth",
            "New study published in Nature about climate patterns",
            "Local community center announces new programs for youth",
            "The restaurant received positive reviews for its menu",
        ]
        labels = [1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0]

        self.model = Pipeline([
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")),
            ("clf", LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced")),
        ])
        self.model.fit(texts, labels)

        self.metadata = {
            "model_version": "default-fallback",
            "training_seconds": 0.0,
            "sample_count": len(texts),
            "label_distribution": {
                REVERSE_LABEL_MAP[k]: int(v)
                for k, v in Counter(labels).items()
            },
            "validation": {
                "accuracy": None,
                "macro_precision": None,
                "macro_recall": None,
                "macro_f1": None,
            },
        }

        os.makedirs(DATA_DIR, exist_ok=True)
        payload = {
            "model": self.model,
            "metadata": self.metadata,
        }
        joblib.dump(payload, MODEL_PATH)
        with open(TRAINING_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def explain_prediction(self, text: str, top_n: int = 5) -> list[dict]:
        """Return top contributing ML features for each class (best effort)."""
        if self.model is None:
            return []

        try:
            vectorizer = self.model.named_steps["tfidf"]
            clf = self.model.named_steps["clf"]
            x = vectorizer.transform([self._normalize_for_training(text)])
            feature_names = vectorizer.get_feature_names_out()
            rows: list[dict] = []

            for class_idx, class_name in REVERSE_LABEL_MAP.items():
                class_coefs = clf.coef_[class_idx]
                contributions = x.multiply(class_coefs)
                if contributions.nnz == 0:
                    rows.append({"label": class_name, "top_features": []})
                    continue
                dense_idx = contributions.indices
                dense_vals = contributions.data
                order = np.argsort(-np.abs(dense_vals))[:top_n]
                top_features = [
                    {
                        "feature": str(feature_names[dense_idx[i]]),
                        "contribution": float(dense_vals[i]),
                    }
                    for i in order
                ]
                rows.append({"label": class_name, "top_features": top_features})
            return rows
        except Exception:
            return []

    def predict(self, text: str) -> dict:
        """
        Predict threat category and confidence.
        Returns: {label, confidence, probabilities}
        """
        if self.model is None:
            return {"label": "safe", "confidence": 0.0, "probabilities": {}}

        normalized_text = self._normalize_for_training(text)
        probabilities = self.model.predict_proba([normalized_text])[0]
        predicted_class = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_class])

        prob_dict = {
            REVERSE_LABEL_MAP.get(i, "unknown"): float(p)
            for i, p in enumerate(probabilities)
        }

        return {
            "label": REVERSE_LABEL_MAP.get(predicted_class, "safe"),
            "confidence": confidence,
            "probabilities": prob_dict,
            "top_features": self.explain_prediction(text, top_n=4),
            "model_version": self.metadata.get("model_version", "unknown"),
        }
