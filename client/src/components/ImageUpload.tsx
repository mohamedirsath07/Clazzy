import { useCallback, useState } from "react";
import { Upload, X, Loader2, Library as LibraryIcon, Save, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import type { ClothingItem } from "@shared/schema";
import { detectClothingType, quickDetectTypeFromFilename } from "@/lib/mlApi";
import { uploadImageToFirebase, isFirebaseConfigured } from "@/lib/firebase";

interface ImageUploadProps {
  onImagesChange: (items: ClothingItem[]) => void;
  onOpenLibrary: () => void;
  maxImages?: number;
}

export function ImageUpload({ onImagesChange, onOpenLibrary, maxImages = 8 }: ImageUploadProps) {
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [detectingTypes, setDetectingTypes] = useState<Set<string>>(new Set());
  const [saveToLibrary, setSaveToLibrary] = useState(true);
  const [uploadingToFirebase, setUploadingToFirebase] = useState<Set<string>>(new Set());
  const [firebaseConfigured] = useState(isFirebaseConfigured());

  const handleFileSelect = useCallback(
    async (files: FileList | null) => {
      if (!files) return;

      const remainingSlots = maxImages - items.length;

      const filesToProcess = Array.from(files).slice(0, remainingSlots);

      for (const file of filesToProcess) {
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = async (e) => {
            const imageUrl = e.target?.result as string;
            const newItemId = Math.random().toString(36).substr(2, 9);
            
            // Quick filename check first
            let detectedType = quickDetectTypeFromFilename(file.name);
            
            // Create item with initial type
            const newItem: ClothingItem = {
              id: newItemId,
              imageUrl,
              type: detectedType || undefined,
              detectedType: detectedType || undefined,
            };
            
            setItems((prev) => {
              const updated = [...prev, newItem];
              onImagesChange(updated);
              return updated;
            });

            // Upload to Firebase if enabled and configured
            if (saveToLibrary && firebaseConfigured) {
              setUploadingToFirebase((prev) => new Set(prev).add(newItemId));
              
              try {
                const firebaseUrl = await uploadImageToFirebase(file);
                console.log('Image uploaded to Firebase:', firebaseUrl);
                
                // Update item with Firebase URL
                setItems((prev) => {
                  const updated = prev.map((item) =>
                    item.id === newItemId
                      ? { ...item, imageUrl: firebaseUrl }
                      : item
                  );
                  onImagesChange(updated);
                  return updated;
                });
              } catch (error) {
                console.error('Failed to upload to Firebase:', error);
                // Continue with local base64 URL
              } finally {
                setUploadingToFirebase((prev) => {
                  const next = new Set(prev);
                  next.delete(newItemId);
                  return next;
                });
              }
            }

            // If we couldn't detect from filename, use ML
            if (!detectedType) {
              setDetectingTypes((prev) => new Set(prev).add(newItemId));
              
              try {
                const mlResult = await detectClothingType(file);
                const mlType = mlResult.predicted_type;
                const mlConfidence = mlResult.confidence;
                
                console.log(`📸 ML Detection: ${file.name} → ${mlType} (${(mlConfidence * 100).toFixed(0)}%)`);
                
                setItems((prev) => {
                  const updated = prev.map((item) =>
                    item.id === newItemId
                      ? { 
                          ...item, 
                          type: mlType, 
                          detectedType: mlType,
                          confidence: mlConfidence  // IMPORTANT: Pass confidence for threshold filtering
                        }
                      : item
                  );
                  onImagesChange(updated);
                  return updated;
                });
              } catch (error) {
                console.error('ML type detection failed:', error);
              } finally {
                setDetectingTypes((prev) => {
                  const next = new Set(prev);
                  next.delete(newItemId);
                  return next;
                });
              }
            }
          };
          reader.readAsDataURL(file);
        }
      }
    },
    [items.length, maxImages, onImagesChange, saveToLibrary, firebaseConfigured]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      handleFileSelect(e.dataTransfer.files);
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const removeItem = (id: string) => {
    setItems((prev) => {
      const updated = prev.filter((item) => item.id !== id);
      onImagesChange(updated);
      return updated;
    });
  };

  const canAddMore = items.length < maxImages;

  return (
    <div className="space-y-6">
      {/* Library and Settings Bar */}
      <div className="flex items-center justify-between gap-4 p-4 rounded-lg border bg-card">
        <div className="flex items-center space-x-2">
          <Switch
            id="save-library"
            checked={saveToLibrary}
            onCheckedChange={setSaveToLibrary}
            disabled={!firebaseConfigured}
          />
          <Label htmlFor="save-library" className="text-sm">
            {firebaseConfigured ? (
              <>Save to library <Save className="inline h-3 w-3 ml-1" /></>
            ) : (
              <>Library (Configure Firebase)</>
            )}
          </Label>
        </div>
        
        <Button
          variant="outline"
          onClick={onOpenLibrary}
          className="gap-2"
        >
          <LibraryIcon className="h-4 w-4" />
          My Library
        </Button>
      </div>

      {/* Upload Options - Two Ways to Add Images */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Option 1: Upload from Device */}
        <Card className="p-0 overflow-hidden">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`relative transition-colors ${
              isDragging
                ? "bg-primary/10 border-primary"
                : "hover:bg-accent/50"
            }`}
          >
            <input
              type="file"
              id="file-upload"
              className="hidden"
              accept="image/*"
              multiple
              onChange={(e) => handleFileSelect(e.target.files)}
              disabled={!canAddMore}
            />
            <label
              htmlFor="file-upload"
              className={`flex min-h-48 ${canAddMore ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'} flex-col items-center justify-center p-6 text-center`}
            >
              <Upload className="mb-3 h-10 w-10 text-muted-foreground" />
              <p className="mb-1 font-semibold">Upload from Device</p>
              <p className="text-xs text-muted-foreground mb-2">
                Drag & drop or click to browse
              </p>
              <p className="text-xs text-muted-foreground">
                ({items.length}/{maxImages} images)
              </p>
            </label>
          </div>
        </Card>

        {/* Option 2: Choose from Library */}
        <Card className="p-0 overflow-hidden">
          <button
            onClick={onOpenLibrary}
            className="flex min-h-48 w-full cursor-pointer flex-col items-center justify-center p-6 text-center hover:bg-accent/50 transition-colors"
            disabled={!canAddMore}
          >
            <LibraryIcon className="mb-3 h-10 w-10 text-primary" />
            <p className="mb-1 font-semibold">Choose from Library</p>
            <p className="text-xs text-muted-foreground mb-2">
              Select from your saved wardrobe
            </p>
            <p className="text-xs text-primary font-medium">
              Browse Library →
            </p>
          </button>
        </Card>
      </div>

      {/* Uploaded Images Grid */}
      {items.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">Selected Images</h3>
            <span className="text-xs text-muted-foreground">
              {items.length} / {maxImages}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {items.map((item) => (
              <Card key={item.id} className="group relative aspect-square overflow-hidden p-0">
                <img
                  src={item.imageUrl}
                  alt="Clothing item"
                  className="h-full w-full object-cover"
                  data-testid={`image-clothing-${item.id}`}
                />
                
                {/* Upload Status Badge */}
                {uploadingToFirebase.has(item.id) && (
                  <div className="absolute top-2 left-2 rounded-md bg-blue-600 px-2 py-1 text-xs text-white backdrop-blur-sm flex items-center gap-1">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Saving...
                  </div>
                )}
                
                {/* ML Type Badge */}
                {item.detectedType && (
                  <div className="absolute bottom-2 left-2 rounded-md bg-black/70 px-2 py-1 text-xs text-white backdrop-blur-sm">
                    {detectingTypes.has(item.id) ? (
                      <span className="flex items-center gap-1">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Detecting...
                      </span>
                    ) : (
                      <span className="capitalize">{item.detectedType}</span>
                    )}
                  </div>
                )}
                
                <Button
                  variant="destructive"
                  size="icon"
                  className="absolute right-2 top-2 h-8 w-8 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => removeItem(item.id)}
                  data-testid={`button-remove-${item.id}`}
                >
                  <X className="h-4 w-4" />
                </Button>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
