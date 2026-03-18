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
- HARD CONSTRAINT: Every outfit MUST have exactly 1 top + 1 bottom
- Confidence threshold filtering (rejects low-confidence classifications)

Usage:
    from outfit_recommender import recommend_outfits, get_outfit_recommender
    
    garments = [
        {"name": "Blue Shirt", "type": "top", "color": "Blue", "hex": "#1f3c88"},
        {"name": "Black Jeans", "type": "bottom", "color": "Black", "hex": "#000000"}
    ]
    
    recommendations = recommend_outfits(garments, occasion="formal")
"""

import colorsys
import logging
from typing import List, Dict, Tuple, Optional
from enum import Enum

# Configure logging for outfit recommendations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------
# Type Enums and Constants
# -----------------------------
class GarmentType(str, Enum):
    """Valid garment types - enforced enum for type safety"""
    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"
    BLAZER = "blazer"
    UNKNOWN = "unknown"


# Confidence threshold - items below this are marked UNKNOWN
CONFIDENCE_THRESHOLD = 0.70  # 70% minimum confidence required

# Type aliases for normalization
TYPE_ALIASES = {
    # Top aliases
    "top": GarmentType.TOP,
    "shirt": GarmentType.TOP,
    "blouse": GarmentType.TOP,
    "t-shirt": GarmentType.TOP,
    "tshirt": GarmentType.TOP,
    "polo": GarmentType.TOP,
    "sweater": GarmentType.TOP,
    "hoodie": GarmentType.TOP,
    "jacket": GarmentType.TOP,
    "coat": GarmentType.TOP,
    # Bottom aliases  
    "bottom": GarmentType.BOTTOM,
    "pants": GarmentType.BOTTOM,
    "pant": GarmentType.BOTTOM,
    "jeans": GarmentType.BOTTOM,
    "trousers": GarmentType.BOTTOM,
    "shorts": GarmentType.BOTTOM,
    "skirt": GarmentType.BOTTOM,
    # Other
    "dress": GarmentType.DRESS,
    "blazer": GarmentType.BLAZER,
}


def normalize_garment_type(raw_type: str, confidence: float = 1.0) -> GarmentType:
    """
    Normalize garment type to valid enum with confidence check.
    
    Args:
        raw_type: Raw type string from classification
        confidence: Classification confidence (0-1)
        
    Returns:
        Normalized GarmentType enum value
    """
    # Check confidence threshold first
    if confidence < CONFIDENCE_THRESHOLD:
        logger.warning(f"Low confidence ({confidence:.2%}) for type '{raw_type}' - marking as UNKNOWN")
        return GarmentType.UNKNOWN
    
    # Normalize to lowercase and strip
    normalized = raw_type.strip().lower() if raw_type else ""
    
    # Look up in aliases
    garment_type = TYPE_ALIASES.get(normalized, GarmentType.UNKNOWN)
    
    if garment_type == GarmentType.UNKNOWN and normalized:
        logger.warning(f"Unknown garment type '{raw_type}' - cannot be used in outfits")
    
    return garment_type


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
# Rule-Based Outfit Validation (HARDENED)
# -----------------------------
def is_valid_outfit(items: List[Dict], return_reason: bool = False) -> bool | Tuple[bool, str]:
    """
    Validate if the combination forms a valid outfit.
    HARD CONSTRAINT: Must have exactly 1 top + 1 bottom for basic outfits.
    
    Args:
        items: List of garment dictionaries with 'type' and optionally 'confidence' keys
        return_reason: If True, return (is_valid, reason) tuple for debugging
        
    Returns:
        True if valid outfit, or (True/False, reason_string) if return_reason=True
    """
    if not items:
        reason = "REJECTED: Empty item list"
        logger.debug(reason)
        return (False, reason) if return_reason else False
    
    # Normalize all types with confidence checking
    normalized_types = []
    for item in items:
        raw_type = item.get("type", "")
        confidence = item.get("confidence", 1.0)  # Default to 1.0 if not provided
        
        normalized = normalize_garment_type(raw_type, confidence)
        normalized_types.append(normalized)
    
    # HARD CONSTRAINT: No UNKNOWN types allowed
    if GarmentType.UNKNOWN in normalized_types:
        reason = f"REJECTED: Contains UNKNOWN type(s) - raw types: {[item.get('type') for item in items]}"
        logger.warning(reason)
        return (False, reason) if return_reason else False
    
    # Count types
    top_count = normalized_types.count(GarmentType.TOP)
    bottom_count = normalized_types.count(GarmentType.BOTTOM)
    dress_count = normalized_types.count(GarmentType.DRESS)
    blazer_count = normalized_types.count(GarmentType.BLAZER)
    
    # ========================================
    # VALID COMBINATIONS (strict rules)
    # ========================================
    
    # Rule 1: EXACTLY one top + one bottom (most common)
    if len(items) == 2 and top_count == 1 and bottom_count == 1:
        reason = "VALID: 1 top + 1 bottom"
        logger.debug(reason)
        return (True, reason) if return_reason else True
    
    # Rule 2: Single dress (complete outfit)
    if len(items) == 1 and dress_count == 1:
        reason = "VALID: Single dress"
        logger.debug(reason)
        return (True, reason) if return_reason else True
    
    # Rule 3: Blazer + top + bottom (formal 3-piece)
    if len(items) == 3 and blazer_count == 1 and top_count == 1 and bottom_count == 1:
        reason = "VALID: Blazer + top + bottom"
        logger.debug(reason)
        return (True, reason) if return_reason else True
    
    # ========================================
    # INVALID COMBINATIONS (explicit rejections)
    # ========================================
    
    if top_count >= 2:
        reason = f"REJECTED: Multiple tops ({top_count}) - cannot pair top+top"
        logger.warning(reason)
        return (False, reason) if return_reason else False
    
    if bottom_count >= 2:
        reason = f"REJECTED: Multiple bottoms ({bottom_count}) - cannot pair bottom+bottom"
        logger.warning(reason)
        return (False, reason) if return_reason else False
    
    if top_count == 0 and bottom_count > 0:
        reason = f"REJECTED: No top found - have {bottom_count} bottom(s)"
        logger.warning(reason)
        return (False, reason) if return_reason else False
    
    if bottom_count == 0 and top_count > 0:
        reason = f"REJECTED: No bottom found - have {top_count} top(s)"
        logger.warning(reason)
        return (False, reason) if return_reason else False
    
    # Default rejection
    types_str = [t.value for t in normalized_types]
    reason = f"REJECTED: Invalid combination - types: {types_str}"
    logger.warning(reason)
    return (False, reason) if return_reason else False


def separate_by_type(garments: List[Dict]) -> Dict[GarmentType, List[Dict]]:
    """
    Separate garments by their normalized type.
    Filters out items with low confidence or unknown types.
    
    Args:
        garments: List of garment dictionaries
        
    Returns:
        Dictionary mapping GarmentType to list of garments
    """
    separated = {
        GarmentType.TOP: [],
        GarmentType.BOTTOM: [],
        GarmentType.DRESS: [],
        GarmentType.BLAZER: [],
        GarmentType.UNKNOWN: [],  # For logging purposes
    }
    
    for g in garments:
        raw_type = g.get("type", "")
        confidence = g.get("confidence", 1.0)
        
        normalized_type = normalize_garment_type(raw_type, confidence)
        
        # Create normalized garment dict
        normalized_garment = {
            "name": g.get("name") or g.get("id") or "Unknown",
            "type": normalized_type.value,
            "normalized_type": normalized_type,
            "color": g.get("color") or g.get("name", "Unknown"),
            "hex": g.get("hex") or g.get("dominant_color") or "#808080",
            "confidence": confidence,
            "original": g
        }
        
        separated[normalized_type].append(normalized_garment)
    
    # Log separation results
    logger.info(f"📊 Garment separation: tops={len(separated[GarmentType.TOP])}, "
                f"bottoms={len(separated[GarmentType.BOTTOM])}, "
                f"dresses={len(separated[GarmentType.DRESS])}, "
                f"unknown={len(separated[GarmentType.UNKNOWN])}")
    
    if separated[GarmentType.UNKNOWN]:
        logger.warning(f"⚠️ {len(separated[GarmentType.UNKNOWN])} items rejected due to low confidence or unknown type")
    
    return separated


# -----------------------------
# Outfit Recommendation Engine (PRODUCTION-GRADE)
# -----------------------------
def recommend_outfits(garments: List[Dict], occasion: str = "casual") -> List[Dict]:
    """
    Generate ranked outfit recommendations using EXPLICIT top×bottom pairing.
    
    ARCHITECTURE:
    1. Separate garments by type (with confidence filtering)
    2. Generate ONLY valid combinations (tops × bottoms)
    3. Score each combination by color harmony
    4. Apply occasion-based boosts
    5. Sort and return top recommendations
    
    HARD CONSTRAINTS:
    - Every outfit MUST have exactly 1 top + 1 bottom
    - Items with confidence < 70% are EXCLUDED
    - No duplicate items in same outfit
    - No top+top or bottom+bottom combinations
    
    Args:
        garments: List of garment dictionaries with keys:
            - name/id: Garment identifier
            - type: "top", "bottom", or "dress"
            - color: Color name (optional)
            - hex/dominant_color: HEX color code
            - confidence: Classification confidence (0-1)
        occasion: One of "formal", "office", "casual", "party", "date", "college", "sports"
    
    Returns:
        List of outfit recommendations sorted by score
    """
    recommendations = []
    rejected_combinations = []  # For debugging
    
    # Step 1: Separate garments by normalized type (with confidence filtering)
    separated = separate_by_type(garments)
    
    tops = separated[GarmentType.TOP]
    bottoms = separated[GarmentType.BOTTOM]
    dresses = separated[GarmentType.DRESS]
    
    logger.info(f"🎯 Generating outfits for occasion: {occasion}")
    logger.info(f"   Available: {len(tops)} tops, {len(bottoms)} bottoms, {len(dresses)} dresses")
    
    # Step 2: Generate ONLY valid top × bottom combinations
    # This is the architectural fix - we NEVER iterate all pairs
    for top in tops:
        for bottom in bottoms:
            # Double-check types (defense in depth)
            if top["normalized_type"] != GarmentType.TOP:
                logger.error(f"Type integrity violation: {top['name']} is not a TOP")
                continue
            if bottom["normalized_type"] != GarmentType.BOTTOM:
                logger.error(f"Type integrity violation: {bottom['name']} is not a BOTTOM")
                continue
            
            # Ensure different items (by ID/name)
            if top["name"] == bottom["name"]:
                rejected_combinations.append({
                    "items": [top["name"], bottom["name"]],
                    "reason": "Same item cannot be both top and bottom"
                })
                continue
            
            outfit = [top, bottom]
            
            # Validate outfit (should always pass, but defense in depth)
            is_valid, reason = is_valid_outfit(
                [{"type": top["type"], "confidence": top["confidence"]},
                 {"type": bottom["type"], "confidence": bottom["confidence"]}],
                return_reason=True
            )
            
            if not is_valid:
                rejected_combinations.append({
                    "items": [top["name"], bottom["name"]],
                    "reason": reason
                })
                continue
            
            # Step 3: Calculate color harmony score
            hex1 = top["hex"]
            hex2 = bottom["hex"]
            
            try:
                h1, s1, v1 = hex_to_hsv(hex1)
                h2, s2, v2 = hex_to_hsv(hex2)
                harmony, base_score = color_harmony(h1, h2)
            except Exception as e:
                logger.warning(f"Color analysis failed for {top['name']} + {bottom['name']}: {e}")
                harmony, base_score = "Unknown", 0.5
            
            # Step 4: Apply occasion boost
            occasion_boost = 0.2 if harmony in OCCASION_WEIGHTS.get(occasion, []) else 0
            final_score = round(min(base_score + occasion_boost, 1.0), 2)
            
            recommendations.append({
                "outfit": [top["name"], bottom["name"]],
                "types": [top["type"], bottom["type"]],
                "colors": [top["color"], bottom["color"]],
                "hexes": [hex1, hex2],
                "harmony": harmony,
                "occasion": occasion,
                "score": final_score,
                "items": [top["original"], bottom["original"]],
                "total_items": 2,
                # Debug metadata
                "_debug": {
                    "top_confidence": top["confidence"],
                    "bottom_confidence": bottom["confidence"],
                    "validation": reason
                }
            })
    
    # Add single dresses as valid outfits
    for dress in dresses:
        is_valid, reason = is_valid_outfit(
            [{"type": dress["type"], "confidence": dress["confidence"]}],
            return_reason=True
        )
        if is_valid:
            recommendations.append({
                "outfit": [dress["name"]],
                "types": [dress["type"]],
                "colors": [dress["color"]],
                "hexes": [dress["hex"]],
                "harmony": "Single Piece",
                "occasion": occasion,
                "score": 0.85,  # Base score for dresses
                "items": [dress["original"]],
                "total_items": 1,
                "_debug": {
                    "confidence": dress["confidence"],
                    "validation": reason
                }
            })
    
    # Log summary
    logger.info(f"✅ Generated {len(recommendations)} valid outfits")
    if rejected_combinations:
        logger.warning(f"❌ Rejected {len(rejected_combinations)} invalid combinations")
        for rej in rejected_combinations[:5]:  # Log first 5
            logger.debug(f"   Rejected: {rej['items']} - {rej['reason']}")
    
    # Step 5: Sort by score (descending)
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
    # ========================================
    # UNIT TESTS - Validate Bug Fixes
    # ========================================
    import sys
    
    print("=" * 60)
    print("OUTFIT RECOMMENDER UNIT TESTS")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test 1: Valid top + bottom combination
    print("\n📋 Test 1: Valid top + bottom combination")
    test_items = [
        {"name": "Blue Shirt", "type": "top", "confidence": 0.95},
        {"name": "Black Jeans", "type": "bottom", "confidence": 0.92}
    ]
    is_valid, reason = is_valid_outfit(test_items, return_reason=True)
    if is_valid:
        print(f"   ✅ PASS: {reason}")
    else:
        print(f"   ❌ FAIL: Expected valid, got: {reason}")
        all_tests_passed = False
    
    # Test 2: Invalid bottom + bottom combination (THE BUG)
    print("\n📋 Test 2: Invalid bottom + bottom combination (THE BUG)")
    test_items = [
        {"name": "Black Pants", "type": "bottom", "confidence": 0.88},
        {"name": "Blue Jeans", "type": "pants", "confidence": 0.91}  # pants = bottom
    ]
    is_valid, reason = is_valid_outfit(test_items, return_reason=True)
    if not is_valid and "Multiple bottoms" in reason:
        print(f"   ✅ PASS: Correctly rejected - {reason}")
    else:
        print(f"   ❌ FAIL: Should reject bottom+bottom, got: valid={is_valid}, {reason}")
        all_tests_passed = False
    
    # Test 3: Invalid top + top combination
    print("\n📋 Test 3: Invalid top + top combination")
    test_items = [
        {"name": "Red Shirt", "type": "shirt", "confidence": 0.85},
        {"name": "Blue Blouse", "type": "blouse", "confidence": 0.90}
    ]
    is_valid, reason = is_valid_outfit(test_items, return_reason=True)
    if not is_valid and "Multiple tops" in reason:
        print(f"   ✅ PASS: Correctly rejected - {reason}")
    else:
        print(f"   ❌ FAIL: Should reject top+top, got: valid={is_valid}, {reason}")
        all_tests_passed = False
    
    # Test 4: Low confidence item rejection
    print("\n📋 Test 4: Low confidence item rejection")
    test_items = [
        {"name": "Maybe Shirt", "type": "top", "confidence": 0.55},  # Below threshold
        {"name": "Black Jeans", "type": "bottom", "confidence": 0.92}
    ]
    is_valid, reason = is_valid_outfit(test_items, return_reason=True)
    if not is_valid and "UNKNOWN" in reason:
        print(f"   ✅ PASS: Low confidence rejected - {reason}")
    else:
        print(f"   ❌ FAIL: Should reject low confidence, got: valid={is_valid}, {reason}")
        all_tests_passed = False
    
    # Test 5: Type normalization (pants → bottom)
    print("\n📋 Test 5: Type normalization (pants → bottom)")
    normalized = normalize_garment_type("pants", 0.85)
    if normalized == GarmentType.BOTTOM:
        print(f"   ✅ PASS: 'pants' correctly normalized to BOTTOM")
    else:
        print(f"   ❌ FAIL: Expected BOTTOM, got {normalized}")
        all_tests_passed = False
    
    # Test 6: Full recommendation pipeline (should NOT produce bottom+bottom)
    print("\n📋 Test 6: Full recommendation pipeline")
    garments = [
        {"name": "Blue Shirt", "type": "top", "hex": "#1f3c88", "confidence": 0.95},
        {"name": "Black Jeans", "type": "bottom", "hex": "#000000", "confidence": 0.92},
        {"name": "Red T-Shirt", "type": "top", "hex": "#c1121f", "confidence": 0.88},
        {"name": "Khaki Pants", "type": "bottom", "hex": "#c3b091", "confidence": 0.91}
    ]
    
    results = recommend_outfits(garments, occasion="formal")
    invalid_found = False
    for r in results:
        types = r["types"]
        if types.count("top") != 1 or types.count("bottom") != 1:
            invalid_found = True
            print(f"   ❌ FAIL: Invalid outfit found - types: {types}")
    
    if not invalid_found and len(results) > 0:
        print(f"   ✅ PASS: Generated {len(results)} valid outfits")
        for i, r in enumerate(results[:3], 1):
            print(f"      {i}. {r['outfit'][0]} ({r['types'][0]}) + {r['outfit'][1]} ({r['types'][1]})")
    elif len(results) == 0:
        print(f"   ❌ FAIL: No outfits generated")
        all_tests_passed = False
    else:
        all_tests_passed = False
    
    # Test 7: Ensure no bottom+bottom ever passes
    print("\n📋 Test 7: Stress test - only bottoms (should produce 0 outfits)")
    only_bottoms = [
        {"name": "Pants 1", "type": "bottom", "hex": "#000000", "confidence": 0.95},
        {"name": "Pants 2", "type": "pants", "hex": "#333333", "confidence": 0.90},
        {"name": "Jeans 1", "type": "jeans", "hex": "#4169e1", "confidence": 0.88}
    ]
    results = recommend_outfits(only_bottoms, occasion="casual")
    if len(results) == 0:
        print(f"   ✅ PASS: Correctly produced 0 outfits (no tops available)")
    else:
        print(f"   ❌ FAIL: Should produce 0 outfits, got {len(results)}")
        all_tests_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✅ ALL TESTS PASSED - Bug fix verified!")
        print("   bottom+bottom combinations are now IMPOSSIBLE")
    else:
        print("❌ SOME TESTS FAILED - Review the implementation")
        sys.exit(1)
    print("=" * 60)
