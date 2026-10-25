/**
 * Outfit Recommendation Logic & Multi-Signal Garment Classifier
 * Ensures tops and bottoms are cleanly distinguished and harmoniously paired.
 */

import {
  MLClothingItem,
  MLOutfitRecommendation,
  RawItem,
  NormalizedItemWithVisual,
  Signal,
} from './mlTypes';
import { calculateColorHarmony, extractDominantColor } from './colorAnalysis';

export const TYPE_ALIASES: Record<string, 'top' | 'bottom' | 'unknown'> = {
  // Top aliases
  top: 'top',
  shirt: 'top',
  blouse: 'top',
  't-shirt': 'top',
  tshirt: 'top',
  polo: 'top',
  sweater: 'top',
  hoodie: 'top',
  jacket: 'top',
  coat: 'top',
  blazer: 'top',
  cardigan: 'top',
  tank: 'top',
  tanktop: 'top',
  vest: 'top',
  tunic: 'top',
  // Bottom aliases
  bottom: 'bottom',
  pants: 'bottom',
  pant: 'bottom',
  jeans: 'bottom',
  jean: 'bottom',
  trousers: 'bottom',
  trouser: 'bottom',
  shorts: 'bottom',
  short: 'bottom',
  skirt: 'bottom',
  leggings: 'bottom',
  legging: 'bottom',
  joggers: 'bottom',
  chinos: 'bottom',
  chino: 'bottom',
  cargo: 'bottom',
  // Unknown
  other: 'unknown',
  dress: 'unknown',
};

export function normalizeType(rawType: string | undefined): 'top' | 'bottom' | 'unknown' {
  if (!rawType) return 'unknown';
  const cleaned = rawType.trim().toLowerCase().replace(/-/g, '').replace(/_/g, '');

  if (TYPE_ALIASES[cleaned]) return TYPE_ALIASES[cleaned];

  for (const [alias, type] of Object.entries(TYPE_ALIASES)) {
    if (cleaned.includes(alias)) return type;
  }

  return 'unknown';
}

export function guessTypeFromFilename(filename: string): 'top' | 'bottom' | null {
  const lower = filename.toLowerCase();

  const topPatterns = [
    'shirt',
    'tee',
    'blouse',
    'top',
    'polo',
    'sweater',
    'hoodie',
    'jacket',
    'blazer',
    'coat',
  ];
  for (const p of topPatterns) {
    if (lower.includes(p)) return 'top';
  }

  const bottomPatterns = [
    'pant',
    'jean',
    'trouser',
    'short',
    'skirt',
    'bottom',
    'cargo',
    'chino',
    'legging',
  ];
  for (const p of bottomPatterns) {
    if (lower.includes(p)) return 'bottom';
  }

  return null;
}

export function quickDetectTypeFromFilename(filename: string): string | null {
  return guessTypeFromFilename(filename);
}

export function getImageDimensions(imageUrl: string): Promise<{ width: number; height: number }> {
  if (typeof window === 'undefined') {
    return Promise.resolve({ width: 0, height: 0 });
  }

  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve({ width: img.width, height: img.height });
    img.onerror = () => resolve({ width: 0, height: 0 });
    setTimeout(() => resolve({ width: 0, height: 0 }), 2000);
    img.src = imageUrl;
  });
}

export function isVisuallyATop(width: number, height: number): boolean {
  if (width <= 0 || height <= 0) return false;
  return height / width < 1.2;
}

export function isVisuallyABottom(width: number, height: number): boolean {
  if (width <= 0 || height <= 0) return false;
  return height / width >= 1.2;
}

export function detectStructuralFeatures(name: string, imageUrl: string): 'top' | 'bottom' | null {
  const text = `${name} ${imageUrl}`.toLowerCase();

  const topFeatures = [
    'sleeve',
    'collar',
    'button',
    'neck',
    'v-neck',
    'crew',
    'polo',
    'hoodie',
    'hood',
    'zip',
    'zipper',
    'pocket',
    'long-sleeve',
    'short-sleeve',
    'sleeveless',
  ];

  for (const feature of topFeatures) {
    if (text.includes(feature)) return 'top';
  }

  const bottomFeatures = ['waist', 'belt-loop', 'beltloop', 'inseam', 'cuff', 'leg'];
  for (const feature of bottomFeatures) {
    if (text.includes(feature)) return 'bottom';
  }

  return null;
}

