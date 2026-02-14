# /home/noorm/Escritorio/SAAS_v2/intelligence_engine/scripts/backup_cloud_to_local.py
import sqlite3
import requests
from loguru import logger
import os

# Configuración Supabase (Read Only from Client Key is enough if RLS allows or use Service Key)
SUPABASE_URL = "https://cbffcvgecksspyhnqpqd.supabase.co"
SUPABASE_KEY = "sb_publishable_jwciMUPWBhpORNq5Ffk2Vw_WsNC3iId" # Usamos la key pública para backup de lectura si está permitido, o la service key si es privada.

def backup_licenses():
    local_db = "/home/noorm/Escritorio/SAAS_v2/intelligence_engine/databases/licenses_backup.db"
    
    # Asegurar que el folder existe
    os.makedirs(os.path.dirname(local_db), exist_ok=True)
    
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()
    
    # Crear tabla local si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        id TEXT PRIMARY KEY,
        license_key TEXT,
        email TEXT,
        is_active BOOLEAN,
        plan_type TEXT,
        created_at TEXT
    )
    """)
    
    logger.info("Fetching licenses from Supabase...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/licenses", headers=headers)
        if r.status_code == 200:
            licenses = r.json()
            logger.info(f"Found {len(licenses)} licenses in cloud.")
            
            for lic in licenses:
                cursor.execute("""
                INSERT OR REPLACE INTO licenses (id, license_key, email, is_active, plan_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (lic['id'], lic['license_key'], lic['email'], lic['is_active'], lic['plan_type'], lic['created_at']))
            
            conn.commit()
            logger.success(f"Backup complete! Local database updated: {local_db}")
        else:
            logger.error(f"Failed to fetch licenses: {r.status_code} - {r.text}")
            
    except Exception as e:
        logger.error(f"Error during backup: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    backup_licenses()
