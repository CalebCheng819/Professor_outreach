import sqlite3
import os

# Path to database
DB_PATH = "sql_app.db"

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(professors)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "target_role" in columns:
            print("Column 'target_role' already exists. Skipping.")
        else:
            print("Adding 'target_role' column...")
            cursor.execute("ALTER TABLE professors ADD COLUMN target_role TEXT DEFAULT 'summer_intern'")
            conn.commit()
            print("Migration successful!")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
