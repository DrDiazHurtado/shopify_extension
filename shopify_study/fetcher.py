import requests
import time
import os
import hashlib
from loguru import logger

class Fetcher:
    def __init__(self, config):
        self.config = config['crawler']
        self.cache_dir = self.config.get('cache_dir', '.html_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.headers = {'User-Agent': self.config['user_agent']}

    def fetch(self, url, use_cache=True):
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{url_hash}.html")

        if use_cache and os.path.exists(cache_path):
            logger.debug(f"Cache hit for {url}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()

        logger.info(f"Fetching: {url}")
        try:
            time.sleep(self.config['rate_limit_seconds'])
            response = requests.get(url, headers=self.headers, timeout=self.config['timeout_seconds'])
            response.raise_for_status()
            
            content = response.text
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return content
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def fetch_json(self, url):
        logger.info(f"Fetching JSON: {url}")
        try:
            time.sleep(self.config['rate_limit_seconds'])
            response = requests.get(url, headers=self.headers, timeout=self.config['timeout_seconds'])
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching JSON {url}: {e}")
            return None
