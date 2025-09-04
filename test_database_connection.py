import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_database_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set in the environment.")
        return

    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(database_url)
        print("✅ Successfully connected to the database!")
        connection.close()
    except Exception as e:
        print(f"❌ Failed to connect to the database: {e}")


if __name__ == "__main__":
    test_database_connection()
