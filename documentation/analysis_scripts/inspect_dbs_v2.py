import sqlite3
import pandas as pd

def check_db(db_path):
    print(f"\n{'='*50}\nChecking {db_path}\n{'='*50}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 10", conn)
        print(df.to_string())
    conn.close()

try:
    check_db("/home/noorm/Escritorio/SAAS_v2/radar.db")
    check_db("/home/noorm/Escritorio/SAAS_v2/shopify_study/database.db")
except Exception as e:
    print(f"Error: {e}")
