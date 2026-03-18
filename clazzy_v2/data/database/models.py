"""
Clazzy V2 - Database Models
SQLAlchemy ORM models for PostgreSQL
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON,
    ForeignKey, Text, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


# ===========================
# Enums
# ===========================

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class BodyType(enum.Enum):
    SLIM = "slim"
    ATHLETIC = "athletic"
    AVERAGE = "average"
    CURVY = "curvy"
    PLUS_SIZE = "plus_size"


class SkinTone(enum.Enum):
    FAIR = "fair"
    LIGHT = "light"
    MEDIUM = "medium"
    TAN = "tan"
    BROWN = "brown"
    DARK = "dark"


class FeedbackAction(enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    SAVE = "save"
    SKIP = "skip"
    WEAR = "wear"


# ===========================
# User Models
# ===========================

class User(Base):
    """User profile for personalization"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(100), nullable=True)

    # Profile data
    gender = Column(SQLEnum(Gender), nullable=True)
    body_type = Column(SQLEnum(BodyType), nullable=True)
    skin_tone = Column(SQLEnum(SkinTone), nullable=True)
    age_range = Column(String(20), nullable=True)

    # Preferences (JSON for flexibility)
    preferred_styles = Column(JSON, default=list)
    avoided_styles = Column(JSON, default=list)
    preferred_colors = Column(JSON, default=list)
    avoided_colors = Column(JSON, default=list)
    budget_tier = Column(String(20), default="mid")

    # Learned preferences (updated by feedback)
    style_affinity_scores = Column(JSON, default=dict)
    color_affinity_scores = Column(JSON, default=dict)
    pattern_affinity_scores = Column(JSON, default=dict)

    # Engagement metrics
    total_outfits_viewed = Column(Integer, default=0)
    total_outfits_liked = Column(Integer, default=0)
    total_outfits_saved = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    wardrobe_items = relationship("WardrobeItem", back_populates="user")
    outfit_history = relationship("OutfitHistory", back_populates="user")
    feedback = relationship("UserFeedback", back_populates="user")

    __table_args__ = (
        Index('idx_user_created', 'created_at'),
    )


# ===========================
# Wardrobe Models
# ===========================

class WardrobeItem(Base):
    """Individual clothing item in user's wardrobe"""
    __tablename__ = "wardrobe_items"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Item details
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # top, bottom, outerwear, dress, footwear, accessory
    clothing_type = Column(String(50), nullable=False)  # t-shirt, jeans, etc.

    # Colors (JSON array)
    colors = Column(JSON, default=list)
    dominant_color_hue = Column(Float, nullable=True)

    # Attributes
    style_tags = Column(JSON, default=list)
    pattern = Column(String(50), default="solid")
    seasons = Column(JSON, default=list)

    # Image
    image_path = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)

    # Embedding (stored separately for efficiency)
    embedding_id = Column(String(36), nullable=True)

    # Usage tracking
    times_worn = Column(Integer, default=0)
    last_worn = Column(DateTime, nullable=True)

    # Metadata
    brand = Column(String(100), nullable=True)
    purchase_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="wardrobe_items")

    __table_args__ = (
        Index('idx_wardrobe_user', 'user_id'),
        Index('idx_wardrobe_category', 'category'),
        Index('idx_wardrobe_type', 'clothing_type'),
    )


# ===========================
# Outfit Models
# ===========================

class OutfitHistory(Base):
    """Record of generated/worn outfits"""
    __tablename__ = "outfit_history"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Outfit composition (item IDs)
    item_ids = Column(JSON, nullable=False)

    # Context
    occasion = Column(String(50), nullable=True)
    weather = Column(String(50), nullable=True)
    temperature = Column(Float, nullable=True)

    # Scoring
    total_score = Column(Float, nullable=True)
    harmony_type = Column(String(50), nullable=True)
    occasion_match = Column(Float, nullable=True)
    style_coherence = Column(Float, nullable=True)

    # User interaction
    was_worn = Column(Boolean, default=False)
    worn_at = Column(DateTime, nullable=True)
    user_rating = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Generated/saved
    is_saved = Column(Boolean, default=False)
    name = Column(String(200), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="outfit_history")

    __table_args__ = (
        Index('idx_outfit_user', 'user_id'),
        Index('idx_outfit_occasion', 'occasion'),
        Index('idx_outfit_saved', 'is_saved'),
        Index('idx_outfit_created', 'created_at'),
    )


class SavedOutfit(Base):
    """User's saved/favorite outfits"""
    __tablename__ = "saved_outfits"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    outfit_history_id = Column(String(36), ForeignKey("outfit_history.id"), nullable=True)

    name = Column(String(200), nullable=True)
    item_ids = Column(JSON, nullable=False)
    occasion = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_saved_user', 'user_id'),
    )


# ===========================
# Feedback Models
# ===========================

class UserFeedback(Base):
    """User feedback on outfits for learning"""
    __tablename__ = "user_feedback"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    outfit_id = Column(String(36), nullable=True)

    # Feedback
    action = Column(SQLEnum(FeedbackAction), nullable=False)
    rating = Column(Integer, nullable=True)

    # Context at time of feedback
    outfit_items = Column(JSON)  # Snapshot of items with attributes
    occasion = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="feedback")

    __table_args__ = (
        Index('idx_feedback_user', 'user_id'),
        Index('idx_feedback_action', 'action'),
        Index('idx_feedback_created', 'created_at'),
    )


# ===========================
# Embedding Models
# ===========================

class ItemEmbedding(Base):
    """Stored embeddings for similarity search"""
    __tablename__ = "item_embeddings"

    id = Column(String(36), primary_key=True)
    wardrobe_item_id = Column(String(36), ForeignKey("wardrobe_items.id"), nullable=False)

    # Embedding data
    embedding_model = Column(String(100), nullable=False)  # e.g., "clip-vit-base-patch32"
    embedding_vector = Column(JSON, nullable=False)  # Store as JSON array
    embedding_dim = Column(Integer, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_embedding_item', 'wardrobe_item_id'),
        Index('idx_embedding_model', 'embedding_model'),
    )


# ===========================
# Analytics Models
# ===========================

class AnalyticsEvent(Base):
    """Usage analytics for insights"""
    __tablename__ = "analytics_events"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=True)

    # Event data
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON)

    # Context
    session_id = Column(String(36), nullable=True)
    device_type = Column(String(50), nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_analytics_user', 'user_id'),
        Index('idx_analytics_type', 'event_type'),
        Index('idx_analytics_created', 'created_at'),
    )
