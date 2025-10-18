import tensorflow as tf
import kagglehub
import pandas as pd
import os
os.environ["KAGGLEHUB_CACHE"] = "./kaggle_downloads"

dataset = "ashwinshrivastav/most-common-recyclable-and-nonrecyclable-objects"
kagglehub.dataset_download(dataset)

print("TensorFlow version:", tf.__version__)