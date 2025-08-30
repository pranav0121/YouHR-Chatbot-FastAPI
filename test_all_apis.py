import requests
import json


def test_all_merchant_endpoints():
    base_url = "http://127.0.0.1:8000"

    # Test all merchant endpoints
    endpoints = [
        "/api/merchant/sales/today",
        "/api/merchant/sales/yesterday",
        "/api/merchant/sales/weekly",
        "/api/merchant/payments/outstanding",
        "/api/merchant/expenses/bills",
        "/api/merchant/staff/attendance",
        "/api/merchant/staff/leave-requests",
        "/api/merchant/staff/messages",
        "/api/merchant/staff/salary"
    ]

    print("🧪 Testing All Merchant API Endpoints")
    print("=" * 50)

    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
            print(f"{status} {endpoint} - Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                # Show a preview of the data
                if isinstance(data, dict):
                    keys = list(data.keys())[:3]
                    preview = {k: data[k] for k in keys}
                    print(f"     Preview: {preview}")
        except Exception as e:
            print(f"❌ FAIL {endpoint} - Error: {e}")

    print("\n🎯 Testing Menu API")
    print("-" * 30)

    # Test menu endpoints
    menu_endpoints = ["/api/menu/merchant", "/api/menu/pos_youhr"]
    for endpoint in menu_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
            count = len(response.json()) if response.status_code == 200 else 0
            print(
                f"{status} {endpoint} - Status: {response.status_code}, Menus: {count}")
        except Exception as e:
            print(f"❌ FAIL {endpoint} - Error: {e}")


if __name__ == "__main__":
    test_all_merchant_endpoints()
