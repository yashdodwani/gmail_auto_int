import psycopg2
import os
from email.utils import parsedate_to_datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("NEON_DATABASE_URL")


def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def setup_database():
    """Ensures the emails table exists."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        create_table_sql = """
                           CREATE TABLE IF NOT EXISTS emails \
                           ( \
                               id \
                               SERIAL \
                               PRIMARY \
                               KEY, \
                               message_id \
                               VARCHAR \
                           ( \
                               255 \
                           ) UNIQUE NOT NULL,
                               sender VARCHAR \
                           ( \
                               255 \
                           ) NOT NULL,
                               subject TEXT,
                               received_date TIMESTAMP WITH TIME ZONE NOT NULL,
                                                           snippet TEXT,
                                                           is_read BOOLEAN DEFAULT FALSE
                                                           ); \
                           """
        cursor.execute(create_table_sql)
        conn.commit()
        print("Database and table checked successfully.")
    except psycopg2.Error as e:
        print(f"Database setup error: {e}")
    finally:
        conn.close()


def save_emails_to_db(emails):
    """
    Takes a list of email dictionaries and saves them to the database.
    Skips emails that already exist (based on message_id).
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        count = 0

        insert_query = """
                       INSERT INTO emails (message_id, sender, subject, received_date, snippet)
                       VALUES (%s, %s, %s, %s, %s) ON CONFLICT (message_id) DO NOTHING; \
                       """

        for email in emails:
            # 1. Parse the date string into a Python datetime object
            try:
                clean_date = parsedate_to_datetime(email['received_date'])
            except Exception:
                # Fallback if date format is weird, though Gmail is usually consistent
                clean_date = None

            if clean_date:
                cursor.execute(insert_query, (
                    email['message_id'],
                    email['sender'],
                    email['subject'],
                    clean_date,
                    email['snippet']
                ))
                if cursor.rowcount > 0:
                    count += 1

        conn.commit()
        print(f"Successfully stored {count} new emails in the database.")

    except psycopg2.Error as e:
        print(f"Error saving emails: {e}")
    finally:
        conn.close()


def get_all_emails():
    """Fetches all emails from the database to process them."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        # Fetch all fields we need for rules
        cursor.execute("SELECT message_id, sender, subject, received_date, snippet FROM emails")
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results
    except psycopg2.Error as e:
        print(f"Error fetching emails: {e}")
        return []
    finally:
        conn.close()


if __name__ == "__main__":
    setup_database()