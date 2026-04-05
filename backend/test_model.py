"""Quick test of the retrained ML classifier."""
import os, sys
# Delete old cached model to force retrain
model_path = os.path.join(os.path.dirname(__file__), "models", "threat_classifier.joblib")
if os.path.exists(model_path):
    os.remove(model_path)
    print("Deleted old model, will retrain...")

from app.ai_engine.ml_classifier import MLClassifier
clf = MLClassifier()

tests = [
    ("Today the weather is sunny in Tunis", "safe"),
    ("Your bank account has been suspended, enter your password now", "phishing"),
    ("Wake up Tunisia! Share before they delete this! Silence is betrayal!", "manipulation"),
    ("Secret documents prove the government is hiding a cancer cure", "disinformation"),
    ("بلدية تونس تعلن عن مشروع جديد لتحسين النقل العمومي", "safe"),
    ("عاجل: حسابك في بنك الزيتونة تم تعليقه! أدخل بياناتك فورا", "phishing"),
    ("اللي ما يشاركش هالخبر خاين لبلادو! فيقوا يا توانسة!", "manipulation"),
    ("فضيحة: الحكومة تبيع أراضي البلاد للأجانب في السر!", "disinformation"),
    ("Le Festival de Carthage annonce sa programmation pour cet été", "safe"),
    ("URGENT BNA: Activité suspecte détectée sur votre compte", "phishing"),
    ("Tunisiens réveillez-vous! On nous ment! Partagez massivement!", "manipulation"),
    ("EXCLUSIF: Des documents prouvent que le FMI contrôle la Tunisie!", "disinformation"),
]

correct = 0
print(f"\n{'='*70}")
print(f"Testing ML Classifier with {len(tests)} samples")
print(f"{'='*70}")
for text, expected in tests:
    result = clf.predict(text)
    predicted = result["label"]
    conf = result["confidence"]
    status = "OK" if predicted == expected else "WRONG"
    if predicted == expected:
        correct += 1
    print(f"\n[{status}] Expected: {expected:15s} | Got: {predicted:15s} ({conf:.1%})")
    print(f"  Text: {text[:80]}...")

print(f"\n{'='*70}")
print(f"Accuracy: {correct}/{len(tests)} ({correct/len(tests):.0%})")
print(f"{'='*70}")
