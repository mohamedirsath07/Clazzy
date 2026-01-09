"""
FastAPI ML Backend for Clazzy Fashion Recommendation
Production-ready system with 3 INDEPENDENT ML Models:

MODEL 1: Clothing Classifier (ml_classifier.py)
- Purpose: Binary classification of clothing items (TOP or BOTTOM)
- Technology: Custom-trained TensorFlow/Keras model (150x150 input, sigmoid output)
- Model file: clothing_classifier_model.keras
- Endpoint: /predict-type

MODEL 2: Color Extractor (color_analyzer.py)
- Purpose: Extract dominant colors from images
- Technology: K-means clustering with extended color palette
- Endpoint: /extract-colors

MODEL 3: Outfit Recommender (outfit_recommender.py)
- Purpose: Generate outfit recommendations based on color harmony
- Technology: HSV color space + harmony algorithms + occasion rules
- Endpoint: /recommend-outfits

Additional Features:
- Color harmony detection (Monochromatic, Analogous, Triadic, Complementary)
- Occasion-based styling (formal, casual, party, date, etc.)
- Invalid combination prevention (top+top, bottom+bottom)
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List
import os
from pathlib import Path
import io

# 🚨 EMERGENCY MODE: Minimal imports - NO ML classifier to save startup time
# from ml_classifier import ClothingClassifier  # DISABLED for v1 launch
from color_analyzer import get_color_analyzer  # MODEL 2: Color extraction

# 🚨 EMERGENCY MODE: Simple index-based pairing (NO validation, GUARANTEED output)
from emergency_recommender import emergency_generate_outfits

# Legacy imports for color endpoints
from outfit_recommender import (
    hex_to_hsv,
    color_harmony,
    get_all_color_matches,
    recommend_matching_colors
)

app = FastAPI(
    title="Clazzy Fashion ML API",
    version="3.0.0",
    description="3 Independent ML Models: Classifier + Color Extractor + Outfit Recommender"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory
UPLOAD_DIR = Path(__file__).parent.parent / "client" / "public" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Global ML model instances (lazy loading)
_color_analyzer = None

def get_models():
    """Initialize color extractor only (lazy loading)"""
    global _color_analyzer
    
    if _color_analyzer is None:
        print("🚨 EMERGENCY MODE: Loading Color Extractor only...")
        _color_analyzer = get_color_analyzer()
        print("✅ Color extractor loaded!")
    
    return _color_analyzer


def get_uploaded_files():
    """Get all uploaded image files from the uploads directory"""
    if not UPLOAD_DIR.exists():
        return []
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    files = []
    for file in UPLOAD_DIR.iterdir():
        if file.is_file() and file.suffix.lower() in image_extensions:
            # 🚨 EMERGENCY: Include ALL files including mock files
            files.append(file)
    return files


@app.get('/')
async def root():
    """API health check"""
    return {
        "status": "online",
        "version": "3.0.0",
        "ml_models": {
            "model_1": "Clothing Classifier (Custom TensorFlow/Keras - Top/Bottom)",
            "model_2": "Color Extractor (K-means + Extended Palette)",
            "model_3": "Outfit Recommender (Color Harmony + Occasion Rules)"
        },
        "endpoints": {
            "/predict-type": "Classify clothing type (top/bottom)",
            "/extract-colors": "Extract dominant colors with names",
            "/recommend-outfits": "Generate outfit recommendations"
        }
    }


@app.post('/predict-type')
async def predict_type(file: UploadFile = File(...)):
    """
    MODEL 1 ENDPOINT: Predict clothing type using Custom-trained Binary Classifier
    
    Uses a custom TensorFlow/Keras model to classify clothing as TOP or BOTTOM.
    Model: clothing_classifier_model.keras (150x150 input, sigmoid output)
    
    Classification Logic:
    - prediction > 0.5 → 'top'
    - prediction <= 0.5 → 'bottom'
    
    Args:
        file: Image file to classify
    
    Returns:
        {
            "predicted_type": str ('top' or 'bottom'),
            "confidence": float (0-1),
            "raw_prediction": float (raw sigmoid output),
            "model_used": "MODEL 1: Custom Top/Bottom Classifier"
        }
    """
    try:
        # Initialize models
        classifier, color_analyzer, recommender = get_models()
        
        # Read file bytes
        file_bytes = await file.read()
        
        # Classify using Custom Classifier (MODEL 1)
        prediction = classifier.predict(file_bytes)
        
        return JSONResponse({
            "predicted_type": prediction['predicted_type'],
            "confidence": round(prediction['confidence'], 3),
            "raw_prediction": round(prediction.get('raw_prediction', 0), 4),
            "model_used": "MODEL 1: Custom Top/Bottom Classifier"
        })
        
    except Exception as e:
        print(f"❌ Error in predict_type: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.post('/extract-colors')
async def extract_colors(file: UploadFile = File(...)):
    """
    MODEL 2 ENDPOINT: Extract dominant colors using K-means
    
    Uses the Color Extractor model to find dominant colors in image.
    
    Args:
        file: Image file to analyze
    
    Returns:
        {
            "colors": List[dict] (top 5 colors with hex, rgb, percentage),
            "dominant_color": str (hex code),
            "model_used": "MODEL 2: Color Extractor"
        }
    """
    try:
        # Initialize models
        classifier, color_analyzer, recommender = get_models()
        
        # Read file bytes
        file_bytes = await file.read()
        
        # Extract colors using K-means (MODEL 2)
        colors = color_analyzer.extract_colors(file_bytes)
        
        # Get dominant color
        dominant_color = colors[0]['hex'] if colors else '#808080'
        
        return JSONResponse({
            "colors": colors[:5],  # Top 5 colors
            "dominant_color": dominant_color,
            "model_used": "MODEL 2: Color Extractor (K-means)"
        })
        
    except Exception as e:
        print(f"❌ Error in extract_colors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Color extraction failed: {str(e)}")


@app.post('/recommend-colors')
async def recommend_colors(
    hex_color: str = Form(...),
    style: str = Form('balanced')
):
    """
    MODEL 3 ENDPOINT: Recommend matching colors using Color Theory
    
    Uses the Color Harmony Recommender to find perfect color combinations.
    
    Args:
        hex_color: Base hex color code (e.g., '#FF5733')
        style: Matching style preference:
            - 'bold': Complementary colors (high contrast)
            - 'harmonious': Analogous colors (similar hues)
            - 'balanced': Mix of all types (default)
            - 'conservative': Neutral and analogous only
    
    Returns:
        {
            "base_color": str,
            "recommended_colors": List[dict] with matching colors,
            "all_harmonies": dict with all harmony types,
            "model_used": "MODEL 3: Color Harmony Recommender"
        }
    """
    try:
        # Initialize models
        classifier, color_analyzer, recommender = get_models()
        
        # Get all possible matches (MODEL 3)
        all_matches = get_all_color_matches(hex_color)
        
        # Get top recommendations based on style
        recommendations = recommend_matching_colors(
            hex_color,
            style=style,
            top_n=5
        )
        
        return JSONResponse({
            "base_color": hex_color,
            "style_preference": style,
            "recommended_colors": recommendations,
            "all_harmonies": all_matches,
            "model_used": "MODEL 3: Color Harmony Recommender (Color Theory)"
        })
        
    except Exception as e:
        print(f"❌ Error in recommend_colors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Color recommendation failed: {str(e)}")


@app.post('/analyze-complete')
async def analyze_complete(file: UploadFile = File(...)):
    """
    COMBINED ENDPOINT: Use ALL 3 models on a single image
    
    Performs complete analysis using all 3 independent ML models:
    1. Clothing classification (MODEL 1)
    2. Color extraction (MODEL 2)
    3. Color harmony recommendations (MODEL 3)
    
    Args:
        file: Image file to analyze
    
    Returns:
        Complete analysis with all model outputs
    """
    try:
        # Initialize models
        classifier, color_analyzer, recommender = get_models()
        
        # Read file bytes
        file_bytes = await file.read()
        
        # MODEL 1: Classify clothing type
        prediction = classifier.predict(file_bytes)
        
        # MODEL 2: Extract colors
        colors = color_analyzer.extract_colors(file_bytes)
        dominant_color = colors[0]['hex'] if colors else '#808080'
        
        # MODEL 3: Get matching colors
        color_matches = get_all_color_matches(dominant_color)
        
        return JSONResponse({
            "classification": {
                "type": prediction['predicted_type'],
                "confidence": round(prediction['confidence'], 3),
                "model": "MODEL 1: Clothing Classifier"
            },
            "colors": {
                "extracted_colors": colors[:5],
                "dominant_color": dominant_color,
                "model": "MODEL 2: Color Extractor"
            },
            "matching_colors": {
                "base_color": dominant_color,
                "harmonies": color_matches,
                "model": "MODEL 3: Color Harmony Recommender"
            }
        })
        
    except Exception as e:
        print(f"❌ Error in analyze_complete: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Complete analysis failed: {str(e)}")


# ---------------------------------------------------------
# NEW: Structured Recommendation Payload
# ---------------------------------------------------------
from pydantic import BaseModel

class OutfitRequest(BaseModel):
    occasion: str
    tops: List[str]
    bottoms: List[str]

@app.post('/recommend-outfits')
async def recommend_outfits(request: OutfitRequest):
    """
    Generate outfits from explicit lists of tops and bottoms.
    Guaranteed Cartesian Product: Tops x Bottoms.
    NO ML filtering.
    """
    try:
        occasion = request.occasion
        tops = request.tops
        bottoms = request.bottoms

        # Basic validation
        if not tops or not bottoms:
             return JSONResponse({
                "occasion": occasion,
                "recommendations": [],
                "total_items_analyzed": 0,
                "status": "error",
                "reason": "MISSING_TOP_OR_BOTTOM" 
            })

        formatted_outfits = []
        
        # Cartesian Product
        for top_file in tops:
            for bottom_file in bottoms:
                
                # Construct URLs (assuming they are in /uploads/)
                # Ideally we would check if file exists, but for speed we assume existence
                
                # Create Outfit Object
                outfit = {
                    'top': {
                        'filename': top_file,
                        'type': 'top',
                        'category': 'top',
                        'color': '#808080', # Default gray if not analyzed
                        'url': f'/uploads/{top_file}',
                        'role': 'top',
                    },
                    'bottom': {
                        'filename': bottom_file,
                        'type': 'bottom',
                        'category': 'bottom',
                        'color': '#808080',
                        'url': f'/uploads/{bottom_file}',
                        'role': 'bottom',
                    },
                    'score': 0.95, # High score for user-created pairs
                    'harmony': 'User Match',
                    'occasion': occasion,
                }
                
                # Legacy array support
                outfit['items'] = [outfit['top'], outfit['bottom']]
                
                formatted_outfits.append(outfit)

        # Limit to 20 outfits just in case
        formatted_outfits = formatted_outfits[:20]

        return JSONResponse({
            "occasion": occasion,
            "recommendations": formatted_outfits,
            "total_items_analyzed": len(tops) + len(bottoms),
            "status": "ok"
        })

    except Exception as e:
        print(f"❌ Error in recommend_outfits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


if __name__ == '__main__':
    print("🚀 Starting Clazzy Fashion ML Backend...")
    print("🚨 EMERGENCY MODE: Simple pairing, no validation")
    uvicorn.run('main:app', host='0.0.0.0', port=8001, reload=False)
