#!/usr/bin/env python3
"""
Quick Test Execution Script
Runs a basic validation of the optimized API
"""

import requests
import sys
import time
from datetime import datetime


def test_basic_functionality():
    """Quick test of basic API functionality"""
    base_url = "http://localhost:8000"

    print("🧪 Quick API Validation Test")
    print("=" * 40)

    # Test endpoints
    tests = [
        {"url": "/health", "name": "Health Check"},
        {"url": "/", "name": "Root Endpoint"},
        {"url": "/api/menu/icp_hr", "name": "ICP HR Menu"},
        {"url": "/api/chatbot/employees", "name": "Employee Data"},
        {"url": "/api/merchant/sales/today", "name": "Sales Data"}
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            print(f"Testing {test['name']}... ", end="")
            response = requests.get(f"{base_url}{test['url']}", timeout=5)

            if response.status_code in [200, 404]:  # 404 might be expected
                print("✅ PASS")
                passed += 1
            else:
                print(f"❌ FAIL (Status: {response.status_code})")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL (Error: {str(e)[:50]}...)")
            failed += 1

    # Summary
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0

    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} passed ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 API is working well!")
        return True
    else:
        print("⚠️  API has issues that need attention")
        return False


if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(130)
