
from app.database import SessionLocal
from app.models import ChatbotMenu, ChatbotSubmenu

# Create DB session
db = SessionLocal()

# ----------- CLEAR EXISTING DATA -----------
db.query(ChatbotSubmenu).delete()
db.query(ChatbotMenu).delete()
db.commit()

# ----------- POS YouHR Menus -----------
attendance_pos = ChatbotMenu(
    menu_key="attendance",
    menu_title="📅 Attendance & Time Management",
    menu_icon="📅",
    company_type="pos_youhr",
    role="employee"
)
leave_pos = ChatbotMenu(
    menu_key="leave",
    menu_title="🏖️ Leave Management",
    menu_icon="🏖️",
    company_type="pos_youhr",
    role="employee"
)
payroll_pos = ChatbotMenu(
    menu_key="payroll",
    menu_title="💵 Payroll",
    menu_icon="💵",
    company_type="pos_youhr",
    role="employee"
)
employee_info_pos = ChatbotMenu(
    menu_key="employee_info",
    menu_title="👥 Employee Information",
    menu_icon="👥",
    company_type="pos_youhr",
    role="employee"
)
db.add_all([attendance_pos, leave_pos, payroll_pos, employee_info_pos])
db.commit()
db.refresh(attendance_pos)
db.refresh(leave_pos)
db.refresh(payroll_pos)
db.refresh(employee_info_pos)

# ----------- POS YouHR Submenus -----------
submenus_pos = [
    # Attendance
    ChatbotSubmenu(menu_id=attendance_pos.id, submenu_key="check_status", submenu_title="Check my attendance status", api_endpoint="/api/attendance/status", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=attendance_pos.id, submenu_key="mark_attendance", submenu_title="Mark attendance (check-in/check-out)", api_endpoint="/api/attendance/mark", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=attendance_pos.id, submenu_key="attendance_history", submenu_title="View attendance history", api_endpoint="/api/attendance/history", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=attendance_pos.id, submenu_key="request_correction", submenu_title="Request attendance correction", api_endpoint="/api/attendance/correction", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=attendance_pos.id, submenu_key="working_hours", submenu_title="View working hours", api_endpoint="/api/attendance/working-hours", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=attendance_pos.id, submenu_key="late_status", submenu_title="Check late arrival status", api_endpoint="/api/attendance/late-status", company_type="pos_youhr", role="employee"),
    # Leave
    ChatbotSubmenu(menu_id=leave_pos.id, submenu_key="leave_balance", submenu_title="Check leave balance", api_endpoint="/api/leave/balance", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=leave_pos.id, submenu_key="apply_leave", submenu_title="Apply for new leave", api_endpoint="/api/leave/apply", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=leave_pos.id, submenu_key="leave_history", submenu_title="View leave history", api_endpoint="/api/leave/history", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=leave_pos.id, submenu_key="cancel_leave", submenu_title="Cancel leave request", api_endpoint="/api/leave/cancel", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=leave_pos.id, submenu_key="leave_approval_status", submenu_title="Check leave approval status", api_endpoint="/api/leave/status", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=leave_pos.id, submenu_key="leave_calendar", submenu_title="Download leave calendar", api_endpoint="/api/leave/calendar", company_type="pos_youhr", role="employee"),
    # Payroll
    ChatbotSubmenu(menu_id=payroll_pos.id, submenu_key="salary_details", submenu_title="Check salary details", api_endpoint="/api/payroll/salary", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=payroll_pos.id, submenu_key="payslips", submenu_title="View payslips", api_endpoint="/api/payroll/payslips", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=payroll_pos.id, submenu_key="tax_deductions", submenu_title="Check tax deductions", api_endpoint="/api/payroll/tax", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=payroll_pos.id, submenu_key="bonus_info", submenu_title="View bonus information", api_endpoint="/api/payroll/bonus", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=payroll_pos.id, submenu_key="bank_details", submenu_title="Bank account details", api_endpoint="/api/payroll/bank-details", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=payroll_pos.id, submenu_key="salary_revision", submenu_title="Salary revision history", api_endpoint="/api/payroll/revisions", company_type="pos_youhr", role="employee"),
    # Employee Information
    ChatbotSubmenu(menu_id=employee_info_pos.id, submenu_key="my_profile", submenu_title="View my profile", api_endpoint="/api/employee/profile", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=employee_info_pos.id, submenu_key="update_details", submenu_title="Update personal details", api_endpoint="/api/employee/update", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=employee_info_pos.id, submenu_key="employment_status", submenu_title="Check employment status", api_endpoint="/api/employee/status", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=employee_info_pos.id, submenu_key="company_policies", submenu_title="View company policies", api_endpoint="/api/policies/list", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=employee_info_pos.id, submenu_key="contact_hr", submenu_title="Contact HR team", api_endpoint="/api/hr/contact", company_type="pos_youhr", role="employee"),
    ChatbotSubmenu(menu_id=employee_info_pos.id, submenu_key="emergency_contacts", submenu_title="Emergency contacts", api_endpoint="/api/employee/emergency", company_type="pos_youhr", role="employee"),
]
db.add_all(submenus_pos)
db.commit()
db.close()

print("✅ POS YouHR menus & submenus inserted successfully!")

