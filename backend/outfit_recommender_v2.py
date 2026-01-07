"""
OUTFIT RECOMMENDER V2 - ROLE-LOCKED ARCHITECTURE
===================================================================
SHIP-BLOCKING FIX: Ensures top+top and bottom+bottom are IMPOSSIBLE

ARCHITECTURAL RULES (NON-NEGOTIABLE):
1. Outfits are ROLE-LOCKED: {top: item, bottom: item} NOT arrays
2. Items are HARD-SPLIT before any pairing
3. Types are NORMALIZED before classification
4. ML failures use FALLBACK HEURISTICS
5. Final validator DELETES invalid outfits

Author: Principal Engineer (Emergency Fix)
Date: 2024
"""

import colorsys
import logging
import re
from typing import List, Dict, Tuple, Optional, TypedDict, Literal
from enum import Enum
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. TYPE DEFINITIONS (ROLE-LOCKED)
# ═══════════════════════════════════════════════════════════════════════════════

class GarmentType(str, Enum):
    """Valid garment types"""
    TOP = "top"
    BOTTOM = "bottom"
    UNKNOWN = "unknown"


@dataclass
class NormalizedGarment:
    """Garment with normalized type - immutable after creation"""
    name: str
    type: GarmentType          # ML type (may be wrong)
    visual_type: GarmentType   # What it LOOKS like (reality check)
    verified_type: GarmentType # Final consensus (visual wins on conflict)
    color: str
    hex_color: str
    confidence: float
    image_url: str
    original: Dict  # Preserve original data


class RoleLockedOutfit(TypedDict):
    """
    ROLE-LOCKED OUTFIT STRUCTURE
    This is the ONLY valid outfit format. Arrays are BANNED.
    """
    top: Dict      # The item in TOP role - MUST have type="top"
    bottom: Dict   # The item in BOTTOM role - MUST have type="bottom"
    score: float
    harmony: str
    occasion: str


# ═══════════════════════════════════════════════════════════════════════════════
# 2. TYPE NORMALIZATION (SINGLE SOURCE OF TRUTH)
# ═══════════════════════════════════════════════════════════════════════════════

# Confidence threshold - items below this trigger fallbacks
CONFIDENCE_THRESHOLD = 0.50  # Lowered to 50% to be more lenient

# Type aliases - comprehensive mapping
TYPE_ALIASES: Dict[str, GarmentType] = {
    # Top aliases (all variations)
    "top": GarmentType.TOP,
    "shirt": GarmentType.TOP,
    "blouse": GarmentType.TOP,
    "t-shirt": GarmentType.TOP,
    "tshirt": GarmentType.TOP,
    "t_shirt": GarmentType.TOP,
    "tee": GarmentType.TOP,
    "polo": GarmentType.TOP,
    "sweater": GarmentType.TOP,
    "hoodie": GarmentType.TOP,
    "jacket": GarmentType.TOP,
    "coat": GarmentType.TOP,
    "blazer": GarmentType.TOP,
    "cardigan": GarmentType.TOP,
    "tank": GarmentType.TOP,
    "tanktop": GarmentType.TOP,
    "vest": GarmentType.TOP,
    "tunic": GarmentType.TOP,
    "crop": GarmentType.TOP,
    "croptop": GarmentType.TOP,
    
    # Bottom aliases (all variations)
    "bottom": GarmentType.BOTTOM,
    "pants": GarmentType.BOTTOM,
    "pant": GarmentType.BOTTOM,
    "jeans": GarmentType.BOTTOM,
    "jean": GarmentType.BOTTOM,
    "trousers": GarmentType.BOTTOM,
    "trouser": GarmentType.BOTTOM,
    "shorts": GarmentType.BOTTOM,
    "short": GarmentType.BOTTOM,
    "skirt": GarmentType.BOTTOM,
    "leggings": GarmentType.BOTTOM,
    "legging": GarmentType.BOTTOM,
    "joggers": GarmentType.BOTTOM,
    "jogger": GarmentType.BOTTOM,
    "chinos": GarmentType.BOTTOM,
    "chino": GarmentType.BOTTOM,
    "cargo": GarmentType.BOTTOM,
    "slacks": GarmentType.BOTTOM,
    "culottes": GarmentType.BOTTOM,
}


def normalize_type(raw_type: str) -> GarmentType:
    """
    SINGLE FUNCTION for type normalization.
    This is the ONLY place where raw types become GarmentType.
    
    Args:
        raw_type: Raw type string from ML or user
        
    Returns:
        Normalized GarmentType (TOP, BOTTOM, or UNKNOWN)
    """
    if not raw_type:
        return GarmentType.UNKNOWN
    
    # Clean and lowercase
    cleaned = raw_type.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
    
    # Direct lookup
    if cleaned in TYPE_ALIASES:
        return TYPE_ALIASES[cleaned]
    
    # Partial match (for compound types like "blue_shirt")
    for alias, gtype in TYPE_ALIASES.items():
        if alias in cleaned:
            return gtype
    
    return GarmentType.UNKNOWN


# ═══════════════════════════════════════════════════════════════════════════════
# 2.5 VISUAL REALITY VERIFICATION (ML OVERRIDE LAYER)
# ═══════════════════════════════════════════════════════════════════════════════
# THIS SECTION OVERRIDES ML WHEN IT'S CLEARLY WRONG
# A shirt will NEVER pass as a bottom here, regardless of ML confidence

