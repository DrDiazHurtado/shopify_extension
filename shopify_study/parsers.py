from bs4 import BeautifulSoup
import re
from datetime import datetime

class ShopifyParser:
    def __init__(self, html_content=None, json_products=None):
        self.soup = BeautifulSoup(html_content, 'lxml') if html_content else None
        self.products = json_products.get('products', []) if json_products else []

    def get_product_metrics(self):
        extracted = []
        for p in self.products:
            variants = p.get('variants', [{}])
            v = variants[0]
            
            # Parse prices handle cases like Null
            price = float(v.get('price', 0)) if v.get('price') else 0
            compare_at = float(v.get('compare_at_price', 0)) if v.get('compare_at_price') else 0
            
            # Parse date
            created_str = p.get('created_at', '')
            try:
                # Format: 2024-02-12T10:00:00-05:00
                dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            except:
                dt = datetime.utcnow()

            extracted.append({
                'name': p.get('title'),
                'price': price,
                'compare_at_price': compare_at,
                'variants_count': len(variants),
                'product_type': p.get('product_type', 'Default'),
                'vendor': p.get('vendor', 'Unknown'),
                'created_at': dt,
                'tags': ",".join(p.get('tags', [])) if isinstance(p.get('tags'), list) else p.get('tags', '')
            })
        return extracted

    def detect_urgency(self):
        if not self.soup: return 0
        keywords = ['limited edition', 'only a few left', 'selling fast', 'hurry', 'seconds', 'countdown', 'ends soon']
        text = self.soup.get_text().lower()
        return 1 if any(kw in text for kw in keywords) else 0

    def detect_bundles(self):
        if not self.soup: return 0
        keywords = ['bundle', 'save on set', 'pack overlap', 'gift set', 'value pack', 'buy the set']
        text = self.soup.get_text().lower()
        return 1 if any(kw in text for kw in keywords) else 0

    def get_hero_product(self):
        if self.products:
            p = self.products[0]
            v = p.get('variants', [{}])[0]
            price = float(v.get('price', 0)) if v.get('price') else 0
            return {'name': p.get('title'), 'price': price}
        return None
