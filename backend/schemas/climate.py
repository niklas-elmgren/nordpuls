from pydantic import BaseModel
from typing import Optional, List


class MarketIndex(BaseModel):
    symbol: str
    name: str
    current_price: float = 0.0
    change_percent: float = 0.0
    trend: str = "neutral"  # "up", "down", "neutral"
    currency: str = "SEK"


class SignalDistribution(BaseModel):
    total_stocks: int = 0
    buy: int = 0
    sell: int = 0
    watch: int = 0
    hold: int = 0
    avoid: int = 0


class InternalSignals(BaseModel):
    signal_distribution: SignalDistribution = SignalDistribution()
    avg_change_percent: float = 0.0
    high_volume_count: int = 0
    overall_sentiment: str = "neutral"  # "bullish", "bearish", "neutral"


class CalendarEvent(BaseModel):
    id: str
    date: str
    title: str
    category: str = ""
    source: str = ""
    impact: str = "medium"  # "high", "medium", "low"
    days_until: int = 0
    is_active: bool = False


class ClimateOverview(BaseModel):
    indices: List[MarketIndex] = []
    signals: InternalSignals = InternalSignals()
    events: List[CalendarEvent] = []
    timestamp: str = ""
