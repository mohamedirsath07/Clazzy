/**
 * Outfit History Storage (IndexedDB)
 * Stores saved outfit combinations for later reference
 */

export interface SavedOutfit {
    id: string;
    topUrl: string;
    bottomUrl: string;
    occasion: string;
    savedAt: number;
    score: number;
}

const DB_NAME = 'StyleAI_History';
const STORE_NAME = 'saved_outfits';
const DB_VERSION = 1;

/**
 * Initialize IndexedDB for outfit history
 */
function openHistoryDatabase(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = (event.target as IDBOpenDBRequest).result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: 'id' });
            }
        };
    });
}

/**
 * Save an outfit to history
 */
export async function saveOutfitToHistory(outfit: Omit<SavedOutfit, 'id' | 'savedAt'>): Promise<string> {
    const db = await openHistoryDatabase();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);

    const id = `outfit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const savedOutfit: SavedOutfit = {
        ...outfit,
        id,
        savedAt: Date.now()
    };

    store.add(savedOutfit);

    return new Promise((resolve, reject) => {
        transaction.oncomplete = () => {
            db.close();
            console.log('✅ Outfit saved to history');
            resolve(id);
        };

        transaction.onerror = () => {
            db.close();
            reject(transaction.error);
        };
    });
}

/**
 * Get all saved outfits from history
 */
export async function getOutfitHistory(): Promise<SavedOutfit[]> {
    try {
        const db = await openHistoryDatabase();
        const transaction = db.transaction([STORE_NAME], 'readonly');
        const store = transaction.objectStore(STORE_NAME);

        return new Promise((resolve, reject) => {
            const request = store.getAll();

            request.onsuccess = () => {
                db.close();
                // Sort by savedAt descending (newest first)
                const outfits = request.result.sort((a: SavedOutfit, b: SavedOutfit) => b.savedAt - a.savedAt);
                resolve(outfits);
            };

            request.onerror = () => {
                db.close();
                reject(request.error);
            };
        });
    } catch (error) {
        console.error('Error fetching outfit history:', error);
        return [];
    }
}

/**
 * Delete an outfit from history
 */
export async function deleteOutfitFromHistory(outfitId: string): Promise<void> {
    const db = await openHistoryDatabase();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);

    store.delete(outfitId);

    return new Promise((resolve, reject) => {
        transaction.oncomplete = () => {
            db.close();
            console.log('✅ Outfit deleted from history');
            resolve();
        };

        transaction.onerror = () => {
            db.close();
            reject(transaction.error);
        };
    });
}

/**
 * Clear all outfit history
 */
export async function clearOutfitHistory(): Promise<void> {
    const db = await openHistoryDatabase();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);

    store.clear();

    return new Promise((resolve, reject) => {
        transaction.oncomplete = () => {
            db.close();
            console.log('✅ Outfit history cleared');
            resolve();
        };

        transaction.onerror = () => {
            db.close();
            reject(transaction.error);
        };
    });
}
