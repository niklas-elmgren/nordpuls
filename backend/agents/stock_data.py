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
    
    def get_technical_analysis(self, symbol: str) -> dict:
        """
        Beräknar tekniska indikatorer för daytrading.

        Returns:
            Dict med RSI, stöd/motstånd, entry/stoploss/target
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")

            if len(hist) < 14:
                return {"error": "För lite data för teknisk analys"}

            close = hist['Close']
            high = hist['High']
            low = hist['Low']
            volume = hist['Volume']
            current_price = close.iloc[-1]

            # === RSI (14 perioder) ===
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]

            # === Stöd och Motstånd (senaste 20 dagar) ===
            recent_high = high.tail(20).max()
            recent_low = low.tail(20).min()

            # Hitta lokala toppar/bottnar för bättre nivåer
            resistance_levels = []
            support_levels = []

            for i in range(2, len(high) - 2):
                # Lokal topp
                if high.iloc[i] > high.iloc[i-1] and high.iloc[i] > high.iloc[i+1]:
                    resistance_levels.append(high.iloc[i])
                # Lokal botten
                if low.iloc[i] < low.iloc[i-1] and low.iloc[i] < low.iloc[i+1]:
                    support_levels.append(low.iloc[i])

            # Närmaste motstånd över current price
            resistance = min([r for r in resistance_levels if r > current_price], default=recent_high)
            # Närmaste stöd under current price
            support = max([s for s in support_levels if s < current_price], default=recent_low)

            # === Volymanalys ===
            avg_volume = volume.tail(20).mean()
            current_volume = volume.iloc[-1]
            volume_spike = current_volume / avg_volume if avg_volume > 0 else 1

            # === ATR (Average True Range) för volatilitet ===
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]

            # === Entry, Stoploss, Target för daytrading ===
            # Entry: Aktuell kurs (eller lite under vid pullback)
            entry_price = round(current_price, 2)

            # Stoploss: 2x ATR under entry, eller strax under support
            atr_stop = current_price - (2 * atr)
            support_stop = support * 0.99  # 1% under support
            stoploss = round(max(atr_stop, support_stop), 2)

            # Target: 3x risk (risk/reward 1:3) eller motstånd
            risk = current_price - stoploss
            atr_target = current_price + (3 * risk)
            target = round(min(atr_target, resistance * 0.99), 2)  # 1% under resistance

            # Garantera rimliga nivåer
            if stoploss >= current_price:
                stoploss = round(current_price * 0.96, 2)  # -4% fallback
            if target <= current_price:
                target = round(current_price * 1.05, 2)  # +5% fallback

            # === Beräkna procent ===
            stoploss_pct = round(((stoploss - current_price) / current_price) * 100, 1)
            target_pct = round(((target - current_price) / current_price) * 100, 1)

            # === Tekniska signaler ===
            signals = []

            if current_rsi < 30:
                signals.append("RSI översåld (<30) - potential för studs")
            elif current_rsi > 70:
                signals.append("RSI överköpt (>70) - varning")
            elif 40 <= current_rsi <= 60:
                signals.append(f"RSI neutral ({current_rsi:.0f})")

            if volume_spike > 1.5:
                signals.append(f"Volymspike: {volume_spike:.1f}x genomsnitt")

            if current_price > resistance * 0.98:
                signals.append(f"Testar motstånd vid {resistance:.2f}")

            if current_price < support * 1.02:
                signals.append(f"Nära stöd vid {support:.2f}")

            # Trend (enkel: över/under 20-dagars MA)
            ma20 = close.tail(20).mean()
            if current_price > ma20:
                signals.append("Över 20-dagars MA (upptrend)")
            else:
                signals.append("Under 20-dagars MA (nedtrend)")

            return {
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "rsi": round(current_rsi, 1),
                "support": round(support, 2),
                "resistance": round(resistance, 2),
                "atr": round(atr, 2),
                "volume_spike": round(volume_spike, 2),
                "entry_price": entry_price,
                "stoploss": stoploss,
                "stoploss_pct": stoploss_pct,
                "target": target,
                "target_pct": target_pct,
                "signals": signals,
                "ma20": round(ma20, 2),
                "trend": "up" if current_price > ma20 else "down"
            }

        except Exception as e:
            return {"error": str(e), "symbol": symbol}

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
