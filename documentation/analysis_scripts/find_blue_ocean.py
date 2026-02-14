import sqlite3
import pandas as pd

def find_low_competition_winners(db_path):
    conn = sqlite3.connect(db_path)
    # Buscamos nichos con AVG Price alto, pocas variantes (fácil de gestionar)
    # y que no sean las marcas de siempre que han salido antes
    query = """
    SELECT s.domain, m.avg_price, m.total_products, m.hero_score, m.vendor_count, m.avg_variants
    FROM stores s
    JOIN metrics m ON s.id = m.store_id
    WHERE m.total_products BETWEEN 10 AND 100
      AND m.avg_price > 50
      AND m.vendor_count BETWEEN 1 AND 3
      AND s.domain NOT LIKE '%huel%' 
      AND s.domain NOT LIKE '%casper%'
      AND s.domain NOT LIKE '%tonal%'
    ORDER BY m.hero_score DESC, m.avg_price DESC
    LIMIT 15
    """
    df = pd.read_sql_query(query, conn)
    print("Potential Blue Ocean Winners (High Margin, Specific Niche):")
    print(df.to_string())
    conn.close()

find_low_competition_winners("/home/noorm/Escritorio/SAAS_v2/shopify_study/database.db")
