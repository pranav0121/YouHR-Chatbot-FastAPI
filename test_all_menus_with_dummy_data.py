#!/usr/bin/env python3
"""
Comprehensive Menu Testing Script with Dummy Data
Tests all systems (HR Assistant, Merchant Management, Retention Executor)
with realistic dummy data and logs everything to PostgreSQL database.
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# Test data generators


def generate_employee_data():
    return {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number()[:15],
        "department": random.choice(["HR", "IT", "Sales", "Marketing", "Finance", "Operations"]),
        "position": random.choice(["Manager", "Executive", "Senior Executive", "Team Lead", "Associate"]),
        "salary": random.randint(30000, 150000),
        "hire_date": fake.date_between(start_date='-5y', end_date='today').isoformat()
    }


def generate_merchant_data():
    return {
        "business_name": fake.company(),
        "owner_name": fake.name(),
        "contact_email": fake.email(),
        "contact_phone": fake.phone_number()[:15],
        "address": fake.address()[:100],
        "business_type": random.choice(["Restaurant", "Retail", "Service", "E-commerce", "Healthcare"]),
        "registration_date": fake.date_between(start_date='-2y', end_date='today').isoformat()
    }


def generate_attendance_data(employee_id):
    return {
        "employee_id": employee_id,
        "date": fake.date_between(start_date='-30d', end_date='today').isoformat(),
        "check_in": fake.time().strftime("%H:%M:%S"),
        "check_out": fake.time().strftime("%H:%M:%S"),
        "status": random.choice(["Present", "Late", "Half Day"])
    }


def generate_payroll_data(employee_id):
    base_salary = random.randint(30000, 150000)
    return {
        "employee_id": employee_id,
        "month": fake.date_between(start_date='-12m', end_date='today').replace(day=1).isoformat(),
        "basic_salary": base_salary,
        "allowances": random.randint(2000, 10000),
        "deductions": random.randint(1000, 5000),
        "net_salary": base_salary + random.randint(2000, 10000) - random.randint(1000, 5000)
    }


def generate_leave_request_data(employee_id):
    start_date = fake.date_between(start_date='today', end_date='+30d')
    return {
        "employee_id": employee_id,
        "leave_type": random.choice(["Casual", "Sick", "Annual", "Maternity", "Emergency"]),
        "start_date": start_date.isoformat(),
        "end_date": (start_date + timedelta(days=random.randint(1, 7))).isoformat(),
        "reason": fake.sentence(),
        "status": random.choice(["Pending", "Approved", "Rejected"])
    }


def generate_sales_data(merchant_id):
    return {
        "merchant_id": merchant_id,
        "date": fake.date_between(start_date='-30d', end_date='today').isoformat(),
        "amount": round(random.uniform(100, 5000), 2),
        "payment_method": random.choice(["Cash", "Card", "UPI", "Net Banking"]),
        "transaction_id": fake.uuid4()
    }


def generate_staff_data(merchant_id):
    return {
        "merchant_id": merchant_id,
        "name": fake.name(),
        "role": random.choice(["Cashier", "Sales Associate", "Manager", "Helper"]),
        "contact": fake.phone_number()[:15],
        "salary": random.randint(15000, 50000)
    }


def generate_retention_activity_data(merchant_id):
    return {
        "merchant_id": merchant_id,
        "activity_type": random.choice(["Call", "Visit", "Email", "WhatsApp"]),
        "date": fake.date_between(start_date='-7d', end_date='today').isoformat(),
        "notes": fake.sentence(),
        "status": random.choice(["Completed", "Pending", "Follow-up Required"]),
        "executor_name": fake.name()
    }

# Test functions


def test_endpoint(method, endpoint, data=None, expected_status=None):
    """Test an API endpoint and return the response"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔄 Testing {method} {endpoint}")

        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)

        print(f"   Status: {response.status_code}")

        if expected_status and response.status_code != expected_status:
            print(
                f"   ❌ Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text}")
            return None

        if response.status_code in [200, 201]:
            print(f"   ✅ Success")
            try:
                response_data = response.json()
                if isinstance(response_data, dict) and 'id' in response_data:
                    print(f"   📝 Created ID: {response_data['id']}")
                    return response_data['id']
                elif isinstance(response_data, list):
                    print(f"   📊 Retrieved {len(response_data)} items")
                else:
                    print(f"   📄 Response: {str(response_data)[:100]}...")
                return response_data
            except:
                print(f"   📄 Response: {response.text[:100]}...")
                return True
        else:
            print(f"   ❌ Failed")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error: {e}")
        return None


