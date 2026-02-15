import sqlite3

def check_candidates():
    db_path = "radar.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check candidates with "Unknown" name
    query = """
    SELECT id, product_name, url, keyword
    FROM candidates 
    WHERE product_name = 'Unknown'
    LIMIT 10;
    """
    
    print("Checking candidates with 'Unknown' name:")
    unknowns = cursor.execute(query).fetchall()
    for u in unknowns:
        print(u)
        
    query_total = "SELECT count(*) FROM candidates WHERE product_name = 'Unknown';"
    total_unknown = cursor.execute(query_total).fetchone()[0]
    print(f"\nTotal 'Unknown' candidates: {total_unknown}")
    
    conn.close()

if __name__ == "__main__":
    check_candidates()
