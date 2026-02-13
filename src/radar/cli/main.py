import typer
from typing import List, Optional
from loguru import logger
from src.radar.utils.config import load_config
from src.radar.utils.logger import setup_logging
from src.radar.utils.fetcher import Fetcher
from src.radar.storage.db import init_db, get_session
from src.radar.storage.models import Candidate, Signal, Score
from src.radar.connectors.google_suggest import GoogleSuggestConnector
from src.radar.connectors.chrome_store import ChromeStoreConnector
from src.radar.extractors.landing_page import LandingPageExtractor
from src.radar.scoring.engine import ScoringEngine
from src.radar.reporting.generator import ReportGenerator
from urllib.parse import urlparse
import json

app = typer.Typer(help="Opportunity Radar CLI")

@app.command()
def init_db_cmd(config_path: str = "config.yaml"):
    """Initialize the database."""
    config = load_config(config_path)
    init_db(config["database"]["url"])
    logger.info("Database initialized.")

@app.command()
def crawl(config_path: str = "config.yaml", limit: int = 10):
    """Crawl Google Suggest and Chrome Web Store for candidates."""
    config = load_config(config_path)
    fetcher = Fetcher(config)
    suggest_conn = GoogleSuggestConnector(fetcher)
    chrome_conn = ChromeStoreConnector(fetcher)
    
    engine = init_db(config["database"]["url"])
    session = get_session(engine)
    
    seeds = config.get("seeds", [])
    for seed in seeds:
        logger.info(f"Processing seed: {seed}")
        # 1. Google Suggest
        suggestions = suggest_conn.get_suggestions(seed)
        
        # 2. Chrome Store for each suggestion + seed
        all_keywords = suggestions + [seed]
        for kw in all_keywords:
            chrome_candidates = chrome_conn.search(kw, limit=limit)
            
            for c in chrome_candidates:
                # Store candidate if doesn't exist
                exists = session.query(Candidate).filter_by(url=c['url']).first()
                if not exists:
                    candidate = Candidate(
                        source=c['source'],
                        keyword=kw,
                        product_name=c['name'],
                        url=c['url'],
                        domain=urlparse(c['url']).netloc
                    )
                    session.add(candidate)
                    session.commit()
    
    logger.info("Crawl complete.")

@app.command()
def extract(config_path: str = "config.yaml"):
    """Extract signals from candidates."""
    config = load_config(config_path)
    fetcher = Fetcher(config)
    chrome_conn = ChromeStoreConnector(fetcher)
    landing_extractor = LandingPageExtractor(fetcher)
    
    engine = init_db(config["database"]["url"])
    session = get_session(engine)
    
    candidates = session.query(Candidate).all()
    for c in candidates:
        logger.info(f"Extracting signals for: {c.product_name}")
        
        url_to_extract = None

        # Chrome details
        if "chromewebstore" in c.url:
            details = chrome_conn.get_details(c.url)
            
            # Store signals
            if "users" in details:
                session.add(Signal(candidate_id=c.id, signal_name="chrome_users", value_numeric=float(details["users"]), evidence_url=c.url))
            if "reviews_count" in details:
                session.add(Signal(candidate_id=c.id, signal_name="reviews_count", value_numeric=float(details["reviews_count"]), evidence_url=c.url))
            if "rating" in details:
                session.add(Signal(candidate_id=c.id, signal_name="rating", value_numeric=details["rating"], evidence_url=c.url))
            
            # Pain signals from reviews
            if "reviews" in details and details["reviews"]:
                pain_words = ["bug", "expensive", "slow", "missing", "error", "bad", "worst", "broken", "scam", "ads", "subscription", "limit"]
                pain_snippets = []
                for r in details["reviews"]:
                    if any(pw in r.lower() for pw in pain_words):
                        pain_snippets.append(r)
                
                session.add(Signal(
                    candidate_id=c.id, 
                    signal_name="pain_keyword_count", 
                    value_numeric=float(len(pain_snippets)),
                    evidence_snippet=json.dumps(pain_snippets)
                ))

            # Rating as pain factor (lower is more pain/opportunity for fix)
            if "rating" in details and details["rating"] > 0:
                # Normalizing: a 1.0 rating is "high pain", 5.0 is "low pain"
                pain_from_rating = max(0, 5.0 - details["rating"])
                session.add(Signal(
                    candidate_id=c.id, 
                    signal_name="pain_rating_factor", 
                    value_numeric=pain_from_rating,
                    evidence_url=c.url
                ))
            
            # Simple heuristic: try to find a domain from product name or just skip landing for now
            # In a full version, we would scrape the homepage link from the Chrome Store page
        
        # If the candidate is already a non-store URL, extract landing signals
        if "chromewebstore" not in c.url:
            url_to_extract = c.url

        if url_to_extract:
            lsignals = landing_extractor.extract_signals(url_to_extract)
            for name, val in lsignals.items():
                if isinstance(val, (int, float)):
                    session.add(Signal(candidate_id=c.id, signal_name=name, value_numeric=float(val), evidence_url=url_to_extract))
                elif isinstance(val, list) and name == "detected_tech":
                    session.add(Signal(candidate_id=c.id, signal_name="has_payment_tech", value_numeric=1.0 if any(t in val for t in ["stripe", "paddle"]) else 0.0, evidence_url=url_to_extract))
        
        session.commit()
    logger.info("Extraction complete.")

