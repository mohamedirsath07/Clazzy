import { InstallButton } from '@/components/InstallPWA';
import { Button } from '@/components/ui/button';

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-background/60 supports-[backdrop-filter]:backdrop-blur-xl">
      <div className="container mx-auto flex h-20 items-center justify-between px-6 lg:px-12">
        <div className="flex items-center gap-4 group cursor-pointer">
          <div className="relative overflow-hidden rounded-xl">
            <img
              src="/Clazzy_Logo.jpg"
              alt="Clazzy Logo"
              className="h-10 w-10 object-cover group-hover:scale-110 transition-transform duration-500"
            />
          </div>
          <h1 className="text-2xl font-black tracking-tighter text-foreground" data-testid="text-app-name">Clazzy.</h1>
        </div>

        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
          <a className="hover:text-primary transition-colors" href="#features">Features</a>
          <a className="hover:text-primary transition-colors" href="#how-it-works">How it works</a>
          <a className="hover:text-primary transition-colors" href="#pricing">Pricing</a>
          <a className="hover:text-primary transition-colors" href="#about">About</a>
        </nav>

        <div className="flex items-center gap-4">
          <a className="hidden sm:inline text-sm font-medium text-muted-foreground hover:text-foreground transition-colors" href="#signin">Sign in</a>
          <Button size="sm" className="hidden sm:inline-flex rounded-xl bg-primary text-primary-foreground font-semibold px-5 py-2 hover:bg-primary/90 hover:scale-105 transition-all shadow-[0_0_20px_rgba(124,58,237,0.3)]">Get started</Button>
          <InstallButton />
        </div>
      </div>
    </header>
  );
}

