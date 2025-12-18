import json
import random
import os

file_path = 'urunler.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for product in data:
    # Add random stock between 1 and 15 to simulate scarcity for some
    product['stok'] = random.randint(1, 15)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Stock information added to urunler.json")
