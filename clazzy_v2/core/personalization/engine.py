"""
Clazzy V2 - Personalization Engine
Learns user preferences and adapts recommendations over time
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)


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


@dataclass
class UserProfile:
    """Complete user profile for personalization"""
    user_id: str
    name: Optional[str] = None

    # Physical attributes (for fit/style recommendations)
    gender: Optional[Gender] = None
    body_type: Optional[BodyType] = None
    skin_tone: Optional[SkinTone] = None
    age_range: Optional[str] = None  # "18-24", "25-34", etc.

    # Style preferences (explicit)
    preferred_styles: List[str] = field(default_factory=list)
    avoided_styles: List[str] = field(default_factory=list)
    preferred_colors: List[str] = field(default_factory=list)
    avoided_colors: List[str] = field(default_factory=list)

    # Budget preferences
    budget_tier: str = "mid"  # "budget", "mid", "premium", "luxury"

    # Behavioral data (learned)
    style_affinity_scores: Dict[str, float] = field(default_factory=dict)
    color_affinity_scores: Dict[str, float] = field(default_factory=dict)
    pattern_affinity_scores: Dict[str, float] = field(default_factory=dict)

    # Engagement metrics
    total_outfits_viewed: int = 0
    total_outfits_liked: int = 0
    total_outfits_saved: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "gender": self.gender.value if self.gender else None,
            "body_type": self.body_type.value if self.body_type else None,
            "skin_tone": self.skin_tone.value if self.skin_tone else None,
            "age_range": self.age_range,
            "preferred_styles": self.preferred_styles,
            "avoided_styles": self.avoided_styles,
            "preferred_colors": self.preferred_colors,
            "avoided_colors": self.avoided_colors,
            "budget_tier": self.budget_tier,
            "style_affinity_scores": self.style_affinity_scores,
            "color_affinity_scores": self.color_affinity_scores,
            "pattern_affinity_scores": self.pattern_affinity_scores,
            "total_outfits_viewed": self.total_outfits_viewed,
            "total_outfits_liked": self.total_outfits_liked,
            "total_outfits_saved": self.total_outfits_saved,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "UserProfile":
        """Create from dictionary"""
        return cls(
            user_id=data["user_id"],
            name=data.get("name"),
            gender=Gender(data["gender"]) if data.get("gender") else None,
            body_type=BodyType(data["body_type"]) if data.get("body_type") else None,
            skin_tone=SkinTone(data["skin_tone"]) if data.get("skin_tone") else None,
            age_range=data.get("age_range"),
            preferred_styles=data.get("preferred_styles", []),
            avoided_styles=data.get("avoided_styles", []),
            preferred_colors=data.get("preferred_colors", []),
            avoided_colors=data.get("avoided_colors", []),
            budget_tier=data.get("budget_tier", "mid"),
            style_affinity_scores=data.get("style_affinity_scores", {}),
            color_affinity_scores=data.get("color_affinity_scores", {}),
            pattern_affinity_scores=data.get("pattern_affinity_scores", {}),
            total_outfits_viewed=data.get("total_outfits_viewed", 0),
            total_outfits_liked=data.get("total_outfits_liked", 0),
            total_outfits_saved=data.get("total_outfits_saved", 0)
        )


@dataclass
class FeedbackEvent:
    """User feedback on an outfit"""
    user_id: str
    outfit_id: str
    action: str  # "like", "dislike", "save", "skip", "wear"
    outfit_items: List[Dict]  # Items in the outfit
    occasion: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PreferenceLearner:
    """
    Learns user preferences from explicit settings and implicit feedback
    Uses exponential moving average for preference updates
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        decay_factor: float = 0.95
    ):
        self.learning_rate = learning_rate
        self.decay_factor = decay_factor

    def update_from_feedback(
        self,
        profile: UserProfile,
        event: FeedbackEvent
    ) -> UserProfile:
        """
        Update user preferences based on feedback event

        Args:
            profile: Current user profile
            event: Feedback event

        Returns:
            Updated user profile
        """
        # Determine feedback weight
        action_weights = {
            "like": 1.0,
            "save": 1.5,
            "wear": 2.0,  # Strongest positive signal
            "skip": -0.3,
            "dislike": -1.0
        }

        weight = action_weights.get(event.action, 0)
        if weight == 0:
            return profile

        # Update engagement count
        profile.total_outfits_viewed += 1
        if event.action in ["like", "save", "wear"]:
            profile.total_outfits_liked += 1
        if event.action == "save":
            profile.total_outfits_saved += 1

        # Extract attributes from outfit items
        for item in event.outfit_items:
            # Update style affinities
            for style in item.get("style_tags", []):
                current = profile.style_affinity_scores.get(style, 0.5)
                new_value = current + self.learning_rate * weight * (1 - current if weight > 0 else current)
                profile.style_affinity_scores[style] = max(0, min(1, new_value))

            # Update color affinities
            for color in item.get("colors", []):
                color_name = color.get("name", "").lower()
                if color_name:
                    current = profile.color_affinity_scores.get(color_name, 0.5)
                    new_value = current + self.learning_rate * weight * (1 - current if weight > 0 else current)
                    profile.color_affinity_scores[color_name] = max(0, min(1, new_value))

            # Update pattern affinities
            pattern = item.get("pattern", "")
            if pattern:
                current = profile.pattern_affinity_scores.get(pattern, 0.5)
                new_value = current + self.learning_rate * weight * (1 - current if weight > 0 else current)
                profile.pattern_affinity_scores[pattern] = max(0, min(1, new_value))

        profile.updated_at = datetime.utcnow()
        return profile

    def decay_preferences(self, profile: UserProfile) -> UserProfile:
        """Apply decay to move preferences back toward neutral"""
        for style in profile.style_affinity_scores:
            current = profile.style_affinity_scores[style]
            profile.style_affinity_scores[style] = 0.5 + (current - 0.5) * self.decay_factor

        for color in profile.color_affinity_scores:
            current = profile.color_affinity_scores[color]
            profile.color_affinity_scores[color] = 0.5 + (current - 0.5) * self.decay_factor

        return profile

    def compute_preference_vector(self, profile: UserProfile) -> Dict[str, float]:
        """Compute normalized preference vector for recommendations"""
        styles = ["casual", "formal", "streetwear", "minimalist", "bohemian",
                  "preppy", "athletic", "vintage", "elegant", "edgy"]

        # Combine explicit and learned preferences
        style_scores = {}
        for style in styles:
            explicit = 1.0 if style in profile.preferred_styles else (
                0.0 if style in profile.avoided_styles else 0.5
            )
            learned = profile.style_affinity_scores.get(style, 0.5)

            # Weighted combination (explicit has more weight initially)
            engagement_factor = min(profile.total_outfits_liked / 50, 1.0)
            style_scores[style] = explicit * (1 - engagement_factor) + learned * engagement_factor

        return style_scores


