import requests
import json
from app.database import get_db
from app import models


def test_complete_integration():
    """
    Complete integration test for Merchant Management System
    Tests: API endpoints + Database menu structure + JavaScript compatibility
    """

    print("🔍 COMPREHENSIVE MERCHANT MANAGEMENT INTEGRATION TEST")
    print("=" * 70)

    # 1. Test Database Menu Structure
    print("\n1️⃣ TESTING DATABASE MENU STRUCTURE")
    print("-" * 50)

    db = next(get_db())
    merchant_menus = db.query(models.ChatbotMenu).filter(
        models.ChatbotMenu.company_type == 'merchant').all()
    total_submenus = 0

    menu_structure = {}
    for menu in merchant_menus:
        submenus = db.query(models.ChatbotSubmenu).filter(
            models.ChatbotSubmenu.menu_id == menu.id).all()
        total_submenus += len(submenus)
        menu_structure[menu.menu_title] = [
            submenu.submenu_title for submenu in submenus]
        print(f"   📋 {menu.menu_title}: {len(submenus)} submenus")

    print(f"\n   ✅ Total Merchant Menus: {len(merchant_menus)}")
    print(f"   ✅ Total Merchant Submenus: {total_submenus}")

    # 2. Test API Endpoints
    print("\n2️⃣ TESTING API ENDPOINTS")
    print("-" * 50)

    # Original 13 endpoints
    original_endpoints = [
        'http://127.0.0.1:8000/api/merchant/sales/today?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/yesterday?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/weekly?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/payments/outstanding?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/expenses/bills?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/staff/attendance?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/staff/leave-requests?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/staff/messages?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/staff/salary?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/staff/add-employee?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/hr/support?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/marketing/whatsapp-campaign?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/marketing/promotion?merchant_id=MERCH001'
    ]

    # New endpoints we just implemented
    new_endpoints = [
        'http://127.0.0.1:8000/api/merchant/sales/today/by-product?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/today/analytics?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/today/export?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/yesterday/by-product?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/yesterday/analytics?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/yesterday/export?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/weekly/analytics?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/weekly/export?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/sales/weekly/compare?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/payments/send-reminders?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/payments/update-status?merchant_id=MERCH001&payment_id=PAY001&status=Paid',
        'http://127.0.0.1:8000/api/merchant/payments/report?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/expenses/add?merchant_id=MERCH001&description=Test+Expense&amount=100',
        'http://127.0.0.1:8000/api/merchant/expenses/monthly-report?merchant_id=MERCH001',
        'http://127.0.0.1:8000/api/merchant/expenses/update-bill?merchant_id=MERCH001&bill_id=BILL001&status=Paid'
    ]

    original_success = 0
    print("   📊 Testing Original 13 Endpoints:")
    for endpoint in original_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            endpoint_name = endpoint.split('/')[-1].split('?')[0]
            if response.status_code == 200:
                print(f"      ✅ {endpoint_name}")
                original_success += 1
            else:
                print(f"      ❌ {endpoint_name} ({response.status_code})")
        except Exception as e:
            endpoint_name = endpoint.split('/')[-1].split('?')[0]
            print(f"      💥 {endpoint_name} (Error: {str(e)[:50]})")

    new_success = 0
    print("\\n   🆕 Testing New 15 Endpoints:")
    for endpoint in new_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            endpoint_name = endpoint.split('/')[-1].split('?')[0]
            if response.status_code == 200:
                print(f"      ✅ {endpoint_name}")
                new_success += 1
            else:
                print(f"      ❌ {endpoint_name} ({response.status_code})")
        except Exception as e:
            endpoint_name = endpoint.split('/')[-1].split('?')[0]
            print(f"      💥 {endpoint_name} (Error: {str(e)[:50]})")

    total_endpoints = len(original_endpoints) + len(new_endpoints)
    total_success = original_success + new_success

    # 3. Test JavaScript Integration
    print("\\n3️⃣ TESTING JAVASCRIPT INTEGRATION")
    print("-" * 50)

    # Check if JavaScript functions exist for the menu items
    js_functions_needed = [
        'fetchTodaysSales', 'fetchYesterdaysSales', 'fetchWeeklySales',
        'fetchOutstandingPayments', 'fetchExpensesBills', 'fetchStaffAttendance',
        'fetchStaffLeaveRequests', 'fetchStaffMessages', 'fetchSalarySummary',
        'showAddEmployeeForm', 'showHRSupportForm', 'showWhatsAppCampaignForm',
        'showCreatePromotionForm',
        # New functions
        'fetchTodaysSalesByProduct', 'fetchTodaysSalesAnalytics', 'exportTodaysSales',
        'fetchYesterdaysSalesByProduct', 'fetchYesterdaysSalesAnalytics', 'exportYesterdaysSales',
        'fetchWeeklyAnalytics', 'exportWeeklyReport', 'compareWeeklySales',
        'sendPaymentReminders', 'showUpdatePaymentForm', 'generatePaymentReport',
        'showAddExpenseForm', 'fetchMonthlyExpenseReport', 'showUpdateBillForm'
    ]

    try:
        with open('static/chat.js', 'r', encoding='utf-8') as f:
            js_content = f.read()

        js_implemented = 0
        js_missing = []

        for func_name in js_functions_needed:
            if func_name in js_content:
                js_implemented += 1
            else:
                js_missing.append(func_name)

        print(
            f"   ✅ JavaScript Functions Implemented: {js_implemented}/{len(js_functions_needed)}")
        if js_missing:
            print(
                f"   ⚠️  Missing JS Functions: {', '.join(js_missing[:5])}{'...' if len(js_missing) > 5 else ''}")

    except FileNotFoundError:
        print("   ❌ JavaScript file not found")
        js_implemented = 0

    # 4. Integration Score
    print("\\n4️⃣ INTEGRATION SUMMARY")
    print("-" * 50)

    db_score = min(100, (total_submenus / 43) * 100)  # 43 expected submenus
    api_score = (total_success / total_endpoints) * 100
    js_score = (js_implemented / len(js_functions_needed)) * 100
    overall_score = (db_score + api_score + js_score) / 3

    print(
        f"   📊 Database Menu Structure: {db_score:.1f}% ({total_submenus}/43 submenus)")
    print(
        f"   🌐 API Endpoints Coverage: {api_score:.1f}% ({total_success}/{total_endpoints} working)")
    print(
        f"   💻 JavaScript Integration: {js_score:.1f}% ({js_implemented}/{len(js_functions_needed)} functions)")
    print(f"   🎯 Overall Integration Score: {overall_score:.1f}%")

    # 5. Recommendations
    print("\\n5️⃣ RECOMMENDATIONS")
    print("-" * 50)

    if overall_score >= 90:
        print("   🎉 EXCELLENT! System is fully integrated and ready for production")
    elif overall_score >= 75:
        print("   ✅ GOOD! System is well integrated with minor improvements needed")
    elif overall_score >= 50:
        print("   ⚠️  MODERATE! System needs additional work for full integration")
    else:
        print("   ❌ POOR! System requires significant work for proper integration")

    if db_score < 100:
        print("   🔧 Add missing submenu entries to database")
    if api_score < 100:
        print("   🔧 Implement missing API endpoints")
    if js_score < 100:
        print("   🔧 Complete JavaScript function implementations")

    print("\\n" + "=" * 70)
    print("🏁 INTEGRATION TEST COMPLETE")

    return {
        'database_score': db_score,
        'api_score': api_score,
        'javascript_score': js_score,
        'overall_score': overall_score,
        'total_submenus': total_submenus,
        'working_endpoints': total_success,
        'total_endpoints': total_endpoints,
        'js_functions': js_implemented
    }


if __name__ == "__main__":
    test_complete_integration()
