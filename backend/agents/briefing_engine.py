"""
briefing_engine.py - Genererar morgon- och kvällsbriefingar

Morgon (08:15 CET): Analys inför börsöppning, fokus på köpmöjligheter
Kväll (17:15 CET): Analys inför börsstängning, fokus på riskhantering
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import json

from .research_agent import ResearchAgent


class BriefingEngine:
    """Genererar strukturerade morgon- och kvällsbriefingar."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "config" / "config.json")
        self.config_path = config_path
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def _get_agent(self) -> ResearchAgent:
        return ResearchAgent(self.config_path)

    def _classify_recommendation(self, score: int, briefing_type: str) -> tuple:
        """Classify signal score into action and confidence."""
        if briefing_type == "morning":
            if score >= 2:
                return "BUY", "HIGH"
            elif score == 1:
                return "WATCH", "MEDIUM"
            elif score == 0:
                return "HOLD", "LOW"
            elif score == -1:
                return "WATCH", "MEDIUM"
            else:
                return "AVOID", "HIGH"
        else:  # evening
            if score >= 2:
                return "HOLD", "HIGH"
            elif score == 1:
                return "HOLD", "MEDIUM"
            elif score == 0:
                return "HOLD", "LOW"
            elif score == -1:
                return "WATCH", "MEDIUM"
            else:
                return "SELL", "HIGH"

    def _get_market_status(self) -> str:
        """Determine current market status based on Stockholm time."""
        now = datetime.now()
        hour = now.hour
        if hour < 9:
            return "pre_open"
        elif hour < 17 or (hour == 17 and now.minute < 30):
            return "open"
        else:
            return "closed"

    def _build_summary(self, analyses: list, briefing_type: str) -> str:
        """Build a human-readable summary."""
        positive = sum(1 for a in analyses if a["signal"]["score"] > 0)
        negative = sum(1 for a in analyses if a["signal"]["score"] < 0)
        neutral = len(analyses) - positive - negative

        date_str = datetime.now().strftime("%Y-%m-%d")

        if briefing_type == "morning":
            return (
                f"Morgonbrief {date_str}. "
                f"Av {len(analyses)} bevakade aktier visar "
                f"{positive} positiva signaler, "
                f"{negative} negativa och "
                f"{neutral} neutrala. "
                f"Analysen baseras på kursdata, nyhetssentiment och kongressaktivitet."
            )
        else:
            return (
                f"Kvällsbrief {date_str}. "
                f"Dagens handel visar "
                f"{positive} aktier med positiv utveckling, "
                f"{negative} med negativ och "
                f"{neutral} utan tydlig riktning. "
                f"Nedan följer rekommendationer inför morgondagen."
            )

    def generate_briefing(self, briefing_type: str = "morning") -> dict:
        """
        Generate a briefing.

        Args:
            briefing_type: "morning" or "evening"

        Returns:
            Complete briefing dict
        """
        agent = self._get_agent()
        watchlist = self.config.get("watchlist", [])

        # Analyze all stocks
        analyses = []
        for stock in watchlist:
            try:
                analysis = agent.analyze_stock(stock["symbol"], stock["name"])
                analyses.append(analysis)
            except Exception as e:
                analyses.append({
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "stock_data": {"error": str(e)},
                    "signal": {"type": "NEUTRAL", "score": 0, "reasons": [f"Fel: {e}"]},
                    "news_summary": {"sentiment": "no_data", "count": 0, "score": 0},
                    "congress_activity": {},
                    "unusual_activity": [],
                    "recent_headlines": [],
                })

        # Separate Swedish and US stocks
        swedish = [a for a in analyses if a["symbol"].endswith(".ST")]
        us = [a for a in analyses if not a["symbol"].endswith(".ST")]

        # Sort by signal score
        if briefing_type == "morning":
            swedish.sort(key=lambda x: x["signal"]["score"], reverse=True)
            us.sort(key=lambda x: x["signal"]["score"], reverse=True)
        else:
            swedish.sort(key=lambda x: x["signal"]["score"])
            us.sort(key=lambda x: x["signal"]["score"])

        all_sorted = swedish + us

        # Build recommendations
        recommendations = []
        for a in all_sorted:
            score = a["signal"]["score"]
            action, confidence = self._classify_recommendation(score, briefing_type)

            recommendations.append({
                "symbol": a["symbol"],
                "name": a["name"],
                "action": action,
                "confidence": confidence,
                "price": a["stock_data"].get("current_price", 0),
                "change_percent": a["stock_data"].get("change_percent", 0),
                "reasons": a["signal"]["reasons"],
                "news_sentiment": a.get("news_summary", {}).get("sentiment", "neutral"),
                "congress_signal": a.get("congress_activity", {}).get("sentiment"),
            })

        # Extract highlights
        highlights = []
        for a in all_sorted:
            if a["signal"]["type"] != "NEUTRAL ➖":
                highlights.append({
                    "stock": a["name"],
                    "signal": a["signal"]["type"],
                    "reasons": a["signal"]["reasons"],
                })
            for flag in a.get("unusual_activity", []):
                highlights.append({
                    "stock": a["name"],
                    "alert": flag,
                })

        # Get notable congress activity
        congress_notable = []
        for a in all_sorted:
            ca = a.get("congress_activity", {})
            if ca.get("has_congress_activity"):
                congress_notable.append({
                    "ticker": ca.get("ticker", a["symbol"]),
                    "sentiment": ca.get("sentiment", ""),
                    "description": ca.get("sentiment_description", ""),
                    "total_trades": ca.get("total_trades", 0),
                })

        return {
            "type": briefing_type,
            "generated_at": datetime.now().isoformat(),
            "market_status": self._get_market_status(),
            "summary": self._build_summary(all_sorted, briefing_type),
            "highlights": highlights,
            "recommendations": recommendations,
            "congress_notable": congress_notable,
            "disclaimer": (
                "OBS: Detta är inte finansiell rådgivning. Informationen är baserad på "
                "automatiserad analys och ska inte användas som enda underlag för "
                "investeringsbeslut. Gör alltid din egen research."
            ),
        }
