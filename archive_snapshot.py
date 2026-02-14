import sqlite3
import datetime
from loguru import logger

def archive_current_state():
    db_path = "shopify_study/database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Seleccionar todas las tiendas activas y sus métricas actuales
    query = """
    SELECT 
        s.id as store_id, 
        m.total_products, 
        m.avg_price, 
        m.hero_score, 
        m.vendor_count, 
        m.discount_ratio,
        m.currency
    FROM stores s
    JOIN metrics m ON s.id = m.store_id
    """
    
    stores = cursor.execute(query).fetchall()
    
    if not stores:
        logger.warning("No stores found to archive.")
        conn.close()
        return

    logger.info(f"Archiving snapshots for {len(stores)} stores...")
    
    # 2. Insertar en tabla histórica con fecha de hoy
    snapshot_sql = """
    INSERT INTO store_snapshots (
        store_id, snapshot_at, total_products, avg_price, hero_score, vendor_count, discount_ratio, currency
    ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?)
    """
    
    count = 0
    for s in stores:
        # store_id, total, avg, hero, vendor, discount, currency
        try:
            cursor.execute(snapshot_sql, (s[0], s[1], s[2], s[3], s[4], s[5], s[6]))
            count += 1
        except Exception as e:
            logger.error(f"Failed to archive store {s[0]}: {e}")
            
    conn.commit()
    conn.close()
    logger.success(f"✅ Created {count} historical snapshots.")

if __name__ == "__main__":
    archive_current_state()
