# Clothing Outfit Recommendation System

A complete AI-powered outfit recommendation system with 3 models:

## Models

| Model | File | Purpose |
|-------|------|---------|
| Model 1 | `clothing_classifier_model.keras` | Classifies clothing as top/bottom |
| Model 2 | `color_extraction.py` | Extracts dominant color from images |
| Model 3 | `outfit_recommendation.py` | Generates outfit recommendations |

## Installation

1. Copy this entire folder to your project
2. Install required packages:

```bash
pip install tensorflow opencv-python scikit-learn pillow numpy
```

## Quick Start

```python
from clothing_analyzer import ClothingAnalyzer

# Initialize the analyzer
analyzer = ClothingAnalyzer()

# Analyze a single image
result = analyzer.analyze_image("path/to/shirt.jpg")
print(result)
# Output: {"name": "Shirt", "type": "top", "color": "Royal Blue", "hex": "#1f3c88"}

# Analyze multiple images and get outfit recommendations
wardrobe = analyzer.analyze_folder("path/to/wardrobe/")
recommendations = analyzer.recommend_outfits(wardrobe, occasion="formal")
print(recommendations)
```

## API Reference

### ClothingAnalyzer

```python
analyzer = ClothingAnalyzer(model_path="clothing_classifier_model.keras")
```

#### Methods:

- `analyze_image(image_path)` - Returns type + color for single image
- `analyze_folder(folder_path)` - Analyzes all images in folder
- `recommend_outfits(garments, occasion)` - Returns ranked outfit recommendations

#### Occasions:
- `formal`, `office`, `casual`, `party`, `date`, `college`

## Output Format

```json
{
  "outfit": ["Blue Shirt", "Black Jeans"],
  "types": ["top", "bottom"],
  "colors": ["Royal Blue", "Black"],
  "harmony": "Monochromatic",
  "occasion": "formal",
  "score": 1.15
}
```
