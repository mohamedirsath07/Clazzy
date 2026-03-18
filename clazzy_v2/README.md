# Clazzy V2 - Intelligent Fashion Assistant

## Project Structure

```
clazzy_v2/
├── api/                          # FastAPI Application
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Configuration management
│   ├── dependencies.py           # Dependency injection
│   │
│   ├── routers/                  # API Routes
│   │   ├── __init__.py
│   │   ├── wardrobe.py           # Wardrobe management endpoints
│   │   ├── outfits.py            # Outfit recommendation endpoints
│   │   ├── assistant.py          # AI assistant endpoints
│   │   ├── users.py              # User profile endpoints
│   │   └── analytics.py          # Usage analytics endpoints
│   │
│   ├── middleware/               # Custom Middleware
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication
│   │   ├── rate_limit.py         # Rate limiting
│   │   └── logging.py            # Request logging
│   │
│   └── schemas/                  # Pydantic Schemas
│       ├── __init__.py
│       ├── clothing.py           # Clothing item schemas
│       ├── outfit.py             # Outfit schemas
│       ├── user.py               # User schemas
│       └── assistant.py          # Assistant query schemas
│
├── core/                         # Core Business Logic
│   ├── __init__.py
│   │
│   ├── vision/                   # Computer Vision Services
│   │   ├── __init__.py
│   │   ├── classifier.py         # Multi-class clothing classifier
│   │   ├── attribute_detector.py # Style, pattern, season detection
│   │   ├── color_analyzer.py     # Enhanced color extraction
│   │   └── embedder.py           # CLIP/Fashion embeddings
│   │
│   ├── recommendation/           # Recommendation Engine
│   │   ├── __init__.py
│   │   ├── engine.py             # Main recommendation orchestrator
│   │   ├── harmony.py            # Color harmony rules
│   │   ├── ranker.py             # ML-based outfit ranking
│   │   ├── scorer.py             # Hybrid scoring system
│   │   └── context.py            # Context-aware adjustments
│   │
│   ├── personalization/          # Personalization Engine
│   │   ├── __init__.py
│   │   ├── profile.py            # User profile management
│   │   ├── preferences.py        # Style preference learning
│   │   └── feedback.py           # Feedback processing
│   │
│   ├── assistant/                # AI Assistant Layer
│   │   ├── __init__.py
│   │   ├── intent_parser.py      # Query intent extraction
│   │   ├── llm_bridge.py         # LLM integration (Claude/OpenAI)
│   │   └── response_builder.py   # Response formatting
│   │
│   └── wardrobe/                 # Wardrobe Intelligence
│       ├── __init__.py
│       ├── analyzer.py           # Wardrobe analysis
│       ├── suggestions.py        # Missing items, capsule wardrobe
│       └── combinations.py       # Outfit combination generator
│
├── ml/                           # Machine Learning Pipeline
│   ├── __init__.py
│   │
│   ├── training/                 # Model Training
│   │   ├── __init__.py
│   │   ├── classifier_trainer.py # Classification model training
│   │   ├── ranker_trainer.py     # Outfit ranker training
│   │   └── data_loader.py        # Dataset loading utilities
│   │
│   ├── evaluation/               # Model Evaluation
│   │   ├── __init__.py
│   │   ├── metrics.py            # Evaluation metrics
│   │   └── benchmark.py          # Benchmark utilities
│   │
│   └── registry/                 # Model Registry
│       ├── __init__.py
│       └── model_manager.py      # Model versioning and loading
│
├── data/                         # Data Layer
│   ├── __init__.py
│   │
│   ├── database/                 # Database Management
│   │   ├── __init__.py
│   │   ├── connection.py         # Database connections
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   └── migrations/           # Alembic migrations
│   │
│   ├── repositories/             # Data Access Layer
│   │   ├── __init__.py
│   │   ├── user_repo.py          # User data access
│   │   ├── wardrobe_repo.py      # Wardrobe data access
│   │   └── outfit_repo.py        # Outfit history data access
│   │
│   ├── cache/                    # Caching Layer
│   │   ├── __init__.py
│   │   └── redis_cache.py        # Redis caching utilities
│   │
│   └── vector_store/             # Vector Database
│       ├── __init__.py
│       └── faiss_store.py        # FAISS vector storage
│
├── external/                     # External Service Integrations
│   ├── __init__.py
│   ├── weather.py                # Weather API integration
│   ├── storage.py                # Cloud storage (S3/GCS)
│   └── llm.py                    # LLM API clients
│
├── models/                       # Trained Model Files
│   ├── classifier/               # Classification models
│   ├── embeddings/               # Embedding models
│   └── ranker/                   # Ranking models
│
├── tests/                        # Test Suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
│
├── scripts/                      # Utility Scripts
│   ├── train_classifier.py       # Train classification model
│   ├── train_ranker.py           # Train ranking model
│   ├── generate_embeddings.py    # Generate fashion embeddings
│   └── migrate_v1_data.py        # Migrate from V1
│
├── config/                       # Configuration Files
│   ├── settings.yaml             # Main settings
│   ├── logging.yaml              # Logging configuration
│   └── model_config.yaml         # Model configurations
│
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose setup
└── pyproject.toml                # Project metadata
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start the server
uvicorn api.main:app --reload --port 8001
```

## Tech Stack

- **API**: FastAPI + Pydantic
- **ML**: PyTorch + EfficientNet + CLIP
- **Database**: PostgreSQL + SQLAlchemy
- **Cache**: Redis
- **Vector Store**: FAISS / ChromaDB
- **LLM**: Anthropic Claude / OpenAI
