#!/usr/bin/env python3
"""
YouHR Assistant - HR & Merchant Management System
Comprehensive FastAPI Backend Startup Script
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True,
                                check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False


def main():
    """Main startup function"""
    print("🚀 Starting YouHR Assistant - HR & Merchant Management System")
    print("=" * 60)

    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Please run this script from the chatbot_backend directory")
        sys.exit(1)

    # Step 1: Create database tables
    print("\n📋 Step 1: Setting up database")
    if not run_command("python create_comprehensive_tables.py", "Creating database tables"):
        print("⚠️ Database setup failed, but continuing...")

    # Step 2: Seed merchant menus
    print("\n🌱 Step 2: Seeding merchant menus")
    if not run_command("python seed_merchant_menus.py", "Seeding merchant management menus"):
        print("⚠️ Menu seeding failed, but continuing...")

    # Step 3: Seed HR menus (if needed)
    print("\n🌱 Step 3: Seeding HR data")
    if os.path.exists("seed_menus.py"):
        if not run_command("python seed_menus.py", "Seeding HR menus"):
            print("⚠️ HR menu seeding failed, but continuing...")

    # Step 4: Seed sample data
    print("\n📊 Step 4: Seeding sample data")
    seed_files = [
        ("seed_employees.py", "employee data"),
        ("seed_attendance.py", "attendance records"),
        ("seed_payslips.py", "payslip data")
    ]

    for seed_file, description in seed_files:
        if os.path.exists(seed_file):
            run_command(f"python {seed_file}", f"Seeding {description}")

    # Step 5: Start the FastAPI server
    print("\n🌐 Step 5: Starting FastAPI server")
    print("=" * 60)
    print("🎯 Server will be available at:")
    print("   • Main Interface: http://127.0.0.1:8000")
    print("   • API Documentation: http://127.0.0.1:8000/docs")
    print("   • Alternative Docs: http://127.0.0.1:8000/redoc")
    print("\n📱 Available Systems:")
    print("   • HR Assistant - Employee management, attendance, payroll")
    print("   • Merchant Management - Sales analytics, staff management, marketing")
    print("\n🔗 Key API Endpoints:")
    print("   HR Endpoints:")
    print("     GET  /api/attendance/history")
    print("     POST /api/leave/apply")
    print("     GET  /api/payroll/payslips")
    print("     GET  /api/employee/status")
    print("\n   Merchant Endpoints:")
    print("     GET  /api/merchant/sales/today")
    print("     GET  /api/merchant/staff/attendance")
    print("     POST /api/merchant/marketing/whatsapp-campaign")
    print("     POST /api/merchant/staff/add-employee")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 60)

    # Start uvicorn server
    try:
        subprocess.run([
            "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to start server: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("   2. Check if port 8000 is already in use")
        print("   3. Verify you're in the correct directory")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
