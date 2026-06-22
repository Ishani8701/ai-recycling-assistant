# AI Recycling Assistant

![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-Keras-FF6F00?logo=tensorflow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)

A computer-vision web app that classifies a photographed item as **recyclable** or **non-recyclable**. Upload a photo or use your device camera, and the app returns a prediction with a confidence score.

The project is a small monorepo with three independent layers: a TensorFlow/Keras image classifier (`ml/`), a FastAPI inference service (`backend/`), and a Next.js web client (`frontend/`) with file upload and live camera capture.

## Architecture

```
┌───────────────┐    image (multipart)    ┌──────────────┐    image array   ┌─────────────────────┐
│  Next.js UI   │ ──────────────────────▶ │  FastAPI API  │ ───────────────▶ │  InceptionV3        │
│ (frontend/)   │     POST /predict       │  (backend/)   │                  │  + keyword mapping  │
│ upload/camera │ ◀────────────────────── │               │ ◀─────────────── │  (ml/)              │
└───────────────┘  { label, confidence }  └──────────────┘    prediction    └─────────────────────┘
```

## How classification works

The classifier used by the API (`SimpleRecyclingClassifier`) builds on **InceptionV3 pretrained on ImageNet**. For an uploaded image it:

1. Resizes to $299 \times 299$ and applies InceptionV3 preprocessing.
2. Predicts the most likely ImageNet class.
3. Maps that class to recyclable / non-recyclable using a keyword list (`bottle`, `can`, `carton`, `glass`, `plastic`, `metal`, and so on).

The batch-evaluation variant (`RecyclingClassifier` in `inceptionv3_pipeline.py`) is more robust: it takes the **top-5** ImageNet predictions, splits their probability mass between the two categories, and normalizes:

$$\text{conf}_{\text{recyclable}} = \frac{\sum_{i \in R} s_i}{\sum_i s_i}, \qquad \hat{y} = \arg\max\left(\text{conf}_{\text{recyclable}},\ \text{conf}_{\text{non-recyclable}}\right)$$

where $s_i$ is the softmax score of the $i$-th ImageNet class and $R$ is the set of classes whose label matches a recyclable keyword.

A fine-tuned approach using a **MobileNetV2** base with a custom classification head is scaffolded in `ml/scripts/test_tf.py` and is the planned next step (see [Roadmap](#roadmap)).

## Repository structure

```
.
├── ml/                          # Model + data pipeline (TensorFlow / Keras)
│   ├── simple_classifier.py     # InceptionV3 + keyword mapping (used by the API)
│   ├── inceptionv3_pipeline.py  # Top-5 evaluation pipeline + results writer
│   ├── metrics.py               # accuracy / precision / recall / confusion matrix
│   ├── resize.py, rename.py     # dataset preprocessing helpers
│   ├── scripts/test_tf.py       # MobileNetV2 transfer-learning scaffold (WIP)
│   └── datasets/                # train / val / test splits (recyclable, non_recyclable)
├── backend/                     # FastAPI inference service
│   └── main.py                  # GET / (health), POST /predict
├── frontend/test-app/           # Next.js (React + TypeScript + Tailwind) client
│   ├── app/page.tsx             # Home page
│   └── components/ImageUploader.tsx   # upload + camera capture + result display
└── results/inceptionv3_results.md     # sample evaluation output
```

## Tech stack

- **Frontend:** Next.js 15 (Turbopack), React 19, TypeScript, Tailwind CSS v4
- **Backend:** FastAPI, Uvicorn, Pillow, NumPy
- **ML:** TensorFlow / Keras, scikit-learn; InceptionV3 (ImageNet) for inference, MobileNetV2 scaffold for future fine-tuning
- **Dataset:** Kaggle — *Most Common Recyclable and Non-Recyclable Objects*

## Dataset

Images come from the Kaggle dataset *Most Common Recyclable and Non-Recyclable Objects*, organized into two classes across train / val / test splits:

| Split | Recyclable | Non-recyclable |
| ----- | ---------- | -------------- |
| Train | 493 | 834 |
| Val | 61 | 53 |
| Test | 61 | 53 |

Recyclable examples include bottles and cans; non-recyclable examples include juice boxes, milk cartons, styrofoam, and utensils. Preprocessing (square-crop and resize, then sequential renaming) is handled by `resize.py` and `rename.py`.

## Results

On a held-out sample, the InceptionV3 + keyword approach reaches roughly **75%** accuracy. The raw ImageNet top prediction is also surfaced alongside each result for interpretability. Full sample predictions are in [`results/inceptionv3_results.md`](results/inceptionv3_results.md).

## API

Base URL (local): `http://localhost:8000`

### `GET /` — health check

```json
{ "message": "Recycling Classifier API is running" }
```

### `POST /predict` — classify an uploaded image

- **Body:** `multipart/form-data` with a `file` field (`image/*`)
- **Response:**

```json
{
  "label": "recyclable",
  "confidence": 0.91,
  "is_recyclable": true,
  "original_label": "water_bottle"
}
```

Example:

```bash
curl -X POST http://localhost:8000/predict -F "file=@path/to/image.jpg"
```

## Getting started

**Prerequisites:** Python 3.10+ and Node.js 18+.

### 1. Backend (FastAPI)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# The API loads InceptionV3 via ml/simple_classifier.py, which requires TensorFlow:
pip install tensorflow
uvicorn main:app --reload --port 8000
```

The first prediction downloads the InceptionV3 ImageNet weights.

### 2. Frontend (Next.js)

```bash
cd frontend/test-app
npm install
npm run dev
```

Open `http://localhost:3000`. The client posts uploads to `http://localhost:8000/predict`, so keep the backend running.

### 3. ML evaluation (optional)

```bash
cd ml
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python inceptionv3_pipeline.py   # point the dataset path inside the script at ml/datasets first
```

## Roadmap

- Replace the ImageNet keyword heuristic with a **MobileNetV2** (or EfficientNet) classifier fine-tuned on the recycling dataset — the training scaffold already exists in `scripts/test_tf.py`.
- Report full precision, recall, and a confusion matrix (`metrics.py` already supports these).
- Load the trained model once at backend startup instead of re-instantiating it per request.
- Containerize the backend and deploy the frontend (e.g. Vercel) for a public demo.
- Extend beyond binary classification to material-specific categories (plastic / glass / metal / paper).

## License

See the [LICENSE](LICENSE) file.

## Team

A collaborative project — see the repository's contributor list.
