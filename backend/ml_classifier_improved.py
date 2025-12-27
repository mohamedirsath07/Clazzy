"""
Improved Clothing Classifier with Better Top/Bottom Detection
==============================================================
Uses a multi-signal approach to accurately distinguish clothing types:
1. Visual aspect ratio (height/width ratio from original image)
2. Color distribution patterns
3. ResNet50 deep features
4. Edge detection for garment shape

Key improvements:
- Preserves original image dimensions before classification
- Uses aspect ratio as primary signal (pants are taller, shirts are wider)
- Better handles edge cases
"""

import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io
import cv2

class ImprovedClothingClassifier:
    """
    Enhanced clothing classifier with better top/bottom detection
    """
    
    def __init__(self):
        """Initialize the classifier"""
        print("🔄 Loading Improved Clothing Classifier...")
        
        # Load ResNet50 for feature extraction
        self.base_model = ResNet50(
            weights='imagenet',
            include_top=False,
            pooling='avg',
            input_shape=(224, 224, 3)
        )
        self.base_model.trainable = False
        
        # Define categories
        self.categories = ['top', 'bottom', 'dress', 'shoes', 'blazer', 'other']
        
        print("✅ Improved Classifier initialized")
    
    def get_image_dimensions(self, img_bytes: bytes) -> tuple:
        """Get original image dimensions"""
        img = Image.open(io.BytesIO(img_bytes))
        return img.size  # (width, height)
    
    def analyze_aspect_ratio(self, width: int, height: int) -> dict:
        """
        Analyze image aspect ratio to determine garment type
        
        Key insight:
        - Pants/bottoms: Typically taller than wide (aspect_ratio < 0.8)
        - Shirts/tops: More square or wide (aspect_ratio > 0.8)
        - Dresses: Very tall (aspect_ratio < 0.6)
        """
        aspect_ratio = width / height if height > 0 else 1.0
        
        signals = {
            'aspect_ratio': aspect_ratio,
            'is_very_tall': aspect_ratio < 0.6,  # Likely dress
            'is_tall': aspect_ratio < 0.8,       # Likely bottom/pants
            'is_square': 0.8 <= aspect_ratio <= 1.3,  # Could be top or bottom
            'is_wide': aspect_ratio > 1.3        # Likely top/shirt
        }
        
        return signals
    
    def analyze_garment_shape(self, img_bytes: bytes) -> dict:
        """
        Analyze garment shape using edge detection
        """
        # Load image
        img = Image.open(io.BytesIO(img_bytes))
        img = img.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Analyze edge distribution
        h, w = edges.shape
        
        # Divide into regions
        top_region = edges[0:h//3, :]
        middle_region = edges[h//3:2*h//3, :]
        bottom_region = edges[2*h//3:h, :]
        
        # Count edges in each region
        top_edges = np.sum(top_region > 0)
        middle_edges = np.sum(middle_region > 0)
        bottom_edges = np.sum(bottom_region > 0)
        total_edges = top_edges + middle_edges + bottom_edges
        
        if total_edges == 0:
            total_edges = 1  # Avoid division by zero
        
        # Edge distribution ratios
        top_ratio = top_edges / total_edges
        middle_ratio = middle_edges / total_edges
        bottom_ratio = bottom_edges / total_edges
        
        signals = {
            'top_concentration': top_ratio,
            'middle_concentration': middle_ratio,
            'bottom_concentration': bottom_ratio,
            'has_collar': top_ratio > 0.4,  # Shirts have collars (edges on top)
            'has_waistband': middle_ratio > 0.5,  # Pants have waistbands (edges in middle)
        }
        
        return signals
    
    def analyze_color_distribution(self, img_bytes: bytes) -> dict:
        """
        Analyze color distribution patterns
        """
        # Load and resize image
        img = Image.open(io.BytesIO(img_bytes))
        img = img.convert('RGB')
        img = img.resize((224, 224), Image.Resampling.LANCZOS)
        img_array = np.array(img)
        
        # Divide into upper and lower halves
        h, w, _ = img_array.shape
        upper_half = img_array[0:h//2, :, :]
        lower_half = img_array[h//2:h, :, :]
        
        # Calculate average colors
        upper_mean = np.mean(upper_half, axis=(0, 1))
        lower_mean = np.mean(lower_half, axis=(0, 1))
        
        # Color uniformity
        upper_std = np.std(upper_half)
        lower_std = np.std(lower_half)
        
        # Color difference between halves
        color_diff = np.linalg.norm(upper_mean - lower_mean)
        
        signals = {
            'color_difference': color_diff,
            'upper_uniformity': upper_std,
            'lower_uniformity': lower_std,
            'is_uniform': upper_std < 40 and lower_std < 40,  # Solid color (often pants)
            'has_pattern': upper_std > 60 or lower_std > 60,   # Patterned (often shirts)
        }
        
        return signals
    
    def extract_features(self, img_bytes: bytes) -> np.ndarray:
        """Extract ResNet50 features"""
        # Load and preprocess image
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((224, 224), Image.Resampling.LANCZOS)
        
        # Convert to array
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Extract features
        features = self.base_model.predict(img_array, verbose=0)
        return features[0]
    
    def classify(self, img_bytes: bytes) -> dict:
        """
        Classify clothing using multiple signals
        
        Returns:
            {
                'predicted_type': str,
                'confidence': float,
                'reasoning': list of str (explanation)
            }
        """
        # Get original dimensions
        width, height = self.get_image_dimensions(img_bytes)
        
        # Analyze multiple signals
        aspect_signals = self.analyze_aspect_ratio(width, height)
        shape_signals = self.analyze_garment_shape(img_bytes)
        color_signals = self.analyze_color_distribution(img_bytes)
        
        # Extract deep features
        features = self.extract_features(img_bytes)
        feature_mean = np.mean(features)
        feature_std = np.std(features)
        
        # Decision logic with reasoning
        reasoning = []
        votes = {'top': 0, 'bottom': 0, 'dress': 0, 'shoes': 0, 'blazer': 0, 'other': 0}
        
        # Signal 1: Aspect Ratio (Most reliable)
        aspect_ratio = aspect_signals['aspect_ratio']
        if aspect_signals['is_very_tall']:
            votes['dress'] += 4
            reasoning.append(f"Very tall image (aspect ratio: {aspect_ratio:.2f}) → dress")
        elif aspect_signals['is_tall']:
            votes['bottom'] += 3
            reasoning.append(f"Tall image (aspect ratio: {aspect_ratio:.2f}) → bottom/pants")
        elif aspect_signals['is_wide']:
            votes['top'] += 3
            reasoning.append(f"Wide image (aspect ratio: {aspect_ratio:.2f}) → top/shirt")
        else:
            # For square images, default to TOP unless strong evidence otherwise
            votes['top'] += 2
            reasoning.append(f"Square image (aspect ratio: {aspect_ratio:.2f}) → likely top")
        
        # Signal 2: Edge Distribution (Strong signal)
        if shape_signals['has_collar']:
            votes['top'] += 2
            votes['blazer'] += 1
            reasoning.append("Collar detected (top edge concentration) → top/blazer")
        
        if shape_signals['has_waistband']:
            votes['bottom'] += 2
            reasoning.append("Waistband detected (middle edge concentration) → bottom")
        
        # Signal 3: Color Patterns (Weaker signal - can be misleading)
        if color_signals['is_uniform'] and aspect_signals['is_tall']:
            # Only trust uniform color if aspect ratio also suggests bottom
            votes['bottom'] += 1
            reasoning.append("Uniform solid color + tall shape → likely pants")
        elif color_signals['has_pattern']:
            votes['top'] += 1
            reasoning.append("Pattern detected → often shirts")
        
        # Signal 4: Deep Features (Supporting evidence)
        if feature_mean > 0.5:
            votes['shoes'] += 3
            reasoning.append("High feature activation → shoes")
        elif feature_std > 0.28:
            votes['top'] += 2
            votes['blazer'] += 1
            reasoning.append("High feature variance (texture/details) → top/blazer")
        elif feature_std < 0.15:
            votes['bottom'] += 1
            reasoning.append("Very low feature variance → possibly plain pants")
        
        # Determine winner
        predicted_type = max(votes, key=votes.get)
        max_votes = votes[predicted_type]
        total_votes = sum(votes.values())
        confidence = max_votes / total_votes if total_votes > 0 else 0.5
        
        # Ensure minimum confidence
        confidence = max(confidence, 0.60)
        
        reasoning.append(f"Final votes: {votes}")
        reasoning.append(f"Winner: {predicted_type} with {max_votes}/{total_votes} votes")
        
        return {
            'predicted_type': predicted_type,
            'confidence': float(confidence),
            'reasoning': reasoning,
            'features': features,  # For similarity matching
            'debug': {
                'dimensions': f"{width}x{height}",
                'aspect_ratio': aspect_ratio,
                'votes': votes
            }
        }
    
    def predict(self, img_bytes: bytes) -> dict:
        """Main prediction method (compatible with existing interface)"""
        result = self.classify(img_bytes)
        
        # Print reasoning in development
        print(f"\n🔍 Classification Reasoning:")
        for reason in result['reasoning']:
            print(f"   {reason}")
        
        return {
            'predicted_type': result['predicted_type'],
            'confidence': result['confidence'],
            'features': result['features']
        }


# Global instance
_improved_classifier = None

def get_improved_classifier():
    """Get or create global improved classifier instance"""
    global _improved_classifier
    if _improved_classifier is None:
        _improved_classifier = ImprovedClothingClassifier()
    return _improved_classifier
