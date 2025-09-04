#!/usr/bin/env python3
"""
Comprehensive Test Script for All New Endpoints
Tests all merchant management and retention executor endpoints
"""

import requests
import json
import time
from datetime import datetime

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"


class EndpointTester:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []

    def test_endpoint(self, method, endpoint, description, data=None, params=None):
        """Test a single endpoint and record the result."""
        self.total_tests += 1
        url = f"{BASE_URL}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(
                    url, json=data, params=params, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(
                    url, json=data, params=params, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code in [200, 201, 202]:
                self.passed_tests += 1
                status = "✅ PASS"
                try:
                    response_data = response.json()
                    data_preview = str(response_data)[
                        :100] + "..." if len(str(response_data)) > 100 else str(response_data)
                except:
                    data_preview = "Non-JSON response"
            else:
                self.failed_tests += 1
                status = f"❌ FAIL (Status: {response.status_code})"
                data_preview = response.text[:100] + \
                    "..." if len(response.text) > 100 else response.text

            result = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": status,
                "status_code": response.status_code,
                "response_preview": data_preview
            }

            self.test_results.append(result)
            print(f"{status} {method} {endpoint} - {description}")

        except requests.exceptions.RequestException as e:
            self.failed_tests += 1
            status = f"❌ ERROR: {str(e)}"
            result = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": status,
                "status_code": "N/A",
                "response_preview": str(e)
            }
            self.test_results.append(result)
            print(f"{status} {method} {endpoint} - {description}")

    def run_all_tests(self):
        """Run all endpoint tests."""
        print("=" * 80)
        print("🚀 TESTING ALL NEW ENDPOINTS")
        print("=" * 80)
        print(
            f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Test Health Check
        print("🏥 TESTING HEALTH CHECK")
        print("-" * 40)
        self.test_endpoint("GET", "/health", "Health check endpoint")
        print()

        # Test Merchant Management Endpoints
        print("🏪 TESTING MERCHANT MANAGEMENT ENDPOINTS")
        print("-" * 50)

        # Sales & Money Endpoints
        print("💰 Sales & Money Endpoints:")
        self.test_endpoint("GET", "/api/merchant/sales/yesterday",
                           "Get yesterday's sales", params={"merchant_id": "MERCH123"})
        self.test_endpoint("GET", "/api/merchant/payments/outstanding",
                           "Get outstanding payments", params={"merchant_id": "MERCH123"})
        self.test_endpoint("GET", "/api/merchant/expenses/bills",
                           "Get expenses and bills", params={"merchant_id": "MERCH123"})

        # My Staff Endpoints
        print("\n👥 My Staff Endpoints:")
        self.test_endpoint("GET", "/api/merchant/staff/attendance",
                           "Get staff attendance", params={"merchant_id": "MERCH123"})
        self.test_endpoint("GET", "/api/merchant/staff/leave-requests",
                           "Get staff leave requests", params={"merchant_id": "MERCH123"})
        self.test_endpoint("POST", "/api/merchant/staff/leave-requests/LR001/approve",
                           "Approve leave request", params={"merchant_id": "MERCH123"})
        self.test_endpoint("POST", "/api/merchant/staff/leave-requests/LR002/reject",
                           "Reject leave request", params={"merchant_id": "MERCH123"})
        self.test_endpoint("GET", "/api/merchant/staff/messages",
                           "Get staff messages", params={"merchant_id": "MERCH123"})
        self.test_endpoint("POST", "/api/merchant/staff/add-employee",
                           "Add new employee", params={"merchant_id": "MERCH123"})
        self.test_endpoint("GET", "/api/merchant/staff/salary",
                           "Get staff salary info", params={"merchant_id": "MERCH123"})
        self.test_endpoint("POST", "/api/merchant/staff/salary/EMP001/mark-paid",
                           "Mark salary as paid", params={"merchant_id": "MERCH123"})
        self.test_endpoint("POST", "/api/merchant/staff/hr-support",
                           "Create HR support ticket", params={"merchant_id": "MERCH123"})

        # Marketing & Growth Endpoints
        print("\n📈 Marketing & Growth Endpoints:")
        self.test_endpoint("POST", "/api/merchant/marketing/whatsapp-campaign",
                           "Create WhatsApp campaign", params={"merchant_id": "MERCH123"})
        self.test_endpoint("POST", "/api/merchant/marketing/instant-promotion",
                           "Send instant promotion", params={"merchant_id": "MERCH123"})
        self.test_endpoint("GET", "/api/merchant/marketing/campaign-results",
                           "Get campaign results", params={"merchant_id": "MERCH123"})
        self.test_endpoint("GET", "/api/merchant/loan/status",
                           "Get loan status", params={"merchant_id": "MERCH123"})
        self.test_endpoint("POST", "/api/merchant/loan/continue",
                           "Continue loan application", params={"merchant_id": "MERCH123"})

        print()

        # Test Retention Executor Endpoints
        print("🎯 TESTING RETENTION EXECUTOR ENDPOINTS")
        print("-" * 50)

        # My Daily Activity Endpoints
        print("📅 My Daily Activity Endpoints:")
        self.test_endpoint(
            "GET", "/api/icp/executor/assigned-merchants", "Get assigned merchants")
        self.test_endpoint(
            "GET", "/api/icp/executor/merchant-profile/MERCH123", "Get merchant profile")
        self.test_endpoint(
            "POST", "/api/icp/executor/mark-activity-complete", "Mark activity complete")
        self.test_endpoint(
            "POST", "/api/icp/executor/submit-summary-report", "Submit summary report")

        # Merchant Follow-Up Endpoints
        print("\n🔄 Merchant Follow-Up Endpoints:")
        self.test_endpoint(
            "POST", "/api/icp/executor/update-merchant-health", "Update merchant health")
        self.test_endpoint(
            "POST", "/api/icp/executor/log-merchant-needs", "Log merchant needs")
        self.test_endpoint(
            "POST", "/api/icp/executor/add-notes-commitments", "Add notes/commitments")
        self.test_endpoint(
            "POST", "/api/icp/executor/attach-photo-proof", "Attach photo proof")

        # Onboarding Support Endpoints
        print("\n🚀 Onboarding Support Endpoints:")
        self.test_endpoint(
            "GET", "/api/icp/executor/check-pending-documents", "Check pending documents")
        self.test_endpoint(
            "POST", "/api/icp/executor/upload-missing-documents", "Upload missing documents")
        self.test_endpoint(
            "POST", "/api/icp/executor/schedule-installation-training", "Schedule installation/training")
        self.test_endpoint(
            "POST", "/api/icp/executor/confirm-merchant-setup", "Confirm merchant setup")

        # My Notifications Endpoints
        print("\n🔔 My Notifications Endpoints:")
        self.test_endpoint(
            "GET", "/api/icp/executor/todays-tasks", "Get today's tasks")
        self.test_endpoint(
            "GET", "/api/icp/executor/followup-reminders", "Get follow-up reminders")
        self.test_endpoint(
            "GET", "/api/icp/executor/pending-actions", "Get pending actions")

        # Merchant Support Requests Endpoints
        print("\n🆘 Merchant Support Requests Endpoints:")
        self.test_endpoint(
            "POST", "/api/icp/executor/raise-pos-issue", "Raise POS issue")
        self.test_endpoint(
            "POST", "/api/icp/executor/raise-hardware-issue", "Raise hardware issue")
        self.test_endpoint(
            "POST", "/api/icp/executor/escalate-urgent-case", "Escalate urgent case")

        # My Feedback Endpoints
        print("\n💬 My Feedback Endpoints:")
        self.test_endpoint(
            "POST", "/api/icp/executor/share-field-experience", "Share field experience")
        self.test_endpoint(
            "POST", "/api/icp/executor/suggest-improvements", "Suggest improvements")

        print()

    def print_summary(self):
        """Print test summary and results."""
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(
            f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📋 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")

        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

        print()

        if self.failed_tests > 0:
            print("❌ FAILED TESTS:")
            print("-" * 40)
            for result in self.test_results:
                if "FAIL" in result["status"] or "ERROR" in result["status"]:
                    print(
                        f"   {result['method']} {result['endpoint']} - {result['description']}")
                    print(f"   Status: {result['status']}")
                    print(f"   Response: {result['response_preview']}")
                    print()

        print("🎉 All new endpoints tested!")
        print("=" * 80)


def main():
    """Main function to run all tests."""
    print("🧪 YouHR Management Assistant - New Endpoints Test Suite")
    print()

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(
                f"⚠️  Server responded with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the FastAPI server is running on http://127.0.0.1:8000")
        return

    print()

    # Run tests
    tester = EndpointTester()
    tester.run_all_tests()
    tester.print_summary()


if __name__ == "__main__":
    main()
