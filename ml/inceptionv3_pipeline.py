import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import pandas as pd
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from tqdm import tqdm
import random

# Set random seeds for reproducibility
random.seed(42)
tf.random.set_seed(42)

class RecyclingClassifier:
    def __init__(self):
        # Load pre-trained InceptionV3 model
        self.model = InceptionV3(weights='imagenet')
        
        # Define mapping from ImageNet classes to recyclable/non-recyclable
        self.recyclable_keywords = [
            'bottle', 'can', 'jar', 'box', 'paper', 'cardboard', 'newspaper',
            'magazine', 'envelope', 'carton', 'container', 'aluminum', 'glass',
            'plastic', 'metal', 'tin', 'steel', 'beverage', 'soda', 'water'
        ]
        
        self.non_recyclable_keywords = [
            'food', 'trash', 'garbage', 'waste', 'diaper', 'styrofoam',
            'plastic bag', 'wrap', 'straw', 'utensil', 'cigarette', 'ceramic',
            'mirror', 'light bulb', 'window', 'pizza box', 'tissue', 'napkin',
            'paper towel', 'wax paper', 'photograph', 'aerosol', 'hazardous',
            'medical', 'syringe', 'needle', 'battery'
        ]
    
    def preprocess_image(self, img_path):
        """Preprocess image for InceptionV3 model"""
        img = image.load_img(img_path, target_size=(299, 299))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        return preprocess_input(img_array)
    
    def predict_recyclable(self, img_path):
        """Predict if an image is recyclable or not"""
        # Preprocess image
        processed_img = self.preprocess_image(img_path)
        
        # Get predictions
        predictions = self.model.predict(processed_img, verbose=0)
        decoded_predictions = decode_predictions(predictions, top=5)[0]
        
        # Convert predictions to readable format and calculate recyclable confidence
        recyclable_confidence = 0.0
        non_recyclable_confidence = 0.0
        preds = []
        
        for _, label, score in decoded_predictions:
            is_recyclable = self._is_recyclable(label)
            if is_recyclable:
                recyclable_confidence += score
            else:
                non_recyclable_confidence += score
                
            preds.append({
                'label': label,
                'score': float(score),
                'is_recyclable': is_recyclable
            })
        
        # Normalize confidences
        total = recyclable_confidence + non_recyclable_confidence
        if total > 0:
            recyclable_confidence /= total
            non_recyclable_confidence /= total
        
        # Determine final prediction
        is_recyclable = recyclable_confidence >= non_recyclable_confidence
        confidence = max(recyclable_confidence, non_recyclable_confidence)
        label = 'recyclable' if is_recyclable else 'non-recyclable'
        
        # Get the top predicted class name for backward compatibility
        top_prediction = preds[0]['label'] if preds else 'unknown'
        
        return {
            'label': label,  # New format: 'recyclable' or 'non-recyclable'
            'top_prediction': top_prediction,  # For backward compatibility
            'confidence': float(confidence),
            'is_recyclable': is_recyclable,
            'all_predictions': preds
        }
    
    def _is_recyclable(self, label):
        """Determine if a label is recyclable based on keywords"""
        label_lower = label.lower()
        
        # Check for recyclable keywords
        if any(keyword in label_lower for keyword in self.recyclable_keywords):
            return True
        
        # Check for non-recyclable keywords
        if any(keyword in label_lower for keyword in self.non_recyclable_keywords):
            return False
        
        # Default to non-recyclable if uncertain
        return False

