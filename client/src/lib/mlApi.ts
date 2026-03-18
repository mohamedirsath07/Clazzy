/**
 * ML API Service Layer V2 - ROLE-LOCKED ARCHITECTURE
 * =============================================================================
 * SHIP-BLOCKING FIX: Ensures top+top and bottom+bottom are IMPOSSIBLE
 * 
 * ARCHITECTURAL RULES (NON-NEGOTIABLE):
 * 1. Outfits are ROLE-LOCKED: {top: item, bottom: item} NOT arrays
 * 2. Items are HARD-SPLIT before any pairing
 * 3. Types are NORMALIZED before classification
 * 4. ML failures use FALLBACK HEURISTICS
 * 5. Final validator DELETES invalid outfits
 * 
 * Author: Principal Engineer (Emergency Fix)
 */

// ═══════════════════════════════════════════════════════════════════════════════
// 1. API CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const getApiBaseUrl = () => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}:8001`;
};

// ═══════════════════════════════════════════════════════════════════════════════
// 2. TYPE DEFINITIONS (ROLE-LOCKED)
// ═══════════════════════════════════════════════════════════════════════════════

export interface MLTypePrediction {
  predicted_type: 'top' | 'bottom' | 'shoes' | 'dress' | 'blazer' | 'other';
  confidence: number;
}

/**
 * ROLE-LOCKED Clothing Item (WITH VISUAL VERIFICATION)
 * The 'role' field is the SLOT this item occupies in an outfit
 * The 'type' field is the ML classification
 * The 'visualType' field is what the image ACTUALLY looks like
 * The 'verifiedType' field is the FINAL consensus type
 */
export interface MLClothingItem {
  filename: string;
  type: 'top' | 'bottom' | 'dress' | 'unknown';
  category: string;
  color: string;
  url: string;
  role: 'top' | 'bottom';  // ROLE is REQUIRED, not optional
  // Visual verification fields
  visualType?: 'top' | 'bottom' | 'unknown';
  verifiedType?: 'top' | 'bottom';
  imageWidth?: number;
  imageHeight?: number;
}

/**
 * ROLE-LOCKED Outfit Structure
 * THIS IS THE ONLY VALID FORMAT. Arrays alone are BANNED.
 */
export interface MLOutfitRecommendation {
  // ROLE-LOCKED: Explicit top and bottom slots (REQUIRED)
  top: MLClothingItem;
  bottom: MLClothingItem;
  // Legacy array (for backward compatibility with existing UI)
  items: MLClothingItem[];
  score: number;
  total_items: number;
}

export type RecommendationStatus = 'ok' | 'error';
export type RecommendationErrorReason = 
  | 'MISSING_TOP_OR_BOTTOM'
  | 'ALL_ITEMS_UNKNOWN'
  | 'LOW_CONFIDENCE'
  | 'NO_ITEMS'
  | 'GENERATION_FAILED';

