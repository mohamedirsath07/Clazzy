"""
Outfit Recommendation Module
Generates outfit recommendations based on color harmony and occasion.

Usage:
    from outfit_recommendation import recommend_outfits
    
    garments = [
        {"name": "Blue Shirt", "type": "top", "color": "Blue", "hex": "#1f3c88"},
        {"name": "Black Jeans", "type": "bottom", "color": "Black", "hex": "#000000"}
    ]
    
    recommendations = recommend_outfits(garments, occasion="formal")
"""

import colorsys


# -----------------------------
# HEX to HSV Conversion
# -----------------------------
def hex_to_hsv(hex_color):
    """Convert HEX color to HSV (Hue in degrees, Saturation, Value)"""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s, v


# -----------------------------
# Color Harmony Detection
# -----------------------------
def color_harmony(h1, h2):
    """Determine color harmony type and score based on hue difference."""
    diff = abs(h1 - h2)
    diff = min(diff, 360 - diff)
    
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
    "casual": ["Analogous", "Triadic"],
    "party": ["Complementary", "Triadic"],
    "date": ["Analogous", "Complementary"],
    "college": ["Monochromatic", "Analogous"]
}


# -----------------------------
# Rule-Based Outfit Validation
# -----------------------------
def is_valid_outfit(items):
    """Validate if the combination forms a valid outfit."""
    types = [item["type"] for item in items]
    
    if types.count("top") == 1 and types.count("bottom") == 1:
        return True
    if types == ["dress"]:
        return True
    if sorted(types) == ["blazer", "bottom", "top"]:
        return True
    
    return False


# -----------------------------
# Outfit Recommendation Engine
# -----------------------------
def recommend_outfits(garments, occasion="casual"):
    """
    Generate ranked outfit recommendations from a list of garments.
    
    Args:
        garments: List of garment dictionaries with keys:
            - name: Garment name
            - type: "top", "bottom", or "dress"
            - color: Color name
            - hex: HEX color code
        occasion: One of "formal", "office", "casual", "party", "date", "college"
    
    Returns:
        List of outfit recommendations sorted by score
    """
    recommendations = []
    
    for i in range(len(garments)):
        for j in range(i + 1, len(garments)):
            outfit = [garments[i], garments[j]]
            
            if not is_valid_outfit(outfit):
                continue
            
            h1, s1, v1 = hex_to_hsv(outfit[0]["hex"])
            h2, s2, v2 = hex_to_hsv(outfit[1]["hex"])
            
            harmony, base_score = color_harmony(h1, h2)
            occasion_boost = 0.2 if harmony in OCCASION_WEIGHTS.get(occasion, []) else 0
            final_score = round(base_score + occasion_boost, 2)
            
            recommendations.append({
                "outfit": [outfit[0]["name"], outfit[1]["name"]],
                "types": [outfit[0]["type"], outfit[1]["type"]],
                "colors": [outfit[0]["color"], outfit[1]["color"]],
                "hexes": [outfit[0]["hex"], outfit[1]["hex"]],
                "harmony": harmony,
                "occasion": occasion,
                "score": final_score
            })
    
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations


if __name__ == "__main__":
    # Example usage
    garments = [
        {"name": "Blue Shirt", "type": "top", "color": "Royal Blue", "hex": "#1f3c88"},
        {"name": "Black Jeans", "type": "bottom", "color": "Black", "hex": "#000000"},
        {"name": "Red T-Shirt", "type": "top", "color": "Red", "hex": "#c1121f"}
    ]
    
    results = recommend_outfits(garments, occasion="formal")
    
    for r in results:
        print(r)
