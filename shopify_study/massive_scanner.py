# /home/noorm/Escritorio/SAAS_v2/shopify_study/massive_scanner.py
import pandas as pd
from shopify_study.cli import app
import typer
from loguru import logger
import subprocess

def scan_batch(limit=100):
    # Leer el CSV masivo
    df = pd.read_csv("shopify_study/shopifystores_massive.csv", header=None, names=['domain'])
    
    # Limpiar dominios
    domains = df['domain'].dropna().unique().tolist()
    
    # Escoger una muestra aleatoria para no saturar
    import random
    selected = random.sample(domains, min(limit, len(domains)))
    
    urls = [f"https://{d}" if not d.startswith('http') else d for d in selected]
    
    logger.info(f"Starting massive scan of {len(urls)} stores...")
    
    # Usar el comando 'scan' ya existente en cli.py
    from shopify_study.cli import scan
    scan(urls=urls)

if __name__ == "__main__":
    scan_batch(limit=150) # Vamos a por 150 para empezar
