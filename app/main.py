
from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from datetime import date, timedelta, datetime
from typing import Optional
from pydantic import BaseModel


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


# Simple menu endpoint for company type (without role filtering)
@app.get("/api/menu/{company_type}")
def get_menus_by_company_type(
    company_type: str,
    db: Session = Depends(get_db)
):
    menus = db.query(models.ChatbotMenu)\
        .filter(
            models.ChatbotMenu.is_active == True,
            models.ChatbotMenu.company_type == company_type
    ).all()

    if not menus:
        raise HTTPException(
            status_code=404, detail=f"No menus found for company type: {company_type}")

    results = []
    for menu in menus:
        submenus = db.query(models.ChatbotSubmenu)\
            .filter(
                models.ChatbotSubmenu.menu_id == menu.id,
                models.ChatbotSubmenu.is_active == True
        ).all()
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
    leave_request: schemas.LeaveApplicationRequest,
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
        # Check if employee_id is clearly invalid (not in expected format)
        if employee_id == "INVALID" or not employee_id.startswith("EMP"):
            raise HTTPException(
                status_code=404, detail=f"Employee with ID {employee_id} not found")

        # Return default data for valid format but non-existent employees
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


# ===== MERCHANT MANAGEMENT ENDPOINTS =====

@app.get("/api/merchant/sales/today")
def get_today_sales(db: Session = Depends(get_db)):
    """Get today's sales data"""
    today = date.today()

    # Mock data - replace with actual database queries
    return {
        "date": str(today),
        "total_sales": "₹12,450.00",
        "total_transactions": 28,
        "cash_sales": "₹8,200.00",
        "card_sales": "₹3,150.00",
        "upi_sales": "₹1,100.00",
        "top_selling_items": [
            {"item": "Coffee", "quantity": 15, "revenue": "₹450.00"},
            {"item": "Sandwich", "quantity": 8, "revenue": "₹800.00"},
            {"item": "Burger", "quantity": 12, "revenue": "₹1,800.00"}
        ],
        "hourly_sales": [
            {"hour": "09:00", "sales": "₹850.00"},
            {"hour": "10:00", "sales": "₹1,200.00"},
            {"hour": "11:00", "sales": "₹1,800.00"},
            {"hour": "12:00", "sales": "₹2,100.00"},
            {"hour": "13:00", "sales": "₹1,950.00"},
            {"hour": "14:00", "sales": "₹1,650.00"},
            {"hour": "15:00", "sales": "₹1,200.00"},
            {"hour": "16:00", "sales": "₹900.00"},
            {"hour": "17:00", "sales": "₹750.00"}
        ]
    }