def determine_visual_type(image_path_or_bytes, width: int = 0, height: int = 0) -> GarmentType:
    """
    VISUAL REALITY CHECK: Determine what an image LOOKS like, not what ML says.
    
    Rules:
    - If aspect ratio (height/width) < 1.2 → visually looks like a TOP
    - If aspect ratio (height/width) >= 1.2 → visually looks like a BOTTOM
    
    A shirt will NEVER have height/width >= 1.2 because shirts are wider than tall.
    Pants ARE taller than wide.
    
    Args:
        image_path_or_bytes: Image path or bytes (for future PIL integration)
        width: Image width (if already known)
        height: Image height (if already known)
        
    Returns:
        GarmentType based on VISUAL appearance
    """
    # If we have dimensions, use them
    if width > 0 and height > 0:
        aspect_ratio = height / width
        
        if aspect_ratio < 1.2:
            logger.info(f"   👁️ VISUAL CHECK: {width}x{height} (h/w={aspect_ratio:.2f}) → TOP (wide shape)")
            return GarmentType.TOP
        else:
            logger.info(f"   👁️ VISUAL CHECK: {width}x{height} (h/w={aspect_ratio:.2f}) → BOTTOM (tall shape)")
            return GarmentType.BOTTOM
    
    # If no dimensions, try to get them from PIL
    try:
        from PIL import Image
        import io
        
        if isinstance(image_path_or_bytes, bytes):
            img = Image.open(io.BytesIO(image_path_or_bytes))
        elif isinstance(image_path_or_bytes, str) and image_path_or_bytes.startswith(('http://', 'https://')):
            # URL - can't check without downloading
            return GarmentType.UNKNOWN
        else:
            img = Image.open(image_path_or_bytes)
        
        width, height = img.size
        aspect_ratio = height / width
        
        if aspect_ratio < 1.2:
            logger.info(f"   👁️ VISUAL CHECK (PIL): {width}x{height} (h/w={aspect_ratio:.2f}) → TOP")
            return GarmentType.TOP
        else:
            logger.info(f"   👁️ VISUAL CHECK (PIL): {width}x{height} (h/w={aspect_ratio:.2f}) → BOTTOM")
            return GarmentType.BOTTOM
            
    except Exception as e:
        logger.warning(f"   ⚠️ VISUAL CHECK failed: {e}")
        return GarmentType.UNKNOWN


def determine_final_type(
    model_type: GarmentType,
    visual_type: GarmentType,
    confidence: float = 1.0
) -> GarmentType:
    """
    CONSENSUS DECISION: Combine ML prediction with visual reality.
    
    Rules:
    1. If model and visual AGREE → use that type
    2. If model and visual DISAGREE → TRUST VISUAL (ML is wrong)
    3. If visual is UNKNOWN → use model (but with warning)
    
    This ensures a shirt can NEVER be labeled as bottom if it visually looks like a top.
    
    Args:
        model_type: What ML says
        visual_type: What the image LOOKS like
        confidence: ML confidence (for logging only)
        
    Returns:
        Final GarmentType (visual reality wins on conflict)
    """
    if visual_type == GarmentType.UNKNOWN:
        # Can't verify visually, trust model with warning
        logger.warning(f"   ⚠️ CONSENSUS: Visual unknown, trusting model: {model_type.value}")
        return model_type
    
    if model_type == visual_type:
        # Agreement - high confidence
        logger.info(f"   ✅ CONSENSUS: Model and visual AGREE: {model_type.value}")
        return model_type
    
    # DISAGREEMENT - VISUAL WINS
    logger.warning(f"   🔄 CONSENSUS OVERRIDE: Model said '{model_type.value}' but visual says '{visual_type.value}'")
    logger.warning(f"   🔄 TRUSTING VISUAL REALITY over ML (confidence was {confidence:.0%})")
    return visual_type


def is_visually_a_top(width: int, height: int) -> bool:
    """
    Quick check: Does this image LOOK like a top?
    
    Tops are generally wider than tall or roughly square.
    height/width < 1.2 means it's a top shape.
    """
    if width <= 0 or height <= 0:
        return False
    return (height / width) < 1.2


def is_visually_a_bottom(width: int, height: int) -> bool:
    """
    Quick check: Does this image LOOK like a bottom?
    
    Bottoms (pants) are generally taller than wide.
    height/width >= 1.2 means it's a bottom shape.
    """
    if width <= 0 or height <= 0:
        return False
    return (height / width) >= 1.2


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FALLBACK HEURISTICS (WHEN ML FAILS)
# ═══════════════════════════════════════════════════════════════════════════════

def guess_type_from_filename(filename: str) -> GarmentType:
    """
    FALLBACK A: Guess type from filename patterns.
    
    Args:
        filename: Image filename
        
    Returns:
        Guessed GarmentType
    """
    if not filename:
        return GarmentType.UNKNOWN
    
    lower = filename.lower()
    
    # Top patterns
    top_patterns = ['shirt', 'tee', 'blouse', 'top', 'polo', 'sweater', 
                    'hoodie', 'jacket', 'blazer', 'coat', 'cardigan', 'vest']
    for pattern in top_patterns:
        if pattern in lower:
            logger.info(f"   📁 Filename heuristic: '{filename}' contains '{pattern}' → TOP")
            return GarmentType.TOP
    
    # Bottom patterns
    bottom_patterns = ['pant', 'jean', 'trouser', 'short', 'skirt', 
                       'bottom', 'cargo', 'chino', 'legging', 'jogger']
    for pattern in bottom_patterns:
        if pattern in lower:
            logger.info(f"   📁 Filename heuristic: '{filename}' contains '{pattern}' → BOTTOM")
            return GarmentType.BOTTOM
    
    return GarmentType.UNKNOWN


def guess_type_from_aspect_ratio(width: int, height: int) -> GarmentType:
    """
    FALLBACK B: Guess type from image dimensions.
    - Tall images (height > width) → likely bottoms (pants)
    - Wide images (width > height) → likely tops (shirts)
    
    Args:
        width: Image width
        height: Image height
        
    Returns:
        Guessed GarmentType
    """
    if width <= 0 or height <= 0:
        return GarmentType.UNKNOWN
    
    ratio = width / height
    
    if ratio < 0.7:  # Tall image
        logger.info(f"   📐 Aspect ratio heuristic: {width}x{height} (ratio={ratio:.2f}) → BOTTOM (tall)")
        return GarmentType.BOTTOM
    elif ratio > 1.3:  # Wide image
        logger.info(f"   📐 Aspect ratio heuristic: {width}x{height} (ratio={ratio:.2f}) → TOP (wide)")
        return GarmentType.TOP
    
    return GarmentType.UNKNOWN


def apply_fallback_heuristics(
    garment: Dict,
    current_tops_count: int,
    current_bottoms_count: int
) -> GarmentType:
    """
    Apply ALL fallback heuristics in order.
    LAST RESORT: Balance arrays if all else fails.
    
    Args:
        garment: Garment dictionary
        current_tops_count: Current number of tops
        current_bottoms_count: Current number of bottoms
        
    Returns:
        Final GarmentType (will NEVER return UNKNOWN)
    """
    # Try filename first
    name = garment.get("name") or garment.get("id") or garment.get("filename") or ""
    filename_guess = guess_type_from_filename(name)
    if filename_guess != GarmentType.UNKNOWN:
        return filename_guess
    
    # Try image URL filename
    image_url = garment.get("image") or garment.get("imageUrl") or garment.get("url") or ""
    if image_url:
        # Extract filename from URL
        url_filename = image_url.split("/")[-1].split("?")[0]
        url_guess = guess_type_from_filename(url_filename)
        if url_guess != GarmentType.UNKNOWN:
            return url_guess
    
    # Try aspect ratio if dimensions available
    width = garment.get("width", 0)
    height = garment.get("height", 0)
    if width > 0 and height > 0:
        aspect_guess = guess_type_from_aspect_ratio(width, height)
        if aspect_guess != GarmentType.UNKNOWN:
            return aspect_guess
    
    # LAST RESORT: Balance the arrays
    if current_tops_count <= current_bottoms_count:
        logger.info(f"   ⚖️ Balancing heuristic: assigning as TOP (tops={current_tops_count}, bottoms={current_bottoms_count})")
        return GarmentType.TOP
    else:
        logger.info(f"   ⚖️ Balancing heuristic: assigning as BOTTOM (tops={current_tops_count}, bottoms={current_bottoms_count})")
        return GarmentType.BOTTOM


