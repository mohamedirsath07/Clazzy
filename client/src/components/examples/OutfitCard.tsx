import { OutfitCard } from "../OutfitCard";
import type { OutfitRecommendation } from "@shared/schema";

const mockOutfit: OutfitRecommendation = {
  id: "1",
  occasion: "party",
  matchScore: 95,
  description: "Perfect combination for a night out! The colors complement each other beautifully.",
  items: [
    { id: "1", imageUrl: "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=400", type: "shirt" },
    { id: "2", imageUrl: "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400", type: "pants" },
    { id: "3", imageUrl: "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400", type: "shoes" },
    { id: "4", imageUrl: "https://images.unsplash.com/photo-1616150840652-ed6ea789ef4c?w=400", type: "jacket" },
  ],
};

export default function OutfitCardExample() {
  return (
    <div className="p-8">
      <div className="mx-auto max-w-sm">
        <OutfitCard outfit={mockOutfit} />
      </div>
    </div>
  );
}
