"""
Test loading the export_package model
"""
import tensorflow as tf
import numpy as np

MODEL_PATH = r"D:\Studiess\Project\Clazzy\export_package\clothing_classifier_model.keras"

print("=" * 60)
print("ATTEMPTING TO LOAD EXPORT_PACKAGE MODEL")
print("=" * 60)

try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("✅ Successfully loaded model!")
    print(f"\nModel input shape: {model.input_shape}")
    print(f"Model output shape: {model.output_shape}")
    
    # Test with dummy data
    input_h = model.input_shape[1]
    input_w = model.input_shape[2]
    print(f"\nTesting with random inputs ({input_h}x{input_w}x3)...")
    
    # Test multiple random inputs
    for i in range(5):
        dummy = np.random.random((1, input_h, input_w, 3)).astype(np.float32)
        pred = model.predict(dummy, verbose=0)[0][0]
        print(f"  Random input {i+1}: {pred:.4f}")
    
    # Check if predictions vary
    preds = []
    for i in range(10):
        dummy = np.random.random((1, input_h, input_w, 3)).astype(np.float32)
        preds.append(model.predict(dummy, verbose=0)[0][0])
    
    unique_preds = len(set([round(p, 3) for p in preds]))
    if unique_preds == 1:
        print(f"\n⚠️ All predictions identical: {preds[0]:.4f}")
    else:
        print(f"\n✅ Predictions vary ({unique_preds} unique values) - model is functional!")
        
    # Copy to backend if successful
    print("\n" + "=" * 60)
    print("COPYING MODEL TO BACKEND")
    print("=" * 60)
    
    import shutil
    dst = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model_working.keras"
    shutil.copy(MODEL_PATH, dst)
    print(f"✅ Copied to: {dst}")
    
    # Verify copy
    model2 = tf.keras.models.load_model(dst, compile=False)
    print("✅ Copied model loads successfully!")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
