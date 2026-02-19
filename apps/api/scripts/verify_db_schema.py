import sqlite3
import os

DB_PATH = "sql_app.db"

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Table 'professors' columns:")
        cursor.execute("PRAGMA table_info(professors)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
            
        target_role_exists = any(col[1] == 'target_role' for col in columns)
        if target_role_exists:
            print("\nSUCCESS: 'target_role' column exists.")
        else:
            print("\nFAILURE: 'target_role' column is MISSING.")
            
    except Exception as e:
        print(f"Error inspecting DB: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
