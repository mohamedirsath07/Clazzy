"""
MODEL DIAGNOSTIC SCRIPT
========================
This script diagnoses the top/bottom classification model to identify
why it might be misclassifying clothing items.

Run this script from the backend directory:
    python diagnose_model.py
"""

import os
import sys
import numpy as np
from PIL import Image
import io

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_classifier import ClothingClassifier, IMAGE_SIZE, CLASS_NAMES

def load_and_test_image(classifier, image_path: str) -> dict:
    """Load an image and get prediction with full details."""
    try:
        with open(image_path, 'rb') as f:
            img_bytes = f.read()
        
        result = classifier.predict(img_bytes)
        return {
            'path': image_path,
            'filename': os.path.basename(image_path),
            'predicted_type': result['predicted_type'],
            'confidence': result['confidence'],
            'raw_prediction': result['raw_prediction'],
            'success': True
        }
    except Exception as e:
        return {
            'path': image_path,
            'filename': os.path.basename(image_path),
            'error': str(e),
            'success': False
        }

def infer_expected_type(filename: str) -> str:
    """Infer expected type from filename."""
    filename_lower = filename.lower()
    
    # Bottom indicators
    bottom_keywords = ['pant', 'pants', 'jeans', 'short', 'shorts', 'skirt', 'trouser', 'bottom', 'cargo']
    for kw in bottom_keywords:
        if kw in filename_lower:
            return 'bottom'
    
    # Top indicators
    top_keywords = ['shirt', 'top', 'tshirt', 't-shirt', 'blouse', 'sweater', 'hoodie', 'jacket', 'polo']
    for kw in top_keywords:
        if kw in filename_lower:
            return 'top'
    
    return 'unknown'

