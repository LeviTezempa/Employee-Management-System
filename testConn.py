from app_utils import get_db_connection

connection = get_db_connection()
try:
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT 1")
        cursor.fetchone()
        print("Database connection successful.")
    finally:
        cursor.close()
finally:
    connection.close()