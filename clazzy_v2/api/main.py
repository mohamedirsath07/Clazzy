"""
Clazzy V2 - FastAPI Main Application
Production-grade API with all endpoints
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional
from PIL import Image
import io
import logging
import time

from api.config import get_settings, Settings
from api.schemas.clothing import (
    ClothingAnalysisResponse,
    ClothingItem,
    ColorInfo
)
from api.schemas.outfit import (
    OutfitRecommendationRequest,
    OutfitRecommendationResponse,
    OutfitScoreRequest
)
from api.schemas.user import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    FeedbackRequest
)
from api.schemas.assistant import (
    AssistantQueryRequest,
    AssistantQueryResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instances
models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize models on startup, cleanup on shutdown"""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Load models
    try:
        from core.vision.classifier import ClothingClassifier
        models["classifier"] = ClothingClassifier(
            model_path=f"{settings.model_dir}/classifier/clothing_classifier.pt"
        )
        logger.info("Loaded clothing classifier")
    except Exception as e:
        logger.warning(f"Classifier not loaded: {e}")
        models["classifier"] = None

    try:
        from core.vision.embedder import FashionEmbedder
        models["embedder"] = FashionEmbedder()
        logger.info("Loaded fashion embedder")
    except Exception as e:
        logger.warning(f"Embedder not loaded: {e}")
        models["embedder"] = None

    # Initialize recommendation engine
    from core.recommendation.engine import RecommendationEngine
    models["recommender"] = RecommendationEngine(embedder=models.get("embedder"))

    # Initialize personalization engine
    from core.personalization.engine import PersonalizationEngine
    models["personalization"] = PersonalizationEngine()

    yield

    # Cleanup
    logger.info("Shutting down...")
    models.clear()


