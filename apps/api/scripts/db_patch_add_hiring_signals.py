import sqlite3
import os

# Path to database
DB_PATH = "sql_app.db"

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(professor_cards)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "hiring_signals" not in column_names:
            print("Adding 'hiring_signals' column to 'professor_cards'...")
            cursor.execute("ALTER TABLE professor_cards ADD COLUMN hiring_signals TEXT")
            conn.commit()
            print("Migration successful!")
        else:
            print("'hiring_signals' column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
