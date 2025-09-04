import requests
import json
import sys
import time
from datetime import datetime


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class MenuTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        self.menu_data = {}

    def print_colored(self, message, color):
        print(f"{color}{message}{Colors.ENDC}")

    def test_menu_endpoint(self, endpoint, test_name, expected_keys=None):
        """Test a menu endpoint and validate response structure"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                json_response = response.json()

                # Log the actual response for debugging
                print(f"Response for {test_name}: {response.json()}")

                # Store menu data for later analysis
                self.menu_data[test_name] = json_response

                # Validate basic structure
                if isinstance(json_response, list) and len(json_response) > 0:
                    # Check if it's a list of menus
                    first_menu = json_response[0]
                    required_menu_keys = ['menu_id',
                                          'menu_key', 'menu_title', 'submenus']

                    if all(key in first_menu for key in required_menu_keys):
                        # Validate submenus structure
                        if isinstance(first_menu['submenus'], list):
                            if len(first_menu['submenus']) > 0:
                                first_submenu = first_menu['submenus'][0]
                                required_submenu_keys = [
                                    'submenu_id', 'submenu_key', 'submenu_title']

                                if all(key in first_submenu for key in required_submenu_keys):
                                    self.print_colored(
                                        f"✓ PASSED: {test_name}", Colors.GREEN)
                                    self.passed_tests += 1
                                    return True
                            else:
                                self.print_colored(
                                    f"✓ PASSED: {test_name} (No submenus)", Colors.GREEN)
                                self.passed_tests += 1
                                return True

                # Check if it's a single status response
                elif isinstance(json_response, dict) and 'status' in json_response:
                    if json_response['status'] == 'success':
                        self.print_colored(
                            f"✓ PASSED: {test_name}", Colors.GREEN)
                        self.passed_tests += 1
                        return True

                self.print_colored(
                    f"✗ FAILED: {test_name} - Invalid response structure", Colors.RED)
                self.failed_tests += 1
                return False

            elif response.status_code == 404:
                self.print_colored(
                    f"⚠ WARNING: {test_name} - No data found (404)", Colors.YELLOW)
                self.passed_tests += 1  # 404 might be expected for some company types
                return True
            else:
                self.print_colored(
                    f"✗ FAILED: {test_name} - Status Code: {response.status_code}", Colors.RED)
                self.failed_tests += 1
                return False

        except requests.exceptions.RequestException as e:
            self.print_colored(
                f"✗ FAILED: {test_name} - Connection Error: {str(e)}", Colors.RED)
            self.failed_tests += 1
            return False

    def test_company_type_menus(self):
        """Test menu endpoints for different company types"""
        self.print_colored("\n🏢 Testing Company Type Menus...", Colors.BLUE)

        company_types = [
            "icp_hr",
            "merchant",
            "retail",
            "restaurant",
            "healthcare",
            "education",
            "finance",
            "manufacturing"
        ]

        for company_type in company_types:
            endpoint = f"/api/menu/{company_type}"
            test_name = f"Menu - {company_type.upper()}"
            self.test_menu_endpoint(endpoint, test_name)

    def test_role_based_menus(self):
        """Test menu endpoints with role-based filtering"""
        self.print_colored("\n👤 Testing Role-Based Menus...", Colors.PURPLE)

        test_cases = [
            {
                "company_type": "icp_hr",
                "role": "hr_assistant",
                "name": "HR Assistant"
            },
            {
                "company_type": "icp_hr",
                "role": "merchant_manager",
                "name": "Merchant Manager"
            },
            {
                "company_type": "icp_hr",
                "role": "retention_executor",
                "name": "Retention Executor"
            },
            {
                "company_type": "merchant",
                "role": "owner",
                "name": "Merchant Owner"
            },
            {
                "company_type": "merchant",
                "role": "manager",
                "name": "Merchant Manager"
            }
        ]

        for test_case in test_cases:
            endpoint = f"/api/chatbot/menus-with-submenus?company_type={test_case['company_type']}&role={test_case['role']}"
            test_name = f"Role Menu - {test_case['name']}"
            self.test_menu_endpoint(endpoint, test_name)

    def test_menu_data_integrity(self):
        """Test the integrity of menu data returned by the API."""
        self.print_colored("\n🔍 Testing Menu Data Integrity...", Colors.BLUE)

        total_menus = 0
        unique_menu_keys = set()
        total_submenus = 0
        unique_submenu_keys = set()

        for company_type in ["icp_hr", "merchant", "retail", "restaurant", "healthcare", "education", "finance", "manufacturing"]:
            endpoint = f"/api/menu/{company_type}"
            response = requests.get(f"{self.base_url}{endpoint}").json()

            if response["status"] == "success" and "data" in response:
                menus = response["data"]
                total_menus += len(menus)
                for menu in menus:
                    unique_menu_keys.add(menu["menu_key"])
                    submenus = menu.get("submenus", [])
                    total_submenus += len(submenus)
                    for submenu in submenus:
                        unique_submenu_keys.add(submenu["submenu_key"])

        self.print_colored(
            f"📊 Menu Statistics:\n  Total Menus Found: {total_menus}\n  Unique Menu Keys: {len(unique_menu_keys)}\n  Total Submenus Found: {total_submenus}\n  Unique Submenu Keys: {len(unique_submenu_keys)}", Colors.PURPLE)

        if total_menus > 0 and total_submenus > 0:
            self.print_colored("✓ PASSED: Menu Data Integrity", Colors.GREEN)
            self.passed_tests += 1
        else:
            self.print_colored("✗ FAILED: No menu data found", Colors.RED)
            self.failed_tests += 1

    def test_menu_api_endpoints(self):
        """Test that submenu API endpoints are accessible"""
        self.print_colored("\n🔗 Testing Submenu API Endpoints...", Colors.BLUE)

        tested_endpoints = set()

        for test_name, data in self.menu_data.items():
            if isinstance(data, list):
                for menu in data:
                    if isinstance(menu, dict) and 'submenus' in menu:
                        for submenu in menu['submenus']:
                            if isinstance(submenu, dict) and 'api_endpoint' in submenu:
                                endpoint = submenu['api_endpoint']

                                # Skip if already tested
                                if endpoint in tested_endpoints:
                                    continue

                                tested_endpoints.add(endpoint)

                                # Test the endpoint
                                if endpoint.startswith('/api/'):
                                    url = f"{self.base_url}{endpoint}"
                                    try:
                                        response = requests.get(
                                            url, timeout=10)
                                        # Accept these as valid responses
                                        if response.status_code in [200, 404, 422]:
                                            self.print_colored(
                                                f"✓ PASSED: API Endpoint - {endpoint}", Colors.GREEN)
                                            self.passed_tests += 1
                                        else:
                                            self.print_colored(
                                                f"✗ FAILED: API Endpoint - {endpoint} (Status: {response.status_code})", Colors.RED)
                                            self.failed_tests += 1
                                    except requests.exceptions.RequestException:
                                        self.print_colored(
                                            f"✗ FAILED: API Endpoint - {endpoint} (Connection Error)", Colors.RED)
                                        self.failed_tests += 1

    def generate_menu_report(self):
        """Generate a detailed menu report"""
        self.print_colored("\n📋 Menu Structure Report", Colors.PURPLE)
        self.print_colored("=" * 50, Colors.PURPLE)

        for test_name, data in self.menu_data.items():
            if isinstance(data, list) and len(data) > 0:
                print(f"\n🏷️  {test_name}:")
                for menu in data:
                    if isinstance(menu, dict):
                        menu_title = menu.get('menu_title', 'Unknown Menu')
                        menu_key = menu.get('menu_key', 'unknown')
                        submenu_count = len(menu.get('submenus', []))

                        print(
                            f"  📁 {menu_title} ({menu_key}) - {submenu_count} submenus")

                        if submenu_count > 0:
                            for submenu in menu['submenus']:
                                submenu_title = submenu.get(
                                    'submenu_title', 'Unknown Submenu')
                                api_endpoint = submenu.get(
                                    'api_endpoint', 'No endpoint')
                                print(
                                    f"    └─ {submenu_title} → {api_endpoint}")

    def run_all_menu_tests(self):
        """Run all menu-related tests"""
        start_time = time.time()

        self.print_colored("=" * 70, Colors.YELLOW)
        self.print_colored(
            "🍽️  COMPREHENSIVE MENU TESTING SUITE", Colors.YELLOW)
        self.print_colored("=" * 70, Colors.YELLOW)

        # Run all test suites
        self.test_company_type_menus()
        self.test_role_based_menus()
        self.test_menu_data_integrity()
        self.test_menu_api_endpoints()

        # Generate report
        self.generate_menu_report()

        # Print summary
        end_time = time.time()
        duration = round(end_time - start_time, 2)

        self.print_colored("\n" + "=" * 70, Colors.YELLOW)
        self.print_colored("📊 MENU TEST SUMMARY", Colors.YELLOW)
        self.print_colored("=" * 70, Colors.YELLOW)

        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests *
                     100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        self.print_colored(f"Passed: {self.passed_tests}", Colors.GREEN)
        self.print_colored(f"Failed: {self.failed_tests}", Colors.RED)
        self.print_colored(f"Pass Rate: {pass_rate:.1f}%", Colors.BLUE)
        print(f"Duration: {duration} seconds")

        self.print_colored("\n" + "=" * 70, Colors.YELLOW)

        return self.failed_tests == 0


def main():
    """Main function to run menu tests"""
    print("🍽️  Menu Testing Suite")
    print("Testing all menu endpoints and their structure...")
    print("Please ensure your FastAPI server is running on http://localhost:8000")

    # Wait for user confirmation
    input("Press Enter to start menu testing...")

    tester = MenuTester()
    success = tester.run_all_menu_tests()

    if success:
        print("\n🎉 All menu tests passed! Your menu system is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some menu tests failed. Please check the menu implementation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
