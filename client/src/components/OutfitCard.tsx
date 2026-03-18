import { Star } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { OutfitRecommendation } from "@shared/schema";

interface OutfitCardProps {
  outfit: OutfitRecommendation;
}

export function OutfitCard({ outfit }: OutfitCardProps) {
  return (
    <Card className="overflow-hidden p-0">
      <div className="relative">
        <div className="grid grid-cols-2 gap-1 bg-muted p-1">
          {outfit.items.slice(0, 4).map((item) => (
            <div
              key={item.id}
              className="aspect-square overflow-hidden rounded-md bg-background"
            >
              <img
                src={item.imageUrl}
                alt={item.type || "Clothing item"}
                className="h-full w-full object-cover"
                data-testid={`outfit-item-${item.id}`}
              />
            </div>
          ))}
        </div>
        <Badge className="absolute right-3 top-3 capitalize" data-testid={`badge-occasion-${outfit.occasion}`}>
          {outfit.occasion}
        </Badge>
      </div>

      <div className="p-4">
        <div className="mb-2 flex items-center justify-between">
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            <span className="font-semibold" data-testid={`text-match-score-${outfit.id}`}>
              {outfit.matchScore}% Match
            </span>
          </div>
        </div>
        {outfit.description && (
          <p className="text-sm text-muted-foreground" data-testid={`text-description-${outfit.id}`}>
            {outfit.description}
          </p>
        )}
      </div>
    </Card>
  );
}
