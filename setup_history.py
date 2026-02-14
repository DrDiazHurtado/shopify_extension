import sqlite3

def setup_snapshots():
    conn = sqlite3.connect("shopify_study/database.db")
    
    # 1. Tabla Snapshots (Histórico)
    # Almacena una foto de cómo estaba la tienda en ese momento.
    # Así podemos calcular "Crecimiento Semanal" o "Bajada de Precios".
    conn.execute("""
    CREATE TABLE IF NOT EXISTS store_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_id INTEGER,
        snapshot_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_products INTEGER,
        avg_price FLOAT,
        hero_score FLOAT,
        vendor_count INTEGER,
        discount_ratio FLOAT,
        currency TEXT,
        scan_meta JSON,
        FOREIGN KEY(store_id) REFERENCES stores(id)
    )
    """)
    
    try:
        conn.execute("ALTER TABLE store_snapshots ADD COLUMN scan_meta JSON")
    except:
        pass
    
    # Índice para buscar rápido el historial de una tienda
    conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_store ON store_snapshots(store_id, snapshot_at DESC)")
    
    conn.commit()
    conn.close()
    print("✅ Historial de Snapshots configurado en SQLite.")

if __name__ == "__main__":
    setup_snapshots()
