import { z } from "zod";

export const clothingItemSchema = z.object({
  id: z.string(),
  imageUrl: z.string(),
  type: z.string().optional(),
  detectedType: z.string().optional(),
  confidence: z.number().min(0).max(1).optional(),  // ML classification confidence (0-1)
});

export const userProfileSchema = z.object({
  name: z.string().min(1, "Name is required"),
  age: z.number().min(13, "Must be at least 13 years old").max(120),
  gender: z.enum(["male", "female", "other"]),
});

export const occasionSchema = z.enum([
  "casual",
  "formal",
  "party",
  "work",
  "business", // ML backend uses 'business'
  "date",
  "sport",
  "sports", // ML backend uses 'sports'
]);

export const outfitRecommendationSchema = z.object({
  id: z.string(),
  items: z.array(clothingItemSchema),
  occasion: occasionSchema,
  matchScore: z.number().min(0).max(100),
  description: z.string().optional(),
});

export type ClothingItem = z.infer<typeof clothingItemSchema>;
export type UserProfile = z.infer<typeof userProfileSchema>;
export type Occasion = z.infer<typeof occasionSchema>;
export type OutfitRecommendation = z.infer<typeof outfitRecommendationSchema>;
