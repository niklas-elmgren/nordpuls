"""
news_fetcher.py - Hämtar och analyserar nyheter från RSS-flöden

Funktioner:
- Hämtar nyheter från svenska och internationella källor
- Filtrerar nyheter relaterade till specifika aktier/bolag
- Enkel sentimentanalys baserad på nyckelord
"""

import feedparser
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import re


class NewsFetcher:
    """Hämtar och filtrerar nyheter från RSS-flöden."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.sentiment_keywords = self.config.get("settings", {}).get("sentiment_keywords", {})
    
    def fetch_feed(self, url: str) -> list:
        """
        Hämtar artiklar från ett RSS-flöde.
        
        Args:
            url: RSS-flödets URL
            
        Returns:
            Lista med artiklar
        """
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:20]:  # Max 20 artiklar per källa
                published = entry.get("published_parsed")
                if published:
                    pub_date = datetime(*published[:6])
                else:
                    pub_date = datetime.now()
                
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:500],  # Begränsa längd
                    "link": entry.get("link", ""),
                    "published": pub_date.isoformat(),
                    "source": feed.feed.get("title", "Okänd källa")
                })
            
            return articles
            
        except Exception as e:
            print(f"Fel vid hämtning av {url}: {e}")
            return []
    
    def fetch_all_news(self) -> list:
        """Hämtar nyheter från alla konfigurerade källor."""
        all_articles = []
        
        for category in ["swedish", "international"]:
            feeds = self.config.get("news_feeds", {}).get(category, [])
            for feed_config in feeds:
                articles = self.fetch_feed(feed_config["url"])
                for article in articles:
                    article["category"] = category
                all_articles.extend(articles)
        
        # Sortera efter datum (nyast först)
        all_articles.sort(key=lambda x: x["published"], reverse=True)
        
        return all_articles
    
    def filter_by_company(self, articles: list, company_name: str, symbol: str = None) -> list:
        """
        Filtrerar artiklar som nämner ett specifikt bolag.
        
        Args:
            articles: Lista med artiklar
            company_name: Bolagsnamn att söka efter
            symbol: Aktiesymbol (valfritt)
            
        Returns:
            Filtrerade artiklar
        """
        keywords = [company_name.lower()]
        
        # Lägg till varianter av namnet
        if " " in company_name:
            keywords.append(company_name.split()[0].lower())  # Första ordet
        
        if symbol:
            # Ta bort .ST suffix för svenska aktier
            clean_symbol = symbol.replace(".ST", "").replace("-B", "").replace("-A", "")
            keywords.append(clean_symbol.lower())
        
        filtered = []
        for article in articles:
            text = (article["title"] + " " + article["summary"]).lower()
            if any(kw in text for kw in keywords):
                filtered.append(article)
        
        return filtered
    
    def analyze_sentiment(self, text: str) -> dict:
        """
        Enkel sentimentanalys baserad på nyckelord.
        
        Args:
            text: Text att analysera
            
        Returns:
            Dict med sentiment-score och matchade ord
        """
        text_lower = text.lower()
        
        positive_matches = [w for w in self.sentiment_keywords.get("positive", []) 
                          if w.lower() in text_lower]
        negative_matches = [w for w in self.sentiment_keywords.get("negative", []) 
                          if w.lower() in text_lower]
        
        pos_count = len(positive_matches)
        neg_count = len(negative_matches)
        total = pos_count + neg_count
        
        if total == 0:
            sentiment = "neutral"
            score = 0
        elif pos_count > neg_count:
            sentiment = "positive"
            score = pos_count / total
        elif neg_count > pos_count:
            sentiment = "negative"
            score = -neg_count / total
        else:
            sentiment = "mixed"
            score = 0
        
        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive_words": positive_matches,
            "negative_words": negative_matches
        }
    
    def get_news_summary(self, company_name: str, symbol: str = None) -> dict:
        """
        Hämtar och sammanfattar nyheter för ett bolag.
        
        Returns:
            Sammanfattning med nyheter och sentiment
        """
        all_news = self.fetch_all_news()
        company_news = self.filter_by_company(all_news, company_name, symbol)
        
        # Analysera sentiment för varje artikel
        for article in company_news:
            text = article["title"] + " " + article["summary"]
            article["sentiment"] = self.analyze_sentiment(text)
        
        # Räkna ut övergripande sentiment
        if company_news:
            avg_score = sum(a["sentiment"]["score"] for a in company_news) / len(company_news)
            if avg_score > 0.2:
                overall = "positive"
            elif avg_score < -0.2:
                overall = "negative"
            else:
                overall = "neutral"
        else:
            overall = "no_data"
            avg_score = 0
        
        return {
            "company": company_name,
            "symbol": symbol,
            "article_count": len(company_news),
            "overall_sentiment": overall,
            "sentiment_score": round(avg_score, 2),
            "articles": company_news[:10],  # Max 10 artiklar i sammanfattningen
            "timestamp": datetime.now().isoformat()
        }


# Enkel test
if __name__ == "__main__":
    fetcher = NewsFetcher()
    
    print("Hämtar alla nyheter...")
    news = fetcher.fetch_all_news()
    print(f"Hittade {len(news)} artiklar totalt\n")
    
    print("Söker nyheter om Volvo...")
    summary = fetcher.get_news_summary("Volvo", "VOLV-B.ST")
    print(f"Hittade {summary['article_count']} artiklar om Volvo")
    print(f"Övergripande sentiment: {summary['overall_sentiment']}")
    
    if summary["articles"]:
        print("\nSenaste artiklarna:")
        for article in summary["articles"][:3]:
            print(f"  - {article['title'][:60]}...")
            print(f"    Sentiment: {article['sentiment']['sentiment']}")
