import { createRoot } from "react-dom/client";
import { registerSW } from 'virtual:pwa-register';
import App from "./App";
import "./index.css";

// Register PWA service worker with auto-update
const updateSW = registerSW({
    onNeedRefresh() {
        // Show update notification when new content is available
        if (confirm('New version available! Reload to update?')) {
            updateSW(true);
        }
    },
    onOfflineReady() {
        console.log('App ready for offline use');
    },
});

createRoot(document.getElementById("root")!).render(<App />);
