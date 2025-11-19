from io import BytesIO
import os
import json
import tensorflow as tf
from keras.applications import MobileNetV2
from keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from keras.preprocessing import image
import numpy as np
from PIL import Image
import requests

# 1. Load Pretrained MobileNetV2
print("Loading MobileNetV2 (ImageNet weights)...")
model = MobileNetV2(weights='imagenet', include_top=True)
print("Model loaded successfully!\n")

# 2. Keyword-based Recyclable Mapping
RECYCLABLE_KEYWORDS = [
    'bottle', 'water bottle', 'plastic bottle', 'soda bottle', 'pop bottle',
    'can', 'tin can', 'beer can', 'aluminum can', 'soda can',
    'carton', 'milk jug', 'juice carton', 'cardboard', 'box',
    'paper', 'newspaper', 'magazine', 'envelope', 'mail',
    'glass bottle', 'wine bottle', 'beer bottle', 'jar'
]

NON_RECYCLABLE_KEYWORDS = [
    'banana', 'apple', 'orange', 'pizza', 'cake', 'sandwich', 'hotdog',
    'donut', 'bread', 'food', 'trash', 'waste', 'diaper', 'battery',
    'cigarette', 'styrofoam', 'foam', 'plastic bag', 'wrapper',
    'chip bag', 'crisp packet', 'coffee cup', 'lid', 'takeout container'
]

def is_recyclable(label):
    label_lower = label.lower()

    if any(k in label_lower for k in RECYCLABLE_KEYWORDS):
        return True, "Recyclable"
    if any(k in label_lower for k in NON_RECYCLABLE_KEYWORDS):
        return False, "Non-recyclable"
    
    # Special rules
    if 'carton' in label_lower and 'egg' not in label_lower:
        return True, "Recyclable"
    if 'packet' in label_lower or 'bag' in label_lower:
        return False, "Non-recyclable"
    return False, "Non-recyclable (Uncertain)"

# 3. Prediction Function
def predict_image(img_path_or_url):
    # Load image
    if img_path_or_url.startswith('http'):
        response = requests.get(img_path_or_url, timeout=10)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(img_path_or_url)

    img = img.convert('RGB').resize((224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Predict
    preds = model.predict(img_array, verbose=0)
    decoded = decode_predictions(preds, top=3)[0]

    top_label = decoded[0][1]
    top_conf = float(decoded[0][2])
    recyclable, category = is_recyclable(top_label)

    return {
        "image": os.path.basename(img_path_or_url) if not img_path_or_url.startswith('http') else img_path_or_url.split('/')[-1].split('?')[0],
        "top_prediction": top_label,
        "confidence": top_conf,
        "recyclable": recyclable,
        "category": category,
        "top_3": [(label, float(conf)) for _, label, conf in decoded]
    }

# 4. Test on Sample Images
def run_tests():
    test_images = [
        # Recyclable (expected: True)
        "ml/datasets/test/recyclable/Bottle 40.jpg",
        "ml/datasets/test/recyclable/Bottle 76.jpg",
        "ml/datasets/test/recyclable/Bottle 69.jpg",
        "ml/datasets/test/recyclable/Can 23.jpg",
        "ml/datasets/test/recyclable/Can 30.jpg",
        "ml/datasets/test/recyclable/Can 42.jpg",
        "ml/datasets/test/recyclable/Can 35.jpg",

        # Non-recyclable (expected: False)
        "ml/datasets/test/non_recyclable/Juice Box 8.jpg",
        "ml/datasets/test/non_recyclable/Juice Box 12.jpg",
        "ml/datasets/test/non_recyclable/Milk Carton 14.jpg",
        "ml/datasets/test/non_recyclable/Styrofoam 20.jpg",
        "ml/datasets/test/non_recyclable/Styrofoam 37.jpg",
        "ml/datasets/test/non_recyclable/Utensil 20.jpg",
        "ml/datasets/test/non_recyclable/Utensil 35.jpg"
    ]

    results = []
    correct = 0
    total = len(test_images)

    print("Running predictions on 10 sample images...\n")
    print(f"{'#':<3} {'Image':<20} {'Prediction':<30} {'Result':<20} {'Conf'}")
    print("-" * 80)

    for i, url in enumerate(test_images):
        try:
            result = predict_image(url)
            results.append(result)

            expected_recyclable = i < 5  # First 5 are recyclable
            is_correct = result["recyclable"] == expected_recyclable
            status = "Correct" if is_correct else "Wrong"

            if is_correct:
                correct += 1
            
            img_name = result["image"][:18] + "..." if len(result["image"]) > 18 else result["image"]
            print(f"{i+1:<3} {img_name:<20} {result['top_prediction'][:28]:<30} {result['category']:<20} {result['confidence']:.3f} {status}")

        except Exception as e:
            print(f"{i+1:<3} ERROR: {e}")
            results.append({"image": url, "error": str(e)})

    accuracy = correct / total
    print("\n" + "="*80)
    print(f"FINAL RESULT: {correct}/{total} correct → Accuracy: {accuracy:.1%}")
    print("="*80)

    # Save full report
    summary = {
        "model": "MobileNetV2 (ImageNet pretrained)",
        "approach": "Zero-shot classification with keyword mapping",
        "total_images": total,
        "correct": correct,
        "accuracy": accuracy,
        "results": results
    }

    os.makedirs("results", exist_ok=True)
    with open("results/mobilenetv2_results.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Generate Markdown report
    md = f"""# MobileNetV2 Zero-Shot Recycling Classifier Results

**Model**: MobileNetV2 (pretrained on ImageNet)  
**Method**: Top-1 ImageNet label => keyword-based recyclable mapping

## Summary
- Images tested: {total}
- Correct predictions: {correct}
- **Accuracy**: {accuracy:.1%}

## Detailed Results

| # | Image | Top Prediction | Confidence | Category | Correct |
|---|-------|----------------|------------|----------|---------|
"""

    for i, r in enumerate(results):
        if "error" in r:
            md += f"| {i+1} | {r['image'][:15]} | ERROR | - | - | Wrong |\n"
            continue
        status = "Correct" if (i < 5) == r["recyclable"] else "Wrong"
        md += f"| {i+1} | {r['image'][:15]} | {r['top_prediction'][:20]} | {r['confidence']:.3f} | {r['category'][:15]} | {status} |\n"

    with open("results/mobilenetv2_results.md", "w") as f:
        f.write(md)

    print("\nFull report saved to: results/mobilenetv2_results.md")

if __name__ == "__main__":
    run_tests()
