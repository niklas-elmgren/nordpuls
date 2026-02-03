"""
congress_trades.py - Hämtar aktiehandel från amerikanska kongressmedlemmar

Använder Quiver Quantitative API:
https://api.quiverquant.com/beta/live/congresstrading

Data uppdateras när nya STOCK Act-rapporter lämnas in (inom 45 dagar efter transaktion).
"""

import requests
from datetime import datetime, timedelta
from typing import Optional, List
import json


class CongressTradesFetcher:
    """Hämtar och analyserar kongressmedlemmars aktiehandel."""

    API_URL = "https://api.quiverquant.com/beta/live/congresstrading"

    def __init__(self):
        self.data = None
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=30)

    def _fetch_data(self) -> list:
        """Hämtar data från Quiver Quantitative API."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            response = requests.get(self.API_URL, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Fel vid hämtning av kongressdata: {e}")
            return []

    def refresh_data(self):
        """Hämtar färsk data från API."""
        print("Hämtar kongressdata från Quiver Quantitative...")
        self.data = self._fetch_data()
        self._cache_timestamp = datetime.now()
        print(f"  Hämtade {len(self.data)} transaktioner")

    def _ensure_data(self):
        """Ser till att vi har data (hämtar om det behövs eller cache har utgått)."""
        if self.data is None:
            self.refresh_data()
        elif self._cache_timestamp and datetime.now() - self._cache_timestamp > self._cache_duration:
            self.refresh_data()

    def get_recent_trades(self, days: int = 30, min_amount: str = "$1,001 -") -> list:
        """
        Hämtar senaste transaktionerna.

        Args:
            days: Antal dagar tillbaka att söka
            min_amount: Minsta transaktionsbelopp (ignoreras i denna implementation)

        Returns:
            Lista med transaktioner
        """
        self._ensure_data()

        if not self.data:
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        trades = []

        for trade in self.data:
            try:
                # Parse transaction date
                trade_date_str = trade.get("TransactionDate", "")
                if not trade_date_str:
                    continue

                trade_date = datetime.strptime(trade_date_str, "%Y-%m-%d")

                if trade_date >= cutoff_date:
                    # Map to our format
                    transaction_type = trade.get("Transaction", "")

                    trades.append({
                        "chamber": trade.get("House", ""),
                        "politician": trade.get("Representative", "Unknown"),
                        "party": trade.get("Party", ""),
                        "ticker": trade.get("Ticker", ""),
                        "asset": trade.get("Description", "") or trade.get("Ticker", ""),
                        "type": transaction_type,
                        "amount": trade.get("Range", ""),
                        "transaction_date": trade_date.isoformat(),
                        "disclosure_date": trade.get("ReportDate", ""),
                        "excess_return": trade.get("ExcessReturn"),
                        "price_change": trade.get("PriceChange"),
                    })
            except Exception as e:
                continue

        # Sortera efter datum (nyast först)
        trades.sort(key=lambda x: x.get("transaction_date", ""), reverse=True)

        return trades

    def get_trades_by_ticker(self, ticker: str, days: int = 90) -> list:
        """
        Hämtar alla transaktioner för en specifik aktie.

        Args:
            ticker: Aktiesymbol (t.ex. "AAPL", "MSFT")
            days: Antal dagar tillbaka

        Returns:
            Lista med transaktioner
        """
        all_trades = self.get_recent_trades(days=days)
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
        all_trades = self.get_recent_trades(days=days)
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
            if ticker and ticker != "--" and ticker != "N/A":
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
            if party == "D":
                party_counts["D"] += 1
            elif party == "R":
                party_counts["R"] += 1
            elif party == "I":
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
