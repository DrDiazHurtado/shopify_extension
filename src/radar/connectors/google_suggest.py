import json
import xml.etree.ElementTree as ET
from typing import List
from src.radar.utils.fetcher import Fetcher
from loguru import logger

class GoogleSuggestConnector:
    def __init__(self, fetcher: Fetcher):
        self.fetcher = fetcher
        self.base_url = "http://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q="

    def get_suggestions(self, seed: str) -> List[str]:
        url = self.base_url + seed.replace(" ", "+")
        content = self.fetcher.fetch(url)
        
        if not content:
            return []

        try:
            root = ET.fromstring(content)
            suggestions = [complete.get("data") for complete in root.findall(".//suggestion") if complete.get("data")]
            logger.info(f"Found {len(suggestions)} suggestions for '{seed}'")
            return suggestions
        except Exception as e:
            logger.error(f"Error parsing Google Suggest XML: {e}")
            return []