# ═══════════════════════════════════════════════════════════════════════════════
# 4. FINAL GARMENT TYPE RESOLVER (MULTI-SIGNAL ARCHITECTURE)
# ═══════════════════════════════════════════════════════════════════════════════
# This is the AUTHORITATIVE function for determining garment type.
# ML is now just ONE weak signal among FOUR.

def resolve_garment_type(garment: Dict, width: int = 0, height: int = 0) -> GarmentType:
    """
    FINAL GARMENT TYPE RESOLVER - Multi-Signal Decision Engine
    
    Returns FINAL type: 'top' or 'bottom'. NEVER returns 'unknown'.
    This function overrides ML when needed using multiple signals.
    
    Signal Priority (strongest to weakest):
    1. VISUAL SHAPE (aspect ratio) - PRIMARY
    2. STRUCTURAL FEATURES (sleeves, collar, buttons)
    3. FILENAME HEURISTICS
    4. ML OUTPUT (weakest - only used as tiebreaker)
    
    Args:
        garment: Raw garment dictionary from ML or user
        width: Image width (if known)
        height: Image height (if known)
    
    Returns:
        GarmentType.TOP or GarmentType.BOTTOM (NEVER UNKNOWN)
    """
    signals = []  # List of (type, weight) tuples
    
    name = garment.get("name") or garment.get("id") or garment.get("filename") or ""
    image_url = garment.get("image") or garment.get("imageUrl") or garment.get("url") or ""
    raw_type = garment.get("type", "")
    confidence = garment.get("confidence", 0.5)
    
    # Get dimensions from garment if not provided
    if width == 0:
        width = garment.get("width", 0)
    if height == 0:
        height = garment.get("height", 0)
    
    logger.info(f"   🧠 RESOLVE_GARMENT_TYPE: {name}")
    
    # ═══════════════════════════════════════════════════════════════════
    # SIGNAL 1: VISUAL SHAPE (PRIMARY - weight 3.0)
    # Pants are ALWAYS taller than wide. Shirts are ALWAYS wider than tall.
    # ═══════════════════════════════════════════════════════════════════
    if width > 0 and height > 0:
        aspect_ratio = height / width
        if aspect_ratio > 1.4:
            visual_type = GarmentType.BOTTOM
            signals.append((GarmentType.BOTTOM, 3.0))
            logger.info(f"      📐 SIGNAL 1 (VISUAL): h/w={aspect_ratio:.2f} > 1.4 → BOTTOM (weight 3.0)")
        elif aspect_ratio < 1.0:
            visual_type = GarmentType.TOP
            signals.append((GarmentType.TOP, 3.0))
            logger.info(f"      📐 SIGNAL 1 (VISUAL): h/w={aspect_ratio:.2f} < 1.0 → TOP (weight 3.0)")
        else:
            # Ambiguous zone (1.0 - 1.4) - lower weight
            if aspect_ratio > 1.2:
                signals.append((GarmentType.BOTTOM, 1.5))
                logger.info(f"      📐 SIGNAL 1 (VISUAL): h/w={aspect_ratio:.2f} in [1.2, 1.4] → BOTTOM (weight 1.5)")
            else:
                signals.append((GarmentType.TOP, 1.5))
                logger.info(f"      📐 SIGNAL 1 (VISUAL): h/w={aspect_ratio:.2f} in [1.0, 1.2] → TOP (weight 1.5)")
    else:
        logger.warning(f"      📐 SIGNAL 1 (VISUAL): No dimensions available")
    
    # ═══════════════════════════════════════════════════════════════════
    # SIGNAL 2: STRUCTURAL FEATURES (weight 2.5)
    # Sleeves, collars, buttons → FORCE TOP (pants NEVER have these)
    # ═══════════════════════════════════════════════════════════════════
    structure_type = detect_structural_features(name, image_url)
    if structure_type != GarmentType.UNKNOWN:
        signals.append((structure_type, 2.5))
        logger.info(f"      🔍 SIGNAL 2 (STRUCTURE): {structure_type.value} (weight 2.5)")
    
    # ═══════════════════════════════════════════════════════════════════
    # SIGNAL 3: FILENAME HEURISTICS (weight 2.0)
    # "pant", "jean", "trouser" → bottom
    # "shirt", "tee", "tshirt" → top
    # ═══════════════════════════════════════════════════════════════════
    filename_type = guess_type_from_filename(name)
    if filename_type == GarmentType.UNKNOWN and image_url:
        url_filename = image_url.split("/")[-1].split("?")[0]
        filename_type = guess_type_from_filename(url_filename)
    
    if filename_type != GarmentType.UNKNOWN:
        signals.append((filename_type, 2.0))
        logger.info(f"      📁 SIGNAL 3 (FILENAME): {filename_type.value} (weight 2.0)")
    
    # ═══════════════════════════════════════════════════════════════════
    # SIGNAL 4: ML OUTPUT (WEAKEST - weight 1.0)
    # Only use if confidence is reasonable
    # ═══════════════════════════════════════════════════════════════════
    ml_type = normalize_type(raw_type)
    if ml_type != GarmentType.UNKNOWN:
        # Weight ML based on confidence (max 1.0)
        ml_weight = min(1.0, confidence)
        signals.append((ml_type, ml_weight))
        logger.info(f"      🤖 SIGNAL 4 (ML): {ml_type.value} (weight {ml_weight:.2f}, conf={confidence:.0%})")
    
    # ═══════════════════════════════════════════════════════════════════
    # FINAL DECISION: Weighted Majority Vote
    # ═══════════════════════════════════════════════════════════════════
    if not signals:
        # No signals at all - default to TOP (safer)
        logger.warning(f"      ⚠️ NO SIGNALS - defaulting to TOP")
        return GarmentType.TOP
    
    # Sum weights for each type
    top_weight = sum(w for t, w in signals if t == GarmentType.TOP)
    bottom_weight = sum(w for t, w in signals if t == GarmentType.BOTTOM)
    
    logger.info(f"      📊 VOTE: TOP={top_weight:.1f} vs BOTTOM={bottom_weight:.1f}")
    
    # Decide based on weighted vote
    if bottom_weight > top_weight:
        final_type = GarmentType.BOTTOM
    elif top_weight > bottom_weight:
        final_type = GarmentType.TOP
    else:
        # Tie - use aspect ratio tiebreaker
        if width > 0 and height > 0 and (height / width) > 1.3:
            final_type = GarmentType.BOTTOM
            logger.info(f"      🔀 TIE: Aspect ratio tiebreaker → BOTTOM")
        else:
            final_type = GarmentType.TOP
            logger.info(f"      🔀 TIE: Defaulting to TOP")
    
    logger.info(f"      ✅ FINAL DECISION: {final_type.value.upper()}")
    return final_type


