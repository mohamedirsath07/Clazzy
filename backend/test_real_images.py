"""
Test the rebuilt model on actual clothing images
"""
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import glob

MODEL_PATH = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model_v2.keras"
UPLOADS_DIR = r"D:\Studiess\Project\Clazzy\Fashion-Style\client\public\uploads"
INPUTS_DIR = r"D:\Studiess\Project\Clazzy\Inputs"

print("=" * 60)
print("TESTING MODEL ON REAL IMAGES")
print("=" * 60)

# Load model
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print(f"Model loaded: {model.input_shape}")

def predict_image(img_path):
    """Predict top/bottom for an image"""
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=(150, 150))
    img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    prediction = model.predict(img_array, verbose=0)[0][0]
    predicted_class = 'top' if prediction > 0.5 else 'bottom'
    confidence = prediction if prediction > 0.5 else 1 - prediction
    
    return predicted_class, confidence, prediction

# Find test images
test_dirs = [UPLOADS_DIR, INPUTS_DIR]
image_files = []

for d in test_dirs:
    if os.path.exists(d):
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
            image_files.extend(glob.glob(os.path.join(d, ext)))
            image_files.extend(glob.glob(os.path.join(d, '**', ext), recursive=True))

print(f"\nFound {len(image_files)} test images")
print("=" * 60)

if not image_files:
    print("No test images found. Testing with synthetic patterns...")
    
    # Create synthetic test patterns
    # Black image (should be unpredictable)
    black = np.zeros((1, 150, 150, 3), dtype=np.float32)
    pred = model.predict(black, verbose=0)[0][0]
    print(f"Black image: {pred:.4f} -> {'top' if pred > 0.5 else 'bottom'}")
    
    # White image
    white = np.ones((1, 150, 150, 3), dtype=np.float32)
    pred = model.predict(white, verbose=0)[0][0]
    print(f"White image: {pred:.4f} -> {'top' if pred > 0.5 else 'bottom'}")
    
    # Random noise
    for i in range(5):
        noise = np.random.random((1, 150, 150, 3)).astype(np.float32)
        pred = model.predict(noise, verbose=0)[0][0]
        print(f"Random {i+1}: {pred:.4f} -> {'top' if pred > 0.5 else 'bottom'}")
else:
    # Test actual images
    results = []
    for img_path in image_files[:20]:  # Test up to 20 images
        try:
            pred_class, confidence, raw = predict_image(img_path)
            filename = os.path.basename(img_path)
            results.append((filename, pred_class, confidence, raw))
            print(f"{filename:40s} -> {pred_class:6s} ({raw:.4f})")
        except Exception as e:
            print(f"{os.path.basename(img_path):40s} -> ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    tops = [r for r in results if r[1] == 'top']
    bottoms = [r for r in results if r[1] == 'bottom']
    
    print(f"Tops detected: {len(tops)}")
    print(f"Bottoms detected: {len(bottoms)}")
    
    if tops:
        print(f"\nTop predictions:")
        for r in tops:
            print(f"  {r[0]:40s} (raw: {r[3]:.4f})")
    
    if bottoms:
        print(f"\nBottom predictions:")
        for r in bottoms:
            print(f"  {r[0]:40s} (raw: {r[3]:.4f})")
    
    # Check for bias
    raw_preds = [r[3] for r in results]
    avg_pred = np.mean(raw_preds)
    print(f"\nAverage raw prediction: {avg_pred:.4f}")
    if avg_pred < 0.3:
        print("⚠️ Model appears biased towards 'bottom'")
    elif avg_pred > 0.7:
        print("⚠️ Model appears biased towards 'top'")
    else:
        print("✅ Model appears reasonably balanced")
