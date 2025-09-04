from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from datetime import date, timedelta, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from pathlib import Path
import os
import random
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


@app.get("/api/downloads/{filename}")
def download_file(filename: str):
    """Serve exported files from the downloads directory securely."""
    # Protect against path traversal
    requested = (DOWNLOAD_DIR / filename).resolve()
    try:
        if not str(requested).startswith(str(DOWNLOAD_DIR.resolve())):
            raise HTTPException(status_code=400, detail="Invalid filename")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not requested.exists() or not requested.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=str(requested), filename=filename, media_type='application/octet-stream')

# Menu Management Endpoints


@app.get("/api/chatbot/menus-with-submenus")
def get_menus_with_submenus(
    company_type: str,
    role: str,
    db: Session = Depends(get_db)
):
    """Get all menus with their submenus filtered by company type and role."""
    menus = db.query(models.ChatbotMenu).filter(
        models.ChatbotMenu.is_active == True,
        models.ChatbotMenu.company_type == company_type,
        models.ChatbotMenu.role == role
    ).all()

    if not menus:
        raise HTTPException(status_code=404, detail="No menus found")

    results = []
    for menu in menus:
        submenus = db.query(models.ChatbotSubmenu).filter(
            models.ChatbotSubmenu.menu_id == menu.id,
            models.ChatbotSubmenu.is_active == True,
            models.ChatbotSubmenu.company_type == company_type,
            models.ChatbotSubmenu.role == role
        ).all()

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

    return results


