"""
Test the running API server with real images
"""
import requests
import os

API_URL = "http://localhost:8001"
INPUTS_DIR = r"D:\Studiess\Project\Clazzy\Inputs"

print("=" * 60)
print("TESTING BACKEND API")
print("=" * 60)

# Test health endpoint
print("\n1. Testing health endpoint...")
try:
    resp = requests.get(f"{API_URL}/health", timeout=5)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test classify endpoint with images
print("\n2. Testing /ml/classify endpoint...")

test_images = [
    ("green_shirt.webp", "top"),
    ("maroon_shirt.webp", "top"),
    ("black_pant.jpg", "bottom"),
    ("blue_pant.jpg", "bottom"),
]

for filename, expected in test_images:
    path = os.path.join(INPUTS_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                files = {'file': (filename, f, 'image/webp')}
                resp = requests.post(f"{API_URL}/ml/classify", files=files, timeout=30)
            
            if resp.status_code == 200:
                result = resp.json()
                predicted = result.get('predicted_type', 'unknown')
                confidence = result.get('confidence', 0)
                raw = result.get('raw_prediction', 0)
                
                match = "✅" if predicted == expected else "❌"
                print(f"   {match} {filename:25s} -> {predicted:6s} (conf: {confidence:.2f}, raw: {raw:.4f}) [expected: {expected}]")
            else:
                print(f"   ❌ {filename}: HTTP {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            print(f"   ❌ {filename}: {e}")
    else:
        print(f"   ⚠️ {filename}: File not found")

print("\n" + "=" * 60)
print("API TEST COMPLETE")
print("=" * 60)
