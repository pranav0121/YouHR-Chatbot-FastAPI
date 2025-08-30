from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import ChatbotMenu, ChatbotSubmenu, Base
from datetime import date

# Create tables
Base.metadata.create_all(bind=engine)


def seed_merchant_menus():
    db = SessionLocal()

    try:
        # Clear existing merchant menus
        db.query(ChatbotSubmenu).filter(
            ChatbotSubmenu.company_type == "merchant").delete()
        db.query(ChatbotMenu).filter(
            ChatbotMenu.company_type == "merchant").delete()
        db.commit()

        # Create Merchant Management Menu
        merchant_menu = ChatbotMenu(
            menu_key="merchant_management",
            menu_title="Merchant Management",
            menu_icon="🏪",
            is_active=True,
            company_type="merchant",
            role="admin"
        )
        db.add(merchant_menu)
        db.flush()

        # Merchant Management Submenus
        merchant_submenus = [
            # Sales Analytics
            {
                "submenu_key": "sales_today",
                "submenu_title": "Today's Sales",
                "api_endpoint": "/api/merchant/sales/today"
            },
            {
                "submenu_key": "sales_yesterday",
                "submenu_title": "Yesterday's Sales",
                "api_endpoint": "/api/merchant/sales/yesterday"
            },
            {
                "submenu_key": "sales_weekly",
                "submenu_title": "Weekly Sales Report",
                "api_endpoint": "/api/merchant/sales/weekly"
            },

            # Financial Management
            {
                "submenu_key": "outstanding_payments",
                "submenu_title": "Outstanding Payments",
                "api_endpoint": "/api/merchant/payments/outstanding"
            },
            {
                "submenu_key": "expense_bills",
                "submenu_title": "Expenses & Bills",
                "api_endpoint": "/api/merchant/expenses/bills"
            },

            # Staff Management
            {
                "submenu_key": "staff_attendance",
                "submenu_title": "Staff Attendance",
                "api_endpoint": "/api/merchant/staff/attendance"
            },
            {
                "submenu_key": "staff_leave_requests",
                "submenu_title": "Leave Requests",
                "api_endpoint": "/api/merchant/staff/leave-requests"
            },
            {
                "submenu_key": "staff_messages",
                "submenu_title": "Staff Messages",
                "api_endpoint": "/api/merchant/staff/messages"
            },
            {
                "submenu_key": "add_employee",
                "submenu_title": "Add New Employee",
                "api_endpoint": "/api/merchant/staff/add-employee"
            },
            {
                "submenu_key": "staff_salary",
                "submenu_title": "Salary Information",
                "api_endpoint": "/api/merchant/staff/salary"
            },
            {
                "submenu_key": "hr_support",
                "submenu_title": "HR Support",
                "api_endpoint": "/api/merchant/staff/hr-support"
            },

            # Marketing Tools
            {
                "submenu_key": "whatsapp_campaign",
                "submenu_title": "WhatsApp Campaign",
                "api_endpoint": "/api/merchant/marketing/whatsapp-campaign"
            },
            {
                "submenu_key": "instant_promotion",
                "submenu_title": "Create Promotion",
                "api_endpoint": "/api/merchant/marketing/instant-promotion"
            }
        ]

        for submenu_data in merchant_submenus:
            submenu = ChatbotSubmenu(
                menu_id=merchant_menu.id,
                submenu_key=submenu_data["submenu_key"],
                submenu_title=submenu_data["submenu_title"],
                api_endpoint=submenu_data["api_endpoint"],
                is_active=True,
                company_type="merchant",
                role="admin"
            )
            db.add(submenu)

        # Keep existing HR menus and update them
        hr_menu = db.query(ChatbotMenu).filter(
            ChatbotMenu.menu_key == "hr_assistant",
            ChatbotMenu.company_type == "pos_youhr"
        ).first()

        if not hr_menu:
            # Create HR Assistant Menu
            hr_menu = ChatbotMenu(
                menu_key="hr_assistant",
                menu_title="HR Assistant",
                menu_icon="👥",
                is_active=True,
                company_type="pos_youhr",
                role="employee"
            )
            db.add(hr_menu)
            db.flush()

            # HR Assistant Submenus
            hr_submenus = [
                {
                    "submenu_key": "attendance_history",
                    "submenu_title": "Attendance & Time Management",
                    "api_endpoint": "/api/attendance/history"
                },
                {
                    "submenu_key": "leave_management",
                    "submenu_title": "Leave Management",
                    "api_endpoint": "/api/leave/applications"
                },
                {
                    "submenu_key": "payroll",
                    "submenu_title": "Payroll",
                    "api_endpoint": "/api/payroll/payslips"
                },
                {
                    "submenu_key": "employee_info",
                    "submenu_title": "Employee Information",
                    "api_endpoint": "/api/employee/status"
                }
            ]

            for submenu_data in hr_submenus:
                submenu = ChatbotSubmenu(
                    menu_id=hr_menu.id,
                    submenu_key=submenu_data["submenu_key"],
                    submenu_title=submenu_data["submenu_title"],
                    api_endpoint=submenu_data["api_endpoint"],
                    is_active=True,
                    company_type="pos_youhr",
                    role="employee"
                )
                db.add(submenu)

        db.commit()
        print("✅ Merchant menus seeded successfully!")
        print(
            f"✅ Created Merchant Management menu with {len(merchant_submenus)} submenus")
        print("✅ HR Assistant menu maintained")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding merchant menus: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding merchant management menus...")
    seed_merchant_menus()
