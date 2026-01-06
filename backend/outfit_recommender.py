"""
MODEL 3: Outfit Recommendation Engine
===================================================================
Generates outfit recommendations based on color harmony and occasion.

Purpose: Create valid outfit combinations from analyzed clothing items
Technology: Color harmony theory (HSV analysis) + rule-based validation
Input: List of garment dictionaries with type, color, hex
Output: Ranked outfit recommendations sorted by harmony score

Features:
- Color harmony detection (Monochromatic, Analogous, Triadic, Complementary)
- Occasion-based scoring (formal, office, casual, party, date, college)
- Rule-based outfit validation (top + bottom required)
- Score-based ranking

Usage:
    from outfit_recommender import recommend_outfits, get_outfit_recommender
    
    garments = [
        {"name": "Blue Shirt", "type": "top", "color": "Blue", "hex": "#1f3c88"},
        {"name": "Black Jeans", "type": "bottom", "color": "Black", "hex": "#000000"}
    ]
    
    recommendations = recommend_outfits(garments, occasion="formal")
"""

import colorsys
from typing import List, Dict, Tuple


# -----------------------------
# HEX to HSV Conversion
# -----------------------------
def hex_to_hsv(hex_color: str) -> Tuple[float, float, float]:
    """Convert HEX color to HSV (Hue in degrees, Saturation, Value)"""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s, v


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def hsv_to_hex(h: float, s: float, v: float) -> str:
    """Convert HSV to HEX color"""
    r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


def get_all_color_matches(hex_color: str) -> Dict[str, List[str]]:
    """
    Get all color harmony matches for a given hex color.
    
    Args:
        hex_color: Base HEX color code
        
    Returns:
        Dictionary with harmony types and their matching colors
    """
    h, s, v = hex_to_hsv(hex_color)
    
    matches = {
        "monochromatic": [],
        "analogous": [],
        "complementary": [],
        "triadic": []
    }
    
    # Monochromatic - same hue, different saturation/value
    for sv_offset in [-0.3, -0.15, 0.15, 0.3]:
        new_s = max(0.1, min(1.0, s + sv_offset))
        new_v = max(0.2, min(1.0, v - sv_offset * 0.5))
        matches["monochromatic"].append(hsv_to_hex(h, new_s, new_v))
    
    # Analogous - hues within 30 degrees
    for h_offset in [-30, -15, 15, 30]:
        new_h = (h + h_offset) % 360
        matches["analogous"].append(hsv_to_hex(new_h, s, v))
    
    # Complementary - opposite on color wheel
    comp_h = (h + 180) % 360
    matches["complementary"].append(hsv_to_hex(comp_h, s, v))
    matches["complementary"].append(hsv_to_hex(comp_h, max(0.2, s - 0.2), v))
    matches["complementary"].append(hsv_to_hex(comp_h, min(1.0, s + 0.2), v))
    
    # Triadic - 120 degrees apart
    for h_offset in [120, 240]:
        new_h = (h + h_offset) % 360
        matches["triadic"].append(hsv_to_hex(new_h, s, v))
    
    return matches


def recommend_matching_colors(
    hex_color: str,
    style: str = "balanced",
    top_n: int = 5
) -> List[Dict]:
    """
    Recommend matching colors based on style preference.
    
    Args:
        hex_color: Base HEX color
        style: 'bold', 'harmonious', 'balanced', 'conservative'
        top_n: Number of recommendations
        
    Returns:
        List of recommended colors with metadata
    """
    all_matches = get_all_color_matches(hex_color)
    recommendations = []
    
    style_priorities = {
        "bold": ["complementary", "triadic", "analogous", "monochromatic"],
        "harmonious": ["analogous", "monochromatic", "triadic", "complementary"],
        "balanced": ["analogous", "complementary", "triadic", "monochromatic"],
        "conservative": ["monochromatic", "analogous", "triadic", "complementary"]
    }
    
    priority = style_priorities.get(style, style_priorities["balanced"])
    
    for harmony_type in priority:
        for color in all_matches.get(harmony_type, []):
            if len(recommendations) >= top_n:
                break
            recommendations.append({
                "hex": color,
                "harmony_type": harmony_type,
                "confidence": 0.9 if harmony_type in ["monochromatic", "analogous"] else 0.8
            })
        if len(recommendations) >= top_n:
            break
    
    return recommendations


# -----------------------------
# Color Harmony Detection
# -----------------------------
def color_harmony(h1: float, h2: float) -> Tuple[str, float]:
    """
    Determine color harmony type and score based on hue difference.
    
    Args:
        h1, h2: Hue values in degrees (0-360)
        
    Returns:
        (harmony_type, base_score)
    """
    diff = abs(h1 - h2)
    diff = min(diff, 360 - diff)  # Handle circular hue
    
    if diff < 15:
        return "Monochromatic", 0.95
    elif diff < 40:
        return "Analogous", 0.90
    elif abs(diff - 120) < 15:
        return "Triadic", 0.85
    elif abs(diff - 180) < 15:
        return "Complementary", 0.90
    else:
        return "Low Harmony", 0.50


# -----------------------------
# Occasion-Based Weights
# -----------------------------
OCCASION_WEIGHTS = {
    "formal": ["Monochromatic", "Analogous"],
    "office": ["Monochromatic", "Analogous"],
    "business": ["Monochromatic", "Analogous"],
    "casual": ["Analogous", "Triadic"],
    "party": ["Complementary", "Triadic"],
    "date": ["Analogous", "Complementary"],
    "college": ["Monochromatic", "Analogous"],
    "sports": ["Triadic", "Complementary"]
}


