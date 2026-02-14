import sqlite3
import pandas as pd
from loguru import logger
import numpy as np

def audit_current_db():
    db_path = "shopify_study/database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 1. Total Stores and Products Distribution
        df_metrics = pd.read_sql_query("""
            SELECT m.total_products, m.avg_price, s.id 
            FROM metrics m JOIN stores s ON m.store_id = s.id
        """, conn)
        
        total_stores = len(df_metrics)
        if total_stores == 0:
            logger.error("No data in DB to audit.")
            return

        # Status simulated check (assuming all scraped are 'active' unless empty)
        # In real scenario we would check HTTP status field if it existed
        active_proxy = df_metrics[df_metrics['total_products'] > 0]
        active_pct = (len(active_proxy) / total_stores) * 100
        
        # Distributions
        p50_prod = df_metrics['total_products'].median()
        p90_prod = df_metrics['total_products'].quantile(0.9)
        p99_prod = df_metrics['total_products'].quantile(0.99)
        
        stores_over_10 = (len(df_metrics[df_metrics['total_products'] > 10]) / total_stores) * 100
        
        # Price Outliers
        p99_price = df_metrics['avg_price'].quantile(0.99)
        max_price = df_metrics['avg_price'].max()
        
        logger.info("=== RAPID DATA AUDIT ===")
        logger.info(f"Total Stores: {total_stores}")
        logger.info(f"Active Stores (>0 products): {active_pct:.2f}%")
        logger.info(f"Stores with >10 products: {stores_over_10:.2f}%")
        logger.info(f"Product Count Dist: p50={p50_prod}, p90={p90_prod}, p99={p99_prod}")
        logger.info(f"Price Outliers: p99={p99_price:.2f}, Max={max_price:.2f}")
        
        if p50_prod <= 1 or active_pct < 30:
            logger.warning("⚠️  CRITICAL: Data quality looks poor. Check scraper pagination or block detection.")
        else:
            logger.success("✅ Data quality looks healthy for scaling.")
            
    except Exception as e:
        logger.error(f"Audit failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    audit_current_db()
