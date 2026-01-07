"""
Test the rebuilt model on ALL images in Inputs folder
"""
import tensorflow as tf
import numpy as np
import os

# Use the TRAINED model
MODEL_PATH = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_trained.keras"
INPUTS_DIR = r"D:\Studiess\Project\Clazzy\Inputs"

print("=" * 60)
print("TESTING MODEL ON ALL INPUTS")
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

# Test all images in Inputs
print("\n" + "=" * 60)
print("TESTING ALL IMAGES IN INPUTS FOLDER")
print("=" * 60 + "\n")

files = os.listdir(INPUTS_DIR)
results = []

for f in files:
    path = os.path.join(INPUTS_DIR, f)
    if os.path.isfile(path):
        try:
            pred_class, confidence, raw = predict_image(path)
            results.append((f, pred_class, confidence, raw))
            
            # Determine expected type from filename
            name_lower = f.lower()
            if 'shirt' in name_lower or 'top' in name_lower or 'tshirt' in name_lower:
                expected = 'top'
            elif 'pant' in name_lower or 'short' in name_lower or 'jean' in name_lower or 'bottom' in name_lower:
                expected = 'bottom'
            else:
                expected = '???'
            
            match = "✅" if pred_class == expected else "❌" if expected != '???' else "❓"
            print(f"{match} {f:25s} -> {pred_class:6s} (raw: {raw:.4f}) [expected: {expected}]")
        except Exception as e:
            print(f"❌ {f:25s} -> ERROR: {e}")

# Summary
print("\n" + "=" * 60)
print("ACCURACY ANALYSIS")
print("=" * 60)

# Calculate accuracy
expected_tops = [r for r in results if 'shirt' in r[0].lower() or 'top' in r[0].lower()]
expected_bottoms = [r for r in results if 'pant' in r[0].lower() or 'short' in r[0].lower()]

top_correct = sum(1 for r in expected_tops if r[1] == 'top')
bottom_correct = sum(1 for r in expected_bottoms if r[1] == 'bottom')

print(f"\nExpected Tops: {len(expected_tops)} items")
print(f"  Correctly classified as TOP: {top_correct}")
for r in expected_tops:
    status = "✅" if r[1] == 'top' else "❌"
    print(f"    {status} {r[0]} -> {r[1]} (raw: {r[3]:.4f})")

print(f"\nExpected Bottoms: {len(expected_bottoms)} items")
print(f"  Correctly classified as BOTTOM: {bottom_correct}")
for r in expected_bottoms:
    status = "✅" if r[1] == 'bottom' else "❌"
    print(f"    {status} {r[0]} -> {r[1]} (raw: {r[3]:.4f})")

total = len(expected_tops) + len(expected_bottoms)
correct = top_correct + bottom_correct
if total > 0:
    accuracy = (correct / total) * 100
    print(f"\nOverall Accuracy: {correct}/{total} = {accuracy:.1f}%")
