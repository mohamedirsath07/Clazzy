import urllib.request
import json
import sys

url = "http://localhost:8001/recommend-outfits"
data = {
    "occasion": "casual",
    "tops": ["t1.jpg"],
    "bottoms": ["b1.jpg"]
}
json_data = json.dumps(data).encode('utf-8')

req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print(f"✅ Success: {response.status}")
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"❌ Error {e.code}: {e.reason}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"❌ Failed: {str(e)}")
