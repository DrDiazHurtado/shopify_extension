import sqlite3
import pandas as pd

def find_hidden_winners(db_path):
    conn = sqlite3.connect(db_path)
    # Relajamos filtros para encontrar más datos
    query = """
    SELECT s.domain, m.avg_price, m.total_products, m.hero_score, m.vendor_count, m.inventory_recency_days
    FROM stores s
    JOIN metrics m ON s.id = m.store_id
    WHERE m.inventory_recency_days < 30
      AND m.hero_score > 0.1
    ORDER BY m.hero_score DESC
    LIMIT 20
    """
    df = pd.read_sql_query(query, conn)
    print("Stores with Recent Inventory Activity (Active Sales):")
    print(df.to_string())
    conn.close()

find_hidden_winners("/home/noorm/Escritorio/SAAS_v2/shopify_study/database.db")
