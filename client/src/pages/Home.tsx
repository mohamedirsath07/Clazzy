import { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { ProgressIndicator } from "@/components/ProgressIndicator";
import { ImageUpload } from "@/components/ImageUpload";
import { Library } from "@/components/Library";
import { UserDetailsForm } from "@/components/UserDetailsForm";
import { OccasionSelector } from "@/components/OccasionSelector";
import { MLOutfitCard } from "@/components/MLOutfitCard";
import { OutfitHistory } from "@/components/OutfitHistory";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ArrowLeft, Sparkles, Loader2 } from "lucide-react";
import type { ClothingItem, UserProfile, Occasion } from "@shared/schema";
import { getAIRecommendations, type MLRecommendationResponse } from "@/lib/mlApi";

const steps = [
  { number: 1, title: "Upload" },
  { number: 2, title: "Details" },
  { number: 3, title: "Results" },
];

export default function Home() {
  const [currentStep, setCurrentStep] = useState(0);
  const [tops, setTops] = useState<ClothingItem[]>([]);
  const [bottoms, setBottoms] = useState<ClothingItem[]>([]);
  // computed for backward compatibility if needed, though we use tops/bottoms explicitly now
  const [clothingItems, setClothingItems] = useState<ClothingItem[]>([]);

  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [selectedOccasion, setSelectedOccasion] = useState<Occasion | undefined>();
  const [showLibrary, setShowLibrary] = useState(false);
  const [libraryMode, setLibraryMode] = useState<'top' | 'bottom'>('top');
  const [showHistory, setShowHistory] = useState(false);

  // Update unified clothing items whenever tops or bottoms change
  useEffect(() => {
    setClothingItems([...tops, ...bottoms]);
  }, [tops, bottoms]);

  // ML AI Recommendations State
  const [mlRecommendations, setMlRecommendations] = useState<MLRecommendationResponse | null>(null);
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [showMLResults, setShowMLResults] = useState(false);

  const handleGetStarted = () => {
    setCurrentStep(1);
  };

  const handleTopsChange = (items: ClothingItem[]) => {
    setTops(items);
  };

  const handleBottomsChange = (items: ClothingItem[]) => {
    setBottoms(items);
  };

  const handleLibraryOpen = (mode: 'top' | 'bottom') => {
    setLibraryMode(mode);
    setShowLibrary(true);
  };

  const handleLibrarySelect = (items: ClothingItem[]) => {
    // Add library items to specific section based on mode
    if (libraryMode === 'top') {
      const newItems = items.map(i => ({ ...i, type: 'top' as const, detectedType: 'top' }));
      setTops(prev => [...prev, ...newItems]);
    } else {
      const newItems = items.map(i => ({ ...i, type: 'bottom' as const, detectedType: 'bottom' }));
      setBottoms(prev => [...prev, ...newItems]);
    }
  };

  const handleNextFromUpload = () => {
    if (tops.length > 0 && bottoms.length > 0) {
      setCurrentStep(2);
    }
  };

  const handleUserDetailsSubmit = (profile: UserProfile) => {
    setUserProfile(profile);
  };

  const handleOccasionSelect = (occasion: Occasion) => {
    setSelectedOccasion(occasion);
  };

  // NEW: Get AI-Powered Recommendations
  const handleGetAIRecommendations = async () => {
    if (!selectedOccasion) return;

    setIsLoadingAI(true);
    setAiError(null);
    setShowMLResults(true);

    try {
      // Pass separated tops and bottoms lists
      const result = await getAIRecommendations(selectedOccasion, tops, bottoms, 2);
      setMlRecommendations(result);

      if (result.status === 'error') {
        setAiError(result.reason || "Unknown error generating outfits");
      } else if (result.recommendations.length === 0) {
        setAiError('No outfit combinations could be generated from your items.');
      } else {
        setAiError(null);
        setTimeout(() => {
          setCurrentStep(3);
        }, 1000);
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
    setTops([]);
    setBottoms([]);
    setUserProfile(null);
    setSelectedOccasion(undefined);
    setMlRecommendations(null);
    setShowMLResults(false);
    setAiError(null);
  };

  return (
    <div className="min-h-screen bg-black">
      <Header />

      {currentStep === 0 && <Hero onGetStarted={handleGetStarted} onViewHistory={() => setShowHistory(true)} />}

      {/* Outfit History Modal */}
      {showHistory && (
        <OutfitHistory onClose={() => setShowHistory(false)} />
      )}

      {currentStep > 0 && (
        <div className="container mx-auto px-4 py-12 bg-gradient-to-br from-gray-900 via-black to-gray-900 min-h-screen">
          <ProgressIndicator currentStep={currentStep} steps={steps} />

          {currentStep === 1 && (
            <div className="mx-auto max-w-6xl">
              <div className="mb-8 text-center">
                <h2 className="mb-2 text-3xl font-bold" data-testid="text-step-title">
                  Upload Your Wardrobe
                </h2>
                <p className="text-muted-foreground">
                  Please upload your Tops and Bottoms in the sections below.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* TOPS SECTION */}
                <div className="bg-gray-900/50 p-6 rounded-xl border border-gray-800">
                  <h3 className="text-xl font-semibold mb-4 text-purple-400">1. Upload Tops</h3>
                  <p className="text-sm text-gray-400 mb-4">Shirts, T-shirts, Blouses, Jackets</p>
                  <ImageUpload
                    onImagesChange={handleTopsChange}
                    onOpenLibrary={() => handleLibraryOpen('top')}
                    maxImages={8}
                    forcedType="top"
                    externalItems={tops}
                  />
                  <div className="mt-2 text-right text-xs text-gray-500">
                    {tops.length} items
                  </div>
                </div>

                {/* BOTTOMS SECTION */}
                <div className="bg-gray-900/50 p-6 rounded-xl border border-gray-800">
                  <h3 className="text-xl font-semibold mb-4 text-blue-400">2. Upload Bottoms</h3>
                  <p className="text-sm text-gray-400 mb-4">Pants, Jeans, Skirts, Shorts</p>
                  <ImageUpload
                    onImagesChange={handleBottomsChange}
                    onOpenLibrary={() => handleLibraryOpen('bottom')}
                    maxImages={8}
                    forcedType="bottom"
                    externalItems={bottoms}
                  />
                  <div className="mt-2 text-right text-xs text-gray-500">
                    {bottoms.length} items
                  </div>
                </div>
              </div>

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
                  disabled={tops.length === 0 || bottoms.length === 0}
                  className="flex-1 rounded-xl h-12 text-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  data-testid="button-next-upload"
                >
                  Continue ({tops.length + bottoms.length} items)
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
                    Generating guaranteed outfits from your {tops.length} tops and {bottoms.length} bottoms.
                  </p>

                  <Button
                    onClick={handleGetAIRecommendations}
                    disabled={isLoadingAI}
                    className="w-full gap-2 rounded-xl h-12 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    data-testid="button-ai-recommendations"
                  >
                    {isLoadingAI ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        AI is mixing match...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4" />
                        Generate Outfits
                      </>
                    )}
                  </Button>

                  {/* AI Error Alert */}
                  {aiError && (
                    <Alert variant="destructive" className="mt-4">
                      <AlertDescription>{aiError}</AlertDescription>
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
                    ? `Generated using your ${tops.length} tops and ${bottoms.length} bottoms`
                    : `Here are our top recommendations for ${selectedOccasion} occasions`}
                </p>
              </div>

              {/* AI-Generated Outfits Section */}
              {mlRecommendations && mlRecommendations.recommendations.length > 0 && (
                <div className="mb-12">
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

              {/* Fallback */}
              {(!mlRecommendations || mlRecommendations.recommendations.length === 0) && (
                <div className="mb-8">
                  <Alert className="mt-4">
                    <AlertDescription>
                      No valid outfit combinations found. Please try adding more items.
                    </AlertDescription>
                  </Alert>
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
          filterType={libraryMode}
        />
      )}
    </div>
  );
}