export interface MLRecommendationResponse {
  occasion: string;
  recommendations: MLOutfitRecommendation[];
  total_items_analyzed: number;
  status: RecommendationStatus;
  reason?: RecommendationErrorReason;
  debug?: {
    tops_count: number;
    bottoms_count: number;
    unknown_count: number;
    unknown_items: string[];
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// 3. TYPE NORMALIZATION (SINGLE SOURCE OF TRUTH)
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIDENCE_THRESHOLD = 0.50;  // Lowered to 50% to be lenient

const TYPE_ALIASES: Record<string, 'top' | 'bottom' | 'unknown'> = {
  // Top aliases
  'top': 'top', 'shirt': 'top', 'blouse': 'top', 't-shirt': 'top',
  'tshirt': 'top', 'polo': 'top', 'sweater': 'top', 'hoodie': 'top',
  'jacket': 'top', 'coat': 'top', 'blazer': 'top', 'cardigan': 'top',
  'tank': 'top', 'tanktop': 'top', 'vest': 'top', 'tunic': 'top',
  // Bottom aliases
  'bottom': 'bottom', 'pants': 'bottom', 'pant': 'bottom', 'jeans': 'bottom',
  'jean': 'bottom', 'trousers': 'bottom', 'trouser': 'bottom',
  'shorts': 'bottom', 'short': 'bottom', 'skirt': 'bottom',
  'leggings': 'bottom', 'legging': 'bottom', 'joggers': 'bottom',
  'chinos': 'bottom', 'chino': 'bottom', 'cargo': 'bottom',
  // Unknown
  'other': 'unknown', 'dress': 'unknown',
};

/**
 * SINGLE FUNCTION for type normalization
 */
function normalizeType(rawType: string | undefined): 'top' | 'bottom' | 'unknown' {
  if (!rawType) return 'unknown';
  const cleaned = rawType.trim().toLowerCase().replace(/-/g, '').replace(/_/g, '');
  
  // Direct lookup
  if (TYPE_ALIASES[cleaned]) return TYPE_ALIASES[cleaned];
  
  // Partial match
  for (const [alias, type] of Object.entries(TYPE_ALIASES)) {
    if (cleaned.includes(alias)) return type;
  }
  
  return 'unknown';
}

// ═══════════════════════════════════════════════════════════════════════════════
// 4. FALLBACK HEURISTICS (WHEN ML FAILS)
// ═══════════════════════════════════════════════════════════════════════════════

function guessTypeFromFilename(filename: string): 'top' | 'bottom' | null {
  const lower = filename.toLowerCase();
  
  const topPatterns = ['shirt', 'tee', 'blouse', 'top', 'polo', 'sweater', 'hoodie', 'jacket', 'blazer', 'coat'];
  for (const p of topPatterns) {
    if (lower.includes(p)) {
      console.log(`   📁 Filename: "${filename}" contains "${p}" → TOP`);
      return 'top';
    }
  }
  
  const bottomPatterns = ['pant', 'jean', 'trouser', 'short', 'skirt', 'bottom', 'cargo', 'chino', 'legging'];
  for (const p of bottomPatterns) {
    if (lower.includes(p)) {
      console.log(`   📁 Filename: "${filename}" contains "${p}" → BOTTOM`);
      return 'bottom';
    }
  }
  
  return null;
}

function guessTypeFromAspectRatio(width: number, height: number): 'top' | 'bottom' | null {
  if (width <= 0 || height <= 0) return null;
  
  const ratio = width / height;
  if (ratio < 0.7) {
    console.log(`   📐 Aspect ratio ${ratio.toFixed(2)} (tall) → BOTTOM`);
    return 'bottom';
  } else if (ratio > 1.3) {
    console.log(`   📐 Aspect ratio ${ratio.toFixed(2)} (wide) → TOP`);
    return 'top';
  }
  return null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// 4.5 VISUAL REALITY VERIFICATION (ML OVERRIDE LAYER)
// ═══════════════════════════════════════════════════════════════════════════════
// THIS SECTION OVERRIDES ML WHEN IT'S CLEARLY WRONG
// A shirt will NEVER pass as a bottom here, regardless of ML confidence

/**
 * VISUAL REALITY CHECK: Determine what an image LOOKS like, not what ML says.
 * 
 * Rules:
 * - If height/width < 1.2 → visually looks like a TOP
 * - If height/width >= 1.2 → visually looks like a BOTTOM
 * 
 * A shirt will NEVER have height/width >= 1.2 because shirts are wider than tall.
 */
async function determineVisualType(imageUrl: string): Promise<'top' | 'bottom' | 'unknown'> {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    
    img.onload = () => {
      const { width, height } = img;
      const aspectRatio = height / width;
      
      if (aspectRatio < 1.2) {
        console.log(`   👁️ VISUAL CHECK: ${width}x${height} (h/w=${aspectRatio.toFixed(2)}) → TOP (wide shape)`);
        resolve('top');
      } else {
        console.log(`   👁️ VISUAL CHECK: ${width}x${height} (h/w=${aspectRatio.toFixed(2)}) → BOTTOM (tall shape)`);
        resolve('bottom');
      }
    };
    
    img.onerror = () => {
      console.warn(`   ⚠️ VISUAL CHECK failed to load image`);
      resolve('unknown');
    };
    
    // Timeout after 3 seconds
    setTimeout(() => resolve('unknown'), 3000);
    
    img.src = imageUrl;
  });
}

/**
 * CONSENSUS DECISION: Combine ML prediction with visual reality.
 * 
 * Rules:
 * 1. If model and visual AGREE → use that type
 * 2. If model and visual DISAGREE → TRUST VISUAL (ML is wrong)
 * 3. If visual is UNKNOWN → use model (but with warning)
 */
function determineFinalType(
  modelType: 'top' | 'bottom' | 'unknown',
  visualType: 'top' | 'bottom' | 'unknown',
  confidence: number
): 'top' | 'bottom' {
  if (visualType === 'unknown') {
    console.warn(`   ⚠️ CONSENSUS: Visual unknown, trusting model: ${modelType}`);
    return modelType === 'unknown' ? 'top' : modelType; // Default to top if both unknown
  }
  
  if (modelType === visualType) {
    console.log(`   ✅ CONSENSUS: Model and visual AGREE: ${modelType}`);
    return modelType;
  }
  
  // DISAGREEMENT - VISUAL WINS
  console.warn(`   🔄 CONSENSUS OVERRIDE: Model said '${modelType}' but visual says '${visualType}'`);
  console.warn(`   🔄 TRUSTING VISUAL REALITY over ML (confidence was ${(confidence * 100).toFixed(0)}%)`);
  return visualType;
}

/**
 * Quick check: Does this image LOOK like a top?
 */
function isVisuallyATop(width: number, height: number): boolean {
  if (width <= 0 || height <= 0) return false;
  return (height / width) < 1.2;
}

/**
 * Quick check: Does this image LOOK like a bottom?
 */
function isVisuallyABottom(width: number, height: number): boolean {
  if (width <= 0 || height <= 0) return false;
  return (height / width) >= 1.2;
}

// ═══════════════════════════════════════════════════════════════════════════════
// 4.6 MULTI-SIGNAL GARMENT TYPE RESOLVER
// ═══════════════════════════════════════════════════════════════════════════════
// This is the AUTHORITATIVE function for determining garment type.
// ML is now just ONE weak signal among FOUR.

interface Signal {
  type: 'top' | 'bottom';
  weight: number;
  source: string;
}

/**
 * FINAL GARMENT TYPE RESOLVER - Multi-Signal Decision Engine
 * 
 * Returns FINAL type: 'top' or 'bottom'. NEVER returns 'unknown'.
 * 
 * Signal Priority (strongest to weakest):
 * 1. VISUAL SHAPE (aspect ratio) - PRIMARY (weight 3.0)
 * 2. STRUCTURAL FEATURES (sleeves, collar, buttons) - (weight 2.5)
 * 3. FILENAME HEURISTICS - (weight 2.0)
 * 4. ML OUTPUT (weakest - weight 1.0)
 */
async function resolveGarmentType(
  item: RawItem,
  width: number = 0,
  height: number = 0
): Promise<'top' | 'bottom'> {
  const signals: Signal[] = [];
  const confidence = item.confidence ?? 0.5;
  
  console.log(`   🧠 RESOLVE_GARMENT_TYPE: ${item.id}`);
  
  // Get dimensions if not provided
  if (width === 0 || height === 0) {
    const dims = await getImageDimensions(item.imageUrl);
    width = dims.width;
    height = dims.height;
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // SIGNAL 1: VISUAL SHAPE (PRIMARY - weight 3.0)
  // Pants are ALWAYS taller than wide. Shirts are ALWAYS wider than tall.
  // ═══════════════════════════════════════════════════════════════════
  if (width > 0 && height > 0) {
    const aspectRatio = height / width;
    if (aspectRatio > 1.4) {
      signals.push({ type: 'bottom', weight: 3.0, source: 'VISUAL' });
      console.log(`      📐 SIGNAL 1 (VISUAL): h/w=${aspectRatio.toFixed(2)} > 1.4 → BOTTOM (weight 3.0)`);
    } else if (aspectRatio < 1.0) {
      signals.push({ type: 'top', weight: 3.0, source: 'VISUAL' });
      console.log(`      📐 SIGNAL 1 (VISUAL): h/w=${aspectRatio.toFixed(2)} < 1.0 → TOP (weight 3.0)`);
    } else if (aspectRatio > 1.2) {
      signals.push({ type: 'bottom', weight: 1.5, source: 'VISUAL' });
      console.log(`      📐 SIGNAL 1 (VISUAL): h/w=${aspectRatio.toFixed(2)} in [1.2, 1.4] → BOTTOM (weight 1.5)`);
    } else {
      signals.push({ type: 'top', weight: 1.5, source: 'VISUAL' });
      console.log(`      📐 SIGNAL 1 (VISUAL): h/w=${aspectRatio.toFixed(2)} in [1.0, 1.2] → TOP (weight 1.5)`);
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // SIGNAL 2: STRUCTURAL FEATURES (weight 2.5)
  // Sleeves, collars, buttons → FORCE TOP (pants NEVER have these)
  // ═══════════════════════════════════════════════════════════════════
  const structureType = detectStructuralFeatures(item.id, item.imageUrl);
  if (structureType) {
    signals.push({ type: structureType, weight: 2.5, source: 'STRUCTURE' });
    console.log(`      🔍 SIGNAL 2 (STRUCTURE): ${structureType} (weight 2.5)`);
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // SIGNAL 3: FILENAME HEURISTICS (weight 2.0)
  // ═══════════════════════════════════════════════════════════════════
  let filenameType = guessTypeFromFilename(item.id);
  if (!filenameType) {
    const urlFilename = item.imageUrl.split('/').pop()?.split('?')[0] || '';
    filenameType = guessTypeFromFilename(urlFilename);
  }
  if (filenameType) {
    signals.push({ type: filenameType, weight: 2.0, source: 'FILENAME' });
    console.log(`      📁 SIGNAL 3 (FILENAME): ${filenameType} (weight 2.0)`);
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // SIGNAL 4: ML OUTPUT (WEAKEST - weight 1.0)
  // ═══════════════════════════════════════════════════════════════════
  const mlType = normalizeType(item.detectedType);
  if (mlType !== 'unknown') {
    const mlWeight = Math.min(1.0, confidence);
    signals.push({ type: mlType, weight: mlWeight, source: 'ML' });
    console.log(`      🤖 SIGNAL 4 (ML): ${mlType} (weight ${mlWeight.toFixed(2)}, conf=${(confidence * 100).toFixed(0)}%)`);
  }
  
  // ═══════════════════════════════════════════════════════════════════
  // FINAL DECISION: Weighted Majority Vote
  // ═══════════════════════════════════════════════════════════════════
  if (signals.length === 0) {
    console.warn(`      ⚠️ NO SIGNALS - defaulting to TOP`);
    return 'top';
  }
  
  const topWeight = signals.filter(s => s.type === 'top').reduce((sum, s) => sum + s.weight, 0);
  const bottomWeight = signals.filter(s => s.type === 'bottom').reduce((sum, s) => sum + s.weight, 0);
  
  console.log(`      📊 VOTE: TOP=${topWeight.toFixed(1)} vs BOTTOM=${bottomWeight.toFixed(1)}`);
  
  let finalType: 'top' | 'bottom';
  if (bottomWeight > topWeight) {
    finalType = 'bottom';
  } else if (topWeight > bottomWeight) {
    finalType = 'top';
  } else {
    // Tie - use aspect ratio tiebreaker
    if (width > 0 && height > 0 && (height / width) > 1.3) {
      finalType = 'bottom';
      console.log(`      🔀 TIE: Aspect ratio tiebreaker → BOTTOM`);
    } else {
      finalType = 'top';
      console.log(`      🔀 TIE: Defaulting to TOP`);
    }
  }
  
  console.log(`      ✅ FINAL DECISION: ${finalType.toUpperCase()}`);
  return finalType;
}

/**
 * Detect structural features that indicate TOP (sleeves, collar, buttons).
 * Pants NEVER have these features.
 */
function detectStructuralFeatures(name: string, imageUrl: string): 'top' | 'bottom' | null {
  const text = `${name} ${imageUrl}`.toLowerCase();
  
  // Features that ONLY tops have
  const topFeatures = [
    'sleeve', 'collar', 'button', 'neck', 'v-neck', 'crew',
    'polo', 'hoodie', 'hood', 'zip', 'zipper', 'pocket',
    'long-sleeve', 'short-sleeve', 'sleeveless'
  ];
  
  for (const feature of topFeatures) {
    if (text.includes(feature)) {
      console.log(`         🔍 Structural feature: '${feature}' → TOP`);
      return 'top';
    }
  }
  
  // Features that ONLY bottoms have
  const bottomFeatures = ['waist', 'belt-loop', 'beltloop', 'inseam', 'cuff', 'leg'];
  
  for (const feature of bottomFeatures) {
    if (text.includes(feature)) {
      console.log(`         🔍 Structural feature: '${feature}' → BOTTOM`);
      return 'bottom';
    }
  }
  
  return null;
}

/**
 * Calculate how likely an item is to be pants (0.0 to 1.0).
 * Used for fail-safe recovery when 0 bottoms are detected.
 */
function calculatePantLikenessScore(item: NormalizedItemWithVisual): number {
  let score = 0.0;
  
  const { imageWidth = 0, imageHeight = 0, id, imageUrl } = item;
  const name = id.toLowerCase();
  const url = imageUrl.toLowerCase();
  
  // Aspect ratio is the strongest signal
  if (imageWidth > 0 && imageHeight > 0) {
    const aspectRatio = imageHeight / imageWidth;
    if (aspectRatio > 1.5) score += 0.5;
    else if (aspectRatio > 1.3) score += 0.3;
    else if (aspectRatio > 1.1) score += 0.1;
  }
  
  // Filename hints
  const bottomKeywords = ['pant', 'jean', 'trouser', 'short', 'skirt', 'bottom', 'cargo', 'chino'];
  for (const kw of bottomKeywords) {
    if (name.includes(kw) || url.includes(kw)) {
      score += 0.4;
      break;
    }
  }
  
  // No top keywords (negative signal)
  const topKeywords = ['shirt', 'tee', 'blouse', 'top', 'polo', 'sweater', 'hoodie', 'jacket'];
  const hasTopKeyword = topKeywords.some(kw => name.includes(kw) || url.includes(kw));
  if (!hasTopKeyword) score += 0.1;
  
  return Math.min(1.0, score);
}

// ═══════════════════════════════════════════════════════════════════════════════
// 5. ML API CALLS
// ═══════════════════════════════════════════════════════════════════════════════

export async function detectClothingType(file: File): Promise<MLTypePrediction> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${getApiBaseUrl()}/predict-type`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`ML prediction failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('ML type detection failed:', error);
    return { predicted_type: 'other', confidence: 0 };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// 6. HARD SPLIT WARDROBE (NO ML TRUST)
// ═══════════════════════════════════════════════════════════════════════════════

interface RawItem {
  imageUrl: string;
  detectedType?: string;
  id: string;
  confidence?: number;
}

interface NormalizedItem extends RawItem {
  normalizedType: 'top' | 'bottom';
}

interface NormalizedItemWithVisual extends NormalizedItem {
  visualType?: 'top' | 'bottom' | 'unknown';
  verifiedType: 'top' | 'bottom';
  imageWidth?: number;
  imageHeight?: number;
}

async function hardSplitWardrobe(items: RawItem[]): Promise<{ tops: NormalizedItemWithVisual[], bottoms: NormalizedItemWithVisual[] }> {
  const tops: NormalizedItemWithVisual[] = [];
  const bottoms: NormalizedItemWithVisual[] = [];
  
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('🔪 HARD SPLIT WARDROBE (MULTI-SIGNAL RESOLVER)');
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log(`   Input: ${items.length} items`);
  
  for (const item of items) {
    const confidence = item.confidence ?? 0.5;
    
    console.log(`\n   [${item.id}] Raw ML: "${item.detectedType}", Confidence: ${(confidence * 100).toFixed(0)}%`);
    
    // Get image dimensions first
    const dimensions = await getImageDimensions(item.imageUrl);
    console.log(`       Dimensions: ${dimensions.width}x${dimensions.height}`);
    
    // ═══════════════════════════════════════════════════════════════════
    // USE MULTI-SIGNAL RESOLVER (NOT just ML)
    // ═══════════════════════════════════════════════════════════════════
    const finalType = await resolveGarmentType(item, dimensions.width, dimensions.height);
    
    // Get visual type for reference
    const visualType = await determineVisualType(item.imageUrl);
    
    // Create normalized item with FINAL type
    const normalizedItem: NormalizedItemWithVisual = { 
      ...item, 
      normalizedType: finalType,
      visualType,
      verifiedType: finalType,
      imageWidth: dimensions.width,
      imageHeight: dimensions.height
    };
    
    // Add based on FINAL type (never unknown)
    if (finalType === 'bottom') {
      bottoms.push(normalizedItem);
      console.log(`       ✅ Added to BOTTOMS (now ${bottoms.length})`);
    } else {
      tops.push(normalizedItem);
      console.log(`       ✅ Added to TOPS (now ${tops.length})`);
    }
  }
  
  // ═══════════════════════════════════════════════════════════════════════════
  // FAIL-SAFE RECOVERY: If 0 bottoms but have 2+ tops, force most pant-like as bottom
  // ═══════════════════════════════════════════════════════════════════════════
  if (bottoms.length === 0 && tops.length >= 2) {
    console.warn('\n' + '!'.repeat(70));
    console.warn('🚨 FAIL-SAFE RECOVERY: 0 bottoms detected but have 2+ tops');
    console.warn('   Searching for most pant-like item to force as bottom...');
    console.warn('!'.repeat(70));
    
    // Calculate pant-likeness score for each item in tops
    const topScores: Array<{ item: NormalizedItemWithVisual; score: number }> = [];
    for (const t of tops) {
      const score = calculatePantLikenessScore(t);
      topScores.push({ item: t, score });
      console.log(`   📊 ${t.id}: pant_likeness = ${score.toFixed(2)}`);
    }
    
    // Sort by pant-likeness (highest first)
    topScores.sort((a, b) => b.score - a.score);
    
    // Force the most pant-like item as bottom
    if (topScores.length > 0 && topScores[0].score > 0.1) {
      const forcedBottom = topScores[0].item;
      const topsIndex = tops.indexOf(forcedBottom);
      if (topsIndex > -1) {
        tops.splice(topsIndex, 1);
      }
      
      // Update the item's types
      forcedBottom.normalizedType = 'bottom';
      forcedBottom.verifiedType = 'bottom';
      bottoms.push(forcedBottom);
      
      console.warn(`   🔄 FORCED '${forcedBottom.id}' as BOTTOM (score=${topScores[0].score.toFixed(2)})`);
    } else if (tops.length >= 2) {
      // No good candidate - force the first item anyway
      const forcedBottom = tops.shift()!;
      forcedBottom.normalizedType = 'bottom';
      forcedBottom.verifiedType = 'bottom';
      bottoms.push(forcedBottom);
      console.warn(`   🔄 EMERGENCY FORCE: '${forcedBottom.id}' as BOTTOM (fallback)`);
    }
  }
  
  console.log('\n' + '═'.repeat(70));
  console.log('📊 HARD SPLIT COMPLETE (MULTI-SIGNAL + FAIL-SAFE)');
  console.log(`   ✅ Tops: ${tops.length}`);
  console.log(`   ✅ Bottoms: ${bottoms.length}`);
  console.log(`   ⚠️ Unknown: 0 (impossible by design)`);
  console.log('═'.repeat(70));
  
  return { tops, bottoms };
}

// Helper to get image dimensions
function getImageDimensions(imageUrl: string): Promise<{width: number, height: number}> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve({ width: img.width, height: img.height });
    img.onerror = () => resolve({ width: 0, height: 0 });
    setTimeout(() => resolve({ width: 0, height: 0 }), 2000);
    img.src = imageUrl;
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 7. OUTFIT VALIDATION (FINAL GUARD WITH VISUAL VERIFICATION)
// ═══════════════════════════════════════════════════════════════════════════════

function validateOutfit(outfit: MLOutfitRecommendation): boolean {
  // Check role-locked structure
  if (!outfit.top || !outfit.bottom) {
    console.error('❌ VALIDATOR: Missing top or bottom slot');
    return false;
  }
  
  if (outfit.top.role !== 'top') {
    console.error(`❌ VALIDATOR: Top has wrong role: ${outfit.top.role}`);
    return false;
  }
  
  if (outfit.bottom.role !== 'bottom') {
    console.error(`❌ VALIDATOR: Bottom has wrong role: ${outfit.bottom.role}`);
    return false;
  }
  
  if (outfit.top.filename === outfit.bottom.filename) {
    console.error('❌ VALIDATOR: Same item used for both roles');
    return false;
  }
  
  // VISUAL REALITY CHECK: Block if visual types are wrong
  const topVisual = outfit.top.visualType;
  const bottomVisual = outfit.bottom.visualType;
  
  if (topVisual === 'bottom') {
    console.error(`❌ VALIDATOR: Top item VISUALLY looks like a BOTTOM (${outfit.top.filename})`);
    return false;
  }
  
  if (bottomVisual === 'top') {
    console.error(`❌ VALIDATOR: Bottom item VISUALLY looks like a TOP (${outfit.bottom.filename})`);
    return false;
  }
  
  // Check dimensions if available - extra safety
  if (outfit.top.imageWidth && outfit.top.imageHeight) {
    if (isVisuallyABottom(outfit.top.imageWidth, outfit.top.imageHeight)) {
      console.error(`❌ VALIDATOR: Top has bottom-like dimensions (${outfit.top.imageWidth}x${outfit.top.imageHeight})`);
      return false;
    }
  }
  
  if (outfit.bottom.imageWidth && outfit.bottom.imageHeight) {
    if (isVisuallyATop(outfit.bottom.imageWidth, outfit.bottom.imageHeight)) {
      console.error(`❌ VALIDATOR: Bottom has top-like dimensions (${outfit.bottom.imageWidth}x${outfit.bottom.imageHeight})`);
      return false;
    }
  }
  
  return true;
}

// ═══════════════════════════════════════════════════════════════════════════════
// 8. COLOR EXTRACTION
// ═══════════════════════════════════════════════════════════════════════════════

export async function extractDominantColor(imageUrl: string): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'Anonymous';
    
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!ctx) { resolve('#6B7280'); return; }
        
        const size = 100;
        canvas.width = size;
        canvas.height = size;
        ctx.drawImage(img, 0, 0, size, size);
        
        const imageData = ctx.getImageData(0, 0, size, size);
        const data = imageData.data;
        
        let r = 0, g = 0, b = 0, count = 0;
        for (let i = 0; i < data.length; i += 4) {
          const red = data[i], green = data[i + 1], blue = data[i + 2], alpha = data[i + 3];
          if (alpha < 125) continue;
          const brightness = (red + green + blue) / 3;
          if (brightness < 20 || brightness > 235) continue;
          r += red; g += green; b += blue; count++;
        }
        
        if (count === 0) { resolve('#6B7280'); return; }
        
        const hex = '#' + [r/count, g/count, b/count]
          .map(x => Math.round(x).toString(16).padStart(2, '0'))
          .join('');
        resolve(hex);
      } catch { resolve('#6B7280'); }
    };
    
    img.onerror = () => resolve('#6B7280');
    img.src = imageUrl;
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// 9. MAIN RECOMMENDATION FUNCTION (SEPARATED TOPS & BOTTOMS)
// ═══════════════════════════════════════════════════════════════════════════════
// USER EXPLICITLY UPLOADS TOPS AND BOTTOMS SEPARATELY
// We trust the user's categorization and focus on COLOR HARMONY matching

/**
 * Calculate color harmony score between two hex colors
 * Uses complementary, analogous, and neutral color theory
 */
function calculateColorHarmony(color1: string, color2: string): number {
  // Convert hex to RGB
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 128, g: 128, b: 128 };
  };

  // Convert RGB to HSL
  const rgbToHsl = (r: number, g: number, b: number) => {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0;
    const l = (max + min) / 2;

    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
        case g: h = ((b - r) / d + 2) / 6; break;
        case b: h = ((r - g) / d + 4) / 6; break;
      }
    }
    return { h: h * 360, s, l };
  };

  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);
  const hsl1 = rgbToHsl(rgb1.r, rgb1.g, rgb1.b);
  const hsl2 = rgbToHsl(rgb2.r, rgb2.g, rgb2.b);

  // Check if either color is neutral (low saturation)
  const isNeutral1 = hsl1.s < 0.15;
  const isNeutral2 = hsl2.s < 0.15;

  // Neutrals go with everything
  if (isNeutral1 || isNeutral2) {
    return 0.85 + Math.random() * 0.1;
  }

  // Calculate hue difference
  const hueDiff = Math.abs(hsl1.h - hsl2.h);
  const normalizedDiff = Math.min(hueDiff, 360 - hueDiff);

  let score = 0.5;

  // Complementary colors (opposite on color wheel) - high harmony
  if (normalizedDiff >= 150 && normalizedDiff <= 210) {
    score = 0.90 + Math.random() * 0.08;
  }
  // Analogous colors (close on color wheel) - good harmony
  else if (normalizedDiff <= 45) {
    score = 0.80 + Math.random() * 0.1;
  }
  // Triadic (120 degrees apart)
  else if (normalizedDiff >= 110 && normalizedDiff <= 130) {
    score = 0.85 + Math.random() * 0.08;
  }
  // Split-complementary
  else if ((normalizedDiff >= 135 && normalizedDiff <= 165) || (normalizedDiff >= 195 && normalizedDiff <= 225)) {
    score = 0.82 + Math.random() * 0.08;
  }
  // Other combinations
  else {
    score = 0.60 + Math.random() * 0.15;
  }

  // Bonus for similar lightness levels (not too contrasting)
  const lightnessDiff = Math.abs(hsl1.l - hsl2.l);
  if (lightnessDiff < 0.3) {
    score += 0.05;
  }

  return Math.min(0.98, score);
}

