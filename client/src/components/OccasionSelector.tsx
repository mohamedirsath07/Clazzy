import { Briefcase, Heart, Sparkles, Sun, Zap, GraduationCap, Trophy } from "lucide-react";
import { Card } from "@/components/ui/card";
import type { Occasion } from "@shared/schema";

const occasions = [
  { value: "casual" as const, label: "Casual", icon: Sun, color: "text-yellow-500" },
  { value: "formal" as const, label: "Formal", icon: GraduationCap, color: "text-blue-500" },
  { value: "business" as const, label: "Business", icon: Briefcase, color: "text-gray-600" },
  { value: "party" as const, label: "Party", icon: Sparkles, color: "text-purple-500" },
  { value: "date" as const, label: "Date", icon: Heart, color: "text-pink-500" },
  { value: "sports" as const, label: "Sports", icon: Trophy, color: "text-green-500" },
];

interface OccasionSelectorProps {
  selected?: Occasion;
  onSelect: (occasion: Occasion) => void;
}

export function OccasionSelector({ selected, onSelect }: OccasionSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
      {occasions.map((occasion) => {
        const Icon = occasion.icon;
        const isSelected = selected === occasion.value;
        
        return (
          <Card
            key={occasion.value}
            className={`cursor-pointer p-6 transition-all hover-elevate active-elevate-2 ${
              isSelected ? "border-primary bg-primary/5" : ""
            }`}
            onClick={() => onSelect(occasion.value)}
            data-testid={`card-occasion-${occasion.value}`}
          >
            <div className="flex flex-col items-center gap-3 text-center">
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-xl ${
                  isSelected ? "bg-primary text-primary-foreground" : "bg-muted"
                }`}
              >
                <Icon className={`h-6 w-6 ${isSelected ? "" : occasion.color}`} />
              </div>
              <span className="font-semibold">{occasion.label}</span>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
