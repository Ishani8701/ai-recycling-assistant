import os
import random
import tensorflow as tf
import keras
import kagglehub
import pandas as pd
from keras.preprocessing import image
import numpy as np

os.environ["KAGGLEHUB_CACHE"] = "./kaggle_downloads"

dataset = "ashwinshrivastav/most-common-recyclable-and-nonrecyclable-objects"
path = kagglehub.dataset_download(dataset)

print("TensorFlow version:", tf.__version__)

# Load pretrained MobileNetV2 as base model
base_model = keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False  # Freeze the base model for now

# Add classification head for binary classification (recyclable vs non-recyclable)
model = keras.Sequential([
    base_model,
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(2, activation='softmax')
])

# Find all image files in the dataset directory
image_extensions = ('.jpg', '.jpeg', '.png')
image_paths = []
for root, dirs, files in os.walk(path):
    for file in files:
        if file.lower().endswith(image_extensions):
            image_paths.append(os.path.join(root, file))
            print(os.path.join(root, file))

if not image_paths:
    raise ValueError("No images found in the dataset directory.")

# Select a random image
random_image_path = random.choice(image_paths)
print(f"Selected image: {random_image_path}")

# Load and preprocess the image
img = image.load_img(random_image_path, target_size=(224, 224))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
preprocessed_img = keras.applications.mobilenet_v2.preprocess_input(img_array)

# Run prediction
predictions = model.predict(preprocessed_img)
predicted_class_index = np.argmax(predictions, axis=1)[0]
classes = ['non_recyclable', 'recyclable']
predicted_class = classes[predicted_class_index]

print(f"Predicted class: {predicted_class}")
