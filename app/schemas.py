from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date


# ===== HR SCHEMAS =====

class LeaveApplicationRequest(BaseModel):
    employee_id: str
    employee_name: str
    leave_type: str
    from_date: str
    to_date: str
    reason: str


class AttendanceHistoryResponse(BaseModel):
    employee_id: str
    employee_name: str
    total_records: int
    date_range: dict
    summary: dict
    records: List[dict]


class LeaveApplicationResponse(BaseModel):
    success: bool
    message: str
    application_id: int
    employee_id: str
    employee_name: str
    leave_type: str
    from_date: str
    to_date: str
    total_days: int
    reason: str
    status: str
    applied_date: str


class PayslipResponse(BaseModel):
    employee_id: str
    employee_name: str
    total_payslips: int
    payslips: List[dict]


class EmployeeStatusResponse(BaseModel):
    employee_id: str
    employee_name: str
    employment_status: str
    employment_type: str
    department: str
    position: str
    hire_date: str
    years_of_service: float
    reporting_manager: Optional[str]
    office_location: Optional[str]


# ===== MERCHANT SCHEMAS =====

class AddEmployeeRequest(BaseModel):
    employee_id: str
    employee_name: str
    email: EmailStr
    phone: Optional[str] = None
    department: str
    position: str
    employment_type: str  # Full-time, Part-time, Contract
    hire_date: str
    reporting_manager: Optional[str] = None
    office_location: Optional[str] = None


class HRSupportRequest(BaseModel):
    employee_id: str
    employee_name: str
    category: str  # Payroll, Benefits, Policy, Technical, Other
    subject: str
    description: str
    priority: str = "Medium"  # Low, Medium, High, Urgent


class WhatsAppCampaignRequest(BaseModel):
    campaign_name: str
    target_audience: str  # All Customers, Regular Customers, New Customers
    message_content: str
    scheduled_date: Optional[str] = None  # If None, send immediately
    budget: Optional[float] = None


class InstantPromotionRequest(BaseModel):
    promotion_name: str
    promotion_type: str  # Percentage, Fixed Amount, Buy One Get One
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    valid_from: str
    valid_until: str
    # Specific items or "All Items"
    applicable_items: Optional[str] = "All Items"
    minimum_purchase: Optional[float] = None


class SalesDataResponse(BaseModel):
    date: str
    total_sales: str
    total_transactions: int
    payment_breakdown: dict
    top_selling_items: List[dict]


class WeeklySalesResponse(BaseModel):
    week_period: str
    total_weekly_sales: str
    total_transactions: int
    average_daily_sales: str
    daily_breakdown: List[dict]
    best_performing_day: str
    growth_trend: str


class OutstandingPaymentsResponse(BaseModel):
    total_outstanding: str
    overdue_amount: str
    pending_invoices: int
    outstanding_payments: List[dict]
    payment_reminders_sent: int
    last_reminder_date: str


class ExpenseBillsResponse(BaseModel):
    total_monthly_expenses: str
    pending_bills: str
    paid_this_month: str
    expense_categories: List[dict]
    upcoming_bills: List[dict]
    monthly_budget: str
    budget_utilization: str


class StaffAttendanceResponse(BaseModel):
    date: str
    total_staff: int
    present_today: int
    absent_today: int
    attendance_rate: str
    staff_status: List[dict]
    weekly_summary: dict


class StaffLeaveResponse(BaseModel):
    pending_requests: int
    approved_this_month: int
    rejected_this_month: int
    leave_requests: List[dict]
    leave_balance_summary: List[dict]


class StaffMessagesResponse(BaseModel):
    unread_messages: int
    total_messages: int
    messages: List[dict]
    announcements: List[dict]


class SalarySummaryResponse(BaseModel):
    total_monthly_payroll: str
    employees_count: int
    average_salary: str
    salary_breakdown: List[dict]
    pending_payments: str
    next_payroll_date: str
    overtime_hours: dict


# ===== MENU SCHEMAS =====

class MenuResponse(BaseModel):
    menu_id: int
    menu_key: str
    menu_title: str
    menu_icon: str
    company_type: str
    role: str
    submenus: List[dict]


class SubmenuResponse(BaseModel):
    submenu_id: int
    submenu_key: str
    submenu_title: str
    api_endpoint: str


class CompanyInfoResponse(BaseModel):
    company_name: str
    version: str
    description: str
    features: List[str]
    last_updated: str
