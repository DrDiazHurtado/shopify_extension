import sqlite3

def check_structure():
    conn = sqlite3.connect("shopify_study/database.db")
    cursor = conn.cursor()
    
    print("--- Table 'stores' ---")
    rows = cursor.execute("PRAGMA table_info(stores)").fetchall()
    for row in rows:
        print(row)
        
    print("\n--- Table 'metrics' ---")
    rows = cursor.execute("PRAGMA table_info(metrics)").fetchall()
    for row in rows:
        print(row)
        
    conn.close()

if __name__ == "__main__":
    check_structure()