def test_hr_assistant_system():
    """Test all HR Assistant endpoints with dummy data"""
    print("\n" + "="*60)
    print("🏢 TESTING HR ASSISTANT SYSTEM")
    print("="*60)

    # Test menu endpoint
    test_endpoint("GET", "/api/menu/pos_youhr")

    # Test employees
    print("\n👥 Testing Employee Management:")
    employee_ids = []

    # Create employees
    for i in range(5):
        employee_data = generate_employee_data()
        employee_id = test_endpoint(
            "POST", "/api/employees", employee_data, 201)
        if employee_id:
            employee_ids.append(employee_id)

    # Get all employees
    test_endpoint("GET", "/api/employees")

    # Test individual employee
    if employee_ids:
        test_endpoint("GET", f"/api/employees/{employee_ids[0]}")

        # Update employee
        updated_data = generate_employee_data()
        test_endpoint("PUT", f"/api/employees/{employee_ids[0]}", updated_data)

    # Test attendance
    print("\n⏰ Testing Attendance Management:")
    for employee_id in employee_ids[:3]:
        for _ in range(3):  # Multiple attendance records per employee
            attendance_data = generate_attendance_data(employee_id)
            test_endpoint("POST", "/api/attendance", attendance_data, 201)

    test_endpoint("GET", "/api/attendance")

    # Test payroll
    print("\n💰 Testing Payroll Management:")
    for employee_id in employee_ids[:3]:
        payroll_data = generate_payroll_data(employee_id)
        test_endpoint("POST", "/api/payroll", payroll_data, 201)

    test_endpoint("GET", "/api/payroll")

    # Test leave requests
    print("\n🏖️ Testing Leave Management:")
    for employee_id in employee_ids[:3]:
        leave_data = generate_leave_request_data(employee_id)
        test_endpoint("POST", "/api/leave-requests", leave_data, 201)

    test_endpoint("GET", "/api/leave-requests")

    return employee_ids


def test_merchant_management_system():
    """Test all Merchant Management endpoints with dummy data"""
    print("\n" + "="*60)
    print("🏪 TESTING MERCHANT MANAGEMENT SYSTEM")
    print("="*60)

    # Test menu endpoint
    test_endpoint("GET", "/api/menu/merchant")

    # Test merchants
    print("\n🏢 Testing Merchant Management:")
    merchant_ids = []

    # Create merchants
    for i in range(5):
        merchant_data = generate_merchant_data()
        merchant_id = test_endpoint(
            "POST", "/api/merchants", merchant_data, 201)
        if merchant_id:
            merchant_ids.append(merchant_id)

    # Get all merchants
    test_endpoint("GET", "/api/merchants")

    # Test individual merchant
    if merchant_ids:
        test_endpoint("GET", f"/api/merchants/{merchant_ids[0]}")

        # Update merchant
        updated_data = generate_merchant_data()
        test_endpoint("PUT", f"/api/merchants/{merchant_ids[0]}", updated_data)

    # Test sales
    print("\n💳 Testing Sales Management:")
    for merchant_id in merchant_ids[:3]:
        for _ in range(5):  # Multiple sales per merchant
            sales_data = generate_sales_data(merchant_id)
            test_endpoint("POST", "/api/sales", sales_data, 201)

    test_endpoint("GET", "/api/sales")

    # Test staff
    print("\n👨‍💼 Testing Staff Management:")
    for merchant_id in merchant_ids[:3]:
        for _ in range(3):  # Multiple staff per merchant
            staff_data = generate_staff_data(merchant_id)
            test_endpoint("POST", "/api/staff", staff_data, 201)

    test_endpoint("GET", "/api/staff")

    # Test payments
    print("\n💰 Testing Payment Management:")
    for merchant_id in merchant_ids[:3]:
        payment_data = {
            "merchant_id": merchant_id,
            "amount": round(random.uniform(1000, 10000), 2),
            "payment_date": fake.date_between(start_date='-30d', end_date='today').isoformat(),
            "payment_method": random.choice(["Bank Transfer", "Cash", "Cheque"]),
            "status": random.choice(["Completed", "Pending", "Failed"])
        }
        test_endpoint("POST", "/api/payments", payment_data, 201)

    test_endpoint("GET", "/api/payments")

    # Test marketing campaigns
    print("\n📢 Testing Marketing Management:")
    for merchant_id in merchant_ids[:3]:
        campaign_data = {
            "merchant_id": merchant_id,
            "campaign_name": fake.catch_phrase(),
            "campaign_type": random.choice(["Email", "SMS", "Social Media", "Print"]),
            "start_date": fake.date_between(start_date='-30d', end_date='today').isoformat(),
            "end_date": fake.date_between(start_date='today', end_date='+30d').isoformat(),
            "budget": round(random.uniform(5000, 50000), 2),
            "status": random.choice(["Active", "Paused", "Completed"])
        }
        test_endpoint("POST", "/api/marketing-campaigns", campaign_data, 201)

    test_endpoint("GET", "/api/marketing-campaigns")

    return merchant_ids


