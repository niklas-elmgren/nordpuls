"""
Climate API routes - marknadsklimat och ekonomisk kalender.
"""

from fastapi import APIRouter
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from agents.climate_agent import ClimateAgent
from agents.stock_data import StockDataFetcher
from agents.research_agent import ResearchAgent
from services.cache import ttl_cache

router = APIRouter()

_climate_agent = ClimateAgent()
_stock_fetcher = StockDataFetcher()
_config_path = str(Path(__file__).parent.parent / "config" / "config.json")
_omx_path = Path(__file__).parent.parent / "config" / "omx_stockholm.json"


def _load_omx_stocks() -> dict:
    with open(_omx_path, "r", encoding="utf-8") as f:
        return json.load(f)


@ttl_cache(seconds=300)
def _get_indices() -> list:
    return _climate_agent.get_all_indices()


@ttl_cache(seconds=21600)
def _get_di_events() -> list:
    """DI-scrape cachas 6 timmar."""
    return _climate_agent.scrape_di_calendar()


@ttl_cache(seconds=3600)
def _get_events() -> list:
    """Alla events ihopslagna, cachas 1 timme."""
    di_events = _get_di_events()
    return _climate_agent.get_all_events(di_events=di_events)


@ttl_cache(seconds=300)
def _get_signals() -> dict:
    """Hämtar signalfördelning från Large Cap aktier."""
    omx_data = _load_omx_stocks()
    stocks = omx_data.get("stocks", {}).get("large_cap", [])

    agent = ResearchAgent(_config_path)

    analyses = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(_analyze_stock, agent, stock): stock
            for stock in stocks[:30]  # Begränsa till 30 för snabbhet
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    analyses.append(result)
            except Exception:
                pass

    return _climate_agent.aggregate_internal_signals(analyses)


def _analyze_stock(agent: ResearchAgent, stock: dict) -> dict:
    """Analysera en aktie med felhantering."""
    try:
        return agent.analyze_stock(stock["symbol"], stock["name"])
    except Exception as e:
        return {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "stock_data": {"error": str(e), "change_percent": 0, "volume_vs_avg": 1},
            "signal": {"type": "NEUTRAL", "score": 0, "reasons": [f"Fel: {e}"]},
        }


@router.get("/overview")
def get_climate_overview():
    """Komplett marknadsklimat: index + signaler + events."""
    indices = _get_indices()
    signals = _get_signals()
    events = _get_events()

    return {
        "indices": indices,
        "signals": signals,
        "events": events,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/indices")
def get_indices():
    """Bara indexdata (OMX30, S&P 500, VIX)."""
    return {
        "indices": _get_indices(),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/events")
def get_events():
    """Bara ekonomisk kalender."""
    return {
        "events": _get_events(),
        "timestamp": datetime.now().isoformat(),
    }
