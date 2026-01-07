"""Quick debug script to verify ML classifier predictions"""
import os
from ml_classifier import ClothingClassifier

c = ClothingClassifier()

# Test with actual images
inputs_dir = r'D:\Studiess\Project\Clazzy\Inputs'
print("\n" + "="*60)
print("ML CLASSIFIER DEBUG TEST")
print("="*60 + "\n")

for f in sorted(os.listdir(inputs_dir)):
    if f.endswith(('.jpg', '.jpeg', '.png', '.webp')):
        path = os.path.join(inputs_dir, f)
        with open(path, 'rb') as file:
            result = c.predict(file.read())
        
        ptype = result['predicted_type']
        conf = result['confidence']
        raw = result['raw_prediction']
        
        icon = "👕" if ptype == 'top' else "👖"
        print(f"{icon} {f:<25} → {ptype:<6} conf={conf:.2%}  raw={raw:.4f}")

print("\n" + "="*60)