class SkinToneColorRecommender:
    """Recommends colors based on skin tone color theory"""

    SKIN_TONE_PALETTES = {
        SkinTone.FAIR: {
            "ideal": ["navy", "burgundy", "forest-green", "charcoal", "dusty-pink"],
            "good": ["soft-blue", "lavender", "cream", "rose", "silver"],
            "avoid": ["neon", "bright-yellow", "orange"]
        },
        SkinTone.LIGHT: {
            "ideal": ["navy", "teal", "burgundy", "olive", "coral"],
            "good": ["sage", "dusty-blue", "mauve", "camel"],
            "avoid": ["pale-yellow", "beige"]
        },
        SkinTone.MEDIUM: {
            "ideal": ["mustard", "rust", "olive", "burgundy", "teal"],
            "good": ["coral", "turquoise", "emerald", "camel"],
            "avoid": ["pale-pastels"]
        },
        SkinTone.TAN: {
            "ideal": ["white", "coral", "turquoise", "gold", "orange"],
            "good": ["bright-blue", "fuchsia", "lime", "red"],
            "avoid": ["muted-browns", "olive"]
        },
        SkinTone.BROWN: {
            "ideal": ["gold", "orange", "coral", "white", "purple"],
            "good": ["yellow", "pink", "emerald", "royal-blue"],
            "avoid": ["muted-greens", "pastels"]
        },
        SkinTone.DARK: {
            "ideal": ["white", "bright-yellow", "fuchsia", "cobalt", "orange"],
            "good": ["gold", "coral", "emerald", "red"],
            "avoid": ["black", "dark-brown", "navy"]
        }
    }

    @classmethod
    def get_recommendations(cls, skin_tone: SkinTone) -> Dict[str, List[str]]:
        """Get color recommendations for skin tone"""
        return cls.SKIN_TONE_PALETTES.get(skin_tone, {
            "ideal": ["navy", "white", "black"],
            "good": ["gray", "blue"],
            "avoid": []
        })

    @classmethod
    def score_color_for_skin_tone(
        cls,
        color_name: str,
        skin_tone: Optional[SkinTone]
    ) -> float:
        """Score how well a color works with skin tone"""
        if not skin_tone:
            return 0.7  # Neutral if no skin tone specified

        palette = cls.SKIN_TONE_PALETTES.get(skin_tone, {})
        color_lower = color_name.lower()

        if color_lower in palette.get("ideal", []):
            return 1.0
        elif color_lower in palette.get("good", []):
            return 0.8
        elif color_lower in palette.get("avoid", []):
            return 0.3
        else:
            return 0.6  # Neutral


