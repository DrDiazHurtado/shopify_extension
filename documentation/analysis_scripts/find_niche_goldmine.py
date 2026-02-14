import sqlite3
import pandas as pd

def find_niche_goldmine(db_path):
    conn = sqlite3.connect(db_path)
    # Criterios:
    # 1. Pocos productos (Fácil de implementar)
    # 2. Precio medio decente (Margen alto)
    # 3. Un solo vendedor (Marca propia/Nicho)
    # 4. Hero Score saludable (Un producto estrella claro)
    query = """
    SELECT s.domain, m.avg_price, m.total_products, m.hero_score, m.vendor_count
    FROM stores s
    JOIN metrics m ON s.id = m.store_id
    WHERE m.total_products BETWEEN 5 AND 50
      AND m.avg_price BETWEEN 30 AND 150
      AND m.vendor_count = 1
    ORDER BY m.hero_score DESC
    """
    df = pd.read_sql_query(query, conn)
    print("Niche Goldmines Found:")
    print(df.to_string())
    conn.close()

find_niche_goldmine("/home/noorm/Escritorio/SAAS_v2/shopify_study/database.db")
