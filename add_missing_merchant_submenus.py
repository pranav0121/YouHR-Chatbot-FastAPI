from app.database import get_db
from app import models


def add_missing_submenus():
    db = next(get_db())

    # Get existing merchant menus
    merchant_menus = db.query(models.ChatbotMenu).filter(
        models.ChatbotMenu.company_type == 'merchant').all()
    menu_dict = {menu.menu_title: menu.id for menu in merchant_menus}

    print(f"Found {len(menu_dict)} merchant menus")

    # Define all missing submenus to add
    missing_submenus = [
        # Today's Sales (additional submenus)
        {"menu_title": "Today's Sales", "submenu_key": "today_sales_by_product",
            "submenu_title": "View Sales by Product", "endpoint": "/api/merchant/sales/today/by-product"},
        {"menu_title": "Today's Sales", "submenu_key": "today_sales_analytics",
            "submenu_title": "View Sales Analytics", "endpoint": "/api/merchant/sales/today/analytics"},
        {"menu_title": "Today's Sales", "submenu_key": "today_export_sales",
            "submenu_title": "Export Today's Sales", "endpoint": "/api/merchant/sales/today/export"},

        # Yesterday's Sales (additional submenus)
        {"menu_title": "Yesterday's Sales", "submenu_key": "yesterday_by_product",
            "submenu_title": "View Sales by Product", "endpoint": "/api/merchant/sales/yesterday/by-product"},
        {"menu_title": "Yesterday's Sales", "submenu_key": "yesterday_analytics",
            "submenu_title": "View Sales Analytics", "endpoint": "/api/merchant/sales/yesterday/analytics"},
        {"menu_title": "Yesterday's Sales", "submenu_key": "yesterday_export_sales",
            "submenu_title": "Export Yesterday's Sales", "endpoint": "/api/merchant/sales/yesterday/export"},

        # Weekly Sales Report (additional submenus)
        {"menu_title": "Weekly Sales Report", "submenu_key": "weekly_analytics",
            "submenu_title": "View Weekly Analytics", "endpoint": "/api/merchant/sales/weekly/analytics"},
        {"menu_title": "Weekly Sales Report", "submenu_key": "weekly_export_report",
            "submenu_title": "Export Weekly Report", "endpoint": "/api/merchant/sales/weekly/export"},
        {"menu_title": "Weekly Sales Report", "submenu_key": "weekly_compare",
            "submenu_title": "Compare with Previous Week", "endpoint": "/api/merchant/sales/weekly/compare"},

        # Outstanding Payments (additional submenus)
        {"menu_title": "Outstanding Payments", "submenu_key": "payment_send_reminders",
            "submenu_title": "Send Payment Reminders", "endpoint": "/api/merchant/payments/send-reminders"},
        {"menu_title": "Outstanding Payments", "submenu_key": "payment_update_status",
            "submenu_title": "Update Payment Status", "endpoint": "/api/merchant/payments/update-status"},
        {"menu_title": "Outstanding Payments", "submenu_key": "payment_generate_report",
            "submenu_title": "Generate Payment Report", "endpoint": "/api/merchant/payments/report"},

        # Expenses & Bills (additional submenus)
        {"menu_title": "Expenses & Bills", "submenu_key": "expense_add_new",
            "submenu_title": "Add New Expense", "endpoint": "/api/merchant/expenses/add"},
        {"menu_title": "Expenses & Bills", "submenu_key": "expense_monthly_report",
            "submenu_title": "Monthly Expense Report", "endpoint": "/api/merchant/expenses/monthly-report"},
        {"menu_title": "Expenses & Bills", "submenu_key": "expense_update_bill",
            "submenu_title": "Update Bill Status", "endpoint": "/api/merchant/expenses/update-bill"},

        # Staff Attendance (additional submenus)
        {"menu_title": "Staff Attendance", "submenu_key": "staff_mark_attendance",
            "submenu_title": "Mark Staff Attendance", "endpoint": "/api/merchant/staff/mark-attendance"},
        {"menu_title": "Staff Attendance", "submenu_key": "staff_attendance_report",
            "submenu_title": "Monthly Attendance Report", "endpoint": "/api/merchant/staff/attendance-report"},

        # Staff Leave Requests (additional submenus)
        {"menu_title": "Staff Leave Requests", "submenu_key": "staff_approve_leave",
            "submenu_title": "Approve Leave Request", "endpoint": "/api/merchant/staff/approve-leave"},
        {"menu_title": "Staff Leave Requests", "submenu_key": "staff_reject_leave",
            "submenu_title": "Reject Leave Request", "endpoint": "/api/merchant/staff/reject-leave"},

        # Staff Messages (additional submenus)
        {"menu_title": "Staff Messages", "submenu_key": "staff_send_message",
            "submenu_title": "Send Staff Message", "endpoint": "/api/merchant/staff/send-message"},
        {"menu_title": "Staff Messages", "submenu_key": "staff_broadcast_all",
            "submenu_title": "Broadcast to All Staff", "endpoint": "/api/merchant/staff/broadcast"},

        # Salary Information (additional submenus)
        {"menu_title": "Salary Information", "submenu_key": "staff_generate_payslip",
            "submenu_title": "Generate Payslip", "endpoint": "/api/merchant/staff/generate-payslip"},
        {"menu_title": "Salary Information", "submenu_key": "staff_update_salary",
            "submenu_title": "Update Salary", "endpoint": "/api/merchant/staff/update-salary"},

        # Add New Employee (additional submenus)
        {"menu_title": "Add New Employee", "submenu_key": "staff_employee_onboarding",
            "submenu_title": "Employee Onboarding", "endpoint": "/api/merchant/staff/employee-onboarding"},
        {"menu_title": "Add New Employee", "submenu_key": "staff_bulk_import",
            "submenu_title": "Bulk Import Employees", "endpoint": "/api/merchant/staff/bulk-import"},

        # HR Support (additional submenus)
        {"menu_title": "HR Support", "submenu_key": "hr_view_tickets",
            "submenu_title": "View Support Tickets", "endpoint": "/api/merchant/hr/tickets"},
        {"menu_title": "HR Support", "submenu_key": "hr_resources_portal",
            "submenu_title": "HR Resources", "endpoint": "/api/merchant/hr/resources"},

        # WhatsApp Marketing (additional submenus)
        {"menu_title": "WhatsApp Marketing", "submenu_key": "marketing_customer_notifications",
            "submenu_title": "Customer Notifications", "endpoint": "/api/merchant/marketing/customer-notifications"},
        {"menu_title": "WhatsApp Marketing", "submenu_key": "marketing_analytics_dashboard",
            "submenu_title": "Marketing Analytics", "endpoint": "/api/merchant/marketing/analytics"},

        # Create Promotion (additional submenus)
        {"menu_title": "Create Promotion", "submenu_key": "marketing_manage_promotions",
            "submenu_title": "Manage Active Promotions", "endpoint": "/api/merchant/marketing/manage-promotions"},
    ]

    added_count = 0
    for submenu_data in missing_submenus:
        menu_title = submenu_data["menu_title"]
        if menu_title in menu_dict:
            menu_id = menu_dict[menu_title]

            # Check if submenu already exists
            existing = db.query(models.ChatbotSubmenu).filter(
                models.ChatbotSubmenu.menu_id == menu_id,
                models.ChatbotSubmenu.submenu_key == submenu_data["submenu_key"]
            ).first()

            if not existing:
                new_submenu = models.ChatbotSubmenu(
                    menu_id=menu_id,
                    submenu_key=submenu_data["submenu_key"],
                    submenu_title=submenu_data["submenu_title"],
                    api_endpoint=submenu_data["endpoint"],
                    is_active=True,
                    company_type='merchant',
                    role=None
                )
                db.add(new_submenu)
                added_count += 1
                print(
                    f"Added: {submenu_data['submenu_title']} -> {submenu_data['endpoint']}")

    db.commit()
    print(f"\nAdded {added_count} new submenus to the database")

    # Verify total count
    total_submenus = db.query(models.ChatbotSubmenu).join(models.ChatbotMenu).filter(
        models.ChatbotMenu.company_type == 'merchant'
    ).count()
    print(f"Total merchant submenus now: {total_submenus}")


if __name__ == "__main__":
    add_missing_submenus()