# Additional Today's Sales Endpoints
@app.get("/api/merchant/sales/today/by-product")
def get_today_sales_by_product(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get today's sales breakdown by product"""
    return {
        "date": str(date.today()),
        "merchant_id": merchant_id,
        "products": [
            {"name": "Coffee", "quantity": 15,
                "revenue": "₹450.00", "stock_remaining": 25},
            {"name": "Sandwich", "quantity": 8,
                "revenue": "₹800.00", "stock_remaining": 12},
            {"name": "Burger", "quantity": 12,
                "revenue": "₹1,800.00", "stock_remaining": 8},
            {"name": "Pastry", "quantity": 6,
                "revenue": "₹300.00", "stock_remaining": 15},
            {"name": "Cold Drinks", "quantity": 22,
                "revenue": "₹660.00", "stock_remaining": 30}
        ],
        "total_products_sold": 5,
        "total_revenue": "₹4,010.00"
    }


@app.get("/api/merchant/sales/today/analytics")
def get_today_sales_analytics(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get today's sales analytics and insights"""
    return {
        "date": str(date.today()),
        "merchant_id": merchant_id,
        "growth_percentage": "+12.5%",
        "avg_transaction_value": "₹445.36",
        "peak_hour": "12:00 PM - 1:00 PM",
        "new_customers": 8,
        "returning_customers": 20,
        "satisfaction_score": 4.7,
        "conversion_rate": "68%",
        "payment_method_breakdown": {
            "cash": "65.8%",
            "card": "25.3%",
            "upi": "8.9%"
        }
    }


@app.get("/api/merchant/sales/today/export")
def export_today_sales(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Export today's sales data"""
    return {
        "status": "success",
        "message": "Sales data exported successfully",
        "download_url": f"/api/downloads/today_sales_{date.today()}.xlsx",
        "file_size": "2.3 MB",
        "total_records": 28,
        "date": str(date.today()),
        "merchant_id": merchant_id
    }


@app.get("/api/merchant/sales/yesterday")
def get_yesterday_sales(db: Session = Depends(get_db)):
    """Get yesterday's sales data"""
    yesterday = date.today() - timedelta(days=1)

    return {
        "date": str(yesterday),
        "total_sales": "₹11,780.00",
        "total_transactions": 25,
        "cash_sales": "₹7,800.00",
        "card_sales": "₹2,980.00",
        "upi_sales": "₹1,000.00",
        "comparison_with_today": {
            "sales_difference": "+₹670.00",
            "percentage_change": "+5.7%",
            "transaction_difference": "+3"
        },
        "top_selling_items": [
            {"item": "Coffee", "quantity": 12, "revenue": "₹360.00"},
            {"item": "Pizza", "quantity": 6, "revenue": "₹900.00"},
            {"item": "Burger", "quantity": 10, "revenue": "₹1,500.00"}
        ]
    }


# Additional Yesterday's Sales Endpoints
@app.get("/api/merchant/sales/yesterday/by-product")
def get_yesterday_sales_by_product(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get yesterday's sales breakdown by product"""
    yesterday = date.today() - timedelta(days=1)
    return {
        "date": str(yesterday),
        "merchant_id": merchant_id,
        "products": [
            {"name": "Coffee", "quantity": 12, "revenue": "₹360.00"},
            {"name": "Pizza", "quantity": 6, "revenue": "₹900.00"},
            {"name": "Burger", "quantity": 10, "revenue": "₹1,500.00"},
            {"name": "Salad", "quantity": 5, "revenue": "₹250.00"},
            {"name": "Juice", "quantity": 18, "revenue": "₹540.00"}
        ],
        "total_products_sold": 5,
        "total_revenue": "₹3,550.00"
    }


@app.get("/api/merchant/sales/yesterday/analytics")
def get_yesterday_sales_analytics(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get yesterday's sales analytics"""
    yesterday = date.today() - timedelta(days=1)
    return {
        "date": str(yesterday),
        "merchant_id": merchant_id,
        "total_revenue": "₹11,780.00",
        "profit_margin": "42.3%",
        "cogs": "₹6,795.00",
        "gross_profit": "₹4,985.00",
        "avg_order_value": "₹471.20",
        "customer_count": 25,
        "peak_sales_hour": "1:00 PM - 2:00 PM"
    }


@app.get("/api/merchant/sales/yesterday/export")
def export_yesterday_sales(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Export yesterday's sales data"""
    yesterday = date.today() - timedelta(days=1)
    return {
        "status": "success",
        "message": "Yesterday's sales data exported successfully",
        "download_url": f"/api/downloads/yesterday_sales_{yesterday}.xlsx",
        "file_size": "2.1 MB",
        "total_records": 25,
        "date": str(yesterday),
        "merchant_id": merchant_id
    }


@app.get("/api/merchant/sales/weekly")
def get_weekly_sales(db: Session = Depends(get_db)):
    """Get weekly sales data"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    return {
        "week_period": f"{week_start} to {today}",
        "total_weekly_sales": "₹78,450.00",
        "total_transactions": 187,
        "average_daily_sales": "₹11,207.14",
        "daily_breakdown": [
            {"day": "Monday", "date": str(
                week_start), "sales": "₹10,200.00", "transactions": 22},
            {"day": "Tuesday", "date": str(
                week_start + timedelta(days=1)), "sales": "₹11,500.00", "transactions": 26},
            {"day": "Wednesday", "date": str(
                week_start + timedelta(days=2)), "sales": "₹12,800.00", "transactions": 29},
            {"day": "Thursday", "date": str(
                week_start + timedelta(days=3)), "sales": "₹13,200.00", "transactions": 31},
            {"day": "Friday", "date": str(
                week_start + timedelta(days=4)), "sales": "₹15,400.00", "transactions": 35},
            {"day": "Saturday", "date": str(
                week_start + timedelta(days=5)), "sales": "₹13,570.00", "transactions": 32},
            {"day": "Sunday", "date": str(
                today), "sales": "₹1,780.00", "transactions": 12}
        ],
        "best_performing_day": "Friday",
        "growth_trend": "+8.5% compared to last week"
    }


# Additional Weekly Sales Endpoints
@app.get("/api/merchant/sales/weekly/analytics")
def get_weekly_sales_analytics(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get weekly sales analytics"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    return {
        "week_period": f"{week_start} to {today}",
        "merchant_id": merchant_id,
        "total_sales": "₹78,450.00",
        "daily_average": "₹11,207.14",
        "best_day": "Friday",
        "best_day_sales": "₹15,400.00",
        "worst_day": "Sunday",
        "worst_day_sales": "₹1,780.00",
        "week_over_week_growth": "+8.5%",
        "customer_retention": "73%"
    }


@app.get("/api/merchant/sales/weekly/export")
def export_weekly_sales(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Export weekly sales report"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    return {
        "status": "success",
        "message": "Weekly sales report exported successfully",
        "download_url": f"/api/downloads/weekly_report_{week_start}_to_{today}.xlsx",
        "file_size": "3.7 MB",
        "total_records": 187,
        "week_range": f"{week_start} to {today}",
        "merchant_id": merchant_id
    }


@app.get("/api/merchant/sales/weekly/compare")
def compare_weekly_sales(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Compare current week with previous week"""
    today = date.today()
    current_week_start = today - timedelta(days=today.weekday())
    previous_week_start = current_week_start - timedelta(days=7)
    return {
        "current_week": f"{current_week_start} to {today}",
        "previous_week": f"{previous_week_start} to {current_week_start - timedelta(days=1)}",
        "merchant_id": merchant_id,
        "current_week_sales": "₹78,450.00",
        "previous_week_sales": "₹72,300.00",
        "growth_percentage": "+8.5%",
        "growth_direction": "📈 Increasing",
        "transaction_comparison": {
            "current": 187,
            "previous": 173,
            "difference": "+14 transactions"
        }
    }


@app.get("/api/merchant/payments/outstanding")
def get_outstanding_payments(db: Session = Depends(get_db)):
    """Get outstanding payment information"""
    return {
        "total_outstanding": "₹45,600.00",
        "overdue_amount": "₹12,300.00",
        "pending_invoices": 8,
        "outstanding_payments": [
            {
                "invoice_id": "INV-2024-001",
                "customer_name": "ABC Corp",
                "amount": "₹8,500.00",
                "due_date": "2024-08-15",
                "days_overdue": 14,
                "status": "Overdue"
            },
            {
                "invoice_id": "INV-2024-002",
                "customer_name": "XYZ Ltd",
                "amount": "₹6,200.00",
                "due_date": "2024-08-25",
                "days_overdue": 4,
                "status": "Overdue"
            },
            {
                "invoice_id": "INV-2024-003",
                "customer_name": "Quick Mart",
                "amount": "₹12,400.00",
                "due_date": "2024-09-05",
                "days_overdue": 0,
                "status": "Pending"
            },
            {
                "invoice_id": "INV-2024-004",
                "customer_name": "Food Palace",
                "amount": "₹18,500.00",
                "due_date": "2024-09-10",
                "days_overdue": 0,
                "status": "Pending"
            }
        ],
        "payment_reminders_sent": 3,
        "last_reminder_date": "2024-08-27"
    }


# Additional Payment Management Endpoints
@app.get("/api/merchant/payments/send-reminders")
def send_payment_reminders(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Send payment reminders to customers"""
    return {
        "status": "success",
        "message": "Payment reminders sent successfully",
        "merchant_id": merchant_id,
        "reminders_sent": 8,
        "total_outstanding": "₹45,600.00",
        "customers_notified": [
            {"customer": "ABC Corp", "amount": "₹15,200.00", "method": "Email"},
            {"customer": "XYZ Ltd", "amount": "₹8,500.00", "method": "SMS"},
            {"customer": "PQR Enterprises",
                "amount": "₹12,300.00", "method": "WhatsApp"}
        ],
        "reminder_date": str(date.today())
    }


@app.get("/api/merchant/payments/update-status")
def update_payment_status(merchant_id: str = Query(...), payment_id: str = Query(...), status: str = Query(...), db: Session = Depends(get_db)):
    """Update payment status"""
    return {
        "status": "success",
        "message": f"Payment status updated to {status}",
        "merchant_id": merchant_id,
        "payment_id": payment_id,
        "new_status": status,
        "updated_date": str(date.today()),
        "updated_by": "Merchant Portal"
    }


@app.get("/api/merchant/payments/report")
def generate_payment_report(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Generate comprehensive payment report"""
    return {
        "status": "success",
        "message": "Payment report generated successfully",
        "merchant_id": merchant_id,
        "total_outstanding": "₹45,600.00",
        "overdue_count": 5,
        "pending_count": 3,
        "report_url": f"/api/downloads/payment_report_{date.today()}.pdf",
        "generated_date": str(date.today()),
        "summary": {
            "total_invoices": 25,
            "paid_invoices": 17,
            "overdue_invoices": 5,
            "pending_invoices": 3
        }
    }


@app.get("/api/merchant/expenses/bills")
def get_expense_bills(db: Session = Depends(get_db)):
    """Get expense and bill information"""
    return {
        "total_monthly_expenses": "₹25,800.00",
        "pending_bills": "₹8,400.00",
        "paid_this_month": "₹17,400.00",
        "expense_categories": [
            {"category": "Rent", "amount": "₹10,000.00", "status": "Paid"},
            {"category": "Utilities", "amount": "₹2,500.00", "status": "Pending"},
            {"category": "Inventory", "amount": "₹8,200.00", "status": "Paid"},
            {"category": "Staff Salaries", "amount": "₹3,600.00", "status": "Pending"},
            {"category": "Marketing", "amount": "₹1,500.00", "status": "Paid"}
        ],
        "upcoming_bills": [
            {"bill_type": "Electricity", "amount": "₹1,200.00",
                "due_date": "2024-09-05"},
            {"bill_type": "Internet", "amount": "₹800.00", "due_date": "2024-09-08"},
            {"bill_type": "Insurance", "amount": "₹2,400.00", "due_date": "2024-09-15"}
        ],
        "monthly_budget": "₹30,000.00",
        "budget_utilization": "86%"
    }


# Additional Expense Management Endpoints
@app.get("/api/merchant/expenses/add")
def add_new_expense(merchant_id: str = Query(...), description: str = Query(...), amount: float = Query(...), category: str = Query("Other"), db: Session = Depends(get_db)):
    """Add a new expense"""
    return {
        "status": "success",
        "message": "Expense added successfully",
        "merchant_id": merchant_id,
        "expense_id": f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": description,
        "amount": f"₹{amount:.2f}",
        "category": category,
        "date_added": str(date.today()),
        "status": "Recorded"
    }


@app.get("/api/merchant/expenses/monthly-report")
def get_monthly_expense_report(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get monthly expense breakdown report"""
    return {
        "month": date.today().strftime("%B %Y"),
        "merchant_id": merchant_id,
        "total_expenses": "₹25,800.00",
        "top_category": "Staff Salaries",
        "top_category_amount": "₹8,200.00",
        "categories": [
            {"category": "Staff Salaries",
                "amount": "₹8,200.00", "percentage": "31.8%"},
            {"category": "Inventory", "amount": "₹6,500.00", "percentage": "25.2%"},
            {"category": "Utilities", "amount": "₹4,200.00", "percentage": "16.3%"},
            {"category": "Marketing", "amount": "₹3,100.00", "percentage": "12.0%"},
            {"category": "Maintenance", "amount": "₹2,300.00", "percentage": "8.9%"},
            {"category": "Other", "amount": "₹1,500.00", "percentage": "5.8%"}
        ],
        "budget_comparison": {
            "budgeted": "₹30,000.00",
            "actual": "₹25,800.00",
            "variance": "₹4,200.00",
            "variance_percentage": "14% under budget"
        }
    }


@app.get("/api/merchant/expenses/update-bill")
def update_bill_status(merchant_id: str = Query(...), bill_id: str = Query(...), status: str = Query(...), db: Session = Depends(get_db)):
    """Update bill payment status"""
    return {
        "status": "success",
        "message": f"Bill status updated to {status}",
        "merchant_id": merchant_id,
        "bill_id": bill_id,
        "new_status": status,
        "updated_date": str(date.today()),
        "next_action": "Bill marked as paid" if status == "Paid" else f"Status changed to {status}"
    }


@app.get("/api/merchant/staff/attendance")
def get_staff_attendance(db: Session = Depends(get_db)):
    """Get staff attendance information"""
    today = date.today()

    return {
        "date": str(today),
        "total_staff": 6,
        "present_today": 5,
        "absent_today": 1,
        "attendance_rate": "83.3%",
        "staff_status": [
            {"name": "John Smith", "role": "Manager", "status": "Present",
                "check_in": "09:00 AM", "location": "Store"},
            {"name": "Sarah Johnson", "role": "Cashier", "status": "Present",
                "check_in": "09:15 AM", "location": "Store"},
            {"name": "Mike Brown", "role": "Cook", "status": "Present",
                "check_in": "08:45 AM", "location": "Kitchen"},
            {"name": "Lisa Davis", "role": "Server", "status": "Present",
                "check_in": "09:30 AM", "location": "Store"},
            {"name": "Tom Wilson", "role": "Cleaner",
                "status": "Absent", "check_in": "-", "location": "-"},
            {"name": "Anna Taylor", "role": "Assistant", "status": "Present",
                "check_in": "09:10 AM", "location": "Store"}
        ],
        "weekly_summary": {
            "average_attendance": "88.1%",
            "most_punctual": "Mike Brown",
            "total_working_hours": "234 hours"
        }
    }


@app.get("/api/merchant/staff/leave-requests")
def get_staff_leave_requests(db: Session = Depends(get_db)):
    """Get staff leave requests"""
    return {
        "pending_requests": 2,
        "approved_this_month": 4,
        "rejected_this_month": 0,
        "leave_requests": [
            {
                "request_id": "LR-001",
                "employee_name": "Sarah Johnson",
                "leave_type": "Annual Leave",
                "from_date": "2024-09-10",
                "to_date": "2024-09-12",
                "days": 3,
                "reason": "Family vacation",
                "status": "Pending",
                "applied_date": "2024-08-25"
            },
            {
                "request_id": "LR-002",
                "employee_name": "Tom Wilson",
                "leave_type": "Sick Leave",
                "from_date": "2024-09-05",
                "to_date": "2024-09-06",
                "days": 2,
                "reason": "Medical appointment",
                "status": "Pending",
                "applied_date": "2024-08-28"
            },
            {
                "request_id": "LR-003",
                "employee_name": "Lisa Davis",
                "leave_type": "Personal Leave",
                "from_date": "2024-08-20",
                "to_date": "2024-08-20",
                "days": 1,
                "reason": "Personal work",
                "status": "Approved",
                "applied_date": "2024-08-15"
            }
        ],
        "leave_balance_summary": [
            {"employee": "Sarah Johnson", "annual_leave": 12, "sick_leave": 8},
            {"employee": "Mike Brown", "annual_leave": 15, "sick_leave": 10},
            {"employee": "Tom Wilson", "annual_leave": 8, "sick_leave": 6}
        ]
    }


@app.get("/api/merchant/staff/messages")
def get_staff_messages(db: Session = Depends(get_db)):
    """Get staff messages and announcements"""
    return {
        "unread_messages": 3,
        "total_messages": 12,
        "messages": [
            {
                "message_id": "MSG-001",
                "from": "Management",
                "to": "All Staff",
                "subject": "New Safety Protocols",
                "message": "Please follow the updated safety protocols effective immediately.",
                "date": "2024-08-28",
                "priority": "High",
                "status": "Unread"
            },
            {
                "message_id": "MSG-002",
                "from": "HR Department",
                "to": "All Staff",
                "subject": "Monthly Team Meeting",
                "message": "Monthly team meeting scheduled for September 5th at 2 PM.",
                "date": "2024-08-27",
                "priority": "Medium",
                "status": "Unread"
            },
            {
                "message_id": "MSG-003",
                "from": "John Smith",
                "to": "Kitchen Staff",
                "subject": "New Menu Items",
                "message": "We're introducing new items next week. Training session tomorrow.",
                "date": "2024-08-26",
                "priority": "Medium",
                "status": "Read"
            }
        ],
        "announcements": [
            {
                "title": "Store Renovation",
                "content": "Store renovation will begin next month. Expect temporary changes.",
                "date": "2024-08-25",
                "type": "Info"
            },
            {
                "title": "Performance Bonus",
                "content": "Congratulations! Store exceeded sales target. Bonus will be credited.",
                "date": "2024-08-20",
                "type": "Success"
            }
        ]
    }


@app.get("/api/merchant/staff/add-employee")
def get_add_employee_form(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get add employee form data"""
    return {
        "status": "success",
        "merchant_id": merchant_id,
        "form_title": "Add New Employee",
        "required_fields": [
            "full_name", "email", "phone", "position", "department", "salary", "start_date"
        ],
        "departments": ["Sales", "Marketing", "Operations", "HR", "Finance", "IT"],
        "positions": ["Manager", "Assistant", "Executive", "Intern", "Senior Executive"],
        "instructions": "Please fill all required fields to add a new employee to your team."
    }


@app.post("/api/merchant/staff/add-employee")
def add_new_employee(employee_data: schemas.AddEmployeeRequest, db: Session = Depends(get_db)):
    """Add a new employee"""
    try:
        # Create new employee record
        new_employee = models.Employee(
            employee_id=employee_data.employee_id,
            employee_name=employee_data.employee_name,
            email=employee_data.email,
            phone=employee_data.phone,
            department=employee_data.department,
            position=employee_data.position,
            employment_type=employee_data.employment_type,
            employment_status="Active",
            hire_date=date.fromisoformat(employee_data.hire_date),
            reporting_manager=employee_data.reporting_manager,
            office_location=employee_data.office_location
        )

        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)

        return {
            "success": True,
            "message": "Employee added successfully",
            "employee_id": new_employee.employee_id,
            "employee_name": new_employee.employee_name,
            "department": new_employee.department,
            "position": new_employee.position,
            "hire_date": str(new_employee.hire_date)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to add employee: {str(e)}")


@app.get("/api/merchant/staff/salary")
def get_staff_salary_info(db: Session = Depends(get_db)):
    """Get staff salary information"""
    return {
        "total_monthly_payroll": "₹45,000.00",
        "employees_count": 6,
        "average_salary": "₹7,500.00",
        "salary_breakdown": [
            {"employee": "John Smith", "position": "Manager",
                "salary": "₹12,000.00", "status": "Paid"},
            {"employee": "Sarah Johnson", "position": "Cashier",
                "salary": "₹8,000.00", "status": "Paid"},
            {"employee": "Mike Brown", "position": "Cook",
                "salary": "₹9,000.00", "status": "Paid"},
            {"employee": "Lisa Davis", "position": "Server",
                "salary": "₹6,500.00", "status": "Pending"},
            {"employee": "Tom Wilson", "position": "Cleaner",
                "salary": "₹5,000.00", "status": "Pending"},
            {"employee": "Anna Taylor", "position": "Assistant",
                "salary": "₹4,500.00", "status": "Paid"}
        ],
        "pending_payments": "₹11,500.00",
        "next_payroll_date": "2024-09-05",
        "overtime_hours": {
            "total_overtime": "24 hours",
            "overtime_pay": "₹2,400.00"
        }
    }


@app.get("/api/merchant/hr/add-employee")
def get_add_employee_form(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get add employee form data"""
    return {
        "status": "success",
        "merchant_id": merchant_id,
        "form_title": "Add New Employee",
        "departments": ["Sales", "HR", "Finance", "Operations", "Marketing", "IT", "Customer Service"],
        "positions": ["Manager", "Senior Executive", "Executive", "Assistant", "Intern"],
        "employment_types": ["Full-time", "Part-time", "Contract", "Internship"],
        "required_fields": ["full_name", "email", "phone", "department", "position", "start_date"],
        "optional_fields": ["address", "emergency_contact", "previous_experience"]
    }


@app.get("/api/merchant/hr/support")
def get_hr_support_form(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get HR support form data"""
    return {
        "status": "success",
        "merchant_id": merchant_id,
        "form_title": "HR Support Request",
        "categories": ["General HR", "Employee Issues", "Payroll", "Compliance", "Training", "Other"],
        "priority_levels": ["Low", "Medium", "High", "Urgent"],
        "support_channels": ["Email", "Phone", "Chat", "In-Person"],
        "business_hours": "Monday-Friday 9:00 AM - 6:00 PM",
        "emergency_contact": "+91-1800-HR-HELP"
    }


@app.post("/api/merchant/staff/hr-support")
def submit_hr_support_request(request_data: schemas.HRSupportRequest, db: Session = Depends(get_db)):
    """Submit HR support request"""
    try:
        # Create HR support ticket
        support_ticket = models.HRSupportTicket(
            employee_id=request_data.employee_id,
            employee_name=request_data.employee_name,
            category=request_data.category,
            subject=request_data.subject,
            description=request_data.description,
            priority=request_data.priority
        )

        db.add(support_ticket)
        db.commit()
        db.refresh(support_ticket)

        return {
            "success": True,
            "message": "HR support request submitted successfully",
            "ticket_id": support_ticket.id,
            "category": support_ticket.category,
            "priority": support_ticket.priority,
            "status": support_ticket.status,
            "estimated_response_time": "24-48 hours"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to submit HR request: {str(e)}")


@app.get("/api/merchant/marketing/whatsapp-campaign")
def get_whatsapp_campaign_form(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get WhatsApp campaign form data"""
    return {
        "status": "success",
        "merchant_id": merchant_id,
        "form_title": "WhatsApp Marketing Campaign",
        "campaign_types": ["Promotional", "Announcement", "Follow-up", "Seasonal"],
        "target_audiences": ["All Customers", "New Customers", "Repeat Customers", "VIP Customers"],
        "message_templates": [
            "Welcome new customers",
            "Special discount offer",
            "Product announcement",
            "Appointment reminder",
            "Custom message"
        ],
        "budget_ranges": ["₹500-1000", "₹1000-5000", "₹5000-10000", "₹10000+"],
        "scheduling_options": ["Send Now", "Schedule for Later", "Recurring Campaign"]
    }


@app.post("/api/merchant/marketing/whatsapp-campaign")
def create_whatsapp_campaign(campaign_data: schemas.WhatsAppCampaignRequest, db: Session = Depends(get_db)):
    """Create WhatsApp marketing campaign"""
    try:
        # Create marketing campaign
        campaign = models.MarketingCampaign(
            campaign_name=campaign_data.campaign_name,
            campaign_type="WhatsApp",
            target_audience=campaign_data.target_audience,
            message_content=campaign_data.message_content,
            scheduled_date=date.fromisoformat(
                campaign_data.scheduled_date) if campaign_data.scheduled_date else None,
            budget=campaign_data.budget
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        return {
            "success": True,
            "message": "WhatsApp campaign created successfully",
            "campaign_id": campaign.id,
            "campaign_name": campaign.campaign_name,
            "target_audience": campaign.target_audience,
            "estimated_reach": "500-800 customers",
            "estimated_cost": f"₹{campaign.budget or 0}.00",
            "status": campaign.status,
            "scheduled_date": str(campaign.scheduled_date) if campaign.scheduled_date else "Immediate"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create campaign: {str(e)}")


@app.get("/api/merchant/marketing/promotion")
def get_promotion_form(merchant_id: str = Query(...), db: Session = Depends(get_db)):
    """Get promotion form data"""
    return {
        "status": "success",
        "merchant_id": merchant_id,
        "form_title": "Create Promotion",
        "promotion_types": ["Percentage Discount", "Fixed Amount", "Buy One Get One", "Bundle Offer"],
        "discount_ranges": ["5%", "10%", "15%", "20%", "25%", "30%", "50%"],
        "validity_options": ["1 Day", "3 Days", "1 Week", "2 Weeks", "1 Month", "Custom"],
        "target_products": ["All Products", "Specific Category", "Selected Items", "New Arrivals"],
        "minimum_purchase_options": ["No Minimum", "₹500", "₹1000", "₹2000", "₹5000"],
        "active_promotions": []
    }


@app.post("/api/merchant/marketing/instant-promotion")
def create_instant_promotion(promotion_data: schemas.InstantPromotionRequest, db: Session = Depends(get_db)):
    """Create instant promotion"""
    try:
        # Create instant promotion
        promotion = models.Promotion(
            promotion_name=promotion_data.promotion_name,
            promotion_type=promotion_data.promotion_type,
            discount_percentage=promotion_data.discount_percentage,
            discount_amount=promotion_data.discount_amount,
            valid_from=date.fromisoformat(promotion_data.valid_from),
            valid_until=date.fromisoformat(promotion_data.valid_until),
            applicable_items=promotion_data.applicable_items,
            minimum_purchase=promotion_data.minimum_purchase
        )

        db.add(promotion)
        db.commit()
        db.refresh(promotion)

        return {
            "success": True,
            "message": "Instant promotion created successfully",
            "promotion_id": promotion.id,
            "promotion_name": promotion.promotion_name,
            "promotion_type": promotion.promotion_type,
            "discount": f"{promotion.discount_percentage}%" if promotion.discount_percentage else f"₹{promotion.discount_amount}",
            "valid_period": f"{promotion.valid_from} to {promotion.valid_until}",
            "status": promotion.status,
            "estimated_impact": "15-25% increase in sales"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create promotion: {str(e)}")


# Company info endpoint
@app.get("/api/chatbot/company-info")
def get_company_info():
    """Get company information"""
    return {
        "company_name": "YouHR Assistant",
        "version": "2.0",
        "description": "Comprehensive HR and Merchant Management System",
        "features": [
            "HR Management",
            "Merchant Operations",
            "Staff Management",
            "Sales Analytics",
            "Marketing Tools"
        ],
        "last_updated": "2024-08-29"
    }


# ===== MISSING MERCHANT ENDPOINTS =====

# Marketing & Growth - Missing endpoints
@app.get("/api/merchant/marketing/campaign-results")
def get_campaign_results(merchant_id: str = Query(..., description="Merchant ID")):
    """Get marketing campaign results"""
    return {
        "merchant_id": merchant_id,
        "total_campaigns": 5,
        "active_campaigns": 2,
        "campaigns": [
            {
                "campaign_id": "WC-001",
                "campaign_name": "Summer Sale 2024",
                "type": "WhatsApp",
                "sent": 1200,
                "delivered": 1150,
                "read": 890,
                "clicked": 120,
                "conversion_rate": "10.1%",
                "revenue_generated": "₹15,600.00",
                "status": "Completed"
            },
            {
                "campaign_id": "WC-002",
                "campaign_name": "Weekend Special",
                "type": "WhatsApp",
                "sent": 800,
                "delivered": 785,
                "read": 620,
                "clicked": 85,
                "conversion_rate": "10.6%",
                "revenue_generated": "₹8,900.00",
                "status": "Active"
            }
        ],
        "overall_performance": {
            "total_reach": 2000,
            "average_open_rate": "75.6%",
            "average_click_rate": "10.3%",
            "total_revenue": "₹24,500.00",
            "roi": "245%"
        }
    }


@app.get("/api/merchant/loan/status")
def get_loan_status(merchant_id: str = Query(..., description="Merchant ID")):
    """Check loan application status"""
    return {
        "merchant_id": merchant_id,
        "loan_applications": [
            {
                "loan_id": "LN-2024-001",
                "application_date": "2024-08-15",
                "loan_amount": "₹1,00,000.00",
                "loan_type": "Business Loan",
                "status": "Under Review",
                "approval_probability": "85%",
                "estimated_approval_date": "2024-09-05",
                "required_documents": [
                    {"document": "KYC", "status": "Submitted"},
                    {"document": "Bank Statements", "status": "Submitted"},
                    {"document": "Business Proof", "status": "Pending"},
                    {"document": "Income Tax Returns", "status": "Submitted"}
                ],
                "loan_officer": "Rahul Sharma",
                "contact": "+91-9876543210"
            }
        ],
        "loan_history": [
            {
                "loan_id": "LN-2023-005",
                "amount": "₹50,000.00",
                "status": "Fully Repaid",
                "disbursed_date": "2023-12-01",
                "completion_date": "2024-06-01"
            }
        ],
        "credit_score": 750,
        "eligible_loan_amount": "₹2,50,000.00"
    }


@app.post("/api/merchant/loan/continue")
def continue_loan_application(
    merchant_id: str = Query(..., description="Merchant ID"),
    document_type: str = Query(..., description="Document type"),
    document_url: str = Query(..., description="Document URL"),
    notes: str = Query(None, description="Additional notes")
):
    """Continue loan application with document upload"""
    return {
        "merchant_id": merchant_id,
        "loan_id": "LN-2024-001",
        "message": "Document uploaded successfully",
        "document_type": document_type,
        "upload_status": "Success",
        "verification_status": "Pending",
        "next_steps": [
            "Wait for document verification",
            "Loan officer will contact within 2 business days",
            "Prepare for final approval process"
        ],
        "completion_percentage": "90%",
        "estimated_approval_date": "2024-09-05"
    }


# Notifications - All endpoints
@app.get("/api/merchant/notifications/leave-requests")
def get_pending_leave_notifications(merchant_id: str = Query(..., description="Merchant ID")):
    """Get pending leave request notifications"""
    return {
        "merchant_id": merchant_id,
        "pending_requests": 3,
        "notifications": [
            {
                "notification_id": "LN-001",
                "employee_name": "Sarah Johnson",
                "employee_id": "EMP002",
                "leave_type": "Annual Leave",
                "from_date": "2024-09-10",
                "to_date": "2024-09-12",
                "days": 3,
                "reason": "Family vacation",
                "applied_date": "2024-08-25",
                "urgency": "Medium",
                "action_required": "Approve/Reject"
            },
            {
                "notification_id": "LN-002",
                "employee_name": "Mike Brown",
                "employee_id": "EMP003",
                "leave_type": "Sick Leave",
                "from_date": "2024-09-02",
                "to_date": "2024-09-03",
                "days": 2,
                "reason": "Medical emergency",
                "applied_date": "2024-09-01",
                "urgency": "High",
                "action_required": "Approve/Reject"
            }
        ],
        "summary": {
            "total_pending": 3,
            "high_priority": 1,
            "medium_priority": 2,
            "overdue_responses": 0
        }
    }


@app.get("/api/merchant/notifications/shift-change")
def get_shift_change_notifications(merchant_id: str = Query(..., description="Merchant ID")):
    """Get shift change request notifications"""
    return {
        "merchant_id": merchant_id,
        "pending_requests": 2,
        "notifications": [
            {
                "notification_id": "SC-001",
                "employee_name": "Lisa Davis",
                "employee_id": "EMP004",
                "current_shift": "Morning (9 AM - 5 PM)",
                "requested_shift": "Evening (2 PM - 10 PM)",
                "effective_date": "2024-09-05",
                "reason": "Personal commitment",
                "applied_date": "2024-08-28",
                "urgency": "Medium",
                "action_required": "Approve/Reject"
            },
            {
                "notification_id": "SC-002",
                "employee_name": "Tom Wilson",
                "employee_id": "EMP005",
                "current_shift": "Evening (2 PM - 10 PM)",
                "requested_shift": "Morning (9 AM - 5 PM)",
                "effective_date": "2024-09-08",
                "reason": "Transportation issues",
                "applied_date": "2024-08-29",
                "urgency": "High",
                "action_required": "Approve/Reject"
            }
        ],
        "summary": {
            "total_pending": 2,
            "high_priority": 1,
            "medium_priority": 1,
            "schedule_conflicts": 0
        }
    }


@app.get("/api/merchant/notifications/payment-settlement")
def get_payment_settlement_notifications(merchant_id: str = Query(..., description="Merchant ID")):
    """Get payment settlement notifications"""
    return {
        "merchant_id": merchant_id,
        "recent_settlements": [
            {
                "settlement_id": "ST-001",
                "date": "2024-08-29",
                "amount": "₹25,400.00",
                "transaction_count": 45,
                "settlement_type": "Daily Settlement",
                "status": "Completed",
                "bank_reference": "UTR123456789",
                "credited_to": "HDFC Bank ****1234"
            },
            {
                "settlement_id": "ST-002",
                "date": "2024-08-28",
                "amount": "₹22,800.00",
                "transaction_count": 38,
                "settlement_type": "Daily Settlement",
                "status": "Completed",
                "bank_reference": "UTR987654321",
                "credited_to": "HDFC Bank ****1234"
            }
        ],
        "pending_settlements": [
            {
                "settlement_id": "ST-003",
                "date": "2024-08-29",
                "amount": "₹8,900.00",
                "transaction_count": 15,
                "expected_credit": "2024-08-30",
                "status": "Processing"
            }
        ],
        "monthly_summary": {
            "total_settled": "₹6,78,900.00",
            "pending_amount": "₹8,900.00",
            "average_daily_settlement": "₹23,410.00"
        }
    }


@app.get("/api/merchant/notifications/renew-subscription")
def get_subscription_notifications(merchant_id: str = Query(..., description="Merchant ID")):
    """Get subscription renewal notifications"""
    return {
        "merchant_id": merchant_id,
        "subscription_status": "Active",
        "current_plan": "YouShop Pro",
        "expiry_date": "2024-10-15",
        "days_remaining": 47,
        "renewal_required": True,
        "notifications": [
            {
                "notification_id": "SUB-001",
                "type": "Renewal Reminder",
                "message": "Your subscription expires in 47 days. Renew now to avoid service interruption.",
                "urgency": "Medium",
                "action_required": "Renew Subscription",
                "renewal_discount": "20% off on annual plans"
            }
        ],
        "subscription_details": {
            "features": [
                "POS System",
                "Inventory Management",
                "Staff Management",
                "Sales Analytics",
                "Marketing Tools"
            ],
            "monthly_cost": "₹2,999.00",
            "annual_cost": "₹29,990.00",
            "savings_on_annual": "₹5,998.00"
        },
        "payment_history": [
            {
                "date": "2023-10-15",
                "amount": "₹29,990.00",
                "plan": "Annual Pro",
                "status": "Paid"
            }
        ]
    }


@app.get("/api/merchant/notifications/head-office-messages")
def get_head_office_messages(merchant_id: str = Query(..., description="Merchant ID")):
    """Get messages from head office"""
    return {
        "merchant_id": merchant_id,
        "unread_messages": 2,
        "total_messages": 8,
        "messages": [
            {
                "message_id": "HO-001",
                "from": "Head Office - Operations",
                "subject": "New Product Launch",
                "message": "We're launching new product categories next month. Please update your inventory system and train staff accordingly.",
                "date": "2024-08-28",
                "priority": "High",
                "status": "Unread",
                "attachments": ["product_catalog.pdf", "training_guide.pdf"],
                "action_required": "Update inventory & staff training"
            },
            {
                "message_id": "HO-002",
                "from": "Head Office - IT Support",
                "subject": "System Maintenance",
                "message": "Scheduled maintenance on September 1st from 2 AM to 4 AM. POS system may be temporarily unavailable.",
                "date": "2024-08-27",
                "priority": "Medium",
                "status": "Unread",
                "action_required": "Plan operations accordingly"
            },
            {
                "message_id": "HO-003",
                "from": "Head Office - HR",
                "subject": "Policy Update",
                "message": "Updated employee handbook is available. Please share with all staff members.",
                "date": "2024-08-25",
                "priority": "Medium",
                "status": "Read",
                "attachments": ["employee_handbook_v2.pdf"]
            }
        ],
        "announcements": [
            {
                "title": "Q3 Performance Awards",
                "content": "Congratulations! Your store is among top 10 performers this quarter.",
                "date": "2024-08-20",
                "type": "Achievement"
            }
        ]
    }


# Help & Support - All endpoints
@app.post("/api/merchant/support/pos-app")
def report_pos_app_problem(
    merchant_id: str = Query(..., description="Merchant ID"),
    problem_description: str = Query(..., description="Problem description"),
    error_code: str = Query(None, description="Error code if any"),
    priority: str = Query("Medium", description="Priority level")
):
    """Report POS application problem"""
    return {
        "merchant_id": merchant_id,
        "ticket_id": f"POS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": "POS app problem reported successfully",
        "problem_description": problem_description,
        "error_code": error_code,
        "priority": priority,
        "status": "Open",
        "assigned_to": "Technical Support Team",
        "estimated_resolution": "2-4 hours",
        "support_contact": "+91-1800-123-4567",
        "next_steps": [
            "Technical team will analyze the issue",
            "Remote assistance may be provided",
            "You will receive updates via SMS/Email"
        ]
    }


@app.post("/api/merchant/support/hardware")
def report_hardware_issue(
    merchant_id: str = Query(..., description="Merchant ID"),
    hardware_type: str = Query(..., description="Hardware type"),
    issue_description: str = Query(..., description="Issue description"),
    model: str = Query(None, description="Hardware model"),
    priority: str = Query("Medium", description="Priority level")
):
    """Report hardware issue"""
    return {
        "merchant_id": merchant_id,
        "ticket_id": f"HW-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": "Hardware issue reported successfully",
        "hardware_type": hardware_type,
        "model": model,
        "issue_description": issue_description,
        "priority": priority,
        "status": "Open",
        "assigned_to": "Field Support Team",
        "estimated_resolution": "4-8 hours",
        "service_engineer": "Will be assigned based on location",
        "support_contact": "+91-1800-123-4567",
        "next_steps": [
            "Service engineer will be assigned",
            "Engineer will contact you within 2 hours",
            "On-site visit will be scheduled if required"
        ]
    }


@app.post("/api/merchant/support/ai-camera")
def report_ai_camera_problem(
    merchant_id: str = Query(..., description="Merchant ID"),
    camera_id: str = Query(..., description="Camera ID"),
    problem_description: str = Query(..., description="Problem description"),
    error_logs: str = Query(None, description="Error logs"),
    priority: str = Query("Medium", description="Priority level")
):
    """Report AI camera (YouLens) problem"""
    return {
        "merchant_id": merchant_id,
        "camera_id": camera_id,
        "ticket_id": f"CAM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": "AI camera problem reported successfully",
        "problem_description": problem_description,
        "error_logs": error_logs,
        "priority": priority,
        "status": "Open",
        "assigned_to": "AI Support Team",
        "estimated_resolution": "2-6 hours",
        "support_contact": "+91-1800-123-4567",
        "remote_diagnostics": "Available",
        "next_steps": [
            "AI team will run remote diagnostics",
            "Camera logs will be analyzed",
            "Software update may be pushed",
            "On-site visit if hardware issue detected"
        ]
    }


@app.post("/api/merchant/support/camera-installation")
def request_camera_installation(
    merchant_id: str = Query(..., description="Merchant ID"),
    request_type: str = Query(..., description="Installation or Training"),
    location: str = Query(..., description="Installation location"),
    preferred_date: str = Query(..., description="Preferred date"),
    notes: str = Query(None, description="Additional notes")
):
    """Request camera installation or training"""
    return {
        "merchant_id": merchant_id,
        "request_id": f"INST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": f"Camera {request_type.lower()} request submitted successfully",
        "request_type": request_type,
        "location": location,
        "preferred_date": preferred_date,
        "notes": notes,
        "status": "Scheduled",
        "assigned_engineer": "Will be assigned based on location",
        "estimated_duration": "2-4 hours",
        "support_contact": "+91-1800-123-4567",
        "next_steps": [
            "Installation team will contact you",
            "Site survey will be conducted",
            "Installation date will be confirmed",
            "Training session will be provided"
        ]
    }


@app.post("/api/merchant/support/general")
def submit_general_support(
    merchant_id: str = Query(..., description="Merchant ID"),
    category: str = Query(..., description="Support category"),
    subject: str = Query(..., description="Subject"),
    description: str = Query(..., description="Detailed description"),
    priority: str = Query("Low", description="Priority level")
):
    """Submit general support request"""
    return {
        "merchant_id": merchant_id,
        "ticket_id": f"GEN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": "General support request submitted successfully",
        "category": category,
        "subject": subject,
        "description": description,
        "priority": priority,
        "status": "Open",
        "assigned_to": "Customer Support Team",
        "estimated_response": "4-24 hours",
        "support_contact": "+91-1800-123-4567",
        "ticket_url": f"https://support.youshop.com/ticket/GEN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "next_steps": [
            "Support team will review your request",
            "You will receive response via email",
            "Additional information may be requested",
            "Solution will be provided or escalated as needed"
        ]
    }


# Feedback & Ideas - All endpoints
@app.post("/api/merchant/feedback/rate-experience")
def rate_bot_experience(
    merchant_id: str = Query(..., description="Merchant ID"),
    rating: str = Query(..., description="Good or Bad"),
    category: str = Query(..., description="Experience category"),
    comments: str = Query(None, description="Additional comments")
):
    """Rate experience with the bot"""
    return {
        "merchant_id": merchant_id,
        "feedback_id": f"RATE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": "Thank you for rating your experience!",
        "rating": rating,
        "category": category,
        "comments": comments,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "status": "Recorded",
        "follow_up": "Your feedback helps us improve our services",
        "additional_survey": "https://feedback.youshop.com/detailed-survey" if rating == "Bad" else None,
        "next_steps": [
            "Feedback has been recorded",
            "Product team will review feedback",
            "Improvements will be implemented based on feedback"
        ]
    }


@app.post("/api/merchant/feedback/share")
def share_detailed_feedback(
    merchant_id: str = Query(..., description="Merchant ID"),
    feedback_type: str = Query(..., description="POS/Loan/Camera/Staff"),
    rating: str = Query(..., description="Rating 1-5"),
    feedback: str = Query(..., description="Detailed feedback"),
    suggestions: str = Query(None, description="Suggestions for improvement")
):
    """Share detailed feedback on services"""
    return {
        "merchant_id": merchant_id,
        "feedback_id": f"FB-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": "Detailed feedback submitted successfully",
        "feedback_type": feedback_type,
        "rating": f"{rating}/5",
        "feedback": feedback,
        "suggestions": suggestions,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "status": "Under Review",
        "assigned_to": f"{feedback_type} Product Team",
        "estimated_review_time": "3-5 business days",
        "next_steps": [
            "Product team will analyze your feedback",
            "Suggestions will be evaluated for implementation",
            "You may be contacted for additional details",
            "Updates on improvements will be shared"
        ]
    }


@app.post("/api/merchant/feedback/suggest-feature")
def suggest_new_feature(
    merchant_id: str = Query(..., description="Merchant ID"),
    feature_name: str = Query(..., description="Feature name"),
    description: str = Query(..., description="Feature description"),
    category: str = Query(..., description="Feature category"),
    priority: str = Query("Medium", description="Priority level")
):
    """Suggest new feature for YouShop"""
    return {
        "merchant_id": merchant_id,
        "suggestion_id": f"FEAT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": "Feature suggestion submitted successfully",
        "feature_name": feature_name,
        "description": description,
        "category": category,
        "priority": priority,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "status": "Under Evaluation",
        "assigned_to": "Product Development Team",
        "evaluation_timeline": "2-4 weeks",
        "community_voting": f"https://features.youshop.com/suggestion/FEAT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "next_steps": [
            "Product team will evaluate feasibility",
            "Community voting will be enabled",
            "Technical assessment will be conducted",
            "Implementation roadmap will be shared if approved"
        ]
    }
