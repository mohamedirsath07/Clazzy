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
    <section ref={heroRef} className="relative overflow-hidden bg-background pt-24 pb-32 md:pt-32 md:pb-40 lg:pt-40 lg:pb-48">
      {/* Dynamic Animated Background Gradients (Gong/Atlassian inspired) */}
      <div className="absolute inset-0 bg-background" />
      
      {/* Animated Gradient Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-primary/20 blur-[120px] mix-blend-screen animate-pulse-slow pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-secondary/20 blur-[120px] mix-blend-screen animate-pulse-slow pointer-events-none" style={{ animationDelay: '2s' }} />
      <div className="absolute top-[20%] right-[10%] w-[30vw] h-[30vw] rounded-full bg-accent/20 blur-[100px] mix-blend-screen animate-float pointer-events-none" style={{ animationDelay: '1s' }} />

      {/* Grid Pattern overlay for Atlassian-like structure */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PHBhdGggZD0iTTAgMGg0MHY0MEgweiIgZmlsbD0ibm9uZSIvPjxwaGF0aCBkPSJNMCAwaDF2NDBIMHptMCAwaDQwdjFIMHoiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wMykiLz48L3N2Zz4=')] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_80%)] pointer-events-none" />

      <div className="container relative mx-auto px-6 lg:px-12 text-center z-10">
        {/* Main heading */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary text-sm font-medium mb-8 opacity-0" ref={el => titleRef.current = el as any}>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
          </span>
          Introducing Clazzy 2.0
        </div>

        <h1
          ref={titleRef}
          className="mb-8 text-5xl font-black tracking-tight text-foreground md:text-7xl lg:text-[5.5rem] leading-[1.1] opacity-0"
          data-testid="text-hero-title"
        >
          Your Intelligent <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-accent to-secondary animate-gradient-x">
            Fashion Companion.
          </span>
        </h1>

        {/* Subtitle */}
        <p
          ref={subtitleRef}
          className="mx-auto mb-12 max-w-2xl text-lg leading-relaxed text-muted-foreground md:text-xl font-body opacity-0"
          data-testid="text-hero-subtitle"
        >
          Elevate your daily style. Get AI-powered outfit recommendations, perfect color combinations, and complete wardrobe curation for every occasion.
        </p>

        {/* CTA Buttons */}
        <div ref={buttonsRef} className="flex flex-col sm:flex-row gap-5 justify-center items-center">
          <Button
            size="lg"
            className="gap-2 rounded-xl h-14 px-10 text-lg font-semibold bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-105 transition-all duration-300 shadow-[0_0_30px_rgba(124,58,237,0.4)]"
            onClick={onGetStarted}
            data-testid="button-get-started"
          >
            Start Styling
            <ArrowRight className="h-5 w-5" />
          </Button>

          <Button
            variant="outline"
            size="lg"
            className="gap-2 rounded-xl h-14 px-8 text-lg font-medium border-white/10 bg-white/5 hover:bg-white/10 backdrop-blur-md text-foreground hover:scale-105 transition-all duration-300"
            onClick={onViewHistory}
            data-testid="button-view-history"
          >
            <History className="h-5 w-5 text-muted-foreground" />
            View Wardrobe
          </Button>
        </div>

        {/* Feature cards */}
        <div ref={cardsRef} className="mt-28 grid gap-6 md:grid-cols-3 max-w-6xl mx-auto">
          {/* Color Theory */}
          <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-card/40 backdrop-blur-xl p-8 shadow-2xl hover:border-primary/40 transition-all duration-500 cursor-pointer text-left">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10">
              <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/20 text-primary ring-1 ring-primary/30 group-hover:scale-110 transition-transform duration-500">
                <Palette className="h-6 w-6 stroke-[2]" />
              </div>
              <h3 className="mb-3 text-2xl font-bold text-foreground">Color Theory</h3>
              <p className="text-base leading-relaxed text-muted-foreground font-body">
                Masterfully crafted color combinations rooted in professional design theory.
              </p>
            </div>
          </div>

          {/* AI Powered */}
          <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-card/40 backdrop-blur-xl p-8 shadow-2xl hover:border-accent/40 transition-all duration-500 cursor-pointer text-left mt-0 md:mt-8">
            <div className="absolute inset-0 bg-gradient-to-br from-accent/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10">
              <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-accent/20 text-accent ring-1 ring-accent/30 group-hover:scale-110 transition-transform duration-500">
                <Bot className="h-6 w-6 stroke-[2]" />
              </div>
              <h3 className="mb-3 text-2xl font-bold text-foreground">AI Powered</h3>
              <p className="text-base leading-relaxed text-muted-foreground font-body">
                Advanced machine learning algorithms that understand visual similarity.
              </p>
            </div>
          </div>

          {/* Complete Outfits */}
          <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-card/40 backdrop-blur-xl p-8 shadow-2xl hover:border-secondary/40 transition-all duration-500 cursor-pointer text-left">
            <div className="absolute inset-0 bg-gradient-to-br from-secondary/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10">
              <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-secondary/20 text-secondary ring-1 ring-secondary/30 group-hover:scale-110 transition-transform duration-500">
                <Shirt className="h-6 w-6 stroke-[2]" />
              </div>
              <h3 className="mb-3 text-2xl font-bold text-foreground">Curated Looks</h3>
              <p className="text-base leading-relaxed text-muted-foreground font-body">
                Full outfit combinations tailored perfectly for your specific occasions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
