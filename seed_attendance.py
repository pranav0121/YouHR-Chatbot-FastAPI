from app.database import SessionLocal
from app.models import AttendanceRecord
from datetime import date, time, timedelta
import random

# Create DB session
db = SessionLocal()

# Sample attendance data for the last 30 days
employee_id = "EMP001"
employee_name = "John Doe"
end_date = date.today()

print("Seeding attendance data...")

# Generate attendance records for the last 30 days
attendance_records = []
for i in range(30):
    current_date = end_date - timedelta(days=i)

    # Skip weekends (Saturday=5, Sunday=6)
    if current_date.weekday() >= 5:
        continue

    # Randomly determine attendance status
    status_choice = random.choices(
        ["Present", "Late", "Absent", "Half Day"],
        weights=[70, 15, 10, 5]
    )[0]

    check_in_time = None
    check_out_time = None
    working_hours = None

    if status_choice == "Present":
        check_in_time = time(9, random.randint(0, 30))  # 9:00-9:30 AM
        check_out_time = time(18, random.randint(0, 30))  # 6:00-6:30 PM
        working_hours = "8h 30m"
    elif status_choice == "Late":
        check_in_time = time(9, random.randint(45, 59))  # 9:45-9:59 AM
        check_out_time = time(18, random.randint(0, 30))  # 6:00-6:30 PM
        working_hours = "8h 15m"
    elif status_choice == "Half Day":
        check_in_time = time(9, random.randint(0, 30))  # 9:00-9:30 AM
        check_out_time = time(13, random.randint(0, 30))  # 1:00-1:30 PM
        working_hours = "4h 30m"
    # For "Absent", times remain None

    location = "Main Office" if status_choice != "Absent" else None

    record = AttendanceRecord(
        employee_id=employee_id,
        employee_name=employee_name,
        date=current_date,
        check_in_time=check_in_time,
        check_out_time=check_out_time,
        working_hours=working_hours,
        status=status_choice,
        location=location
    )
    attendance_records.append(record)

# Add all records to database
db.add_all(attendance_records)
db.commit()
db.close()

print(
    f"✅ Added {len(attendance_records)} attendance records for employee {employee_id}")
