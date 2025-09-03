from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, date
from .database import Base


class ChatbotMenu(Base):
    __tablename__ = "chatbot_menus"

    id = Column(Integer, primary_key=True, index=True)
    menu_key = Column(String(50), nullable=False)
    menu_title = Column(String(100), nullable=False)
    menu_icon = Column(String(10))
    is_active = Column(Boolean, default=True)
    # e.g., "pos_youhr", "icp_hr"
    company_type = Column(String(50), nullable=True)
    # e.g., "employee", "admin"
    role = Column(String(50), nullable=True)

    submenus = relationship(
        "ChatbotSubmenu", back_populates="menu", cascade="all, delete")


class ChatbotSubmenu(Base):
    __tablename__ = "chatbot_submenus"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey(
        "chatbot_menus.id", ondelete="CASCADE"))
    submenu_key = Column(String(50), unique=True, nullable=False)
    submenu_title = Column(String(100), nullable=False)
    api_endpoint = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    # e.g., "pos_youhr", "icp_hr"
    company_type = Column(String(50), nullable=True)
    # e.g., "employee", "admin"
    role = Column(String(50), nullable=True)

    menu = relationship("ChatbotMenu", back_populates="submenus")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    employee_name = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    working_hours = Column(String(20), nullable=True)  # e.g., "8h 30m"
    # Present, Absent, Late, Half Day
    status = Column(String(20), nullable=False)
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LeaveApplication(Base):
    __tablename__ = "leave_applications"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    employee_name = Column(String(100), nullable=False)
    # Annual, Sick, Personal, etc.
    leave_type = Column(String(50), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    total_days = Column(Integer, nullable=False)
    reason = Column(String(500), nullable=False)
    # Pending, Approved, Rejected
    status = Column(String(20), default="Pending")
    applied_date = Column(Date, default=date.today)
    approved_by = Column(String(100), nullable=True)
    approved_date = Column(Date, nullable=True)
    comments = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    employee_name = Column(String(100), nullable=False)
    # e.g., "2025-07", "2025-08"
    pay_period = Column(String(20), nullable=False)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    basic_salary = Column(String(20), nullable=False)
    allowances = Column(String(20), nullable=False)
    gross_salary = Column(String(20), nullable=False)
    deductions = Column(String(20), nullable=False)
    net_salary = Column(String(20), nullable=False)
    # Generated, Sent, Downloaded
    status = Column(String(20), default="Generated")
    generated_date = Column(Date, default=date.today)
    download_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    employee_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    department = Column(String(50), nullable=False)
    position = Column(String(100), nullable=False)
    # Full-time, Part-time, Contract
    employment_type = Column(String(20), nullable=False)
    # Active, Inactive, Terminated
    employment_status = Column(String(20), nullable=False)
    hire_date = Column(Date, nullable=False)
    reporting_manager = Column(String(100), nullable=True)
    office_location = Column(String(100), nullable=True)
    salary_grade = Column(String(10), nullable=True)
    probation_end_date = Column(Date, nullable=True)
    last_promotion_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ===== MERCHANT MANAGEMENT MODELS =====

class HRSupportTicket(Base):
    __tablename__ = "hr_support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    employee_name = Column(String(100), nullable=False)
    # Payroll, Benefits, Policy, Technical, Other
    category = Column(String(50), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=False)
    # Low, Medium, High, Urgent
    priority = Column(String(20), default="Medium")
    # Open, In Progress, Resolved, Closed
    status = Column(String(20), default="Open")
    assigned_to = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(String(1000), nullable=True)


class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String(100), nullable=False)
    # WhatsApp, Email, SMS, Social Media
    campaign_type = Column(String(50), nullable=False)
    target_audience = Column(String(100), nullable=False)
    message_content = Column(String(2000), nullable=False)
    scheduled_date = Column(Date, nullable=True)
    budget = Column(String(20), nullable=True)
    # Draft, Scheduled, Running, Completed, Cancelled
    status = Column(String(20), default="Draft")
    reach_count = Column(Integer, default=0)
    engagement_rate = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    launched_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    promotion_name = Column(String(100), nullable=False)
    # Percentage, Fixed Amount, Buy One Get One
    promotion_type = Column(String(50), nullable=False)
    discount_percentage = Column(Integer, nullable=True)
    discount_amount = Column(String(20), nullable=True)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    applicable_items = Column(String(500), default="All Items")
    minimum_purchase = Column(String(20), nullable=True)
    status = Column(String(20), default="Active")  # Active, Inactive, Expired
    usage_count = Column(Integer, default=0)
    total_savings = Column(String(20), default="₹0.00")
    created_at = Column(DateTime, default=datetime.utcnow)


class SalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(50), nullable=False)
    product_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    revenue = Column(String(20), nullable=False)
    sale_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExpenseRecord(Base):
    __tablename__ = "expense_records"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(String(50), unique=True, nullable=False)
    # Rent, Utilities, Inventory, Salaries, Marketing
    category = Column(String(50), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    vendor_name = Column(String(100), nullable=True)
    payment_method = Column(String(20), nullable=False)
    status = Column(String(20), default="Pending")  # Pending, Paid, Overdue
    receipt_url = Column(String(500), nullable=True)
    approved_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(50), unique=True, nullable=False)
    item_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    current_stock = Column(Integer, nullable=False)
    minimum_stock = Column(Integer, default=10)
    unit_price = Column(String(20), nullable=False)
    supplier_name = Column(String(100), nullable=True)
    last_restocked = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    # Active, Low Stock, Out of Stock, Discontinued
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class CustomerData(Base):
    __tablename__ = "customer_data"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    total_purchases = Column(String(20), default="₹0.00")
    visit_count = Column(Integer, default=1)
    last_visit = Column(Date, nullable=False)
    # New, Regular, VIP, Inactive
    customer_type = Column(String(20), default="Regular")
    preferred_items = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class StaffMessage(Base):
    __tablename__ = "staff_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(50), unique=True, nullable=False)
    from_user = Column(String(100), nullable=False)
    to_user = Column(String(100), nullable=False)  # Individual or "All Staff"
    subject = Column(String(200), nullable=False)
    message_content = Column(String(2000), nullable=False)
    priority = Column(String(20), default="Medium")  # Low, Medium, High
    status = Column(String(20), default="Unread")  # Unread, Read, Archived
    # Message, Announcement, Alert
    message_type = Column(String(20), default="Message")
    sent_date = Column(DateTime, default=datetime.utcnow)
    read_date = Column(DateTime, nullable=True)


class WorkSchedule(Base):
    __tablename__ = "work_schedules"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), nullable=False)
    employee_name = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    shift_start = Column(Time, nullable=False)
    shift_end = Column(Time, nullable=False)
    break_duration = Column(String(20), default="30 minutes")
    total_hours = Column(String(20), nullable=False)
    # Scheduled, Completed, No Show, Modified
    status = Column(String(20), default="Scheduled")
    assigned_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
