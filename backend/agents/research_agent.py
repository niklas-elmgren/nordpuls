"""
research_agent.py - Huvudagent som kombinerar aktiedata, nyheter och kongresshandel

Detta är "hjärnan" som:
1. Läser din watchlist
2. Hämtar aktiedata och nyheter för varje aktie
3. Kollar om amerikanska kongressmedlemmar handlat aktien
4. Skapar en sammanfattande rapport
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .stock_data import StockDataFetcher
from .news_fetcher import NewsFetcher
from .congress_trades import CongressTradesFetcher


class ResearchAgent:
    """Huvudagent för aktieresearch."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.stock_fetcher = StockDataFetcher()
        self.news_fetcher = NewsFetcher(config_path)
        self.congress_fetcher = CongressTradesFetcher()
    
    def analyze_stock(self, symbol: str, name: str) -> dict:
        """
        Gör en komplett analys av en aktie.
        
        Args:
            symbol: Aktiesymbol
            name: Bolagsnamn
            
        Returns:
            Komplett analysresultat
        """
        print(f"  Analyserar {name} ({symbol})...")
        
        # Hämta aktiedata
        stock_data = self.stock_fetcher.get_stock_info(symbol)
        activity = self.stock_fetcher.check_unusual_activity(symbol)
        
        # Hämta nyheter
        news_summary = self.news_fetcher.get_news_summary(name, symbol)
        
        # Kolla kongresshandel (för amerikanska aktier)
        # Extrahera ren ticker utan .ST suffix
        clean_ticker = symbol.replace(".ST", "").replace("-B", "").replace("-A", "").upper()
        congress_activity = self.congress_fetcher.check_ticker_congress_activity(clean_ticker)
        
        # Kombinera till en "signal"
        signal = self._generate_signal(stock_data, activity, news_summary, congress_activity)
        
        return {
            "symbol": symbol,
            "name": name,
            "stock_data": stock_data,
            "unusual_activity": activity.get("flags", []),
            "news_summary": {
                "count": news_summary["article_count"],
                "sentiment": news_summary["overall_sentiment"],
                "score": news_summary["sentiment_score"]
            },
            "recent_headlines": [a["title"] for a in news_summary["articles"][:3]],
            "congress_activity": congress_activity,
            "signal": signal,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_signal(self, stock_data: dict, activity: dict, news: dict, congress: dict = None) -> dict:
        """
        Genererar en enkel signal baserad på data.
        OBS: Detta är INTE finansiell rådgivning!
        """
        points = 0
        reasons = []
        
        # Kursrörelse
        change = stock_data.get("change_percent", 0)
        if change > 2:
            points += 1
            reasons.append(f"Positiv kursrörelse (+{change:.1f}%)")
        elif change < -2:
            points -= 1
            reasons.append(f"Negativ kursrörelse ({change:.1f}%)")
        
        # Volym
        vol_ratio = stock_data.get("volume_vs_avg", 1)
        if vol_ratio > 1.5:
            reasons.append(f"Ovanligt hög volym ({vol_ratio:.1f}x)")
        
        # Nyhetssentiment
        sentiment = news.get("overall_sentiment", "neutral")
        if sentiment == "positive":
            points += 1
            reasons.append("Positivt nyhetssentiment")
        elif sentiment == "negative":
            points -= 1
            reasons.append("Negativt nyhetssentiment")
        
        # Kongresshandel
        if congress and congress.get("has_congress_activity"):
            congress_sentiment = congress.get("sentiment", "")
            if "BULLISH" in congress_sentiment:
                points += 1
                reasons.append(f"🏛️ Kongressen köper ({congress.get('buys', 0)} köp senaste 90 dagarna)")
            elif "BEARISH" in congress_sentiment:
                points -= 1
                reasons.append(f"🏛️ Kongressen säljer ({congress.get('sells', 0)} sälj senaste 90 dagarna)")
            else:
                reasons.append(f"🏛️ Kongressaktivitet ({congress.get('total_trades', 0)} transaktioner)")
        
        # Bestäm övergripande signal
        if points >= 2:
            signal_type = "INTRESSANT 👀"
        elif points <= -2:
            signal_type = "VARNING ⚠️"
        else:
            signal_type = "NEUTRAL ➖"
        
        return {
            "type": signal_type,
            "score": points,
            "reasons": reasons
        }
    
    def run_daily_report(self, include_congress_summary: bool = True) -> dict:
        """
        Kör en komplett daglig analys av hela watchlisten.
        
        Args:
            include_congress_summary: Om en separat kongresssammanfattning ska inkluderas
        
        Returns:
            Komplett rapport
        """
        print(f"\n{'='*60}")
        print(f"📊 DAGLIG MARKNADSRAPPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}\n")
        
        watchlist = self.config.get("watchlist", [])
        results = []
        
        for stock in watchlist:
            analysis = self.analyze_stock(stock["symbol"], stock["name"])
            results.append(analysis)
        
        # Hämta kongressöversikt
        congress_summary = None
        if include_congress_summary:
            print("\n  Hämtar kongresshandel-översikt...")
            congress_summary = self.congress_fetcher.get_summary_stats(days=30)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "stocks_analyzed": len(results),
            "results": results,
            "highlights": self._extract_highlights(results),
            "congress_summary": congress_summary
        }
        
        return report
    
    def _extract_highlights(self, results: list) -> list:
        """Extraherar viktiga händelser från analysen."""
        highlights = []
        
        for r in results:
            # Flagga intressanta eller varningssignaler
            if r["signal"]["type"] != "NEUTRAL ➖":
                highlights.append({
                    "stock": r["name"],
                    "signal": r["signal"]["type"],
                    "reasons": r["signal"]["reasons"]
                })
            
            # Flagga hög volym
            if r["unusual_activity"]:
                for flag in r["unusual_activity"]:
                    highlights.append({
                        "stock": r["name"],
                        "alert": flag
                    })
        
        return highlights
    
    def format_report_text(self, report: dict) -> str:
        """Formaterar rapporten som läsbar text."""
        lines = [
            f"# Marknadsrapport {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Sammanfattning",
            ""
        ]
        
        # Highlights
        if report["highlights"]:
            lines.append("### ⚡ Viktiga händelser")
            for h in report["highlights"]:
                if "signal" in h:
                    lines.append(f"- **{h['stock']}**: {h['signal']}")
                    for reason in h.get("reasons", []):
                        lines.append(f"  - {reason}")
                elif "alert" in h:
                    lines.append(f"- **{h['stock']}**: {h['alert']}")
            lines.append("")
        
        # Kongressöversikt
        congress = report.get("congress_summary")
        if congress and "error" not in congress:
            lines.append("## 🏛️ Kongresshandel (senaste 30 dagarna)")
            lines.append("")
            lines.append(f"- **Totalt**: {congress.get('total_trades', 0)} transaktioner")
            lines.append(f"- **Köp/Sälj**: {congress.get('buys', 0)} köp, {congress.get('sells', 0)} sälj (ratio: {congress.get('buy_sell_ratio', 0)})")
            
            top_tickers = congress.get("top_tickers", [])[:5]
            if top_tickers:
                lines.append("- **Mest handlade**:")
                for ticker, count in top_tickers:
                    lines.append(f"  - {ticker}: {count} transaktioner")
            
            top_pols = congress.get("top_politicians", [])[:3]
            if top_pols:
                lines.append("- **Mest aktiva politiker**:")
                for name, count in top_pols:
                    lines.append(f"  - {name}: {count} transaktioner")
            lines.append("")
        
        # Detaljer per aktie
        lines.append("## Aktier i fokus")
        lines.append("")
        
        for r in report["results"]:
            stock = r["stock_data"]
            lines.append(f"### {r['name']} ({r['symbol']})")
            
            if "error" not in stock:
                lines.append(f"- **Kurs**: {stock['current_price']} {stock.get('currency', 'SEK')}")
                lines.append(f"- **Förändring**: {stock['change_percent']:+.2f}%")
                lines.append(f"- **Volym vs snitt**: {stock['volume_vs_avg']:.1f}x")
            
            lines.append(f"- **Nyhetssentiment**: {r['news_summary']['sentiment']}")
            
            # Kongressaktivitet för denna aktie
            congress_act = r.get("congress_activity", {})
            if congress_act.get("has_congress_activity"):
                lines.append(f"- **Kongressaktivitet**: {congress_act.get('sentiment', 'N/A')}")
                lines.append(f"  - {congress_act.get('sentiment_description', '')}")
            
            if r["recent_headlines"]:
                lines.append("- **Senaste nyheter**:")
                for headline in r["recent_headlines"]:
                    lines.append(f"  - {headline[:70]}...")
            
            lines.append(f"- **Signal**: {r['signal']['type']}")
            lines.append("")
        
        lines.append("---")
        lines.append("*OBS: Detta är inte finansiell rådgivning. Gör alltid din egen research.*")
        
        return "\n".join(lines)


# Huvudprogram
if __name__ == "__main__":
    agent = ResearchAgent()
    
    # Kör daglig rapport
    report = agent.run_daily_report()
    
    # Formatera och skriv ut
    text_report = agent.format_report_text(report)
    print(text_report)
    
    # Spara till fil
    output_path = Path(__file__).parent.parent / "output" / f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_report)
    print(f"\n✅ Rapport sparad till: {output_path}")
