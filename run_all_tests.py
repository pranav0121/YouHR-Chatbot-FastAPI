#!/usr/bin/env python3
"""
Test Runner for HR Assistant Chatbot API
Runs all test suites and generates a comprehensive report
"""

import subprocess
import sys
import time
import os
from datetime import datetime
import json


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


class TestRunner:
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None

    def print_colored(self, message, color):
        print(f"{color}{message}{Colors.ENDC}")

    def print_header(self, title):
        self.print_colored("=" * 80, Colors.YELLOW)
        self.print_colored(f"🧪 {title}", Colors.YELLOW)
        self.print_colored("=" * 80, Colors.YELLOW)

    def run_test_file(self, test_file, test_name):
        """Run a specific test file and capture results"""
        self.print_colored(f"\n🔄 Running {test_name}...", Colors.BLUE)

        try:
            start_time = time.time()

            # Run the test file
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(test_file)),
                timeout=300  # 5 minute timeout
            )

            end_time = time.time()
            duration = round(end_time - start_time, 2)

            # Store results
            self.test_results[test_name] = {
                "exit_code": result.returncode,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

            # Print immediate feedback
            if result.returncode == 0:
                self.print_colored(
                    f"✅ {test_name} PASSED ({duration}s)", Colors.GREEN)
            else:
                self.print_colored(
                    f"❌ {test_name} FAILED ({duration}s)", Colors.RED)
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}...")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            self.print_colored(
                f"⏰ {test_name} TIMEOUT (5 minutes)", Colors.RED)
            self.test_results[test_name] = {
                "exit_code": -1,
                "duration": 300,
                "stdout": "",
                "stderr": "Test timed out after 5 minutes",
                "success": False
            }
            return False

        except Exception as e:
            self.print_colored(f"💥 {test_name} ERROR: {str(e)}", Colors.RED)
            self.test_results[test_name] = {
                "exit_code": -2,
                "duration": 0,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
            return False

    def check_server_running(self):
        """Check if the FastAPI server is running"""
        self.print_colored(
            "\n🔍 Checking if FastAPI server is running...", Colors.BLUE)

        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.print_colored(
                    "✅ Server is running and healthy", Colors.GREEN)
                return True
            else:
                self.print_colored(
                    f"⚠️  Server responded with status {response.status_code}", Colors.YELLOW)
                return True  # Server is running but might not have health endpoint
        except requests.exceptions.RequestException:
            self.print_colored(
                "❌ Server is not running on http://localhost:8000", Colors.RED)
            self.print_colored(
                "Please start the server with: python -m uvicorn app.main:app --reload", Colors.YELLOW)
            return False

    def run_all_tests(self):
        """Run all available test suites"""
        self.start_time = time.time()

        self.print_header(
            "HR ASSISTANT CHATBOT API - COMPREHENSIVE TEST SUITE")

        # Check if server is running first
        if not self.check_server_running():
            print("\n❌ Cannot run tests without a running server.")
            return False

        # Define test files to run
        test_files = [
            {
                "file": "test_postgresql_endpoints.py",
                "name": "PostgreSQL Endpoints Test",
                "description": "Tests all API endpoints with comprehensive validation"
            },
            {
                "file": "test_all_menus.py",
                "name": "Menu Structure Test",
                "description": "Tests menu system structure and integrity"
            },
            {
                "file": "comprehensive_menu_test.py",
                "name": "Comprehensive Menu Test",
                "description": "Advanced menu testing with performance benchmarks"
            }
        ]

        successful_tests = 0
        total_tests = len(test_files)

        # Run each test file
        for test_info in test_files:
            test_file = test_info["file"]
            test_name = test_info["name"]

            # Check if test file exists
            if not os.path.exists(test_file):
                self.print_colored(
                    f"⚠️  Test file {test_file} not found, skipping...", Colors.YELLOW)
                continue

            self.print_colored(f"\n📋 {test_info['description']}", Colors.CYAN)

            success = self.run_test_file(test_file, test_name)
            if success:
                successful_tests += 1

        self.end_time = time.time()

        # Generate comprehensive report
        self.generate_final_report(successful_tests, total_tests)

        return successful_tests == total_tests

    def generate_final_report(self, successful_tests, total_tests):
        """Generate a comprehensive final report"""
        self.print_header("FINAL TEST REPORT")

        total_duration = round(self.end_time - self.start_time, 2)
        pass_rate = (successful_tests / total_tests *
                     100) if total_tests > 0 else 0

        # Overall summary
        self.print_colored("\n📊 OVERALL SUMMARY", Colors.WHITE)
        print(f"🕒 Total Test Duration: {total_duration} seconds")
        print(f"📈 Test Suites Run: {total_tests}")
        self.print_colored(
            f"✅ Successful Suites: {successful_tests}", Colors.GREEN)
        self.print_colored(
            f"❌ Failed Suites: {total_tests - successful_tests}", Colors.RED)
        self.print_colored(
            f"📊 Overall Pass Rate: {pass_rate:.1f}%", Colors.BLUE)

        # Individual test results
        self.print_colored("\n📋 DETAILED RESULTS", Colors.WHITE)
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["success"] else "❌"
            status_color = Colors.GREEN if result["success"] else Colors.RED

            self.print_colored(f"{status_icon} {test_name}", status_color)
            print(f"   Duration: {result['duration']}s")
            print(f"   Exit Code: {result['exit_code']}")

            if not result["success"] and result["stderr"]:
                print(f"   Error: {result['stderr'][:100]}...")

        # Performance summary
        self.print_colored("\n⚡ PERFORMANCE SUMMARY", Colors.CYAN)
        fastest_test = min(self.test_results.items(),
                           key=lambda x: x[1]["duration"], default=None)
        slowest_test = max(self.test_results.items(),
                           key=lambda x: x[1]["duration"], default=None)

        if fastest_test:
            print(
                f"🏃 Fastest Test: {fastest_test[0]} ({fastest_test[1]['duration']}s)")
        if slowest_test:
            print(
                f"🐌 Slowest Test: {slowest_test[0]} ({slowest_test[1]['duration']}s)")

        # Recommendations
        self.print_colored("\n💡 RECOMMENDATIONS", Colors.PURPLE)

        if pass_rate == 100:
            print("🎉 Excellent! All tests passed. Your API is working perfectly.")
        elif pass_rate >= 80:
            print("👍 Good! Most tests passed. Review failed tests for minor issues.")
        elif pass_rate >= 60:
            print(
                "⚠️  Moderate. Several tests failed. Significant issues need attention.")
        else:
            print(
                "🚨 Critical! Many tests failed. Major issues require immediate attention.")

        # Save report to file
        self.save_report_to_file()

        self.print_colored("\n" + "=" * 80, Colors.YELLOW)

    def save_report_to_file(self):
        """Save test report to a JSON file"""
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "total_duration": round(self.end_time - self.start_time, 2),
                "test_results": self.test_results,
                "summary": {
                    "total_tests": len(self.test_results),
                    "successful_tests": sum(1 for r in self.test_results.values() if r["success"]),
                    "failed_tests": sum(1 for r in self.test_results.values() if not r["success"]),
                    "pass_rate": (sum(1 for r in self.test_results.values() if r["success"]) / len(self.test_results) * 100) if self.test_results else 0
                }
            }

            report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(report_filename, 'w') as f:
                json.dump(report_data, f, indent=2)

            self.print_colored(
                f"📄 Test report saved to: {report_filename}", Colors.BLUE)

        except Exception as e:
            self.print_colored(
                f"⚠️  Could not save report to file: {str(e)}", Colors.YELLOW)


def main():
    """Main function"""
    print("🧪 HR Assistant Chatbot API - Test Runner")
    print("This will run all available test suites for the API")
    print("\nAvailable test suites:")
    print("  • PostgreSQL Endpoints Test - Comprehensive API endpoint testing")
    print("  • Menu Structure Test - Menu system validation")
    print("  • Comprehensive Menu Test - Advanced menu testing with benchmarks")
    print()

    runner = TestRunner()

    try:
        success = runner.run_all_tests()

        if success:
            print("\n🎉 All test suites completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Some test suites failed. Check the detailed report above.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error during test execution: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
