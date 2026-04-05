"""Explicit local retraining entrypoint for ML model artifact generation."""

import os
import sys

os.environ["CS_FORCE_RETRAIN_ON_STARTUP"] = "1"

repo_root = os.path.dirname(__file__)
backend_root = os.path.join(repo_root, "backend")
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.ai_engine.ml_classifier import MLClassifier  # noqa: E402


def main():
    clf = MLClassifier()
    print("Model retrained and saved.")
    print("Metadata:")
    for k, v in clf.metadata.items():
        print(f"- {k}: {v}")


if __name__ == "__main__":
    main()
