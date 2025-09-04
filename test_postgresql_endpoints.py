import requests
import json
import sys
import time
from datetime import datetime, date, timedelta


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []

    def print_colored(self, message, color):
        print(f"{color}{message}{Colors.ENDC}")

    def test_endpoint(self, endpoint, method="GET", data=None, expected_status=200, test_name=None):
        """Test a single API endpoint"""
        if not test_name:
            test_name = f"{method} {endpoint}"

        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)

            # Check status code
            if response.status_code == expected_status:
                # Check if response is JSON and has expected structure
                try:
                    json_response = response.json()
                    # Accept multiple valid JSON response formats:
                    # 1. Our API format: 'status' or 'data' fields
                    # 2. FastAPI validation format: 'detail' field (for 422 errors)
                    # 3. Basic dict response
                    if isinstance(json_response, dict) and (
                        'status' in json_response or
                        'data' in json_response or
                        'detail' in json_response or
                        len(json_response) > 0
                    ):
                        self.print_colored(
                            f"✓ PASSED: {test_name}", Colors.GREEN)
                        self.passed_tests += 1
                        self.test_results.append(
                            {"test": test_name, "status": "PASSED", "response_code": response.status_code})
                        return True
                    else:
                        self.print_colored(
                            f"✗ FAILED: {test_name} - Invalid JSON structure", Colors.RED)
                        self.failed_tests += 1
                        self.test_results.append(
                            {"test": test_name, "status": "FAILED", "reason": "Invalid JSON structure"})
                        return False
                except json.JSONDecodeError:
                    self.print_colored(
                        f"✗ FAILED: {test_name} - Invalid JSON response", Colors.RED)
                    self.failed_tests += 1
                    self.test_results.append(
                        {"test": test_name, "status": "FAILED", "reason": "Invalid JSON"})
                    return False
            else:
                self.print_colored(
                    f"✗ FAILED: {test_name} - Status Code: {response.status_code}", Colors.RED)
                self.failed_tests += 1
                self.test_results.append(
                    {"test": test_name, "status": "FAILED", "reason": f"Status code {response.status_code}"})
                return False

        except requests.exceptions.RequestException as e:
            self.print_colored(
                f"✗ FAILED: {test_name} - Connection Error: {str(e)}", Colors.RED)
            self.failed_tests += 1
            self.test_results.append(
                {"test": test_name, "status": "FAILED", "reason": f"Connection error: {str(e)}"})
            return False

    def test_server_health(self):
        """Test if the server is running and responsive"""
        self.print_colored("\n🔍 Testing Server Health...", Colors.BLUE)

        # Test health endpoint
        self.test_endpoint("/health", test_name="Health Check")

        # Test root API endpoint (returns JSON)
        self.test_endpoint("/api/", expected_status=200,
                           test_name="Root Endpoint")

    def test_menu_endpoints(self):
        """Test menu-related endpoints"""
        self.print_colored("\n📋 Testing Menu Endpoints...", Colors.BLUE)

        # Test menu endpoints with different company types
        company_types = ["icp_hr", "merchant", "retail", "restaurant"]

        for company_type in company_types:
            self.test_endpoint(
                f"/api/menu/{company_type}", test_name=f"Menu for {company_type}")

        # Test menus with submenus
        self.test_endpoint("/api/chatbot/menus-with-submenus?company_type=icp_hr&role=hr_assistant",
                           test_name="Menus with submenus (HR)")
        self.test_endpoint("/api/chatbot/menus-with-submenus?company_type=icp_hr&role=merchant_manager",
                           test_name="Menus with submenus (Merchant Manager)")

    def test_hr_endpoints(self):
        """Test HR-related endpoints"""
        self.print_colored("\n👥 Testing HR Endpoints...", Colors.BLUE)

        # Test employee endpoints
        self.test_endpoint("/api/chatbot/employees", test_name="Employee List")
        self.test_endpoint(
            "/api/employee/status?employee_id=EMP001", test_name="Employee Status")

        # Test attendance endpoints
        self.test_endpoint(
            "/api/attendance/history?employee_id=EMP001", test_name="Attendance History")
        self.test_endpoint("/api/attendance/history?employee_id=EMP001&start_date=2025-08-01&end_date=2025-08-31",
                           test_name="Attendance History with Date Range")

        # Test leave endpoints
        self.test_endpoint(
            "/api/leave/applications?employee_id=EMP001", test_name="Leave Applications")

        # Test leave application submission
        leave_data = {
            "employee_id": "EMP001",
            "leave_type": "Sick Leave",
            "start_date": "2025-09-10",
            "end_date": "2025-09-12",
            "reason": "Medical appointment",
            "days": 3
        }
        self.test_endpoint("/api/leave/apply", method="POST",
                           data=leave_data, test_name="Apply Leave")

        # Test payroll endpoints
        self.test_endpoint(
            "/api/payroll/payslips?employee_id=EMP001", test_name="Payslips")
        self.test_endpoint(
            "/api/payroll/payslips?employee_id=EMP001&year=2025&month=8", test_name="Payslips with filters")

    def test_chatbot_endpoints(self):
        """Test chatbot data endpoints"""
        self.print_colored(
            "\n🤖 Testing Chatbot Data Endpoints...", Colors.BLUE)

        chatbot_data_types = [
            "employees", "attendance", "payslips", "leave-applications",
            "hr-support-tickets", "marketing-campaigns", "promotions", "sales-records"
        ]

        for data_type in chatbot_data_types:
            self.test_endpoint(
                f"/api/chatbot/{data_type}", test_name=f"Chatbot {data_type}")

    def test_merchant_endpoints(self):
        """Test merchant-related endpoints"""
        self.print_colored("\n🏪 Testing Merchant Endpoints...", Colors.BLUE)

        # Test sales endpoints
        self.test_endpoint("/api/merchant/sales/today",
                           test_name="Today's Sales")
        self.test_endpoint("/api/merchant/sales/today?merchant_id=MERCH002",
                           test_name="Today's Sales (Custom Merchant)")
        self.test_endpoint("/api/merchant/sales/weekly",
                           test_name="Weekly Sales")
        self.test_endpoint("/api/merchant/sales/weekly?merchant_id=MERCH003",
                           test_name="Weekly Sales (Custom Merchant)")

    def test_file_endpoints(self):
        """Test file-related endpoints"""
        self.print_colored("\n📁 Testing File Endpoints...", Colors.BLUE)

        # Test download endpoint with a non-existent file (should return 404)
        self.test_endpoint("/api/downloads/nonexistent.xlsx",
                           expected_status=404, test_name="Download Non-existent File")

    def test_error_handling(self):
        """Test error handling for invalid endpoints"""
        self.print_colored("\n⚠️ Testing Error Handling...", Colors.BLUE)

        # Test invalid endpoints
        self.test_endpoint("/api/invalid/endpoint",
                           expected_status=404, test_name="Invalid Endpoint")
        self.test_endpoint("/api/chatbot/invalid-data-type",
                           expected_status=404, test_name="Invalid Chatbot Data Type")

        # Test endpoints with missing parameters
        self.test_endpoint("/api/attendance/history", expected_status=422,
                           test_name="Missing Required Parameters")

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        start_time = time.time()

        self.print_colored("=" * 60, Colors.YELLOW)
        self.print_colored("🚀 STARTING COMPREHENSIVE API TESTS", Colors.YELLOW)
        self.print_colored("=" * 60, Colors.YELLOW)

        # Run all test suites
        self.test_server_health()
        self.test_menu_endpoints()
        self.test_hr_endpoints()
        self.test_chatbot_endpoints()
        self.test_merchant_endpoints()
        self.test_file_endpoints()
        self.test_error_handling()

        # Print summary
        end_time = time.time()
        duration = round(end_time - start_time, 2)

        self.print_colored("\n" + "=" * 60, Colors.YELLOW)
        self.print_colored("📊 TEST SUMMARY", Colors.YELLOW)
        self.print_colored("=" * 60, Colors.YELLOW)

        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests *
                     100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        self.print_colored(f"Passed: {self.passed_tests}", Colors.GREEN)
        self.print_colored(f"Failed: {self.failed_tests}", Colors.RED)
        self.print_colored(f"Pass Rate: {pass_rate:.1f}%", Colors.BLUE)
        print(f"Duration: {duration} seconds")

        if self.failed_tests > 0:
            self.print_colored("\n❌ FAILED TESTS:", Colors.RED)
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(
                        f"  - {result['test']}: {result.get('reason', 'Unknown error')}")

        self.print_colored("\n" + "=" * 60, Colors.YELLOW)

        return self.failed_tests == 0


def main():
    """Main function to run tests"""
    print("🔧 PostgreSQL Endpoints Test Suite")
    print("Please ensure your FastAPI server is running on http://localhost:8000")

    # Wait for user confirmation
    input("Press Enter to start testing...")

    tester = APITester()
    success = tester.run_comprehensive_tests()

    if success:
        print("\n🎉 All tests passed! Your API is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the API implementation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
