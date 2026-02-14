import sqlite3

def check_stores_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info(stores)")
    print(cursor.fetchall())
    conn.close()

check_stores_schema("/home/noorm/Escritorio/SAAS_v2/shopify_study/database.db")
