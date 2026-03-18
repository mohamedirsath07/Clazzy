"""Pydantic schemas for outfit-related endpoints"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from api.schemas.clothing import ClothingItem


class OutfitRecommendationRequest(BaseModel):
    """Request for outfit recommendations"""
    wardrobe: List[ClothingItem] = Field(..., description="List of wardrobe items")
    occasion: str = Field(default="casual", description="Target occasion")
    user_id: Optional[str] = Field(default=None, description="User ID for personalization")
    top_k: Optional[int] = Field(default=5, description="Number of recommendations")
    must_include: Optional[str] = Field(default=None, description="Item ID that must be included")
    style_filter: Optional[str] = Field(default=None, description="Filter by style")
    weather: Optional[str] = Field(default=None, description="Weather context")


class OutfitRecommendation(BaseModel):
    """Single outfit recommendation"""
    items: List[str] = Field(..., description="Item IDs in this outfit")
    score: float = Field(..., description="Overall score 0-1")
    reasons: List[str] = Field(default=[], description="Reasons for recommendation")
    harmony_type: str = Field(..., description="Color harmony type")
    occasion_match: float = Field(..., description="Occasion appropriateness score")
    style_coherence: float = Field(..., description="Style coherence score")
    personalization_boost: Optional[float] = Field(default=None, description="Personalization boost applied")


class OutfitRecommendationResponse(BaseModel):
    """Response containing outfit recommendations"""
    recommendations: List[OutfitRecommendation] = Field(..., description="List of outfit recommendations")
    occasion: str = Field(..., description="Target occasion")
    personalized: bool = Field(default=False, description="Whether personalization was applied")
    processing_time_ms: Optional[float] = Field(default=None, description="Processing time")


class OutfitScoreRequest(BaseModel):
    """Request to score a specific outfit"""
    items: List[ClothingItem] = Field(..., description="Items in the outfit")
    occasion: str = Field(default="casual", description="Target occasion")


class OutfitScoreResponse(BaseModel):
    """Response with outfit score"""
    score: float = Field(..., description="Overall score 0-1")
    reasons: List[str] = Field(default=[], description="Scoring reasons")
    harmony_type: str = Field(..., description="Color harmony type")
    occasion_match: float = Field(..., description="Occasion appropriateness")
    style_coherence: float = Field(..., description="Style coherence")
    breakdown: Dict = Field(default={}, description="Detailed score breakdown")


class OutfitHistory(BaseModel):
    """Historical outfit record"""
    id: str
    items: List[str]
    occasion: str
    worn_at: str
    user_rating: Optional[int] = None
    weather: Optional[str] = None
    notes: Optional[str] = None


class SaveOutfitRequest(BaseModel):
    """Request to save an outfit"""
    items: List[str] = Field(..., description="Item IDs")
    occasion: str = Field(default="casual", description="Occasion")
    name: Optional[str] = Field(default=None, description="Custom name for outfit")
