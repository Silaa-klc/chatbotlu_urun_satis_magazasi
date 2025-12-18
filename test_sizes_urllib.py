import urllib.request
import json

try:
    with urllib.request.urlopen('http://127.0.0.1:5000/api/products/4') as response:
        data = json.loads(response.read().decode())
        print(f"Shoe Sizes: {data.get('bedenler')}")
        
    with urllib.request.urlopen('http://127.0.0.1:5000/api/products/1') as response:
        data = json.loads(response.read().decode())
        print(f"Dress Sizes: {data.get('bedenler')}")
        
except Exception as e:
    print(f"Error: {e}")
