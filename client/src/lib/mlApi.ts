/**
 * ML API Service Layer
 * Re-exports core types and algorithms while orchestrating backend ML and client-side fallback.
 */

import {
  MLClothingItem,
  MLOutfitRecommendation,
  MLRecommendationResponse,
  MLTypePrediction,
} from './mlTypes';
import { extractDominantColor, getScoreColor, formatMatchScore } from './colorAnalysis';
import {
  quickDetectTypeFromFilename,
  generateClientOutfitRecommendations,
} from './outfitRecommender';

// Re-export types & utilities for full backwards compatibility
export * from './mlTypes';
export * from './colorAnalysis';
export * from './outfitRecommender';

/**
 * Resolve the API base URL for the ML backend
 */
export const getApiBaseUrl = (): string => {
  // 1. Check environment variable
  const envUrl = (import.meta as any).env?.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim().length > 0) {
    return envUrl.replace(/\/+$/, '');
  }

  // 2. Local development fallback (FastAPI typically runs on port 8000 or 8001)
  if (typeof window !== 'undefined') {
    const isLocalhost =
      window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (isLocalhost) {
      return `${window.location.protocol}//${window.location.hostname}:8000`;
    }
  }

  // 3. Fallback when deployed without custom backend URL
  return '';
};

/**
 * Predict clothing type using Python FastAPI model, with client heuristic fallback
 */
export async function detectClothingType(file: File): Promise<MLTypePrediction> {
  const baseUrl = getApiBaseUrl();

  if (baseUrl) {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${baseUrl}/predict-type`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('ML backend unavailable, using heuristic fallback:', error);
    }
  }

  // Client-side heuristic fallback
  const filenameGuess = quickDetectTypeFromFilename(file.name);
  if (filenameGuess) {
    return {
      predicted_type: filenameGuess as 'top' | 'bottom',
      confidence: 0.85,
    };
  }

  return { predicted_type: 'other', confidence: 0.5 };
}

/**
 * Generate AI outfit recommendations.
 * Tries the FastAPI backend first; if unavailable or offline, executes client-side color harmony engine.
 */
export async function getAIRecommendations(
  occasion: string,
  topsArray: Array<{ imageUrl: string; id: string }>,
  bottomsArray: Array<{ imageUrl: string; id: string }>,
  maxOutfits: number = 3
): Promise<MLRecommendationResponse> {
  // Guard check
  if (!topsArray || !bottomsArray || topsArray.length === 0 || bottomsArray.length === 0) {
    return {
      occasion,
      recommendations: [],
      total_items_analyzed: (topsArray?.length || 0) + (bottomsArray?.length || 0),
      status: 'error',
      reason: 'MISSING_TOP_OR_BOTTOM',
      backendMode: 'client_heuristic',
      debug: {
        tops_count: topsArray?.length || 0,
        bottoms_count: bottomsArray?.length || 0,
        unknown_count: 0,
        unknown_items: [],
      },
    };
  }

  const baseUrl = getApiBaseUrl();

  // Try FastAPI backend if a base URL is configured
  if (baseUrl) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000);

      const response = await fetch(`${baseUrl}/recommend-outfits`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tops: topsArray,
          bottoms: bottomsArray,
          occasion,
          max_outfits: maxOutfits,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        if (data.recommendations && data.recommendations.length > 0) {
          return {
            ...data,
            status: 'ok',
            backendMode: 'fastapi_ml',
          };
        }
      }
    } catch (err) {
      console.info('Backend ML recommendation failed or timed out. Falling back to client engine.');
    }
  }

  // Client-Side Color Harmony Engine Fallback
  const recommendations = await generateClientOutfitRecommendations(
    occasion,
    topsArray,
    bottomsArray,
    maxOutfits
  );

  return {
    occasion,
    recommendations,
    total_items_analyzed: topsArray.length + bottomsArray.length,
    status: 'ok',
    backendMode: 'client_heuristic',
    debug: {
      tops_count: topsArray.length,
      bottoms_count: bottomsArray.length,
      unknown_count: 0,
      unknown_items: [],
    },
  };
}
