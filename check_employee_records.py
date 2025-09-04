import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_employee_records():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set in the environment.")
        return

    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(database_url)
        cursor = connection.cursor()

        # Query to check employee records
        cursor.execute("SELECT * FROM employees;")
        records = cursor.fetchall()

        if records:
            print(f"✅ Found {len(records)} employee records.")
        else:
            print("❌ No employee records found in the database.")

        cursor.close()
        connection.close()
    except Exception as e:
        print(f"❌ Failed to query the database: {e}")


if __name__ == "__main__":
    check_employee_records()
