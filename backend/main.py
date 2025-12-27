"""
FastAPI ML Backend for Clazzy Fashion Recommendation
Production-ready system with 3 INDEPENDENT ML Models:

MODEL 1: Clothing Classifier (ml_classifier.py)
- Purpose: Classify clothing items (top/bottom/dress/shoes/blazer)
- Technology: ResNet50 transfer learning
- Endpoint: /predict-type

MODEL 2: Color Extractor (color_analyzer.py)
- Purpose: Extract dominant colors from images
- Technology: K-means clustering
- Endpoint: /extract-colors

MODEL 3: Color Harmony Recommender (color_harmony.py)
- Purpose: Recommend matching colors based on color theory
- Technology: HSV color space + harmony algorithms
- Endpoint: /recommend-colors

Additional Features:
- Outfit recommendation combining all 3 models
- Occasion-based styling
- Deep learning embeddings for style matching
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List
import os
from pathlib import Path
import io

# Import the 3 independent ML models
from ml_classifier_improved import ImprovedClothingClassifier as ClothingClassifier  # Use improved version
from color_analyzer import get_color_analyzer
from color_harmony import get_color_harmony_recommender
from outfit_recommender import get_outfit_recommender

app = FastAPI(
    title="Clazzy Fashion ML API",
    version="3.0.0",
    description="3 Independent ML Models: Classifier + Color Extractor + Harmony Recommender"
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
_classifier = None
_color_analyzer = None
_color_harmony = None
_recommender = None

def get_models():
    """Initialize all 3 independent ML models on first request (lazy loading)"""
    global _classifier, _color_analyzer, _color_harmony, _recommender
    
    if _classifier is None:
        print("🚀 Loading 3 Independent ML Models...")
        print("   [1/3] Clothing Classifier (Improved Multi-Signal)...")
        _classifier = ClothingClassifier()
        print("   [2/3] Color Extractor (K-means)...")
        _color_analyzer = get_color_analyzer()
        print("   [3/3] Color Harmony Recommender (Color Theory)...")
        _color_harmony = get_color_harmony_recommender()
        print("   [+] Outfit Recommender (Integration Layer)...")
        _recommender = get_outfit_recommender()
        print("✅ All ML models loaded successfully!")
    
    return _classifier, _color_analyzer, _color_harmony, _recommender


def get_uploaded_files():
    """Get all uploaded image files from the uploads directory"""
    if not UPLOAD_DIR.exists():
        return []
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    files = []
    for file in UPLOAD_DIR.iterdir():
        if file.is_file() and file.suffix.lower() in image_extensions:
            # Skip mock files
            if not file.name.startswith('mock_'):
                files.append(file)
    return files


@app.get('/')
async def root():
    """API health check"""
    return {
        "status": "online",
        "version": "3.0.0",
        "ml_models": {
            "model_1": "Clothing Classifier (ResNet50)",
            "model_2": "Color Extractor (K-means)",
            "model_3": "Color Harmony Recommender (Color Theory)"
        },
        "endpoints": {
            "/predict-type": "Classify clothing type",
            "/extract-colors": "Extract dominant colors",
            "/recommend-colors": "Get matching color combinations",
            "/recommend-outfits": "Generate complete outfit recommendations"
        }
    }


@app.post('/predict-type')
async def predict_type(file: UploadFile = File(...)):
    """
    MODEL 1 ENDPOINT: Predict clothing type using Improved Multi-Signal Classifier
    
    Uses the Clothing Classifier model to determine clothing category.
    Uses multiple signals: aspect ratio, edge detection, color patterns, deep features.
    
    Args:
        file: Image file to classify
    
    Returns:
        {
            "predicted_type": str (top/bottom/dress/shoes/blazer/other),
            "confidence": float (0-1),
            "model_used": "MODEL 1: Improved Clothing Classifier"
        }
    """
    try:
        # Initialize models
        classifier, color_analyzer, color_harmony, _ = get_models()
        
        # Read file bytes
        file_bytes = await file.read()
        
        # Classify using Improved Classifier (MODEL 1)
        prediction = classifier.predict(file_bytes)
        
        return JSONResponse({
            "predicted_type": prediction['predicted_type'],
            "confidence": round(prediction['confidence'], 3),
            "model_used": "MODEL 1: Improved Multi-Signal Classifier"
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
        classifier, color_analyzer, color_harmony, _ = get_models()
        
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
        classifier, color_analyzer, color_harmony, _ = get_models()
        
        # Get all possible matches (MODEL 3)
        all_matches = color_harmony.get_all_matches(hex_color)
        
        # Get top recommendations based on style
        recommendations = color_harmony.recommend_matching_colors(
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
        classifier, color_analyzer, color_harmony, _ = get_models()
        
        # Read file bytes
        file_bytes = await file.read()
        
        # MODEL 1: Classify clothing type
        prediction = classifier.predict(file_bytes)
        
        # MODEL 2: Extract colors
        colors = color_analyzer.extract_colors(file_bytes)
        dominant_color = colors[0]['hex'] if colors else '#808080'
        
        # MODEL 3: Get matching colors
        color_matches = color_harmony.get_all_matches(dominant_color)
        
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


@app.post('/recommend-outfits')
async def recommend_outfits(occasion: str = Form(...), max_items: int = Form(2)):
    """
    Generate intelligent outfit recommendations using ALL 3 MODELS
    
    Integration of all 3 independent ML models:
    - MODEL 1: Classify each item's type
    - MODEL 2: Extract dominant colors
    - MODEL 3: Calculate color harmony scores
    
    Plus additional logic:
    - Deep learning style embeddings for similarity
    - Occasion-based matching rules
    
    Args:
        occasion: Event type (casual/formal/business/party/date/sports)
        max_items: Items per outfit (default: 2)
    
    Returns:
        {
            "occasion": str,
            "recommendations": List[dict] with scored outfits,
            "total_items_analyzed": int,
            "models_used": ["MODEL 1", "MODEL 2", "MODEL 3"]
        }
    """
    try:
        # Initialize models
        classifier, color_analyzer, color_harmony, recommender = get_models()
        
        # Get all uploaded files
        uploaded_files = get_uploaded_files()
        
        if not uploaded_files:
            return JSONResponse({
                "occasion": occasion,
                "recommendations": [],
                "total_items_analyzed": 0,
                "message": "No images uploaded yet"
            })
        
        # Analyze each uploaded file using ALL 3 MODELS
        analyzed_items = []
        
        print(f"\n🔍 Analyzing {len(uploaded_files)} uploaded files...")
        
        for file_path in uploaded_files:
            try:
                # Read file
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
                
                # MODEL 1: Classify with ResNet50
                prediction = classifier.predict(file_bytes)
                
                # MODEL 2: Extract colors with K-means
                colors = color_analyzer.extract_colors(file_bytes)
                dominant_color = colors[0]['hex'] if colors else '#808080'
                
                # Log classification results
                print(f"  📸 {file_path.name}")
                print(f"     Type: {prediction['predicted_type']} (confidence: {prediction['confidence']:.2%})")
                print(f"     Color: {dominant_color}")
                
                # Create item data
                item = {
                    'id': file_path.name,
                    'type': prediction['predicted_type'],
                    'colors': colors,
                    'dominant_color': dominant_color,
                    'features': prediction['features'],  # Deep learning embeddings
                    'url': f'/uploads/{file_path.name}'
                }
                
                analyzed_items.append(item)
                
            except Exception as e:
                print(f"⚠️ Error analyzing {file_path.name}: {str(e)}")
                continue
        
        print(f"\n📊 Classification Summary:")
        item_types = {}
        for item in analyzed_items:
            item_type = item['type']
            item_types[item_type] = item_types.get(item_type, 0) + 1
        for item_type, count in item_types.items():
            print(f"   {item_type}: {count} items")
        
        if not analyzed_items:
            return JSONResponse({
                "occasion": occasion,
                "recommendations": [],
                "total_items_analyzed": 0,
                "message": "Failed to analyze uploaded images"
            })
        
        # Generate outfit recommendations
        # (Recommender internally uses MODEL 3 for color harmony scoring)
        outfits = recommender.recommend_outfits(
            clothing_items=analyzed_items,
            occasion=occasion,
            max_outfits=5,
            items_per_outfit=max_items
        )
        
        # Format response
        formatted_outfits = []
        for outfit in outfits:
            formatted_items = []
            for item in outfit['items']:
                formatted_items.append({
                    'filename': item['id'],
                    'type': item['type'],
                    'category': item['type'],
                    'color': item['dominant_color'],
                    'url': item['url']
                })
            
            formatted_outfits.append({
                'items': formatted_items,
                'score': round(outfit['score'], 3),
                'total_items': outfit['total_items']
            })
        
        return JSONResponse({
            "occasion": occasion,
            "recommendations": formatted_outfits,
            "total_items_analyzed": len(analyzed_items),
            "models_used": [
                "MODEL 1: Clothing Classifier",
                "MODEL 2: Color Extractor",
                "MODEL 3: Color Harmony Recommender"
            ]
        })
        
    except Exception as e:
        print(f"❌ Error in recommend_outfits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


if __name__ == '__main__':
    print("🚀 Starting Clazzy Fashion ML Backend...")
    print("📊 3 Independent ML Models:")
    print("   [1] Clothing Classifier (ResNet50)")
    print("   [2] Color Extractor (K-means)")
    print("   [3] Color Harmony Recommender (Color Theory)")
    uvicorn.run('main:app', host='0.0.0.0', port=8001, reload=True)
