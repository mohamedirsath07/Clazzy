/**
 * Local Library Storage (IndexedDB)
 * Fallback for when Firebase is not configured
 * Stores images in browser's IndexedDB for persistence
 */

interface LibraryImage {
  id: string;
  url: string;
  name: string;
  path: string;
  timestamp: number;
  clothingType?: 'top' | 'bottom'; // Type tag for filtering
}

const DB_NAME = 'StyleAI_Library';
const STORE_NAME = 'clothing_items';
const DB_VERSION = 1;

/**
 * Initialize IndexedDB
 */
function openDatabase(): Promise<IDBDatabase> {
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
 * Upload an image to local storage (IndexedDB)
 * @param file - Image file to upload
 * @param clothingType - Optional clothing type tag (top/bottom)
 * @returns Data URL of the image
 */
export async function uploadImageToLocal(file: File, clothingType?: 'top' | 'bottom'): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = async (e) => {
      try {
        const dataUrl = e.target?.result as string;
        const timestamp = Date.now();
        const id = `${timestamp}_${file.name}`;

        const imageData: LibraryImage = {
          id,
          url: dataUrl,
          name: file.name,
          path: `local/${id}`,
          timestamp,
          clothingType // Store the type tag
        };

        const db = await openDatabase();
        const transaction = db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);

        store.add(imageData);

        transaction.oncomplete = () => {
          db.close();
          console.log(`✅ Image saved to local library: ${file.name} (${clothingType || 'untyped'})`);
          resolve(dataUrl);
        };

        transaction.onerror = () => {
          db.close();
          reject(transaction.error);
        };
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

/**
 * Get all images from local library
 * @returns Array of image data including type
 */
export async function getLocalLibraryImages(): Promise<Array<{ url: string, name: string, path: string, clothingType?: 'top' | 'bottom' }>> {
  try {
    const db = await openDatabase();
    const transaction = db.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);

    return new Promise((resolve, reject) => {
      const request = store.getAll();

      request.onsuccess = () => {
        db.close();
        const images = request.result.map((item: LibraryImage) => ({
          url: item.url,
          name: item.name,
          path: item.path,
          clothingType: item.clothingType
        }));
        resolve(images);
      };

      request.onerror = () => {
        db.close();
        reject(request.error);
      };
    });
  } catch (error) {
    console.error('Error fetching local library:', error);
    return [];
  }
}

/**
 * Delete an image from local storage
 * @param imagePath - Path of the image (format: "local/[id]")
 */
export async function deleteImageFromLocal(imagePath: string): Promise<void> {
  try {
    const id = imagePath.replace('local/', '');
    const db = await openDatabase();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);

    store.delete(id);

    return new Promise((resolve, reject) => {
      transaction.oncomplete = () => {
        db.close();
        console.log('✅ Image deleted from local library');
        resolve();
      };

      transaction.onerror = () => {
        db.close();
        reject(transaction.error);
      };
    });
  } catch (error) {
    console.error('Error deleting image from local storage:', error);
    throw error;
  }
}

/**
 * Clear all images from local library
 */
export async function clearLocalLibrary(): Promise<void> {
  try {
    const db = await openDatabase();
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);

    store.clear();

    return new Promise((resolve, reject) => {
      transaction.oncomplete = () => {
        db.close();
        console.log('✅ Local library cleared');
        resolve();
      };

      transaction.onerror = () => {
        db.close();
        reject(transaction.error);
      };
    });
  } catch (error) {
    console.error('Error clearing local library:', error);
    throw error;
  }
}

/**
 * Get library statistics
 */
export async function getLocalLibraryStats(): Promise<{ count: number, estimatedSize: string }> {
  try {
    const images = await getLocalLibraryImages();
    const count = images.length;

    // Estimate size (rough calculation based on base64 data URLs)
    const totalSize = images.reduce((sum, img) => sum + img.url.length, 0);
    const sizeInMB = (totalSize / 1024 / 1024).toFixed(2);

    return {
      count,
      estimatedSize: `${sizeInMB} MB`
    };
  } catch (error) {
    return { count: 0, estimatedSize: '0 MB' };
  }
}
