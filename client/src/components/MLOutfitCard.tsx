/**
 * MLOutfitCard V3 - WITH GSAP ANIMATIONS & HISTORY SAVE
 * =============================================================================
 */

import { useState, useEffect, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sparkles, History, Check } from "lucide-react";
import type { MLOutfitRecommendation } from "@/lib/mlApi";
import { formatMatchScore, getScoreColor } from "@/lib/mlApi";
import { saveOutfitToHistory } from "@/lib/outfitHistory";
import gsap from "gsap";

interface MLOutfitCardProps {
  outfit: MLOutfitRecommendation;
  occasion: string;
  index: number;
}

/**
 * MLOutfitCard - Displays outfit recommendations with save to history
 */
export function MLOutfitCard({ outfit, occasion, index }: MLOutfitCardProps) {
  const { top, bottom } = outfit;
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const scorePercentage = formatMatchScore(outfit.score);
  const scoreColorClass = getScoreColor(outfit.score);

  // GSAP entrance animation
  useEffect(() => {
    if (cardRef.current) {
      gsap.fromTo(
        cardRef.current,
        {
          opacity: 0,
          y: 60,
          scale: 0.9,
          rotateX: -10
        },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          rotateX: 0,
          duration: 0.7,
          delay: index * 0.15, // Stagger based on index
          ease: "power3.out"
        }
      );
    }
  }, [index]);

  const handleSaveToHistory = async () => {
    if (isSaved || isSaving) return;

    setIsSaving(true);
    try {
      await saveOutfitToHistory({
        topUrl: top.url,
        bottomUrl: bottom.url,
        occasion,
        score: outfit.score
      });
      setIsSaved(true);

      // Celebrate animation when saved
      if (cardRef.current) {
        gsap.to(cardRef.current, {
          scale: 1.05,
          duration: 0.2,
          yoyo: true,
          repeat: 1,
          ease: "power2.out"
        });
      }
    } catch (error) {
      console.error('Failed to save outfit:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card
      ref={cardRef}
      className="overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/20 hover:-translate-y-2 opacity-0 cursor-pointer group"
      data-testid={`ml-outfit-card-${index}`}
    >      <CardContent className="p-0">
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
          {/* Ready to wear + Save Button */}
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">
              ✓ Ready to wear
            </p>
            <Button
              variant={isSaved ? "secondary" : "outline"}
              size="sm"
              className="gap-1.5 text-xs"
              onClick={handleSaveToHistory}
              disabled={isSaving || isSaved}
            >
              {isSaved ? (
                <>
                  <Check className="h-3 w-3" />
                  Saved
                </>
              ) : (
                <>
                  <History className="h-3 w-3" />
                  {isSaving ? 'Saving...' : 'Add to Saved Collection'}
                </>
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
