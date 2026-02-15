from shopify_study.cli import scan
from shopify_study.storage import get_session, Metric, Store
import json

def test_scan():
    # Test with a known store
    url = "https://colourpop.com"
    print(f"Scanning {url}...")
    
    # Clean previous record if exists for test
    session = get_session()
    store = session.query(Store).filter_by(url=url).first()
    if store:
        session.query(Metric).filter_by(store_id=store.id).delete()
        session.delete(store)
        session.commit()
    
    try:
        scan(urls=[url])
        
        # Check result
        store = session.query(Store).filter_by(url=url).first()
        metric = session.query(Metric).filter_by(store_id=store.id).first()
        
        print("\n--- NEW METRICS EXTRACTED ---")
        print(f"Currency: {metric.currency}")
        print(f"Theme: {metric.theme}")
        print(f"Social Links: {metric.social_links}")
        print(f"Pixels: {metric.pixels}")
        
    except Exception as e:
        print(f"Scan failed: {e}")

if __name__ == "__main__":
    test_scan()
