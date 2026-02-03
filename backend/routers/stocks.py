"""
Stock data API routes.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.stock_data import StockDataFetcher
from agents.news_fetcher import NewsFetcher
from agents.congress_trades import CongressTradesFetcher
from agents.research_agent import ResearchAgent
from services.cache import ttl_cache

router = APIRouter()

_stock_fetcher = StockDataFetcher()
_config_path = Path(__file__).parent.parent / "config" / "config.json"
_omx_path = Path(__file__).parent.parent / "config" / "omx_stockholm.json"


def _load_config():
    with open(_config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_omx_stocks():
    """Load full OMX Stockholm stock list."""
    with open(_omx_path, "r", encoding="utf-8") as f:
        return json.load(f)


@ttl_cache(seconds=300)
def _get_stock_info(symbol: str) -> dict:
    return _stock_fetcher.get_stock_info(symbol)


@ttl_cache(seconds=300)
def _check_unusual_activity(symbol: str) -> dict:
    return _stock_fetcher.check_unusual_activity(symbol)


def _fetch_stock_data(stock: dict, cap_size: str = "") -> dict:
    """Fetch stock data for a single stock."""
    symbol = stock["symbol"]
    data = _get_stock_info(symbol)
    return {
        "symbol": symbol,
        "name": stock["name"],
        "market": stock.get("market", "OMX Stockholm"),
        "cap_size": cap_size,
        "current_price": data.get("current_price", 0),
        "change_percent": data.get("change_percent", 0),
        "volume_vs_avg": data.get("volume_vs_avg", 1),
        "currency": data.get("currency", "SEK"),
        "high_52w": data.get("high_52w"),
        "low_52w": data.get("low_52w"),
        "error": data.get("error"),
    }


@router.get("/all")
def get_all_stocks(
    cap: Optional[str] = Query(None, description="Filter by cap size: large, mid, small, us"),
    search: Optional[str] = Query(None, description="Search by symbol or name"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: Optional[str] = Query("change_percent", description="Sort field"),
    sort_desc: bool = Query(True, description="Sort descending"),
):
    """Get all stocks with filtering, searching, and pagination."""
    omx_data = _load_omx_stocks()
    stocks_config = omx_data.get("stocks", {})

    # Build stock list with cap size info
    all_stocks = []

    if cap is None or cap == "large":
        for stock in stocks_config.get("large_cap", []):
            all_stocks.append({**stock, "cap_size": "large", "market": "OMX Stockholm"})

    if cap is None or cap == "mid":
        for stock in stocks_config.get("mid_cap", []):
            all_stocks.append({**stock, "cap_size": "mid", "market": "OMX Stockholm"})

    if cap is None or cap == "small":
        for stock in stocks_config.get("small_cap", []):
            all_stocks.append({**stock, "cap_size": "small", "market": "OMX Stockholm"})

    if cap is None or cap == "first_north":
        for stock in stocks_config.get("first_north", []):
            all_stocks.append({**stock, "cap_size": "first_north", "market": "First North"})

    if cap is None or cap == "us":
        for stock in stocks_config.get("us_watchlist", []):
            all_stocks.append({**stock, "cap_size": "us"})

    # Apply search filter
    if search:
        search_lower = search.lower()
        all_stocks = [
            s for s in all_stocks
            if search_lower in s["symbol"].lower() or search_lower in s["name"].lower()
        ]

    total_count = len(all_stocks)

    # Paginate before fetching (to limit API calls)
    paginated_stocks = all_stocks[offset:offset + limit]

    # Fetch data in parallel
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(_fetch_stock_data, stock, stock.get("cap_size", "")): stock
            for stock in paginated_stocks
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                if result.get("current_price", 0) > 0:  # Only include valid stocks
                    results.append(result)
            except Exception as e:
                continue

    # Sort results
    if sort_by:
        results.sort(
            key=lambda x: x.get(sort_by, 0) or 0,
            reverse=sort_desc
        )

    return {
        "stocks": results,
        "total": total_count,
        "limit": limit,
        "offset": offset,
    }


@router.get("/top-movers")
def get_top_movers(limit: int = Query(10, ge=1, le=50)):
    """Get top gaining and losing stocks."""
    omx_data = _load_omx_stocks()
    stocks_config = omx_data.get("stocks", {})

    # Focus on large and mid cap for top movers
    all_stocks = []
    for stock in stocks_config.get("large_cap", []):
        all_stocks.append({**stock, "cap_size": "large", "market": "OMX Stockholm"})
    for stock in stocks_config.get("mid_cap", []):
        all_stocks.append({**stock, "cap_size": "mid", "market": "OMX Stockholm"})

    # Fetch data in parallel
    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {
            executor.submit(_fetch_stock_data, stock, stock.get("cap_size", "")): stock
            for stock in all_stocks
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                if result.get("current_price", 0) > 0:
                    results.append(result)
            except:
                continue

    # Sort by change percent
    results.sort(key=lambda x: x.get("change_percent", 0), reverse=True)

    gainers = results[:limit]
    losers = results[-limit:][::-1]

    return {
        "gainers": gainers,
        "losers": losers,
    }


@router.get("/watchlist")
def get_watchlist():
    """Get original watchlist stocks with current data (legacy endpoint)."""
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


@router.get("/caps")
def get_cap_sizes():
    """Get available cap sizes and stock counts."""
    omx_data = _load_omx_stocks()
    stocks_config = omx_data.get("stocks", {})

    return {
        "caps": [
            {"id": "large", "name": "Large Cap", "count": len(stocks_config.get("large_cap", []))},
            {"id": "mid", "name": "Mid Cap", "count": len(stocks_config.get("mid_cap", []))},
            {"id": "small", "name": "Small Cap", "count": len(stocks_config.get("small_cap", []))},
            {"id": "first_north", "name": "First North", "count": len(stocks_config.get("first_north", []))},
            {"id": "us", "name": "US Market", "count": len(stocks_config.get("us_watchlist", []))},
        ]
    }


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
    # Try to find stock in OMX list first
    omx_data = _load_omx_stocks()
    stocks_config = omx_data.get("stocks", {})

    stock_info = None
    for cap in ["large_cap", "mid_cap", "small_cap", "us_watchlist"]:
        for stock in stocks_config.get(cap, []):
            if stock["symbol"] == symbol:
                stock_info = stock
                break
        if stock_info:
            break

    if not stock_info:
        # Fallback to config
        config = _load_config()
        watchlist = {s["symbol"]: s for s in config.get("watchlist", [])}
        stock_info = watchlist.get(symbol, {"symbol": symbol, "name": symbol})

    agent = ResearchAgent(str(_config_path))
    analysis = agent.analyze_stock(stock_info["symbol"], stock_info.get("name", symbol))
    return analysis
