import { ImageUpload } from "../ImageUpload";

export default function ImageUploadExample() {
  return (
    <div className="p-8">
      <ImageUpload 
        onImagesChange={(items) => console.log("Images updated:", items.length)} 
      />
    </div>
  );
}
