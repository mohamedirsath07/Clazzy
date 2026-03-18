/**
 * Firebase Configuration with Local Storage Fallback
 * If Firebase is not configured, automatically uses browser's IndexedDB
 */

import { initializeApp } from 'firebase/app';
import { getStorage, ref, uploadBytes, getDownloadURL, listAll, deleteObject } from 'firebase/storage';
import type { FirebaseStorage } from 'firebase/storage';
import {
  uploadImageToLocal,
  getLocalLibraryImages,
  deleteImageFromLocal
} from './localLibrary';

// Firebase configuration
// IMPORTANT: Replace these with your actual Firebase project credentials
// Get these from: Firebase Console > Project Settings > General > Your apps
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
let app;
let storage: FirebaseStorage | undefined;
let useLocalStorage = false;

try {
  if (firebaseConfig.apiKey !== "YOUR_API_KEY") {
    app = initializeApp(firebaseConfig);
    storage = getStorage(app);
    console.log('✅ Firebase Storage initialized');
  } else {
    console.log('📦 Using local storage (IndexedDB) - Firebase not configured');
    useLocalStorage = true;
  }
} catch (error) {
  console.error('Firebase initialization failed:', error);
  console.log('📦 Falling back to local storage (IndexedDB)');
  useLocalStorage = true;
}

export { storage };

/**
 * Upload an image to storage (Firebase or Local)
 * @param file - Image file to upload
 * @param userId - User identifier (for organizing images)
 * @param clothingType - Optional clothing type tag (top/bottom)
 * @returns Download URL of uploaded image
 */
export async function uploadImageToFirebase(file: File, userId: string = 'default', clothingType?: 'top' | 'bottom'): Promise<string> {
  // Use local storage if Firebase is not configured
  if (useLocalStorage) {
    return await uploadImageToLocal(file, clothingType);
  }

  if (!storage) {
    throw new Error('Storage not initialized');
  }

  try {
    const timestamp = Date.now();
    // Include type in filename for Firebase (since we can't store metadata easily)
    const typePrefix = clothingType ? `${clothingType}_` : '';
    const fileName = `${typePrefix}${timestamp}_${file.name}`;
    const storageRef = ref(storage, `users/${userId}/clothing/${fileName}`);

    // Upload file
    const snapshot = await uploadBytes(storageRef, file);

    // Get download URL
    const downloadURL = await getDownloadURL(snapshot.ref);

    console.log('✅ Image uploaded to Firebase Storage');
    return downloadURL;
  } catch (error) {
    console.error('Error uploading image to Firebase:', error);
    throw error;
  }
}

/**
 * Get all images from library (Firebase or Local)
 * @param userId - User identifier
 * @returns Array of image URLs with type info
 */
export async function getLibraryImages(userId: string = 'default'): Promise<Array<{ url: string, name: string, path: string, clothingType?: 'top' | 'bottom' }>> {
  // Use local storage if Firebase is not configured
  if (useLocalStorage) {
    return await getLocalLibraryImages();
  }

  if (!storage) {
    throw new Error('Storage not initialized');
  }

  try {
    const listRef = ref(storage, `users/${userId}/clothing`);
    const result = await listAll(listRef);

    const imagePromises = result.items.map(async (itemRef) => {
      const url = await getDownloadURL(itemRef);
      // Try to extract type from filename (format: type_timestamp_name.ext)
      const fileName = itemRef.name;
      let clothingType: 'top' | 'bottom' | undefined = undefined;
      if (fileName.startsWith('top_')) clothingType = 'top';
      else if (fileName.startsWith('bottom_')) clothingType = 'bottom';

      return {
        url,
        name: itemRef.name,
        path: itemRef.fullPath,
        clothingType
      };
    });

    return await Promise.all(imagePromises);
  } catch (error) {
    console.error('Error fetching library images:', error);
    return [];
  }
}

/**
 * Delete an image from storage (Firebase or Local)
 * @param imagePath - Full path of the image in storage
 */
export async function deleteImageFromFirebase(imagePath: string): Promise<void> {
  // Use local storage if Firebase is not configured
  if (useLocalStorage) {
    return await deleteImageFromLocal(imagePath);
  }

  if (!storage) {
    throw new Error('Storage not initialized');
  }

  try {
    const imageRef = ref(storage, imagePath);
    await deleteObject(imageRef);
    console.log('✅ Image deleted from Firebase Storage');
  } catch (error) {
    console.error('Error deleting image:', error);
    throw error;
  }
}

/**
 * Check if storage is configured and ready
 * @returns true if storage is ready (Firebase or Local), false otherwise
 */
export function isFirebaseConfigured(): boolean {
  // Local storage is always available
  if (useLocalStorage) {
    return true;
  }

  // Check if Firebase is properly configured
  return storage !== undefined && firebaseConfig.apiKey !== "YOUR_API_KEY";
}

/**
 * Get storage type being used
 * @returns "firebase" or "local"
 */
export function getStorageType(): 'firebase' | 'local' {
  return useLocalStorage ? 'local' : 'firebase';
}