export function calculatePantLikenessScore(item: NormalizedItemWithVisual): number {
  let score = 0.0;
  const { imageWidth = 0, imageHeight = 0, id, imageUrl } = item;
  const name = id.toLowerCase();
  const url = imageUrl.toLowerCase();

  if (imageWidth > 0 && imageHeight > 0) {
    const aspectRatio = imageHeight / imageWidth;
    if (aspectRatio > 1.5) score += 0.5;
    else if (aspectRatio > 1.3) score += 0.3;
    else if (aspectRatio > 1.1) score += 0.1;
  }

  const bottomKeywords = ['pant', 'jean', 'trouser', 'short', 'skirt', 'bottom', 'cargo', 'chino'];
  for (const kw of bottomKeywords) {
    if (name.includes(kw) || url.includes(kw)) {
      score += 0.4;
      break;
    }
  }

  const topKeywords = ['shirt', 'tee', 'blouse', 'top', 'polo', 'sweater', 'hoodie', 'jacket'];
  const hasTopKeyword = topKeywords.some((kw) => name.includes(kw) || url.includes(kw));
  if (!hasTopKeyword) score += 0.1;

  return Math.min(1.0, score);
}

export async function determineVisualType(imageUrl: string): Promise<'top' | 'bottom' | 'unknown'> {
  if (typeof window === 'undefined') return 'unknown';

  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'Anonymous';

    img.onload = () => {
      const { width, height } = img;
      const aspectRatio = height / width;
      if (aspectRatio < 1.2) {
        resolve('top');
      } else {
        resolve('bottom');
      }
    };

    img.onerror = () => resolve('unknown');
    setTimeout(() => resolve('unknown'), 3000);
    img.src = imageUrl;
  });
}

export async function resolveGarmentType(
  item: RawItem,
  width: number = 0,
  height: number = 0
): Promise<'top' | 'bottom'> {
  const signals: Signal[] = [];
  const confidence = item.confidence ?? 0.5;

  if (width === 0 || height === 0) {
    const dims = await getImageDimensions(item.imageUrl);
    width = dims.width;
    height = dims.height;
  }

  // Visual aspect ratio
  if (width > 0 && height > 0) {
    const aspectRatio = height / width;
    if (aspectRatio > 1.4) {
      signals.push({ type: 'bottom', weight: 3.0, source: 'VISUAL' });
    } else if (aspectRatio < 1.0) {
      signals.push({ type: 'top', weight: 3.0, source: 'VISUAL' });
    } else if (aspectRatio > 1.2) {
      signals.push({ type: 'bottom', weight: 1.5, source: 'VISUAL' });
    } else {
      signals.push({ type: 'top', weight: 1.5, source: 'VISUAL' });
    }
  }

  // Structural cues
  const structureType = detectStructuralFeatures(item.id, item.imageUrl);
  if (structureType) {
    signals.push({ type: structureType, weight: 2.5, source: 'STRUCTURE' });
  }

  // Filename cues
  let filenameType = guessTypeFromFilename(item.id);
  if (!filenameType) {
    const urlFilename = item.imageUrl.split('/').pop()?.split('?')[0] || '';
    filenameType = guessTypeFromFilename(urlFilename);
  }
  if (filenameType) {
    signals.push({ type: filenameType, weight: 2.0, source: 'FILENAME' });
  }

  // ML cues
  const mlType = normalizeType(item.detectedType);
  if (mlType !== 'unknown') {
    const mlWeight = Math.min(1.0, confidence);
    signals.push({ type: mlType, weight: mlWeight, source: 'ML' });
  }

  if (signals.length === 0) {
    return 'top';
  }

  const topWeight = signals.filter((s) => s.type === 'top').reduce((sum, s) => sum + s.weight, 0);
  const bottomWeight = signals
    .filter((s) => s.type === 'bottom')
    .reduce((sum, s) => sum + s.weight, 0);

  if (bottomWeight > topWeight) return 'bottom';
  if (topWeight > bottomWeight) return 'top';

  if (width > 0 && height > 0 && height / width > 1.3) return 'bottom';
  return 'top';
}

