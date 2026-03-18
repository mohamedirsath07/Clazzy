import { useState, useEffect, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
    prompt: () => Promise<void>;
    userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

interface UseInstallAppReturn {
    isInstallable: boolean;
    isInstalled: boolean;
    isIOS: boolean;
    isAndroid: boolean;
    isMobile: boolean;
    promptInstall: () => Promise<boolean>;
    dismissPrompt: () => void;
    showIOSInstructions: boolean;
    setShowIOSInstructions: (show: boolean) => void;
}

export function useInstallApp(): UseInstallAppReturn {
    const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null);
    const [isInstalled, setIsInstalled] = useState(false);
    const [showIOSInstructions, setShowIOSInstructions] = useState(false);

    // Detect platform
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream;
    const isAndroid = /Android/.test(navigator.userAgent);
    const isMobile = isIOS || isAndroid || /webOS|BlackBerry|Opera Mini|IEMobile/.test(navigator.userAgent);

    // Check if already installed as PWA
    useEffect(() => {
        const checkInstalled = () => {
            const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
            const isIOSStandalone = (navigator as any).standalone === true;
            setIsInstalled(isStandalone || isIOSStandalone);
        };

        checkInstalled();

        // Listen for display mode changes
        const mediaQuery = window.matchMedia('(display-mode: standalone)');
        mediaQuery.addEventListener('change', checkInstalled);

        return () => {
            mediaQuery.removeEventListener('change', checkInstalled);
        };
    }, []);

    // Listen for beforeinstallprompt event (Android/Chrome)
    useEffect(() => {
        const handleBeforeInstallPrompt = (e: Event) => {
            e.preventDefault();
            setInstallPrompt(e as BeforeInstallPromptEvent);
        };

        const handleAppInstalled = () => {
            setIsInstalled(true);
            setInstallPrompt(null);
        };

        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
        window.addEventListener('appinstalled', handleAppInstalled);

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
            window.removeEventListener('appinstalled', handleAppInstalled);
        };
    }, []);

    // Prompt install (Android/Chrome)
    const promptInstall = useCallback(async (): Promise<boolean> => {
        // For iOS, show instructions modal
        if (isIOS && !isInstalled) {
            setShowIOSInstructions(true);
            return false;
        }

        // For Android/Chrome with native prompt
        if (installPrompt) {
            try {
                await installPrompt.prompt();
                const { outcome } = await installPrompt.userChoice;

                if (outcome === 'accepted') {
                    setInstallPrompt(null);
                    return true;
                }
            } catch (error) {
                console.error('Install prompt error:', error);
            }
        }

        return false;
    }, [installPrompt, isIOS, isInstalled]);

    // Dismiss prompt with localStorage persistence
    const dismissPrompt = useCallback(() => {
        setShowIOSInstructions(false);
        localStorage.setItem('pwa-install-dismissed', Date.now().toString());
    }, []);

    // Check if installable
    const isInstallable = !isInstalled && (!!installPrompt || isIOS);

    return {
        isInstallable,
        isInstalled,
        isIOS,
        isAndroid,
        isMobile,
        promptInstall,
        dismissPrompt,
        showIOSInstructions,
        setShowIOSInstructions,
    };
}