def load_dataset(dataset_path, split='test', max_images_per_class=10):
    """
    Load and prepare dataset for evaluation
    
    Args:
        dataset_path: Path to the dataset root directory
        split: Which split to use ('train', 'val', or 'test')
        max_images_per_class: Maximum number of images to load per class
    """
    image_paths = []
    true_labels = []
    
    # Define class directories
    class_dirs = {
        'recyclable': os.path.join(dataset_path, split, 'recyclable'),
        'non-recyclable': os.path.join(dataset_path, split, 'non-recyclable')
    }
    
    # Load images from both classes
    for label, is_recyclable in [('recyclable', True), ('non-recyclable', False)]:
        class_dir = class_dirs[label]
        if os.path.exists(class_dir):
            # Get all image files in the directory
            image_files = [f for f in os.listdir(class_dir) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            # Limit the number of images per class
            image_files = image_files[:max_images_per_class]
            
            # Add to our lists
            for img_name in image_files:
                image_paths.append(os.path.join(class_dir, img_name))
                true_labels.append(is_recyclable)
    
    print(f"Loaded {len(image_paths)} images from {split} set")
    return image_paths, true_labels

def evaluate_model(classifier, test_images, true_labels):
    """Evaluate model on test images and return results"""
    results = []
    
    for img_path, true_label in tqdm(zip(test_images, true_labels), total=len(test_images)):
        try:
            pred = classifier.predict_recyclable(img_path)
            results.append({
                'image': os.path.basename(img_path),
                'true_label': 'Recyclable' if true_label else 'Non-recyclable',
                'predicted_label': 'Recyclable' if pred['is_recyclable'] else 'Non-recyclable',
                'confidence': pred['confidence'],
                'top_prediction': pred['top_prediction'],
                'is_correct': (pred['is_recyclable'] == true_label)
            })
        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")
    
    return pd.DataFrame(results)

def save_results(results_df, output_dir='results'):
    """Save evaluation results to a markdown file"""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'inceptionv3_results.md')
    
    # Calculate accuracy
    accuracy = accuracy_score(
        results_df['true_label'] == 'Recyclable',
        results_df['predicted_label'] == 'Recyclable'
    )
    
    with open(output_file, 'w') as f:
        f.write("# InceptionV3 Recycling Classifier Evaluation\n\n")
        f.write(f"## Model: InceptionV3 (pretrained on ImageNet)\n")
        f.write(f"## Accuracy: {accuracy:.2%}\n\n")
        
        f.write("## Sample Predictions\n\n")
        f.write("| Image | True Label | Predicted Label | Confidence | Top Prediction | Correct? |\n")
        f.write("|-------|------------|-----------------|------------|-----------------|----------|\n")
        
        for _, row in results_df.iterrows():
            f.write(f"| {row['image']} | {row['true_label']} | {row['predicted_label']} | "
                   f"{row['confidence']:.2f} | {row['top_prediction']} | {row['is_correct']} |\n")
    
    print(f"Results saved to {output_file}")
    return output_file

def main():
    # Initialize classifier
    print("Loading InceptionV3 model...")
    classifier = RecyclingClassifier()
    
    # Load dataset (update this path to your dataset location)
    dataset_path = "data/recycling_dataset"  # Update this to your dataset path
    print(f"Loading dataset from {dataset_path}...")
    
    # Use the test split for evaluation
    test_images, true_labels = load_dataset(dataset_path, split='test')
    
    if not test_images:
        print("No test images found. Available directories in dataset:")
        if os.path.exists(dataset_path):
            print(os.listdir(dataset_path))
        return
    
    if not test_images:
        print("No images found in the dataset directory.")
        print("Please update the 'dataset_path' in the script to point to your dataset.")
        return
    
    print(f"Found {len(test_images)} images for testing.")
    
    # Evaluate model
    print("\nRunning predictions...")
    results_df = evaluate_model(classifier, test_images, true_labels)
    
    # Save results
    print("\nSaving results...")
    results_file = save_results(results_df)
    
    print("\nEvaluation complete!")
    print(f"Results saved to: {results_file}")
    
    # Print summary
    accuracy = accuracy_score(
        results_df['true_label'] == 'Recyclable',
        results_df['predicted_label'] == 'Recyclable'
    )
    print(f"\nModel Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    main()
