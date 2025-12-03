from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

app = FastAPI(title="Recyclable Object Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World. API is running."}




@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    Accepts an uploaded image file (via multipart/form-data) 
    and returns a mock prediction.
    """

    image_bytes = await file.read()
    
    print(f"Received file: {file.filename}")
    print(f"File size: {len(image_bytes)} bytes")

    # TODO: pass bytes to your model preprocessing/predict code
    # Example placeholder:
    # label, confidence = my_model_predict_from_bytes(contents)

    # For now return a dummy response while wiring up:
    label = "recyclable"
    confidence = 0.85

    return {"label": label, "confidence": confidence}