# Create FastAPI app
app = FastAPI(
    title="Clazzy V2 API",
    description="Intelligent Fashion Assistant API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_timing_header(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    return response


# ============================================
# Health & Info Endpoints
# ============================================

@app.get("/")
async def root():
    """API info and health check"""
    return {
        "name": "Clazzy V2 API",
        "version": "2.0.0",
        "status": "healthy",
        "models": {
            "classifier": models.get("classifier") is not None,
            "embedder": models.get("embedder") is not None,
            "recommender": models.get("recommender") is not None
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "models_loaded": {
            k: v is not None for k, v in models.items()
        }
    }


# ============================================
# Vision Endpoints
# ============================================

@app.post("/api/v2/analyze", response_model=ClothingAnalysisResponse)
async def analyze_clothing(file: UploadFile = File(...)):
    """
    Analyze a clothing item image

    Returns:
    - Clothing type (45+ categories)
    - Style attributes
    - Pattern detection
    - Season suitability
    - Color analysis
    - Fashion embedding (optional)
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        result = {}

        # Classification
        classifier = models.get("classifier")
        if classifier:
            classification = classifier.predict(image)
            result["classification"] = classification
        else:
            result["classification"] = {"error": "Classifier not loaded"}

        # Color analysis (using existing analyzer)
        try:
            from Fashion_Style.backend.color_analyzer import ColorAnalyzer
            analyzer = ColorAnalyzer()
            colors = analyzer.extract_colors(image)
            result["colors"] = colors
        except ImportError:
            # Use simple color extraction
            result["colors"] = _simple_color_extraction(image)

        # Generate embedding
        embedder = models.get("embedder")
        if embedder:
            embedding = embedder.embed_image(image)
            result["embedding_available"] = True
            # Don't send full embedding in response (large)
        else:
            result["embedding_available"] = False

        return result

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@app.post("/api/v2/classify")
async def classify_clothing(file: UploadFile = File(...)):
    """Classify clothing type only (faster)"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    classifier = models.get("classifier")
    if not classifier:
        raise HTTPException(503, "Classifier not available")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    result = classifier.predict(image)
    return result


@app.post("/api/v2/extract-colors")
async def extract_colors(file: UploadFile = File(...)):
    """Extract dominant colors from clothing image"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    try:
        from Fashion_Style.backend.color_analyzer import ColorAnalyzer
        analyzer = ColorAnalyzer()
        colors = analyzer.extract_colors(image)
        return {"colors": colors}
    except ImportError:
        return {"colors": _simple_color_extraction(image)}


# ============================================
# Recommendation Endpoints
# ============================================

@app.post("/api/v2/recommend", response_model=OutfitRecommendationResponse)
async def recommend_outfits(request: OutfitRecommendationRequest):
    """
    Generate outfit recommendations

    Input:
    - wardrobe: List of clothing items with their attributes
    - occasion: Target occasion (casual, formal, date, etc.)
    - user_id: User ID for personalization (optional)

    Returns:
    - Top 5 outfit combinations with scores and reasons
    """
    recommender = models.get("recommender")
    if not recommender:
        raise HTTPException(503, "Recommendation engine not available")

    # Convert request items to ClothingItem objects
    from core.recommendation.engine import ClothingItem
    wardrobe = []
    for item in request.wardrobe:
        wardrobe.append(ClothingItem(
            id=item.id,
            name=item.name,
            category=item.category,
            clothing_type=item.clothing_type,
            colors=item.colors,
            dominant_color_hue=item.dominant_color_hue or 0,
            style_tags=item.style_tags or [],
            pattern=item.pattern or "solid",
            seasons=item.seasons or ["all-season"]
        ))

    # Get user preferences
    user_prefs = None
    if request.user_id:
        personalization = models.get("personalization")
        if personalization:
            user_prefs = personalization.get_recommendation_context(request.user_id)

    # Generate recommendations
    recommendations = recommender.generate_outfits(
        wardrobe=wardrobe,
        occasion=request.occasion,
        user_preferences=user_prefs,
        top_k=request.top_k or 5
    )

    # Format response
    return {
        "recommendations": [
            {
                "items": [item.id for item in rec.items],
                "score": rec.score,
                "reasons": rec.reasons,
                "harmony_type": rec.harmony_type,
                "occasion_match": rec.occasion_match,
                "style_coherence": rec.style_coherence
            }
            for rec in recommendations
        ],
        "occasion": request.occasion,
        "personalized": user_prefs is not None
    }


@app.post("/api/v2/score-outfit")
async def score_outfit(request: OutfitScoreRequest):
    """Score a specific outfit combination"""
    recommender = models.get("recommender")
    if not recommender:
        raise HTTPException(503, "Recommendation engine not available")

    from core.recommendation.engine import ClothingItem
    items = [
        ClothingItem(
            id=item.id,
            name=item.name,
            category=item.category,
            clothing_type=item.clothing_type,
            colors=item.colors,
            dominant_color_hue=item.dominant_color_hue or 0,
            style_tags=item.style_tags or [],
            pattern=item.pattern or "solid",
            seasons=item.seasons or ["all-season"]
        )
        for item in request.items
    ]

    result = recommender.score_outfit(
        items=items,
        occasion=request.occasion
    )

    return {
        "score": result.score,
        "reasons": result.reasons,
        "harmony_type": result.harmony_type,
        "occasion_match": result.occasion_match,
        "style_coherence": result.style_coherence,
        "breakdown": result.breakdown
    }


# ============================================
# User Profile Endpoints
# ============================================

@app.post("/api/v2/users", response_model=UserProfileResponse)
async def create_user_profile(profile: UserProfileCreate):
    """Create a new user profile"""
    personalization = models.get("personalization")
    if not personalization:
        raise HTTPException(503, "Personalization engine not available")

    user = personalization.update_profile(
        user_id=profile.user_id,
        updates=profile.dict(exclude={"user_id"}, exclude_none=True)
    )

    return user.to_dict()


@app.get("/api/v2/users/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """Get user profile"""
    personalization = models.get("personalization")
    if not personalization:
        raise HTTPException(503, "Personalization engine not available")

    profile = personalization.get_profile(user_id)
    return profile.to_dict()


@app.patch("/api/v2/users/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, updates: UserProfileUpdate):
    """Update user profile"""
    personalization = models.get("personalization")
    if not personalization:
        raise HTTPException(503, "Personalization engine not available")

    profile = personalization.update_profile(
        user_id=user_id,
        updates=updates.dict(exclude_none=True)
    )

    return profile.to_dict()


@app.post("/api/v2/users/{user_id}/feedback")
async def record_feedback(user_id: str, request: FeedbackRequest):
    """Record user feedback on outfit"""
    personalization = models.get("personalization")
    if not personalization:
        raise HTTPException(503, "Personalization engine not available")

    from core.personalization.engine import FeedbackEvent

    event = FeedbackEvent(
        user_id=user_id,
        outfit_id=request.outfit_id,
        action=request.action,
        outfit_items=request.outfit_items,
        occasion=request.occasion
    )

    profile = personalization.record_feedback(event)

    return {
        "status": "recorded",
        "new_engagement_score": min(profile.total_outfits_liked / 100, 1.0)
    }


# ============================================
# AI Assistant Endpoints
# ============================================

@app.post("/api/v2/assistant/query", response_model=AssistantQueryResponse)
async def process_assistant_query(request: AssistantQueryRequest):
    """
    Process natural language fashion query

    Examples:
    - "What should I wear for a date tonight?"
    - "Match my black shirt"
    - "Suggest a casual summer outfit"
    """
    try:
        from core.assistant.intent_parser import FashionAssistant

        assistant = FashionAssistant(
            recommendation_engine=models.get("recommender"),
            personalization_engine=models.get("personalization"),
            use_llm=request.use_llm
        )

        response = assistant.process_query(
            query=request.query,
            user_id=request.user_id,
            wardrobe=request.wardrobe,
            context=request.context
        )

        return response

    except Exception as e:
        logger.error(f"Assistant query failed: {e}")
        raise HTTPException(500, f"Failed to process query: {str(e)}")


# ============================================
# Wardrobe Management Endpoints
# ============================================

@app.post("/api/v2/wardrobe/analyze")
async def analyze_wardrobe(files: List[UploadFile] = File(...)):
    """
    Analyze multiple wardrobe items

    Upload multiple clothing images to get analysis and auto-tagging
    """
    if len(files) > 20:
        raise HTTPException(400, "Maximum 20 images per request")

    results = []
    classifier = models.get("classifier")

    for file in files:
        if not file.content_type.startswith("image/"):
            results.append({"filename": file.filename, "error": "Not an image"})
            continue

        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))

            result = {"filename": file.filename}

            if classifier:
                classification = classifier.predict(image)
                result["classification"] = classification

            results.append(result)

        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})

    return {"items": results, "count": len(results)}


@app.post("/api/v2/wardrobe/suggestions")
async def get_wardrobe_suggestions(request: dict):
    """
    Get suggestions for wardrobe gaps and capsule wardrobe

    Input wardrobe items, get suggestions for:
    - Missing essentials
    - Capsule wardrobe recommendations
    - Versatile pieces to add
    """
    wardrobe = request.get("wardrobe", [])

    # Analyze wardrobe composition
    categories = {}
    for item in wardrobe:
        cat = item.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    suggestions = []

    # Check for missing categories
    essentials = {"top", "bottom", "outerwear"}
    missing = essentials - set(categories.keys())
    for cat in missing:
        suggestions.append({
            "type": "missing_essential",
            "category": cat,
            "message": f"Consider adding {cat}s to your wardrobe"
        })

    # Check for basic items
    has_white_top = any(
        item.get("category") == "top" and
        any(c.get("name", "").lower() == "white" for c in item.get("colors", []))
        for item in wardrobe
    )
    if not has_white_top:
        suggestions.append({
            "type": "versatile_piece",
            "item": "white t-shirt",
            "message": "A white t-shirt is a versatile essential"
        })

    has_dark_jeans = any(
        item.get("clothing_type") == "jeans" and
        any(c.get("name", "").lower() in ["navy", "dark blue", "black"]
            for c in item.get("colors", []))
        for item in wardrobe
    )
    if not has_dark_jeans:
        suggestions.append({
            "type": "versatile_piece",
            "item": "dark jeans",
            "message": "Dark jeans work for both casual and semi-formal"
        })

    return {
        "wardrobe_stats": categories,
        "suggestions": suggestions,
        "total_items": len(wardrobe)
    }


# ============================================
# Context Endpoints
# ============================================

@app.get("/api/v2/context/weather")
async def get_weather_context(lat: float, lon: float):
    """Get weather context for location-aware recommendations"""
    settings = get_settings()

    if not settings.weather_api_key:
        return {"error": "Weather API not configured", "default": "mild"}

    try:
        from external.weather import WeatherService
        weather_service = WeatherService(settings.weather_api_key)
        weather = await weather_service.get_current(lat, lon)
        return weather
    except Exception as e:
        logger.warning(f"Weather fetch failed: {e}")
        return {"error": str(e), "default": "mild"}


# ============================================
# Helper Functions
# ============================================

def _simple_color_extraction(image: Image.Image) -> List[dict]:
    """Simple color extraction fallback"""
    import numpy as np
    from sklearn.cluster import KMeans

    # Resize for speed
    image = image.convert("RGB").resize((100, 100))
    pixels = np.array(image).reshape(-1, 3)

    # Filter out extremes
    mask = (pixels.min(axis=1) > 10) & (pixels.max(axis=1) < 245)
    pixels = pixels[mask]

    if len(pixels) < 10:
        return [{"hex": "#808080", "name": "Gray", "percentage": 100}]

    # Cluster
    kmeans = KMeans(n_clusters=min(5, len(pixels)), random_state=42)
    kmeans.fit(pixels)

    # Get colors
    colors = []
    labels = kmeans.labels_
    for i, center in enumerate(kmeans.cluster_centers_):
        pct = (labels == i).sum() / len(labels) * 100
        r, g, b = map(int, center)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        colors.append({
            "hex": hex_color,
            "rgb": [r, g, b],
            "percentage": round(pct, 1),
            "name": _closest_color_name(r, g, b)
        })

    colors.sort(key=lambda x: -x["percentage"])
    return colors


def _closest_color_name(r: int, g: int, b: int) -> str:
    """Get closest color name"""
    # Simple color mapping
    h = max(r, g, b)
    l = min(r, g, b)

    if h - l < 30:  # Grayscale
        if h < 50:
            return "Black"
        elif h > 200:
            return "White"
        else:
            return "Gray"

    if r > g and r > b:
        return "Red" if r > 200 else "Dark Red"
    elif g > r and g > b:
        return "Green" if g > 200 else "Dark Green"
    elif b > r and b > g:
        return "Blue" if b > 200 else "Navy"
    elif r > 200 and g > 200:
        return "Yellow"
    elif r > 150 and b > 150:
        return "Purple"
    else:
        return "Brown"


# ============================================
# Run with: uvicorn api.main:app --reload --port 8001
# ============================================
