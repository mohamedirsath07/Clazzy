"""
MODEL 1: Clothing Classification Model (Top/Bottom Classifier)
===================================================================
Custom-trained ML model for binary clothing classification.

Purpose: Determine if a clothing item is a TOP or BOTTOM.
Technology: Custom TensorFlow/Keras model trained on clothing dataset
Model file: clothing_classifier_trained.keras (MobileNetV2 backbone)
Input: Image bytes (resized to 150x150 RGB, normalized by 255)
Output: Binary classification with confidence score

Classification Logic:
- Sigmoid output: prediction > 0.5 → 'top', else → 'bottom'
- Model loaded once at startup for efficiency

Usage:
    classifier = ClothingClassifier()
    result = classifier.predict(image_bytes)
    # Returns: {'predicted_type': 'top', 'confidence': 0.89}
"""

import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import h5py

# Model configuration
IMAGE_SIZE = (150, 150)  # Model input size
CLASS_NAMES = ['bottom', 'top']  # Index 0 = bottom, Index 1 = top

# Get model path relative to this file
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
# Use the trained model (priority order: trained > v2 > original)
MODEL_PATH_TRAINED = os.path.join(MODEL_DIR, 'clothing_classifier_trained.keras')
MODEL_PATH_V2 = os.path.join(MODEL_DIR, 'clothing_classifier_model_v2.keras')
MODEL_PATH_KERAS = os.path.join(MODEL_DIR, 'clothing_classifier_model.keras')
MODEL_PATH_H5 = os.path.join(MODEL_DIR, 'clothing_classifier_model.h5')


def build_model():
    """
    Rebuild the model architecture matching the trained model.
    
    IMPORTANT: The H5 file contains weights for:
    - MobileNetV2 (224x224 input)
    - Dense head: GlobalAveragePooling2D → Dropout → Dense(128) → Dropout → Dense(1)
    
    This architecture MUST match the saved weights exactly!
    """
    # Create Sequential model matching the saved architecture
    model = tf.keras.Sequential([
        # Input layer
        tf.keras.layers.InputLayer(input_shape=(224, 224, 3)),
        
        # Base model - MobileNetV2 (matches the saved H5 file)
        tf.keras.applications.MobileNetV2(
            include_top=False,
            weights=None,  # We'll load the trained weights
            input_shape=(224, 224, 3),
            pooling=None
        ),
        
        # Classification head (matches saved layer names: global_average_pooling2d_1, dropout_4, dense_2, dropout_5, dense_3)
        tf.keras.layers.GlobalAveragePooling2D(name='global_average_pooling2d_1'),
        tf.keras.layers.Dropout(0.3, name='dropout_4'),
        tf.keras.layers.Dense(128, activation='relu', name='dense_2'),
        tf.keras.layers.Dropout(0.3, name='dropout_5'),
        tf.keras.layers.Dense(1, activation='sigmoid', name='dense_3'),
    ], name='sequential_3')
    
    return model


