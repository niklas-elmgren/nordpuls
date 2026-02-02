"""
congress_trades.py - Hämtar aktiehandel från amerikanska kongressmedlemmar

Använder gratis API:er från:
- House Stock Watcher (https://housestockwatcher.com/api)
- Senate Stock Watcher (https://senatestockwatcher.com/api)

Data uppdateras när nya STOCK Act-rapporter lämnas in (inom 45 dagar efter transaktion).
"""

import requests
from datetime import datetime, timedelta
from typing import Optional, List
import json


class CongressTradesFetcher:
    """Hämtar och analyserar kongressmedlemmars aktiehandel."""
    
    HOUSE_API = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
    SENATE_API = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json"
    
    def __init__(self):
        self.house_data = None
        self.senate_data = None
        self._cache_timestamp = None
    
    def _fetch_data(self, url: str) -> list:
        """Hämtar data från API."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Fel vid hämtning från {url}: {e}")
            return []
    
    def refresh_data(self):
        """Hämtar färsk data från båda API:erna."""
        print("Hämtar kongressdata...")
        self.house_data = self._fetch_data(self.HOUSE_API)
        self.senate_data = self._fetch_data(self.SENATE_API)
        self._cache_timestamp = datetime.now()
        print(f"  House: {len(self.house_data)} transaktioner")
        print(f"  Senate: {len(self.senate_data)} transaktioner")
    
    def _ensure_data(self):
        """Ser till att vi har data (hämtar om det behövs)."""
        if self.house_data is None or self.senate_data is None:
            self.refresh_data()
    
    def get_recent_trades(self, days: int = 30, min_amount: str = "$1,001 -") -> list:
        """
        Hämtar senaste transaktionerna.
        
        Args:
            days: Antal dagar tillbaka att söka
            min_amount: Minsta transaktionsbelopp (t.ex. "$50,001 - $100,000")
            
        Returns:
            Lista med transaktioner
        """
        self._ensure_data()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        trades = []
        
        # Belopp-ordning för filtrering
        amount_order = [
            "$1,001 -", "$1,001 - $15,000", "$15,001 - $50,000",
            "$50,001 - $100,000", "$100,001 - $250,000", 
            "$250,001 - $500,000", "$500,001 - $1,000,000",
            "$1,000,001 - $5,000,000", "$5,000,001 - $25,000,000",
            "$25,000,001 - $50,000,000", "Over $50,000,000"
        ]
        
        min_index = 0
        for i, amt in enumerate(amount_order):
            if min_amount in amt or amt in min_amount:
                min_index = i
                break
        
        # Processa House-data
        for trade in self.house_data or []:
            try:
                trade_date = self._parse_date(trade.get("transaction_date"))
                if trade_date and trade_date >= cutoff_date:
                    # Kolla belopp
                    amount = trade.get("amount", "")
                    amount_index = next((i for i, a in enumerate(amount_order) if a in amount or amount in a), -1)
                    
                    if amount_index >= min_index:
                        trades.append({
                            "chamber": "House",
                            "politician": trade.get("representative", "Unknown"),
                            "party": trade.get("party", ""),
                            "state": trade.get("state", ""),
                            "ticker": trade.get("ticker", ""),
                            "asset": trade.get("asset_description", ""),
                            "type": trade.get("type", ""),
                            "amount": amount,
                            "transaction_date": trade_date.isoformat() if trade_date else "",
                            "disclosure_date": trade.get("disclosure_date", "")
                        })
            except Exception as e:
                continue
        
        # Processa Senate-data
        for trade in self.senate_data or []:
            try:
                trade_date = self._parse_date(trade.get("transaction_date"))
                if trade_date and trade_date >= cutoff_date:
                    amount = trade.get("amount", "")
                    amount_index = next((i for i, a in enumerate(amount_order) if a in amount or amount in a), -1)
                    
                    if amount_index >= min_index:
                        trades.append({
                            "chamber": "Senate",
                            "politician": trade.get("senator", "Unknown"),
                            "party": trade.get("party", ""),
                            "state": trade.get("state", ""),
                            "ticker": trade.get("ticker", ""),
                            "asset": trade.get("asset_description", ""),
                            "type": trade.get("type", ""),
                            "amount": amount,
                            "transaction_date": trade_date.isoformat() if trade_date else "",
                            "disclosure_date": trade.get("disclosure_date", "")
                        })
            except Exception as e:
                continue
        
        # Sortera efter datum (nyast först)
        trades.sort(key=lambda x: x.get("transaction_date", ""), reverse=True)
        
        return trades
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parsar datum från olika format."""
        if not date_str or date_str == "--":
            return None
        
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def get_trades_by_ticker(self, ticker: str, days: int = 90) -> list:
        """
        Hämtar alla transaktioner för en specifik aktie.
        
        Args:
            ticker: Aktiesymbol (t.ex. "AAPL", "MSFT")
            days: Antal dagar tillbaka
            
        Returns:
            Lista med transaktioner
        """
        all_trades = self.get_recent_trades(days=days, min_amount="$1,001 -")
        return [t for t in all_trades if t.get("ticker", "").upper() == ticker.upper()]
    
    def get_trades_by_politician(self, name: str, days: int = 365) -> list:
        """
        Hämtar alla transaktioner för en specifik politiker.
        
        Args:
            name: Politikerns namn (delmatchning fungerar)
            days: Antal dagar tillbaka
            
        Returns:
            Lista med transaktioner
        """
        all_trades = self.get_recent_trades(days=days, min_amount="$1,001 -")
        name_lower = name.lower()
        return [t for t in all_trades if name_lower in t.get("politician", "").lower()]
    
    def get_summary_stats(self, days: int = 30) -> dict:
        """
        Genererar sammanfattande statistik.
        
        Returns:
            Dict med statistik
        """
        trades = self.get_recent_trades(days=days)
        
        if not trades:
            return {"error": "Inga trades hittades"}
        
        # Räkna köp vs sälj
        buys = [t for t in trades if "purchase" in t.get("type", "").lower()]
        sells = [t for t in trades if "sale" in t.get("type", "").lower()]
        
        # Mest handlade aktier
        ticker_counts = {}
        for t in trades:
            ticker = t.get("ticker", "")
            if ticker and ticker != "--":
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
        
        top_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Mest aktiva politiker
        politician_counts = {}
        for t in trades:
            pol = t.get("politician", "Unknown")
            politician_counts[pol] = politician_counts.get(pol, 0) + 1
        
        top_politicians = sorted(politician_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Parti-fördelning
        party_counts = {"D": 0, "R": 0, "I": 0, "Other": 0}
        for t in trades:
            party = t.get("party", "")
            if "D" in party:
                party_counts["D"] += 1
            elif "R" in party:
                party_counts["R"] += 1
            elif "I" in party:
                party_counts["I"] += 1
            else:
                party_counts["Other"] += 1
        
        return {
            "period_days": days,
            "total_trades": len(trades),
            "buys": len(buys),
            "sells": len(sells),
            "buy_sell_ratio": round(len(buys) / max(len(sells), 1), 2),
            "top_tickers": top_tickers,
            "top_politicians": top_politicians,
            "party_breakdown": party_counts,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_ticker_congress_activity(self, ticker: str) -> dict:
        """
        Kontrollerar om kongressmedlemmar nyligen handlat en aktie.
        Användbart för att integrera med aktieanalys.
        
        Args:
            ticker: Aktiesymbol
            
        Returns:
            Dict med aktivitetsinformation
        """
        # Kolla senaste 90 dagarna
        trades = self.get_trades_by_ticker(ticker, days=90)
        
        if not trades:
            return {
                "ticker": ticker,
                "has_congress_activity": False,
                "message": f"Ingen kongressaktivitet för {ticker} senaste 90 dagarna"
            }
        
        buys = [t for t in trades if "purchase" in t.get("type", "").lower()]
        sells = [t for t in trades if "sale" in t.get("type", "").lower()]
        
        # Skapa sammanfattning
        recent_trades = trades[:5]  # Senaste 5
        
        # Bedöm sentiment
        if len(buys) > len(sells) * 2:
            sentiment = "BULLISH 🟢"
            sentiment_desc = f"Kongressen köper mer än de säljer ({len(buys)} köp vs {len(sells)} sälj)"
        elif len(sells) > len(buys) * 2:
            sentiment = "BEARISH 🔴"
            sentiment_desc = f"Kongressen säljer mer än de köper ({len(sells)} sälj vs {len(buys)} köp)"
        else:
            sentiment = "NEUTRAL 🟡"
            sentiment_desc = f"Blandad aktivitet ({len(buys)} köp, {len(sells)} sälj)"
        
        return {
            "ticker": ticker,
            "has_congress_activity": True,
            "total_trades": len(trades),
            "buys": len(buys),
            "sells": len(sells),
            "sentiment": sentiment,
            "sentiment_description": sentiment_desc,
            "recent_trades": recent_trades,
            "politicians_involved": list(set(t.get("politician") for t in trades))
        }


# Enkel test
if __name__ == "__main__":
    fetcher = CongressTradesFetcher()
    
    print("\n=== KONGRESS-TRADING RAPPORT ===\n")
    
    # Hämta sammanfattning
    print("Hämtar statistik för senaste 30 dagarna...")
    stats = fetcher.get_summary_stats(days=30)
    
    if "error" not in stats:
        print(f"\nTotalt antal transaktioner: {stats['total_trades']}")
        print(f"Köp: {stats['buys']} | Sälj: {stats['sells']}")
        print(f"Köp/Sälj-ratio: {stats['buy_sell_ratio']}")
        
        print(f"\nParti-fördelning:")
        print(f"  Demokrater (D): {stats['party_breakdown']['D']}")
        print(f"  Republikaner (R): {stats['party_breakdown']['R']}")
        
        print(f"\nMest handlade aktier:")
        for ticker, count in stats['top_tickers'][:5]:
            print(f"  {ticker}: {count} transaktioner")
        
        print(f"\nMest aktiva politiker:")
        for name, count in stats['top_politicians'][:5]:
            print(f"  {name}: {count} transaktioner")
    else:
        print(stats["error"])
    
    # Testa specifik aktie
    print("\n--- Kollar kongressaktivitet för NVDA ---")
    nvda_activity = fetcher.check_ticker_congress_activity("NVDA")
    print(f"Aktivitet: {nvda_activity.get('sentiment', 'Ingen data')}")
    if nvda_activity.get("has_congress_activity"):
        print(f"  {nvda_activity['sentiment_description']}")
