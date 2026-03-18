import { useState, useEffect } from 'react';
import { useInstallApp } from '@/hooks/useInstallApp';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Download, X, Smartphone, Share, PlusSquare, MoreVertical } from 'lucide-react';

export function InstallPrompt() {
  const {
    isInstallable,
    isInstalled,
    isIOS,
    isMobile,
    promptInstall,
    dismissPrompt,
    showIOSInstructions,
    setShowIOSInstructions,
  } = useInstallApp();

  const [showBanner, setShowBanner] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  // Check if banner was dismissed recently
  useEffect(() => {
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    if (dismissed) {
      const dismissedTime = parseInt(dismissed);
      const sevenDays = 7 * 24 * 60 * 60 * 1000;
      if (Date.now() - dismissedTime < sevenDays) {
        setIsDismissed(true);
      }
    }
  }, []);

  // Show banner for mobile users after a delay
  useEffect(() => {
    if (isInstallable && isMobile && !isDismissed && !isInstalled) {
      const timer = setTimeout(() => {
        setShowBanner(true);
      }, 3000); // Show after 3 seconds
      return () => clearTimeout(timer);
    }
  }, [isInstallable, isMobile, isDismissed, isInstalled]);

  const handleInstall = async () => {
    const installed = await promptInstall();
    if (installed) {
      setShowBanner(false);
    }
  };

  const handleDismiss = () => {
    setShowBanner(false);
    dismissPrompt();
    setIsDismissed(true);
  };

  // Don't render anything if installed
  if (isInstalled) {
    return null;
  }

  return (
    <>
      {/* Mobile Install Banner */}
      {showBanner && !showIOSInstructions && (
        <div className="fixed bottom-4 left-4 right-4 z-50 md:left-auto md:right-4 md:max-w-md animate-in slide-in-from-bottom-4 duration-300">
          <Alert className="border-2 border-primary bg-gradient-to-br from-purple-50 to-blue-50 shadow-lg dark:from-purple-950/50 dark:to-blue-950/50 dark:border-purple-500/50">
            <Smartphone className="h-5 w-5 text-primary" />
            <AlertDescription>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <p className="font-semibold text-sm mb-1">Install Clazzy App</p>
                  <p className="text-xs text-muted-foreground mb-3">
                    Add to your home screen for quick access and the best experience!
                  </p>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={handleInstall}
                      className="gap-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    >
                      <Download className="h-3 w-3" />
                      Install
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleDismiss}
                    >
                      Later
                    </Button>
                  </div>
                </div>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-6 w-6 shrink-0"
                  onClick={handleDismiss}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* iOS Instructions Dialog */}
      <Dialog open={showIOSInstructions} onOpenChange={setShowIOSInstructions}>
        <DialogContent className="sm:max-w-md bg-gradient-to-br from-gray-900 to-gray-950 border-purple-500/30">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-white">
              <Smartphone className="h-5 w-5 text-purple-400" />
              Install Clazzy on iOS
            </DialogTitle>
            <DialogDescription className="text-gray-400">
              Follow these steps to add Clazzy to your home screen
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Step 1 */}
            <div className="flex items-start gap-4 p-3 rounded-lg bg-gray-800/50">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-purple-600 text-white text-sm font-bold">
                1
              </div>
              <div className="flex-1">
                <p className="font-medium text-white mb-1">Tap the Share button</p>
                <p className="text-sm text-gray-400">
                  Look for the <Share className="h-4 w-4 inline mx-1" /> icon at the bottom of Safari
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex items-start gap-4 p-3 rounded-lg bg-gray-800/50">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-purple-600 text-white text-sm font-bold">
                2
              </div>
              <div className="flex-1">
                <p className="font-medium text-white mb-1">Scroll and find "Add to Home Screen"</p>
                <p className="text-sm text-gray-400">
                  Look for <PlusSquare className="h-4 w-4 inline mx-1" /> Add to Home Screen
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex items-start gap-4 p-3 rounded-lg bg-gray-800/50">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-purple-600 text-white text-sm font-bold">
                3
              </div>
              <div className="flex-1">
                <p className="font-medium text-white mb-1">Tap "Add"</p>
                <p className="text-sm text-gray-400">
                  Confirm by tapping Add in the top right corner
                </p>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setShowIOSInstructions(false)}
              className="border-gray-700 hover:bg-gray-800"
            >
              Got it!
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

// Export a navbar button component for the Header
export function InstallButton() {
  const { isInstallable, isInstalled, isIOS, promptInstall } = useInstallApp();

  if (isInstalled || !isInstallable) {
    return null;
  }

  return (
    <Button
      size="sm"
      onClick={promptInstall}
      className="gap-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg shadow-purple-500/25"
    >
      <Download className="h-4 w-4" />
      <span className="hidden sm:inline">Install App</span>
      <span className="sm:hidden">Install</span>
    </Button>
  );
}