# -----------------------------
# Rule-Based Outfit Validation
# -----------------------------
def is_valid_outfit(items: List[Dict]) -> bool:
    """
    Validate if the combination forms a valid outfit.
    
    Args:
        items: List of garment dictionaries with 'type' key
        
    Returns:
        True if valid outfit (has one top and one bottom)
    """
    types = [item.get("type", "").lower() for item in items]
    
    # Valid: one top and one bottom
    if types.count("top") == 1 and types.count("bottom") == 1:
        return True
    
    # Valid: single dress
    if types == ["dress"]:
        return True
    
    # Valid: blazer + bottom + top
    if sorted(types) == ["blazer", "bottom", "top"]:
        return True
    
    return False


# -----------------------------
# Outfit Recommendation Engine
# -----------------------------
def recommend_outfits(garments: List[Dict], occasion: str = "casual") -> List[Dict]:
    """
    Generate ranked outfit recommendations from a list of garments.
    
    Args:
        garments: List of garment dictionaries with keys:
            - name/id: Garment identifier
            - type: "top", "bottom", or "dress"
            - color: Color name (optional)
            - hex/dominant_color: HEX color code
        occasion: One of "formal", "office", "casual", "party", "date", "college", "sports"
    
    Returns:
        List of outfit recommendations sorted by score, each containing:
        - outfit: List of garment names
        - types: List of garment types
        - colors: List of color names
        - hexes: List of HEX codes
        - harmony: Harmony type
        - occasion: Occasion used
        - score: Final score (0-1)
        - items: Original garment objects
    """
    recommendations = []
    
    # Normalize garment data (handle different key names)
    normalized = []
    for g in garments:
        normalized.append({
            "name": g.get("name") or g.get("id") or "Unknown",
            "type": g.get("type", "").lower(),
            "color": g.get("color") or g.get("name", "Unknown"),
            "hex": g.get("hex") or g.get("dominant_color") or "#808080",
            "original": g
        })
    
    # Generate all pairwise combinations
    for i in range(len(normalized)):
        for j in range(i + 1, len(normalized)):
            outfit = [normalized[i], normalized[j]]
            
            # Skip invalid combinations
            if not is_valid_outfit(outfit):
                continue
            
            # Get hex colors
            hex1 = outfit[0]["hex"]
            hex2 = outfit[1]["hex"]
            
            # Calculate color harmony
            h1, s1, v1 = hex_to_hsv(hex1)
            h2, s2, v2 = hex_to_hsv(hex2)
            
            harmony, base_score = color_harmony(h1, h2)
            
            # Apply occasion boost
            occasion_boost = 0.2 if harmony in OCCASION_WEIGHTS.get(occasion, []) else 0
            final_score = round(min(base_score + occasion_boost, 1.0), 2)
            
            recommendations.append({
                "outfit": [outfit[0]["name"], outfit[1]["name"]],
                "types": [outfit[0]["type"], outfit[1]["type"]],
                "colors": [outfit[0]["color"], outfit[1]["color"]],
                "hexes": [hex1, hex2],
                "harmony": harmony,
                "occasion": occasion,
                "score": final_score,
                "items": [outfit[0]["original"], outfit[1]["original"]]
            })
    
    # Sort by score (descending)
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations


class OutfitRecommender:
    """
    Class wrapper for outfit recommendation functionality.
    Provides compatibility with existing API.
    """
    
    def __init__(self):
        """Initialize the recommender"""
        print("✅ Outfit Recommender initialized (Color Harmony + Occasion Rules)")
    
    def recommend_outfits(
        self,
        clothing_items: List[Dict],
        occasion: str = "casual",
        max_outfits: int = 5,
        items_per_outfit: int = 2
    ) -> List[Dict]:
        """
        Generate intelligent outfit recommendations.
        
        Args:
            clothing_items: List of garment dictionaries
            occasion: Occasion type
            max_outfits: Maximum number of outfits to return
            items_per_outfit: Items per outfit (currently always 2)
            
        Returns:
            List of outfit recommendations
        """
        all_recommendations = recommend_outfits(clothing_items, occasion)
        return all_recommendations[:max_outfits]
    
    def get_best_outfit(self, clothing_items: List[Dict], occasion: str = "casual") -> Dict:
        """Get the single best outfit recommendation."""
        recommendations = self.recommend_outfits(clothing_items, occasion, max_outfits=1)
        return recommendations[0] if recommendations else None


# Global recommender instance
_recommender = None


def get_outfit_recommender() -> OutfitRecommender:
    """Get or create global outfit recommender instance"""
    global _recommender
    if _recommender is None:
        _recommender = OutfitRecommender()
    return _recommender


if __name__ == "__main__":
    # Example usage
    garments = [
        {"name": "Blue Shirt", "type": "top", "color": "Royal Blue", "hex": "#1f3c88"},
        {"name": "Black Jeans", "type": "bottom", "color": "Black", "hex": "#000000"},
        {"name": "Red T-Shirt", "type": "top", "color": "Red", "hex": "#c1121f"},
        {"name": "Khaki Pants", "type": "bottom", "color": "Khaki", "hex": "#c3b091"}
    ]
    
    print("Testing Outfit Recommender...")
    results = recommend_outfits(garments, occasion="formal")
    
    print(f"\nFound {len(results)} outfit combinations:\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['outfit'][0]} + {r['outfit'][1]}")
        print(f"   Colors: {r['colors'][0]} + {r['colors'][1]}")
        print(f"   Harmony: {r['harmony']} | Score: {r['score']}")
        print()