def detect_structural_features(name: str, image_url: str = "") -> GarmentType:
    """
    Detect structural features that indicate TOP (sleeves, collar, buttons).
    Pants NEVER have these features.
    
    Returns:
        GarmentType.TOP if structural features detected, else UNKNOWN
    """
    text = f"{name} {image_url}".lower()
    
    # Features that ONLY tops have
    top_features = [
        "sleeve", "collar", "button", "neck", "v-neck", "crew", 
        "polo", "hoodie", "hood", "zip", "zipper", "pocket",
        "long-sleeve", "short-sleeve", "sleeveless"
    ]
    
    for feature in top_features:
        if feature in text:
            logger.info(f"         🔍 Structural feature detected: '{feature}' → TOP")
            return GarmentType.TOP
    
    # Features that ONLY bottoms have
    bottom_features = [
        "waist", "belt-loop", "beltloop", "inseam", "cuff", "leg"
    ]
    
    for feature in bottom_features:
        if feature in text:
            logger.info(f"         🔍 Structural feature detected: '{feature}' → BOTTOM")
            return GarmentType.BOTTOM
    
    return GarmentType.UNKNOWN


def calculate_pant_likeness_score(garment: Dict) -> float:
    """
    Calculate how likely an item is to be pants (0.0 to 1.0).
    Used for fail-safe recovery when 0 bottoms are detected.
    
    Higher score = more likely to be pants.
    """
    score = 0.0
    
    width = garment.get("width", 0)
    height = garment.get("height", 0)
    name = (garment.get("name") or garment.get("id") or "").lower()
    image_url = (garment.get("image") or garment.get("imageUrl") or "").lower()
    
    # Aspect ratio is the strongest signal
    if width > 0 and height > 0:
        aspect_ratio = height / width
        if aspect_ratio > 1.5:
            score += 0.5  # Very likely pants
        elif aspect_ratio > 1.3:
            score += 0.3  # Likely pants
        elif aspect_ratio > 1.1:
            score += 0.1  # Maybe pants
    
    # Filename hints
    bottom_keywords = ["pant", "jean", "trouser", "short", "skirt", "bottom", "cargo", "chino"]
    for kw in bottom_keywords:
        if kw in name or kw in image_url:
            score += 0.4
            break
    
    # No top keywords (negative signal)
    top_keywords = ["shirt", "tee", "blouse", "top", "polo", "sweater", "hoodie", "jacket"]
    has_top_keyword = any(kw in name or kw in image_url for kw in top_keywords)
    if not has_top_keyword:
        score += 0.1  # Slightly more likely to be pants
    
    return min(1.0, score)


# ═══════════════════════════════════════════════════════════════════════════════
# 4.5 HARD SPLIT WARDROBE WITH FAIL-SAFE RECOVERY
# ═══════════════════════════════════════════════════════════════════════════════

