from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import SalesRecord
from datetime import datetime, date

# Update the database URL if necessary
database_url = "sqlite:///chatbot.db"

# Create the database engine and session
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_sales_data():
    session = SessionLocal()
    try:
        # Sample sales data
        sales_data = [
            {"merchant_id": "M001", "product_name": "Coffee", "quantity": 12,
                "revenue": "₹360.00", "sale_date": "2025-08-30"},
            {"merchant_id": "M001", "product_name": "Pizza", "quantity": 6,
                "revenue": "₹900.00", "sale_date": "2025-08-30"},
            {"merchant_id": "M001", "product_name": "Burger", "quantity": 10,
                "revenue": "₹1,500.00", "sale_date": "2025-08-30"},
            {"merchant_id": "M001", "product_name": "Salad", "quantity": 5,
                "revenue": "₹250.00", "sale_date": "2025-08-30"},
            {"merchant_id": "M001", "product_name": "Juice", "quantity": 18,
                "revenue": "₹540.00", "sale_date": "2025-08-30"},
            {"merchant_id": "MERCH001", "product_name": "Coffee",
                "quantity": 12, "revenue": "₹360.00", "sale_date": "2025-08-30"},
            {"merchant_id": "MERCH001", "product_name": "Pizza",
                "quantity": 6, "revenue": "₹900.00", "sale_date": "2025-08-30"},
            {"merchant_id": "MERCH001", "product_name": "Burger",
                "quantity": 10, "revenue": "₹1,500.00", "sale_date": "2025-08-30"}
        ]

        # Convert sale_date to Python date objects
        for data in sales_data:
            data["sale_date"] = datetime.strptime(
                data["sale_date"], "%Y-%m-%d").date()

        # Insert sales data into the database
        for data in sales_data:
            sale = SalesRecord(**data)
            session.add(sale)

        session.commit()
        print("Sales data seeded successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    seed_sales_data()
