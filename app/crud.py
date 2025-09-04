from sqlalchemy.orm import Session
from app import models, schemas


def get_merchant_sales_today(db: Session, merchant_id: int):
    return db.execute(
        "SELECT transaction_id, amount, customer_name FROM sales WHERE date = CURRENT_DATE AND merchant_id = :merchant_id",
        {"merchant_id": merchant_id}
    ).fetchall()


def get_merchant_sales_weekly(db: Session, merchant_id: int):
    return db.execute(
        "SELECT date, SUM(amount) as total_sales, COUNT(transaction_id) as transactions FROM sales WHERE date >= CURRENT_DATE - INTERVAL '7 days' AND merchant_id = :merchant_id GROUP BY date",
        {"merchant_id": merchant_id}
    ).fetchall()


def get_retention_activities(db: Session):
    return db.query(models.Activity).all()
