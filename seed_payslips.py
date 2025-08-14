from app.database import SessionLocal
from app.models import Payslip
from datetime import date, timedelta
import calendar

# Create DB session
db = SessionLocal()

print("Seeding payslip data...")

# Sample payslip data for the last 6 months
employee_id = "EMP001"
employee_name = "John Doe"

# Generate payslips for last 6 months
payslips = []
current_date = date.today()

for i in range(6):
    # Calculate the month
    month_date = date(current_date.year, current_date.month - i, 1)
    if month_date.month <= 0:
        month_date = date(current_date.year - 1, 12 + month_date.month, 1)

    # Get the last day of the month
    last_day = calendar.monthrange(month_date.year, month_date.month)[1]
    period_start = month_date
    period_end = date(month_date.year, month_date.month, last_day)
    pay_period = f"{month_date.year}-{month_date.month:02d}"

    # Sample salary data (varying slightly each month)
    basic_salary = "$4,500"
    allowances = "$1,200"
    gross_salary = "$5,700"
    deductions = "$1,140"
    net_salary = "$4,560"

    # Adjust for some months (bonus, overtime, etc.)
    if i == 1:  # Last month - bonus
        allowances = "$1,700"
        gross_salary = "$6,200"
        net_salary = "$5,060"
    elif i == 3:  # 3 months ago - overtime
        allowances = "$1,400"
        gross_salary = "$5,900"
        net_salary = "$4,760"

    payslip = Payslip(
        employee_id=employee_id,
        employee_name=employee_name,
        pay_period=pay_period,
        pay_period_start=period_start,
        pay_period_end=period_end,
        basic_salary=basic_salary,
        allowances=allowances,
        gross_salary=gross_salary,
        deductions=deductions,
        net_salary=net_salary,
        status="Generated",
        # Generated 3 days after month end
        generated_date=period_end + timedelta(days=3)
    )
    payslips.append(payslip)

# Add all payslips to database
db.add_all(payslips)
db.commit()
db.close()

print(f"✅ Added {len(payslips)} payslip records for employee {employee_id}")
