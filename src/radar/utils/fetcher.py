import httpx
import time
import hashlib
from pathlib import Path
from loguru import logger
from typing import Optional

class Fetcher:
    def __init__(self, config: dict):
        self.config = config.get("crawler", {})
        self.user_agent = self.config.get("user_agent", "RadarBot/1.0")
        self.rate_limit = self.config.get("rate_limit_seconds", 1.0)
        self.timeout = self.config.get("timeout_seconds", 10)
        self.retries = self.config.get("retries", 3)
        self.cache_dir = Path(self.config.get("cache_dir", ".cache"))
        self.cache_dir.mkdir(exist_ok=True)
        self.last_request_time = 0

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.html"

    def fetch(self, url: str, use_cache: bool = True) -> Optional[str]:
        if use_cache:
            cache_path = self._get_cache_path(url)
            if cache_path.exists():
                logger.debug(f"Cache hit: {url}")
                return cache_path.read_text()

        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

        headers = {"User-Agent": self.user_agent}
        
        for i in range(self.retries):
            try:
                logger.info(f"Fetching: {url}")
                response = httpx.get(url, headers=headers, timeout=self.timeout, follow_redirects=True)
                self.last_request_time = time.time()
                
                if response.status_code == 200:
                    content = response.text
                    if use_cache:
                        self._get_cache_path(url).write_text(content)
                    return content
                else:
                    logger.warning(f"Failed to fetch {url}: Status {response.status_code}")
                    if response.status_code == 429:
                        time.sleep(self.rate_limit * (i + 1) * 2) # Backoff
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                time.sleep(1)

        return None