export function validateOutfit(outfit: MLOutfitRecommendation): boolean {
  if (!outfit.top || !outfit.bottom) return false;
  if (outfit.top.role !== 'top' || outfit.bottom.role !== 'bottom') return false;
  if (outfit.top.filename === outfit.bottom.filename) return false;
  return true;
}

export async function hardSplitWardrobe(
  items: RawItem[]
): Promise<{ tops: NormalizedItemWithVisual[]; bottoms: NormalizedItemWithVisual[] }> {
  const tops: NormalizedItemWithVisual[] = [];
  const bottoms: NormalizedItemWithVisual[] = [];

  for (const item of items) {
    const dimensions = await getImageDimensions(item.imageUrl);
    const finalType = await resolveGarmentType(item, dimensions.width, dimensions.height);
    const visualType = await determineVisualType(item.imageUrl);

    const normalizedItem: NormalizedItemWithVisual = {
      ...item,
      normalizedType: finalType,
      visualType,
      verifiedType: finalType,
      imageWidth: dimensions.width,
      imageHeight: dimensions.height,
    };

    if (finalType === 'bottom') {
      bottoms.push(normalizedItem);
    } else {
      tops.push(normalizedItem);
    }
  }

  if (bottoms.length === 0 && tops.length >= 2) {
    const topScores: Array<{ item: NormalizedItemWithVisual; score: number }> = [];
    for (const t of tops) {
      topScores.push({ item: t, score: calculatePantLikenessScore(t) });
    }
    topScores.sort((a, b) => b.score - a.score);

    const forcedBottom = topScores[0].item;
    const topsIndex = tops.indexOf(forcedBottom);
    if (topsIndex > -1) {
      tops.splice(topsIndex, 1);
    }
    forcedBottom.normalizedType = 'bottom';
    forcedBottom.verifiedType = 'bottom';
    bottoms.push(forcedBottom);
  }

  return { tops, bottoms };
}

/**
 * Generate occasion-adapted outfit recommendations from tops and bottoms arrays
 */
export async function generateClientOutfitRecommendations(
  occasion: string,
  topsArray: Array<{ imageUrl: string; id: string }>,
  bottomsArray: Array<{ imageUrl: string; id: string }>,
  maxOutfits: number = 3
): Promise<MLOutfitRecommendation[]> {
  interface ItemWithColor {
    id: string;
    imageUrl: string;
    color: string;
  }

  const topsWithColors: ItemWithColor[] = [];
  const bottomsWithColors: ItemWithColor[] = [];

  for (const top of topsArray) {
    const color = await extractDominantColor(top.imageUrl);
    topsWithColors.push({ ...top, color });
  }

  for (const bottom of bottomsArray) {
    const color = await extractDominantColor(bottom.imageUrl);
    bottomsWithColors.push({ ...bottom, color });
  }

  interface ScoredPair {
    top: ItemWithColor;
    bottom: ItemWithColor;
    harmonyScore: number;
  }

  const scoredPairs: ScoredPair[] = [];

  for (const top of topsWithColors) {
    for (const bottom of bottomsWithColors) {
      let score = calculateColorHarmony(top.color, bottom.color);

      // Occasion adjustments
      const occ = occasion.toLowerCase();
      if (occ === 'formal' || occ === 'business') {
        score = Math.min(0.99, score * 1.05);
      } else if (occ === 'party') {
        score = Math.min(0.99, score * 1.03);
      }

      scoredPairs.push({ top, bottom, harmonyScore: score });
    }
  }

  scoredPairs.sort((a, b) => b.harmonyScore - a.harmonyScore);
  const bestPairs = scoredPairs.slice(0, maxOutfits);

  return bestPairs.map((pair) => {
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

    return {
      top: topItem,
      bottom: bottomItem,
      items: [topItem, bottomItem],
      score: pair.harmonyScore,
      total_items: 2,
    };
  });
}
