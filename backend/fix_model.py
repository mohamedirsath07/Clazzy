"""
Script to properly load and test the H5 model file.
"""
import tensorflow as tf
import numpy as np
import os
import h5py

MODEL_PATH = r"D:\Studiess\Project\Clazzy\Fashion-Style\backend\clothing_classifier_model.h5"

print("=" * 60)
print("ATTEMPTING TO LOAD H5 MODEL")
print("=" * 60)

# First, let's see if the H5 file is a complete model or just weights
with h5py.File(MODEL_PATH, 'r') as f:
    has_model_config = 'model_config' in f.attrs
    has_keras_version = 'keras_version' in f.attrs
    print(f"Has model_config attribute: {has_model_config}")
    print(f"Has keras_version attribute: {has_keras_version}")
    
    if has_model_config:
        import json
        config = json.loads(f.attrs['model_config'])
        print(f"\nModel class: {config.get('class_name', 'Unknown')}")
        if 'config' in config and 'layers' in config['config']:
            print(f"Number of layers: {len(config['config']['layers'])}")
            print("\nLayer summary:")
            for i, layer in enumerate(config['config']['layers']):
                lclass = layer.get('class_name', 'Unknown')
                lname = layer.get('config', {}).get('name', 'unnamed')
                print(f"  {i}: {lclass} - {lname}")

print("\n" + "=" * 60)
print("LOADING WITH LEGACY FORMAT")
print("=" * 60)

# Try loading with legacy format
try:
    # Use legacy keras format for older H5 files
    model = tf.keras.models.load_model(
        MODEL_PATH, 
        compile=False,
        custom_objects=None
    )
    print("✅ Successfully loaded model!")
    print(f"\nModel Summary:")
    model.summary()
    
    # Test prediction with dummy input
    print("\n" + "=" * 60)
    print("TESTING PREDICTIONS")
    print("=" * 60)
    
    # Get input shape from the model
    input_shape = model.input_shape
    print(f"Model input shape: {input_shape}")
    
    # Create dummy input matching the shape
    if input_shape[1:] == (224, 224, 3):
        dummy_input = np.random.random((1, 224, 224, 3)).astype(np.float32)
    elif input_shape[1:] == (150, 150, 3):
        dummy_input = np.random.random((1, 150, 150, 3)).astype(np.float32)
    else:
        h, w, c = input_shape[1], input_shape[2], input_shape[3]
        dummy_input = np.random.random((1, h, w, c)).astype(np.float32)
    
    prediction = model.predict(dummy_input, verbose=0)
    print(f"Dummy prediction output: {prediction}")
    print(f"Output shape: {prediction.shape}")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    
    # Try with TF_USE_LEGACY_KERAS
    print("\n\nTrying with legacy keras...")
    import os
    os.environ['TF_USE_LEGACY_KERAS'] = '1'
    
    try:
        # Reload TF
        import importlib
        import tensorflow
        importlib.reload(tensorflow)
        from tensorflow import keras
        
        model = keras.models.load_model(MODEL_PATH, compile=False)
        print("✅ Successfully loaded model with legacy keras!")
        model.summary()
    except Exception as e2:
        print(f"❌ Legacy keras also failed: {e2}")
