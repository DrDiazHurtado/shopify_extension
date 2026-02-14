import sqlite3

def check_db_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"\nTable: {table[0]}")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        print(cursor.fetchall())
    conn.close()

check_db_schema("/home/noorm/Escritorio/SAAS_v2/shopify_study/database.db")
