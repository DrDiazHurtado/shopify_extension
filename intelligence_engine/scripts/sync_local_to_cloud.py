# /home/noorm/Escritorio/SAAS_v2/sync_local_to_cloud.py
import sqlite3
import requests
import os
from loguru import logger
import pandas as pd

# Configuración Supabase
SUPABASE_URL = "https://cbffcvgecksspyhnqpqd.supabase.co"
SUPABASE_KEY = "sb_publishable_jwciMUPWBhpORNq5Ffk2Vw_WsNC3iId" 

import json

def sync_massive_intelligence():
    local_db = "/home/noorm/Escritorio/SAAS_v2/shopify_study/database.db"
    conn = sqlite3.connect(local_db)
    
    # 1. Cargamos tiendas y sus métricas
    query_stores = """
    SELECT s.id as local_id, s.domain, m.avg_price, m.hero_score, m.total_products, m.vendor_count, m.discount_ratio,
           m.currency, m.theme, m.social_links, m.pixels
    FROM stores s
    JOIN metrics m ON s.id = m.store_id
    """
    df_stores = pd.read_sql_query(query_stores, conn)
    
    if df_stores.empty:
        logger.error("Local database is empty!")
        return

    # 2. Para cada tienda, buscamos sus Top 5 productos
    logger.info(f"Syncing {len(df_stores)} stores with product details...")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    for _, row in df_stores.iterrows():
        # Obtener Top 5 productos (ordenados por precio desc como proxy de calidad/hero)
        query_products = f"SELECT name, price FROM products WHERE store_id = {row['local_id']} ORDER BY price DESC LIMIT 5"
        products = pd.read_sql_query(query_products, conn).to_dict('records')
        
        market_percentile = row['hero_score'] / 2.0 # Mock percentile logic simplified

        # Parse extra JSONs
        try:
            social = json.loads(row['social_links']) if row['social_links'] else {}
            pixels = json.loads(row['pixels']) if row['pixels'] else []
        except:
            social = {}
            pixels = []

        payload = {
            "domain": row['domain'],
            "avg_price": float(row['avg_price']),
            "hero_score": float(row['hero_score']),
            "total_products": int(row['total_products']),
            "discount_ratio": float(row['discount_ratio'] if not pd.isna(row['discount_ratio']) else 0),
            "category": "E-commerce Elite" if market_percentile > 0.8 else "Niche Player",
            "last_scanned": "2026-02-14",
            "payload": {
                "top_products": products,
                "currency": row['currency'],
                "theme": row['theme'],
                "social": social,
                "pixels": pixels
            } 
        }

        try:
            r = requests.post(f"{SUPABASE_URL}/rest/v1/stores?on_conflict=domain", json=payload, headers=headers)
            if r.status_code in [200, 201]:
                logger.success(f"Synced {row['domain']} with top products.")
            else:
                logger.error(f"Failed to sync {row['domain']}: {r.status_code} - {r.text}")
        except Exception as e:
            logger.error(f"Error syncing {row['domain']}: {e}")

    conn.close()

if __name__ == "__main__":
    sync_massive_intelligence()
