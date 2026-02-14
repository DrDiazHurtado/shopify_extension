import sqlite3
import pandas as pd

def analyze_best_niche(db_path):
    conn = sqlite3.connect(db_path)
    # Buscamos tiendas con métricas de éxito (Hero Score alto, buen volumen)
    # y miramos los productos que están "explotando"
    query = """
    SELECT s.domain, m.hero_score, m.discount_ratio, m.avg_price, m.total_products, m.vendor_count
    FROM stores s
    JOIN metrics m ON s.id = m.store_id
    WHERE m.total_products > 10 AND m.total_products < 250
    ORDER BY m.hero_score DESC
    LIMIT 10
    """
    df_stores = pd.read_sql_query(query, conn)
    print("Top Stores by Hero Score (Dominancia de un solo producto):")
    print(df_stores.to_string())
    
    # Análisis de categorías si estuvieran disponibles, o productos recurrentes
    conn.close()

print("Analizando datos de shopify_study/database.db...")
analyze_best_niche("/home/noorm/Escritorio/SAAS_v2/shopify_study/database.db")
