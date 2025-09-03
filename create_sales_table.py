from sqlalchemy import create_engine
from app.models import Base

# Update the database URL if necessary
database_url = "sqlite:///chatbot.db"

# Create the database engine
engine = create_engine(database_url)

# Create the sales_records table
if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
