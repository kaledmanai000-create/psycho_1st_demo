"""ML Classifier - Logistic Regression for threat classification."""

import os
import json
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score

from app.config import get_settings

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
        self.settings = get_settings()
        self._load_or_train()

    def _load_or_train(self):
        """Load existing model or train a new one from training data."""
        # Always retrain if training data is newer than model
        model_exists = os.path.exists(self.settings.model_path)
        data_exists = os.path.exists(self.settings.training_data_path)

        if model_exists and data_exists:
            model_mtime = os.path.getmtime(self.settings.model_path)
            data_mtime = os.path.getmtime(self.settings.training_data_path)
            if data_mtime > model_mtime:
                # Data is newer, retrain
                self._train_from_data()
                return

        if model_exists:
            try:
                self.model = joblib.load(self.settings.model_path)
                return
            except Exception:
                pass

        if data_exists:
            self._train_from_data()
        else:
            self._train_default()

    def _train_from_data(self):
        """Train model from training_data.json with improved parameters."""
        with open(self.settings.training_data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = [item["text"] for item in data]
        labels = [LABEL_MAP.get(item["label"], 0) for item in data]

        # No stop_words since we have Arabic/French/English multilingual data
        # Use sublinear_tf for better feature scaling
        # Use char_wb analyzer alongside word for better Arabic handling
        self.model = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 3),
                sublinear_tf=True,
                analyzer="word",
                min_df=2,
                max_df=0.95,
            )),
            ("clf", LogisticRegression(
                max_iter=2000,
                C=5.0,
                class_weight="balanced",
                solver="lbfgs",
            )),
        ])

        self.model.fit(texts, labels)

        # Print training accuracy
        try:
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scores = cross_val_score(self.model, texts, labels, cv=cv, scoring="accuracy")
            print(f"ML Classifier: Trained on {len(texts)} samples, "
                  f"CV accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})")
        except Exception:
            print(f"ML Classifier: Trained on {len(texts)} samples")

        os.makedirs(self.settings.model_dir, exist_ok=True)
        joblib.dump(self.model, self.settings.model_path)

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

        os.makedirs(self.settings.model_dir, exist_ok=True)
        joblib.dump(self.model, self.settings.model_path)

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
