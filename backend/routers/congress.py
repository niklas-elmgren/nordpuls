"""
Congress trading API routes.
"""

from fastapi import APIRouter
from typing import Optional

from agents.congress_trades import CongressTradesFetcher
from services.cache import ttl_cache

router = APIRouter()

_congress_fetcher = CongressTradesFetcher()


@ttl_cache(seconds=1800)
def _get_congress_stats(days: int) -> dict:
    return _congress_fetcher.get_summary_stats(days)


@ttl_cache(seconds=1800)
def _get_recent_trades(days: int, min_amount: str) -> list:
    return _congress_fetcher.get_recent_trades(days, min_amount)


@ttl_cache(seconds=1800)
def _get_ticker_activity(ticker: str) -> dict:
    return _congress_fetcher.check_ticker_congress_activity(ticker)


@router.get("/recent")
def get_recent_trades(days: int = 30, min_amount: str = "$1,001 -"):
    """Get recent congress trades."""
    trades = _get_recent_trades(days, min_amount)
    return {"trades": trades[:100], "total": len(trades)}


@router.get("/stats")
def get_stats(days: int = 30):
    """Get congress trading summary statistics."""
    return _get_congress_stats(days)


@router.get("/ticker/{ticker}")
def get_ticker_activity(ticker: str):
    """Get congress activity for a specific ticker."""
    return _get_ticker_activity(ticker.upper())


@router.get("/politician/{name}")
def get_politician_trades(name: str, days: int = 365):
    """Get trades by a specific politician."""
    trades = _congress_fetcher.get_trades_by_politician(name, days)
    return {"politician": name, "trades": trades[:50], "total": len(trades)}
