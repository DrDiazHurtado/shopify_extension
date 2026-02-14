import sqlite3
import pandas as pd

def find_niche_goldmine_v2(db_path):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT s.domain, m.avg_price, m.total_products, m.hero_score, m.vendor_count
    FROM stores s
    JOIN metrics m ON s.id = m.store_id
    WHERE m.total_products < 100
      AND m.avg_price > 30
    ORDER BY m.hero_score DESC
    LIMIT 20
    """
    df = pd.read_sql_query(query, conn)
    print("Potential Niche Winners:")
    print(df.to_string())
    
    # Ver qué venden los top results
    for domain in df['domain'].head(5):
        print(f"\nSample products from {domain}:")
        p_query = f"SELECT title, price FROM products WHERE store_id = (SELECT id FROM stores WHERE domain = '{domain}') LIMIT 5"
        print(pd.read_sql_query(p_query, conn).to_string())
        
    conn.close()

find_niche_goldmine_v2("/home/noorm/Escritorio/SAAS_v2/shopify_study/database.db")
