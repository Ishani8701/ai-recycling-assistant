from fastapi import FastAPI, UploadFile, File
from typing import Dict

app = FastAPI(title="Recyclable Object Detector API")

@app.get("/")
async def root():
    return {"message": "Hello World. API is running."}


@app.post("/predict")
async def predict_json(data: Dict):
    # log the received data
    print(f"Received JSON data for mock prediction: {data}")

    return {"result": "recyclable"}


@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    """
    Accepts an uploaded image file (via multipart/form-data) 
    and returns a mock prediction.
    """
    image_bytes = await file.read()
    
    print(f"Received file: {file.filename}")
    print(f"File size: {len(image_bytes)} bytes")

    return {"result": "recyclable"}
