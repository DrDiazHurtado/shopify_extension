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
        # H2-centric approach (More robust for modern Grid Layouts)
        # We assume the visual Title is an H2 (as confirmed by markdown conversions)
        h2s = soup.find_all("h2")
        
        candidates_list = []
        seen_urls = set()

        for h2 in h2s:
            if len(candidates_list) >= limit:
                break

            name = h2.get_text(strip=True)
            if not name: continue

            # Find the link associated with this H2
            # Case 1: H2 is inside <a>
            link = h2.find_parent("a", href=re.compile(r"/detail/"))
            
            # Case 2: H2 is next to <a> or in same container
            if not link:
                # Walk up tree to find a container that has the link
                # Try 3 levels up
                parent = h2.parent
                for _ in range(3):
                    if not parent: break
                    link = parent.find("a", href=re.compile(r"/detail/"))
                    if link: break
                    parent = parent.parent
            
            if not link:
                continue

            href = link.get('href', '')
            # Clean URL
            if '?' in href:
                href = href.split('?')[0]
                
            full_url = urljoin("https://chromewebstore.google.com", href)
            
            if full_url in seen_urls:
                continue

            seen_urls.add(full_url)
            candidates_list.append({
                "name": name,
                "url": full_url,
                "source": "chrome_store",
                "keyword": keyword
            })
            
        return candidates_list

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
