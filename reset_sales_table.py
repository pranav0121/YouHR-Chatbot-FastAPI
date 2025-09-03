from sqlalchemy import create_engine, MetaData
from app.models import Base

# Update the database URL if necessary
database_url = "sqlite:///chatbot.db"

# Create the database engine
engine = create_engine(database_url)
metadata = MetaData()


def reset_sales_table():
    with engine.connect() as connection:
        # Drop the sales_records table if it exists
        print("Dropping existing sales_records table (if any)...")
        connection.execute("DROP TABLE IF EXISTS sales_records")

        # Recreate all tables based on the current models
        print("Recreating tables...")
        Base.metadata.create_all(engine)
        print("Tables recreated successfully.")


if __name__ == "__main__":
    reset_sales_table()
