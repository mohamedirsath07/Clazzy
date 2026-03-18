"""Pydantic schemas for user-related endpoints"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class BodyType(str, Enum):
    SLIM = "slim"
    ATHLETIC = "athletic"
    AVERAGE = "average"
    CURVY = "curvy"
    PLUS_SIZE = "plus_size"


class SkinTone(str, Enum):
    FAIR = "fair"
    LIGHT = "light"
    MEDIUM = "medium"
    TAN = "tan"
    BROWN = "brown"
    DARK = "dark"


class UserProfileCreate(BaseModel):
    """Schema for creating a new user profile"""
    user_id: str = Field(..., description="Unique user identifier")
    name: Optional[str] = Field(default=None, description="User's name")
    gender: Optional[Gender] = Field(default=None, description="Gender")
    body_type: Optional[BodyType] = Field(default=None, description="Body type")
    skin_tone: Optional[SkinTone] = Field(default=None, description="Skin tone")
    age_range: Optional[str] = Field(default=None, description="Age range: 18-24, 25-34, etc.")
    preferred_styles: Optional[List[str]] = Field(default=[], description="Preferred style tags")
    avoided_styles: Optional[List[str]] = Field(default=[], description="Styles to avoid")
    preferred_colors: Optional[List[str]] = Field(default=[], description="Preferred colors")
    avoided_colors: Optional[List[str]] = Field(default=[], description="Colors to avoid")
    budget_tier: Optional[str] = Field(default="mid", description="Budget tier: budget, mid, premium, luxury")


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = None
    gender: Optional[Gender] = None
    body_type: Optional[BodyType] = None
    skin_tone: Optional[SkinTone] = None
    age_range: Optional[str] = None
    preferred_styles: Optional[List[str]] = None
    avoided_styles: Optional[List[str]] = None
    preferred_colors: Optional[List[str]] = None
    avoided_colors: Optional[List[str]] = None
    budget_tier: Optional[str] = None


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""
    user_id: str
    name: Optional[str] = None
    gender: Optional[str] = None
    body_type: Optional[str] = None
    skin_tone: Optional[str] = None
    age_range: Optional[str] = None
    preferred_styles: List[str] = []
    avoided_styles: List[str] = []
    preferred_colors: List[str] = []
    avoided_colors: List[str] = []
    budget_tier: str = "mid"
    style_affinity_scores: Dict[str, float] = {}
    color_affinity_scores: Dict[str, float] = {}
    pattern_affinity_scores: Dict[str, float] = {}
    total_outfits_viewed: int = 0
    total_outfits_liked: int = 0
    total_outfits_saved: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Schema for recording user feedback"""
    outfit_id: str = Field(..., description="ID of the outfit")
    action: str = Field(..., description="Action: like, dislike, save, skip, wear")
    outfit_items: List[Dict] = Field(default=[], description="Items in the outfit with attributes")
    occasion: Optional[str] = Field(default=None, description="Occasion context")


class FeedbackResponse(BaseModel):
    """Response after recording feedback"""
    status: str
    new_engagement_score: float


class UserPreferencesContext(BaseModel):
    """User preferences context for recommendations"""
    user_id: str
    style_preferences: Dict[str, float]
    preferred_colors: List[str]
    avoided_colors: List[str]
    color_recommendations: Dict[str, List[str]]
    engagement_level: float
    profile_complete: bool
