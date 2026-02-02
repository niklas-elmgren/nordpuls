from pydantic import BaseModel
from typing import Optional, List


class BriefingRecommendation(BaseModel):
    symbol: str
    name: str
    action: str  # BUY, SELL, HOLD, WATCH, AVOID
    confidence: str  # HIGH, MEDIUM, LOW
    price: float = 0.0
    change_percent: float = 0.0
    reasons: List[str] = []
    news_sentiment: str = "neutral"
    congress_signal: Optional[str] = None


class Briefing(BaseModel):
    type: str  # "morning" or "evening"
    generated_at: str
    market_status: str  # "pre_open", "open", "closed"
    summary: str
    highlights: List[dict] = []
    recommendations: List[BriefingRecommendation] = []
    congress_notable: List[dict] = []
    disclaimer: str = (
        "OBS: Detta \u00e4r inte finansiell r\u00e5dgivning. Informationen \u00e4r baserad p\u00e5 "
        "automatiserad analys och ska inte anv\u00e4ndas som enda underlag f\u00f6r "
        "investeringsbeslut. G\u00f6r alltid din egen research."
    )
