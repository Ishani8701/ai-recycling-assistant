from PIL import Image
import os
from pillow_heif import register_heif_opener
register_heif_opener()

tileImageFolder = ""
tileImageDimension = 800

smallTileImageFolder = ""
os.makedirs(smallTileImageFolder, exist_ok=True)

def isImageFile(path):
    for ext in [".jpg", ".png", ".jpeg"]:
        if path.lower().endswith(ext):
            return True
    return False

for fileName in os.listdir(tileImageFolder):
    fullPath = os.path.join(tileImageFolder, fileName)
    if os.path.isfile(fullPath) and isImageFile(fullPath):
        try:
            image = Image.open(fullPath).convert("RGB")
            width, height = image.size
            dimension = min(width, height)
            image = image.crop((0, 0, dimension, dimension))
            image = image.resize((tileImageDimension, tileImageDimension), resample=Image.Resampling.LANCZOS)
            image.save(os.path.join(smallTileImageFolder, fileName))
        except Exception as e:
            pass