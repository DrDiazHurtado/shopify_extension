# /home/noorm/Escritorio/SAAS_v2/auto_pulse.py
import subprocess
import time
import sys
from loguru import logger

def run_shopify_scan():
    logger.info("Running SHOPIFY Database Pulse...")
    try:
        # Ejecuta el escáner masivo de tiendas (150 tiendas aleatorias del CSV)
        subprocess.run([sys.executable, "-m", "shopify_study.massive_scanner"], check=True)
        # Sincroniza local -> nube (Supabase)
        subprocess.run([sys.executable, "intelligence_engine/scripts/sync_local_to_cloud.py"], check=True)
        logger.success("SHOPIFY pulse complete.")
    except Exception as e:
        logger.error(f"SHOPIFY pulse failed: {e}")

def run_saas_radar_crawl():
    logger.info("Running SAAS RADAR Database Pulse...")
    try:
        # Crawl: Busca nuevas oportunidades en Chrome Store y Google Suggest
        subprocess.run([sys.executable, "-m", "src.radar.cli.main", "crawl"], check=True)
        # Extract: Saca señales (usuarios, pain points, tech)
        subprocess.run([sys.executable, "-m", "src.radar.cli.main", "extract"], check=True)
        # Score: Calcula las puntuaciones de negocio
        subprocess.run([sys.executable, "-m", "src.radar.cli.main", "score"], check=True)
        logger.success("SAAS RADAR pulse complete.")
    except Exception as e:
        logger.error(f"SAAS RADAR pulse failed: {e}")

def check_db_status():
    try:
        # Check Local DB
        conn = sqlite3.connect("shopify_study/database.db")
        local_count = conn.execute("SELECT count(*) FROM stores").fetchone()[0]
        conn.close()
        
        # Check Cloud DB (Supabase)
        headers = {
            "apikey": "sb_publishable_jwciMUPWBhpORNq5Ffk2Vw_WsNC3iId", 
            "Authorization": "Bearer sb_publishable_jwciMUPWBhpORNq5Ffk2Vw_WsNC3iId",
            "Prefer": "count=exact",
            "Range": "0-0"
        }
        r = requests.get("https://cbffcvgecksspyhnqpqd.supabase.co/rest/v1/stores?select=*", headers=headers)
        cloud_count = int(r.headers.get('content-range', '0/0').split('/')[1])
        
        logger.info(f"📊 LIVE STATUS: Local DB: {local_count} stores | Cloud Radar: {cloud_count} stores")
        return local_count, cloud_count
    except Exception as e:
        logger.warning(f"Could not check DB status: {e}")
        return 0, 0

if __name__ == "__main__":
    logger.info("=== AUTO-PULSE SYSTEM INITIALIZED ===")
    logger.info("Dual Database Expansion Mode: Shopify Stores & SaaS Opportunities")
    
    import sqlite3
    import requests
    import threading

    while True:
        # 0. Verificar Estado de Sincronización
        check_db_status()

        # Usar hilos para que un proceso lento (Shopify) no bloquee al otro (SaaS Radar)
        t1 = threading.Thread(target=run_shopify_scan)
        t2 = threading.Thread(target=run_saas_radar_crawl)

        logger.info("🚀 Launching parallel expansion tasks...")
        t1.start()
        t2.start()

        # Esperar a que ambos terminen
        t1.join()
        t2.join()
        
        logger.success("✅ All expansion tasks finished. Waiting 1 hour for next wave...")
        time.sleep(3600)  # Ciclo cada hora para expansión continua
