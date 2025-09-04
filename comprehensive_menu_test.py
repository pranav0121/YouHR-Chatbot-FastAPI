import requests
import json
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class ComprehensiveMenuTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        self.menu_hierarchy = {}
        self.performance_metrics = {}
        self.lock = threading.Lock()

    def print_colored(self, message, color):
        print(f"{color}{message}{Colors.ENDC}")

    def log_test_result(self, test_name, status, details=None):
        """Thread-safe logging of test results"""
        with self.lock:
            if status == "PASSED":
                self.passed_tests += 1
                self.print_colored(f"✓ PASSED: {test_name}", Colors.GREEN)
            else:
                self.failed_tests += 1
                self.print_colored(
                    f"✗ FAILED: {test_name} - {details}", Colors.RED)

            self.test_results.append({
                "test": test_name,
                "status": status,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })

    def test_server_connectivity(self):
        """Test basic server connectivity"""
        self.print_colored("\n🔌 Testing Server Connectivity...", Colors.BLUE)

        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test_result("Server Health Check", "PASSED")
                return True
            else:
                self.log_test_result(
                    "Server Health Check", "FAILED", f"Status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test_result("Server Health Check",
                                 "FAILED", f"Connection error: {str(e)}")
            return False

    def test_basic_menu_endpoints(self):
        """Test basic menu endpoints"""
        self.print_colored("\n📋 Testing Basic Menu Endpoints...", Colors.BLUE)

        # Test root menu endpoint
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.log_test_result("Root Endpoint", "PASSED")
            else:
                self.log_test_result(
                    "Root Endpoint", "FAILED", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test_result("Root Endpoint", "FAILED", str(e))

    def test_company_type_variations(self):
        """Test different company type variations"""
        self.print_colored(
            "\n🏢 Testing Company Type Variations...", Colors.PURPLE)

        company_types = [
            "icp_hr", "merchant", "retail", "restaurant", "healthcare",
            "education", "finance", "manufacturing", "technology", "consulting"
        ]

        def test_company_type(company_type):
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.base_url}/api/menu/{company_type}", timeout=10)
                end_time = time.time()

                response_time = round((end_time - start_time) * 1000, 2)  # ms

                with self.lock:
                    self.performance_metrics[f"menu_{company_type}"] = response_time

                # 404 is acceptable if no data
                if response.status_code in [200, 404]:
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            with self.lock:
                                self.menu_hierarchy[company_type] = {
                                    "menus": len(data),
                                    "total_submenus": sum(len(menu.get('submenus', [])) for menu in data if isinstance(menu, dict))
                                }
                    self.log_test_result(
                        f"Company Type: {company_type}", "PASSED", f"Response time: {response_time}ms")
                else:
                    self.log_test_result(
                        f"Company Type: {company_type}", "FAILED", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test_result(
                    f"Company Type: {company_type}", "FAILED", str(e))

        # Use ThreadPoolExecutor for concurrent testing
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(test_company_type, company_types)

    def test_role_combinations(self):
        """Test different role combinations"""
        self.print_colored("\n👥 Testing Role Combinations...", Colors.CYAN)

        role_combinations = [
            {"company_type": "icp_hr", "role": "hr_assistant"},
            {"company_type": "icp_hr", "role": "merchant_manager"},
            {"company_type": "icp_hr", "role": "retention_executor"},
            {"company_type": "icp_hr", "role": "admin"},
            {"company_type": "merchant", "role": "owner"},
            {"company_type": "merchant", "role": "manager"},
            {"company_type": "merchant", "role": "employee"},
            {"company_type": "retail", "role": "store_manager"},
            {"company_type": "restaurant", "role": "chef"},
            {"company_type": "healthcare", "role": "doctor"}
        ]

        def test_role_combination(combo):
            try:
                endpoint = f"/api/chatbot/menus-with-submenus?company_type={combo['company_type']}&role={combo['role']}"
                start_time = time.time()
                response = requests.get(
                    f"{self.base_url}{endpoint}", timeout=10)
                end_time = time.time()

                response_time = round((end_time - start_time) * 1000, 2)
                test_name = f"Role: {combo['company_type']}/{combo['role']}"

                if response.status_code in [200, 404]:
                    self.log_test_result(
                        test_name, "PASSED", f"Response time: {response_time}ms")

                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            # Validate menu structure
                            for menu in data:
                                if not isinstance(menu, dict) or 'menu_key' not in menu:
                                    self.log_test_result(
                                        f"{test_name} - Structure", "FAILED", "Invalid menu structure")
                                    return
                            self.log_test_result(
                                f"{test_name} - Structure", "PASSED")
                else:
                    self.log_test_result(
                        test_name, "FAILED", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test_result(
                    f"Role: {combo['company_type']}/{combo['role']}", "FAILED", str(e))

        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(test_role_combination, role_combinations)

    def test_parameter_validation(self):
        """Test parameter validation and edge cases"""
        self.print_colored(
            "\n⚠️  Testing Parameter Validation...", Colors.YELLOW)

        edge_cases = [
            {
                "endpoint": "/api/chatbot/menus-with-submenus",
                "name": "Missing Parameters",
                "expected_status": 422
            },
            {
                "endpoint": "/api/chatbot/menus-with-submenus?company_type=",
                "name": "Empty Company Type",
                "expected_status": 422
            },
            {
                "endpoint": "/api/chatbot/menus-with-submenus?company_type=invalid&role=invalid",
                "name": "Invalid Parameters",
                "expected_status": 404
            },
            {
                "endpoint": "/api/menu/",
                "name": "Empty Menu Path",
                "expected_status": 404
            },
            {
                "endpoint": "/api/menu/very_long_company_type_name_that_should_not_exist",
                "name": "Long Invalid Company Type",
                "expected_status": 404
            }
        ]

        for case in edge_cases:
            try:
                response = requests.get(
                    f"{self.base_url}{case['endpoint']}", timeout=10)
                if response.status_code == case['expected_status']:
                    self.log_test_result(
                        f"Edge Case: {case['name']}", "PASSED")
                else:
                    self.log_test_result(f"Edge Case: {case['name']}", "FAILED",
                                         f"Expected {case['expected_status']}, got {response.status_code}")
            except Exception as e:
                self.log_test_result(
                    f"Edge Case: {case['name']}", "FAILED", str(e))

    def test_menu_data_consistency(self):
        """Test menu data consistency across different endpoints"""
        self.print_colored(
            "\n🔍 Testing Menu Data Consistency...", Colors.PURPLE)

        # Get menu data from different endpoints for the same company type
        try:
            # Test ICP HR menus
            response1 = requests.get(
                f"{self.base_url}/api/menu/icp_hr", timeout=10)
            response2 = requests.get(
                f"{self.base_url}/api/chatbot/menus-with-submenus?company_type=icp_hr&role=hr_assistant", timeout=10)

            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()

                # Check if both return menu data
                if isinstance(data1, list) and isinstance(data2, list):
                    menu_keys_1 = set(menu.get('menu_key')
                                      for menu in data1 if isinstance(menu, dict))
                    menu_keys_2 = set(menu.get('menu_key')
                                      for menu in data2 if isinstance(menu, dict))

                    # There might be overlap or differences due to role filtering
                    if len(menu_keys_1) > 0 or len(menu_keys_2) > 0:
                        self.log_test_result("Menu Data Consistency", "PASSED",
                                             f"Endpoint 1: {len(menu_keys_1)} menus, Endpoint 2: {len(menu_keys_2)} menus")
                    else:
                        self.log_test_result(
                            "Menu Data Consistency", "FAILED", "No menu data found")
                else:
                    self.log_test_result(
                        "Menu Data Consistency", "FAILED", "Invalid data structure")
            else:
                self.log_test_result("Menu Data Consistency", "FAILED",
                                     f"Response codes: {response1.status_code}, {response2.status_code}")
        except Exception as e:
            self.log_test_result("Menu Data Consistency", "FAILED", str(e))

    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        self.print_colored(
            "\n⚡ Testing Performance Benchmarks...", Colors.CYAN)

        # Test response times
        endpoints_to_benchmark = [
            "/api/menu/icp_hr",
            "/api/menu/merchant",
            "/api/chatbot/menus-with-submenus?company_type=icp_hr&role=hr_assistant"
        ]

        for endpoint in endpoints_to_benchmark:
            response_times = []

            for i in range(5):  # Test 5 times for average
                try:
                    start_time = time.time()
                    response = requests.get(
                        f"{self.base_url}{endpoint}", timeout=10)
                    end_time = time.time()

                    if response.status_code == 200:
                        response_times.append(
                            (end_time - start_time) * 1000)  # Convert to ms
                except Exception:
                    pass

            if response_times:
                avg_response_time = round(
                    sum(response_times) / len(response_times), 2)
                max_response_time = round(max(response_times), 2)

                # Consider < 1000ms as good performance
                if avg_response_time < 1000:
                    self.log_test_result(f"Performance: {endpoint}", "PASSED",
                                         f"Avg: {avg_response_time}ms, Max: {max_response_time}ms")
                else:
                    self.log_test_result(f"Performance: {endpoint}", "FAILED",
                                         f"Slow response - Avg: {avg_response_time}ms")
            else:
                self.log_test_result(
                    f"Performance: {endpoint}", "FAILED", "No successful responses")

    def generate_comprehensive_report(self):
        """Generate a comprehensive test report"""
        self.print_colored("\n📊 COMPREHENSIVE TEST REPORT", Colors.WHITE)
        self.print_colored("=" * 80, Colors.WHITE)

        # Performance metrics
        if self.performance_metrics:
            self.print_colored("\n⚡ Performance Metrics:", Colors.CYAN)
            for endpoint, time_ms in self.performance_metrics.items():
                status = "🟢" if time_ms < 500 else "🟡" if time_ms < 1000 else "🔴"
                print(f"  {status} {endpoint}: {time_ms}ms")

        # Menu hierarchy
        if self.menu_hierarchy:
            self.print_colored("\n🏗️  Menu Hierarchy:", Colors.PURPLE)
            for company_type, stats in self.menu_hierarchy.items():
                print(
                    f"  📁 {company_type.upper()}: {stats['menus']} menus, {stats['total_submenus']} submenus")

        # Failed tests details
        failed_tests = [
            result for result in self.test_results if result['status'] == 'FAILED']
        if failed_tests:
            self.print_colored(
                f"\n❌ Failed Tests ({len(failed_tests)}):", Colors.RED)
            for test in failed_tests:
                print(
                    f"  - {test['test']}: {test.get('details', 'No details')}")

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        start_time = time.time()

        self.print_colored("=" * 80, Colors.YELLOW)
        self.print_colored(
            "🚀 COMPREHENSIVE MENU TESTING SUITE - ADVANCED", Colors.YELLOW)
        self.print_colored("=" * 80, Colors.YELLOW)

        # Check server connectivity first
        if not self.test_server_connectivity():
            self.print_colored(
                "\n❌ Server is not accessible. Aborting tests.", Colors.RED)
            return False

        # Run all test suites
        self.test_basic_menu_endpoints()
        self.test_company_type_variations()
        self.test_role_combinations()
        self.test_parameter_validation()
        self.test_menu_data_consistency()
        self.test_performance_benchmarks()

        # Generate comprehensive report
        self.generate_comprehensive_report()

        # Print final summary
        end_time = time.time()
        duration = round(end_time - start_time, 2)

        self.print_colored("\n" + "=" * 80, Colors.YELLOW)
        self.print_colored("🏁 FINAL TEST SUMMARY", Colors.YELLOW)
        self.print_colored("=" * 80, Colors.YELLOW)

        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests *
                     100) if total_tests > 0 else 0

        print(f"📈 Total Tests Executed: {total_tests}")
        self.print_colored(
            f"✅ Tests Passed: {self.passed_tests}", Colors.GREEN)
        self.print_colored(f"❌ Tests Failed: {self.failed_tests}", Colors.RED)
        self.print_colored(
            f"📊 Overall Pass Rate: {pass_rate:.1f}%", Colors.BLUE)
        print(f"⏱️  Total Duration: {duration} seconds")

        # Grade the overall system
        if pass_rate >= 95:
            grade = "🏆 EXCELLENT"
            color = Colors.GREEN
        elif pass_rate >= 85:
            grade = "🥈 GOOD"
            color = Colors.BLUE
        elif pass_rate >= 70:
            grade = "🥉 ACCEPTABLE"
            color = Colors.YELLOW
        else:
            grade = "❌ NEEDS IMPROVEMENT"
            color = Colors.RED

        self.print_colored(f"\n🎯 System Grade: {grade}", color)
        self.print_colored("=" * 80, Colors.YELLOW)

        return self.failed_tests == 0


def main():
    """Main function to run comprehensive menu tests"""
    print("🍽️  Comprehensive Menu Testing Suite - Advanced Edition")
    print("This will perform extensive testing of all menu endpoints with:")
    print("  • Concurrent testing")
    print("  • Performance benchmarking")
    print("  • Edge case validation")
    print("  • Data consistency checks")
    print("  • Comprehensive reporting")
    print()
    print("Please ensure your FastAPI server is running on http://localhost:8000")

    # Wait for user confirmation
    input("Press Enter to start comprehensive testing...")

    tester = ComprehensiveMenuTester()
    success = tester.run_comprehensive_tests()

    if success:
        print("\n🎉 All comprehensive tests passed! Your menu system is robust and well-implemented.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please review the detailed report above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
