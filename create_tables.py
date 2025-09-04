from app.database import Base, engine, SessionLocal
from app.models import Menu, Submenu, Payslip, EmployeeStatus


def seed_data():
    db = SessionLocal()
    try:
        # Seed sample menus
        menu = Menu(menu_key="sales", menu_title="Sales", is_active=True)
        db.add(menu)
        db.commit()

        # Seed sample payslips
        payslip = Payslip(employee_id="E001", employee_name="John Doe",
                          month="August 2025", amount=5000, status="Paid")
        db.add(payslip)
        db.commit()

        # Seed sample employee status
        employee_status = EmployeeStatus(
            employee_id="E001", employee_name="John Doe", status="Active")
        db.add(employee_status)
        db.commit()

        print("Sample data seeded successfully.")
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    print("Seeding data...")
    seed_data()
