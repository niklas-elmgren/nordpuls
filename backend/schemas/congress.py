from pydantic import BaseModel
from typing import Optional, List, Tuple


class CongressTrade(BaseModel):
    chamber: str = ""
    politician: str = ""
    party: str = ""
    state: str = ""
    ticker: str = ""
    asset: str = ""
    type: str = ""
    amount: str = ""
    transaction_date: str = ""
    disclosure_date: str = ""


class CongressStats(BaseModel):
    period_days: int = 30
    total_trades: int = 0
    buys: int = 0
    sells: int = 0
    buy_sell_ratio: float = 0.0
    top_tickers: List[List] = []
    top_politicians: List[List] = []
    party_breakdown: dict = {}
    timestamp: str = ""
    error: Optional[str] = None


class CongressTickerActivity(BaseModel):
    ticker: str
    has_congress_activity: bool = False
    total_trades: int = 0
    buys: int = 0
    sells: int = 0
    sentiment: Optional[str] = None
    sentiment_description: Optional[str] = None
    recent_trades: List[dict] = []
    politicians_involved: List[str] = []
    message: Optional[str] = None
