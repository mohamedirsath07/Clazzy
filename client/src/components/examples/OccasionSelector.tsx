import { useState } from "react";
import { OccasionSelector } from "../OccasionSelector";
import type { Occasion } from "@shared/schema";

export default function OccasionSelectorExample() {
  const [selected, setSelected] = useState<Occasion>("party");

  return (
    <div className="p-8">
      <OccasionSelector 
        selected={selected} 
        onSelect={(occasion) => {
          setSelected(occasion);
          console.log("Occasion selected:", occasion);
        }}
      />
    </div>
  );
}
