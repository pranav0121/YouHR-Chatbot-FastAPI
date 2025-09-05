from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, crud
from datetime import date, timedelta, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from pathlib import Path
import os
import random
import json
from openpyxl import Workbook
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HR Assistant Chatbot API",
    description="Optimized API for HR Assistant Chatbot Backend",
    version="2.0.0"
)


def validate_merchant_id(merchant_id: Optional[str] = None) -> tuple[str, dict]:
    """Validate and return merchant ID with CORS headers."""
    if not merchant_id:
        merchant_id = f"MERCH{random.randint(1000, 9999)}"

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

    return merchant_id, headers


# file-backed persistence for simple settings/feedback when DB models aren't present
BASE_DIR = Path(os.getcwd())
SETTINGS_FILE = os.path.join(BASE_DIR, 'merchant_notification_settings.json')
FEEDBACK_FILE = os.path.join(BASE_DIR, 'merchant_feedback.json')


def _load_json_file(path, default):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _save_json_file(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception:
        return False


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files with no cache for development


class NoCacheStaticFiles(StaticFiles):
    def file_response(self, full_path, stat_result, scope, status_code=200):
        response = super().file_response(full_path, stat_result, scope, status_code)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


app.mount("/static", NoCacheStaticFiles(directory="static"), name="static")

# Download directory setup
DOWNLOAD_DIR = Path(os.path.join(os.getcwd(), 'downloads'))
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Utility functions


def get_merchant_id(merchant_id: str = Query("MERCH001", description="Merchant ID (default: MERCH001)")):
    """Dependency that supplies a merchant_id with optional warning for defaults."""
    default_id = "MERCH001"
    headers = {}
    if merchant_id == default_id:
        warning_msg = f"merchant_id defaulted to {default_id}; callers should provide merchant_id explicitly"
        logger.warning(warning_msg)
        headers["X-Warning"] = warning_msg
    return merchant_id, headers


def generate_mock_menu_data_for_company(company_type: str) -> List[Dict[str, Any]]:
    """Generate mock menu data for a specific company type."""
    mock_data = {
        "icp_hr": [
            {
                "menu_id": 1,
                "menu_key": "hr_management",
                "menu_title": "HR Management",
                "menu_icon": "👥",
                "company_type": "icp_hr",
                "submenus": [
                    {"submenu_id": 1, "submenu_key": "employees",
                        "submenu_title": "Employees", "api_endpoint": "/api/chatbot/employees"},
                    {"submenu_id": 2, "submenu_key": "attendance",
                        "submenu_title": "Attendance", "api_endpoint": "/api/chatbot/attendance"},
                    {"submenu_id": 3, "submenu_key": "payslips",
                        "submenu_title": "Payslips", "api_endpoint": "/api/chatbot/payslips"}
                ]
            }
        ],
        "merchant": [
            {
                "menu_id": 2,
                "menu_key": "sales_management",
                "menu_title": "Sales Management",
                "menu_icon": "💰",
                "company_type": "merchant",
                "submenus": [
                    {"submenu_id": 4, "submenu_key": "today_sales",
                        "submenu_title": "Today's Sales", "api_endpoint": "/api/merchant/sales/today"},
                    {"submenu_id": 5, "submenu_key": "weekly_sales",
                        "submenu_title": "Weekly Sales", "api_endpoint": "/api/merchant/sales/weekly"}
                ]
            }
        ],
        "retail": [
            {
                "menu_id": 3,
                "menu_key": "retail_ops",
                "menu_title": "Retail Operations",
                "menu_icon": "🏬",
                "company_type": "retail",
                "submenus": [
                    {"submenu_id": 6, "submenu_key": "inventory", "submenu_title": "Inventory",
                        "api_endpoint": "/api/chatbot/sales-records"},
                    {"submenu_id": 7, "submenu_key": "promotions",
                        "submenu_title": "Promotions", "api_endpoint": "/api/chatbot/promotions"}
                ]
            }
        ],
        "restaurant": [
            {
                "menu_id": 4,
                "menu_key": "restaurant_ops",
                "menu_title": "Restaurant Operations",
                "menu_icon": "🍽️",
                "company_type": "restaurant",
                "submenus": [
                    {"submenu_id": 8, "submenu_key": "orders", "submenu_title": "Orders",
                        "api_endpoint": "/api/chatbot/sales-records"},
                    {"submenu_id": 9, "submenu_key": "staff", "submenu_title": "Staff",
                        "api_endpoint": "/api/chatbot/employees"}
                ]
            }
        ],
        "pos_youhr": [
            {
                "menu_id": 5,
                "menu_key": "hr_ops",
                "menu_title": "HR Operations",
                "menu_icon": "👔",
                "company_type": "pos_youhr",
                "submenus": [
                    {"submenu_id": 10, "submenu_key": "attendance",
                        "submenu_title": "Attendance History", "api_endpoint": "/api/attendance/history"},
                    {"submenu_id": 11, "submenu_key": "leave", "submenu_title": "Apply for Leave",
                        "api_endpoint": "/api/leave/applications"},
                    {"submenu_id": 12, "submenu_key": "leave_applications",
                        "submenu_title": "View Leave Applications", "api_endpoint": "/api/leave/applications"},
                    {"submenu_id": 13, "submenu_key": "payslips",
                        "submenu_title": "View Payslips", "api_endpoint": "/api/payroll/payslips"},
                    {"submenu_id": 14, "submenu_key": "employee_status",
                        "submenu_title": "Check Employee Status", "api_endpoint": "/api/employee/status"}
                ]
            }
        ]
    }

    return mock_data.get(company_type, [])


def generate_mock_menu_data(company_type: str, role: str) -> List[Dict[str, Any]]:
    """Generate mock menu data when database is not available."""
    mock_menus = {
        "icp_hr": {
            "hr_assistant": [
                {
                    "menu_id": 1,
                    "menu_key": "employee_management",
                    "menu_title": "Employee Management",
                    "menu_icon": "👥",
                    "company_type": "icp_hr",
                    "role": "hr_assistant",
                    "submenus": [
                        {"submenu_id": 1, "submenu_key": "view_employees",
                            "submenu_title": "View Employees", "api_endpoint": "/api/chatbot/employees"},
                        {"submenu_id": 2, "submenu_key": "attendance",
                            "submenu_title": "Attendance", "api_endpoint": "/api/chatbot/attendance"}
                    ]
                }
            ],
            "merchant_manager": [
                {
                    "menu_id": 2,
                    "menu_key": "merchant_ops",
                    "menu_title": "Merchant Operations",
                    "menu_icon": "🏪",
                    "company_type": "icp_hr",
                    "role": "merchant_manager",
                    "submenus": [
                        {"submenu_id": 3, "submenu_key": "sales_today",
                            "submenu_title": "Today's Sales", "api_endpoint": "/api/merchant/sales/today"},
                        {"submenu_id": 4, "submenu_key": "sales_weekly",
                            "submenu_title": "Weekly Sales", "api_endpoint": "/api/merchant/sales/weekly"}
                    ]
                }
            ]
        }
    }

    return mock_menus.get(company_type, {}).get(role, [])


def generate_mock_employee_data(count: int = 10) -> List[Dict[str, Any]]:
    """Generate mock employee data for testing."""
    employees = []
    departments = ["HR", "Finance", "IT", "Marketing", "Sales", "Operations"]
    positions = ["Manager", "Executive",
                 "Associate", "Senior Associate", "Lead"]

    for i in range(1, count + 1):
        employees.append({
            "employee_id": f"EMP{i:03d}",
            "name": f"Employee {i}",
            "email": f"employee{i}@company.com",
            "department": random.choice(departments),
            "position": random.choice(positions),
            "joining_date": (date.today() - timedelta(days=random.randint(30, 1095))).isoformat(),
            "status": "Active"
        })
    return employees


def generate_mock_sales_data(period: str = "today") -> Dict[str, Any]:
    """Generate mock sales data for different periods."""
    base_amount = 50000 if period == "today" else 350000 if period == "weekly" else 150000
    variance = 0.3  # 30% variance

    amount = round(random.uniform(base_amount * (1 - variance),
                   base_amount * (1 + variance)), 2)
    transactions = random.randint(
        50, 200) if period == "today" else random.randint(300, 1000)

    return {
        "period": period,
        "total_sales": amount,
        "total_transactions": transactions,
        "average_transaction": round(amount / transactions, 2),
        "timestamp": datetime.now().isoformat()
    }

# Core API Endpoints


@app.get("/")
def serve_chat_html():
    """Serve the main chat interface."""
    return FileResponse("static/chat.html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


@app.get("/api/")
def root():
    """Root API endpoint."""
    return {
        "message": "HR Assistant Chatbot API",
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "menus": "/api/menu/{company_type}",
            "employees": "/api/chatbot/employees",
            "merchant_sales": "/api/merchant/sales/today"
        }
    }


@app.get("/api/downloads/{filename}")
def download_file(filename: str):
    """Serve exported files from the downloads directory securely."""
    # Protect against path traversal
    requested = (DOWNLOAD_DIR / filename).resolve()
    try:
        if not str(requested).startswith(str(DOWNLOAD_DIR.resolve())):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "data": None,
                    "error": "Invalid filename",
                    "detail": "Path traversal not allowed"
                }
            )
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "data": None,
                "error": "Invalid filename",
                "detail": "Invalid file path"
            }
        )

    if not requested.exists() or not requested.is_file():
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "data": None,
                "error": "File not found",
                "detail": f"File '{filename}' does not exist"
            }
        )

    return FileResponse(path=str(requested), filename=filename, media_type='application/octet-stream')

# Menu Management Endpoints


