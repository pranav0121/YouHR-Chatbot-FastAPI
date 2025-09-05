from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatbotMenu, ChatbotSubmenu


def populate_chatbot_menus(db: Session):
    """Populate chatbot menus and submenus with initial data."""
    # Clear existing data
    db.query(ChatbotSubmenu).delete()
    db.query(ChatbotMenu).delete()
    db.commit()

    # Build menus matching the frontend screenshots (merchant & HR)
    menus = []

    # POS YouHR (HR Assistant) - company_type 'pos_youhr' used by frontend
    menus.append(
        ChatbotMenu(
            menu_key="hr_ops",
            menu_title="HR Operations",
            menu_icon="�",
            company_type="pos_youhr",
            role="employee",
            submenus=[
                ChatbotSubmenu(submenu_key="attendance_history", submenu_title="Attendance History",
                               api_endpoint="/api/attendance/history", company_type="pos_youhr", role="employee"),
                ChatbotSubmenu(submenu_key="apply_leave", submenu_title="Apply for Leave",
                               api_endpoint="/api/leave/apply", company_type="pos_youhr", role="employee"),
                ChatbotSubmenu(submenu_key="view_leave_applications", submenu_title="View Leave Applications",
                               api_endpoint="/api/leave/applications", company_type="pos_youhr", role="employee"),
                ChatbotSubmenu(submenu_key="view_payslips", submenu_title="View Payslips",
                               api_endpoint="/api/payroll/payslips", company_type="pos_youhr", role="employee"),
                ChatbotSubmenu(submenu_key="employee_status", submenu_title="Check Employee Status",
                               api_endpoint="/api/employee/status", company_type="pos_youhr", role="employee")
            ]
        )
    )

    # Merchant menus - create entries that cover both the special-case the API expects
    # (company_type 'icp_hr' with role 'merchant_manager') and a direct 'merchant' set

    merchant_categories = [
        ("sales_money", "Sales & Money", [
            ("today_sales", "Today's Sales", "/api/merchant/sales/today"),
            ("yesterday_sales", "Yesterday's Sales",
             "/api/merchant/sales/yesterday"),
            ("weekly_sales", "Weekly Sales", "/api/merchant/sales/weekly"),
            ("outstanding_payments", "Outstanding Payments",
             "/api/merchant/payments/outstanding"),
            ("expenses_bills", "Expenses & Bills", "/api/merchant/expenses/bills")
        ]),
        ("my_staff", "My Staff", [
            ("view_attendance", "View Attendance",
             "/api/merchant/staff/attendance"),
            ("approve_leave_requests", "Approve Leave Requests",
             "/api/merchant/staff/leave-requests"),
            ("messages_from_staff", "Messages from Staff",
             "/api/merchant/staff/messages"),
            ("add_new_employee", "Add New Employee",
             "/api/merchant/staff/add-employee"),
            ("view_mark_salary", "View/Mark Salary Paid",
             "/api/merchant/staff/salary"),
            ("hr_support", "HR Support Issue", "/api/merchant/staff/hr-support")
        ]),
        ("marketing_growth", "Marketing & Growth", [
            ("whatsapp_campaign", "Run WhatsApp Campaign",
             "/api/merchant/marketing/whatsapp-campaign"),
            ("instant_promo", "Send Instant Promotion",
             "/api/merchant/marketing/instant-promotion"),
            ("campaign_results", "Check Campaign Results",
             "/api/merchant/marketing/results"),
            ("loan_status", "Check Loan Status", "/api/merchant/loans/status"),
            ("continue_loan", "Continue Loan Application",
             "/api/merchant/loans/continue")
        ]),
        ("notifications", "Notifications", [
            ("approve_leave_requests_pending", "Approve Pending Leave Requests",
             "/api/merchant/notifications/approve-leave"),
            ("approve_shift_changes", "Approve Shift Change Requests",
             "/api/merchant/notifications/approve-shift"),
            ("payment_settlement_update", "Latest Payment Settlement Update",
             "/api/merchant/notifications/payment-settlement"),
            ("renew_subscription", "Renew Subscription",
             "/api/merchant/notifications/renew-subscription"),
            ("head_office_messages", "Messages from Head Office",
             "/api/merchant/notifications/head-office"),
            ("manage_notification_settings", "Manage Notification Settings",
             "/api/merchant/notifications/settings")
        ]),
        ("help_support", "Help & Support", [
            ("report_pos_app", "Report POS App Problem",
             "/api/merchant/help/report-pos"),
            ("report_hardware", "Report Hardware Issue",
             "/api/merchant/help/report-hardware"),
            ("report_camera", "Report AI Camera Problem",
             "/api/merchant/help/report-camera"),
            ("request_camera_install", "Request Camera Installation/Training",
             "/api/merchant/help/request-camera"),
            ("general_support", "Ask for General Support",
             "/api/merchant/help/general")
        ]),
        ("feedback_ideas", "Feedback & Ideas", [
            ("rate_experience", "Rate Your Experience",
             "/api/merchant/feedback/rate"),
            ("share_feedback", "Share Feedback", "/api/merchant/feedback-ideas"),
            ("suggest_feature", "Suggest a Feature",
             "/api/merchant/feedback/suggest"),
            ("view_past_suggestions", "View Past Suggestions",
             "/api/merchant/feedback/list")
        ])
    ]

    # Insert two sets: one for 'icp_hr' role='merchant_manager' (API special case)
    # and one for direct 'merchant' company_type to be robust.
    for company_type_value, role_value in [("icp_hr", "merchant_manager"), ("merchant", "manager")]:
        for cat_key, cat_title, opts in merchant_categories:
            menu = ChatbotMenu(
                menu_key=f"merchant_{cat_key}",
                menu_title=cat_title,
                menu_icon="📋",
                company_type=company_type_value,
                role=role_value,
                submenus=[]
            )
            for skey, stitle, endpoint in opts:
                submenu = ChatbotSubmenu(
                    submenu_key=f"{company_type_value}_{skey}",
                    submenu_title=stitle,
                    api_endpoint=endpoint,
                    company_type=company_type_value,
                    role=role_value
                )
                menu.submenus.append(submenu)

            menus.append(menu)

    db.add_all(menus)
    db.commit()
    print("Chatbot menus and submenus populated successfully.")


if __name__ == "__main__":
    db = next(get_db())
    populate_chatbot_menus(db)
