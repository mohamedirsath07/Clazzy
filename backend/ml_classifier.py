"""
MODEL 1: Clothing Classification Model (Top/Bottom Classifier)
===================================================================
Custom-trained ML model for binary clothing classification.

Purpose: Determine if a clothing item is a TOP or BOTTOM.
Technology: Custom TensorFlow/Keras model trained on clothing dataset
Model file: clothing_classifier_model.keras or .h5
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
IMAGE_SIZE = (150, 150)
CLASS_NAMES = ['bottom', 'top']  # Index 0 = bottom, Index 1 = top

# Get model path relative to this file
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH_KERAS = os.path.join(MODEL_DIR, 'clothing_classifier_model.keras')
MODEL_PATH_H5 = os.path.join(MODEL_DIR, 'clothing_classifier_model.h5')


def build_model():
    """
    Rebuild the model architecture matching the trained model.
    Uses EfficientNetB0 as base with custom classification head.
    """
    # Input layer
    inputs = tf.keras.Input(shape=(150, 150, 3))
    
    # Base model - EfficientNetB0
    base_model = tf.keras.applications.EfficientNetB0(
        include_top=False,
        weights=None,  # We'll load weights from the saved model
        input_tensor=inputs
    )
    
    # Classification head
    x = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Dense(128, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
    
    model = tf.keras.Model(inputs, outputs)
    return model


class ClothingClassifier:
    """
    Custom-trained clothing classifier for TOP/BOTTOM detection.
    Uses a TensorFlow/Keras model with sigmoid output for binary classification.
    """
    
    def __init__(self):
        """Initialize and load the custom-trained model once at startup"""
        print("🔄 Loading Custom Clothing Classifier...")
        
        # Determine which model file to use (.h5 preferred for compatibility)
        model_path = None
        if os.path.exists(MODEL_PATH_H5):
            model_path = MODEL_PATH_H5  # Try H5 first (more compatible)
        elif os.path.exists(MODEL_PATH_KERAS):
            model_path = MODEL_PATH_KERAS
        else:
            raise FileNotFoundError(
                f"Model file not found. Please ensure one of these files is in the backend directory:\n"
                f"  - clothing_classifier_model.h5\n"
                f"  - clothing_classifier_model.keras"
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
        
        # Strategy 1: For H5 files, rebuild architecture and load weights first (most reliable)
        if model_path.endswith('.h5'):
            try:
                model = build_model()
                model.load_weights(model_path)
                print("   ✅ Loaded H5 weights into rebuilt architecture")
                return model
            except Exception as e:
                print(f"   H5 weight loading failed: {str(e)[:50]}...")
            
            # Try with skip_mismatch
            try:
                model = build_model()
                model.load_weights(model_path, by_name=True, skip_mismatch=True)
                print("   ✅ Loaded H5 weights with skip_mismatch")
                return model
            except Exception as e:
                print(f"   H5 skip_mismatch loading failed: {str(e)[:50]}...")
        
        # Strategy 2: Try direct loading with compile=False
        try:
            model = tf.keras.models.load_model(model_path, compile=False)
            print("   ✅ Loaded model directly")
            return model
        except Exception as e:
            print(f"   Direct loading failed: {str(e)[:50]}...")
        
        # Strategy 3: Use custom object scope
        try:
            with tf.keras.utils.custom_object_scope({}):
                model = tf.keras.models.load_model(model_path, compile=False)
            print("   ✅ Loaded with custom object scope")
            return model
        except Exception as e:
            print(f"   Custom scope loading failed: {str(e)[:50]}...")
        
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