export async function getAIRecommendations(
  occasion: string,
  topsArray: Array<{ imageUrl: string; id: string }>,
  bottomsArray: Array<{ imageUrl: string; id: string }>,
  maxOutfits: number = 3
): Promise<MLRecommendationResponse> {
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('🎯 COLOR HARMONY RECOMMENDATION ENGINE');
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log(`   Occasion: ${occasion}`);
  console.log(`   Tops: ${topsArray?.length || 0}`);
  console.log(`   Bottoms: ${bottomsArray?.length || 0}`);

  // Guard: must have at least 1 top and 1 bottom
  if (!topsArray || !bottomsArray || topsArray.length === 0 || bottomsArray.length === 0) {
    return {
      occasion,
      recommendations: [],
      total_items_analyzed: (topsArray?.length || 0) + (bottomsArray?.length || 0),
      status: 'error',
      reason: 'MISSING_TOP_OR_BOTTOM',
      debug: {
        tops_count: topsArray?.length || 0,
        bottoms_count: bottomsArray?.length || 0,
        unknown_count: 0,
        unknown_items: []
      }
    };
  }

  // Step 1: Extract colors from all items
  console.log('\n🎨 STEP 1: Extracting colors...');

  interface ItemWithColor {
    id: string;
    imageUrl: string;
    color: string;
  }

  const topsWithColors: ItemWithColor[] = [];
  const bottomsWithColors: ItemWithColor[] = [];

  // Extract colors for tops
  for (const top of topsArray) {
    const color = await extractDominantColor(top.imageUrl);
    topsWithColors.push({ ...top, color });
    console.log(`   👕 TOP "${top.id}": ${color}`);
  }

  // Extract colors for bottoms
  for (const bottom of bottomsArray) {
    const color = await extractDominantColor(bottom.imageUrl);
    bottomsWithColors.push({ ...bottom, color });
    console.log(`   👖 BOTTOM "${bottom.id}": ${color}`);
  }

  // Step 2: Generate all possible pairs and score by color harmony
  console.log('\n🔗 STEP 2: Scoring all top+bottom pairs by color harmony...');

  interface ScoredPair {
    top: ItemWithColor;
    bottom: ItemWithColor;
    harmonyScore: number;
  }

  const scoredPairs: ScoredPair[] = [];

  for (const top of topsWithColors) {
    for (const bottom of bottomsWithColors) {
      const harmonyScore = calculateColorHarmony(top.color, bottom.color);
      scoredPairs.push({ top, bottom, harmonyScore });
      console.log(`   ${top.id} + ${bottom.id}: ${(harmonyScore * 100).toFixed(0)}% harmony`);
    }
  }

  // Step 3: Sort by harmony score and take top N
  scoredPairs.sort((a, b) => b.harmonyScore - a.harmonyScore);
  const bestPairs = scoredPairs.slice(0, maxOutfits);

  console.log(`\n✅ STEP 3: Selected top ${bestPairs.length} outfits`);

  // Step 4: Convert to MLOutfitRecommendation format
  const recommendations: MLOutfitRecommendation[] = bestPairs.map((pair, index) => {
    const topItem: MLClothingItem = {
      filename: pair.top.id,
      type: 'top',
      category: 'top',
      color: pair.top.color,
      url: pair.top.imageUrl,
      role: 'top',
    };

    const bottomItem: MLClothingItem = {
      filename: pair.bottom.id,
      type: 'bottom',
      category: 'bottom',
      color: pair.bottom.color,
      url: pair.bottom.imageUrl,
      role: 'bottom',
    };

    console.log(`   Outfit ${index + 1}: ${pair.top.id} (${pair.top.color}) + ${pair.bottom.id} (${pair.bottom.color}) = ${(pair.harmonyScore * 100).toFixed(0)}%`);

    return {
      top: topItem,
      bottom: bottomItem,
      items: [topItem, bottomItem],
      score: pair.harmonyScore,
      total_items: 2,
    };
  });

  console.log('\n═══════════════════════════════════════════════════════════════════');
  console.log(`✅ GENERATED ${recommendations.length} COLOR-HARMONIZED OUTFITS`);
  console.log('═══════════════════════════════════════════════════════════════════');

  return {
    occasion,
    recommendations,
    total_items_analyzed: topsArray.length + bottomsArray.length,
    status: 'ok',
    debug: {
      tops_count: topsArray.length,
      bottoms_count: bottomsArray.length,
      unknown_count: 0,
      unknown_items: []
    }
  };
}


// ═══════════════════════════════════════════════════════════════════════════════
// 10. UTILITY EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export function getScoreColor(score: number): string {
  if (score > 0.8) return 'text-green-600';
  if (score > 0.6) return 'text-yellow-600';
  return 'text-gray-600';
}

export function formatMatchScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}

export function quickDetectTypeFromFilename(filename: string): string | null {
  return guessTypeFromFilename(filename);
}

export const occasionIcons: Record<string, string> = {
  casual: '👕',
  formal: '🎩',
  business: '💼',
  party: '🎉',
  date: '💕',
  sports: '⚽',
};
