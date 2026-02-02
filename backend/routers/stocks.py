"""
Stock data API routes.
"""

from fastapi import APIRouter, HTTPException
from typing import List
import json
from pathlib import Path

from agents.stock_data import StockDataFetcher
from agents.news_fetcher import NewsFetcher
from agents.congress_trades import CongressTradesFetcher
from agents.research_agent import ResearchAgent
from services.cache import ttl_cache

router = APIRouter()

_stock_fetcher = StockDataFetcher()
_config_path = Path(__file__).parent.parent / "config" / "config.json"


def _load_config():
    with open(_config_path, "r", encoding="utf-8") as f:
        return json.load(f)


@ttl_cache(seconds=300)
def _get_stock_info(symbol: str) -> dict:
    return _stock_fetcher.get_stock_info(symbol)


@ttl_cache(seconds=300)
def _check_unusual_activity(symbol: str) -> dict:
    return _stock_fetcher.check_unusual_activity(symbol)


@router.get("/watchlist")
def get_watchlist():
    """Get all watchlist stocks with current data."""
    config = _load_config()
    watchlist = config.get("watchlist", [])
    results = []

    for stock in watchlist:
        data = _get_stock_info(stock["symbol"])
        results.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "market": stock.get("market", ""),
            "current_price": data.get("current_price", 0),
            "change_percent": data.get("change_percent", 0),
            "volume_vs_avg": data.get("volume_vs_avg", 1),
            "currency": data.get("currency", "SEK"),
            "error": data.get("error"),
        })

    return {"stocks": results}


@router.get("/{symbol}")
def get_stock(symbol: str):
    """Get detailed stock data."""
    data = _get_stock_info(symbol)
    if "error" in data and not data.get("current_price"):
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@router.get("/{symbol}/activity")
def get_stock_activity(symbol: str):
    """Check for unusual activity."""
    return _check_unusual_activity(symbol)


@router.get("/{symbol}/history")
def get_stock_history(symbol: str, days: int = 30):
    """Get price history as OHLCV data."""
    df = _stock_fetcher.get_price_history(symbol, days)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No history for {symbol}")

    records = []
    for idx, row in df.iterrows():
        records.append({
            "time": idx.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        })
    return {"symbol": symbol, "data": records}


@router.get("/{symbol}/analysis")
def get_stock_analysis(symbol: str):
    """Full analysis combining stock data, news, and congress activity."""
    config = _load_config()
    watchlist = {s["symbol"]: s for s in config.get("watchlist", [])}
    stock_info = watchlist.get(symbol, {"symbol": symbol, "name": symbol})

    agent = ResearchAgent(str(_config_path))
    analysis = agent.analyze_stock(stock_info["symbol"], stock_info.get("name", symbol))
    return analysis
