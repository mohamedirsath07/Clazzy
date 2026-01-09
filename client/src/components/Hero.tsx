import { ArrowRight, Palette, Bot, Shirt, History } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeroProps {
  onGetStarted: () => void;
  onViewHistory: () => void;
}

export function Hero({ onGetStarted, onViewHistory }: HeroProps) {
  return (
    <section className="relative overflow-hidden bg-black py-24 md:py-32 lg:py-40">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-black to-blue-900/20" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-900/30 via-transparent to-transparent" />

      <div className="container relative mx-auto px-4 text-center">
        {/* Main heading */}
        <h1 className="mb-6 text-6xl font-black tracking-tight text-white md:text-7xl lg:text-8xl" data-testid="text-hero-title">
          Clazzy
        </h1>

        {/* Subtitle */}
        <p className="mx-auto mb-12 max-w-3xl text-lg leading-relaxed text-gray-300 md:text-xl" data-testid="text-hero-subtitle">
          Your intelligent fashion companion. Get AI-powered outfit recommendations, perfect color combinations, and complete wardrobe styling for any occasion.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button
            size="lg"
            className="gap-2 rounded-full h-14 px-12 text-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
            onClick={onGetStarted}
            data-testid="button-get-started"
          >
            Get Started
            <ArrowRight className="h-5 w-5" />
          </Button>

          <Button
            variant="outline"
            size="lg"
            className="gap-2 rounded-full h-14 px-8 text-lg border-purple-500/50 text-purple-400 hover:bg-purple-500/10 hover:text-purple-300"
            onClick={onViewHistory}
            data-testid="button-view-history"
          >
            <History className="h-5 w-5" />
            View Saved Collection
          </Button>
        </div>

        {/* Feature cards */}
        <div className="mt-20 grid gap-6 md:grid-cols-3 max-w-5xl mx-auto">
          {/* Color Theory */}
          <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative">
              <div className="mb-4 flex justify-center">
                <Palette className="h-16 w-16 text-purple-500 stroke-[2]" />
              </div>
              <h3 className="mb-3 text-xl font-bold text-white">Color Theory</h3>
              <p className="text-sm leading-relaxed text-gray-400">
                Perfect color combinations based on professional color theory
              </p>
            </div>
          </div>

          {/* AI Powered */}
          <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative">
              <div className="mb-4 flex justify-center">
                <Bot className="h-16 w-16 text-blue-500 stroke-[2]" />
              </div>
              <h3 className="mb-3 text-xl font-bold text-white">AI Powered</h3>
              <p className="text-sm leading-relaxed text-gray-400">
                Machine learning recommendations based on visual similarity
              </p>
            </div>
          </div>

          {/* Complete Outfits */}
          <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-pink-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative">
              <div className="mb-4 flex justify-center">
                <Shirt className="h-16 w-16 text-pink-500 stroke-[2]" />
              </div>
              <h3 className="mb-3 text-xl font-bold text-white">Complete Outfits</h3>
              <p className="text-sm leading-relaxed text-gray-400">
                Full outfit combinations tailored for specific occasions
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
