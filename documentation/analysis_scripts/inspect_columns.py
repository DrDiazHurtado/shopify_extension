import sqlite3

def print_columns(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\nColumns in {table_name}:")
    for col in columns:
        print(col)
    conn.close()

print_columns("/home/noorm/Escritorio/SAAS_v2/radar.db", "candidates")
print_columns("/home/noorm/Escritorio/SAAS_v2/radar.db", "scores")
