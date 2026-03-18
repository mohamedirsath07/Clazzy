"""Pydantic schemas for clothing-related endpoints"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ColorInfo(BaseModel):
    """Color information for a clothing item"""
    hex: str = Field(..., description="Hex color code")
    name: str = Field(..., description="Color name")
    percentage: float = Field(default=0, description="Percentage of item this color covers")
    rgb: Optional[List[int]] = Field(default=None, description="RGB values")


class ClothingItemBase(BaseModel):
    """Base clothing item schema"""
    id: str = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Item name")
    category: str = Field(..., description="Category: top, bottom, outerwear, dress, footwear, accessory")
    clothing_type: str = Field(..., description="Specific type: t-shirt, jeans, etc.")
    colors: List[Dict] = Field(default=[], description="Dominant colors")
    dominant_color_hue: Optional[float] = Field(default=None, description="HSV hue of dominant color")
    style_tags: Optional[List[str]] = Field(default=[], description="Style tags: casual, formal, etc.")
    pattern: Optional[str] = Field(default="solid", description="Pattern: solid, striped, etc.")
    seasons: Optional[List[str]] = Field(default=["all-season"], description="Suitable seasons")
    image_path: Optional[str] = Field(default=None, description="Path to item image")


class ClothingItem(ClothingItemBase):
    """Full clothing item with all attributes"""
    pass


class ClothingClassification(BaseModel):
    """Classification result for a clothing item"""
    type: Dict = Field(..., description="Primary and alternative type predictions")
    category: str = Field(..., description="Category: top, bottom, etc.")
    style: List[Dict] = Field(default=[], description="Detected style attributes")
    pattern: Dict = Field(..., description="Pattern detection")
    season: List[Dict] = Field(default=[], description="Season suitability")
    metadata: Optional[Dict] = Field(default=None, description="Model metadata")


class ClothingAnalysisResponse(BaseModel):
    """Complete analysis response for a clothing item"""
    classification: Dict = Field(..., description="Classification results")
    colors: List[Dict] = Field(default=[], description="Extracted colors")
    embedding_available: bool = Field(default=False, description="Whether embedding was generated")


class WardrobeItem(BaseModel):
    """Item in user's wardrobe"""
    id: str
    name: str
    category: str
    clothing_type: str
    colors: List[Dict] = []
    dominant_color_hue: Optional[float] = None
    style_tags: List[str] = []
    pattern: str = "solid"
    seasons: List[str] = ["all-season"]
    image_url: Optional[str] = None
    added_at: Optional[str] = None
    times_worn: int = 0
    last_worn: Optional[str] = None


class WardrobeAnalysisRequest(BaseModel):
    """Request for wardrobe analysis"""
    items: List[WardrobeItem]


class WardrobeSuggestion(BaseModel):
    """Suggestion for wardrobe improvement"""
    type: str  # missing_essential, versatile_piece, capsule_suggestion
    category: Optional[str] = None
    item: Optional[str] = None
    message: str
    priority: int = 0
