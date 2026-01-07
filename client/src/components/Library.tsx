import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Library as LibraryIcon, Trash2, Upload, AlertCircle, Check, X, Plus, Image as ImageIcon, HardDrive, Cloud, Loader2 } from "lucide-react";
import { getLibraryImages, deleteImageFromFirebase, isFirebaseConfigured, uploadImageToFirebase, getStorageType } from "@/lib/firebase";
import { detectClothingType } from "@/lib/mlApi";
import type { ClothingItem } from "@shared/schema";

interface LibraryProps {
  onSelectImages: (items: ClothingItem[]) => void;
  onClose: () => void;
}

export function Library({ onSelectImages, onClose }: LibraryProps) {
  const [libraryImages, setLibraryImages] = useState<Array<{url: string, name: string, path: string}>>([]);
  const [selectedImages, setSelectedImages] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConfigured, setIsConfigured] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({ current: 0, total: 0 });
  const [isDetecting, setIsDetecting] = useState(false);
  const [storageType, setStorageType] = useState<'firebase' | 'local'>('local');

  useEffect(() => {
    loadLibraryImages();
    setIsConfigured(isFirebaseConfigured());
    setStorageType(getStorageType());
  }, []);

  const loadLibraryImages = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const images = await getLibraryImages();
      setLibraryImages(images);
    } catch (err) {
      setError('Failed to load library. Please check your Firebase configuration.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleSelect = (imageUrl: string) => {
    const newSelected = new Set(selectedImages);
    if (newSelected.has(imageUrl)) {
      newSelected.delete(imageUrl);
    } else {
      newSelected.add(imageUrl);
    }
    setSelectedImages(newSelected);
  };

  const handleDeleteImage = async (imagePath: string) => {
    try {
      await deleteImageFromFirebase(imagePath);
      setLibraryImages(libraryImages.filter(img => img.path !== imagePath));
    } catch (err) {
      alert('Failed to delete image. Please try again.');
      console.error(err);
    }
  };

  const handleUseSelected = async () => {
    if (selectedImages.size === 0) return;
    
    setIsDetecting(true);
    
    try {
      // Create items and detect types using ML
      const selectedItems: ClothingItem[] = [];
      const urls = Array.from(selectedImages);
      
      for (let index = 0; index < urls.length; index++) {
        const url = urls[index];
        const image = libraryImages.find(img => img.url === url);
        
        // Try to detect type using ML
        let detectedType: string = 'other';
        let detectedConfidence: number = 0;
        try {
          // Fetch the image and convert to File for ML detection
          const response = await fetch(url);
          const blob = await response.blob();
          const file = new File([blob], image?.name || `image-${index}.jpg`, { type: blob.type });
          
          const mlResult = await detectClothingType(file);
          detectedType = mlResult.predicted_type;
          detectedConfidence = mlResult.confidence;
          console.log(`📸 Library item ${index + 1}: detected as "${detectedType}" (${(detectedConfidence * 100).toFixed(0)}%)`);
        } catch (err) {
          console.warn(`⚠️ ML detection failed for library image ${index}, using 'other'`, err);
        }
        
        selectedItems.push({
          id: `library-${Date.now()}-${index}`,
          imageUrl: url,
          type: detectedType,
          detectedType: detectedType,
          confidence: detectedConfidence  // IMPORTANT: Pass confidence for threshold filtering
        });
      }
      
      onSelectImages(selectedItems);
      onClose();
    } catch (err) {
      console.error('Failed to process selected images:', err);
      setError('Failed to detect clothing types. Please try again.');
    } finally {
      setIsDetecting(false);
    }
  };

  const handleBulkUpload = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadProgress({ current: 0, total: files.length });
    setError(null);

    const uploadedUrls: Array<{url: string, name: string, path: string}> = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      if (!file.type.startsWith('image/')) {
        console.warn(`Skipping non-image file: ${file.name}`);
        continue;
      }

      try {
        setUploadProgress({ current: i + 1, total: files.length });
        const url = await uploadImageToFirebase(file);
        
        // Add to uploaded list
        uploadedUrls.push({
          url,
          name: file.name,
          path: `users/default/clothing/${Date.now()}_${file.name}`
        });
      } catch (err) {
        console.error(`Failed to upload ${file.name}:`, err);
      }
    }

    // Reload library to get all images including newly uploaded
    await loadLibraryImages();
    
    setIsUploading(false);
    setUploadProgress({ current: 0, total: 0 });

    if (uploadedUrls.length > 0) {
      // Show success message
      const message = `Successfully uploaded ${uploadedUrls.length} image${uploadedUrls.length > 1 ? 's' : ''} to your library!`;
      console.log(message);
    }
  }, []);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleBulkUpload(e.target.files);
  };

  if (!isConfigured) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <Card className="max-w-2xl w-full p-6 max-h-[90vh] overflow-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <LibraryIcon className="h-6 w-6" />
              Image Library - Error
            </h2>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          <Alert className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Storage Initialization Failed</strong>
              <br />
              <br />
              Unable to initialize storage. Please try refreshing the page or check your browser settings.
            </AlertDescription>
          </Alert>

          <Button onClick={onClose} className="w-full">
            Close
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="max-w-6xl w-full p-6 max-h-[90vh] overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <LibraryIcon className="h-6 w-6" />
              My Clothing Library
            </h2>
            <div className="flex items-center gap-2 mt-1">
              {storageType === 'local' ? (
                <Badge variant="secondary" className="text-xs flex items-center gap-1">
                  <HardDrive className="h-3 w-3" />
                  Local Storage
                </Badge>
              ) : (
                <Badge variant="secondary" className="text-xs flex items-center gap-1">
                  <Cloud className="h-3 w-3" />
                  Cloud Storage
                </Badge>
              )}
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Upload Progress Bar */}
        {isUploading && (
          <Card className="mb-4 p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Uploading images to library...</span>
                <span className="text-muted-foreground">
                  {uploadProgress.current} / {uploadProgress.total}
                </span>
              </div>
              <Progress 
                value={(uploadProgress.current / uploadProgress.total) * 100} 
                className="h-2"
              />
            </div>
          </Card>
        )}

        {/* Bulk Upload Button */}
        <div className="mb-6">
          <input
            type="file"
            id="library-bulk-upload"
            className="hidden"
            accept="image/*"
            multiple
            onChange={handleFileInputChange}
            disabled={isUploading}
          />
          <label htmlFor="library-bulk-upload">
            <Button 
              className="w-full gap-2" 
              disabled={isUploading}
              asChild
            >
              <span>
                <Plus className="h-4 w-4" />
                {isUploading ? 'Uploading...' : 'Add Images to Library'}
              </span>
            </Button>
          </label>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Upload multiple images at once to build your wardrobe library
          </p>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading your library...</p>
          </div>
        ) : libraryImages.length === 0 ? (
          <div className="text-center py-12">
            <LibraryIcon className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-xl font-semibold mb-2">Your library is empty</h3>
            <p className="text-muted-foreground mb-4">
              Upload images with the "Save to Library" option to build your collection
            </p>
          </div>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                {libraryImages.length} items in library • {selectedImages.size} selected
              </p>
              {selectedImages.size > 0 && (
                <Button onClick={handleUseSelected} className="gap-2" disabled={isDetecting}>
                  {isDetecting ? (
                    <><Loader2 className="h-4 w-4 animate-spin" /> Detecting types...</>
                  ) : (
                    <><Check className="h-4 w-4" /> Use {selectedImages.size} Selected</>
                  )}
                </Button>
              )}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {libraryImages.map((image) => (
                <div
                  key={image.path}
                  className={`relative group rounded-lg overflow-hidden border-2 transition-all cursor-pointer ${
                    selectedImages.has(image.url)
                      ? 'border-primary ring-2 ring-primary'
                      : 'border-transparent hover:border-gray-300'
                  }`}
                  onClick={() => handleToggleSelect(image.url)}
                >
                  <img
                    src={image.url}
                    alt={image.name}
                    className="w-full h-48 object-cover"
                  />
                  
                  {selectedImages.has(image.url) && (
                    <div className="absolute top-2 right-2 bg-primary text-white rounded-full p-1">
                      <Check className="h-4 w-4" />
                    </div>
                  )}

                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="destructive"
                      size="sm"
                      className="w-full gap-2"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteImage(image.path);
                      }}
                    >
                      <Trash2 className="h-3 w-3" />
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        <div className="mt-6 flex gap-2">
          <Button variant="outline" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          {selectedImages.size > 0 && (
            <Button onClick={handleUseSelected} className="flex-1 gap-2" disabled={isDetecting}>
              {isDetecting ? (
                <><Loader2 className="h-4 w-4 animate-spin" /> Detecting clothing types...</>
              ) : (
                <><Upload className="h-4 w-4" /> Use {selectedImages.size} Selected Images</>
              )}
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}
