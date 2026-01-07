import { useState } from "react";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { ProgressIndicator } from "@/components/ProgressIndicator";
import { ImageUpload } from "@/components/ImageUpload";
import { Library } from "@/components/Library";
import { UserDetailsForm } from "@/components/UserDetailsForm";
import { OccasionSelector } from "@/components/OccasionSelector";
import { OutfitCard } from "@/components/OutfitCard";
import { MLOutfitCard } from "@/components/MLOutfitCard";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ArrowLeft, Sparkles, Loader2 } from "lucide-react";
import type { ClothingItem, UserProfile, Occasion, OutfitRecommendation } from "@shared/schema";
import { getAIRecommendations, type MLRecommendationResponse } from "@/lib/mlApi";

const steps = [
  { number: 1, title: "Upload" },
  { number: 2, title: "Details" },
  { number: 3, title: "Results" },
];

export default function Home() {
  const [currentStep, setCurrentStep] = useState(0);
  const [clothingItems, setClothingItems] = useState<ClothingItem[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [selectedOccasion, setSelectedOccasion] = useState<Occasion | undefined>();
  const [showLibrary, setShowLibrary] = useState(false);
  
  // ML AI Recommendations State
  const [mlRecommendations, setMlRecommendations] = useState<MLRecommendationResponse | null>(null);
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [showMLResults, setShowMLResults] = useState(false);

  const mockRecommendations: OutfitRecommendation[] = [
    {
      id: "1",
      occasion: selectedOccasion || "casual",
      matchScore: 95,
      description: "Perfect balance of style and comfort for your occasion.",
      items: clothingItems.slice(0, 4),
    },
    {
      id: "2",
      occasion: selectedOccasion || "casual",
      matchScore: 88,
      description: "A bold combination that makes a statement.",
      items: clothingItems.slice(1, 5),
    },
    {
      id: "3",
      occasion: selectedOccasion || "casual",
      matchScore: 82,
      description: "Classic and timeless outfit choice.",
      items: clothingItems.slice(2, 6),
    },
  ];

  const handleGetStarted = () => {
    setCurrentStep(1);
  };

  const handleImagesChange = (items: ClothingItem[]) => {
    setClothingItems(items);
  };

  const handleLibrarySelect = (items: ClothingItem[]) => {
    // Add library items to existing items
    setClothingItems((prev) => [...prev, ...items]);
  };

  const handleNextFromUpload = () => {
    if (clothingItems.length >= 2) {
      setCurrentStep(2);
    }
  };

  const handleUserDetailsSubmit = (profile: UserProfile) => {
    setUserProfile(profile);
  };

  const handleOccasionSelect = (occasion: Occasion) => {
    setSelectedOccasion(occasion);
  };

  const handleGetRecommendations = async () => {
    if (!selectedOccasion) return;
    
    // Automatically generate AI recommendations when moving to results
    if (clothingItems.length >= 2) {
      setIsLoadingAI(true);
      try {
        const result = await getAIRecommendations(selectedOccasion, clothingItems, 2);
        setMlRecommendations(result);
      } catch (error) {
        console.error('AI recommendation error:', error);
      } finally {
        setIsLoadingAI(false);
      }
    }
    
    setCurrentStep(3);
  };

  // NEW: Get AI-Powered Recommendations
  const handleGetAIRecommendations = async () => {
    if (!selectedOccasion) return;
    
    setIsLoadingAI(true);
    setAiError(null);
    setShowMLResults(true);
    
    try {
      // Pass actual uploaded clothing items to get recommendations
      // Request 2 items per outfit: 1 top + 1 bottom
      const result = await getAIRecommendations(selectedOccasion, clothingItems, 2);
      setMlRecommendations(result);
      
      // NEW: Check status field for proper error handling
      if (result.status === 'error') {
        // Handle specific error reasons with appropriate messages
        switch (result.reason) {
          case 'MISSING_TOP_OR_BOTTOM':
            // Check which type is missing for specific guidance
            const hasTop = result.debug?.tops_count && result.debug.tops_count > 0;
            const hasBottom = result.debug?.bottoms_count && result.debug.bottoms_count > 0;
            if (!hasTop && !hasBottom) {
              setAiError('No clothing items detected. Please upload images of shirts, pants, or other clothing.');
            } else if (!hasTop) {
              setAiError('Please upload at least one TOP (shirt, blouse, t-shirt) to create outfit combinations.');
            } else {
              setAiError('Please upload at least one BOTTOM (pants, jeans, skirt) to create outfit combinations.');
            }
            break;
          case 'ALL_ITEMS_UNKNOWN':
            setAiError('Could not identify clothing types. Please ensure images clearly show clothing items and try again.');
            break;
          case 'LOW_CONFIDENCE':
            setAiError('Clothing detection confidence was too low. Try uploading clearer images of your clothing.');
            break;
          case 'NO_ITEMS':
            setAiError('No items found. Please upload clothing images first.');
            break;
          default:
            setAiError('Could not generate recommendations. Please check your uploaded images.');
        }
        // Log debug info for transparency
        if (result.debug) {
          console.log('📊 Recommendation Debug Info:', result.debug);
        }
      } else if (result.recommendations.length === 0) {
        // Status is OK but no recommendations (shouldn't happen, but handle gracefully)
        setAiError('No outfit combinations could be generated from your items.');
      } else {
        // Success! Clear any previous error and move to results
        setAiError(null);
        // Automatically move to results page after generating AI recommendations
        setTimeout(() => {
          setCurrentStep(3);
        }, 1000); // Small delay to show the generated outfits preview
      }
    } catch (error) {
      console.error('AI recommendation error:', error);
      setAiError('Technical error generating recommendations. Please try again.');
      setMlRecommendations(null);
    } finally {
      setIsLoadingAI(false);
    }
  };

  const handleBack = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleStartOver = () => {
    setCurrentStep(0);
    setClothingItems([]);
    setUserProfile(null);
    setSelectedOccasion(undefined);
    setMlRecommendations(null);
    setShowMLResults(false);
    setAiError(null);
  };

  return (
    <div className="min-h-screen bg-black">
      <Header />

      {currentStep === 0 && <Hero onGetStarted={handleGetStarted} />}

      {currentStep > 0 && (
        <div className="container mx-auto px-4 py-12 bg-gradient-to-br from-gray-900 via-black to-gray-900 min-h-screen">
          <ProgressIndicator currentStep={currentStep} steps={steps} />

          {currentStep === 1 && (
            <div className="mx-auto max-w-4xl">
              <div className="mb-8 text-center">
                <h2 className="mb-2 text-3xl font-bold" data-testid="text-step-title">
                  Upload Your Clothes
                </h2>
                <p className="text-muted-foreground">
                  Add photos of your clothing items (minimum 2 items)
                </p>
              </div>

              <ImageUpload 
                onImagesChange={handleImagesChange}
                onOpenLibrary={() => setShowLibrary(true)}
              />

              <div className="mt-8 flex gap-4">
                <Button
                  variant="outline"
                  onClick={handleBack}
                  className="gap-2"
                  data-testid="button-back"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back
                </Button>
                <Button
                  onClick={handleNextFromUpload}
                  disabled={clothingItems.length < 2}
                  className="flex-1 rounded-xl h-12"
                  data-testid="button-next-upload"
                >
                  Continue
                </Button>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="mx-auto max-w-4xl">
              <div className="mb-8 text-center">
                <h2 className="mb-2 text-3xl font-bold" data-testid="text-step-title">
                  Tell Us About Yourself
                </h2>
                <p className="text-muted-foreground">
                  Help us personalize your outfit recommendations
                </p>
              </div>

              <div className="mb-8">
                <UserDetailsForm
                  onSubmit={handleUserDetailsSubmit}
                  defaultValues={userProfile || undefined}
                />
              </div>

              <div className="mb-8">
                <h3 className="mb-4 text-xl font-semibold">
                  What's the occasion?
                </h3>
                <OccasionSelector
                  selected={selectedOccasion}
                  onSelect={handleOccasionSelect}
                />
              </div>

              {/* AI Recommendations Section */}
              {selectedOccasion && (
                <div className="mb-8 rounded-xl border bg-gradient-to-br from-purple-50 to-blue-50 p-6 dark:from-purple-950/20 dark:to-blue-950/20">
                  <div className="mb-4 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-purple-600" />
                    <h3 className="text-lg font-semibold">AI-Powered Outfit Suggestions</h3>
                  </div>
                  
                  <p className="mb-4 text-sm text-muted-foreground">
                    Get intelligent shirt + pant combinations powered by ML models analyzing your wardrobe
                  </p>

                  <Button
                    onClick={handleGetAIRecommendations}
                    disabled={isLoadingAI || clothingItems.length < 2}
                    className="w-full gap-2 rounded-xl h-12 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    data-testid="button-ai-recommendations"
                  >
                    {isLoadingAI ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        AI is analyzing your wardrobe...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4" />
                        Get AI Recommendations
                      </>
                    )}
                  </Button>

                  {clothingItems.length < 2 && (
                    <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                      Upload at least 2 clothing items (tops and bottoms) to get AI recommendations
                    </p>
                  )}

                  {/* AI Error Alert - now with specific messages based on reason */}
                  {aiError && (
                    <Alert variant="destructive" className="mt-4">
                      <AlertDescription>{aiError}</AlertDescription>
                    </Alert>
                  )}

                  {/* Debug info display (helpful for users) */}
                  {showMLResults && mlRecommendations?.debug && mlRecommendations.status === 'error' && (
                    <div className="mt-2 text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                      <p>Detected: {mlRecommendations.debug.tops_count} tops, {mlRecommendations.debug.bottoms_count} bottoms</p>
                      {mlRecommendations.debug.unknown_count > 0 && (
                        <p className="text-amber-600">
                          {mlRecommendations.debug.unknown_count} items could not be classified
                        </p>
                      )}
                    </div>
                  )}

                  {/* ML Recommendations Display */}
                  {showMLResults && mlRecommendations && mlRecommendations.status === 'ok' && mlRecommendations.recommendations.length > 0 && (
                    <div className="mt-6">
                      <div className="mb-4 flex items-center justify-between">
                        <h4 className="font-semibold">
                          {mlRecommendations.recommendations.length} AI-Generated Outfits
                        </h4>
                        <span className="text-xs text-muted-foreground">
                          Analyzed {mlRecommendations.total_items_analyzed} items
                          {mlRecommendations.debug && (
                            <> ({mlRecommendations.debug.tops_count} tops, {mlRecommendations.debug.bottoms_count} bottoms)</>
                          )}
                        </span>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2">
                        {mlRecommendations.recommendations.map((outfit, index) => (
                          <MLOutfitCard
                            key={index}
                            outfit={outfit}
                            occasion={selectedOccasion}
                            index={index}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Only show this if status is OK but no recommendations (edge case) */}
                  {showMLResults && mlRecommendations && mlRecommendations.status === 'ok' && mlRecommendations.recommendations.length === 0 && (
                    <Alert className="mt-4">
                      <AlertDescription>
                        No outfit combinations could be generated. Try uploading more clothing items.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              )}

              <div className="flex gap-4">
                <Button
                  variant="outline"
                  onClick={handleBack}
                  className="gap-2"
                  data-testid="button-back"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back
                </Button>
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="mx-auto max-w-6xl">
              <div className="mb-8 text-center">
                <h2 className="mb-2 text-3xl font-bold" data-testid="text-step-title">
                  Your Perfect Outfits
                </h2>
                <p className="text-muted-foreground">
                  {mlRecommendations && mlRecommendations.recommendations.length > 0
                    ? `AI-powered recommendations for ${selectedOccasion} occasions`
                    : `Here are our top recommendations for ${selectedOccasion} occasions`}
                </p>
              </div>

              {/* AI-Generated Outfits Section */}
              {mlRecommendations && mlRecommendations.recommendations.length > 0 && (
                <div className="mb-12">
                  <div className="mb-6 flex items-center gap-3">
                    <div className="flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-100 to-blue-100 px-4 py-2 dark:from-purple-900/30 dark:to-blue-900/30">
                      <Sparkles className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                      <span className="font-semibold text-purple-900 dark:text-purple-100">
                        {mlRecommendations.recommendations.length} AI-Generated Outfits
                      </span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      Analyzed {mlRecommendations.total_items_analyzed} items from your wardrobe
                    </span>
                  </div>

                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {mlRecommendations.recommendations.map((outfit, index) => (
                      <MLOutfitCard
                        key={index}
                        outfit={outfit}
                        occasion={selectedOccasion || 'casual'}
                        index={index}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Fallback to Mock Recommendations if no AI results */}
              {(!mlRecommendations || mlRecommendations.recommendations.length === 0) && (
                <div className="mb-8">
                  <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-900/20">
                    <p className="text-sm text-amber-800 dark:text-amber-200">
                      <strong>Tip:</strong> Click "Get AI Recommendations" on the previous step to see personalized outfit combinations based on your uploaded items!
                    </p>
                  </div>
                  
                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {mockRecommendations.map((outfit) => (
                      <OutfitCard key={outfit.id} outfit={outfit} />
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-center gap-4">
                <Button
                  variant="outline"
                  onClick={handleBack}
                  className="gap-2"
                  data-testid="button-back"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back
                </Button>
                <Button
                  onClick={handleStartOver}
                  className="rounded-xl h-12 px-8"
                  data-testid="button-start-over"
                >
                  Start Over
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Library Modal */}
      {showLibrary && (
        <Library
          onSelectImages={handleLibrarySelect}
          onClose={() => setShowLibrary(false)}
        />
      )}
    </div>
  );
}
