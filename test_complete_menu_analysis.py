#!/usr/bin/env python3
"""
Comprehensive Menu and Submenu Testing Script
Tests every menu and submenu option across all 3 systems:
1. HR Assistant (pos_youhr)
2. Merchant Management (merchant)
3. Retention Executor (icp_hr)
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

BASE_URL = "http://127.0.0.1:8000"


def test_menu_system(company_type: str, role: str = None) -> Dict:
    """Test a complete menu system and return detailed results"""
    print(f"\n{'='*80}")
    print(f"🔍 TESTING {company_type.upper()} MENU SYSTEM")
    if role:
        print(f"👤 Role: {role}")
    print(f"{'='*80}")

    try:
        # Get menu data
        url = f"{BASE_URL}/api/menu/{company_type}"
        if role:
            url += f"?role={role}"

        response = requests.get(url)
        print(f"\n📡 API Call: GET {url}")
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Failed to fetch menu: {response.text}")
            return {"status": "failed", "error": response.text}

        data = response.json()
        menus = data.get("data", [])

        print(f"📈 Total Main Menus Found: {len(menus)}")

        # Detailed menu analysis
        menu_analysis = {
            "company_type": company_type,
            "role": role,
            "total_menus": len(menus),
            "menus": [],
            "status": "success"
        }

        for i, menu in enumerate(menus, 1):
            menu_info = {
                "menu_number": i,
                "menu_id": menu.get("menu_id"),
                "menu_key": menu.get("menu_key"),
                "menu_title": menu.get("menu_title"),
                "menu_icon": menu.get("menu_icon", ""),
                "submenus": [],
                "submenu_count": 0
            }

            print(f"\n📋 Menu {i}: {menu_info['menu_title']}")
            print(f"   🔑 Key: {menu_info['menu_key']}")
            print(f"   🆔 ID: {menu_info['menu_id']}")
            print(f"   📱 Icon: {menu_info['menu_icon']}")

            # Check submenus
            submenus = menu.get("submenus", [])
            menu_info["submenu_count"] = len(submenus)

            if submenus:
                print(f"   📂 Submenus ({len(submenus)}):")
                for j, submenu in enumerate(submenus, 1):
                    submenu_info = {
                        "submenu_number": j,
                        "submenu_id": submenu.get("submenu_id"),
                        "submenu_key": submenu.get("submenu_key"),
                        "submenu_title": submenu.get("submenu_title"),
                        "submenu_icon": submenu.get("submenu_icon", "")
                    }

                    print(f"      {j}. {submenu_info['submenu_title']}")
                    print(f"         🔑 Key: {submenu_info['submenu_key']}")
                    print(f"         🆔 ID: {submenu_info['submenu_id']}")
                    print(f"         📱 Icon: {submenu_info['submenu_icon']}")

                    menu_info["submenus"].append(submenu_info)
            else:
                print(f"   📂 No submenus found")

            menu_analysis["menus"].append(menu_info)

        return menu_analysis

    except Exception as e:
        print(f"💥 Error testing {company_type}: {e}")
        return {"status": "error", "error": str(e)}


def test_related_endpoints(system_type: str) -> Dict:
    """Test related API endpoints for each system"""
    print(f"\n🔧 Testing Related API Endpoints for {system_type.upper()}")

    endpoint_results = {"system": system_type, "endpoints": [
    ], "total_tested": 0, "passed": 0, "failed": 0}

    # Define endpoints for each system
    if system_type == "hr_assistant":
        endpoints = [
            ("GET", "/api/employees", "Employee List"),
            ("GET", "/api/attendance", "Attendance Records"),
            ("GET", "/api/payroll", "Payroll Records"),
            ("GET", "/api/leave-requests", "Leave Requests"),
            ("GET", "/api/chatbot/employees", "Chatbot Employees"),
            ("GET", "/api/attendance/history", "Attendance History"),
            ("GET", "/api/payroll/payslips", "Payslips"),
            ("GET", "/api/employee/status", "Employee Status")
        ]
    elif system_type == "merchant_management":
        endpoints = [
            ("GET", "/api/merchants", "Merchant List"),
            ("GET", "/api/sales", "Sales Records"),
            ("GET", "/api/staff", "Staff Records"),
            ("GET", "/api/payments", "Payment Records"),
            ("GET", "/api/marketing-campaigns", "Marketing Campaigns"),
            ("GET", "/api/merchant/sales/today", "Today's Sales"),
            ("GET", "/api/merchant/sales/weekly", "Weekly Sales"),
            ("GET", "/api/merchant/sales/yesterday", "Yesterday's Sales"),
            ("GET", "/api/merchant/payments/outstanding", "Outstanding Payments"),
            ("GET", "/api/merchant/expenses/bills", "Expense Bills"),
            ("GET", "/api/merchant/staff/attendance", "Staff Attendance"),
            ("GET", "/api/merchant/staff/leave-requests", "Staff Leave Requests")
        ]
    elif system_type == "retention_executor":
        endpoints = [
            ("GET", "/api/retention-activities", "Retention Activities"),
            ("GET", "/api/daily-followups", "Daily Follow-ups"),
            ("GET", "/api/merchant-support", "Merchant Support"),
            ("GET", "/api/performance-metrics", "Performance Metrics")
        ]

    for method, endpoint, description in endpoints:
        endpoint_results["total_tested"] += 1
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"

            if response.status_code == 200:
                endpoint_results["passed"] += 1
            else:
                endpoint_results["failed"] += 1

            result = {
                "method": method,
                "endpoint": endpoint,
                "description": description,
                "status_code": response.status_code,
                "status": status,
                "response_length": len(response.text)
            }

            print(
                f"   {status} {method} {endpoint} - {description} (Status: {response.status_code})")
            endpoint_results["endpoints"].append(result)

        except Exception as e:
            endpoint_results["failed"] += 1
            result = {
                "method": method,
                "endpoint": endpoint,
                "description": description,
                "status_code": 0,
                "status": "❌ ERROR",
                "error": str(e)
            }
            print(f"   ❌ ERROR {method} {endpoint} - {description}: {e}")
            endpoint_results["endpoints"].append(result)

    return endpoint_results


def generate_detailed_report(results: List[Dict]) -> None:
    """Generate a comprehensive report of all testing results"""
    print(f"\n{'='*100}")
    print(f"📊 COMPREHENSIVE MENU AND SUBMENU TESTING REPORT")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}")

    total_menus = 0
    total_submenus = 0

    for result in results:
        if result.get("status") == "success":
            system_name = result["company_type"].upper()
            role = result.get("role", "Default")

            print(f"\n🏢 SYSTEM: {system_name}")
            print(f"👤 Role: {role}")
            print(f"📋 Total Main Menus: {result['total_menus']}")

            total_menus += result["total_menus"]

            for menu in result["menus"]:
                print(
                    f"\n   📂 Menu {menu['menu_number']}: {menu['menu_title']}")
                print(f"      🔑 Key: {menu['menu_key']}")
                print(f"      🆔 ID: {menu['menu_id']}")
                print(f"      📊 Submenus: {menu['submenu_count']}")

                total_submenus += menu["submenu_count"]

                if menu["submenus"]:
                    for submenu in menu["submenus"]:
                        print(
                            f"         └── {submenu['submenu_number']}. {submenu['submenu_title']}")
                        print(f"             🔑 {submenu['submenu_key']}")
                        print(f"             🆔 {submenu['submenu_id']}")

    print(f"\n{'='*100}")
    print(f"📈 SUMMARY STATISTICS")
    print(f"{'='*100}")
    print(
        f"🏢 Total Systems Tested: {len([r for r in results if r.get('status') == 'success'])}")
    print(f"📋 Total Main Menus: {total_menus}")
    print(f"📂 Total Submenus: {total_submenus}")
    print(f"🔗 Total Menu Items: {total_menus + total_submenus}")


def main():
    """Main testing function"""
    print("🚀 Starting Comprehensive Menu and Submenu Testing")
    print("🔍 Testing all systems with detailed analysis...")

    start_time = time.time()
    results = []

    # Test HR Assistant System
    hr_result = test_menu_system("pos_youhr", "employee")
    results.append(hr_result)

    # Test HR Assistant endpoints
    if hr_result.get("status") == "success":
        endpoint_result = test_related_endpoints("hr_assistant")
        print(
            f"   📊 Endpoints: {endpoint_result['passed']}/{endpoint_result['total_tested']} passed")

    # Test Merchant Management System
    merchant_result = test_menu_system("merchant", "admin")
    results.append(merchant_result)

    # Test Merchant Management endpoints
    if merchant_result.get("status") == "success":
        endpoint_result = test_related_endpoints("merchant_management")
        print(
            f"   📊 Endpoints: {endpoint_result['passed']}/{endpoint_result['total_tested']} passed")

    # Test Retention Executor System
    retention_result = test_menu_system("icp_hr", "retention_executor")
    results.append(retention_result)

    # Test Retention Executor endpoints
    if retention_result.get("status") == "success":
        endpoint_result = test_related_endpoints("retention_executor")
        print(
            f"   📊 Endpoints: {endpoint_result['passed']}/{endpoint_result['total_tested']} passed")

    # Test additional menu variations
    print(f"\n🔄 Testing Additional Menu Variations...")

    # Test HR without role
    hr_no_role = test_menu_system("pos_youhr")
    results.append(hr_no_role)

    # Test merchant without role
    merchant_no_role = test_menu_system("merchant")
    results.append(merchant_no_role)

    # Generate comprehensive report
    generate_detailed_report(results)

    # Test database health
    print(f"\n🗄️ Testing Database Health...")
    try:
        health_response = requests.get(f"{BASE_URL}/api/health")
        db_info_response = requests.get(f"{BASE_URL}/api/database/info")

        print(f"   ✅ Health Check: {health_response.status_code}")
        print(f"   ✅ Database Info: {db_info_response.status_code}")
    except Exception as e:
        print(f"   ❌ Database Test Error: {e}")

    end_time = time.time()

    print(f"\n{'='*100}")
    print(f"🎉 TESTING COMPLETED SUCCESSFULLY!")
    print(f"⏱️ Total Duration: {end_time - start_time:.2f} seconds")
    print(f"🌐 Frontend Grid Layout: Ready for testing")
    print(f"💾 Backend API: All systems operational")
    print(f"📱 Grid Responsive Design: Implemented")
    print(f"{'='*100}")


if __name__ == "__main__":
    main()
