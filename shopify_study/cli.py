import typer
import yaml
from loguru import logger
from shopify_study.storage import init_db, get_session, Store, Product, Metric
from shopify_study.fetcher import Fetcher
from shopify_study.parsers import ShopifyParser
from shopify_study.metrics import MetricsCalculator
from shopify_study.aggregator import Aggregator
from shopify_study.reporting import Reporter
import os

app = typer.Typer()

def load_config():
    with open("shopify_study/config.yaml", "r") as f:
        return yaml.safe_load(f)

@app.command()
def init():
    """Initialize the database."""
    init_db()
    logger.success("Database initialized at shopify_study/database.db")

import json

@app.command()
def scan(urls: list[str] = None):
    """Scan Shopify stores from config or list."""
    config = load_config()
    target_urls = urls or config.get('urls', [])
    session = get_session()
    fetcher = Fetcher(config)

    for url in target_urls:
        # Check if already processed
        existing = session.query(Store).filter(Store.url == url).first()
        if existing:
            logger.info(f"Updating existing store: {url}")
            # Delete old metrics and products to refresh data
            session.query(Metric).filter(Metric.store_id == existing.id).delete()
            session.query(Product).filter(Product.store_id == existing.id).delete()
            session.delete(existing)
            session.commit()

        logger.info(f"Processing {url}...")
        
        # 1. Fetch Landing Page
        html = fetcher.fetch(url)
        if not html: continue
        
        # 2. Fetch Products JSON
        domain = url.split("//")[-1].split("/")[0]
        json_url = f"{url.rstrip('/')}/products.json?limit=250"
        json_data = fetcher.fetch_json(json_url)
        
        if not json_data:
            logger.error(f"Failed to fetch products for {url}")
            continue

        parser = ShopifyParser(html, json_data)
        
        # 3. Storage
        store = Store(url=url, domain=domain)
        session.add(store)
        session.commit()
        
        products_data = parser.get_product_metrics()
        for p in products_data:
            session.add(Product(
                store_id=store.id, 
                name=p['name'], 
                price=p['price'], 
                compare_at_price=p['compare_at_price'],
                variants_count=p['variants_count'],
                product_type=p['product_type'],
                vendor=p['vendor'],
                created_at=p['created_at'],
                tags=p['tags']
            ))
        
        # 4. Metrics
        hero = parser.get_hero_product()
        urgency = parser.detect_urgency()
        bundle = parser.detect_bundles()
        
        # New Extractions
        currency = parser.get_currency()
        theme = parser.get_theme_name()
        social = parser.get_social_links()
        pixels = parser.detect_pixels()
        
        calc_metrics = MetricsCalculator.calculate_store_metrics(
            products_data, hero, urgency, bundle
        )
        
        if calc_metrics:
            session.add(Metric(
                store_id=store.id,
                hero_score=calc_metrics['hero_score'],
                discount_ratio=calc_metrics['discount_ratio'],
                avg_variants=calc_metrics['avg_variants'],
                urgency=calc_metrics['urgency'],
                bundle=calc_metrics['bundle'],
                total_products=calc_metrics['total_products'],
                avg_price=calc_metrics['avg_price'],
                inventory_recency_days=calc_metrics['inventory_recency_days'],
                vendor_count=calc_metrics['vendor_count'],
                currency=currency,
                theme=theme,
                social_links=json.dumps(social),
                pixels=json.dumps(pixels)
            ))
            session.commit()
            logger.success(f"Stored metrics for {domain}")

@app.command()
def report():
    """Analyze data and generate HTML report."""
    session = get_session()
    agg = Aggregator(session)
    stats_result = agg.get_global_stats()
    
    if not stats_result:
        logger.error("No data found to generate report. Run 'scan' first.")
        return

    stats, df = stats_result
    insights = agg.generate_insights(stats)
    
    rep_path = Reporter.generate_html(stats, df, insights)
    logger.success(f"Report generated at {rep_path}")

@app.command()
def run_all():
    """Clean run of init, scan and report."""
    init()
    scan()
    report()

if __name__ == "__main__":
    app()
