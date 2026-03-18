# Clazzy V2 - Upgrade Plan

## Executive Summary

Transform Clazzy from a basic top/bottom classifier with rule-based recommendations into a production-grade intelligent fashion assistant system.

---

## Phase 1: Foundation (Week 1-2)

### 1.1 Project Structure Migration
```bash
# Create V2 directory structure
mkdir -p clazzy_v2/{api,core,ml,data,external,models,scripts,config,tests}

# Install dependencies
pip install -r clazzy_v2/requirements.txt
```

### 1.2 Configuration Management
- [x] Create centralized config with environment variables
- [x] Set up Pydantic settings for type-safe configuration
- [ ] Create `.env.example` with required variables

### 1.3 Database Setup
```bash
# Initialize database
cd clazzy_v2
alembic init data/database/migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## Phase 2: Vision Upgrade (Week 2-3)

### 2.1 Multi-Class Classifier
**Current**: Binary classification (top/bottom)
**Upgrade**: 45+ clothing categories with EfficientNet-B0

```python
# Migration path
1. Keep existing MobileNetV2 model as fallback
2. Train new EfficientNet model on larger dataset
3. A/B test both models
4. Gradual rollout
```

**Required Dataset**:
- [DeepFashion](http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html)
- [Fashion Product Images](https://www.kaggle.com/paramaggarwal/fashion-product-images-dataset)
- Custom labeled data

### 2.2 Multi-Label Detection
Add detection for:
- Style attributes (casual, formal, streetwear, etc.)
- Pattern detection (solid, striped, floral, etc.)
- Season suitability

### 2.3 CLIP Integration
```python
# Add embedding capability
from core.vision.embedder import FashionEmbedder

embedder = FashionEmbedder()
embedding = embedder.embed_image(image)  # 512-dim vector
```

---

## Phase 3: Smart Recommendation Engine (Week 3-4)

### 3.1 Hybrid Scoring System

**Current V1 Approach**:
```python
# Rule-based only
score = color_harmony_score * 0.6 + occasion_score * 0.4
```

**V2 Hybrid Approach**:
```python
# Multi-signal scoring
score = (
    color_harmony * 0.30 +
    style_compatibility * 0.25 +
    occasion_match * 0.25 +
    embedding_similarity * 0.20
)
```

### 3.2 Outfit Validation
Add proper validation for:
- Required pieces (top + bottom or dress)
- 3-piece outfits (top + bottom + outerwear)
- Accessory combinations

### 3.3 ML-Based Ranking
Train a learning-to-rank model on:
- Liked/saved outfits (positive)
- Skipped/disliked outfits (negative)
- Fashion runway/editorial data

---

## Phase 4: Personalization Engine (Week 4-5)

### 4.1 User Profile Schema
```python
UserProfile:
    - Demographics (optional): gender, body_type, skin_tone
    - Explicit preferences: preferred_styles, avoided_styles
    - Learned preferences: style_affinity_scores (updated from feedback)
```

### 4.2 Feedback Loop
```
User Action → FeedbackEvent → PreferenceLearner → Updated Profile → Better Recommendations
```

### 4.3 Skin Tone Color Matching
Integrate color theory for skin tone recommendations:
- Fair: Navy, burgundy, forest green
- Medium: Mustard, rust, teal
- Dark: White, bright yellow, cobalt

---

## Phase 5: AI Assistant Layer (Week 5-6)

### 5.1 Intent Parsing
**Rule-based (fast)**:
```
"What should I wear for a date?" → IntentType.OCCASION_OUTFIT, occasion="date"
```

**LLM-enhanced (complex queries)**:
```
"I have a casual brunch but might go hiking after" → Multiple intents parsed
```

### 5.2 Natural Language Flow
```
User: "Match my black shirt"
→ Parse intent
→ Find black shirt in wardrobe
→ Generate outfits including black shirt
→ Format natural language response
```

---

## Phase 6: Context Awareness (Week 6)

### 6.1 Weather Integration
```python
# OpenWeatherMap API
weather = await weather_service.get_current(lat, lon)
context = weather.to_outfit_context()
# Returns: temperature, needs_layers, recommended_fabrics
```

### 6.2 Time-Based Recommendations
- Morning: Professional, work-appropriate
- Evening: Date-ready, event-appropriate
- Weekend: Casual, comfortable

---

## Phase 7: API & Integration (Week 6-7)

### 7.1 New Endpoints
| Endpoint | Purpose |
|----------|---------|
| `POST /api/v2/analyze` | Full image analysis |
| `POST /api/v2/recommend` | Get outfit recommendations |
| `POST /api/v2/assistant/query` | Natural language queries |
| `PATCH /api/v2/users/{id}` | Update user profile |
| `POST /api/v2/users/{id}/feedback` | Record feedback |

### 7.2 Performance Targets
- Response time < 2 seconds
- Support 10k concurrent users
- Model inference < 500ms

---

## Migration Strategy

### Backward Compatibility
```python
# Keep V1 endpoints working
@app.post("/predict-type")  # V1
async def predict_type_v1(file: UploadFile):
    # Forward to V2 with legacy response format
    result = await analyze_clothing(file)
    return {
        "type": result["classification"]["category"],  # Map to top/bottom
        "confidence": result["classification"]["type"]["primary"]["confidence"]
    }