def main():
    print("=" * 80)
    print("🔬 CLOTHING CLASSIFICATION MODEL DIAGNOSTIC")
    print("=" * 80)
    print()
    
    # Phase 1: Load the classifier
    print("📦 PHASE 1: Loading Model...")
    print("-" * 40)
    try:
        classifier = ClothingClassifier()
        print("✅ Model loaded successfully!")
        print(f"   Input size: {IMAGE_SIZE}")
        print(f"   Classes: {CLASS_NAMES}")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    print()
    
    # Phase 2: Test on known images from Inputs folder
    print("🧪 PHASE 2: Testing on Sample Images...")
    print("-" * 40)
    
    inputs_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'Inputs')
    inputs_folder = os.path.abspath(inputs_folder)
    
    if not os.path.exists(inputs_folder):
        print(f"⚠️ Inputs folder not found: {inputs_folder}")
        inputs_folder = None
    
    # Also check uploads folder
    uploads_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'client', 'public', 'uploads')
    uploads_folder = os.path.abspath(uploads_folder)
    
    test_images = []
    
    # Collect images from Inputs folder
    if inputs_folder and os.path.exists(inputs_folder):
        for f in os.listdir(inputs_folder):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                test_images.append(os.path.join(inputs_folder, f))
        print(f"📂 Found {len(test_images)} images in Inputs folder")
    
    # Collect images from uploads folder
    if os.path.exists(uploads_folder):
        upload_count = 0
        for f in os.listdir(uploads_folder):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and not f.startswith('mock_'):
                test_images.append(os.path.join(uploads_folder, f))
                upload_count += 1
        if upload_count > 0:
            print(f"📂 Found {upload_count} images in uploads folder")
    
    if not test_images:
        print("⚠️ No test images found!")
        print("   Please add some images to the Inputs folder or upload some clothing images.")
        return
    
    print()
    
    # Phase 3: Run predictions and analyze
    print("🔍 PHASE 3: Running Predictions...")
    print("-" * 40)
    
    results = []
    for img_path in test_images:
        result = load_and_test_image(classifier, img_path)
        result['expected_type'] = infer_expected_type(result['filename'])
        results.append(result)
    
    # Display results
    print()
    print(f"{'Filename':<35} {'Expected':<10} {'Predicted':<10} {'Conf':<8} {'Raw':<8} {'Status'}")
    print("-" * 90)
    
    correct = 0
    incorrect = 0
    unknown = 0
    
    tops_as_bottom = 0
    bottoms_as_top = 0
    
    for r in results:
        if not r['success']:
            print(f"{r['filename']:<35} {'ERROR':<10} {r.get('error', 'Unknown error')[:40]}")
            continue
        
        expected = r['expected_type']
        predicted = r['predicted_type']
        confidence = r['confidence']
        raw = r['raw_prediction']
        
        if expected == 'unknown':
            status = '❓ Unknown'
            unknown += 1
        elif expected == predicted:
            status = '✅ Correct'
            correct += 1
        else:
            status = '❌ WRONG!'
            incorrect += 1
            if expected == 'top' and predicted == 'bottom':
                tops_as_bottom += 1
            elif expected == 'bottom' and predicted == 'top':
                bottoms_as_top += 1
        
        print(f"{r['filename']:<35} {expected:<10} {predicted:<10} {confidence:.2%}   {raw:.4f}   {status}")
    
    # Phase 4: Summary and Diagnosis
    print()
    print("=" * 80)
    print("📊 PHASE 4: DIAGNOSIS SUMMARY")
    print("=" * 80)
    
    total_known = correct + incorrect
    if total_known > 0:
        accuracy = correct / total_known * 100
        print(f"   ✅ Correct predictions: {correct}/{total_known} ({accuracy:.1f}%)")
        print(f"   ❌ Incorrect predictions: {incorrect}/{total_known} ({100-accuracy:.1f}%)")
        print(f"   ❓ Unknown (can't verify): {unknown}")
        print()
        
        if incorrect > 0:
            print("   🔴 MISCLASSIFICATION BREAKDOWN:")
            print(f"      - Tops classified as Bottom: {tops_as_bottom}")
            print(f"      - Bottoms classified as Top: {bottoms_as_top}")
            print()
        
        # Diagnosis
        print("   🩺 DIAGNOSIS:")
        if accuracy >= 90:
            print("      ✅ Model accuracy is GOOD (≥90%)")
            print("      The issue might be in the recommendation logic, not classification.")
        elif accuracy >= 70:
            print("      ⚠️ Model accuracy is MODERATE (70-90%)")
            print("      Some misclassifications may cause invalid outfit recommendations.")
        else:
            print("      ❌ Model accuracy is POOR (<70%)")
            print("      The model needs retraining or the labels might be SWAPPED!")
        
        # Check for label swap
        if bottoms_as_top > tops_as_bottom and bottoms_as_top > correct:
            print()
            print("   🚨 CRITICAL: POSSIBLE LABEL SWAP DETECTED!")
            print("      The model might have INVERTED labels.")
            print("      Bottoms are being predicted as 'top' more often than correct predictions.")
            print()
            print("   💡 SUGGESTED FIX:")
            print("      In ml_classifier.py, try swapping the classification logic:")
            print("      - Change: prediction > 0.5 → 'top'")
            print("      - To:     prediction > 0.5 → 'bottom'")
    else:
        print("   ⚠️ No known-type images to verify accuracy.")
        print("   Please add images with 'shirt', 'pant', 'jeans', etc. in filenames.")
    
    print()
    print("=" * 80)
    print("📋 RAW PREDICTION ANALYSIS")
    print("=" * 80)
    
    # Analyze raw predictions
    raw_values = [r['raw_prediction'] for r in results if r['success']]
    if raw_values:
        print(f"   Min raw prediction: {min(raw_values):.4f}")
        print(f"   Max raw prediction: {max(raw_values):.4f}")
        print(f"   Mean raw prediction: {np.mean(raw_values):.4f}")
        print()
        
        # Check if model is biased
        high_values = sum(1 for v in raw_values if v > 0.5)
        low_values = sum(1 for v in raw_values if v <= 0.5)
        
        print(f"   Predictions > 0.5 (classified as 'top'): {high_values}")
        print(f"   Predictions ≤ 0.5 (classified as 'bottom'): {low_values}")
        
        if high_values > low_values * 2:
            print()
            print("   ⚠️ Model is BIASED towards 'top' classification!")
        elif low_values > high_values * 2:
            print()
            print("   ⚠️ Model is BIASED towards 'bottom' classification!")
    
    print()
    print("=" * 80)
    print("🔧 RECOMMENDED ACTIONS")
    print("=" * 80)
    
    if incorrect > correct:
        print("""
   1. SWAP LABELS (Quick Fix):
      In ml_classifier.py, change the predict() method:
      
      # BEFORE:
      if prediction > 0.5:
          predicted_type = 'top'
      else:
          predicted_type = 'bottom'
      
      # AFTER (try this):
      if prediction > 0.5:
          predicted_type = 'bottom'  # SWAPPED!
      else:
          predicted_type = 'top'     # SWAPPED!

   2. RETRAIN MODEL (Better Fix):
      - Ensure training data labels are correct
      - Verify folder names match expected classes
      - Check CLASS_NAMES order matches training data
""")
    else:
        print("""
   1. Model seems to be working reasonably well.
   2. Check the recommendation logic in outfit_recommender.py
   3. Ensure type normalization handles all variants (pants, jeans, shirt, etc.)
""")

if __name__ == "__main__":
    main()
