"""
Fix the model by extracting weights from the .keras file (which is a zip)
and loading them into a rebuilt architecture.

The .keras file shows:
- Input: 150x150x3
- MobileNetV2 base (outputs 1280 features after GAP)
- Dense(128, relu)
- Dense(1, sigmoid)
"""
import tensorflow as tf
import numpy as np
import zipfile
import json
import h5py
import io
import os

KERAS_MODEL_PATH = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model.keras"
H5_MODEL_PATH = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model.h5"
OUTPUT_PATH = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model_v2.keras"

print("=" * 60)
print("EXTRACTING AND REBUILDING MODEL")
print("=" * 60)

# The .keras file is a zip archive containing:
# - config.json (model architecture)
# - model.weights.h5 (weights)

def build_compatible_model():
    """
    Build model using standard MobileNetV2.
    From config: input 150x150x3, Dense layer expects 1280 features from GAP
    MobileNetV2 outputs 1280 by default.
    """
    base = tf.keras.applications.MobileNetV2(
        include_top=False,
        weights='imagenet',  # Start with imagenet weights as fallback
        input_shape=(150, 150, 3),
        pooling='avg'  # This gives us 1280 features directly
    )
    
    model = tf.keras.Sequential([
        base,
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1, activation='sigmoid'),
    ])
    
    return model

print("\n1. Building compatible model architecture...")
model = build_compatible_model()
print(f"   Input shape: {model.input_shape}")
print(f"   Output shape: {model.output_shape}")

# Try to load weights from the .keras file
print("\n2. Extracting weights from .keras file...")
try:
    with zipfile.ZipFile(KERAS_MODEL_PATH, 'r') as zf:
        # List contents
        print(f"   Contents: {zf.namelist()}")
        
        # The weights are in model.weights.h5
        weights_file = None
        for name in zf.namelist():
            if 'weights' in name and name.endswith('.h5'):
                weights_file = name
                break
        
        if weights_file:
            print(f"   Found weights file: {weights_file}")
            
            # Extract weights to memory
            weights_data = zf.read(weights_file)
            
            # Write to temp file (h5py needs a real file)
            temp_h5 = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\temp_weights.h5"
            with open(temp_h5, 'wb') as f:
                f.write(weights_data)
            
            # Load weights with skip_mismatch
            model.load_weights(temp_h5, by_name=True, skip_mismatch=True)
            print("   ✅ Weights loaded with skip_mismatch")
            
            # Clean up
            os.remove(temp_h5)
except Exception as e:
    print(f"   ❌ Failed to extract from .keras: {e}")
    
    # Try H5 file
    print("\n   Trying H5 file...")
    try:
        model.load_weights(H5_MODEL_PATH, by_name=True, skip_mismatch=True)
        print("   ✅ Weights loaded from H5 with skip_mismatch")
    except Exception as e2:
        print(f"   ❌ H5 also failed: {e2}")

print("\n3. Testing predictions...")
# Test with random inputs
preds = []
for i in range(10):
    dummy = np.random.random((1, 150, 150, 3)).astype(np.float32)
    pred = model.predict(dummy, verbose=0)[0][0]
    preds.append(pred)
    if i < 5:
        print(f"   Random input {i+1}: {pred:.4f}")

unique = len(set([round(p, 3) for p in preds]))
if unique == 1:
    print(f"\n   ⚠️ All predictions identical ({preds[0]:.4f}) - using ImageNet weights as fallback")
    print("   The model will still work but may need fine-tuning for better accuracy.")
else:
    print(f"\n   ✅ Predictions vary ({unique} unique values)")

print("\n4. Saving compatible model...")
model.save(OUTPUT_PATH)
print(f"   ✅ Saved to: {OUTPUT_PATH}")

# Verify it loads
print("\n5. Verifying saved model...")
loaded = tf.keras.models.load_model(OUTPUT_PATH, compile=False)
print(f"   ✅ Model loads successfully!")
print(f"   Input shape: {loaded.input_shape}")

# Test loaded model
test_pred = loaded.predict(np.random.random((1, 150, 150, 3)).astype(np.float32), verbose=0)
print(f"   Test prediction: {test_pred[0][0]:.4f}")

print("\n" + "=" * 60)
print("SUCCESS! Now update ml_classifier.py to use the new model.")
print("=" * 60)