@app.get("/api/menu/{company_type}")
def get_menus_by_company_type(company_type: str, db: Session = Depends(get_db)):
    """Get menus by company type with special handling for merchant type."""
    if company_type == "merchant":
        # Special handling for merchant to return ICP HR merchant manager menus
        menus = db.query(models.ChatbotMenu).filter(
            models.ChatbotMenu.is_active == True,
            models.ChatbotMenu.company_type == "icp_hr",
            models.ChatbotMenu.role == "merchant_manager"
        ).all()
        submenu_filter = {
            "company_type": "icp_hr",
            "role": "merchant_manager"
        }
    else:
        menus = db.query(models.ChatbotMenu).filter(
            models.ChatbotMenu.is_active == True,
            models.ChatbotMenu.company_type == company_type
        ).all()
        submenu_filter = {}

    if not menus:
        raise HTTPException(
            status_code=404, detail=f"No menus found for company type: {company_type}")

    results = []
    for menu in menus:
        submenu_query = db.query(models.ChatbotSubmenu).filter(
            models.ChatbotSubmenu.menu_id == menu.id,
            models.ChatbotSubmenu.is_active == True
        )

        # Apply additional filters for merchant type
        if submenu_filter:
            for key, value in submenu_filter.items():
                submenu_query = submenu_query.filter(
                    getattr(models.ChatbotSubmenu, key) == value)

        submenus = submenu_query.all()

        results.append({
            "menu_id": menu.id,
            "menu_key": menu.menu_key,
            "menu_title": menu.menu_title,
            "menu_icon": menu.menu_icon,
            "company_type": menu.company_type,
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

    return results

# HR Core Endpoints


@app.get("/api/chatbot/employees")
def get_employees():
    """Get employee information for chatbot."""
    return {
        "status": "success",
        "data": generate_mock_employee_data(15)
    }


@app.get("/api/attendance/history")
def get_attendance_history(
    employee_id: str = Query(..., description="Employee ID"),
    start_date: Optional[str] = Query(
        None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get attendance history for an employee."""
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()

    # Generate mock attendance data
    attendance_records = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    while current_date <= end_dt:
        if current_date.weekday() < 5:  # Monday to Friday
            status = random.choice(["Present", "Absent", "Late", "Half Day"])
            attendance_records.append({
                "date": current_date.isoformat(),
                "status": status,
                "check_in": f"{random.randint(8,10)}:{random.randint(0,59):02d} AM" if status != "Absent" else None,
                "check_out": f"{random.randint(5,7)}:{random.randint(0,59):02d} PM" if status == "Present" else None,
                "hours_worked": round(random.uniform(7.5, 9.0), 1) if status == "Present" else 0
            })
        current_date += timedelta(days=1)

    return {
        "status": "success",
        "employee_id": employee_id,
        "period": {"start_date": start_date, "end_date": end_date},
        "attendance": attendance_records
    }


@app.post("/api/leave/apply")
def apply_leave(leave_data: schemas.LeaveApplication, db: Session = Depends(get_db)):
    """Apply for leave."""
    # In a real implementation, this would save to database
    application_id = f"LA{random.randint(1000, 9999)}"

    return {
        "status": "success",
        "message": "Leave application submitted successfully",
        "application_id": application_id,
        "data": {
            **leave_data.dict(),
            "application_id": application_id,
            "status": "Pending",
            "applied_date": datetime.now().isoformat()
        }
    }


@app.get("/api/leave/applications")
def get_leave_applications(
    employee_id: str = Query(..., description="Employee ID"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get leave applications for an employee."""
    statuses = ["Pending", "Approved", "Rejected"] if not status else [status]

    applications = []
    for i in range(random.randint(3, 8)):
        app_status = random.choice(statuses)
        applications.append({
            "application_id": f"LA{random.randint(1000, 9999)}",
            "leave_type": random.choice(["Sick Leave", "Casual Leave", "Annual Leave", "Maternity Leave"]),
            "start_date": (date.today() + timedelta(days=random.randint(-30, 60))).isoformat(),
            "end_date": (date.today() + timedelta(days=random.randint(-25, 65))).isoformat(),
            "days": random.randint(1, 5),
            "status": app_status,
            "applied_date": (date.today() - timedelta(days=random.randint(1, 15))).isoformat(),
            "reason": "Personal work" if app_status == "Approved" else "Medical emergency"
        })

    return {
        "status": "success",
        "employee_id": employee_id,
        "applications": applications
    }


@app.get("/api/payroll/payslips")
def get_payslips(
    employee_id: str = Query(..., description="Employee ID"),
    year: Optional[int] = Query(None, description="Year"),
    month: Optional[int] = Query(None, description="Month")
):
    """Get payslips for an employee."""
    target_year = year or date.today().year
    target_month = month or date.today().month

    payslips = []
    for i in range(3):  # Last 3 months
        month_date = date(target_year, target_month, 1) - timedelta(days=30*i)

        basic_salary = random.uniform(30000, 80000)
        allowances = basic_salary * 0.3
        deductions = basic_salary * 0.15
        net_salary = basic_salary + allowances - deductions

        payslips.append({
            "payslip_id": f"PS{month_date.strftime('%Y%m')}_{employee_id}",
            "month": month_date.strftime("%B %Y"),
            "basic_salary": round(basic_salary, 2),
            "allowances": round(allowances, 2),
            "deductions": round(deductions, 2),
            "net_salary": round(net_salary, 2),
            "generated_date": month_date.replace(day=28).isoformat()
        })

    return {
        "status": "success",
        "employee_id": employee_id,
        "payslips": payslips
    }


@app.get("/api/employee/status")
def get_employee_status(employee_id: str = Query(..., description="Employee ID")):
    """Get comprehensive employee status."""
    return {
        "status": "success",
        "employee_id": employee_id,
        "data": {
            "basic_info": {
                "name": f"Employee {employee_id[-3:]}",
                "department": random.choice(["HR", "Finance", "IT", "Marketing", "Sales"]),
                "position": random.choice(["Manager", "Executive", "Associate", "Lead"]),
                "employee_status": "Active",
                "joining_date": (date.today() - timedelta(days=random.randint(365, 1095))).isoformat()
            },
            "current_month": {
                "attendance_percentage": round(random.uniform(85, 98), 1),
                "present_days": random.randint(20, 23),
                "leave_days": random.randint(0, 3),
                "overtime_hours": round(random.uniform(0, 15), 1)
            },
            "pending_actions": {
                "leave_applications": random.randint(0, 2),
                "approvals_pending": random.randint(0, 3),
                "documents_pending": random.randint(0, 1)
            }
        }
    }

# Merchant Endpoints


@app.get("/api/merchant/sales/today")
def get_today_sales(merchant_info=Depends(get_merchant_id)):
    """Get today's sales data for merchant."""
    merchant_id, headers = merchant_info

    sales_data = generate_mock_sales_data("today")
    sales_data["merchant_id"] = merchant_id

    response_data = {
        "status": "success",
        "data": sales_data
    }

    return JSONResponse(content=response_data, headers=headers)


@app.get("/api/merchant/sales/weekly")
def get_weekly_sales(merchant_info=Depends(get_merchant_id)):
    """Get weekly sales data for merchant."""
    merchant_id, headers = merchant_info

    sales_data = generate_mock_sales_data("weekly")
    sales_data["merchant_id"] = merchant_id

    # Add daily breakdown
    daily_sales = []
    for i in range(7):
        day_date = date.today() - timedelta(days=i)
        daily_sales.append({
            "date": day_date.isoformat(),
            "sales": round(random.uniform(30000, 70000), 2),
            "transactions": random.randint(40, 120)
        })

    sales_data["daily_breakdown"] = daily_sales

    response_data = {
        "status": "success",
        "data": sales_data
    }

    return JSONResponse(content=response_data, headers=headers)

# Generic data endpoints for chatbot responses


@app.get("/api/chatbot/{data_type}")
def get_chatbot_data(data_type: str):
    """Generic endpoint for chatbot data requests."""
    data_generators = {
        "attendance": lambda: [{"employee": f"EMP{i:03d}", "status": random.choice(["Present", "Absent", "Late"])}
                               for i in range(1, 11)],
        "payslips": lambda: [{"employee": f"EMP{i:03d}", "amount": round(random.uniform(30000, 80000), 2)}
                             for i in range(1, 6)],
        "leave-applications": lambda: [{"employee": f"EMP{i:03d}", "status": random.choice(["Pending", "Approved", "Rejected"])}
                                       for i in range(1, 8)],
        "hr-support-tickets": lambda: [{"ticket_id": f"TK{i:04d}", "status": random.choice(["Open", "In Progress", "Resolved"])}
                                       for i in range(1, 6)],
        "marketing-campaigns": lambda: [{"campaign": f"Campaign {i}", "status": random.choice(["Active", "Scheduled", "Completed"])}
                                        for i in range(1, 4)],
        "promotions": lambda: [{"promotion": f"Promo {i}", "discount": f"{random.randint(10, 50)}%"}
                               for i in range(1, 5)],
        "sales-records": lambda: [{"period": f"Q{i}", "sales": round(random.uniform(100000, 500000), 2)}
                                  for i in range(1, 5)]
    }

    if data_type not in data_generators:
        raise HTTPException(
            status_code=404, detail=f"Data type '{data_type}' not found")

    return {
        "status": "success",
        "data_type": data_type,
        "data": data_generators[data_type]()
    }

# Health check endpoint


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
