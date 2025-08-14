#!/usr/bin/env python3
"""
Seed script for Employee data
Creates sample employee records for the HR chatbot system.
"""

from app.database import SessionLocal, engine
from app.models import Base, Employee
from datetime import date


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def seed_employees():
    """Create sample employee records"""
    db = SessionLocal()
    try:
        # Check if employees already exist
        existing_count = db.query(Employee).count()
        if existing_count > 0:
            print(f"Found {existing_count} existing employees. Skipping seed.")
            return

        employees = [
            Employee(
                employee_id="EMP001",
                employee_name="John Smith",
                email="john.smith@company.com",
                phone="+1-555-0101",
                employment_status="Active",
                department="Human Resources",
                position="HR Specialist",
                employment_type="Full-time",
                hire_date=date(2022, 3, 15),
                reporting_manager="Sarah Johnson",
                office_location="New York Office",
                salary_grade="G5"
            ),
            Employee(
                employee_id="EMP002",
                employee_name="Jane Doe",
                email="jane.doe@company.com",
                phone="+1-555-0102",
                employment_status="Active",
                department="Information Technology",
                position="Software Developer",
                employment_type="Full-time",
                hire_date=date(2021, 8, 1),
                reporting_manager="Michael Chen",
                office_location="San Francisco Office",
                salary_grade="G6"
            ),
            Employee(
                employee_id="EMP003",
                employee_name="Alice Johnson",
                email="alice.johnson@company.com",
                phone="+1-555-0103",
                employment_status="Active",
                department="Marketing",
                position="Marketing Coordinator",
                employment_type="Full-time",
                hire_date=date(2023, 1, 10),
                reporting_manager="Emily Davis",
                office_location="Remote",
                salary_grade="G4"
            ),
            Employee(
                employee_id="EMP004",
                employee_name="Robert Wilson",
                email="robert.wilson@company.com",
                phone="+1-555-0104",
                employment_status="Active",
                department="Finance",
                position="Financial Analyst",
                employment_type="Full-time",
                hire_date=date(2020, 11, 20),
                reporting_manager="Robert Kim",
                office_location="Chicago Office",
                salary_grade="G5"
            ),
            Employee(
                employee_id="EMP005",
                employee_name="Lisa Brown",
                email="lisa.brown@company.com",
                phone="+1-555-0105",
                employment_status="Active",
                department="Sales",
                position="Sales Representative",
                employment_type="Full-time",
                hire_date=date(2023, 6, 5),
                reporting_manager="Lisa Thompson",
                office_location="Dallas Office",
                salary_grade="G4"
            )
        ]

        # Add all employees to database
        for employee in employees:
            db.add(employee)

        db.commit()
        print(f"✅ Successfully created {len(employees)} employee records")

        # Print summary
        for emp in employees:
            print(
                f"   👤 {emp.employee_id}: {emp.position} ({emp.employment_status})")

    except Exception as e:
        print(f"❌ Error seeding employees: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting Employee database seeding...")
    create_tables()
    seed_employees()
    print("✨ Employee seeding completed!")
