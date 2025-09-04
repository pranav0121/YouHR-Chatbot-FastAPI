import psycopg2

# Database connection details
DATABASE_URL = "postgresql://postgres:pranav@localhost:5433/you_assistant"

# Path to the SQL file
SQL_FILE = "migrations/create_missing_tables.sql"


def execute_sql_file():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Read the SQL file
        with open(SQL_FILE, "r") as file:
            sql_commands = file.read()

        # Execute the SQL commands
        cursor.execute(sql_commands)
        conn.commit()

        print("SQL file executed successfully.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    execute_sql_file()
