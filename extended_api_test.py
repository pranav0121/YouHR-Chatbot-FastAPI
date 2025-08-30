#!/usr/bin/env python3
"""
Extended API Testing Suite for Missing Merchant Endpoints
Tests all remaining merchant endpoints that weren't covered in the comprehensive test
"""

import requests
import json
import sys
from datetime import datetime


class ExtendedAPITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.passed = 0
        self.failed = 0
        self.total = 0

    def test_endpoint(self, method, endpoint, data=None, params=None, expected_status=200, description=""):
        """Test a single API endpoint"""
        self.total += 1
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                if params:
                    response = requests.post(url, params=params, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)
            else:
                print(f"❌ {method} {endpoint}")
                print(f"    Unsupported method: {method}")
                self.failed += 1
                return

            status_code = response.status_code

            # Check if status matches expected
            if status_code == expected_status:
                print(f"✅ {method} {endpoint}")
                print(f"    Description: {description}")
                print(
                    f"    Status: {status_code} (Expected: {expected_status})")

                try:
                    json_response = response.json()
                    if isinstance(json_response, dict):
                        print(f"    Response: {len(json_response)} fields")
                        # Show preview of first few fields
                        preview_items = list(json_response.items())[:3]
                        preview_text = ", ".join(
                            [f"{k}: {v}" for k, v in preview_items])
                        if len(preview_text) > 100:
                            preview_text = preview_text[:100] + "..."
                        print(f"    Preview: {preview_text}")
                    elif isinstance(json_response, list):
                        print(f"    Response: {len(json_response)} items")
                    else:
                        print(f"    Response: {type(json_response).__name__}")
                except:
                    print(f"    Response: {len(response.text)} characters")

                self.passed += 1
            else:
                print(f"❌ {method} {endpoint}")
                print(f"    Description: {description}")
                print(
                    f"    Status: {status_code} (Expected: {expected_status})")
                try:
                    error_detail = response.json()
                    error_text = json.dumps(error_detail)[
                        :200] + "..." if len(json.dumps(error_detail)) > 200 else json.dumps(error_detail)
                    print(f"    Error: {error_text}")
                except:
                    print(f"    Error: {response.text[:200]}...")
                self.failed += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ {method} {endpoint}")
            print(f"    Description: {description}")
            print(f"    Connection Error: {str(e)}")
            self.failed += 1
        except Exception as e:
            print(f"❌ {method} {endpoint}")
            print(f"    Description: {description}")
            print(f"    Unexpected Error: {str(e)}")
            self.failed += 1

        print()

    def run_missing_endpoint_tests(self):
        """Test all missing merchant endpoints"""
        print("🔍 EXTENDED MERCHANT API TEST SUITE")
        print("=" * 60)
        print("Testing Missing Endpoints...")
        print(f"Testing server: {self.base_url}")
        print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 1. MARKETING & GROWTH - MISSING ENDPOINTS
        print("\n📢 1. MARKETING & GROWTH - MISSING ENDPOINTS")
        print("-" * 50)

        self.test_endpoint("GET", "/api/merchant/marketing/campaign-results?merchant_id=MERCH001",
                           description="Check campaign results (sent, delivered, read)")

        self.test_endpoint("GET", "/api/merchant/loan/status?merchant_id=MERCH001",
                           description="Check loan status (approved, pending, declined)")

        loan_continue_params = {
            "merchant_id": "MERCH001",
            "document_type": "KYC",
            "document_url": "https://example.com/kyc.pdf",
            "notes": "KYC documents uploaded"
        }

        self.test_endpoint("POST", "/api/merchant/loan/continue", params=loan_continue_params,
                           description="Continue loan application (upload documents)")

        # 2. NOTIFICATIONS - ALL ENDPOINTS
        print("\n🔔 2. NOTIFICATIONS - ALL ENDPOINTS")
        print("-" * 40)

        self.test_endpoint("GET", "/api/merchant/notifications/leave-requests?merchant_id=MERCH001",
                           description="Approve pending leave requests")

        self.test_endpoint("GET", "/api/merchant/notifications/shift-change?merchant_id=MERCH001",
                           description="Approve shift change requests")

        self.test_endpoint("GET", "/api/merchant/notifications/payment-settlement?merchant_id=MERCH001",
                           description="See latest payment settlement update")

        self.test_endpoint("GET", "/api/merchant/notifications/renew-subscription?merchant_id=MERCH001",
                           description="Renew subscription (if expiring soon)")

        self.test_endpoint("GET", "/api/merchant/notifications/head-office-messages?merchant_id=MERCH001",
                           description="Read messages from Head Office")

        # 3. HELP & SUPPORT - ALL ENDPOINTS
        print("\n🛠 3. HELP & SUPPORT - ALL ENDPOINTS")
        print("-" * 40)

        pos_app_params = {
            "merchant_id": "MERCH001",
            "problem_description": "POS app crashes when processing large orders",
            "error_code": "ERR_001",
            "priority": "High"
        }

        self.test_endpoint("POST", "/api/merchant/support/pos-app", params=pos_app_params,
                           description="Report POS app problem")

        hardware_params = {
            "merchant_id": "MERCH001",
            "hardware_type": "Printer",
            "issue_description": "Printer not responding to print commands",
            "model": "HP LaserJet Pro",
            "priority": "Medium"
        }

        self.test_endpoint("POST", "/api/merchant/support/hardware", params=hardware_params,
                           description="Report hardware issue (printer, scanner, POS)")

        camera_problem_params = {
            "merchant_id": "MERCH001",
            "camera_id": "CAM001",
            "problem_description": "AI camera not detecting products correctly",
            "error_logs": "Error in object detection module",
            "priority": "High"
        }

        self.test_endpoint("POST", "/api/merchant/support/ai-camera", params=camera_problem_params,
                           description="Report AI camera problem (YouLens)")

        camera_install_params = {
            "merchant_id": "MERCH001",
            "request_type": "Installation",
            "location": "Main entrance",
            "preferred_date": "2024-09-15",
            "notes": "Need security camera installation"
        }

        self.test_endpoint("POST", "/api/merchant/support/camera-installation", params=camera_install_params,
                           description="Request camera installation or training")

        general_support_params = {
            "merchant_id": "MERCH001",
            "category": "General",
            "subject": "Account settings help",
            "description": "Need help updating payment methods",
            "priority": "Low"
        }

        self.test_endpoint("POST", "/api/merchant/support/general", params=general_support_params,
                           description="Ask for general support")

        # 4. FEEDBACK & IDEAS - ALL ENDPOINTS
        print("\n💬 4. FEEDBACK & IDEAS - ALL ENDPOINTS")
        print("-" * 40)

        rate_experience_params = {
            "merchant_id": "MERCH001",
            "rating": "Good",
            "category": "Overall Experience",
            "comments": "Very satisfied with the service"
        }

        self.test_endpoint("POST", "/api/merchant/feedback/rate-experience", params=rate_experience_params,
                           description="Rate experience with bot (Good/Bad)")

        share_feedback_params = {
            "merchant_id": "MERCH001",
            "feedback_type": "POS",
            "rating": "4",
            "feedback": "POS system is working well, but could be faster",
            "suggestions": "Improve checkout speed"
        }

        self.test_endpoint("POST", "/api/merchant/feedback/share", params=share_feedback_params,
                           description="Share feedback on POS/Loan/Camera/Staff")

        suggest_feature_params = {
            "merchant_id": "MERCH001",
            "feature_name": "Inventory Auto-Reorder",
            "description": "Automatically reorder items when stock is low",
            "category": "Inventory Management",
            "priority": "Medium"
        }

        self.test_endpoint("POST", "/api/merchant/feedback/suggest-feature", params=suggest_feature_params,
                           description="Suggest new feature for YouShop")

        # SUMMARY
        print("\n" + "=" * 60)
        print("📊 EXTENDED TEST SUMMARY")
        print("=" * 60)
        print(f"Total Extended Tests: {self.total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        success_rate = (self.passed / self.total) * \
            100 if self.total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")

        if self.failed > 0:
            print(f"\n⚠️  {self.failed} tests failed. Check the errors above.")
            print("\n🔧 RECOMMENDATIONS:")
            print("   1. Implement missing API endpoints")
            print("   2. Add proper error handling")
            print("   3. Update database models if needed")
            print("   4. Test with frontend integration")
        else:
            print("\n🎉 ALL EXTENDED TESTS PASSED! Complete system coverage achieved.")

        print(
            f"\nExtended test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return self.failed == 0


def main():
    """Main function to run extended tests"""
    try:
        tester = ExtendedAPITester()
        success = tester.run_missing_endpoint_tests()

        print("\n" + "=" * 60)
        print("🎯 COMPLETE SYSTEM ANALYSIS")
        print("=" * 60)
        print("Previously Tested (Comprehensive): 28 endpoints ✅")
        print(f"Extended Testing (Missing): {tester.total} endpoints")
        print(f"Total System Coverage: {28 + tester.total} endpoints")

        if success:
            print("\n✅ RESULT: Complete merchant management system fully operational!")
        else:
            print(
                f"\n⚠️  RESULT: {tester.failed} endpoints need implementation")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Extended tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error during extended testing: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
