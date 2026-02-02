"""
stock_data.py - Hämtar aktiedata från Yahoo Finance

Använder yfinance för att hämta:
- Aktuell kurs och daglig förändring
- Volym (jämfört med genomsnitt)
- Historisk data för enkel teknisk analys
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd


class StockDataFetcher:
    """Hämtar och bearbetar aktiedata."""
    
    def __init__(self):
        self.cache = {}
    
    def get_stock_info(self, symbol: str) -> dict:
        """
        Hämtar aktuell info för en aktie.
        
        Args:
            symbol: Aktiesymbol (t.ex. "VOLV-B.ST" för Volvo B på Stockholmsbörsen)
            
        Returns:
            Dict med kursinformation
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return {"error": f"Ingen data hittades för {symbol}"}
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # Volymanalys
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            return {
                "symbol": symbol,
                "name": info.get("shortName", symbol),
                "current_price": round(current_price, 2),
                "change_percent": round(change_pct, 2),
                "volume": int(current_volume),
                "volume_vs_avg": round(volume_ratio, 2),
                "high_52w": info.get("fiftyTwoWeekHigh"),
                "low_52w": info.get("fiftyTwoWeekLow"),
                "market_cap": info.get("marketCap"),
                "currency": info.get("currency", "SEK"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "symbol": symbol}
    
    def get_price_history(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        Hämtar prishistorik för teknisk analys.
        
        Args:
            symbol: Aktiesymbol
            days: Antal dagar tillbaka
            
        Returns:
            DataFrame med OHLCV-data
        """
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = ticker.history(start=start_date, end=end_date)
            return hist
            
        except Exception as e:
            print(f"Fel vid hämtning av historik för {symbol}: {e}")
            return pd.DataFrame()
    
    def check_unusual_activity(self, symbol: str) -> dict:
        """
        Kontrollerar om det finns ovanlig aktivitet (volym/prisrörelse).
        
        Returns:
            Dict med flaggor för ovanlig aktivitet
        """
        info = self.get_stock_info(symbol)
        
        if "error" in info:
            return info
        
        flags = []
        
        # Hög volym = mer än 1.5x genomsnittet
        if info.get("volume_vs_avg", 0) > 1.5:
            flags.append(f"🔥 Hög volym: {info['volume_vs_avg']}x genomsnittet")
        
        # Stor kursrörelse = mer än 3%
        change = abs(info.get("change_percent", 0))
        if change > 3:
            direction = "📈" if info["change_percent"] > 0 else "📉"
            flags.append(f"{direction} Stor rörelse: {info['change_percent']:+.2f}%")
        
        # Nära 52-veckors high/low
        price = info.get("current_price", 0)
        high = info.get("high_52w")
        low = info.get("low_52w")
        
        if high and price > high * 0.95:
            flags.append("🎯 Nära 52-veckors högsta")
        if low and price < low * 1.05:
            flags.append("⚠️ Nära 52-veckors lägsta")
        
        return {
            "symbol": symbol,
            "flags": flags,
            "has_unusual_activity": len(flags) > 0,
            "data": info
        }


# Enkel test
if __name__ == "__main__":
    fetcher = StockDataFetcher()
    
    # Testa med Volvo B
    print("Hämtar data för Volvo B...")
    result = fetcher.get_stock_info("VOLV-B.ST")
    print(result)
    
    print("\nKontrollerar ovanlig aktivitet...")
    activity = fetcher.check_unusual_activity("VOLV-B.ST")
    print(activity)