class PersonalizationEngine:
    """
    Main personalization engine
    Orchestrates profile management and preference learning
    """

    def __init__(self, storage=None):
        """
        Args:
            storage: Optional storage backend for profiles
        """
        self.storage = storage
        self.learner = PreferenceLearner()
        self.skin_tone_recommender = SkinToneColorRecommender()

        # In-memory cache
        self._profile_cache: Dict[str, UserProfile] = {}

    def get_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        if user_id in self._profile_cache:
            return self._profile_cache[user_id]

        if self.storage:
            try:
                data = self.storage.get_profile(user_id)
                if data:
                    profile = UserProfile.from_dict(data)
                    self._profile_cache[user_id] = profile
                    return profile
            except Exception as e:
                logger.warning(f"Failed to load profile: {e}")

        # Create new profile
        profile = UserProfile(user_id=user_id)
        self._profile_cache[user_id] = profile
        return profile

    def save_profile(self, profile: UserProfile):
        """Save user profile"""
        self._profile_cache[profile.user_id] = profile
        if self.storage:
            try:
                self.storage.save_profile(profile.to_dict())
            except Exception as e:
                logger.error(f"Failed to save profile: {e}")

    def update_profile(
        self,
        user_id: str,
        updates: Dict
    ) -> UserProfile:
        """Update user profile with explicit preferences"""
        profile = self.get_profile(user_id)

        # Update physical attributes
        if "gender" in updates:
            profile.gender = Gender(updates["gender"])
        if "body_type" in updates:
            profile.body_type = BodyType(updates["body_type"])
        if "skin_tone" in updates:
            profile.skin_tone = SkinTone(updates["skin_tone"])
        if "age_range" in updates:
            profile.age_range = updates["age_range"]

        # Update explicit preferences
        if "preferred_styles" in updates:
            profile.preferred_styles = updates["preferred_styles"]
        if "avoided_styles" in updates:
            profile.avoided_styles = updates["avoided_styles"]
        if "preferred_colors" in updates:
            profile.preferred_colors = updates["preferred_colors"]
        if "avoided_colors" in updates:
            profile.avoided_colors = updates["avoided_colors"]

        profile.updated_at = datetime.utcnow()
        self.save_profile(profile)
        return profile

    def record_feedback(
        self,
        event: FeedbackEvent
    ) -> UserProfile:
        """Record user feedback and update preferences"""
        profile = self.get_profile(event.user_id)
        profile = self.learner.update_from_feedback(profile, event)
        self.save_profile(profile)
        return profile

    def get_recommendation_context(
        self,
        user_id: str
    ) -> Dict:
        """Get personalization context for recommendations"""
        profile = self.get_profile(user_id)

        # Compute style preferences
        style_scores = self.learner.compute_preference_vector(profile)

        # Get skin tone color recommendations
        color_recs = {}
        if profile.skin_tone:
            color_recs = self.skin_tone_recommender.get_recommendations(profile.skin_tone)

        return {
            "user_id": user_id,
            "style_preferences": style_scores,
            "preferred_colors": profile.preferred_colors + color_recs.get("ideal", []),
            "avoided_colors": profile.avoided_colors + color_recs.get("avoid", []),
            "color_recommendations": color_recs,
            "engagement_level": min(profile.total_outfits_liked / 100, 1.0),
            "profile_complete": all([
                profile.gender,
                profile.preferred_styles,
                profile.skin_tone
            ])
        }

    def personalize_recommendations(
        self,
        user_id: str,
        recommendations: List[Dict],
        boost_factor: float = 0.2
    ) -> List[Dict]:
        """
        Re-rank recommendations based on user preferences

        Args:
            user_id: User ID
            recommendations: List of outfit recommendations
            boost_factor: Maximum score boost from personalization

        Returns:
            Re-ranked recommendations
        """
        context = self.get_recommendation_context(user_id)
        profile = self.get_profile(user_id)

        for rec in recommendations:
            boost = 0.0

            # Style match boost
            for item in rec.get("items", []):
                for style in item.get("style_tags", []):
                    affinity = context["style_preferences"].get(style, 0.5)
                    boost += (affinity - 0.5) * 0.1

                # Color match boost
                for color in item.get("colors", []):
                    color_name = color.get("name", "").lower()
                    if color_name in context["preferred_colors"]:
                        boost += 0.05
                    elif color_name in context["avoided_colors"]:
                        boost -= 0.1

                    # Skin tone color scoring
                    if profile.skin_tone:
                        st_score = self.skin_tone_recommender.score_color_for_skin_tone(
                            color_name, profile.skin_tone
                        )
                        boost += (st_score - 0.5) * 0.05

            # Apply boost (clamped)
            boost = max(-boost_factor, min(boost_factor, boost))
            rec["personalized_score"] = rec.get("score", 0.5) + boost
            rec["personalization_boost"] = boost

        # Re-sort by personalized score
        recommendations.sort(
            key=lambda x: x.get("personalized_score", x.get("score", 0)),
            reverse=True
        )

        return recommendations
