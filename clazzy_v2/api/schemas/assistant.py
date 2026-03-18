"""Pydantic schemas for AI assistant endpoints"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class AssistantQueryRequest(BaseModel):
    """Request for AI assistant query"""
    query: str = Field(..., description="Natural language query", min_length=1, max_length=500)
    user_id: str = Field(default="anonymous", description="User ID for personalization")
    wardrobe: List[Dict] = Field(default=[], description="User's wardrobe items")
    context: Optional[Dict] = Field(default=None, description="Additional context: weather, location, time")
    use_llm: bool = Field(default=True, description="Whether to use LLM for complex queries")


class OutfitCard(BaseModel):
    """Single outfit card in response"""
    rank: int = Field(..., description="Recommendation rank")
    items: List[Dict] = Field(..., description="Items in the outfit")
    score: int = Field(..., description="Match score 0-100")
    match_quality: str = Field(..., description="Quality label: Excellent, Great, Good, Okay")
    reasons: List[str] = Field(default=[], description="Recommendation reasons")


class QueryUnderstanding(BaseModel):
    """How the query was understood"""
    intent_type: str = Field(..., description="Detected intent type")
    confidence: float = Field(..., description="Confidence score")
    occasion: Optional[str] = None
    target_item: Optional[str] = None
    color_preference: Optional[str] = None
    style_preference: Optional[str] = None
    weather: Optional[str] = None
    time_of_day: Optional[str] = None
    constraints: List[str] = []
    original_query: str = ""


class AssistantQueryResponse(BaseModel):
    """Response from AI assistant"""
    intro: str = Field(..., description="Introduction text")
    outfits: List[OutfitCard] = Field(default=[], description="Outfit recommendations")
    tips: List[str] = Field(default=[], description="Fashion tips")
    query_understanding: QueryUnderstanding = Field(..., description="How the query was parsed")


class QuickReplyOption(BaseModel):
    """Quick reply option for follow-up"""
    label: str
    query: str


class ConversationMessage(BaseModel):
    """Single message in conversation"""
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = None
    outfits: Optional[List[OutfitCard]] = None
