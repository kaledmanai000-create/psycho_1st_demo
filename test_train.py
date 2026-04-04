import sys, os
os.chdir(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, os.getcwd())
from app.ai_engine.ml_classifier import MLClassifier

print("Training model with expanded dataset...")
c = MLClassifier()
print("Model trained successfully!")

tests = [
    "ادخل كلمة السر متاعك تو على الرابط هذا",
    "اصحى يا تونسي! شارك قبل ما يمسحوا البوست",
    "اليوم الطقس باهي في تونس",
    "الحكومة تبيع البلاد و الحقيقة المخفية",
]
for t in tests:
    r = c.predict(t)
    print(f"\n[{r['label']}] conf={r['confidence']:.2f} => {t[:60]}")