class ClothingClassifier:
    """
    Custom-trained clothing classifier for TOP/BOTTOM detection.
    Uses a TensorFlow/Keras model with sigmoid output for binary classification.
    """
    
    def __init__(self):
        """Initialize and load the custom-trained model once at startup"""
        print("🔄 Loading Custom Clothing Classifier...")
        
        # Determine which model file to use (order of preference)
        model_path = None
        
        # 1. First try the trained model (best accuracy)
        if os.path.exists(MODEL_PATH_TRAINED):
            model_path = MODEL_PATH_TRAINED
            print(f"   Using trained model: {MODEL_PATH_TRAINED}")
        # 2. Try the v2 model (rebuilt with imagenet weights)
        elif os.path.exists(MODEL_PATH_V2):
            model_path = MODEL_PATH_V2
            print(f"   Using v2 model: {MODEL_PATH_V2}")
        # 3. Fall back to original (may have compatibility issues)
        elif os.path.exists(MODEL_PATH_KERAS):
            model_path = MODEL_PATH_KERAS
        elif os.path.exists(MODEL_PATH_H5):
            model_path = MODEL_PATH_H5
        else:
            raise FileNotFoundError(
                f"Model file not found. Please ensure one of these files is in the backend directory:\n"
                f"  - clothing_classifier_trained.keras (recommended)\n"
                f"  - clothing_classifier_model.keras\n"
                f"  - clothing_classifier_model.h5"
            )
        
        # Try different loading strategies
        self.model = self._load_model(model_path)
        
        # Store class names for reference
        self.class_names = CLASS_NAMES
        self.image_size = IMAGE_SIZE
        
        print(f"✅ Custom Clothing Classifier loaded successfully!")
        print(f"   Model: {model_path}")
        print(f"   Input size: {IMAGE_SIZE[0]}x{IMAGE_SIZE[1]} RGB")
        print(f"   Classes: {CLASS_NAMES}")
    
    def _load_model(self, model_path):
        """Try multiple strategies to load the model"""
        
        # Strategy 1: Try direct loading first (works for trained model)
        try:
            model = tf.keras.models.load_model(model_path, compile=False)
            print("   ✅ Loaded model directly")
            return model
        except Exception as e:
            print(f"   Direct loading failed: {str(e)[:100]}...")
        
        # Strategy 2: Check if it's a complete model with config and try to fix incompatibilities
        try:
            with h5py.File(model_path, 'r') as f:
                if 'model_config' in f.attrs:
                    # It's a complete saved model, try to fix config issues
                    config_str = f.attrs['model_config']
                    if isinstance(config_str, bytes):
                        config_str = config_str.decode('utf-8')
                    config = json.loads(config_str)
                    
                    # Fix: Remove 'quantization_config' from Dense layers (incompatible with older Keras)
                    def clean_config(obj):
                        if isinstance(obj, dict):
                            # Remove problematic keys
                            obj.pop('quantization_config', None)
                            for key, value in obj.items():
                                clean_config(value)
                        elif isinstance(obj, list):
                            for item in obj:
                                clean_config(item)
                    
                    clean_config(config)
                    
                    # Recreate model from cleaned config
                    model = tf.keras.models.model_from_json(json.dumps(config))
                    model.load_weights(model_path)
                    print("   ✅ Loaded model with cleaned config (removed quantization_config)")
                    return model
        except Exception as e:
            print(f"   Config cleaning approach failed: {str(e)[:100]}...")
        
        # Strategy 3: Rebuild architecture and load weights by name
        try:
            model = build_model()
            model.load_weights(model_path, by_name=True)
            print("   ✅ Loaded H5 weights by name into rebuilt architecture")
            return model
        except Exception as e:
            print(f"   H5 weight loading by name failed: {str(e)[:100]}...")
        
        # Strategy 4: Rebuild architecture and load weights directly
        if model_path.endswith('.h5'):
            try:
                model = build_model()
                model.load_weights(model_path)
                print("   ✅ Loaded H5 weights into rebuilt architecture")
                return model
            except Exception as e:
                print(f"   H5 weight loading failed: {str(e)[:100]}...")
        
        # Strategy 5: Use custom object scope
        try:
            with tf.keras.utils.custom_object_scope({}):
                model = tf.keras.models.load_model(model_path, compile=False)
            print("   ✅ Loaded with custom object scope")
            return model
        except Exception as e:
            print(f"   Custom scope loading failed: {str(e)[:100]}...")
        
        raise RuntimeError(f"Failed to load model from {model_path}. Please re-save the model with compatible format.")
    
    def preprocess_image(self, img_bytes: bytes) -> np.ndarray:
        """
        Preprocess image exactly as during training.
        
        Args:
            img_bytes: Raw image bytes
            
        Returns:
            Preprocessed numpy array (1, 150, 150, 3) normalized to [0, 1]
        """
        # Load image from bytes
        img = Image.open(io.BytesIO(img_bytes))
        
        # Convert to RGB (handles RGBA, grayscale, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to model input size (150x150)
        img_resized = img.resize(self.image_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize by 255
        img_array = np.array(img_resized) / 255.0
        
        # Add batch dimension (1, 150, 150, 3)
        img_batch = np.expand_dims(img_array, axis=0)
        
        return img_batch
    
    def predict(self, img_bytes: bytes) -> dict:
        """
        Predict clothing type (top or bottom) from image bytes.
        
        Args:
            img_bytes: Raw image bytes
            
        Returns:
            {
                'predicted_type': str ('top' or 'bottom'),
                'confidence': float (0-1, prediction confidence),
                'raw_prediction': float (raw sigmoid output for debugging)
            }
        """
        # Preprocess image
        img_batch = self.preprocess_image(img_bytes)
        
        # Run prediction (sigmoid output)
        prediction = self.model.predict(img_batch, verbose=0)[0][0]
        
        # Apply classification logic: > 0.5 = top, <= 0.5 = bottom
        if prediction > 0.5:
            predicted_type = 'top'
            confidence = float(prediction)
        else:
            predicted_type = 'bottom'
            confidence = float(1 - prediction)
        
        return {
            'predicted_type': predicted_type,
            'confidence': confidence,
            'raw_prediction': float(prediction)  # For debugging/logging
        }
    
    def predict_from_path(self, image_path: str) -> tuple:
        """
        Predict clothing type from image file path.
        Convenience method matching the reference implementation.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            (predicted_type, confidence) tuple
        """
        with open(image_path, 'rb') as f:
            img_bytes = f.read()
        
        result = self.predict(img_bytes)
        return result['predicted_type'], result['confidence']


# Global classifier instance (singleton pattern for efficiency)
_classifier = None


def get_classifier() -> ClothingClassifier:
    """
    Get or create global classifier instance.
    Model is loaded once and reused across all requests.
    """
    global _classifier
    if _classifier is None:
        _classifier = ClothingClassifier()
    return _classifier
