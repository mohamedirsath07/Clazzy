"""
Test the improved classifier with debug output
"""
import sys
import os
from PIL import Image
import io

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from ml_classifier_improved import ImprovedClothingClassifier

def test_classifier():
    print("=" * 80)
    print("TESTING IMPROVED CLOTHING CLASSIFIER")
    print("=" * 80)
    
    # Initialize classifier
    print("\n1. Initializing classifier...")
    classifier = ImprovedClothingClassifier()
    
    # Check if there are any uploaded images
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'client', 'public', 'uploads')
    
    if os.path.exists(uploads_dir):
        files = [f for f in os.listdir(uploads_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"\n2. Found {len(files)} images in uploads directory")
        
        for filename in files[:5]:  # Test first 5
            filepath = os.path.join(uploads_dir, filename)
            print(f"\n{'=' * 80}")
            print(f"Testing: {filename}")
            print('=' * 80)
            
            # Read image
            with open(filepath, 'rb') as f:
                img_bytes = f.read()
            
            # Get dimensions
            img = Image.open(io.BytesIO(img_bytes))
            width, height = img.size
            aspect_ratio = width / height
            
            print(f"   Dimensions: {width}x{height}")
            print(f"   Aspect Ratio: {aspect_ratio:.2f}")
            
            if aspect_ratio < 0.6:
                print(f"   → Very tall (dress range)")
            elif aspect_ratio < 0.8:
                print(f"   → Tall (bottom/pants range)")
            elif aspect_ratio > 1.3:
                print(f"   → Wide (top/shirt range)")
            else:
                print(f"   → Square (ambiguous)")
            
            # Classify
            result = classifier.classify(img_bytes)
            
            print(f"\n   RESULT: {result['predicted_type']} ({result['confidence']:.2%})")
            print(f"   Votes: {result['debug']['votes']}")
    else:
        print(f"\n⚠️  Uploads directory not found: {uploads_dir}")
        print("   Create test images first!")

if __name__ == "__main__":
    test_classifier()
