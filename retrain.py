import json, os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

DATA_DIR = os.path.join(os.path.dirname(__file__), "backend", "data")
TRAIN_PATH = os.path.join(DATA_DIR, "training_data.json")
MODEL_PATH = os.path.join(DATA_DIR, "ml_model.joblib")

LABEL_MAP = {"safe": 0, "phishing": 1, "manipulation": 2, "disinformation": 3}
REV_MAP = {v: k for k, v in LABEL_MAP.items()}

with open(TRAIN_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [d["text"] for d in data]
labels = [LABEL_MAP.get(d["label"], 0) for d in data]
print(f"Training on {len(texts)} samples...")

model = Pipeline([
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
model.fit(texts, labels)
joblib.dump(model, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")

# Quick test
tests = [
    "ادخل كلمة السر متاعك تو على الرابط هذا",
    "اصحى يا تونسي! شارك قبل ما يمسحوا البوست",
    "اليوم الطقس باهي في تونس",
    "الحكومة تبيع البلاد و الحقيقة المخفية",
]
for t in tests:
    probs = model.predict_proba([t])[0]
    idx = probs.argmax()
    print(f"[{REV_MAP[idx]}] conf={probs[idx]:.2f} => {t[:60]}")
