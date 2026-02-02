from pydantic import BaseModel
from typing import Optional, List


class StockInfo(BaseModel):
    symbol: str
    name: str = ""
    current_price: float = 0.0
    change_percent: float = 0.0
    volume: int = 0
    volume_vs_avg: float = 1.0
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    market_cap: Optional[int] = None
    currency: str = "SEK"
    timestamp: str = ""
    error: Optional[str] = None


class UnusualActivity(BaseModel):
    symbol: str
    flags: List[str] = []
    has_unusual_activity: bool = False
    data: Optional[StockInfo] = None


class Signal(BaseModel):
    type: str
    score: int
    reasons: List[str] = []


class NewsSummaryBrief(BaseModel):
    count: int = 0
    sentiment: str = "neutral"
    score: float = 0.0


class StockAnalysis(BaseModel):
    symbol: str
    name: str
    stock_data: dict
    unusual_activity: List[str] = []
    news_summary: NewsSummaryBrief
    recent_headlines: List[str] = []
    congress_activity: dict = {}
    signal: Signal
    timestamp: str = ""


class WatchlistItem(BaseModel):
    symbol: str
    name: str
    market: str
    note: Optional[str] = None


class WatchlistStockData(BaseModel):
    symbol: str
    name: str
    market: str
    current_price: float = 0.0
    change_percent: float = 0.0
    volume_vs_avg: float = 1.0
    currency: str = "SEK"
    signal_score: Optional[int] = None
    signal_type: Optional[str] = None
    error: Optional[str] = None
