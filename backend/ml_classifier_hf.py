"""
MODEL 1: Clothing Type Classifier (Hugging Face Version)
===================================================================
Uses pre-trained Hugging Face model for accurate clothing classification.

Purpose: Classify clothing items into specific types and map to general categories
Technology: wargoninnovation/wargon-clothing-classifier from Hugging Face
Input: Image bytes
Output: Classification result with confidence score

Categories mapped:
- Top: Blazer, Blouse, Cardigan, Hoodie, Jacket, Sweater, Shirt, T-shirt, etc.
- Bottom: Jeans, Shorts, Skirt, Trousers, Tights, etc.
- Dress: Dress, Nightgown, Robe
"""

import io
from PIL import Image
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

class ClothingClassifier:
    """
    Clothing classifier using Hugging Face pre-trained model
    Maps 30+ clothing categories to simplified types: top/bottom/dress/blazer
    """
    
    def __init__(self):
        """Initialize the Hugging Face clothing classifier"""
        print("🔄 Loading Hugging Face clothing classifier...")
        
        # Load the pre-trained clothing classifier
        self.classifier = pipeline(
            "image-classification",
            model="wargoninnovation/wargon-clothing-classifier",
            device=-1  # Use CPU (-1), change to 0 for GPU
        )
        
        # Category mapping to our simplified types
        self.category_mapping = {
            # Top garments
            'Blazer': 'blazer',
            'Blouse': 'top',
            'Cardigan': 'top',
            'Hoodie': 'top',
            'Jacket': 'blazer',
            'Sweater': 'top',
            'Rain jacket': 'blazer',
            'Shirt': 'top',
            'Robe': 'dress',
            'T-shirt': 'top',
            'Tank top': 'top',
            'Top': 'top',
            'Training top': 'top',
            'Pajamas': 'top',
            'Vest': 'blazer',
            'Winter jacket': 'blazer',
            
            # Bottom garments
            'Jeans': 'bottom',
            'Nightgown': 'dress',
            'Outerwear': 'blazer',
            'Rain trousers': 'bottom',
            'Shorts': 'bottom',
            'Skirt': 'bottom',
            'Tights': 'bottom',
            'Trousers': 'bottom',
            'Tunic': 'top',
            'Winter trousers': 'bottom',
            
            # Dresses
            'Dress': 'dress',
        }
        
        print("✅ Hugging Face Clothing Classifier initialized")
    
    def predict(self, img_bytes: bytes) -> dict:
        """
        Classify clothing type using Hugging Face model
        Args:
            img_bytes: Raw image bytes
        Returns:
            {
                'predicted_type': str (top/bottom/blazer/dress/other),
                'confidence': float,
                'raw_prediction': str (original model prediction),
                'features': None (kept for compatibility)
            }
        """
        # Load image from bytes
        img = Image.open(io.BytesIO(img_bytes))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Run inference
        predictions = self.classifier(img, top_k=1)
        
        # Get top prediction
        top_prediction = predictions[0]
        raw_label = top_prediction['label']
        confidence = top_prediction['score']
        
        # Map to our categories
        predicted_type = self.category_mapping.get(raw_label, 'other')
        
        print(f"    HF Prediction: {raw_label} → {predicted_type} ({confidence:.2%})")
        
        return {
            'predicted_type': predicted_type,
            'confidence': float(confidence),
            'raw_prediction': raw_label,
            'features': None  # Not needed for color/similarity matching anymore
        }
