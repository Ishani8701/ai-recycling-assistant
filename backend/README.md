# Backend - AI Recycling Assistant

This directory contains the FastAPI backend for the AI Recycling Assistant.

Quick start (macOS / Linux):

1. Create and activate a virtual environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app locally (development)

```bash
uvicorn main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/
```

Notes and next steps:

- The current endpoints return mock predictions. To enable real model inference:
  - Train a model and save it to `ml/models/` (see `ml/requirements.txt` & ML scripts).
  - Install TensorFlow in the backend environment (uncomment/add `tensorflow` in `requirements.txt`) or serve the model from a separate ML service.
  - Load the model at app startup (e.g., `model = tf.keras.models.load_model(path)`) and preprocess uploaded images before calling `model.predict()`.
- Add CORS middleware if you want to call this backend from the frontend dev server (example using `fastapi.middleware.cors.CORSMiddleware`).
- This README should be expanded when the model serving flow is implemented.

