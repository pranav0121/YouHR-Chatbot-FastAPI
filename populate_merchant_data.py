from app.database import get_db
from app import models
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random


def populate_merchant_data(db: Session, merchant_id: int = 1):
    # Clear some merchant-related tables (safe for dev)
    try:
        db.query(models.SalesRecord).delete()
        db.query(models.ExpenseRecord).delete()
        db.query(models.Promotion).delete()
        db.query(models.MarketingCampaign).delete()
        db.query(models.StaffMessage).delete()
        db.query(models.Employee).delete()
        db.commit()
    except Exception:
        db.rollback()

    today = date.today()

    # Sales: create entries for today and last 7 days
    sales = []
    for d in range(0, 8):
        dt = today - timedelta(days=d)
        for _ in range(random.randint(3, 8)):
            sales.append(models.SalesRecord(
                date=dt, amount=random.randint(100, 5000), merchant_id=merchant_id))

    db.add_all(sales)

    # Expenses
    expenses = [
        models.ExpenseRecord(expense_id=f"EXP{1000+i}", category=random.choice(["Rent", "Utilities", "Inventory", "Salaries", "Marketing"]), description="Dummy expense", amount=str(
            random.randint(100, 5000)), date=today - timedelta(days=random.randint(0, 7)), vendor_name="Vendor X", payment_method="Bank Transfer", status="Paid")
        for i in range(3)
    ]
    db.add_all(expenses)

    # Promotions
    promotions = [
        models.Promotion(promotion_name="Back to School", promotion_type="Percentage", discount_percentage=10,
                         valid_from=today - timedelta(days=10), valid_until=today + timedelta(days=20)),
        models.Promotion(promotion_name="Weekend Sale", promotion_type="Fixed Amount", discount_amount="50",
                         valid_from=today - timedelta(days=2), valid_until=today + timedelta(days=5))
    ]
    db.add_all(promotions)

    # Marketing campaigns
    campaigns = [
        models.MarketingCampaign(campaign_name="Launch Promo", campaign_type="Email",
                                 target_audience="All Customers", message_content="Welcome offer", scheduled_date=today)
    ]
    db.add_all(campaigns)

    # Staff / employees
    employees = [
        models.Employee(employee_id=f"EMP{100+i}", employee_name=f"Staff {i}", email=f"staff{i}@shop.com", phone="", department="Sales",
                        position="Associate", employment_type="Full-time", employment_status="Active", hire_date=today - timedelta(days=365))
        for i in range(3)
    ]
    db.add_all(employees)

    # Staff messages
    messages = [
        models.StaffMessage(message_id=f"MSG{100+i}", from_user=f"Staff {i}", to_user="Manager",
                            subject="Request", message_content="Please approve leave", priority="Medium")
        for i in range(2)
    ]
    db.add_all(messages)

    db.commit()
    print("Merchant dummy data populated.")


if __name__ == '__main__':
    db = next(get_db())
    populate_merchant_data(db)
