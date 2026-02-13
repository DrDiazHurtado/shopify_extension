from bs4 import BeautifulSoup
from typing import List, Dict
from src.radar.utils.fetcher import Fetcher
from loguru import logger
import re
from urllib.parse import urljoin

class ChromeStoreConnector:
    def __init__(self, fetcher: Fetcher):
        self.fetcher = fetcher
        self.base_url = "https://chromewebstore.google.com/"

    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        # Note: The new Chrome Web Store might be harder to scrape without Javascript.
        # However, the user requested BS4/requests. 
        # I will use the old interface URL if possible or try to find a way to get data.
        # The new store is at chromewebstore.google.com
        url = f"https://chromewebstore.google.com/search/{keyword.replace(' ', '%20')}"
        content = self.fetcher.fetch(url)
        
        if not content:
            return []

        soup = BeautifulSoup(content, "lxml")
        candidates = []
        
        # This is a heuristic based on the current structure of the Chrome Web Store
        # We look for result items.
        # Note: The structure might change often.
        items = soup.find_all("a", href=re.compile(r"/detail/"))
        
        for item in items[:limit]:
            try:
                name_elem = item.find("h2") or item.find("div", string=True)
                name = name_elem.get_text(strip=True) if name_elem else "Unknown"
                href = item['href']
                if not href.startswith("http"):
                    href = urljoin(self.base_url, href)
                
                # Check if it's already in our list
                if any(c['url'] == href for c in candidates):
                    continue

                candidates.append({
                    "name": name,
                    "url": href,
                    "source": "chrome_store",
                    "keyword": keyword
                })
            except Exception as e:
                logger.error(f"Error parsing chrome store item: {e}")

        logger.info(f"Found {len(candidates)} candidates in Chrome Store for '{keyword}'")
        return candidates

    def get_details(self, url: str) -> Dict:
        content = self.fetcher.fetch(url)
        if not content:
            return {}

        soup = BeautifulSoup(content, "lxml")
        details = {}
        
        try:
            # Users count
            user_text = soup.find(string=re.compile(r"[\d,]+\+? users"))
            if user_text:
                users_match = re.search(r"([\d,]+)", user_text)
                if users_match:
                    details["users"] = int(users_match.group(1).replace(",", ""))
            
            # Rating and Reviews
            rating_elem = soup.find("div", {"aria-label": re.compile(r"Average rating")})
            if rating_elem:
                label = rating_elem["aria-label"]
                rating_match = re.search(r"Average rating ([\d.]+)", label)
                reviews_match = re.search(r"([\d,]+) ratings", label)
                if rating_match:
                    details["rating"] = float(rating_match.group(1))
                if reviews_match:
                    details["reviews_count"] = int(reviews_match.group(1).replace(",", ""))

            # Reviews snippets (only what's in the initial page)
            reviews = []
            review_elems = soup.find_all("div", string=True) # Very broad, might need refinement
            for r in review_elems:
                if len(r.get_text()) > 20 and any(kw in r.get_text().lower() for kw in ["bug", "expensive", "missing", "slow", "error"]):
                    reviews.append(r.get_text(strip=True))
            details["reviews"] = reviews[:10]

        except Exception as e:
            logger.error(f"Error extracting details from {url}: {e}")

        return details
