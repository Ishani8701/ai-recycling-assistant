# MobileNetV2 Zero-Shot Recycling Classifier Results

**Model**: MobileNetV2 (pretrained on ImageNet)  
**Method**: Top-1 ImageNet label => keyword-based recyclable mapping

## Summary
- Images tested: 14
- Correct predictions: 12
- **Accuracy**: 85.7%

## Detailed Results

| # | Image | Top Prediction | Confidence | Category | Correct |
|---|-------|----------------|------------|----------|---------|
| 1 | Bottle 40.jpg | water_bottle | 0.664 | Recyclable | Correct |
| 2 | Bottle 76.jpg | water_bottle | 0.413 | Recyclable | Correct |
| 3 | Bottle 69.jpg | water_bottle | 0.497 | Recyclable | Correct |
| 4 | Can 23.jpg | spotlight | 0.362 | Non-recyclable  | Wrong |
| 5 | Can 30.jpg | oil_filter | 0.167 | Non-recyclable  | Wrong |
| 6 | Can 42.jpg | oil_filter | 0.189 | Non-recyclable  | Correct |
| 7 | Can 35.jpg | lighter | 0.258 | Non-recyclable  | Correct |
| 8 | Juice Box 8.jpg | croquet_ball | 0.203 | Non-recyclable  | Correct |
| 9 | Juice Box 12.jp | vending_machine | 0.168 | Non-recyclable  | Correct |
| 10 | Milk Carton 14. | eggnog | 0.780 | Non-recyclable  | Correct |
| 11 | Styrofoam 20.jp | tray | 0.119 | Non-recyclable  | Correct |
| 12 | Styrofoam 37.jp | tray | 0.093 | Non-recyclable  | Correct |
| 13 | Utensil 20.jpg | maraca | 0.500 | Non-recyclable  | Correct |
| 14 | Utensil 35.jpg | spatula | 0.977 | Non-recyclable  | Correct |
