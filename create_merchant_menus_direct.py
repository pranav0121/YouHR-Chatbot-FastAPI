#!/usr/bin/env python3
"""
Direct merchant menu creation without Unicode emojis
"""

from app.database import SessionLocal, engine
from app.models import Base, ChatbotMenu, ChatbotSubmenu


def create_merchant_menus():
    """Create merchant management menus directly"""

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if merchant menus already exist
        existing_merchant = db.query(ChatbotMenu).filter_by(
            company_type='merchant').first()
        if existing_merchant:
            print("Merchant menus already exist. Skipping creation.")
            return True

        print("Creating merchant management menus...")

        # Create main merchant management menus
        menus_data = [
            {
                'menu_title': 'Today\'s Sales',
                'menu_key': 'todays_sales',
                'submenus': [
                    {
                        'submenu_title': 'View Today\'s Sales',
                        'submenu_key': 'view_todays_sales',
                        'api_endpoint': '/api/merchant/sales/today'
                    }
                ]
            },
            {
                'menu_title': 'Yesterday\'s Sales',
                'menu_key': 'yesterdays_sales',
                'submenus': [
                    {
                        'submenu_title': 'View Yesterday\'s Sales',
                        'submenu_key': 'view_yesterdays_sales',
                        'api_endpoint': '/api/merchant/sales/yesterday'
                    }
                ]
            },
            {
                'menu_title': 'Weekly Sales Report',
                'menu_key': 'weekly_sales',
                'submenus': [
                    {
                        'submenu_title': 'View Weekly Sales',
                        'submenu_key': 'view_weekly_sales',
                        'api_endpoint': '/api/merchant/sales/weekly'
                    }
                ]
            },
            {
                'menu_title': 'Outstanding Payments',
                'menu_key': 'outstanding_payments',
                'submenus': [
                    {
                        'submenu_title': 'View Outstanding Payments',
                        'submenu_key': 'view_outstanding_payments',
                        'api_endpoint': '/api/merchant/payments/outstanding'
                    }
                ]
            },
            {
                'menu_title': 'Expenses & Bills',
                'menu_key': 'expenses_bills',
                'submenus': [
                    {
                        'submenu_title': 'View Expenses & Bills',
                        'submenu_key': 'view_expenses_bills',
                        'api_endpoint': '/api/merchant/expenses/bills'
                    }
                ]
            },
            {
                'menu_title': 'Staff Attendance',
                'menu_key': 'staff_attendance',
                'submenus': [
                    {
                        'submenu_title': 'View Staff Attendance',
                        'submenu_key': 'view_staff_attendance',
                        'api_endpoint': '/api/merchant/staff/attendance'
                    }
                ]
            },
            {
                'menu_title': 'Staff Leave Requests',
                'menu_key': 'staff_leave',
                'submenus': [
                    {
                        'submenu_title': 'View Leave Requests',
                        'submenu_key': 'view_staff_leave',
                        'api_endpoint': '/api/merchant/staff/leave-requests'
                    }
                ]
            },
            {
                'menu_title': 'Staff Messages',
                'menu_key': 'staff_messages',
                'submenus': [
                    {
                        'submenu_title': 'View Staff Messages',
                        'submenu_key': 'view_staff_messages',
                        'api_endpoint': '/api/merchant/staff/messages'
                    }
                ]
            },
            {
                'menu_title': 'Salary Information',
                'menu_key': 'salary_info',
                'submenus': [
                    {
                        'submenu_title': 'View Salary Information',
                        'submenu_key': 'view_salary_info',
                        'api_endpoint': '/api/merchant/staff/salary'
                    }
                ]
            },
            {
                'menu_title': 'Add New Employee',
                'menu_key': 'add_employee',
                'submenus': [
                    {
                        'submenu_title': 'Add Employee Form',
                        'submenu_key': 'add_employee_form',
                        'api_endpoint': '/api/merchant/staff/add-employee'
                    }
                ]
            },
            {
                'menu_title': 'HR Support',
                'menu_key': 'hr_support',
                'submenus': [
                    {
                        'submenu_title': 'Submit Support Request',
                        'submenu_key': 'hr_support_form',
                        'api_endpoint': '/api/merchant/hr/support'
                    }
                ]
            },
            {
                'menu_title': 'WhatsApp Marketing',
                'menu_key': 'whatsapp_marketing',
                'submenus': [
                    {
                        'submenu_title': 'Create WhatsApp Campaign',
                        'submenu_key': 'whatsapp_campaign_form',
                        'api_endpoint': '/api/merchant/marketing/whatsapp-campaign'
                    }
                ]
            },
            {
                'menu_title': 'Create Promotion',
                'menu_key': 'create_promotion',
                'submenus': [
                    {
                        'submenu_title': 'Create New Promotion',
                        'submenu_key': 'create_promotion_form',
                        'api_endpoint': '/api/merchant/marketing/promotion'
                    }
                ]
            }
        ]

        # Insert menus and submenus
        for menu_data in menus_data:
            # Create main menu
            menu = ChatbotMenu(
                company_type='merchant',
                menu_title=menu_data['menu_title'],
                menu_key=menu_data['menu_key']
            )
            db.add(menu)
            db.flush()  # Get the menu ID

            # Create submenus
            for submenu_data in menu_data['submenus']:
                submenu = ChatbotSubmenu(
                    menu_id=menu.id,
                    submenu_title=submenu_data['submenu_title'],
                    submenu_key=submenu_data['submenu_key'],
                    api_endpoint=submenu_data['api_endpoint']
                )
                db.add(submenu)

        db.commit()
        print(
            f"SUCCESS: Created {len(menus_data)} merchant menus with submenus")
        return True

    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to create merchant menus: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = create_merchant_menus()
    if success:
        print("Merchant menus created successfully!")
    else:
        print("Failed to create merchant menus!")
