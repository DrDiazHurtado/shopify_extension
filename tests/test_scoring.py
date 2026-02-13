from src.radar.scoring.engine import ScoringEngine
from src.radar.storage.models import Signal

def test_scoring_basic():
    config = {
        "scoring_weights": {
            "money": {"has_pricing_page": 5},
            "demand": {"chrome_users_log_weight": 1},
            "competition": {"chrome_competitors_count_weight": 1},
            "pain": {"negative_review_ratio_weight": 10}
        }
    }
    engine = ScoringEngine(config)
    
    signals = [
        Signal(signal_name="has_pricing_page", value_numeric=1.0),
        Signal(signal_name="chrome_users", value_numeric=100.0), # log10(101) ~ 2
        Signal(signal_name="chrome_competitors_count", value_numeric=1.0) # 1 + 1 = 2
    ]
    
    result = engine.calculate_candidate_score(signals)
    
    assert result["money_score"] == 5.0
    assert result["demand_score"] > 1.9 and result["demand_score"] < 2.1
    assert result["competition_score"] == 2.0
    # total = (5 * 2 * 1) / 2 = 5
    assert result["total_score"] > 4.9 and result["total_score"] < 5.1
