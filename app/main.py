
from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from datetime import date, timedelta
from typing import Optional
from pydantic import BaseModel

# Pydantic models for request/response


class LeaveApplicationRequest(BaseModel):
    employee_id: str
    employee_name: str
    leave_type: str
    from_date: str
    to_date: str
    reason: str


app = FastAPI()

# Allow CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend) with no caching for development


class NoCacheStaticFiles(StaticFiles):
    def file_response(self, full_path, stat_result, scope, status_code=200):
        response = super().file_response(full_path, stat_result, scope, status_code)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


app.mount("/static", NoCacheStaticFiles(directory="static"), name="static")

# Serve chat.html at root


@app.get("/")
def serve_chat_html():
    return FileResponse("static/chat.html")

# Get all menus with submenus (filtered)


@app.get("/api/chatbot/menus-with-submenus")
def get_menus_with_submenus(
    company_type: str,
    role: str,
    db: Session = Depends(get_db)
):
    menus = db.query(models.ChatbotMenu)\
        .filter(
            models.ChatbotMenu.is_active == True,
            models.ChatbotMenu.company_type == company_type,
            models.ChatbotMenu.role == role
    ).all()

    if not menus:
        raise HTTPException(status_code=404, detail="No menus found")

    results = []
    for menu in menus:
        submenus = db.query(models.ChatbotSubmenu)\
            .filter(
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


# Get attendance history
@app.get("/api/attendance/history")
def get_attendance_history(
    employee_id: str = Query(..., description="Employee ID"),
    days: Optional[int] = Query(
        30, description="Number of days to fetch (default: 30)"),
    db: Session = Depends(get_db)
):
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # Query attendance records
    attendance_records = db.query(models.AttendanceRecord)\
        .filter(
            models.AttendanceRecord.employee_id == employee_id,
            models.AttendanceRecord.date >= start_date,
            models.AttendanceRecord.date <= end_date
    )\
        .order_by(models.AttendanceRecord.date.desc())\
        .all()

    if not attendance_records:
        return {
            "employee_id": employee_id,
            "message": "No attendance records found for the specified period",
            "total_records": 0,
            "date_range": {
                "from": str(start_date),
                "to": str(end_date)
            },
            "records": []
        }

    # Calculate summary statistics
    present_days = len(
        [r for r in attendance_records if r.status == "Present"])
    late_days = len([r for r in attendance_records if r.status == "Late"])
    absent_days = len([r for r in attendance_records if r.status == "Absent"])

    # Format response
    formatted_records = []
    for record in attendance_records:
        formatted_records.append({
            "date": str(record.date),
            "check_in_time": str(record.check_in_time) if record.check_in_time else None,
            "check_out_time": str(record.check_out_time) if record.check_out_time else None,
            "working_hours": record.working_hours,
            "status": record.status,
            "location": record.location
        })

    return {
        "employee_id": employee_id,
        "employee_name": attendance_records[0].employee_name,
        "total_records": len(attendance_records),
        "date_range": {
            "from": str(start_date),
            "to": str(end_date)
        },
        "summary": {
            "present_days": present_days,
            "late_days": late_days,
            "absent_days": absent_days,
            "total_working_days": len(attendance_records)
        },
        "records": formatted_records
    }


# Apply for leave
@app.post("/api/leave/apply")
def apply_for_leave(
    leave_request: LeaveApplicationRequest,
    db: Session = Depends(get_db)
):
    try:
        # Parse dates
        from_date_obj = date.fromisoformat(leave_request.from_date)
        to_date_obj = date.fromisoformat(leave_request.to_date)

        # Calculate total days
        total_days = (to_date_obj - from_date_obj).days + 1

        # Create leave application
        leave_application = models.LeaveApplication(
            employee_id=leave_request.employee_id,
            employee_name=leave_request.employee_name,
            leave_type=leave_request.leave_type,
            from_date=from_date_obj,
            to_date=to_date_obj,
            total_days=total_days,
            reason=leave_request.reason
        )

        db.add(leave_application)
        db.commit()
        db.refresh(leave_application)

        return {
            "success": True,
            "message": "Leave application submitted successfully",
            "application_id": leave_application.id,
            "employee_id": leave_application.employee_id,
            "employee_name": leave_application.employee_name,
            "leave_type": leave_application.leave_type,
            "from_date": str(leave_application.from_date),
            "to_date": str(leave_application.to_date),
            "total_days": leave_application.total_days,
            "reason": leave_application.reason,
            "status": leave_application.status,
            "applied_date": str(leave_application.applied_date)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to submit leave application: {str(e)}")


# Get leave applications for an employee
@app.get("/api/leave/applications")
def get_leave_applications(
    employee_id: str = Query(..., description="Employee ID"),
    db: Session = Depends(get_db)
):
    applications = db.query(models.LeaveApplication)\
        .filter(models.LeaveApplication.employee_id == employee_id)\
        .order_by(models.LeaveApplication.applied_date.desc())\
        .all()

    if not applications:
        return {
            "employee_id": employee_id,
            "message": "No leave applications found",
            "applications": []
        }

    formatted_applications = []
    for app in applications:
        formatted_applications.append({
            "application_id": app.id,
            "leave_type": app.leave_type,
            "from_date": str(app.from_date),
            "to_date": str(app.to_date),
            "total_days": app.total_days,
            "reason": app.reason,
            "status": app.status,
            "applied_date": str(app.applied_date),
            "approved_by": app.approved_by,
            "approved_date": str(app.approved_date) if app.approved_date else None,
            "comments": app.comments
        })

    return {
        "employee_id": employee_id,
        "total_applications": len(applications),
        "applications": formatted_applications
    }


# Get payslips for an employee
@app.get("/api/payroll/payslips")
def get_payslips(
    employee_id: str = Query(..., description="Employee ID"),
    db: Session = Depends(get_db)
):
    payslips = db.query(models.Payslip)\
        .filter(models.Payslip.employee_id == employee_id)\
        .order_by(models.Payslip.pay_period.desc())\
        .all()

    if not payslips:
        return {
            "employee_id": employee_id,
            "message": "No payslips found",
            "payslips": []
        }

    formatted_payslips = []
    for payslip in payslips:
        formatted_payslips.append({
            "payslip_id": payslip.id,
            "pay_period": payslip.pay_period,
            "pay_period_start": str(payslip.pay_period_start),
            "pay_period_end": str(payslip.pay_period_end),
            "basic_salary": payslip.basic_salary,
            "allowances": payslip.allowances,
            "gross_salary": payslip.gross_salary,
            "deductions": payslip.deductions,
            "net_salary": payslip.net_salary,
            "status": payslip.status,
            "generated_date": str(payslip.generated_date),
            "download_url": payslip.download_url or f"/api/payroll/download/{payslip.id}"
        })

    return {
        "employee_id": employee_id,
        "employee_name": payslips[0].employee_name,
        "total_payslips": len(payslips),
        "payslips": formatted_payslips
    }


# Get employee status information
@app.get("/api/employee/status")
def get_employee_status(
    employee_id: str = Query(..., description="Employee ID"),
    db: Session = Depends(get_db)
):
    employee = db.query(models.Employee)\
        .filter(models.Employee.employee_id == employee_id)\
        .first()

    if not employee:
        # Return default data if no employee record found
        return {
            "employee_id": employee_id,
            "employee_name": "John Doe",
            "employment_status": "Active",
            "employment_type": "Full-time",
            "department": "IT Development",
            "position": "Senior Developer",
            "hire_date": "2023-01-15",
            "years_of_service": 2.6,
            "reporting_manager": "Jane Smith",
            "office_location": "Main Office - Floor 3",
            "salary_grade": "L4",
            "probation_status": "Completed",
            "last_promotion": "2024-01-15",
            "performance_rating": "Exceeds Expectations",
            "next_review_date": "2026-01-15"
        }

    # Calculate years of service
    today = date.today()
    years_of_service = round((today - employee.hire_date).days / 365.25, 1)

    # Determine probation status
    probation_status = "Completed"
    if employee.probation_end_date and today < employee.probation_end_date:
        probation_status = "In Progress"
    elif employee.probation_end_date and today >= employee.probation_end_date:
        probation_status = "Completed"

    return {
        "employee_id": employee.employee_id,
        "employee_name": employee.employee_name,
        "employment_status": employee.employment_status,
        "employment_type": employee.employment_type,
        "department": employee.department,
        "position": employee.position,
        "hire_date": str(employee.hire_date),
        "years_of_service": years_of_service,
        "reporting_manager": employee.reporting_manager,
        "office_location": employee.office_location,
        "salary_grade": employee.salary_grade,
        "probation_status": probation_status,
        "last_promotion": str(employee.last_promotion_date) if employee.last_promotion_date else None,
        # This could come from another table
        "performance_rating": "Exceeds Expectations",
        "next_review_date": "2026-01-15"  # This could be calculated
    }
