#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for YouHR Assistant
Tests all HR and Merchant Management endpoints
"""

import requests
import json
from datetime import datetime        whatsapp_data = {
    "campaign_name": "Summer Special Offer",
    "target_audience": "All Customers",
    "message_content": "🌞 Summer Special: 20% off on all beverages! Valid until August 31st.",
    "budget": 5000,
    "scheduled_date": "2024-09-01"
}t sys


class APITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.passed = 0
        self.failed = 0
        self.total = 0

    def test_endpoint(self, method, endpoint, data=None, expected_status=200, description=""):
        """Test a single API endpoint"""
        self.total += 1
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url)
            elif method.upper() == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            status_icon = "✅" if success else "❌"

            if success:
                self.passed += 1
            else:
                self.failed += 1

            print(f"{status_icon} {method} {endpoint}")
            print(f"    Description: {description}")
            print(
                f"    Status: {response.status_code} (Expected: {expected_status})")

            if success and response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        # Show key metrics
                        key_count = len(data.keys())
                        print(f"    Response: {key_count} fields")

                        # Show important fields
                        important_fields = []
                        for key, value in list(data.items())[:3]:
                            if isinstance(value, (str, int, float)):
                                important_fields.append(f"{key}: {value}")
                        if important_fields:
                            print(
                                f"    Preview: {', '.join(important_fields)}")
                    elif isinstance(data, list):
                        print(f"    Response: {len(data)} items")
                except:
                    print(f"    Response: {len(response.text)} characters")
            elif not success:
                print(f"    Error: {response.text[:100]}...")

        except Exception as e:
            self.failed += 1
            print(f"❌ {method} {endpoint}")
            print(f"    Description: {description}")
            print(f"    Error: {str(e)}")

        print()

    def run_comprehensive_tests(self):
        """Run all API tests"""
        print("🧪 COMPREHENSIVE API TEST SUITE")
        print("=" * 60)
        print(f"Testing server: {self.base_url}")
        print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 1. CORE SYSTEM ENDPOINTS
        print("\n📋 1. CORE SYSTEM ENDPOINTS")
        print("-" * 40)

        self.test_endpoint("GET", "/",
                           description="Main chatbot interface")

        self.test_endpoint("GET", "/api/menu/pos_youhr",
                           description="HR menu system")

        self.test_endpoint("GET", "/api/menu/merchant",
                           description="Merchant menu system")

        self.test_endpoint("GET", "/api/chatbot/menus-with-submenus?company_type=pos_youhr&role=employee",
                           description="HR menus with role filtering")

        # 2. HR ASSISTANT ENDPOINTS
        print("\n👥 2. HR ASSISTANT ENDPOINTS")
        print("-" * 40)

        self.test_endpoint("GET", "/api/attendance/history?employee_id=EMP001&days=30",
                           description="Employee attendance history")

        self.test_endpoint("GET", "/api/leave/applications?employee_id=EMP001",
                           description="Employee leave applications")

        self.test_endpoint("GET", "/api/payroll/payslips?employee_id=EMP001&year=2024",
                           description="Employee payslip records")

        self.test_endpoint("GET", "/api/employee/status?employee_id=EMP001",
                           description="Employee status and information")

        # HR POST endpoints
        leave_data = {
            "employee_id": "EMP001",
            "employee_name": "John Smith",
            "leave_type": "Annual Leave",
            "from_date": "2024-09-15",
            "to_date": "2024-09-17",
            "reason": "Family vacation"
        }

        self.test_endpoint("POST", "/api/leave/apply", data=leave_data,
                           description="Submit leave application")

        # 3. MERCHANT MANAGEMENT - SALES ANALYTICS
        print("\n💰 3. MERCHANT SALES ANALYTICS")
        print("-" * 40)

        self.test_endpoint("GET", "/api/merchant/sales/today",
                           description="Today's sales data and analytics")

        self.test_endpoint("GET", "/api/merchant/sales/yesterday",
                           description="Yesterday's sales comparison")

        self.test_endpoint("GET", "/api/merchant/sales/weekly",
                           description="Weekly sales report and trends")

        # 4. MERCHANT MANAGEMENT - FINANCIAL
        print("\n💳 4. MERCHANT FINANCIAL MANAGEMENT")
        print("-" * 40)

        self.test_endpoint("GET", "/api/merchant/payments/outstanding",
                           description="Outstanding payments and invoices")

        self.test_endpoint("GET", "/api/merchant/expenses/bills",
                           description="Expenses and bill management")

        # 5. MERCHANT MANAGEMENT - STAFF
        print("\n👨‍💼 5. MERCHANT STAFF MANAGEMENT")
        print("-" * 40)

        self.test_endpoint("GET", "/api/merchant/staff/attendance",
                           description="Staff attendance monitoring")

        self.test_endpoint("GET", "/api/merchant/staff/leave-requests",
                           description="Staff leave request management")

        self.test_endpoint("GET", "/api/merchant/staff/messages",
                           description="Staff communication system")

        self.test_endpoint("GET", "/api/merchant/staff/salary",
                           description="Staff salary information")

        # Staff POST endpoints
        employee_data = {
            "employee_id": "EMP007",
            "employee_name": "Test Employee",
            "email": "test@example.com",
            "phone": "+1234567890",
            "department": "Sales",
            "position": "Sales Associate",
            "employment_type": "Full-time",
            "hire_date": "2024-09-01"
        }

        self.test_endpoint("POST", "/api/merchant/staff/add-employee", data=employee_data,
                           description="Add new employee")

        hr_support_data = {
            "employee_id": "EMP001",
            "employee_name": "John Smith",
            "category": "Technical",
            "subject": "System Access Issue",
            "description": "Unable to access payroll system",
            "priority": "High"
        }

        self.test_endpoint("POST", "/api/merchant/staff/hr-support", data=hr_support_data,
                           description="Submit HR support request")

        # 6. MERCHANT MANAGEMENT - MARKETING
        print("\n📱 6. MERCHANT MARKETING TOOLS")
        print("-" * 40)

        whatsapp_data = {
            "campaign_name": "Summer Special",
            "target_audience": "All Customers",
            "message": "🌞 Summer Special: 20% off on all beverages! Valid until August 31st.",
            "budget": 5000,
            "scheduled_date": "2024-09-01"
        }

        self.test_endpoint("POST", "/api/merchant/marketing/whatsapp-campaign", data=whatsapp_data,
                           description="Create WhatsApp marketing campaign")

        promotion_data = {
            "promotion_name": "Happy Hour Special",
            "promotion_type": "Percentage",
            "discount_percentage": 25,
            "valid_from": "2024-09-01",
            "valid_until": "2024-09-30",
            "applicable_items": "Beverages",
            "minimum_purchase": 100
        }

        self.test_endpoint("POST", "/api/merchant/marketing/instant-promotion", data=promotion_data,
                           description="Create instant promotion")

        # 7. ADDITIONAL ENDPOINTS
        print("\n🔧 7. ADDITIONAL SYSTEM ENDPOINTS")
        print("-" * 40)

        self.test_endpoint("GET", "/api/chatbot/company-info",
                           description="Company information endpoint")

        self.test_endpoint("GET", "/docs",
                           description="API documentation (Swagger UI)")

        self.test_endpoint("GET", "/redoc",
                           description="Alternative API documentation")

        # 8. ERROR HANDLING TESTS
        print("\n⚠️  8. ERROR HANDLING TESTS")
        print("-" * 40)

        self.test_endpoint("GET", "/api/nonexistent", expected_status=404,
                           description="Non-existent endpoint (should return 404)")

        self.test_endpoint("GET", "/api/employee/status?employee_id=INVALID", expected_status=404,
                           description="Invalid employee ID (should return 404)")

        self.test_endpoint("POST", "/api/leave/apply", data={}, expected_status=422,
                           description="Invalid leave data (should return 422)")

        # SUMMARY
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")

        success_rate = (self.passed / self.total) * \
            100 if self.total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! System is fully operational.")
        else:
            print(f"\n⚠️  {self.failed} tests failed. Check the errors above.")

        print(
            f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return self.failed == 0


def main():
    """Main test runner"""
    tester = APITester()

    try:
        success = tester.run_comprehensive_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
