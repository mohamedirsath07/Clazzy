"""
Clazzy V2 Configuration Management
Centralized configuration with environment variable support
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    app_name: str = "Clazzy V2"
    app_version: str = "2.0.0"
    debug: bool = False
    environment: str = "development"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_prefix: str = "/api/v2"
    cors_origins: list[str] = ["http://localhost:5000", "http://localhost:3000"]

    # Database
    database_url: str = "sqlite:///./clazzy.db"  # Default SQLite for solo dev
    redis_url: Optional[str] = None  # Optional Redis for caching

    # ML Models
    model_dir: str = "./models"
    classifier_model: str = "efficientnet_b0"
    embedding_model: str = "clip-vit-base-patch32"

    # External Services
    weather_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Performance
    max_request_size_mb: int = 10
    inference_timeout_seconds: float = 2.0
    cache_ttl_seconds: int = 3600

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Storage
    storage_backend: str = "local"  # local, s3, gcs
    storage_bucket: Optional[str] = None
    local_storage_path: str = "./uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Clothing categories for multi-class classification
CLOTHING_CATEGORIES = {
    "tops": [
        "t-shirt", "shirt", "blouse", "polo", "sweater",
        "hoodie", "tank-top", "crop-top", "cardigan"
    ],
    "bottoms": [
        "jeans", "trousers", "shorts", "skirt", "chinos",
        "joggers", "leggings", "cargo-pants"
    ],
    "outerwear": [
        "jacket", "blazer", "coat", "windbreaker", "vest",
        "denim-jacket", "leather-jacket", "parka"
    ],
    "dresses": [
        "casual-dress", "formal-dress", "maxi-dress",
        "mini-dress", "midi-dress", "sundress"
    ],
    "footwear": [
        "sneakers", "boots", "loafers", "sandals",
        "heels", "flats", "oxford-shoes"
    ],
    "accessories": [
        "belt", "watch", "hat", "scarf", "bag", "sunglasses"
    ]
}

# Flatten for classification
ALL_CLOTHING_TYPES = []
CATEGORY_MAP = {}
for category, items in CLOTHING_CATEGORIES.items():
    for item in items:
        ALL_CLOTHING_TYPES.append(item)
        CATEGORY_MAP[item] = category

# Style attributes
STYLE_ATTRIBUTES = [
    "casual", "formal", "streetwear", "minimalist", "bohemian",
    "preppy", "athletic", "vintage", "elegant", "edgy"
]

# Pattern attributes
PATTERN_ATTRIBUTES = [
    "solid", "striped", "checkered", "floral", "geometric",
    "abstract", "polka-dot", "camouflage", "animal-print"
]

# Season attributes
SEASON_ATTRIBUTES = ["spring", "summer", "fall", "winter", "all-season"]

# Occasion types
OCCASIONS = [
    "casual", "formal", "office", "date", "party", "wedding",
    "interview", "workout", "beach", "travel", "college"
]
