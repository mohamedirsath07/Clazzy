/**
 * MLOutfitCard V1 - DETERMINISTIC ROLE DISPLAY
 * =============================================================================
 * v1 uses deterministic pairing for reliability.
 * ML-based role detection will be reintroduced in v2.
 * 
 * PRODUCT DECISION:
 * - First image in outfit → always labeled TOP
 * - Second image in outfit → always labeled BOTTOM
 * - UI NEVER reads item.type (ML labels are ignored)
 * - An outfit is always valid if it exists
 * 
 * RULES FOR v1:
 * 1. ALWAYS render outfits - NO validation
 * 2. TRUST backend completely
 * 3. Labels are HARDCODED based on position
 * 4. NO blocking logic, NO error cards
 */

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sparkles } from "lucide-react";
import type { MLOutfitRecommendation } from "@/lib/mlApi";
import { formatMatchScore, getScoreColor } from "@/lib/mlApi";

interface MLOutfitCardProps {
  outfit: MLOutfitRecommendation;
  occasion: string;
  index: number;
}

/**
 * Color Badge - Shows hex color with visual swatch and ROLE label
 */
function ColorBadge({ color, role }: { color: string; role: 'top' | 'bottom' }) {
  return (
    <div className="flex items-center gap-1.5">
      <div
        className="h-3 w-3 rounded-full border border-gray-300"
        style={{ backgroundColor: color }}
        title={`Color: ${color}`}
      />
      <span className="text-xs capitalize font-medium text-muted-foreground">
        {role}
      </span>
    </div>
  );
}

/**
 * MLOutfitCard - Displays outfit recommendations (NO VALIDATION)
 */
export function MLOutfitCard({ outfit, occasion, index }: MLOutfitCardProps) {
  // 🚨 EMERGENCY MODE: Trust backend, no validation
  const { top, bottom } = outfit;
  
  const scorePercentage = formatMatchScore(outfit.score);
  const scoreColorClass = getScoreColor(outfit.score);

  return (
    <Card className="overflow-hidden transition-all hover:shadow-lg" data-testid={`ml-outfit-card-${index}`}>
      <CardContent className="p-0">
        {/* Outfit Images Grid - top first, bottom second */}
        <div className="grid grid-cols-2 gap-1 bg-muted/30 p-2">
          {/* TOP IMAGE */}
          <div className="relative aspect-square overflow-hidden rounded-lg bg-white">
            <img
              src={top.url}
              alt="Top"
              className="h-full w-full object-cover"
              data-testid={`ml-outfit-item-${index}-top`}
              onError={(e) => {
                (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';
              }}
            />
            <div className="absolute bottom-1 left-1 rounded bg-blue-600/80 px-2 py-0.5 text-xs text-white font-medium backdrop-blur-sm">
              TOP
            </div>
          </div>
          
          {/* BOTTOM IMAGE */}
          <div className="relative aspect-square overflow-hidden rounded-lg bg-white">
            <img
              src={bottom.url}
              alt="Bottom"
              className="h-full w-full object-cover"
              data-testid={`ml-outfit-item-${index}-bottom`}
              onError={(e) => {
                (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23ddd" width="200" height="200"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';
              }}
            />
            <div className="absolute bottom-1 left-1 rounded bg-amber-600/80 px-2 py-0.5 text-xs text-white font-medium backdrop-blur-sm">
              BOTTOM
            </div>
          </div>
        </div>

        {/* Match Score Badge */}
        <div className="absolute right-3 top-3 flex items-center gap-1 rounded-full bg-white/95 px-3 py-1.5 shadow-md backdrop-blur-sm">
          <Sparkles className={`h-3.5 w-3.5 ${scoreColorClass}`} />
          <span className={`text-sm font-semibold ${scoreColorClass}`} data-testid={`ml-match-score-${index}`}>
            {scorePercentage}
          </span>
        </div>

        {/* Outfit Details */}
        <div className="p-4">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-semibold text-lg" data-testid={`ml-outfit-title-${index}`}>
              Outfit #{index + 1}
            </h3>
            <Badge variant="outline" className="capitalize">
              {occasion}
            </Badge>
          </div>

          {/* Color Badges */}
          <div className="mb-3">
            <div className="flex flex-wrap gap-3">
              <ColorBadge color={top.color} role="top" />
              <span className="text-muted-foreground">+</span>
              <ColorBadge color={bottom.color} role="bottom" />
            </div>
          </div>

          {/* Info Text */}
          <p className="text-xs text-muted-foreground">
            ✓ Ready to wear
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
