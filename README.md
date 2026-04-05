# Cognitive Shield TN

A local hybrid threat-detection system for browser content.

This project detects:
- phishing
- manipulation
- disinformation
- safe content

It combines three local subsystems:
- Rule engine
- Classical ML classifier (scikit-learn: TF-IDF + LogisticRegression)
- Retrieval layer (FAISS over known threat patterns)

No external LLM or paid AI API is required.

## Project Structure

- `backend/` - FastAPI backend and detection pipeline
- `extension/` - Chrome extension UI (v4 integrated)
- `dashboard/` - Local web dashboard UI
- `backend/data/` - Training data, pattern data, model artifact, logs DB

## Requirements

- Windows (tested)
- Python 3.13+
- Chrome (for extension)

## 1) Backend Setup

From project root:

```powershell
cd c:\Users\namou\OneDrive\Desktop\extension\psycho_1st_demo\backend
"C:/Program Files/Python313/python.exe" -m pip install -r requirements.txt
```

## 2) Run FastAPI Backend

Run from any directory:

```powershell
"C:/Program Files/Python313/python.exe" -m uvicorn app.main:app --app-dir c:\Users\namou\OneDrive\Desktop\extension\psycho_1st_demo\backend --host 0.0.0.0 --port 8000
```

Health check:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```

Expected response includes:
- status: healthy
- service: Cognitive Shield TN

### If port 8000 is already in use

```powershell
$conn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
  $procIds = $conn | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($procId in $procIds) {
    Stop-Process -Id $procId -Force
  }
}
```

Then start Uvicorn again.

## 3) Run Dashboard Frontend

```powershell
cd c:\Users\namou\OneDrive\Desktop\extension\psycho_1st_demo\dashboard
"C:/Program Files/Python313/python.exe" -m http.server 8080
```

Open:
- http://localhost:8080

Dashboard calls backend endpoints on port 8000.

## 4) Load Chrome Extension

Open Chrome extensions page:
- chrome://extensions/

Steps:
1. Enable Developer mode.
2. Click Load unpacked.
3. Select this exact folder:
   - `c:\Users\namou\OneDrive\Desktop\extension\psycho_1st_demo\extension`

Important:
- Do not select the repo root.
- `manifest.json` is inside the `extension/` folder.

## 5) Train / Retrain the Model

Retrain and regenerate artifact + metadata:

```powershell
cd c:\Users\namou\OneDrive\Desktop\extension\psycho_1st_demo
"C:/Program Files/Python313/python.exe" retrain.py
```

Outputs:
- `backend/data/ml_model.joblib`
- `backend/data/ml_training_report.json`

Runtime behavior:
- If model artifact exists, backend loads it.
- Retraining is explicit by default.

## 6) Evaluate Detection Quality

```powershell
cd c:\Users\namou\OneDrive\Desktop\extension\psycho_1st_demo\backend
"C:/Program Files/Python313/python.exe" evaluate_system.py
```

This prints:
- accuracy
- macro precision
- macro recall
- macro F1
- confusion matrix
- false positive/negative samples
- calibration proxy (multiclass brier)

## 7) Run Tests

```powershell
cd c:\Users\namou\OneDrive\Desktop\extension\psycho_1st_demo\backend
"C:/Program Files/Python313/python.exe" -m pytest -q
```

## API Overview

Main endpoints:
- `POST /analyze`
- `POST /log`
- `GET /log/history`
- `GET /log/export`
- `GET /analytics`
- `POST /model/retrain`
- `GET /health`

## Typical Local Workflow

1. Install requirements.
2. Start backend on 8000.
3. Start dashboard on 8080.
4. Load extension from `extension/`.
5. Browse content and inspect detections.
6. Log user decisions.
7. Retrain model when enough user labels are available.
8. Run evaluation and tests.

## Troubleshooting

### "ModuleNotFoundError: No module named 'app'"
Use `--app-dir` exactly as shown in the run command.

### "Pack extension error: Manifest file is missing or unreadable"
You selected the wrong folder. Load `...\psycho_1st_demo\extension`, not repo root.

### Dashboard shows failed requests
- Confirm backend is running on port 8000.
- Check `http://localhost:8000/health`.
- Ensure no firewall/proxy blocks localhost.

## Data Files

- `backend/data/training_data.json` - supervised training dataset
- `backend/data/phishing_patterns.json` - retrieval patterns
- `backend/data/disinfo_patterns.json` - retrieval patterns
- `backend/data/cognitive_shield.db` - logged analysis history

## Security and Scope Notes

- This tool assists human judgment; it does not auto-block by default.
- Predictions are probabilistic and should be reviewed by a human.
- Keep training data quality high to reduce false positives/negatives.