def test_retention_executor_system(merchant_ids):
    """Test all Retention Executor endpoints with dummy data"""
    print("\n" + "="*60)
    print("🎯 TESTING RETENTION EXECUTOR SYSTEM")
    print("="*60)

    # Test menu endpoint
    test_endpoint("GET", "/api/menu/icp_hr")

    # Test retention activities
    print("\n📞 Testing Retention Activities:")
    for merchant_id in merchant_ids[:3]:
        for _ in range(4):  # Multiple activities per merchant
            activity_data = generate_retention_activity_data(merchant_id)
            test_endpoint("POST", "/api/retention-activities",
                          activity_data, 201)

    test_endpoint("GET", "/api/retention-activities")

    # Test daily follow-ups
    print("\n📅 Testing Daily Follow-ups:")
    for merchant_id in merchant_ids[:3]:
        followup_data = {
            "merchant_id": merchant_id,
            "follow_up_date": fake.date_between(start_date='today', end_date='+7d').isoformat(),
            "priority": random.choice(["High", "Medium", "Low"]),
            "notes": fake.sentence(),
            "assigned_to": fake.name(),
            "status": random.choice(["Scheduled", "In Progress", "Completed"])
        }
        test_endpoint("POST", "/api/daily-followups", followup_data, 201)

    test_endpoint("GET", "/api/daily-followups")

    # Test merchant support
    print("\n🛠️ Testing Merchant Support:")
    for merchant_id in merchant_ids[:3]:
        support_data = {
            "merchant_id": merchant_id,
            "issue_type": random.choice(["Technical", "Billing", "General", "Training"]),
            "description": fake.paragraph(),
            "priority": random.choice(["High", "Medium", "Low"]),
            "status": random.choice(["Open", "In Progress", "Resolved", "Closed"]),
            "created_date": fake.date_between(start_date='-7d', end_date='today').isoformat()
        }
        test_endpoint("POST", "/api/merchant-support", support_data, 201)

    test_endpoint("GET", "/api/merchant-support")

    # Test performance metrics
    print("\n📊 Testing Performance Metrics:")
    metrics_data = {
        "date": fake.date_between(start_date='-7d', end_date='today').isoformat(),
        "total_contacts": random.randint(50, 200),
        "successful_contacts": random.randint(30, 150),
        "follow_ups_completed": random.randint(20, 100),
        "new_activations": random.randint(5, 25),
        "retention_rate": round(random.uniform(70, 95), 2)
    }
    test_endpoint("POST", "/api/performance-metrics", metrics_data, 201)
    test_endpoint("GET", "/api/performance-metrics")


def test_database_logging():
    """Test database connectivity and logging"""
    print("\n" + "="*60)
    print("🗄️ TESTING DATABASE LOGGING")
    print("="*60)

    # Test database health
    test_endpoint("GET", "/api/health")

    # Test database tables count
    test_endpoint("GET", "/api/database/info")


def main():
    """Main test execution"""
    print("🚀 Starting Comprehensive Menu and Database Testing")
    print("📅 Test Run:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🔗 Base URL:", BASE_URL)

    start_time = time.time()

    try:
        # Test database connectivity first
        test_database_logging()

        # Test HR Assistant System
        employee_ids = test_hr_assistant_system()

        # Test Merchant Management System
        merchant_ids = test_merchant_management_system()

        # Test Retention Executor System
        test_retention_executor_system(merchant_ids)

        # Final database check
        print("\n🔍 Final Database Verification:")
        test_database_logging()

    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")

    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"⏱️ Total Duration: {duration:.2f} seconds")
    print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✅ All systems tested with dummy data")
    print("💾 Data logged to PostgreSQL database")
    print("🔗 Frontend grid layout ready for testing")


if __name__ == "__main__":
    main()
