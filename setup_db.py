# python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("NEON_DATABASE_URL")


def setup_database():
    """Connects to the database and ensures the emails table exists."""
    if not DATABASE_URL:
        print("NEON_DATABASE_URL not set in environment.")
        return

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        create_table_sql = """
        CREATE TABLE IF NOT EXISTS emails (
            id SERIAL PRIMARY KEY,
            message_id VARCHAR(255) UNIQUE NOT NULL,
            sender VARCHAR(255) NOT NULL,
            subject TEXT,
            received_date TIMESTAMP WITH TIME ZONE NOT NULL,
            snippet TEXT,
            is_read BOOLEAN DEFAULT FALSE
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print("Database connection successful and 'emails' table ensured.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    setup_database()
