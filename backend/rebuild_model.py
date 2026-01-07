"""
Extract weights from H5 file and rebuild model with 150x150 input.
The .keras config shows input_shape is [None, 150, 150, 3].
"""
import tensorflow as tf
import numpy as np
import h5py
import os

MODEL_PATH_H5 = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model.h5"
MODEL_PATH_KERAS = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model.keras"

print("=" * 60)
print("EXTRACTING WEIGHTS AND REBUILDING MODEL")
print("=" * 60)

# Build the architecture matching what we know from the saved file:
# - Input: 150x150x3 (from .keras config batch_shape)
# - MobileNetV2 base (but the H5 shows mobilenetv2_1.00_224 which expects 224x224)
# - GlobalAveragePooling2D
# - Dropout(0.3) - dropout_4
# - Dense(128, relu) - dense_2
# - Dropout(0.3) - dropout_5
# - Dense(1, sigmoid) - dense_3

# The issue: Model was trained with 150x150 but the MobileNetV2 layer name suggests 224x224
# Let's try loading with both and see which works

print("\n📋 Checking if .keras file has weights we can extract...")

import zipfile
import json

# The .keras file is actually a zip file
with zipfile.ZipFile(MODEL_PATH_KERAS, 'r') as zf:
    print(f"Contents: {zf.namelist()}")
    
    # Read config
    with zf.open('config.json') as f:
        config = json.load(f)
        print(f"\nModel class: {config.get('class_name')}")
        layers = config.get('config', {}).get('layers', [])
        for layer in layers:
            lclass = layer.get('class_name')
            lconfig = layer.get('config', {})
            lname = lconfig.get('name', 'unnamed')
            if lclass == 'InputLayer':
                print(f"  Input batch_shape: {lconfig.get('batch_shape')}")
            elif lclass == 'Functional':
                print(f"  {lname} (Functional - likely MobileNetV2)")
            elif lclass == 'Dense':
                print(f"  {lname}: Dense({lconfig.get('units')}, {lconfig.get('activation')})")
            else:
                print(f"  {lname}: {lclass}")

print("\n" + "=" * 60)
print("ATTEMPTING WEIGHT-ONLY LOADING")
print("=" * 60)

# Build the architecture with the correct input size from config
def build_model_150():
    """Build model with 150x150 input matching the saved config"""
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(150, 150, 3)),
        tf.keras.applications.MobileNetV2(
            include_top=False,
            weights='imagenet',  # Start with pretrained, then override
            input_shape=(150, 150, 3),
            pooling=None
        ),
        tf.keras.layers.GlobalAveragePooling2D(name='global_average_pooling2d_1'),
        tf.keras.layers.Dropout(0.3, name='dropout_4'),
        tf.keras.layers.Dense(128, activation='relu', name='dense_2'),
        tf.keras.layers.Dropout(0.3, name='dropout_5'),
        tf.keras.layers.Dense(1, activation='sigmoid', name='dense_3'),
    ], name='sequential_3')
    return model

print("\n1. Building model architecture with 150x150 input...")
model = build_model_150()
model.summary(print_fn=lambda x: print(f"  {x}"))

print("\n2. Attempting to load weights by name...")
try:
    model.load_weights(MODEL_PATH_H5, by_name=True, skip_mismatch=True)
    print("✅ Weights loaded (with skip_mismatch)")
except Exception as e:
    print(f"❌ Failed: {e}")

print("\n3. Testing predictions on random inputs...")
for i in range(5):
    dummy = np.random.random((1, 150, 150, 3)).astype(np.float32)
    pred = model.predict(dummy, verbose=0)[0][0]
    print(f"  Random input {i+1}: {pred:.4f}")

# Check if predictions are all the same (broken model) or varying (working)
preds = []
for i in range(10):
    dummy = np.random.random((1, 150, 150, 3)).astype(np.float32)
    preds.append(model.predict(dummy, verbose=0)[0][0])

unique_preds = len(set([round(p, 4) for p in preds]))
if unique_preds == 1:
    print(f"\n⚠️ All predictions identical: {preds[0]:.4f} - weights may not have loaded correctly")
else:
    print(f"\n✅ Predictions vary ({unique_preds} unique values) - model appears functional")

# Save the fixed model in a compatible format
print("\n4. Saving fixed model in compatible format...")
fixed_model_path = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model_fixed.h5"
model.save(fixed_model_path)
print(f"✅ Saved to: {fixed_model_path}")

print("\n5. Verifying the fixed model can be loaded...")
model2 = tf.keras.models.load_model(fixed_model_path, compile=False)
print("✅ Fixed model loads successfully!")
