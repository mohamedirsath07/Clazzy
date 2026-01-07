"""
Test loading the .keras model format
"""
import tensorflow as tf
import numpy as np
import os

MODEL_PATH = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model.keras"

print("=" * 60)
print("ATTEMPTING TO LOAD .KERAS MODEL")
print("=" * 60)

try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("✅ Successfully loaded .keras model!")
    print(f"\nModel input shape: {model.input_shape}")
    print(f"Model output shape: {model.output_shape}")
    model.summary()
    
    # Test with dummy data
    input_h = model.input_shape[1]
    input_w = model.input_shape[2]
    print(f"\n\nTesting with dummy input ({input_h}x{input_w}x3)...")
    
    # Test multiple random inputs to see if outputs vary
    for i in range(5):
        dummy = np.random.random((1, input_h, input_w, 3)).astype(np.float32)
        pred = model.predict(dummy, verbose=0)[0][0]
        print(f"  Random input {i+1}: {pred:.4f}")
    
    print("\n✅ Model is working correctly!")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
