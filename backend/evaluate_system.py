"""Evaluate hybrid detector quality with stratified holdout and detailed metrics."""

import json
import os
from collections import defaultdict

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split

from app.ai_engine.ml_classifier import LABEL_MAP, REVERSE_LABEL_MAP
from app.ai_engine.pipeline import AnalysisPipeline
from app.ai_engine.config import TRAINING_DATA_PATH


def load_data() -> tuple[list[str], list[int]]:
    with open(TRAINING_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [d["text"] for d in data if d.get("label") in LABEL_MAP]
    labels = [LABEL_MAP[d["label"]] for d in data if d.get("label") in LABEL_MAP]
    return texts, labels


def macro_multiclass_brier(y_true: np.ndarray, prob_matrix: np.ndarray, n_classes: int) -> float:
    one_hot = np.zeros((len(y_true), n_classes), dtype=float)
    one_hot[np.arange(len(y_true)), y_true] = 1.0
    return float(np.mean(np.sum((prob_matrix - one_hot) ** 2, axis=1)))


def evaluate():
    texts, labels = load_data()
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    pipeline = AnalysisPipeline()

    # Train a holdout-safe temporary model using the classifier's upgraded builder.
    normalized_train = [pipeline.ml_classifier._normalize_for_training(t) for t in X_train]
    temp_model = pipeline.ml_classifier._build_model()
    temp_model.fit(normalized_train, y_train)
    pipeline.ml_classifier.model = temp_model
    pipeline.ml_classifier.metadata = {
        "model_version": "holdout-eval-temp",
        "sample_count": len(X_train),
    }

    y_pred = []
    prob_rows = []
    false_positives = []
    false_negatives = []

    for text, true_label in zip(X_test, y_test):
        result = pipeline.analyze(text)
        pred_label = result["threat_type"]
        pred_idx = LABEL_MAP.get(pred_label, 0)
        y_pred.append(pred_idx)

        ml_probs = result.get("details", {}).get("ml_probabilities", {})
        prob_rows.append([float(ml_probs.get(REVERSE_LABEL_MAP[i], 0.0)) for i in range(len(REVERSE_LABEL_MAP))])

        true_name = REVERSE_LABEL_MAP[int(true_label)]
        pred_name = REVERSE_LABEL_MAP[int(pred_idx)]

        if true_name == "safe" and pred_name != "safe":
            false_positives.append({"text": text[:180], "pred": pred_name, "risk": result["risk_score"]})
        if true_name != "safe" and pred_name == "safe":
            false_negatives.append({"text": text[:180], "true": true_name, "risk": result["risk_score"]})

    y_pred = np.array(y_pred)
    prob_matrix = np.array(prob_rows)

    acc = accuracy_score(y_test, y_pred)
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="macro", zero_division=0
    )

    report = classification_report(
        y_test,
        y_pred,
        target_names=[REVERSE_LABEL_MAP[i] for i in sorted(REVERSE_LABEL_MAP)],
        zero_division=0,
    )
    cm = confusion_matrix(y_test, y_pred)
    brier = macro_multiclass_brier(y_test, prob_matrix, n_classes=4)

    print("HYBRID_EVAL_METRICS")
    print(f"accuracy={acc:.4f}")
    print(f"macro_precision={macro_p:.4f}")
    print(f"macro_recall={macro_r:.4f}")
    print(f"macro_f1={macro_f1:.4f}")
    print(f"multiclass_brier={brier:.4f}")
    print("confusion_matrix=")
    print(cm)
    print("classification_report=")
    print(report)

    print("false_positives_sample=")
    for item in false_positives[:10]:
        print(item)

    print("false_negatives_sample=")
    for item in false_negatives[:10]:
        print(item)

    class_counts = defaultdict(int)
    for idx in y:
        class_counts[REVERSE_LABEL_MAP[int(idx)]] += 1
    print("dataset_class_counts=", dict(class_counts))


if __name__ == "__main__":
    evaluate()