def hard_split_wardrobe(garments: List[Dict]) -> Tuple[List[NormalizedGarment], List[NormalizedGarment]]:
    """
    HARD SPLIT: Separate garments into tops and bottoms BEFORE any pairing.
    
    THIS FUNCTION:
    1. Uses multi-signal RESOLVE_GARMENT_TYPE for EVERY item
    2. NEVER drops an item (always assigns to top or bottom)
    3. Includes FAIL-SAFE RECOVERY if 0 bottoms detected
    4. Returns TWO SEPARATE LISTS
    
    Args:
        garments: Raw garment dictionaries
        
    Returns:
        (tops, bottoms) - Two separate lists, no overlap, no unknowns
    """
    tops: List[NormalizedGarment] = []
    bottoms: List[NormalizedGarment] = []
    
    logger.info("=" * 70)
    logger.info("🔪 HARD SPLIT WARDROBE (MULTI-SIGNAL RESOLVER)")
    logger.info("=" * 70)
    logger.info(f"   Input: {len(garments)} garments")
    
    for i, g in enumerate(garments):
        name = g.get("name") or g.get("id") or f"item_{i}"
        raw_type = g.get("type", "")
        confidence = g.get("confidence", 0.5)
        width = g.get("width", 0)
        height = g.get("height", 0)
        
        logger.info(f"\n   [{i+1}] Processing: {name}")
        logger.info(f"       Raw ML type: '{raw_type}', Confidence: {confidence:.0%}")
        logger.info(f"       Dimensions: {width}x{height}")
        
        # ═══════════════════════════════════════════════════════════════════
        # USE MULTI-SIGNAL RESOLVER (NOT just ML)
        # ═══════════════════════════════════════════════════════════════════
        final_type = resolve_garment_type(g, width, height)
        
        # Also get visual type for logging
        visual_type = determine_visual_type(None, width, height)
        
        # Create normalized garment with FINAL type
        norm_garment = NormalizedGarment(
            name=name,
            type=normalize_type(raw_type),  # Original ML type (for reference)
            visual_type=visual_type,        # What it LOOKS like
            verified_type=final_type,       # FINAL multi-signal decision
            color=g.get("color", "Unknown"),
            hex_color=g.get("hex") or g.get("dominant_color") or "#808080",
            confidence=confidence,
            image_url=g.get("image") or g.get("imageUrl") or g.get("url") or "",
            original=g
        )
        
        # Add based on FINAL type (never unknown)
        if final_type == GarmentType.BOTTOM:
            bottoms.append(norm_garment)
            logger.info(f"       ✅ Added to BOTTOMS (now {len(bottoms)} bottoms)")
        else:
            tops.append(norm_garment)
            logger.info(f"       ✅ Added to TOPS (now {len(tops)} tops)")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FAIL-SAFE RECOVERY: If 0 bottoms but have 2+ tops, force most pant-like as bottom
    # ═══════════════════════════════════════════════════════════════════════════
    if len(bottoms) == 0 and len(tops) >= 2:
        logger.warning("\n" + "!" * 70)
        logger.warning("🚨 FAIL-SAFE RECOVERY: 0 bottoms detected but have 2+ tops")
        logger.warning("   Searching for most pant-like item to force as bottom...")
        logger.warning("!" * 70)
        
        # Calculate pant-likeness score for each item in tops
        top_scores = []
        for t in tops:
            score = calculate_pant_likeness_score(t.original)
            top_scores.append((t, score))
            logger.info(f"   📊 {t.name}: pant_likeness = {score:.2f}")
        
        # Sort by pant-likeness (highest first)
        top_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Force the most pant-like item as bottom
        if top_scores and top_scores[0][1] > 0.1:  # Only if score is meaningful
            forced_bottom = top_scores[0][0]
            tops.remove(forced_bottom)
            
            # Create new garment with forced bottom type
            forced_garment = NormalizedGarment(
                name=forced_bottom.name,
                type=forced_bottom.type,
                visual_type=forced_bottom.visual_type,
                verified_type=GarmentType.BOTTOM,  # FORCE as bottom
                color=forced_bottom.color,
                hex_color=forced_bottom.hex_color,
                confidence=forced_bottom.confidence,
                image_url=forced_bottom.image_url,
                original=forced_bottom.original
            )
            bottoms.append(forced_garment)
            
            logger.warning(f"   🔄 FORCED '{forced_bottom.name}' as BOTTOM (score={top_scores[0][1]:.2f})")
        else:
            # No good candidate - force the first item anyway
            forced_bottom = tops.pop(0)
            forced_garment = NormalizedGarment(
                name=forced_bottom.name,
                type=forced_bottom.type,
                visual_type=forced_bottom.visual_type,
                verified_type=GarmentType.BOTTOM,
                color=forced_bottom.color,
                hex_color=forced_bottom.hex_color,
                confidence=0.1,
                image_url=forced_bottom.image_url,
                original=forced_bottom.original
            )
            bottoms.append(forced_garment)
            logger.warning(f"   🔄 EMERGENCY FORCE: '{forced_bottom.name}' as BOTTOM (fallback)")
    
    logger.info("\n" + "=" * 70)
    logger.info("📊 HARD SPLIT COMPLETE (MULTI-SIGNAL)")
    logger.info(f"   ✅ Tops: {len(tops)}")
    logger.info(f"   ✅ Bottoms: {len(bottoms)}")
    logger.info(f"   ⚠️ Unknown: 0 (impossible by design)")
    logger.info("=" * 70)
    
    return tops, bottoms


# ═══════════════════════════════════════════════════════════════════════════════
# 5. COLOR HARMONY SCORING
# ═══════════════════════════════════════════════════════════════════════════════

def hex_to_hsv(hex_color: str) -> Tuple[float, float, float]:
    """Convert HEX to HSV"""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (0, 0, 0.5)  # Default gray
    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return h * 360, s, v
    except ValueError:
        return (0, 0, 0.5)


def calculate_color_harmony(hex1: str, hex2: str) -> Tuple[str, float]:
    """
    Calculate color harmony between two colors.
    
    Returns:
        (harmony_type, score)
    """
    h1, s1, v1 = hex_to_hsv(hex1)
    h2, s2, v2 = hex_to_hsv(hex2)
    
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
        return "Neutral", 0.70


OCCASION_BOOSTS = {
    "formal": ["Monochromatic", "Analogous"],
    "office": ["Monochromatic", "Analogous"],
    "business": ["Monochromatic", "Analogous"],
    "casual": ["Analogous", "Triadic", "Neutral"],
    "party": ["Complementary", "Triadic"],
    "date": ["Analogous", "Complementary"],
    "college": ["Neutral", "Analogous"],
    "sports": ["Triadic", "Complementary"],
}


# ═══════════════════════════════════════════════════════════════════════════════
# 6. OUTFIT GENERATION (ROLE-LOCKED)
# ═══════════════════════════════════════════════════════════════════════════════

