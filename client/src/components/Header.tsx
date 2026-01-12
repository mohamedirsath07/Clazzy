import { InstallButton } from '@/components/InstallPWA';

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-black/95 backdrop-blur supports-[backdrop-filter]:bg-black/80">
      <div className="container mx-auto flex h-20 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <img
              src="/Clazzy_Logo.jpg"
              alt="Clazzy Logo"
              className="h-12 w-12 rounded-lg object-cover"
            />
          </div>
          <h1 className="text-3xl font-black tracking-tight text-white" data-testid="text-app-name">
            Clazzy
          </h1>
        </div>

        {/* Install Button - shown when app is installable */}
        <div className="flex items-center gap-3">
          <InstallButton />
        </div>
      </div>
    </header>
  );
}

