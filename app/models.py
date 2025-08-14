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
