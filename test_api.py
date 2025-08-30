import requests
import json

try:
    # Test merchant menu API
    response = requests.get('http://127.0.0.1:8000/api/menu/merchant')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Number of merchant menus: {len(data)}")
        print("Merchant menus:")
        for menu in data[:3]:  # Show first 3
            print(f"- {menu['menu_title']} ({menu['menu_key']})")
        print("✅ Merchant API working!")
    else:
        print(f"❌ API Error: {response.text}")
except Exception as e:
    print(f"❌ Connection Error: {e}")
