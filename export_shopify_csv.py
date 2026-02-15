import sqlite3
import pandas as pd

def export_shopify_csv():
    db_path = "shopify_study/database.db"
    conn = sqlite3.connect(db_path)
    
    # Query to join stores and metrics
    query = """
    SELECT 
        s.domain, 
        m.total_products, 
        m.avg_price, 
        m.hero_score, 
        m.vendor_count, 
        m.discount_ratio
    FROM stores s
    JOIN metrics m ON s.id = m.store_id
    ORDER BY m.hero_score DESC
    LIMIT 250;
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        output_file = "shopify_stores_export.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Exported {len(df)} Shopify stores to {output_file}")
    except Exception as e:
        print(f"❌ Error exporting CSV: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    export_shopify_csv()
