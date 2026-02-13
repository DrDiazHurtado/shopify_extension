from bs4 import BeautifulSoup
from typing import Dict, List
import re
from loguru import logger
from urllib.parse import urlparse

class LandingPageExtractor:
    def __init__(self, fetcher):
        self.fetcher = fetcher
        self.pricing_keywords = ["pricing", "plans", "annual", "month", "trial", "stripe", "checkout", "billing", "subscribe"]
        self.tech_signatures = {
            "stripe": [r"js.stripe.com", r"stripe-checkout"],
            "paddle": [r"paddle.com/checkout", r"cdn.paddle.com"],
            "intercom": [r"widget.intercom.io", r"intercom-settings"],
            "crisp": [r"client.crisp.chat"],
            "segment": [r"cdn.segment.com"],
            "google_analytics": [r"google-analytics.com", r"googletagmanager.com"]
        }

    def extract_signals(self, url: str) -> Dict:
        if not url or not url.startswith("http"):
            return {}

        content = self.fetcher.fetch(url)
        if not content:
            return {}

        soup = BeautifulSoup(content, "lxml")
        page_text = soup.get_text().lower()
        scripts = [s.get("src", "") for s in soup.find_all("script") if s.get("src")]
        
        signals = {
            "has_pricing_page": 0,
            "mentions_monthly_price": 0,
            "has_annual_plan": 0,
            "has_checkout_keywords": 0,
            "detected_tech": [],
            "extracted_price_min": None
        }

        # Check links for pricing
        for link in soup.find_all("a", href=True):
            href = link["href"].lower()
            if any(k in href for k in ["pricing", "plans", "billing"]):
                signals["has_pricing_page"] = 1
                break

        # Check text for keywords
        if any(k in page_text for k in ["monthly", "/mo", "per month"]):
            signals["mentions_monthly_price"] = 1
        
        if any(k in page_text for k in ["annual", "yearly", "/yr"]):
            signals["has_annual_plan"] = 1

        if any(k in page_text for k in ["checkout", "stripe", "paddle", "billing", "secure payment"]):
            signals["has_checkout_keywords"] = 1

        # Detect technologies from scripts
        for tech, patterns in self.tech_signatures.items():
            for pattern in patterns:
                if any(re.search(pattern, s) for s in scripts):
                    signals["detected_tech"].append(tech)
                    break

        # Simple price extraction heuristic
        price_matches = re.findall(r"\$\s?(\d+)", page_text)
        if price_matches:
            prices = [float(p) for p in price_matches if float(p) > 0 and float(p) < 1000]
            if prices:
                signals["extracted_price_min"] = min(prices)

        return signals
