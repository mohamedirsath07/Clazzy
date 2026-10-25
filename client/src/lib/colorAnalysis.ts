/**
 * Color Theory & Analysis Algorithms for Clazzy Fashion Engine
 * Handles HSL conversions, harmony scoring (complementary, analogous, triadic),
 * and dominant color extraction.
 */

export interface RGB {
  r: number;
  g: number;
  b: number;
}

export interface HSL {
  h: number;
  s: number;
  l: number;
}

/**
 * Convert Hex color string to RGB object
 */
export function hexToRgb(hex: string): RGB {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : { r: 128, g: 128, b: 128 };
}

/**
 * Convert RGB components (0-255) to HSL (h: 0-360, s: 0-1, l: 0-1)
 */
export function rgbToHsl(r: number, g: number, b: number): HSL {
  r /= 255;
  g /= 255;
  b /= 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0;
  let s = 0;
  const l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        break;
      case g:
        h = ((b - r) / d + 2) / 6;
        break;
      case b:
        h = ((r - g) / d + 4) / 6;
        break;
    }
  }
  return { h: Math.round(h * 360), s, l };
}

/**
 * Calculate color harmony score between two hex colors using color theory
 */
export function calculateColorHarmony(color1: string, color2: string): number {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);
  const hsl1 = rgbToHsl(rgb1.r, rgb1.g, rgb1.b);
  const hsl2 = rgbToHsl(rgb2.r, rgb2.g, rgb2.b);

  // Check if either color is neutral (low saturation)
  const isNeutral1 = hsl1.s < 0.15;
  const isNeutral2 = hsl2.s < 0.15;

  // Neutrals (white, grey, black, beige) pair harmoniously with almost everything
  if (isNeutral1 || isNeutral2) {
    return 0.88;
  }

  // Calculate shortest distance on the color wheel
  const hueDiff = Math.abs(hsl1.h - hsl2.h);
  const normalizedDiff = Math.min(hueDiff, 360 - hueDiff);

  let score = 0.6;

  // Complementary colors (opposite on color wheel: 150-210 deg)
  if (normalizedDiff >= 150 && normalizedDiff <= 210) {
    score = 0.94;
  }
  // Analogous colors (close on color wheel: <= 45 deg)
  else if (normalizedDiff <= 45) {
    score = 0.86;
  }
  // Triadic colors (~120 deg apart)
  else if (normalizedDiff >= 110 && normalizedDiff <= 130) {
    score = 0.84;
  }
  // Split-complementary (135-165 or 195-225 deg)
  else if (
    (normalizedDiff >= 135 && normalizedDiff <= 165) ||
    (normalizedDiff >= 195 && normalizedDiff <= 225)
  ) {
    score = 0.82;
  } else {
    score = 0.65;
  }

  // Bonus for balanced lightness difference
  const lightnessDiff = Math.abs(hsl1.l - hsl2.l);
  if (lightnessDiff >= 0.15 && lightnessDiff <= 0.6) {
    score += 0.04;
  }

  return Math.min(0.98, Math.max(0.4, score));
}

/**
 * Extract the dominant color from an image URL using canvas pixel sampling
 */
export async function extractDominantColor(imageUrl: string): Promise<string> {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return '#6B7280';
  }

  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'Anonymous';

    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          resolve('#6B7280');
          return;
        }

        const size = 100;
        canvas.width = size;
        canvas.height = size;
        ctx.drawImage(img, 0, 0, size, size);

        const imageData = ctx.getImageData(0, 0, size, size);
        const data = imageData.data;

        let r = 0;
        let g = 0;
        let b = 0;
        let count = 0;
        for (let i = 0; i < data.length; i += 4) {
          const red = data[i];
          const green = data[i + 1];
          const blue = data[i + 2];
          const alpha = data[i + 3];

          if (alpha < 125) continue;
          const brightness = (red + green + blue) / 3;
          if (brightness < 20 || brightness > 235) continue;

          r += red;
          g += green;
          b += blue;
          count++;
        }

        if (count === 0) {
          resolve('#6B7280');
          return;
        }

        const hex =
          '#' +
          [r / count, g / count, b / count]
            .map((x) => Math.round(x).toString(16).padStart(2, '0'))
            .join('');
        resolve(hex);
      } catch {
        resolve('#6B7280');
      }
    };

    img.onerror = () => resolve('#6B7280');
    img.src = imageUrl;
  });
}

/**
 * Return CSS color class based on recommendation match score
 */
export function getScoreColor(score: number): string {
  if (score >= 0.85) return 'text-emerald-500';
  if (score >= 0.7) return 'text-amber-500';
  return 'text-slate-400';
}

/**
 * Format score into percentage string
 */
export function formatMatchScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}
