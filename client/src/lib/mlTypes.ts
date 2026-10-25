/**
 * ML API & Wardrobe Recommendation Type Definitions
 */

export interface MLTypePrediction {
  predicted_type: 'top' | 'bottom' | 'shoes' | 'dress' | 'blazer' | 'other';
  confidence: number;
}

/**
 * Role-locked clothing item structure
 */
export interface MLClothingItem {
  filename: string;
  type: 'top' | 'bottom' | 'dress' | 'unknown';
  category: string;
  color: string;
  url: string;
  role: 'top' | 'bottom';
  visualType?: 'top' | 'bottom' | 'unknown';
  verifiedType?: 'top' | 'bottom';
  imageWidth?: number;
  imageHeight?: number;
}

/**
 * Role-locked outfit structure
 */
export interface MLOutfitRecommendation {
  top: MLClothingItem;
  bottom: MLClothingItem;
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
  backendMode?: 'fastapi_ml' | 'client_heuristic';
  debug?: {
    tops_count: number;
    bottoms_count: number;
    unknown_count: number;
    unknown_items: string[];
  };
}

export interface RawItem {
  imageUrl: string;
  detectedType?: string;
  id: string;
  confidence?: number;
}

export interface NormalizedItem extends RawItem {
  normalizedType: 'top' | 'bottom';
}

export interface NormalizedItemWithVisual extends NormalizedItem {
  visualType?: 'top' | 'bottom' | 'unknown';
  verifiedType: 'top' | 'bottom';
  imageWidth?: number;
  imageHeight?: number;
}

export interface Signal {
  type: 'top' | 'bottom';
  weight: number;
  source: string;
}

export const occasionIcons: Record<string, string> = {
  casual: '👕',
  formal: '🎩',
  business: '💼',
  party: '🎉',
  date: '💕',
  sports: '⚽',
};
