from pydantic import BaseModel
from typing import Optional, List


class SentimentResult(BaseModel):
    sentiment: str = "neutral"
    score: float = 0.0
    positive_words: List[str] = []
    negative_words: List[str] = []


class NewsArticle(BaseModel):
    title: str
    summary: str = ""
    link: str = ""
    published: str = ""
    source: str = ""
    category: Optional[str] = None
    sentiment: Optional[SentimentResult] = None


class NewsSummary(BaseModel):
    company: str
    symbol: Optional[str] = None
    article_count: int = 0
    overall_sentiment: str = "no_data"
    sentiment_score: float = 0.0
    articles: List[NewsArticle] = []
    timestamp: str = ""
