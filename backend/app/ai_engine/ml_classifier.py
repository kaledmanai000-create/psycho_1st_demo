"""ML Classifier - Logistic Regression for threat classification."""

import os
import json
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
MODEL_PATH = os.path.join(MODEL_DIR, "ml_model.joblib")
TRAINING_DATA_PATH = os.path.join(MODEL_DIR, "training_data.json")

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
        self._load_or_train()

    def _load_or_train(self):
        """Load existing model or train a new one from training data."""
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                return
            except Exception:
                pass

        # Train from scratch
        if os.path.exists(TRAINING_DATA_PATH):
            self._train_from_data()
        else:
            # Create a minimal default model
            self._train_default()

    def _train_from_data(self):
        """Train model from training_data.json."""
        with open(TRAINING_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = [item["text"] for item in data]
        labels = [LABEL_MAP.get(item["label"], 0) for item in data]

        self.model = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 3),
                analyzer="char_wb",
                min_df=1,
                sublinear_tf=True,
            )),
            ("clf", LogisticRegression(
                max_iter=2000,
                C=0.8,
                class_weight="balanced",
                solver="lbfgs",
            )),
        ])

        self.model.fit(texts, labels)

        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)

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
            ("clf", LogisticRegression(max_iter=1000, C=1.0)),
        ])
        self.model.fit(texts, labels)

        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)

    def predict(self, text: str) -> dict:
        """
        Predict threat category and confidence.
        Returns: {label, confidence, probabilities}
        """
        if self.model is None:
            return {"label": "safe", "confidence": 0.0, "probabilities": {}}

        probabilities = self.model.predict_proba([text])[0]
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
        }
