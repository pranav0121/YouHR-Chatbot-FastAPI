from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base
import sys


def create_all_tables():
    """Create all database tables"""
    try:
        print("🗄️ Creating all database tables...")

        # Create all tables
        Base.metadata.create_all(bind=engine)

        print("✅ All tables created successfully!")
        print("\n📋 Tables created:")
        print("  • chatbot_menus - Menu structure")
        print("  • chatbot_submenus - Submenu items")
        print("  • attendance_records - Employee attendance")
        print("  • leave_applications - Leave requests")
        print("  • payslips - Payroll information")
        print("  • employees - Employee master data")
        print("  • hr_support_tickets - HR support requests")
        print("  • marketing_campaigns - Marketing campaigns")
        print("  • promotions - Sales promotions")
        print("  • sales_records - Sales transactions")
        print("  • expense_records - Business expenses")
        print("  • inventory_items - Inventory management")
        print("  • customer_data - Customer information")
        print("  • staff_messages - Internal messaging")
        print("  • work_schedules - Staff scheduling")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_all_tables()
