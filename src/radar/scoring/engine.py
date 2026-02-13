import math
from typing import Dict, List
from src.radar.storage.models import Signal
from loguru import logger

class ScoringEngine:
    def __init__(self, config: dict):
        self.weights = config.get("scoring_weights", {})

    def calculate_candidate_score(self, signals: List[Signal]) -> Dict:
        signal_map = {s.signal_name: s.value_numeric for s in signals}
        
        # Money Score
        w_money = self.weights.get("money", {})
        money_score = (
            w_money.get("has_pricing_page", 5) * signal_map.get("has_pricing_page", 0) +
            w_money.get("mentions_monthly_price", 3) * signal_map.get("mentions_monthly_price", 0) +
            w_money.get("has_annual_plan", 2) * signal_map.get("has_annual_plan", 0) +
            w_money.get("has_checkout_keywords", 4) * signal_map.get("has_checkout_keywords", 0) +
            w_money.get("has_payment_tech", 5) * signal_map.get("has_payment_tech", 0)
        )

        # Demand Score
        w_demand = self.weights.get("demand", {})
        chrome_users = signal_map.get("chrome_users", 0)
        demand_score = (
            w_demand.get("chrome_users_log_weight", 1) * math.log10(1 + chrome_users) +
            w_demand.get("suggest_count_weight", 0.5) * signal_map.get("suggest_count", 0) +
            w_demand.get("reviews_count_weight", 0.2) * signal_map.get("reviews_count", 0)
        )

        # Competition Score (Higher is worse for total score, so we use it as divisor or subtract)
        w_comp = self.weights.get("competition", {})
        comp_count = signal_map.get("chrome_competitors_count", 0)
        competition_score = 1 + w_comp.get("chrome_competitors_count_weight", 1) * comp_count

        # Pain Score
        w_pain = self.weights.get("pain", {})
        pain_score = (
            w_pain.get("negative_review_ratio_weight", 10) * signal_map.get("negative_review_ratio", 0) +
            w_pain.get("pain_keyword_count_weight", 2) * signal_map.get("pain_keyword_count", 0) +
            w_pain.get("pain_rating_weight", 5) * signal_map.get("pain_rating_factor", 0)
        )

        # Total Score
        total_score = (money_score * demand_score * (1 + pain_score)) / competition_score

        # Explanation
        # Get top 5 signals by (weight * value)
        contributions = []
        # This is a simplified attribution
        contributions.append(("Money Indicators", money_score))
        contributions.append(("Demand Signals", demand_score))
        contributions.append(("Competition Penalty", competition_score))
        contributions.append(("Pain Signals", pain_score))
        
        explanation = ", ".join([f"{k}: {v:.2f}" for k, v in contributions])

        return {
            "money_score": money_score,
            "demand_score": demand_score,
            "competition_score": competition_score,
            "pain_score": pain_score,
            "total_score": total_score,
            "explanation": explanation
        }