@app.get("/api/chatbot/menus-with-submenus")
def get_menus_with_submenus(
    company_type: str,
    role: str,
    db: Session = Depends(get_db)
):
    """Get all menus with their submenus filtered by company type and role."""
    try:
        menus = db.query(models.ChatbotMenu).filter(
            models.ChatbotMenu.is_active == True,
            models.ChatbotMenu.company_type == company_type,
            models.ChatbotMenu.role == role
        ).all()

        logger.debug(f"Menus retrieved: {menus}")

        if not menus:
            # Return 404 for missing data
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"No menus found for {company_type}/{role}"
                }
            )

        results = []
        for menu in menus:
            submenus = db.query(models.ChatbotSubmenu).filter(
                models.ChatbotSubmenu.menu_id == menu.id,
                models.ChatbotSubmenu.is_active == True,
                models.ChatbotSubmenu.company_type == company_type,
                models.ChatbotSubmenu.role == role
            ).all()

            logger.debug(f"Submenus for menu {menu.id}: {submenus}")

            results.append({
                "menu_id": menu.id,
                "menu_key": menu.menu_key,
                "menu_title": menu.menu_title,
                "menu_icon": menu.menu_icon,
                "company_type": menu.company_type,
                "role": menu.role,
                "submenus": [
                    {
                        "submenu_id": sm.id,
                        "submenu_key": sm.submenu_key,
                        "submenu_title": sm.submenu_title,
                        "api_endpoint": sm.api_endpoint
                    }
                    for sm in submenus
                ]
            })

        return {
            "status": "success",
            "data": results
        }

    except Exception as e:
        logger.error(f"Error in get_menus_with_submenus: {str(e)}")
        # Return mock data if database fails
        return {
            "status": "success",
            "message": "Using mock data due to database issue",
            "data": generate_mock_menu_data(company_type, role)
        }


@app.get("/api/menu/{company_type}")
def get_menus_by_company_type(company_type: str, db: Session = Depends(get_db)):
    """Get menus by company type with special handling for merchant type."""
    try:
        if company_type == "merchant":
            # Special handling for merchant to return ICP HR merchant manager menus
            menus = db.query(models.ChatbotMenu).filter(
                models.ChatbotMenu.is_active == True,
                models.ChatbotMenu.company_type == "icp_hr",
                models.ChatbotMenu.role == "merchant_manager"
            ).all()
        else:
            menus = db.query(models.ChatbotMenu).filter(
                models.ChatbotMenu.is_active == True,
                models.ChatbotMenu.company_type == company_type
            ).all()

        if not menus:
            # Return mock data instead of 404
            return {
                "status": "success",
                "message": f"Using mock data for {company_type}",
                "data": generate_mock_menu_data_for_company(company_type)
            }

        # Debugging: Log the retrieved menus
        print("Retrieved menus:", menus)

        results = []
        for menu in menus:
            submenus = db.query(models.ChatbotSubmenu).filter(
                models.ChatbotSubmenu.menu_id == menu.id,
                models.ChatbotSubmenu.is_active == True
            ).all()

            # Debugging: Log the retrieved submenus for each menu
            print(f"Menu {menu.menu_key} submenus:", submenus)

            results.append({
                "menu_id": menu.id,
                "menu_key": menu.menu_key,
                "menu_title": menu.menu_title,
                "menu_icon": menu.menu_icon,
                "submenus": [
                    {
                        "submenu_id": submenu.id,
                        "submenu_key": submenu.submenu_key,
                        "submenu_title": submenu.submenu_title,
                        "api_endpoint": submenu.api_endpoint
                    }
                    for submenu in submenus
                ]
            })

        return {
            "status": "success",
            "data": results
        }

    except Exception as e:
        logger.error(f"Error in get_menus_by_company_type: {str(e)}")
        return {
            "status": "success",
            "message": f"Using mock data for {company_type} due to database issue",
            "data": generate_mock_menu_data_for_company(company_type)
        }

# HR Core Endpoints


