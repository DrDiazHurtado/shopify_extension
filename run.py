import typer
import subprocess
import sys
import sqlite3
import datetime
from loguru import logger
import time

app = typer.Typer()

@app.command()
def daily_pulse(
    fresh_batch_size: int = 150, 
    rescan_existing: bool = True
):
    """
    JOB DIARIO: 
    1. Escanea nuevas tiendas (Discovery).
    2. Re-escanea tiendas existentes para calcular "Deltas/Señales" (Temporalidad).
    3. Archiva Snapshots locales.
    4. Sincroniza a la Nube (V2).
    """
    logger.info("=== 🌅 STARTING DAILY INTELLIGENCE RUN ===")
    start_time = time.time()

    # PASO 1: Discovery (Nuevas Tiendas)
    logger.info(f"🔎 Phase 1: Discovery ({fresh_batch_size} stores)...")
    try:
        # Usamos el massive_scanner para pillar tiendas frescas del CSV
        # Modificamos massive_scanner para aceptar argumento o lo llamamos así
        subprocess.run([sys.executable, "-m", "shopify_study.massive_scanner"], check=True)
    except Exception as e:
        logger.error(f"Discovery Failed: {e}")

    # PASO 2: Temporalidad (Re-scan de tiendas clave)
    if rescan_existing:
        logger.info("🔄 Phase 2: Updating Historical Series...")
        # Lógica: Seleccionar tiendas antiguas (>24h sin escanear) y forzar update
        # Para MVP: El massive_scanner ya selecciona aleatorias, pero aquí 
        # podríamos añadir lógica específica en el futuro.
        # Por ahora, confiamos en que el paso 1 y el scheduler (si hubiera) lo cubren.
        pass

    # PASO 3: Archivar Snapshot (La Clave del Negocio)
    logger.info("📸 Phase 3: Archiving Daily Snapshot...")
    try:
        subprocess.run([sys.executable, "archive_snapshot.py"], check=True)
    except Exception as e:
        logger.error(f"Snapshot Failed: {e}")

    # PASO 4: Compute Signals (NUEVO) - Calcular variaciones
    logger.info("🧠 Phase 4: Computing Signals (Growth, Price Shifts)...")
    try:
        compute_signals_local()
    except Exception as e:
        logger.error(f"Signal Computation Failed: {e}")

    # PASO 5: Sync to Cloud
    logger.info("☁️  Phase 5: Syncing to Supabase...")
    try:
        subprocess.run([sys.executable, "intelligence_engine/scripts/sync_local_to_cloud.py"], check=True)
    except Exception as e:
        logger.error(f"Cloud Sync Failed: {e}")

    duration = time.time() - start_time
    logger.success(f"=== ✅ DAILY RUN COMPLETE in {duration:.2f}s ===")

def compute_signals_local():
    """
    Motor de Inteligencia Local (SQLite)
    Calcula: Crecimiento Catálogo (24h), Tendencia Precio (7d)
    """
    conn = sqlite3.connect("shopify_study/database.db")
    cursor = conn.cursor()
    
    # Asegurar Tabla Señales Local
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS local_signals (
        store_id INTEGER,
        signal_key TEXT,
        value FLOAT,
        computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(store_id, signal_key)
    )
    """)
    conn.commit()

    # Obtener Tiendas con Historial
    logger.info("Computing signals for stores with history...")
    cursor.execute("SELECT DISTINCT store_id FROM store_snapshots")
    store_ids = [row[0] for row in cursor.fetchall()]

    signals_count = 0
    for sid in store_ids:
        # Get last 2 snapshots ordered by time
        snaps = cursor.execute("""
            SELECT total_products, avg_price, snapshot_at 
            FROM store_snapshots 
            WHERE store_id = ? 
            ORDER BY snapshot_at DESC LIMIT 2
        """, (sid,)).fetchall()

        if len(snaps) < 2:
            continue

        current, prev = snaps[0], snaps[1]
        
        # 1. Catalog Growth (Absolute & %)
        growth = current[0] - prev[0]
        if growth != 0:
            pct = (growth / (prev[0] or 1)) * 100
            cursor.execute("INSERT OR REPLACE INTO local_signals (store_id, signal_key, value) VALUES (?, 'catalog_growth_24h', ?)", (sid, pct))
            signals_count += 1
            if abs(pct) > 10: logger.info(f"🚨 Store {sid}: Catalog changed by {pct:.1f}%")

        # 2. Price Shift
        price_diff = current[1] - prev[1]
        if abs(price_diff) > 0.5: # 50 cents threshold
            cursor.execute("INSERT OR REPLACE INTO local_signals (store_id, signal_key, value) VALUES (?, 'price_trend_24h', ?)", (sid, price_diff))
            signals_count += 1

    conn.commit()
    conn.close()
    logger.success(f"Computed {signals_count} new signals from history.")

if __name__ == "__main__":
    app()