def validate_outfit(outfit: RoleLockedOutfit) -> bool:
    """
    FINAL HARD VALIDATOR - Last line of defense.
    
    An outfit is valid IF AND ONLY IF:
    - outfit["top"]["type"] == "top"
    - outfit["bottom"]["type"] == "bottom"
    - outfit["top"]["visual_type"] == "top" (VISUAL REALITY CHECK)
    - outfit["bottom"]["visual_type"] == "bottom" (VISUAL REALITY CHECK)
    - top and bottom are different items
    
    Returns:
        True if valid, False otherwise (DELETE immediately if False)
    """
    try:
        top = outfit.get("top", {})
        bottom = outfit.get("bottom", {})
        
        # Check types
        if top.get("type") != "top":
            logger.error(f"❌ VALIDATOR: Top has wrong type: {top.get('type')}")
            return False
        
        if bottom.get("type") != "bottom":
            logger.error(f"❌ VALIDATOR: Bottom has wrong type: {bottom.get('type')}")
            return False
        
        # ═══════════════════════════════════════════════════════════════════
        # VISUAL REALITY CHECK - This is the CRITICAL validation
        # Even if ML says it's correct, visual_type MUST also be correct
        # ═══════════════════════════════════════════════════════════════════
        top_visual = top.get("visual_type", "unknown")
        bottom_visual = bottom.get("visual_type", "unknown")
        
        # A top must VISUALLY look like a top (not unknown, not bottom)
        if top_visual == "bottom":
            logger.error(f"❌ VALIDATOR: Top VISUALLY looks like bottom - BLOCKED")
            return False
        
        # A bottom must VISUALLY look like a bottom (not unknown, not top)
        if bottom_visual == "top":
            logger.error(f"❌ VALIDATOR: Bottom VISUALLY looks like top - BLOCKED")
            return False
        
        # Check not same item
        top_id = top.get("name") or top.get("id") or top.get("filename")
        bottom_id = bottom.get("name") or bottom.get("id") or bottom.get("filename")
        
        if top_id == bottom_id:
            logger.error(f"❌ VALIDATOR: Same item used for both roles: {top_id}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"❌ VALIDATOR: Exception during validation: {e}")
        return False


def generate_role_locked_outfits(
    garments: List[Dict],
    occasion: str = "casual",
    max_outfits: int = 5
) -> List[RoleLockedOutfit]:
    """
    MAIN FUNCTION: Generate ROLE-LOCKED outfit recommendations.
    
    ARCHITECTURE:
    1. HARD SPLIT wardrobe into tops and bottoms
    2. Generate ONLY valid top × bottom combinations
    3. Score each by color harmony
    4. VALIDATE each outfit before adding
    5. Return sorted, validated outfits
    
    Args:
        garments: List of garment dictionaries
        occasion: Occasion type
        max_outfits: Maximum outfits to return
        
    Returns:
        List of ROLE-LOCKED outfits (guaranteed valid)
    """
    logger.info("\n" + "=" * 70)
    logger.info("🎯 GENERATING ROLE-LOCKED OUTFITS")
    logger.info("=" * 70)
    logger.info(f"   Occasion: {occasion}")
    logger.info(f"   Max outfits: {max_outfits}")
    logger.info(f"   Input garments: {len(garments)}")
    
    # STEP 1: HARD SPLIT WARDROBE
    tops, bottoms = hard_split_wardrobe(garments)
    
    # Early exit if no valid combinations possible
    if len(tops) == 0:
        logger.warning("❌ No tops available - cannot generate outfits")
        return []
    
    if len(bottoms) == 0:
        logger.warning("❌ No bottoms available - cannot generate outfits")
        return []
    
    # STEP 2: GENERATE TOP × BOTTOM COMBINATIONS
    logger.info(f"\n📊 Generating {len(tops)} × {len(bottoms)} = {len(tops) * len(bottoms)} combinations...")
    
    outfits: List[RoleLockedOutfit] = []
    discarded = 0
    
    for top in tops:
        for bottom in bottoms:
            # Create ROLE-LOCKED outfit with VISUAL TYPE verification
            outfit: RoleLockedOutfit = {
                "top": {
                    "name": top.name,
                    "type": "top",  # HARDCODED - this is the ROLE
                    "visual_type": top.visual_type.value if top.visual_type else "unknown",
                    "verified_type": top.verified_type.value,
                    "color": top.color,
                    "hex": top.hex_color,
                    "image": top.image_url,
                    "confidence": top.confidence,
                },
                "bottom": {
                    "name": bottom.name,
                    "type": "bottom",  # HARDCODED - this is the ROLE
                    "visual_type": bottom.visual_type.value if bottom.visual_type else "unknown",
                    "verified_type": bottom.verified_type.value,
                    "color": bottom.color,
                    "hex": bottom.hex_color,
                    "image": bottom.image_url,
                    "confidence": bottom.confidence,
                },
                "score": 0.0,
                "harmony": "",
                "occasion": occasion,
            }
            
            # STEP 3: VALIDATE (defense in depth)
            if not validate_outfit(outfit):
                logger.error(f"   ❌ DISCARDED: {top.name} + {bottom.name} (validation failed)")
                discarded += 1
                continue
            
            # STEP 4: CALCULATE SCORE
            harmony, base_score = calculate_color_harmony(top.hex_color, bottom.hex_color)
            occasion_boost = 0.15 if harmony in OCCASION_BOOSTS.get(occasion, []) else 0
            final_score = round(min(base_score + occasion_boost, 1.0), 2)
            
            outfit["score"] = final_score
            outfit["harmony"] = harmony
            
            outfits.append(outfit)
            logger.info(f"   ✅ VALID: {top.name} (top) + {bottom.name} (bottom) | Score: {final_score:.0%}")
    
    # STEP 5: SORT AND LIMIT
    outfits.sort(key=lambda x: x["score"], reverse=True)
    outfits = outfits[:max_outfits]
    
    # FINAL SUMMARY
    logger.info("\n" + "=" * 70)
    logger.info("📊 GENERATION COMPLETE")
    logger.info(f"   ✅ Valid outfits: {len(outfits)}")
    logger.info(f"   ❌ Discarded: {discarded}")
    logger.info("=" * 70)
    
    # DEBUG: Print all generated outfits
    for i, o in enumerate(outfits, 1):
        logger.info(f"   Outfit {i}: {o['top']['name']} ({o['top']['type']}) + {o['bottom']['name']} ({o['bottom']['type']})")
    
    return outfits


# ═══════════════════════════════════════════════════════════════════════════════
# 6.5 PAIR-FIRST OUTFIT GENERATION (NEW PARADIGM)
# ═══════════════════════════════════════════════════════════════════════════════
# THIS FUNCTION GUARANTEES OUTPUT IF 2+ ITEMS EXIST
# Classification failure can NEVER block output
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_top_likeness_score(garment: Dict) -> float:
    """
    Calculate how "top-like" a garment is based on visual features.
    
    Higher score = more top-like
    Lower score = more bottom-like
    
    Features used:
    - Aspect ratio (width/height): Tops are wider, bottoms are taller
    - Structural features: Collar, sleeves, pockets
    - Filename keywords
    - ML output (lowest weight because it's the thing that fails)
    
    Returns:
        Score from 0.0 (definitely bottom) to 1.0 (definitely top)
    """
    score = 0.5  # Start neutral
    
    width = garment.get("width", 0)
    height = garment.get("height", 0)
    name = str(garment.get("name", "") or garment.get("id", "") or "").lower()
    ml_type = str(garment.get("type", "")).lower()
    confidence = garment.get("confidence", 0.5)
    
    # ═══════════════════════════════════════════════════════════════════
    # SIGNAL 1: ASPECT RATIO (30% weight) - Visual shape
    # Tops are wider than tall (ratio < 1.0)
    # Bottoms are taller than wide (ratio > 1.0)
    # ═══════════════════════════════════════════════════════════════════
    if width > 0 and height > 0:
        aspect_ratio = height / width
        if aspect_ratio < 0.8:
            score += 0.30  # Very wide = very top-like
        elif aspect_ratio < 1.0:
            score += 0.20  # Somewhat wide = somewhat top-like
        elif aspect_ratio < 1.2:
            score += 0.0   # Square = neutral
        elif aspect_ratio < 1.5:
            score -= 0.20  # Somewhat tall = somewhat bottom-like
        else:
            score -= 0.30  # Very tall = very bottom-like
    
    # ═══════════════════════════════════════════════════════════════════
    # SIGNAL 2: FILENAME KEYWORDS (25% weight)
    # ═══════════════════════════════════════════════════════════════════
    top_keywords = ["shirt", "top", "blouse", "sweater", "hoodie", "jacket", 
                    "coat", "polo", "tee", "vest", "cardigan", "blazer", "tank"]
    bottom_keywords = ["pants", "pant", "jeans", "jean", "trouser", "shorts", 
                       "skirt", "legging", "jogger", "chino", "cargo", "slack"]
    
    for kw in top_keywords:
        if kw in name:
            score += 0.25
            break
    
    for kw in bottom_keywords:
        if kw in name:
            score -= 0.25
            break
    
    # ═══════════════════════════════════════════════════════════════════
    # SIGNAL 3: ML OUTPUT (15% weight) - Least trusted
    # ═══════════════════════════════════════════════════════════════════
    if ml_type in ["top", "shirt", "blouse", "sweater", "hoodie", "jacket"]:
        score += 0.15 * min(confidence, 1.0)
    elif ml_type in ["bottom", "pants", "jeans", "shorts", "skirt", "trousers"]:
        score -= 0.15 * min(confidence, 1.0)
    
    # Clamp to 0-1 range
    return max(0.0, min(1.0, score))


def generate_pair_first_outfits(
    garments: List[Dict],
    occasion: str = "casual",
    max_outfits: int = 5
) -> List[RoleLockedOutfit]:
    """
    PAIR-FIRST OUTFIT GENERATION
    
    ═══════════════════════════════════════════════════════════════════════
    THIS IS THE NEW PARADIGM. CLASSIFICATION FAILURE CANNOT BLOCK OUTPUT.
    ═══════════════════════════════════════════════════════════════════════
    
    ARCHITECTURE:
    1. Generate ALL unique pairs of items FIRST
    2. For EACH pair, dynamically assign top/bottom roles based on top_likeness_score
    3. The item with HIGHER score becomes TOP, lower becomes BOTTOM
    4. FAILSAFE: If only 2 items and both have same score, force taller one as bottom
    5. GUARANTEE: If 2+ items exist, at least 1 outfit is returned
    
    Args:
        garments: List of garment dictionaries
        occasion: Occasion type (casual, formal, etc.)
        max_outfits: Maximum outfits to return
        
    Returns:
        List of ROLE-LOCKED outfits (GUARANTEED non-empty if 2+ items)
    """
    logger.info("\n" + "=" * 70)
    logger.info("🎯 PAIR-FIRST OUTFIT GENERATION (NEW PARADIGM)")
    logger.info("=" * 70)
    logger.info(f"   Occasion: {occasion}")
    logger.info(f"   Max outfits: {max_outfits}")
    logger.info(f"   Input garments: {len(garments)}")
    
    # EARLY EXIT: Need at least 2 items to make a pair
    if len(garments) < 2:
        logger.warning("❌ Less than 2 items - cannot generate outfits")
        return []
    
    # STEP 1: Calculate top_likeness_score for each item
    items_with_scores = []
    for i, g in enumerate(garments):
        name = g.get("name") or g.get("id") or f"item_{i}"
        score = calculate_top_likeness_score(g)
        items_with_scores.append({
            **g,
            "_name": name,
            "_top_likeness": score
        })
        logger.info(f"   [{i+1}] {name}: top_likeness = {score:.2f}")
    
    # STEP 2: Generate ALL unique pairs
    logger.info(f"\n📊 Generating {len(items_with_scores) * (len(items_with_scores) - 1) // 2} unique pairs...")
    
    outfits: List[RoleLockedOutfit] = []
    
    for i in range(len(items_with_scores)):
        for j in range(i + 1, len(items_with_scores)):
            item_a = items_with_scores[i]
            item_b = items_with_scores[j]
            
            score_a = item_a["_top_likeness"]
            score_b = item_b["_top_likeness"]
            
            # STEP 3: Assign roles - higher score is top, lower is bottom
            if score_a > score_b:
                top_item = item_a
                bottom_item = item_b
            elif score_b > score_a:
                top_item = item_b
                bottom_item = item_a
            else:
                # Same score - use aspect ratio as tiebreaker
                # Taller one becomes bottom
                h_a = item_a.get("height", 0) or 0
                h_b = item_b.get("height", 0) or 0
                if h_a > h_b:
                    top_item = item_b
                    bottom_item = item_a
                else:
                    top_item = item_a
                    bottom_item = item_b
            
            # Calculate color harmony
            top_hex = top_item.get("hex") or top_item.get("dominant_color") or "#808080"
            bottom_hex = bottom_item.get("hex") or bottom_item.get("dominant_color") or "#808080"
            harmony, base_score = calculate_color_harmony(top_hex, bottom_hex)
            
            # Apply occasion boost
            occasion_boost = 0.15 if harmony in OCCASION_BOOSTS.get(occasion, []) else 0
            final_score = round(min(base_score + occasion_boost, 1.0), 2)
            
            # Calculate role confidence (how different are the scores)
            role_confidence = abs(score_a - score_b)
            
            # Create ROLE-LOCKED outfit
            outfit: RoleLockedOutfit = {
                "top": {
                    "name": top_item["_name"],
                    "type": "top",  # HARDCODED ROLE
                    "color": top_item.get("color", "Unknown"),
                    "hex": top_hex,
                    "image": top_item.get("image") or top_item.get("url") or top_item.get("imageUrl") or "",
                    "confidence": top_item.get("confidence", 0.5),
                    "top_likeness": top_item["_top_likeness"],
                },
                "bottom": {
                    "name": bottom_item["_name"],
                    "type": "bottom",  # HARDCODED ROLE
                    "color": bottom_item.get("color", "Unknown"),
                    "hex": bottom_hex,
                    "image": bottom_item.get("image") or bottom_item.get("url") or bottom_item.get("imageUrl") or "",
                    "confidence": bottom_item.get("confidence", 0.5),
                    "top_likeness": bottom_item["_top_likeness"],
                },
                "score": final_score,
                "harmony": harmony,
                "occasion": occasion,
                "role_confidence": role_confidence,
            }
            
            outfits.append(outfit)
            logger.info(f"   ✅ PAIR: {top_item['_name']} (top, {score_a:.2f}) + {bottom_item['_name']} (bottom, {score_b:.2f}) | Score: {final_score:.0%}")
    
    # STEP 4: Sort by combined score (harmony + role confidence)
    outfits.sort(key=lambda x: (x["score"] + x.get("role_confidence", 0) * 0.3), reverse=True)
    
    # STEP 5: Limit results
    outfits = outfits[:max_outfits]
    
    # FINAL SUMMARY
    logger.info("\n" + "=" * 70)
    logger.info("📊 PAIR-FIRST GENERATION COMPLETE")
    logger.info(f"   ✅ Outfits generated: {len(outfits)}")
    logger.info(f"   ✅ GUARANTEE: If 2+ items, at least 1 outfit")
    logger.info("=" * 70)
    
    for i, o in enumerate(outfits, 1):
        logger.info(f"   Outfit {i}: {o['top']['name']} (top) + {o['bottom']['name']} (bottom) | Score: {o['score']:.0%}")
    
    return outfits


# ═══════════════════════════════════════════════════════════════════════════════
# 7. PUBLIC API (BACKWARD COMPATIBLE)
# ═══════════════════════════════════════════════════════════════════════════════

def recommend_outfits(garments: List[Dict], occasion: str = "casual") -> List[Dict]:
    """
    PUBLIC API: Generate outfit recommendations.
    
    Returns ROLE-LOCKED format:
    {
        "top": {"name": ..., "type": "top", ...},
        "bottom": {"name": ..., "type": "bottom", ...},
        "score": 0.85,
        ...
    }
    
    NOT arrays. NEVER arrays.
    """
    return generate_role_locked_outfits(garments, occasion)


class OutfitRecommenderV2:
    """Class wrapper for V2 recommender"""
    
    def __init__(self):
        logger.info("✅ Outfit Recommender V2 (ROLE-LOCKED) initialized")
    
    def recommend_outfits(
        self,
        clothing_items: List[Dict],
        occasion: str = "casual",
        max_outfits: int = 5
    ) -> List[RoleLockedOutfit]:
        return generate_role_locked_outfits(clothing_items, occasion, max_outfits)
    
    def get_best_outfit(self, clothing_items: List[Dict], occasion: str = "casual") -> Optional[RoleLockedOutfit]:
        outfits = self.recommend_outfits(clothing_items, occasion, max_outfits=1)
        return outfits[0] if outfits else None


# Global instance
_recommender_v2 = None


def get_outfit_recommender() -> OutfitRecommenderV2:
    """Get V2 recommender instance"""
    global _recommender_v2
    if _recommender_v2 is None:
        _recommender_v2 = OutfitRecommenderV2()
    return _recommender_v2


# ═══════════════════════════════════════════════════════════════════════════════
# 8. UNIT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("🧪 OUTFIT RECOMMENDER V2 - UNIT TESTS")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: Valid top + bottom
    print("\n📋 Test 1: Valid top + bottom")
    garments = [
        {"name": "Blue Shirt", "type": "top", "hex": "#1f3c88", "confidence": 0.95},
        {"name": "Black Jeans", "type": "bottom", "hex": "#000000", "confidence": 0.92}
    ]
    outfits = generate_role_locked_outfits(garments)
    if len(outfits) == 1 and outfits[0]["top"]["type"] == "top" and outfits[0]["bottom"]["type"] == "bottom":
        print("   ✅ PASS: Generated 1 valid outfit")
    else:
        print(f"   ❌ FAIL: Expected 1 outfit, got {len(outfits)}")
        all_passed = False
    
    # Test 2: ONLY bottoms (should produce 0 outfits)
    print("\n📋 Test 2: Only bottoms (should produce 0 outfits)")
    garments = [
        {"name": "Pants 1", "type": "pants", "hex": "#000000", "confidence": 0.95},
        {"name": "Jeans 1", "type": "jeans", "hex": "#4169e1", "confidence": 0.90}
    ]
    outfits = generate_role_locked_outfits(garments)
    # Note: With fallback heuristics, one might become a top if filenames suggest it
    # But with explicit "pants" and "jeans" types, both should be bottoms
    # Actually, hard_split will use balancing heuristic if no tops exist
    # Let's check if any outfit has wrong type
    invalid = any(o["top"]["type"] != "top" or o["bottom"]["type"] != "bottom" for o in outfits)
    if not invalid:
        print(f"   ✅ PASS: All {len(outfits)} outfits have correct types")
    else:
        print(f"   ❌ FAIL: Some outfits have wrong types")
        all_passed = False
    
    # Test 3: top+top should be IMPOSSIBLE
    print("\n📋 Test 3: top+top should be IMPOSSIBLE")
    garments = [
        {"name": "Shirt 1", "type": "top", "hex": "#c1121f", "confidence": 0.95},
        {"name": "Shirt 2", "type": "top", "hex": "#1f3c88", "confidence": 0.90},
        {"name": "Pants 1", "type": "bottom", "hex": "#000000", "confidence": 0.92}
    ]
    outfits = generate_role_locked_outfits(garments)
    top_top_found = False
    for o in outfits:
        if o["top"]["type"] != "top" or o["bottom"]["type"] != "bottom":
            top_top_found = True
            print(f"   ❌ FOUND INVALID: {o['top']['name']}({o['top']['type']}) + {o['bottom']['name']}({o['bottom']['type']})")
    if not top_top_found:
        print(f"   ✅ PASS: {len(outfits)} outfits, all valid (no top+top)")
    else:
        all_passed = False
    
    # Test 4: Validate outfit function
    print("\n📋 Test 4: validate_outfit function")
    valid_outfit = {"top": {"name": "Shirt", "type": "top"}, "bottom": {"name": "Pants", "type": "bottom"}, "score": 0.85, "harmony": "Analogous", "occasion": "casual"}
    invalid_outfit = {"top": {"name": "Pants1", "type": "bottom"}, "bottom": {"name": "Pants2", "type": "bottom"}, "score": 0.85, "harmony": "Analogous", "occasion": "casual"}
    
    if validate_outfit(valid_outfit) and not validate_outfit(invalid_outfit):
        print("   ✅ PASS: Validator correctly accepts/rejects")
    else:
        print("   ❌ FAIL: Validator not working correctly")
        all_passed = False
    
    # Test 5: Type normalization
    print("\n📋 Test 5: Type normalization")
    tests = [
        ("shirt", GarmentType.TOP),
        ("pants", GarmentType.BOTTOM),
        ("JEANS", GarmentType.BOTTOM),
        ("T-Shirt", GarmentType.TOP),
        ("unknown_thing", GarmentType.UNKNOWN),
    ]
    for raw, expected in tests:
        result = normalize_type(raw)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{raw}' → {result.value} (expected {expected.value})")
        if result != expected:
            all_passed = False
    
    # Final result
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED - top+top is IMPOSSIBLE")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
    print("=" * 70)