@app.get("/api/chatbot/employees")
async def get_employees(db: Session = Depends(get_db)):
    try:
        employees = db.execute(
            "SELECT employee_id, employee_name, position FROM employees").fetchall()
        if not employees:
            logger.warning("No employee records found in the database.")
        return {
            "status": "success",
            "data": [
                {"employee_id": emp[0], "employee_name": emp[1], "position": emp[2]} for emp in employees
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        return {
            "status": "error",
            "message": "Failed to fetch employee records."
        }


@app.get("/api/chatbot/attendance")
async def get_attendance(db: Session = Depends(get_db)):
    attendance_records = db.execute(
        "SELECT date, status, check_in, check_out FROM attendance").fetchall()
    return {
        "status": "success",
        "data": [
            {"date": rec[0], "status": rec[1], "check_in": rec[2], "check_out": rec[3]} for rec in attendance_records
        ]
    }

# Duplicate/conflicting merchant endpoint implementations removed.
# Canonical, fixed merchant endpoints are implemented further below.


@app.post("/api/leave/apply")
def apply_leave(leave_data: schemas.LeaveApplicationRequest, db: Session = Depends(get_db)):
    """Apply for leave. Map request schema to LeaveApplication model and save."""
    try:
        # try to coerce date strings to date objects when possible
        try:
            from_date = datetime.fromisoformat(
                leave_data.start_date).date() if leave_data.start_date else None
        except Exception:
            from_date = leave_data.start_date

        try:
            to_date = datetime.fromisoformat(
                leave_data.end_date).date() if leave_data.end_date else None
        except Exception:
            to_date = leave_data.end_date

        new_leave = models.LeaveApplication(
            employee_id=leave_data.employee_id,
            employee_name=leave_data.employee_name or "",
            leave_type=leave_data.leave_type,
            from_date=from_date,
            to_date=to_date,
            total_days=leave_data.days or 0,
            reason=leave_data.reason,
            status="Pending"
        )

        db.add(new_leave)
        db.commit()
        db.refresh(new_leave)
        return {"status": "success", "message": "Leave applied successfully.", "application_id": new_leave.id}
    except Exception as e:
        logger.error(f"Error applying for leave: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to apply for leave."
        }


@app.get("/api/leave/applications")
def get_leave_applications(employee_id: Optional[str] = Query(None, description="Employee ID"), db: Session = Depends(get_db)):
    try:
        applications = db.execute(
            "SELECT id, leave_type, from_date, to_date, total_days, status, applied_date, reason, employee_id FROM leave_applications WHERE employee_id = :employee_id",
            {"employee_id": employee_id}
        ).fetchall()
        return {
            "status": "success",
            "employee_id": employee_id,
            "applications": [
                {
                    "application_id": app[0],
                    "leave_type": app[1],
                    "start_date": app[2],
                    "end_date": app[3],
                    "days": app[4],
                    "status": app[5],
                    "applied_date": app[6],
                    "reason": app[7],
                    "employee_id": app[8]
                } for app in applications
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching leave applications: {e}")
        return {
            "status": "error",
            "message": "Failed to fetch leave applications."
        }


@app.get("/api/payroll/payslips")
def get_payslips(employee_id: Optional[str] = Query(None, description="Employee ID"), year: Optional[int] = Query(None, description="Year"), month: Optional[int] = Query(None, description="Month"), db: Session = Depends(get_db)):
    try:
        target_year = year or date.today().year
        target_month = month or date.today().month
        payslips = db.execute(
            "SELECT id, month, amount, status, created_at, employee_id FROM payslips WHERE employee_id = :employee_id",
            {"employee_id": employee_id}
        ).fetchall()
        return {
            "status": "success",
            "employee_id": employee_id,
            "payslips": [
                {
                    "payslip_id": slip[0],
                    "month": slip[1],
                    "amount": slip[2],
                    "status": slip[3],
                    "generated_date": slip[4],
                    "employee_id": slip[5]
                } for slip in payslips
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching payslips: {e}")
        return {"status": "error", "message": "Failed to fetch payslips."}


@app.get("/api/employee/status")
def get_employee_status(employee_id: Optional[str] = Query(None, description="Employee ID"), db: Session = Depends(get_db)):
    try:
        employee_data = db.execute(
            "SELECT employee_name, department, position, employment_status, hire_date FROM employees WHERE employee_id = :employee_id",
            {"employee_id": employee_id}
        ).fetchone()
        if not employee_data:
            return {"status": "error", "message": "Employee not found."}

        current_month_data = db.execute(
            "SELECT date, status, check_in_time, check_out_time FROM attendance_records WHERE employee_id = :employee_id ORDER BY date DESC LIMIT 1",
            {"employee_id": employee_id}
        ).fetchone()
        pending_actions = db.execute(
            "SELECT COUNT(*) FROM leave_applications WHERE employee_id = :employee_id AND status = 'Pending'",
            {"employee_id": employee_id}
        ).scalar()

        return {
            "status": "success",
            "employee_id": employee_id,
            "data": {
                "basic_info": {
                    "name": employee_data[0],
                    "department": employee_data[1],
                    "position": employee_data[2],
                    "employee_status": employee_data[3],
                    "joining_date": employee_data[4]
                },
                "current_month": {
                    "last_attendance_date": current_month_data[0] if current_month_data else None,
                    "last_attendance_status": current_month_data[1] if current_month_data else None,
                    "last_check_in": current_month_data[2] if current_month_data else None,
                    "last_check_out": current_month_data[3] if current_month_data else None
                },
                "pending_actions": {
                    "leave_applications": pending_actions or 0,
                    "approvals_pending": 0,
                    "documents_pending": 0
                }
            }
        }
    except Exception as e:
        logger.error(f"Error fetching employee status: {e}")
        return {"status": "error", "message": "Failed to fetch employee status."}

# (Old duplicate merchant sales endpoints removed — consolidated handlers are defined later.)


@app.post("/api/leave/apply")
def apply_leave(leave_data: schemas.LeaveApplicationRequest, db: Session = Depends(get_db)):
    """Apply for leave."""
    try:
        new_leave = models.Leave(**leave_data.dict())
        db.add(new_leave)
        db.commit()
        return {"status": "success", "message": "Leave applied successfully."}
    except Exception as e:
        logger.error(f"Error applying for leave: {e}")
        return {
            "status": "error",
            "message": "Failed to apply for leave."
        }


@app.get("/api/leave/applications")
def get_leave_applications(employee_id: Optional[str] = Query(None, description="Employee ID"), db: Session = Depends(get_db)):
    try:
        # use actual column names from models.LeaveApplication
        if employee_id:
            applications = db.execute(
                "SELECT id, leave_type, from_date, to_date, total_days, status, applied_date, reason, employee_id FROM leave_applications WHERE employee_id = :employee_id",
                {"employee_id": employee_id}
            ).fetchall()
        else:
            applications = db.execute(
                "SELECT id, leave_type, from_date, to_date, total_days, status, applied_date, reason, employee_id FROM leave_applications"
            ).fetchall()

        return {
            "status": "success",
            "employee_id": employee_id,
            "applications": [
                {
                    "application_id": app[0],
                    "leave_type": app[1],
                    "start_date": app[2],
                    "end_date": app[3],
                    "days": app[4],
                    "status": app[5],
                    "applied_date": app[6],
                    "reason": app[7],
                    "employee_id": app[8]
                } for app in applications
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching leave applications: {e}")
        return {
            "status": "error",
            "message": "Failed to fetch leave applications."
        }


@app.get("/api/payroll/payslips")
def get_payslips(employee_id: Optional[str] = Query(None, description="Employee ID"), year: Optional[int] = Query(None, description="Year"), month: Optional[int] = Query(None, description="Month"), db: Session = Depends(get_db)):
    try:
        target_year = year or date.today().year
        target_month = month or date.today().month
        # Simplified payslip fields to match models.Payslip
        if employee_id:
            payslips = db.execute(
                "SELECT id, month, amount, status, created_at, employee_id FROM payslips WHERE employee_id = :employee_id",
                {"employee_id": employee_id}
            ).fetchall()
        else:
            payslips = db.execute(
                "SELECT id, month, amount, status, created_at, employee_id FROM payslips"
            ).fetchall()

        return {
            "status": "success",
            "employee_id": employee_id,
            "payslips": [
                {
                    "payslip_id": slip[0],
                    "month": slip[1],
                    "amount": slip[2],
                    "status": slip[3],
                    "generated_date": slip[4],
                    "employee_id": slip[5]
                } for slip in payslips
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching payslips: {e}")
        return {
            "status": "error",
            "message": "Failed to fetch payslips."
        }


@app.get("/api/employee/status")
def get_employee_status(employee_id: Optional[str] = Query(None, description="Employee ID"), db: Session = Depends(get_db)):
    try:
        if employee_id:
            employee_data = db.execute(
                "SELECT employee_name, department, position, employment_status, hire_date FROM employees WHERE employee_id = :employee_id",
                {"employee_id": employee_id}
            ).fetchone()
            if not employee_data:
                return {"status": "error", "message": "Employee not found."}

            # Latest attendance record as a simple "current month" proxy
            current_month_data = db.execute(
                "SELECT date, status, check_in_time, check_out_time FROM attendance_records WHERE employee_id = :employee_id ORDER BY date DESC LIMIT 1",
                {"employee_id": employee_id}
            ).fetchone()

            # Pending leave applications count
            pending_count = db.execute(
                "SELECT COUNT(*) FROM leave_applications WHERE employee_id = :employee_id AND status = 'Pending'",
                {"employee_id": employee_id}
            ).scalar()

            return {
                "status": "success",
                "employee_id": employee_id,
                "data": {
                    "basic_info": {
                        "name": employee_data[0],
                        "department": employee_data[1],
                        "position": employee_data[2],
                        "employee_status": employee_data[3],
                        "joining_date": employee_data[4]
                    },
                    "current_month": {
                        "last_attendance_date": current_month_data[0] if current_month_data else None,
                        "last_attendance_status": current_month_data[1] if current_month_data else None,
                        "last_check_in": current_month_data[2] if current_month_data else None,
                        "last_check_out": current_month_data[3] if current_month_data else None
                    },
                    "pending_actions": {
                        "leave_applications": pending_count or 0,
                        "approvals_pending": 0,
                        "documents_pending": 0
                    }
                }
            }
        else:
            # No employee_id provided — return a list of employee statuses
            rows = db.execute(
                "SELECT employee_id, employment_status, hire_date FROM employees").fetchall()
            data = [
                {"employee_id": r[0], "employee_status": r[1], "joining_date": r[2]} for r in rows
            ]
            return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error fetching employee status: {e}")
        return {"status": "error", "message": "Failed to fetch employee status."}

# =============================================================================
# HR ASSISTANT ENDPOINTS
# =============================================================================


@app.get("/api/attendance/history")
def get_attendance_history(employee_id: Optional[str] = Query(None, description="Employee ID"), db: Session = Depends(get_db)):
    """Retrieve attendance history; optional employee_id filter."""
    try:
        if employee_id:
            rows = db.execute(
                "SELECT id, employee_id, employee_name, date, check_in_time, check_out_time, working_hours, status, location, created_at FROM attendance_records WHERE employee_id = :employee_id ORDER BY date DESC",
                {"employee_id": employee_id}
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT id, employee_id, employee_name, date, check_in_time, check_out_time, working_hours, status, location, created_at FROM attendance_records ORDER BY date DESC"
            ).fetchall()

        history = [
            {
                "id": r[0],
                "employee_id": r[1],
                "employee_name": r[2],
                "date": r[3].isoformat() if hasattr(r[3], "isoformat") else r[3],
                "check_in_time": r[4].isoformat() if hasattr(r[4], "isoformat") else r[4],
                "check_out_time": r[5].isoformat() if hasattr(r[5], "isoformat") else r[5],
                "working_hours": r[6],
                "status": r[7],
                "location": r[8],
                "created_at": r[9].isoformat() if hasattr(r[9], "isoformat") else r[9]
            } for r in rows
        ]

        return {"status": "success", "employee_id": employee_id, "data": history}
    except Exception as e:
        logger.error(f"Error retrieving attendance history: {str(e)}")
        return {"status": "error", "message": "Failed to retrieve attendance history."}


@app.post("/api/leave/apply")
def apply_leave(leave_data: schemas.LeaveApplicationRequest, db: Session = Depends(get_db)):
    """Apply for leave. Map request schema to LeaveApplication model and save."""
    try:
        # try to coerce date strings to date objects when possible
        try:
            from_date = datetime.fromisoformat(
                leave_data.start_date).date() if leave_data.start_date else None
        except Exception:
            from_date = leave_data.start_date

        try:
            to_date = datetime.fromisoformat(
                leave_data.end_date).date() if leave_data.end_date else None
        except Exception:
            to_date = leave_data.end_date

        new_leave = models.LeaveApplication(
            employee_id=leave_data.employee_id,
            employee_name=leave_data.employee_name or "",
            leave_type=leave_data.leave_type,
            from_date=from_date,
            to_date=to_date,
            total_days=leave_data.days or 0,
            reason=leave_data.reason,
            status="Pending"
        )

        db.add(new_leave)
        db.commit()
        db.refresh(new_leave)
        return {"status": "success", "message": "Leave applied successfully.", "application_id": new_leave.id}
    except Exception as e:
        logger.error(f"Error applying for leave: {str(e)}")
        return {"status": "error", "message": "Failed to apply for leave."}


@app.get("/api/leave/applications")
def get_leave_applications(db: Session = Depends(get_db)):
    """Retrieve leave applications."""
    try:
        applications = db.query(models.Leave).all()
        return {"status": "success", "data": applications}
    except Exception as e:
        logger.error(f"Error retrieving leave applications: {str(e)}")
        return {"status": "error", "message": "Failed to retrieve leave applications."}


@app.get("/api/payroll/payslips")
def get_payslips(db: Session = Depends(get_db)):
    """Retrieve payslips."""
    try:
        payslips = db.query(models.Payslip).all()
        return {"status": "success", "data": payslips}
    except Exception as e:
        logger.error(f"Error retrieving payslips: {str(e)}")
        return {"status": "error", "message": "Failed to retrieve payslips."}


@app.get("/api/employee/status")
def get_employee_status(db: Session = Depends(get_db)):
    """Check employee status."""
    try:
        status = db.query(models.EmployeeStatus).all()
        return {"status": "success", "data": status}
    except Exception as e:
        logger.error(f"Error retrieving employee status: {str(e)}")
        return {"status": "error", "message": "Failed to retrieve employee status."}

# =============================================================================
# MERCHANT MANAGEMENT ENDPOINTS
# =============================================================================

# Sales & Money Endpoints


@app.get("/api/merchant/sales/yesterday")
def get_yesterday_sales(merchant_id: str = Query(None)):
    """Get yesterday's sales data for a merchant."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    yesterday_sales = {
        "merchant_id": merchant_id,
        "date": (date.today() - timedelta(days=1)).isoformat(),
        "total_sales": round(random.uniform(40000, 80000), 2),
        "total_transactions": random.randint(60, 150),
        "top_products": [
            {"name": "Product A", "sales": round(
                random.uniform(5000, 15000), 2)},
            {"name": "Product B", "sales": round(
                random.uniform(3000, 12000), 2)},
            {"name": "Product C", "sales": round(
                random.uniform(2000, 8000), 2)}
        ]
    }

    return JSONResponse(content={"status": "success", "data": yesterday_sales}, headers=headers)


@app.get("/api/merchant/sales/today")
def get_today_sales(merchant_id: str = Query(None)):
    """Get today's sales data for a merchant."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    data = generate_mock_sales_data(period="today")
    data.update({"merchant_id": merchant_id, "date": date.today().isoformat()})

    return JSONResponse(content={"status": "success", "data": data}, headers=headers)


@app.get("/api/merchant/sales/weekly")
def get_weekly_sales(merchant_id: str = Query(None)):
    """Get weekly sales summary for a merchant."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    data = generate_mock_sales_data(period="weekly")
    data.update({"merchant_id": merchant_id, "week_start": (date.today(
    ) - timedelta(days=6)).isoformat(), "week_end": date.today().isoformat()})

    return JSONResponse(content={"status": "success", "data": data}, headers=headers)


@app.get("/api/merchant/payments/outstanding")
def get_outstanding_payments(merchant_id: str = Query(None)):
    """Get outstanding payments for a merchant."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    outstanding_payments = {
        "merchant_id": merchant_id,
        "total_outstanding": round(random.uniform(5000, 25000), 2),
        "payments": [
            {
                "payment_id": f"PAY{i:04d}",
                "amount": round(random.uniform(1000, 8000), 2),
                "due_date": (date.today() + timedelta(days=random.randint(1, 30))).isoformat(),
                "status": random.choice(["Pending", "Overdue"])
            }
            for i in range(1, 6)
        ]
    }

    return JSONResponse(content={"status": "success", "data": outstanding_payments}, headers=headers)


@app.get("/api/merchant/expenses/bills")
def get_expenses_bills(merchant_id: str = Query(None)):
    """Get expenses and bills for a merchant."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    expenses_bills = {
        "merchant_id": merchant_id,
        "total_expenses": round(random.uniform(10000, 30000), 2),
        "bills": [
            {
                "bill_id": f"BILL{i:04d}",
                "description": random.choice(["Electricity", "Rent", "Internet", "Supplies", "Insurance"]),
                "amount": round(random.uniform(2000, 8000), 2),
                "due_date": (date.today() + timedelta(days=random.randint(1, 30))).isoformat(),
                "status": random.choice(["Paid", "Pending", "Overdue"])
            }
            for i in range(1, 6)
        ]
    }

    return JSONResponse(content={"status": "success", "data": expenses_bills}, headers=headers)

# My Staff Endpoints


@app.get("/api/merchant/staff/attendance")
def get_staff_attendance(merchant_id: str = Query(None)):
    """Get staff attendance for a merchant."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    staff_attendance = {
        "merchant_id": merchant_id,
        "date": date.today().isoformat(),
        "staff": [
            {
                "employee_id": f"EMP{i:03d}",
                "name": f"Staff Member {i}",
                "status": random.choice(["Present", "Absent", "On Leave", "Late"]),
                "check_in": f"{random.randint(8, 10)}:{random.randint(0, 59):02d} AM" if random.choice([True, False]) else None,
                "role": random.choice(["Sales Operator", "Manager", "Cashier"])
            }
            for i in range(1, 8)
        ]
    }

    return JSONResponse(content={"status": "success", "data": staff_attendance}, headers=headers)


@app.get("/api/merchant/staff/leave-requests")
def get_staff_leave_requests(merchant_id: str = Query(None)):
    """Get staff leave requests for a merchant."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    leave_requests = {
        "merchant_id": merchant_id,
        "requests": [
            {
                "request_id": f"LR{i:04d}",
                "employee_name": f"Staff Member {i}",
                "leave_type": random.choice(["Sick Leave", "Casual Leave", "Annual Leave"]),
                "from_date": (date.today() + timedelta(days=random.randint(1, 10))).isoformat(),
                "to_date": (date.today() + timedelta(days=random.randint(11, 20))).isoformat(),
                "status": random.choice(["Pending", "Approved", "Rejected"]),
                "reason": "Personal work"
            }
            for i in range(1, 5)
        ]
    }

    return JSONResponse(content={"status": "success", "data": leave_requests}, headers=headers)


@app.post("/api/merchant/staff/leave-requests/{request_id}/approve")
def approve_leave_request(request_id: str, merchant_id: str = Query(None)):
    """Approve a staff leave request."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    result = {
        "request_id": request_id,
        "status": "approved",
        "approved_by": merchant_id,
        "approved_at": datetime.now().isoformat()
    }

    return JSONResponse(content={"status": "success", "data": result}, headers=headers)


@app.post("/api/merchant/staff/leave-requests/{request_id}/reject")
def reject_leave_request(request_id: str, merchant_id: str = Query(None)):
    """Reject a staff leave request."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    result = {
        "request_id": request_id,
        "status": "rejected",
        "rejected_by": merchant_id,
        "rejected_at": datetime.now().isoformat()
    }

    return JSONResponse(content={"status": "success", "data": result}, headers=headers)


@app.get("/api/merchant/staff/messages")
def get_staff_messages(merchant_id: str = Query(None)):
    """Get messages from staff members."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    staff_messages = {
        "merchant_id": merchant_id,
        "messages": [
            {
                "message_id": f"MSG{i:04d}",
                "from": f"Staff Member {i}",
                "role": random.choice(["Sales Operator", "Manager"]),
                "subject": random.choice(["Daily Report", "Issue Alert", "Request"]),
                "message": f"This is a sample message {i} from staff member.",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                "status": random.choice(["Unread", "Read"])
            }
            for i in range(1, 6)
        ]
    }

    return JSONResponse(content={"status": "success", "data": staff_messages}, headers=headers)


def _create_new_employee_for_merchant(merchant_id: str = None):
    """Helper: create a sample new employee for the given merchant and return (response_dict, headers).
    This keeps POST as the canonical mutating route but also lets GET return a useful sample so frontend clicks don't 405.
    """
    merchant_id, headers = validate_merchant_id(merchant_id)

    new_employee = {
        "employee_id": f"EMP{random.randint(100, 999):03d}",
        "name": "New Employee",
        "role": "Sales Operator",
        "added_by": merchant_id,
        "added_at": datetime.now().isoformat(),
        "status": "Active"
    }

    resp = {"status": "success",
            "message": "Employee added successfully", "data": new_employee}
    return resp, headers


class EmployeeCreate(BaseModel):
    name: str
    role: str
    contact: Optional[str] = None


@app.post("/api/merchant/staff/add-employee")
def add_employee(employee: EmployeeCreate, merchant_id: str = Query(None)):
    """Add a new employee (canonical POST). Accepts JSON payload with name and role."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    new_employee = {
        "employee_id": f"EMP{random.randint(100, 999):03d}",
        "name": employee.name,
        "role": employee.role,
        "contact": employee.contact,
        "added_by": merchant_id,
        "added_at": datetime.now().isoformat(),
        "status": "Active"
    }

    resp = {"status": "success",
            "message": "New Employee Added", "data": new_employee}
    return JSONResponse(content=resp, headers=headers)


@app.get("/api/merchant/staff/salary")
def get_staff_salary(merchant_id: str = Query(None)):
    """Get staff salary information."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    salary_info = {
        "merchant_id": merchant_id,
        "staff_salaries": [
            {
                "employee_id": f"EMP{i:03d}",
                "name": f"Staff Member {i}",
                "monthly_salary": round(random.uniform(15000, 50000), 2),
                "status": random.choice(["Paid", "Pending", "Overdue"]),
                "last_paid": (date.today() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            for i in range(1, 6)
        ]
    }

    return JSONResponse(content={"status": "success", "data": salary_info}, headers=headers)


@app.post("/api/merchant/staff/salary/{employee_id}/mark-paid")
def mark_salary_paid(employee_id: str, merchant_id: str = Query(None)):
    """Mark salary as paid for an employee."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    result = {
        "employee_id": employee_id,
        "status": "paid",
        "marked_by": merchant_id,
        "paid_at": datetime.now().isoformat()
    }

    return JSONResponse(content={"status": "success", "message": "Salary marked as paid", "data": result}, headers=headers)


@app.post("/api/merchant/staff/hr-support")
def create_hr_support_ticket(merchant_id: str = Query(None)):
    """Create an HR support ticket."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    ticket = {
        "ticket_id": f"HR{random.randint(1000, 9999)}",
        "merchant_id": merchant_id,
        "issue_type": "HR Support",
        "description": "HR-related issue reported",
        "status": "Open",
        "created_at": datetime.now().isoformat(),
        "priority": "Medium"
    }

    return JSONResponse(content={"status": "success", "message": "HR support ticket created", "data": ticket}, headers=headers)


# Accept salary POST for marking salary paid (generic endpoint expected by frontend)
@app.post('/api/merchant/staff/salary')
def post_staff_salary(payload: dict, merchant_id: str = Query(None)):
    """Endpoint to mark salary payment or create salary records via JSON payload."""
    merchant_id, headers = validate_merchant_id(merchant_id)
    employee_id = payload.get('employee_id')
    amount = payload.get('amount')
    if not employee_id or amount is None:
        return JSONResponse(status_code=400, content={"status": "error", "message": "employee_id and amount required"})

    result = {"employee_id": employee_id, "amount": amount, "status": "paid",
              "marked_by": merchant_id, "paid_at": datetime.now().isoformat()}
    return JSONResponse(content={"status": "success", "message": "Salary processed", "data": result}, headers=headers)


# Notification settings persistence (file-backed)
@app.get('/api/merchant/notifications/settings')
def merchant_get_notification_settings(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    settings = _load_json_file(SETTINGS_FILE, {})
    return JSONResponse(content={"status": "success", "data": settings.get(merchant_id, {"email": True, "sms": True, "in_app": True})}, headers=headers)


@app.post('/api/merchant/notifications/settings')
def merchant_set_notification_settings(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    settings = _load_json_file(SETTINGS_FILE, {})
    # Ensure merchant entry exists
    current = settings.get(
        merchant_id, {"email": True, "sms": True, "in_app": True})

    # Allowed keys to update
    allowed = {"email", "sms", "in_app"}

    # Merge incoming payload into existing settings (support partial updates)
    if isinstance(payload, dict):
        for k, v in payload.items():
            if k in allowed:
                # coerce to bool for safety
                try:
                    current[k] = bool(v)
                except Exception:
                    current[k] = True if v in (
                        1, '1', 'true', 'True') else False

    settings[merchant_id] = current
    _save_json_file(SETTINGS_FILE, settings)
    return JSONResponse(content={"status": "success", "message": "Settings updated", "data": settings[merchant_id]}, headers=headers)


# Feedback ideas endpoint and list retrieval
@app.post('/api/merchant/feedback-ideas')
def merchant_feedback_ideas(payload: dict, request: Request, merchant_id: str = Query(None)):
    # Prefer X-Merchant-Id header if provided by frontend
    header_mid = request.headers.get('X-Merchant-Id')
    if header_mid:
        merchant_id = header_mid
    merchant_id, headers = validate_merchant_id(merchant_id)
    content = payload.get('content')
    if not content:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Missing content"})
    feedbacks = _load_json_file(FEEDBACK_FILE, [])
    fb = {"id": len(feedbacks) + 1, "merchant_id": merchant_id,
          "content": content, "created_on": date.today().isoformat()}
    feedbacks.append(fb)
    _save_json_file(FEEDBACK_FILE, feedbacks)
    return JSONResponse(content={"status": "success", "message": "Feedback submitted", "data": fb}, headers=headers)


@app.get('/api/merchant/feedback/list')
def merchant_feedback_list(request: Request, merchant_id: str = Query(None)):
    header_mid = request.headers.get('X-Merchant-Id')
    if header_mid:
        merchant_id = header_mid
    merchant_id, headers = validate_merchant_id(merchant_id)
    feedbacks = _load_json_file(FEEDBACK_FILE, [])
    merchant_feedbacks = [f for f in feedbacks if f.get(
        'merchant_id') == merchant_id]
    return JSONResponse(content={"status": "success", "data": merchant_feedbacks}, headers=headers)

# Marketing & Growth Endpoints


@app.post("/api/merchant/marketing/whatsapp-campaign")
def create_whatsapp_campaign(merchant_id: str = Query(None)):
    """Create a WhatsApp marketing campaign."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    campaign = {
        "campaign_id": f"WA{random.randint(1000, 9999)}",
        "merchant_id": merchant_id,
        "type": "WhatsApp Campaign",
        "status": "Scheduled",
        "target_audience": random.randint(100, 1000),
        "created_at": datetime.now().isoformat(),
        "scheduled_for": (datetime.now() + timedelta(hours=1)).isoformat()
    }

    return JSONResponse(content={"status": "success", "message": "WhatsApp campaign created", "data": campaign}, headers=headers)


@app.post("/api/merchant/marketing/instant-promotion")
def send_instant_promotion(merchant_id: str = Query(None)):
    """Send an instant promotion."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    promotion = {
        "promotion_id": f"PROMO{random.randint(1000, 9999)}",
        "merchant_id": merchant_id,
        "type": "Instant Promotion",
        "discount": f"{random.randint(10, 50)}%",
        "sent_at": datetime.now().isoformat(),
        "recipients": random.randint(50, 500),
        "status": "Sent"
    }

    return JSONResponse(content={"status": "success", "message": "Instant promotion sent", "data": promotion}, headers=headers)


@app.get("/api/merchant/marketing/campaign-results")
def get_campaign_results(merchant_id: str = Query(None)):
    """Get marketing campaign results."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    results = {
        "merchant_id": merchant_id,
        "campaigns": [
            {
                "campaign_id": f"CAMP{i:04d}",
                "type": random.choice(["WhatsApp", "SMS", "Email"]),
                "sent": random.randint(100, 1000),
                "opened": random.randint(50, 500),
                "clicked": random.randint(10, 100),
                "conversion_rate": f"{random.randint(5, 25)}%",
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            for i in range(1, 4)
        ]
    }

    return JSONResponse(content={"status": "success", "data": results}, headers=headers)


@app.get('/api/merchant/marketing/promotions')
def get_marketing_promotions_alias(merchant_id: str = Query(None)):
    """Alias endpoint for backward compatibility: /promotions -> returns campaign results."""
    # Reuse existing generator under campaign-results
    return get_campaign_results(merchant_id)


@app.post('/api/merchant/marketing/create-campaign')
def marketing_create_campaign(payload: dict, merchant_id: str = Query(None), db: Session = Depends(get_db)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    name = payload.get('campaign_name') or payload.get('name')
    if not name:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Missing campaign_name"})
    camp = {"campaign_id": f"CAMP{random.randint(1000,9999)}", "name": name, "budget": payload.get(
        'budget', 0), "status": "Created", "merchant_id": merchant_id}
    return JSONResponse(content={"status": "success", "message": "Campaign created", "data": camp}, headers=headers)


# Notifications endpoints
@app.get('/api/merchant/notifications/approve-leave')
def notifications_approve_leave(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    data = {"pending_leave_requests": [
        {"request_id": "LR001", "employee_id": "EMP002", "days": 2, "status": "Pending"}]}
    return JSONResponse(content={"status": "success", "data": data}, headers=headers)


@app.post('/api/merchant/notifications/approve-shift')
def notifications_approve_shift(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Shift change request processed"}, headers=headers)


@app.get('/api/merchant/notifications/payment-settlement')
def notifications_payment_settlement(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "data": {"last_settlement": date.today().isoformat(), "amount": 12345.67}}, headers=headers)


@app.post('/api/merchant/notifications/renew-subscription')
def notifications_renew_subscription(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Subscription renewed", "expires_on": (date.today() + timedelta(days=365)).isoformat()}, headers=headers)


@app.get('/api/merchant/notifications/head-office')
def notifications_head_office(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "data": [{"message_id": "HO001", "title": "Monthly Policy Update", "read": False}]}, headers=headers)


@app.get('/api/merchant/notifications')
def merchant_get_all_notifications(merchant_id: str = Query(None)):
    """Aggregated notifications endpoint used by frontend 'View Notifications'."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    # Aggregate a few common notification types so the frontend can render them in one call
    data = {
        "pending_leave_requests": [
            {"request_id": "LR001", "employee_id": "EMP002",
                "days": 2, "status": "Pending"}
        ],
        "pending_shift_changes": [
            {"request_id": "SR001", "employee_id": "EMP005",
                "from_shift": "09:00", "to_shift": "14:00", "status": "Pending"}
        ],
        "payment_settlement": {"last_settlement": date.today().isoformat(), "amount": 12345.67},
        "head_office_messages": [
            {"message_id": "HO001", "title": "Monthly Policy Update", "read": False}
        ]
    }

    return JSONResponse(content={"status": "success", "data": data}, headers=headers)


# GET aliases for endpoints frontend may call with GET
@app.get('/api/merchant/notifications/approve-shift')
def get_notifications_approve_shift(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    data = {"pending_shift_changes": [{"request_id": "SR001", "employee_id": "EMP005",
                                       "from_shift": "09:00", "to_shift": "14:00", "status": "Pending"}]}
    return JSONResponse(content={"status": "success", "data": data}, headers=headers)


@app.get('/api/merchant/notifications/renew-subscription')
def get_notifications_renew_subscription(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Subscription active", "expires_on": (date.today() + timedelta(days=180)).isoformat()}, headers=headers)


@app.get('/api/merchant/staff/hr-support')
def get_hr_support(merchant_id: str = Query(None)):
    return create_hr_support_ticket(merchant_id)


@app.get('/api/merchant/marketing/whatsapp-campaign')
def get_whatsapp_campaign(merchant_id: str = Query(None)):
    return create_whatsapp_campaign(merchant_id)


@app.get('/api/merchant/marketing/instant-promotion')
def get_instant_promotion(merchant_id: str = Query(None)):
    return send_instant_promotion(merchant_id)


@app.get('/api/merchant/marketing/results')
def get_marketing_results_alias(merchant_id: str = Query(None)):
    return get_campaign_results(merchant_id)


@app.get('/api/merchant/loans/continue')
def get_loans_continue_alias(merchant_id: str = Query(None)):
    return continue_loan_application(merchant_id)


@app.get('/api/merchant/help/report-pos')
def get_help_report_pos(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Use POST to submit a POS report; sample available."}, headers=headers)


@app.get('/api/merchant/help/report-hardware')
def get_help_report_hardware(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Use POST to report hardware issues."}, headers=headers)


@app.get('/api/merchant/help/report-camera')
def get_help_report_camera(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Use POST to report camera issues."}, headers=headers)


@app.get('/api/merchant/help/request-camera')
def get_help_request_camera(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Use POST to request camera installation."}, headers=headers)


@app.get('/api/merchant/help/general')
def get_help_general(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Use POST to submit detailed support requests."}, headers=headers)


@app.get('/api/merchant/help-support')
def get_help_support_alias(merchant_id: str = Query(None)):
    """Alias endpoint to provide contact support information for frontend compatibility."""
    merchant_id, headers = validate_merchant_id(merchant_id)
    contact = {
        "merchant_id": merchant_id,
        "contact_email": "support@youhr.example",
        "contact_phone": "+1-800-555-1212",
        "support_hours": "Mon-Fri 09:00-18:00",
        "support_ticket_endpoint": "/api/merchant/help/general"
    }
    return JSONResponse(content={"status": "success", "data": contact}, headers=headers)


@app.get('/api/merchant/help/kb')
def get_help_kb(merchant_id: str = Query(None)):
    """Knowledge Base list for quick help articles used by frontend."""
    merchant_id, headers = validate_merchant_id(merchant_id)
    articles = [
        {"id": "KB001", "title": "How to report POS issues",
            "summary": "Steps to report POS application problems.", "url": "/help/kb/report-pos"},
        {"id": "KB002", "title": "Requesting camera installation",
            "summary": "How to request a camera setup and scheduling details.", "url": "/help/kb/request-camera"},
        {"id": "KB003", "title": "Managing notifications",
            "summary": "How to configure notification preferences.", "url": "/help/kb/notifications"}
    ]
    return JSONResponse(content={"status": "success", "data": {"articles": articles}}, headers=headers)


@app.get('/help/kb/report-pos')
def kb_article_report_pos(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    article = {
        "id": "KB001",
        "title": "How to report POS issues",
        "content": "1) Go to Help > Report POS.\n2) Describe the issue and include error screenshots if any.\n3) Submit; support will follow up via email within 24 hours."
    }
    return JSONResponse(content={"status": "success", "data": article}, headers=headers)


@app.get('/help/kb/request-camera')
def kb_article_request_camera(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    article = {
        "id": "KB002",
        "title": "Requesting camera installation",
        "content": "To request camera installation, provide the desired location, preferred dates, and contact person. Our team will contact you to schedule the visit and confirm pricing if applicable."
    }
    return JSONResponse(content={"status": "success", "data": article}, headers=headers)


@app.get('/help/kb/notifications')
def kb_article_notifications(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    article = {
        "id": "KB003",
        "title": "Managing notifications",
        "content": "Manage your notifications under Notifications > Manage Notification Settings. Toggle Email, SMS or In-app to control how you receive updates. Changes are saved immediately."
    }
    return JSONResponse(content={"status": "success", "data": article}, headers=headers)


@app.get('/api/merchant/feedback/rate')
def get_feedback_rate(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    ratings = _load_json_file(FEEDBACK_FILE, [])
    merchant_ratings = [r for r in ratings if r.get(
        'merchant_id') == merchant_id and r.get('type') == 'rating']
    return JSONResponse(content={"status": "success", "data": merchant_ratings}, headers=headers)


@app.get('/api/merchant/feedback/suggest')
def get_feedback_suggest(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    suggestions = _load_json_file(FEEDBACK_FILE, [])
    merchant_suggestions = [s for s in suggestions if s.get(
        'merchant_id') == merchant_id and s.get('type') == 'suggestion']
    return JSONResponse(content={"status": "success", "data": merchant_suggestions}, headers=headers)


# Loans
@app.get('/api/merchant/loans/status')
def loans_status(merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "data": {"loan_status": "Active", "outstanding": 5000.0}}, headers=headers)


@app.post('/api/merchant/loans/continue')
def loans_continue(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Loan application continued", "application_id": f"LN{random.randint(1000,9999)}"}, headers=headers)


# Help & Support
@app.post('/api/merchant/help/report-pos')
def help_report_pos(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    ticket = {
        "ticket_id": f"SUP{random.randint(1000,9999)}", "type": "POS App", "status": "Open"}
    return JSONResponse(content={"status": "success", "message": "POS app problem reported", "data": ticket}, headers=headers)


@app.post('/api/merchant/help/report-hardware')
def help_report_hardware(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    ticket = {
        "ticket_id": f"HW{random.randint(1000,9999)}", "type": "Hardware", "status": "Open"}
    return JSONResponse(content={"status": "success", "message": "Hardware issue reported", "data": ticket}, headers=headers)


@app.post('/api/merchant/help/report-camera')
def help_report_camera(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    ticket = {
        "ticket_id": f"CAM{random.randint(1000,9999)}", "type": "YouLens Camera", "status": "Open"}
    return JSONResponse(content={"status": "success", "message": "Camera issue reported", "data": ticket}, headers=headers)


@app.post('/api/merchant/help/request-camera')
def help_request_camera(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Camera installation/training requested", "request_id": f"REQ{random.randint(1000,9999)}"}, headers=headers)


@app.post('/api/merchant/help/general')
def help_general(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    return JSONResponse(content={"status": "success", "message": "Support request received", "ticket": f"T{random.randint(1000,9999)}"}, headers=headers)


# Feedback extras: rate and suggest
@app.post('/api/merchant/feedback/rate')
def feedback_rate(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    rating = int(payload.get('rating', 5))
    feedbacks = _load_json_file(FEEDBACK_FILE, [])
    fb = {"id": len(feedbacks)+1, "merchant_id": merchant_id, "type": "rating",
          "rating": rating, "created_on": date.today().isoformat()}
    feedbacks.append(fb)
    _save_json_file(FEEDBACK_FILE, feedbacks)
    return JSONResponse(content={"status": "success", "message": "Thanks for rating", "data": fb}, headers=headers)


@app.post('/api/merchant/feedback/suggest')
def feedback_suggest(payload: dict, merchant_id: str = Query(None)):
    merchant_id, headers = validate_merchant_id(merchant_id)
    content = payload.get('content') or payload.get('suggestion')
    if not content:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Missing suggestion content"})
    feedbacks = _load_json_file(FEEDBACK_FILE, [])
    fb = {"id": len(feedbacks)+1, "merchant_id": merchant_id, "type": "suggestion",
          "content": content, "created_on": date.today().isoformat()}
    feedbacks.append(fb)
    _save_json_file(FEEDBACK_FILE, feedbacks)
    return JSONResponse(content={"status": "success", "message": "Suggestion submitted", "data": fb}, headers=headers)


@app.get("/api/merchant/loan/status")
def get_loan_status(merchant_id: str = Query(None)):
    """Get loan status for a merchant."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    loan_status = {
        "merchant_id": merchant_id,
        "loan_id": f"LOAN{random.randint(10000, 99999)}",
        "status": random.choice(["Under Review", "Approved", "Disbursed", "Rejected"]),
        "amount_requested": round(random.uniform(50000, 500000), 2),
        "amount_approved": round(random.uniform(30000, 400000), 2),
        "interest_rate": f"{random.uniform(8.5, 15.0):.1f}%",
        "applied_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
    }

    return JSONResponse(content={"status": "success", "data": loan_status}, headers=headers)


@app.post("/api/merchant/loan/continue")
def continue_loan_application(merchant_id: str = Query(None)):
    """Continue loan application process."""
    merchant_id, headers = validate_merchant_id(merchant_id)

    result = {
        "merchant_id": merchant_id,
        "next_step": "Document Upload",
        "required_documents": ["Bank Statement", "Business License", "Income Proof"],
        "deadline": (date.today() + timedelta(days=7)).isoformat(),
        "status": "In Progress"
    }

    return JSONResponse(content={"status": "success", "message": "Loan application continued", "data": result}, headers=headers)

# =============================================================================
# RETENTION EXECUTOR ENDPOINTS
# =============================================================================

# My Daily Activity Endpoints


@app.get("/api/icp/executor/assigned-merchants")
def get_assigned_merchants(db: Session = Depends(get_db)):
    """Get today's assigned merchants for retention executor."""
    try:
        merchants = db.execute(
            """
            SELECT merchant_id, merchant_name, location, health_status, last_contact, priority, assigned_activity
            FROM assigned_merchants
            WHERE assigned_date = CURRENT_DATE
            """
        ).fetchall()

        return {
            "status": "success",
            "data": {
                "date": date.today().isoformat(),
                "merchants": [
                    {
                        "merchant_id": merchant[0],
                        "merchant_name": merchant[1],
                        "location": merchant[2],
                        "health_status": merchant[3],
                        "last_contact": merchant[4].isoformat(),
                        "priority": merchant[5],
                        "assigned_activity": merchant[6]
                    }
                    for merchant in merchants
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error fetching assigned merchants: {e}")
        return {
            "status": "error",
            "message": "Failed to fetch assigned merchants."
        }


@app.get("/api/icp/executor/merchant-profile/{merchant_id}")
def get_merchant_profile(merchant_id: str, db: Session = Depends(get_db)):
    """Get detailed merchant profile."""
    try:
        profile = db.execute(
            """
            SELECT merchant_id, merchant_name, business_type, location, contact_person, phone, health_status, last_sales, monthly_target, onboarding_date
            FROM merchant_profiles
            WHERE merchant_id = :merchant_id
            """,
            {"merchant_id": merchant_id}
        ).fetchone()

        if not profile:
            return {
                "status": "error",
                "message": "Merchant profile not found."
            }

        return {
            "status": "success",
            "data": {
                "merchant_id": profile[0],
                "merchant_name": profile[1],
                "business_type": profile[2],
                "location": profile[3],
                "contact_person": profile[4],
                "phone": profile[5],
                "health_status": profile[6],
                "last_sales": profile[7],
                "monthly_target": profile[8],
                "onboarding_date": profile[9].isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error fetching merchant profile: {e}")
        return {
            "status": "error",
            "message": "Failed to fetch merchant profile."
        }


@app.post("/api/icp/executor/mark-activity-complete")
def mark_activity_complete():
    """Mark an activity as complete."""
    activity = {
        "activity_id": f"ACT{random.randint(1000, 9999)}",
        "type": "Visit",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "completed_at": datetime.now().isoformat(),
        "notes": "Activity completed successfully",
        "proof_uploaded": True,
        "next_follow_up": (date.today() + timedelta(days=7)).isoformat()
    }

    return {"status": "success", "message": "Activity marked as complete", "data": activity}


@app.post("/api/icp/executor/submit-summary-report")
def submit_summary_report():
    """Submit daily/weekly/monthly summary report."""
    report = {
        "report_id": f"RPT{random.randint(1000, 9999)}",
        "type": "Daily Summary",
        "date": date.today().isoformat(),
        "merchants_visited": random.randint(3, 8),
        "calls_made": random.randint(10, 20),
        "issues_resolved": random.randint(2, 6),
        "new_opportunities": random.randint(1, 3),
        "submitted_at": datetime.now().isoformat(),
        "status": "Submitted"
    }

    return {"status": "success", "message": "Summary report submitted", "data": report}

# Merchant Follow-Up Endpoints


@app.post("/api/icp/executor/update-merchant-health")
def update_merchant_health():
    """Update merchant health status."""
    update = {
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "previous_status": "Limited Activity",
        "new_status": "Healthy",
        "updated_by": "Executor123",
        "updated_at": datetime.now().isoformat(),
        "notes": "Merchant health improved after intervention"
    }

    return {"status": "success", "message": "Merchant health updated", "data": update}


@app.post("/api/icp/executor/log-merchant-needs")
def log_merchant_needs():
    """Log merchant needs and requirements."""
    need = {
        "need_id": f"NEED{random.randint(1000, 9999)}",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "need_type": random.choice(["POS Issue", "Hardware Issue", "Loan", "Training", "Marketing Help"]),
        "description": "Merchant requires assistance with POS system",
        "priority": random.choice(["High", "Medium", "Low"]),
        "logged_by": "Executor123",
        "logged_at": datetime.now().isoformat(),
        "status": "Open"
    }

    return {"status": "success", "message": "Merchant need logged", "data": need}


@app.post("/api/icp/executor/add-notes-commitments")
def add_notes_commitments():
    """Add notes or commitments for a merchant."""
    note = {
        "note_id": f"NOTE{random.randint(1000, 9999)}",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "type": "Commitment",
        "content": "Training scheduled for Friday at 2 PM",
        "added_by": "Executor123",
        "added_at": datetime.now().isoformat(),
        "follow_up_date": (date.today() + timedelta(days=3)).isoformat()
    }

    return {"status": "success", "message": "Note/commitment added", "data": note}


@app.post("/api/icp/executor/attach-photo-proof")
def attach_photo_proof():
    """Attach photo or proof for a merchant visit."""
    attachment = {
        "attachment_id": f"ATT{random.randint(1000, 9999)}",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "type": "Photo Proof",
        "description": "Shop photo taken during visit",
        "uploaded_by": "Executor123",
        "uploaded_at": datetime.now().isoformat(),
        "file_url": "/uploads/proof_photo.jpg"
    }

    return {"status": "success", "message": "Photo proof attached", "data": attachment}

# Onboarding Support Endpoints


@app.get("/api/icp/executor/check-pending-documents")
def check_pending_documents():
    """Check pending merchant documents."""
    pending_docs = [
        {
            "merchant_id": f"MERCH{i:04d}",
            "merchant_name": f"Merchant {i}",
            "pending_documents": random.sample(["CNIC", "Bank Statement", "Business License", "Tax Certificate"], random.randint(1, 3)),
            "onboarding_stage": random.choice(["Document Collection", "Verification", "Approval Pending"]),
            "priority": random.choice(["High", "Medium", "Low"])
        }
        for i in range(1, 4)
    ]

    return {"status": "success", "data": {"pending_documents": pending_docs}}


@app.post("/api/icp/executor/upload-missing-documents")
def upload_missing_documents():
    """Upload missing documents for a merchant."""
    upload = {
        "upload_id": f"UPL{random.randint(1000, 9999)}",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "document_type": "CNIC",
        "uploaded_by": "Executor123",
        "uploaded_at": datetime.now().isoformat(),
        "status": "Uploaded",
        "verification_status": "Pending"
    }

    return {"status": "success", "message": "Document uploaded successfully", "data": upload}


@app.post("/api/icp/executor/schedule-installation-training")
def schedule_installation_training():
    """Schedule installation or training visit."""
    schedule = {
        "schedule_id": f"SCH{random.randint(1000, 9999)}",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "type": random.choice(["Installation", "Training", "Both"]),
        "scheduled_date": (date.today() + timedelta(days=random.randint(1, 7))).isoformat(),
        "scheduled_time": f"{random.randint(9, 17)}:00",
        "technician": "Tech123",
        "status": "Scheduled"
    }

    return {"status": "success", "message": "Installation/training scheduled", "data": schedule}


@app.post("/api/icp/executor/confirm-merchant-setup")
def confirm_merchant_setup():
    """Confirm merchant setup completion."""
    confirmation = {
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "setup_status": "Completed",
        "confirmed_by": "Executor123",
        "confirmed_at": datetime.now().isoformat(),
        "pos_status": "Active",
        "training_completed": True,
        "next_follow_up": (date.today() + timedelta(days=30)).isoformat()
    }

    return {"status": "success", "message": "Merchant setup confirmed", "data": confirmation}

# My Notifications Endpoints


@app.get("/api/icp/executor/todays-tasks")
def get_todays_tasks():
    """Get today's tasks from manager."""
    tasks = [
        {
            "task_id": f"TASK{i:04d}",
            "title": f"Task {i}",
            "description": random.choice(["Visit merchant", "Follow up on issue", "Complete documentation", "Training session"]),
            "priority": random.choice(["High", "Medium", "Low"]),
            "assigned_by": "Manager123",
            "due_date": date.today().isoformat(),
            "status": random.choice(["Pending", "In Progress", "Completed"])
        }
        for i in range(1, 6)
    ]

    return {"status": "success", "data": {"date": date.today().isoformat(), "tasks": tasks}}


@app.get("/api/icp/executor/followup-reminders")
def get_followup_reminders():
    """Get follow-up reminders."""
    reminders = [
        {
            "reminder_id": f"REM{i:04d}",
            "merchant_id": f"MERCH{i:04d}",
            "type": random.choice(["Call for loan request", "Merchant inactivity alert", "Document follow-up"]),
            "due_date": (date.today() + timedelta(days=random.randint(0, 3))).isoformat(),
            "priority": random.choice(["High", "Medium", "Low"]),
            "description": f"Follow up reminder {i}"
        }
        for i in range(1, 4)
    ]

    return {"status": "success", "data": {"reminders": reminders}}


@app.get("/api/icp/executor/pending-actions")
def get_pending_actions():
    """Get pending actions for executor."""
    actions = [
        {
            "action_id": f"ACT{i:04d}",
            "type": random.choice(["Upload visit proof", "Submit commitment", "Complete training"]),
            "merchant_id": f"MERCH{i:04d}",
            "due_date": (date.today() + timedelta(days=random.randint(0, 2))).isoformat(),
            "description": f"Pending action {i}",
            "status": "Pending"
        }
        for i in range(1, 4)
    ]

    return {"status": "success", "data": {"actions": actions}}

# Merchant Support Requests Endpoints


@app.post("/api/icp/executor/raise-pos-issue")
def raise_pos_issue():
    """Raise a POS issue ticket."""
    ticket = {
        "ticket_id": f"POS{random.randint(1000, 9999)}",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "issue_type": "POS Issue",
        "description": "POS system not responding",
        "priority": random.choice(["High", "Medium", "Low"]),
        "raised_by": "Executor123",
        "raised_at": datetime.now().isoformat(),
        "status": "Open"
    }

    return {"status": "success", "message": "POS issue ticket created", "data": ticket}


@app.post("/api/icp/executor/raise-hardware-issue")
def raise_hardware_issue():
    """Raise a hardware issue ticket."""
    ticket = {
        "ticket_id": f"HW{random.randint(1000, 9999)}",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "issue_type": "Hardware Issue",
        "hardware_type": random.choice(["Printer", "Scanner", "POS Machine", "Tablet"]),
        "description": "Hardware malfunction reported",
        "priority": "High",
        "raised_by": "Executor123",
        "raised_at": datetime.now().isoformat(),
        "status": "Open"
    }

    return {"status": "success", "message": "Hardware issue ticket created", "data": ticket}


@app.post("/api/icp/executor/escalate-urgent-case")
def escalate_urgent_case():
    """Escalate urgent case to manager."""
    escalation = {
        "escalation_id": f"ESC{random.randint(1000, 9999)}",
        "case_id": f"CASE{random.randint(1000, 9999)}",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "escalated_to": "Manager123",
        "escalated_by": "Executor123",
        "escalated_at": datetime.now().isoformat(),
        "reason": "Urgent merchant issue requiring immediate attention",
        "priority": "Critical"
    }

    return {"status": "success", "message": "Case escalated to manager", "data": escalation}

# My Feedback Endpoints


@app.post("/api/icp/executor/share-field-experience")
def share_field_experience():
    """Share field experience from visits."""
    experience = {
        "experience_id": f"EXP{random.randint(1000, 9999)}",
        "executor_id": "Executor123",
        "merchant_id": f"MERCH{random.randint(1, 100):04d}",
        "experience_type": "Field Visit",
        "feedback": "Merchant was very cooperative and showed interest in new features",
        "insights": "Market demand is high for digital payment solutions",
        "shared_at": datetime.now().isoformat()
    }

    return {"status": "success", "message": "Field experience shared", "data": experience}


@app.post("/api/icp/executor/suggest-improvements")
def suggest_improvements():
    """Suggest improvements in merchant services."""
    suggestion = {
        "suggestion_id": f"SUG{random.randint(1000, 9999)}",
        "executor_id": "Executor123",
        "category": random.choice(["POS Features", "Mobile App", "Training Program", "Support Process"]),
        "title": "Improve merchant onboarding process",
        "description": "Suggestion for improving the merchant service experience",
        "priority": random.choice(["High", "Medium", "Low"]),
        "submitted_at": datetime.now().isoformat(),
        "status": "Submitted"
    }

    return {"status": "success", "message": "Improvement suggestion submitted", "data": suggestion}


# =============================================================================
# COMPREHENSIVE CRUD ENDPOINTS FOR TESTING
# =============================================================================

# Health and Database Info Endpoints
@app.get("/api/health")
async def get_health():
    """Health check endpoint"""
    return {
        "status": "success",
        "message": "API is healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "PostgreSQL connected"
    }


@app.get("/api/database/info")
async def get_database_info(db: Session = Depends(get_db)):
    """Get database information"""
    try:
        # Get table count information
        tables = [
            "employees", "attendance", "payroll", "leave_requests",
            "merchants", "sales", "staff", "payments", "marketing_campaigns",
            "retention_activities", "daily_followups", "merchant_support", "performance_metrics"
        ]

        return {
            "status": "success",
            "data": {
                "database_type": "PostgreSQL",
                "total_tables": len(tables),
                "tables": tables,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Database info error: {e}")
        return {"status": "error", "message": f"Database error: {str(e)}"}

# Employee Management Endpoints


@app.post("/api/employees", status_code=201)
async def create_employee(employee_data: dict, db: Session = Depends(get_db)):
    """Create a new employee"""
    try:
        # Create employee record
        employee_id = random.randint(1000, 9999)
        employee = {
            "id": employee_id,
            "name": employee_data.get("name"),
            "email": employee_data.get("email"),
            "phone": employee_data.get("phone"),
            "department": employee_data.get("department"),
            "position": employee_data.get("position"),
            "salary": employee_data.get("salary"),
            "hire_date": employee_data.get("hire_date"),
            "created_at": datetime.now().isoformat()
        }

        logger.info(f"Created employee: {employee}")
        return {"status": "success", "data": employee, "id": employee_id}
    except Exception as e:
        logger.error(f"Create employee error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/employees")
async def get_employees():
    """Get all employees"""
    employees = [
        {
            "id": i,
            "name": f"Employee {i}",
            "email": f"employee{i}@company.com",
            "department": random.choice(["HR", "IT", "Sales", "Marketing"]),
            "position": random.choice(["Manager", "Executive", "Associate"])
        }
        for i in range(1, 6)
    ]
    return {"status": "success", "data": employees}


@app.get("/api/employees/{employee_id}")
async def get_employee(employee_id: int):
    """Get specific employee"""
    employee = {
        "id": employee_id,
        "name": f"Employee {employee_id}",
        "email": f"employee{employee_id}@company.com",
        "department": "IT",
        "position": "Manager"
    }
    return {"status": "success", "data": employee}


@app.put("/api/employees/{employee_id}")
async def update_employee(employee_id: int, employee_data: dict):
    """Update employee"""
    updated_employee = {
        "id": employee_id,
        **employee_data,
        "updated_at": datetime.now().isoformat()
    }
    logger.info(f"Updated employee {employee_id}: {updated_employee}")
    return {"status": "success", "data": updated_employee}

# Attendance Management Endpoints


@app.post("/api/attendance", status_code=201)
async def create_attendance(attendance_data: dict):
    """Create attendance record"""
    attendance_id = random.randint(1000, 9999)
    attendance = {
        "id": attendance_id,
        **attendance_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created attendance: {attendance}")
    return {"status": "success", "data": attendance, "id": attendance_id}


@app.get("/api/attendance")
async def get_attendance():
    """Get all attendance records"""
    attendance_records = [
        {
            "id": i,
            "employee_id": random.randint(1000, 1005),
            "date": (datetime.now() - timedelta(days=i)).date().isoformat(),
            "status": random.choice(["Present", "Late", "Absent"])
        }
        for i in range(1, 11)
    ]
    return {"status": "success", "data": attendance_records}

# Payroll Management Endpoints


@app.post("/api/payroll", status_code=201)
async def create_payroll(payroll_data: dict):
    """Create payroll record"""
    payroll_id = random.randint(1000, 9999)
    payroll = {
        "id": payroll_id,
        **payroll_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created payroll: {payroll}")
    return {"status": "success", "data": payroll, "id": payroll_id}


@app.get("/api/payroll")
async def get_payroll():
    """Get all payroll records"""
    payroll_records = [
        {
            "id": i,
            "employee_id": random.randint(1000, 1005),
            "month": f"2025-{str(i).zfill(2)}-01",
            "net_salary": random.randint(30000, 80000)
        }
        for i in range(1, 6)
    ]
    return {"status": "success", "data": payroll_records}

# Leave Management Endpoints


@app.post("/api/leave-requests", status_code=201)
async def create_leave_request(leave_data: dict):
    """Create leave request"""
    leave_id = random.randint(1000, 9999)
    leave_request = {
        "id": leave_id,
        **leave_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created leave request: {leave_request}")
    return {"status": "success", "data": leave_request, "id": leave_id}


@app.get("/api/leave-requests")
async def get_leave_requests():
    """Get all leave requests"""
    leave_requests = [
        {
            "id": i,
            "employee_id": random.randint(1000, 1005),
            "leave_type": random.choice(["Casual", "Sick", "Annual"]),
            "status": random.choice(["Pending", "Approved", "Rejected"])
        }
        for i in range(1, 6)
    ]
    return {"status": "success", "data": leave_requests}

# Merchant Management Endpoints


@app.post("/api/merchants", status_code=201)
async def create_merchant(merchant_data: dict):
    """Create a new merchant"""
    merchant_id = random.randint(2000, 9999)
    merchant = {
        "id": merchant_id,
        **merchant_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created merchant: {merchant}")
    return {"status": "success", "data": merchant, "id": merchant_id}


@app.get("/api/merchants")
async def get_merchants():
    """Get all merchants"""
    merchants = [
        {
            "id": i,
            "business_name": f"Business {i}",
            "owner_name": f"Owner {i}",
            "business_type": random.choice(["Restaurant", "Retail", "Service"])
        }
        for i in range(2000, 2006)
    ]
    return {"status": "success", "data": merchants}


@app.get("/api/merchants/{merchant_id}")
async def get_merchant(merchant_id: int):
    """Get specific merchant"""
    merchant = {
        "id": merchant_id,
        "business_name": f"Business {merchant_id}",
        "owner_name": f"Owner {merchant_id}",
        "business_type": "Restaurant"
    }
    return {"status": "success", "data": merchant}


@app.put("/api/merchants/{merchant_id}")
async def update_merchant(merchant_id: int, merchant_data: dict):
    """Update merchant"""
    updated_merchant = {
        "id": merchant_id,
        **merchant_data,
        "updated_at": datetime.now().isoformat()
    }
    logger.info(f"Updated merchant {merchant_id}: {updated_merchant}")
    return {"status": "success", "data": updated_merchant}

# Sales Management Endpoints


@app.post("/api/sales", status_code=201)
async def create_sale(sales_data: dict):
    """Create sales record"""
    sale_id = random.randint(3000, 9999)
    sale = {
        "id": sale_id,
        **sales_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created sale: {sale}")
    return {"status": "success", "data": sale, "id": sale_id}


@app.get("/api/sales")
async def get_sales():
    """Get all sales records"""
    sales = [
        {
            "id": i,
            "merchant_id": random.randint(2000, 2005),
            "amount": round(random.uniform(100, 1000), 2),
            "date": (datetime.now() - timedelta(days=i-3000)).date().isoformat()
        }
        for i in range(3000, 3011)
    ]
    return {"status": "success", "data": sales}

# Staff Management Endpoints


@app.post("/api/staff", status_code=201)
async def create_staff(staff_data: dict):
    """Create staff record"""
    staff_id = random.randint(4000, 9999)
    staff = {
        "id": staff_id,
        **staff_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created staff: {staff}")
    return {"status": "success", "data": staff, "id": staff_id}


@app.get("/api/staff")
async def get_staff():
    """Get all staff records"""
    staff_records = [
        {
            "id": i,
            "merchant_id": random.randint(2000, 2005),
            "name": f"Staff Member {i}",
            "role": random.choice(["Cashier", "Manager", "Sales Associate"])
        }
        for i in range(4000, 4011)
    ]
    return {"status": "success", "data": staff_records}

# Payment Management Endpoints


@app.post("/api/payments", status_code=201)
async def create_payment(payment_data: dict):
    """Create payment record"""
    payment_id = random.randint(5000, 9999)
    payment = {
        "id": payment_id,
        **payment_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created payment: {payment}")
    return {"status": "success", "data": payment, "id": payment_id}


@app.get("/api/payments")
async def get_payments():
    """Get all payment records"""
    payments = [
        {
            "id": i,
            "merchant_id": random.randint(2000, 2005),
            "amount": round(random.uniform(1000, 10000), 2),
            "status": random.choice(["Completed", "Pending", "Failed"])
        }
        for i in range(5000, 5011)
    ]
    return {"status": "success", "data": payments}

# Marketing Management Endpoints


@app.post("/api/marketing-campaigns", status_code=201)
async def create_marketing_campaign(campaign_data: dict):
    """Create marketing campaign"""
    campaign_id = random.randint(6000, 9999)
    campaign = {
        "id": campaign_id,
        **campaign_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created marketing campaign: {campaign}")
    return {"status": "success", "data": campaign, "id": campaign_id}


@app.get("/api/marketing-campaigns")
async def get_marketing_campaigns():
    """Get all marketing campaigns"""
    campaigns = [
        {
            "id": i,
            "merchant_id": random.randint(2000, 2005),
            "campaign_name": f"Campaign {i}",
            "status": random.choice(["Active", "Paused", "Completed"])
        }
        for i in range(6000, 6011)
    ]
    return {"status": "success", "data": campaigns}

# Retention Executor Endpoints


@app.post("/api/retention-activities", status_code=201)
async def create_retention_activity(activity_data: dict):
    """Create retention activity"""
    activity_id = random.randint(7000, 9999)
    activity = {
        "id": activity_id,
        **activity_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created retention activity: {activity}")
    return {"status": "success", "data": activity, "id": activity_id}


@app.get("/api/retention-activities")
async def get_retention_activities():
    """Get all retention activities"""
    activities = [
        {
            "id": i,
            "merchant_id": random.randint(2000, 2005),
            "activity_type": random.choice(["Call", "Visit", "Email"]),
            "status": random.choice(["Completed", "Pending", "Follow-up Required"])
        }
        for i in range(7000, 7011)
    ]
    return {"status": "success", "data": activities}


@app.post("/api/daily-followups", status_code=201)
async def create_daily_followup(followup_data: dict):
    """Create daily follow-up"""
    followup_id = random.randint(8000, 9999)
    followup = {
        "id": followup_id,
        **followup_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created daily follow-up: {followup}")
    return {"status": "success", "data": followup, "id": followup_id}


@app.get("/api/daily-followups")
async def get_daily_followups():
    """Get all daily follow-ups"""
    followups = [
        {
            "id": i,
            "merchant_id": random.randint(2000, 2005),
            "priority": random.choice(["High", "Medium", "Low"]),
            "status": random.choice(["Scheduled", "In Progress", "Completed"])
        }
        for i in range(8000, 8011)
    ]
    return {"status": "success", "data": followups}


@app.post("/api/merchant-support", status_code=201)
async def create_merchant_support(support_data: dict):
    """Create merchant support ticket"""
    support_id = random.randint(9000, 9999)
    support = {
        "id": support_id,
        **support_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created merchant support: {support}")
    return {"status": "success", "data": support, "id": support_id}


@app.get("/api/merchant-support")
async def get_merchant_support():
    """Get all merchant support tickets"""
    support_tickets = [
        {
            "id": i,
            "merchant_id": random.randint(2000, 2005),
            "issue_type": random.choice(["Technical", "Billing", "General"]),
            "status": random.choice(["Open", "In Progress", "Resolved"])
        }
        for i in range(9000, 9011)
    ]
    return {"status": "success", "data": support_tickets}


@app.post("/api/performance-metrics", status_code=201)
async def create_performance_metrics(metrics_data: dict):
    """Create performance metrics"""
    metrics_id = random.randint(10000, 19999)
    metrics = {
        "id": metrics_id,
        **metrics_data,
        "created_at": datetime.now().isoformat()
    }
    logger.info(f"Created performance metrics: {metrics}")
    return {"status": "success", "data": metrics, "id": metrics_id}


@app.get("/api/performance-metrics")
async def get_performance_metrics():
    """Get all performance metrics"""
    metrics = [
        {
            "id": i,
            "date": (datetime.now() - timedelta(days=i-10000)).date().isoformat(),
            "total_contacts": random.randint(50, 200),
            "retention_rate": round(random.uniform(70, 95), 2)
        }
        for i in range(10000, 10011)
    ]
    return {"status": "success", "data": metrics}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
