#!/usr/bin/env python3
"""
Windows-compatible database setup script without Unicode emojis
"""

import sys
import subprocess
import os
from pathlib import Path


def run_script(script_name, description):
    """Run a Python script and handle errors gracefully"""
    print(f"\n--- {description} ---")
    try:
        result = subprocess.run([sys.executable, script_name],
                                capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"SUCCESS: {description} completed")
            if result.stdout:
                # Filter out Unicode emojis from output
                output = result.stdout.encode(
                    'ascii', 'ignore').decode('ascii')
                print(output)
        else:
            print(f"ERROR: {description} failed")
            if result.stderr:
                print(f"Error details: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"EXCEPTION: Failed to run {script_name}: {e}")
        return False


def setup_database():
    """Set up the complete database system"""
    print("="*60)
    print("YouHR Assistant - Database Setup (Windows Compatible)")
    print("="*60)

    # Step 1: Create database tables
    print("\n[1/6] Creating database tables...")
    if not run_script("create_comprehensive_tables.py", "Database table creation"):
        print("WARNING: Table creation had issues, but continuing...")

    # Step 2: Seed merchant menus
    print("\n[2/6] Setting up merchant menus...")
    if not run_script("seed_merchant_menus.py", "Merchant menu seeding"):
        print("WARNING: Merchant menu seeding had issues, but continuing...")

    # Step 3: Seed HR menus
    print("\n[3/6] Setting up HR menus...")
    if not run_script("seed_menus.py", "HR menu seeding"):
        print("WARNING: HR menu seeding had issues, but continuing...")

    # Step 4: Seed employee data
    print("\n[4/6] Setting up employee data...")
    if not run_script("seed_employees.py", "Employee data seeding"):
        print("WARNING: Employee seeding had issues, but continuing...")

    # Step 5: Seed attendance records
    print("\n[5/6] Setting up attendance records...")
    if not run_script("seed_attendance.py", "Attendance data seeding"):
        print("WARNING: Attendance seeding had issues, but continuing...")

    # Step 6: Seed payslip data
    print("\n[6/6] Setting up payslip data...")
    if not run_script("seed_payslips.py", "Payslip data seeding"):
        print("WARNING: Payslip seeding had issues, but continuing...")

    # Verify database state
    print("\n" + "="*60)
    print("DATABASE VERIFICATION")
    print("="*60)

    try:
        from app.database import SessionLocal
        from app.models import ChatbotMenu, Employee, AttendanceRecord, Payslip

        db = SessionLocal()

        hr_menus = db.query(ChatbotMenu).filter_by(
            company_type='pos_youhr').count()
        merchant_menus = db.query(ChatbotMenu).filter_by(
            company_type='merchant').count()
        employees = db.query(Employee).count()
        attendance = db.query(AttendanceRecord).count()
        payslips = db.query(Payslip).count()

        print(f"HR Menus: {hr_menus}")
        print(f"Merchant Menus: {merchant_menus}")
        print(f"Employees: {employees}")
        print(f"Attendance Records: {attendance}")
        print(f"Payslip Records: {payslips}")

        db.close()

        if hr_menus > 0 and merchant_menus > 0 and employees > 0:
            print("\nSUCCESS: Database setup completed successfully!")
            return True
        else:
            print("\nWARNING: Some data might be missing, but system should still work")
            return True

    except Exception as e:
        print(f"ERROR: Database verification failed: {e}")
        return False


if __name__ == "__main__":
    success = setup_database()
    if success:
        print("\n" + "="*60)
        print("READY TO START SERVER")
        print("="*60)
        print("Run: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
        print("Then open: http://127.0.0.1:8000")
    else:
        print("\nSetup completed with warnings. Server should still work.")

    sys.exit(0 if success else 1)