```

### Database Migration
```python
# scripts/migrate_v1_data.py
async def migrate_wardrobe():
    # Read from V1 MongoDB
    v1_items = await v1_db.wardrobe.find().to_list()

    # Transform and insert to V2 PostgreSQL
    for item in v1_items:
        v2_item = transform_item(item)
        await v2_db.execute(insert(WardrobeItem).values(**v2_item))
```

---

## Tech Stack Recommendations

### Core Stack
| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| API Framework | FastAPI | Django REST |
| ML Framework | PyTorch | TensorFlow |
| Vision Model | EfficientNet-B0 | ResNet-50 |
| Embeddings | CLIP | FashionCLIP |
| Database | PostgreSQL | MongoDB |
| Cache | Redis | In-memory |
| Vector Store | FAISS | ChromaDB |
| LLM | Claude | GPT-4 |

### Why This Stack?
- **FastAPI**: Async, fast, auto-docs, type-safe
- **PyTorch**: Better for research/experimentation
- **EfficientNet**: Best accuracy/speed tradeoff
- **PostgreSQL**: Reliable, JSON support, full-text search
- **FAISS**: Free, fast, scales to millions

---

## Future Monetization Hooks (Not Implemented)

### Tier Structure (Code Ready, Not Active)
```python
class UserTier(str, Enum):
    FREE = "free"           # 10 outfits/day
    PREMIUM = "premium"     # Unlimited
    PRO = "pro"             # + AI assistant

# Middleware hook (inactive)
@app.middleware("http")
async def check_tier_limits(request, call_next):
    # Pass-through for now
    return await call_next(request)
```

### Analytics Events (Ready for Integration)
```python
# Track for business metrics
analytics.track("outfit_generated", {
    "user_id": user_id,
    "occasion": occasion,
    "items_in_wardrobe": len(wardrobe),
    "recommendations_shown": len(results)
})
```

### Affiliate/Shopping Links (Schema Ready)
```python
class ClothingItem:
    # ... existing fields ...
    purchase_links: Optional[List[PurchaseLink]] = None  # Ready for affiliate
```

---

## Deployment Checklist

### Pre-Launch
- [ ] Train multi-class classifier on fashion dataset
- [ ] Generate embeddings for sample wardrobe
- [ ] Load test API (target: 100 req/s)
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure Redis caching
- [ ] Set up CI/CD pipeline

### Launch
- [ ] Deploy to production
- [ ] Enable V2 endpoints
- [ ] Keep V1 endpoints for backward compatibility
- [ ] Monitor error rates and latency

### Post-Launch
- [ ] Collect user feedback
- [ ] A/B test recommendation algorithms
- [ ] Iterate on model based on feedback
- [ ] Add additional features based on usage patterns

---

## Success Metrics

| Metric | V1 Baseline | V2 Target |
|--------|-------------|-----------|
| Classification accuracy | ~70% (2 classes) | >85% (45 classes) |
| Outfit satisfaction rate | Not tracked | >75% likes |
| Response time | ~3s | <2s |
| User retention | New | >40% weekly |
| Outfits generated/user | ~5 | >15 |

---

## Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| 1. Foundation | Week 1-2 | Project structure, config |
| 2. Vision | Week 2-3 | Multi-class classifier |
| 3. Recommendation | Week 3-4 | Hybrid scoring engine |
| 4. Personalization | Week 4-5 | User profiles, feedback |
| 5. AI Assistant | Week 5-6 | Natural language interface |
| 6. Context | Week 6 | Weather integration |
| 7. Integration | Week 6-7 | API, migration, testing |

**Total: 7 weeks for MVP**
