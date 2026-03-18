import { useEffect, useRef } from "react";
import { ArrowRight, Palette, Bot, Shirt, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import gsap from "gsap";

interface HeroProps {
  onGetStarted: () => void;
  onViewHistory: () => void;
}

export function Hero({ onGetStarted, onViewHistory }: HeroProps) {
  const heroRef = useRef<HTMLElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const buttonsRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Create a timeline for sequential animations
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

      // Animate title
      tl.fromTo(
        titleRef.current,
        { opacity: 0, y: 50 },
        { opacity: 1, y: 0, duration: 0.8 }
      );

      // Animate subtitle
      tl.fromTo(
        subtitleRef.current,
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.6 },
        "-=0.4"
      );

      // Animate buttons
      tl.fromTo(
        buttonsRef.current?.children || [],
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, stagger: 0.1 },
        "-=0.3"
      );

      // Animate feature cards
      tl.fromTo(
        cardsRef.current?.children || [],
        { opacity: 0, y: 40 },
        { opacity: 1, y: 0, duration: 0.6, stagger: 0.15 },
        "-=0.2"
      );

    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={heroRef} className="relative overflow-hidden bg-black py-24 md:py-32 lg:py-40">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-black to-blue-900/20" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-900/30 via-transparent to-transparent" />

      {/* Animated floating particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="container relative mx-auto px-4 text-center">
        {/* Main heading */}
        <h1
          ref={titleRef}
          className="mb-6 text-6xl font-black tracking-tight text-white md:text-7xl lg:text-8xl opacity-0"
          data-testid="text-hero-title"
        >
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
            Clazzy
          </span>
        </h1>

        {/* Subtitle */}
        <p
          ref={subtitleRef}
          className="mx-auto mb-12 max-w-3xl text-lg leading-relaxed text-gray-300 md:text-xl opacity-0"
          data-testid="text-hero-subtitle"
        >
          Your intelligent fashion companion. Get AI-powered outfit recommendations, perfect color combinations, and complete wardrobe styling for any occasion.
        </p>

        {/* CTA Buttons */}
        <div ref={buttonsRef} className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button
            size="lg"
            className="gap-2 rounded-full h-14 px-12 text-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 hover:scale-105 transition-transform duration-300"
            onClick={onGetStarted}
            data-testid="button-get-started"
          >
            Get Started
            <ArrowRight className="h-5 w-5" />
          </Button>

          <Button
            variant="outline"
            size="lg"
            className="gap-2 rounded-full h-14 px-8 text-lg border-purple-500/50 text-purple-400 hover:bg-purple-500/10 hover:text-purple-300 hover:scale-105 transition-transform duration-300"
            onClick={onViewHistory}
            data-testid="button-view-history"
          >
            <History className="h-5 w-5" />
            View Saved Collection
          </Button>
        </div>

        {/* Feature cards */}
        <div ref={cardsRef} className="mt-20 grid gap-6 md:grid-cols-3 max-w-5xl mx-auto">
          {/* Color Theory */}
          <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm hover:bg-white/10 hover:border-purple-500/50 hover:scale-[1.02] transition-all duration-300 cursor-pointer">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative">
              <div className="mb-4 flex justify-center">
                <Palette className="h-16 w-16 text-purple-500 stroke-[2] group-hover:scale-110 transition-transform duration-500" />
              </div>
              <h3 className="mb-3 text-xl font-bold text-white">Color Theory</h3>
              <p className="text-sm leading-relaxed text-gray-400">
                Perfect color combinations based on professional color theory
              </p>
            </div>
          </div>

          {/* AI Powered */}
          <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm hover:bg-white/10 hover:border-blue-500/50 hover:scale-[1.02] transition-all duration-300 cursor-pointer">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative">
              <div className="mb-4 flex justify-center">
                <Bot className="h-16 w-16 text-blue-500 stroke-[2] group-hover:scale-110 transition-transform duration-500" />
              </div>
              <h3 className="mb-3 text-xl font-bold text-white">AI Powered</h3>
              <p className="text-sm leading-relaxed text-gray-400">
                Machine learning recommendations based on visual similarity
              </p>
            </div>
          </div>

          {/* Complete Outfits */}
          <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm hover:bg-white/10 hover:border-pink-500/50 hover:scale-[1.02] transition-all duration-300 cursor-pointer">
            <div className="absolute inset-0 bg-gradient-to-br from-pink-600/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative">
              <div className="mb-4 flex justify-center">
                <Shirt className="h-16 w-16 text-pink-500 stroke-[2] group-hover:scale-110 transition-transform duration-500" />
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
