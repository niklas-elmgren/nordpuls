"""
News API routes.
"""

from fastapi import APIRouter
from typing import Optional
from pathlib import Path

from agents.news_fetcher import NewsFetcher
from services.cache import ttl_cache

router = APIRouter()

_config_path = str(Path(__file__).parent.parent / "config" / "config.json")
_news_fetcher = NewsFetcher(_config_path)


@ttl_cache(seconds=600)
def _get_all_news() -> list:
    return _news_fetcher.fetch_all_news()


@ttl_cache(seconds=600)
def _get_news_summary(company: str, symbol: str) -> dict:
    return _news_fetcher.get_news_summary(company, symbol)


@router.get("/feed")
def get_news_feed(company: Optional[str] = None, symbol: Optional[str] = None):
    """Get news articles, optionally filtered by company."""
    articles = _get_all_news()

    if company or symbol:
        articles = _news_fetcher.filter_by_company(
            articles,
            company or "",
            symbol
        )
        for article in articles:
            text = article["title"] + " " + article.get("summary", "")
            article["sentiment"] = _news_fetcher.analyze_sentiment(text)

    return {"articles": articles[:20], "total": len(articles)}


@router.get("/{symbol}/sentiment")
def get_sentiment(symbol: str, company: Optional[str] = None):
    """Get news summary with sentiment for a stock."""
    return _get_news_summary(company or symbol, symbol)
