from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import our simple classifier
from ml.simple_classifier import SimpleRecyclingClassifier

app = FastAPI(title="Recycling Classifier API")

# Initialize classifier
classifier = SimpleRecyclingClassifier()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Recycling Classifier API is running"}

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    Accepts an image and returns if it's recyclable or not
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Get prediction
        result = classifier.predict(temp_file_path)
        return {
            "label": result['label'],
            "confidence": result['confidence'],
            "is_recyclable": result['is_recyclable'],
            "original_label": result['original_label']
        }
    except Exception as e:
        raise HTTPException(500, f"Error processing image: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
