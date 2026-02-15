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
            # Sort products by date (desc) to get latest launch if possible
            # or by price. Let's assume input order is collection order (best selling)
            p = self.products[0]
            if not p: return None
            
            variants = p.get('variants', [{}])
            v = variants[0] if variants else {}
            price = float(v.get('price', 0)) if v.get('price') else 0
            
            return {'name': p.get('title'), 'price': price}
        return None

    def get_currency(self):
        if not self.soup: return "USD" 
        # Search for Shopify.currency = {"active":"EUR"...}
        script_text = self.soup.get_text()
        match = re.search(r'"currency":\s*"([A-Z]{3})"', script_text)
        if match: return match.group(1)
        
        # Fallback to symbol in content
        if "€" in script_text[:1000]: return "EUR"
        if "£" in script_text[:1000]: return "GBP"
        return "USD"

    def get_theme_name(self):
        if not self.soup: return "Unknown"
        # Search for Shopify.theme = {"name":"Dawn"...}
        html_str = str(self.soup)
        match = re.search(r'Shopify\.theme\s*=\s*{.*?name"\s*:\s*"([^"]+)"', html_str, re.DOTALL)
        if match: return match.group(1)
        
        # Fallback: check for common theme class names
        if 'class="gradient"' in html_str: return "Dawn (Generic)"
        return "Custom/Unknown"

    def get_social_links(self):
        if not self.soup: return {}
        links = {}
        for a in self.soup.find_all('a', href=True):
            href = a['href'].lower()
            if 'facebook.com' in href and 'sharer' not in href: links['facebook'] = href
            if 'instagram.com' in href: links['instagram'] = href
            if 'tiktok.com' in href: links['tiktok'] = href
            if 'pinterest.com' in href: links['pinterest'] = href
            if 'twitter.com' in href or 'x.com' in href: links['twitter'] = href
        return links

    def detect_pixels(self):
        if not self.soup: return []
        html_str = str(self.soup).lower()
        pixels = []
        
        # Meta Pixel
        if 'connect.facebook.net' in html_str or 'fbevents.js' in html_str:
            pixels.append("Facebook Pixel")
            
        # TikTok Pixel
        if 'analytics.tiktok.com' in html_str or 'ttq.load' in html_str:
            pixels.append("TikTok Pixel")
            
        # Google Analytics
        if 'googletagmanager.com' in html_str or 'gtag(' in html_str:
            pixels.append("Google Analytics")
        
        # Pinterest Tag
        if 'pinterest.com/ct.js' in html_str:
            pixels.append("Pinterest Tag")
            
        return pixels