@app.command()
def score(config_path: str = "config.yaml"):
    """Calculate scores for all candidates."""
    config = load_config(config_path)
    engine = init_db(config["database"]["url"])
    session = get_session(engine)
    
    scoring_engine = ScoringEngine(config)
    
    candidates = session.query(Candidate).all()
    for c in candidates:
        signals = session.query(Signal).filter_by(candidate_id=c.id).all()
        result = scoring_engine.calculate_candidate_score(signals)
        
        score_obj = session.query(Score).filter_by(candidate_id=c.id).first()
        if not score_obj:
            score_obj = Score(candidate_id=c.id)
            session.add(score_obj)
        
        score_obj.money_score = result["money_score"]
        score_obj.demand_score = result["demand_score"]
        score_obj.competition_score = result["competition_score"]
        score_obj.pain_score = result["pain_score"]
        score_obj.total_score = result["total_score"]
        score_obj.explanation = result["explanation"]
        
        session.commit()
    logger.info("Scoring complete.")

@app.command()
def report(config_path: str = "config.yaml"):
    """Generate reports."""
    config = load_config(config_path)
    engine = init_db(config["database"]["url"])
    session = get_session(engine)
    
    candidates = session.query(Candidate).all()
    report_data = []
    
    for c in candidates:
        if not c.scores:
            continue
            
        signals = {s.signal_name: s.value_numeric for s in c.signals}
        
        tags = []
        if signals.get("chrome_users", 0) > 10000: tags.append("popular")
        if signals.get("pain_keyword_count", 0) >= 1: tags.append("pain points")
        
        # Get snippets
        snippets = []
        pain_signal = session.query(Signal).filter_by(candidate_id=c.id, signal_name="pain_keyword_count").first()
        if pain_signal and pain_signal.evidence_snippet:
            try:
                snippets = json.loads(pain_signal.evidence_snippet)[:5] # Limit to 5
            except:
                pass

        item = {
            "id": c.id,
            "product_name": c.product_name,
            "keyword": c.keyword,
            "source": c.source,
            "url": c.url,
            "domain": c.domain,
            "money_score": c.scores.money_score,
            "demand_score": c.scores.demand_score,
            "competition_score": c.scores.competition_score,
            "pain_score": c.scores.pain_score,
            "total_score": c.scores.total_score,
            "tags": tags,
            "snippets": snippets
        }
        report_data.append(item)
    
    generator = ReportGenerator(config)
    generator.generate(report_data)
    logger.info("Reporting complete.")

if __name__ == "__main__":
    setup_logging()
    app()
