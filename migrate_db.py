import sqlite3

def migrate():
    print("Migrating database schema...")
    conn = sqlite3.connect("shopify_study/database.db")
    cursor = conn.cursor()
    
    # Add new columns to 'metrics' table
    # SQLite doesn't support adding multiple columns in one statement easily in older versions, 
    # so we do one by one.
    
    columns = [
        ("currency", "VARCHAR"),
        ("theme", "VARCHAR"),
        ("social_links", "TEXT"),
        ("pixels", "TEXT")
    ]
    
    for col_name, col_type in columns:
        try:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE metrics ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {col_name} already exists. Skipping.")
            else:
                print(f"Error adding {col_name}: {e}")
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
