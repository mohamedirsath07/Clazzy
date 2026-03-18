"""
Clazzy V2 - Smart Recommendation Engine
Hybrid system: Rule-based + ML-ranking + Embedding similarity
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Occasion(str, Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    OFFICE = "office"
    DATE = "date"
    PARTY = "party"
    WEDDING = "wedding"
    INTERVIEW = "interview"
    WORKOUT = "workout"
    BEACH = "beach"
    TRAVEL = "travel"
    COLLEGE = "college"


@dataclass
class ClothingItem:
    """Represents a clothing item with all attributes"""
    id: str
    name: str
    category: str  # top, bottom, outerwear, dress, footwear, accessory
    clothing_type: str  # specific type like t-shirt, jeans, etc.
    colors: List[Dict]  # List of {hex, name, percentage}
    dominant_color_hue: float  # HSV hue value
    style_tags: List[str]  # casual, formal, streetwear, etc.
    pattern: str  # solid, striped, etc.
    seasons: List[str]  # spring, summer, fall, winter
    embedding: Optional[np.ndarray] = None
    image_path: Optional[str] = None


@dataclass
class OutfitRecommendation:
    """Represents a recommended outfit"""
    items: List[ClothingItem]
    score: float
    reasons: List[str]
    harmony_type: str
    occasion_match: float
    style_coherence: float
    breakdown: Dict  # Detailed scoring breakdown


class HarmonyEngine:
    """Color harmony rules based on color theory"""

    @staticmethod
    def detect_harmony(hue1: float, hue2: float) -> Tuple[str, float]:
        """
        Detect color harmony type between two hues

        Args:
            hue1, hue2: Hue values in range [0, 360]

        Returns:
            Tuple of (harmony_type, base_score)
        """
        diff = abs(hue1 - hue2)
        diff = min(diff, 360 - diff)  # Circular distance

        if diff < 15:
            return "monochromatic", 0.95
        elif diff < 40:
            return "analogous", 0.90
        elif 55 < diff < 65:
            return "triadic", 0.85
        elif 170 < diff < 190:
            return "complementary", 0.90
        elif 25 < diff < 45:
            return "analogous", 0.85
        elif 80 < diff < 100:
            return "split-complementary", 0.80
        else:
            return "contrast", 0.50

    @staticmethod
    def is_neutral(color_name: str) -> bool:
        """Check if color is neutral (works with everything)"""
        neutrals = {
            "black", "white", "gray", "grey", "navy", "beige",
            "cream", "ivory", "charcoal", "silver", "tan", "khaki"
        }
        return color_name.lower() in neutrals

    @staticmethod
    def compute_multi_item_harmony(items: List[ClothingItem]) -> Dict:
        """Compute harmony score for multiple items"""
        if len(items) < 2:
            return {"score": 1.0, "harmony_type": "single"}

        scores = []
        harmonies = []

        for i, item1 in enumerate(items):
            for item2 in items[i + 1:]:
                # Check for neutrals
                c1_neutral = any(HarmonyEngine.is_neutral(c["name"]) for c in item1.colors[:1])
                c2_neutral = any(HarmonyEngine.is_neutral(c["name"]) for c in item2.colors[:1])

                if c1_neutral or c2_neutral:
                    scores.append(0.95)
                    harmonies.append("neutral")
                else:
                    harmony, score = HarmonyEngine.detect_harmony(
                        item1.dominant_color_hue,
                        item2.dominant_color_hue
                    )
                    scores.append(score)
                    harmonies.append(harmony)

        avg_score = np.mean(scores)
        most_common_harmony = max(set(harmonies), key=harmonies.count)

        return {
            "score": float(avg_score),
            "harmony_type": most_common_harmony,
            "details": list(zip(harmonies, scores))
        }


class StyleCompatibilityEngine:
    """Style compatibility rules"""

    # Style compatibility matrix (1.0 = perfect match, 0.0 = clash)
    COMPATIBILITY = {
        "casual": {"casual": 1.0, "streetwear": 0.8, "minimalist": 0.9, "athletic": 0.7, "preppy": 0.6},
        "formal": {"formal": 1.0, "elegant": 0.9, "minimalist": 0.8, "preppy": 0.7},
        "streetwear": {"streetwear": 1.0, "casual": 0.8, "athletic": 0.7, "edgy": 0.9},
        "minimalist": {"minimalist": 1.0, "casual": 0.9, "formal": 0.8, "elegant": 0.9},
        "bohemian": {"bohemian": 1.0, "vintage": 0.8, "casual": 0.7},
        "preppy": {"preppy": 1.0, "casual": 0.8, "formal": 0.7, "elegant": 0.7},
        "athletic": {"athletic": 1.0, "casual": 0.8, "streetwear": 0.7},
        "vintage": {"vintage": 1.0, "bohemian": 0.8, "casual": 0.7, "elegant": 0.7},
        "elegant": {"elegant": 1.0, "formal": 0.9, "minimalist": 0.9},
        "edgy": {"edgy": 1.0, "streetwear": 0.9, "casual": 0.6}
    }

    @classmethod
    def compute_compatibility(cls, items: List[ClothingItem]) -> Dict:
        """Compute style compatibility score for items"""
        if len(items) < 2:
            return {"score": 1.0, "dominant_style": items[0].style_tags[0] if items[0].style_tags else "casual"}

        # Collect all style tags
        all_styles = []
        for item in items:
            all_styles.extend(item.style_tags)

        if not all_styles:
            return {"score": 0.7, "dominant_style": "unknown"}

        # Find dominant style
        dominant = max(set(all_styles), key=all_styles.count)

        # Compute compatibility scores
        scores = []
        for item in items:
            item_score = 0.5  # Default if no matching styles
            for style in item.style_tags:
                if style in cls.COMPATIBILITY:
                    comp = cls.COMPATIBILITY[style].get(dominant, 0.5)
                    item_score = max(item_score, comp)
            scores.append(item_score)

        return {
            "score": float(np.mean(scores)),
            "dominant_style": dominant,
            "per_item_scores": scores
        }


class OccasionEngine:
    """Occasion-appropriate outfit scoring"""

    OCCASION_PREFERENCES = {
        "casual": {
            "preferred_types": ["t-shirt", "jeans", "sneakers", "hoodie", "shorts"],
            "preferred_styles": ["casual", "streetwear", "minimalist"],
            "avoid_types": ["formal-dress", "blazer", "heels"],
            "formality": 0.2
        },
        "formal": {
            "preferred_types": ["shirt", "blazer", "trousers", "heels", "oxford-shoes"],
            "preferred_styles": ["formal", "elegant", "minimalist"],
            "avoid_types": ["t-shirt", "hoodie", "sneakers", "shorts"],
            "formality": 0.9
        },
        "office": {
            "preferred_types": ["shirt", "blouse", "trousers", "chinos", "blazer", "loafers"],
            "preferred_styles": ["formal", "minimalist", "preppy"],
            "avoid_types": ["hoodie", "shorts", "tank-top"],
            "formality": 0.7
        },
        "date": {
            "preferred_types": ["shirt", "jeans", "dress", "blouse", "heels"],
            "preferred_styles": ["elegant", "casual", "minimalist"],
            "avoid_types": ["athletic"],
            "formality": 0.5
        },
        "party": {
            "preferred_types": ["cocktail-dress", "shirt", "blazer", "heels"],
            "preferred_styles": ["elegant", "edgy", "streetwear"],
            "avoid_types": ["athletic", "cargo-pants"],
            "formality": 0.6
        },
        "workout": {
            "preferred_types": ["tank-top", "leggings", "joggers", "sneakers"],
            "preferred_styles": ["athletic"],
            "avoid_types": ["formal-dress", "blazer", "heels"],
            "formality": 0.1
        }
    }

    @classmethod
    def score_outfit_for_occasion(
        cls,
        items: List[ClothingItem],
        occasion: str
    ) -> Dict:
        """Score outfit for specific occasion"""
        occasion = occasion.lower()
        if occasion not in cls.OCCASION_PREFERENCES:
            occasion = "casual"  # Default fallback

        prefs = cls.OCCASION_PREFERENCES[occasion]

        type_scores = []
        style_scores = []
        penalties = []

        for item in items:
            # Type score
            if item.clothing_type in prefs["preferred_types"]:
                type_scores.append(1.0)
            elif item.clothing_type in prefs.get("avoid_types", []):
                type_scores.append(0.2)
                penalties.append(f"{item.clothing_type} not ideal for {occasion}")
            else:
                type_scores.append(0.6)

            # Style score
            style_match = any(s in prefs["preferred_styles"] for s in item.style_tags)
            style_scores.append(1.0 if style_match else 0.6)

        avg_type = np.mean(type_scores) if type_scores else 0.5
        avg_style = np.mean(style_scores) if style_scores else 0.5

        return {
            "score": float((avg_type * 0.6 + avg_style * 0.4)),
            "type_match": float(avg_type),
            "style_match": float(avg_style),
            "penalties": penalties,
            "occasion": occasion
        }


class RecommendationEngine:
    """
    Main recommendation engine
    Combines all scoring systems for final recommendations
    """

    def __init__(
        self,
        embedder=None,  # Optional FashionEmbedder
        use_ml_ranking: bool = True
    ):
        self.harmony_engine = HarmonyEngine()
        self.style_engine = StyleCompatibilityEngine()
        self.occasion_engine = OccasionEngine()
        self.embedder = embedder
        self.use_ml_ranking = use_ml_ranking

    def score_outfit(
        self,
        items: List[ClothingItem],
        occasion: str = "casual",
        user_preferences: Optional[Dict] = None
    ) -> OutfitRecommendation:
        """
        Score an outfit combination

        Args:
            items: List of clothing items
            occasion: Target occasion
            user_preferences: User style preferences

        Returns:
            OutfitRecommendation with detailed scoring
        """
        # Validate outfit structure
        validation = self._validate_outfit(items)
        if not validation["valid"]:
            return OutfitRecommendation(
                items=items,
                score=0.0,
                reasons=[validation["reason"]],
                harmony_type="invalid",
                occasion_match=0.0,
                style_coherence=0.0,
                breakdown={"validation": validation}
            )

        # Color harmony (30% weight)
        harmony_result = self.harmony_engine.compute_multi_item_harmony(items)
        harmony_score = harmony_result["score"]

        # Style compatibility (25% weight)
        style_result = self.style_engine.compute_compatibility(items)
        style_score = style_result["score"]

        # Occasion appropriateness (25% weight)
        occasion_result = self.occasion_engine.score_outfit_for_occasion(items, occasion)
        occasion_score = occasion_result["score"]

        # Embedding similarity if available (20% weight)
        embedding_score = 0.7  # Default
        if self.embedder and all(item.embedding is not None for item in items):
            embeddings = [item.embedding for item in items]
            embedding_result = self._compute_embedding_compatibility(embeddings)
            embedding_score = embedding_result["score"]

        # User preference alignment
        preference_boost = 0.0
        if user_preferences:
            preference_boost = self._compute_preference_alignment(items, user_preferences)

        # Weighted final score
        final_score = (
            harmony_score * 0.30 +
            style_score * 0.25 +
            occasion_score * 0.25 +
            embedding_score * 0.20 +
            preference_boost * 0.10  # Bonus
        )

        # Clamp to [0, 1]
        final_score = max(0.0, min(1.0, final_score))

        # Build reasons
        reasons = self._build_reasons(
            harmony_result, style_result, occasion_result, final_score
        )

        return OutfitRecommendation(
            items=items,
            score=final_score,
            reasons=reasons,
            harmony_type=harmony_result["harmony_type"],
            occasion_match=occasion_score,
            style_coherence=style_score,
            breakdown={
                "harmony": harmony_result,
                "style": style_result,
                "occasion": occasion_result,
                "embedding": {"score": embedding_score},
                "preference_boost": preference_boost
            }
        )

    def generate_outfits(
        self,
        wardrobe: List[ClothingItem],
        occasion: str = "casual",
        user_preferences: Optional[Dict] = None,
        top_k: int = 5,
        must_include: Optional[ClothingItem] = None
    ) -> List[OutfitRecommendation]:
        """
        Generate top outfit combinations from wardrobe

        Args:
            wardrobe: List of all wardrobe items
            occasion: Target occasion
            user_preferences: User style preferences
            top_k: Number of outfits to return
            must_include: Item that must be in outfit (e.g., "match this shirt")

        Returns:
            List of top-scoring outfit recommendations
        """
        # Group items by category
        by_category = self._group_by_category(wardrobe)

        # Generate valid combinations
        combinations = self._generate_combinations(by_category, must_include)

        # Score all combinations
        scored = []
        for combo in combinations:
            rec = self.score_outfit(combo, occasion, user_preferences)
            if rec.score > 0.3:  # Filter low-scoring
                scored.append(rec)

        # Sort by score, return top K
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

    def _validate_outfit(self, items: List[ClothingItem]) -> Dict:
        """Validate outfit has required pieces"""
        categories = [item.category for item in items]

        has_top = "top" in categories or "outerwear" in categories
        has_bottom = "bottom" in categories
        has_dress = "dress" in categories

        # Valid combinations:
        # 1. Top + Bottom
        # 2. Dress (standalone)
        # 3. Top + Bottom + Outerwear

        if has_dress:
            return {"valid": True, "reason": "Valid dress outfit"}

        if has_top and has_bottom:
            return {"valid": True, "reason": "Valid top + bottom combo"}

        if not has_top and not has_dress:
            return {"valid": False, "reason": "Missing top or dress"}

        if not has_bottom and not has_dress:
            return {"valid": False, "reason": "Missing bottom or dress"}

        return {"valid": True, "reason": "Valid outfit"}

    def _group_by_category(
        self,
        items: List[ClothingItem]
    ) -> Dict[str, List[ClothingItem]]:
        """Group items by category"""
        groups = {
            "top": [],
            "bottom": [],
            "outerwear": [],
            "dress": [],
            "footwear": [],
            "accessory": []
        }

        for item in items:
            if item.category in groups:
                groups[item.category].append(item)

        return groups

    def _generate_combinations(
        self,
        by_category: Dict[str, List[ClothingItem]],
        must_include: Optional[ClothingItem] = None
    ) -> List[List[ClothingItem]]:
        """Generate valid outfit combinations"""
        from itertools import product

        combinations = []

        # Top + Bottom combinations
        tops = by_category["top"] + by_category.get("outerwear", [])
        bottoms = by_category["bottom"]

        if tops and bottoms:
            for top, bottom in product(tops, bottoms):
                if must_include is None or must_include.id in [top.id, bottom.id]:
                    combinations.append([top, bottom])

                    # Optionally add outerwear
                    for outer in by_category.get("outerwear", []):
                        if outer.id != top.id:
                            combinations.append([top, bottom, outer])

        # Dress combinations
        for dress in by_category.get("dress", []):
            if must_include is None or must_include.id == dress.id:
                combinations.append([dress])

        return combinations

    def _compute_embedding_compatibility(
        self,
        embeddings: List[np.ndarray]
    ) -> Dict:
        """Compute embedding-based compatibility"""
        if len(embeddings) < 2:
            return {"score": 1.0}

        similarities = []
        for i, emb1 in enumerate(embeddings):
            for emb2 in embeddings[i + 1:]:
                sim = float(np.dot(emb1, emb2))
                similarities.append(sim)

        return {
            "score": np.mean(similarities),
            "min": min(similarities),
            "max": max(similarities)
        }

    def _compute_preference_alignment(
        self,
        items: List[ClothingItem],
        preferences: Dict
    ) -> float:
        """Compute alignment with user preferences"""
        score = 0.0

        preferred_styles = preferences.get("styles", [])
        if preferred_styles:
            match_count = sum(
                1 for item in items
                for style in item.style_tags
                if style in preferred_styles
            )
            score += min(match_count / len(items), 1.0) * 0.5

        preferred_colors = preferences.get("colors", [])
        if preferred_colors:
            match_count = sum(
                1 for item in items
                for color in item.colors
                if color["name"].lower() in preferred_colors
            )
            score += min(match_count / len(items), 1.0) * 0.5

        return score

    def _build_reasons(
        self,
        harmony: Dict,
        style: Dict,
        occasion: Dict,
        final_score: float
    ) -> List[str]:
        """Build human-readable reasons for recommendation"""
        reasons = []

        # Harmony reason
        harmony_type = harmony["harmony_type"]
        if harmony["score"] > 0.85:
            reasons.append(f"Excellent {harmony_type} color harmony")
        elif harmony["score"] > 0.7:
            reasons.append(f"Good {harmony_type} color pairing")

        # Style reason
        if style["score"] > 0.8:
            reasons.append(f"Cohesive {style['dominant_style']} style")

        # Occasion reason
        if occasion["score"] > 0.8:
            reasons.append(f"Perfect for {occasion['occasion']}")
        elif occasion["score"] > 0.6:
            reasons.append(f"Suitable for {occasion['occasion']}")

        # Penalties
        reasons.extend(occasion.get("penalties", []))

        # Overall
        if final_score > 0.85:
            reasons.insert(0, "Highly recommended outfit")
        elif final_score > 0.7:
            reasons.insert(0, "Great outfit choice")

        return reasons
