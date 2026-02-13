"""
climate_agent.py - Marknadsklimat och ekonomisk kalender

Hämtar:
- Marknadsindex (OMX30, S&P 500, VIX) via yfinance
- Signalfördelning från interna aktieanalyser
- Ekonomiska events från DI:s kalender, Riksbanken och manuell JSON
"""

import json
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from pathlib import Path
from typing import List

import yfinance as yf


class ClimateAgent:
    """Hämtar marknadsklimat, index och ekonomiska events."""

    INDICES = [
        {"symbol": "^OMX", "name": "OMX Stockholm 30", "currency": "SEK"},
        {"symbol": "^GSPC", "name": "S&P 500", "currency": "USD"},
        {"symbol": "^VIX", "name": "VIX (Volatilitet)", "currency": "USD"},
    ]

    RIKSBANK_2026 = [
        {"date": "2026-01-29", "title": "Riksbanken räntebesked"},
        {"date": "2026-03-19", "title": "Riksbanken räntebesked"},
        {"date": "2026-05-07", "title": "Riksbanken räntebesked"},
        {"date": "2026-06-17", "title": "Riksbanken räntebesked"},
        {"date": "2026-08-20", "title": "Riksbanken räntebesked"},
        {"date": "2026-09-24", "title": "Riksbanken räntebesked"},
        {"date": "2026-11-04", "title": "Riksbanken räntebesked"},
        {"date": "2026-12-16", "title": "Riksbanken räntebesked"},
    ]

    DI_CALENDAR_URL = "https://www.di.se/kalendern/"

    def __init__(self):
        self._calendar_path = Path(__file__).parent.parent / "config" / "economic_calendar.json"

    def get_all_indices(self) -> list:
        """Hämtar aktuell data för OMX30, S&P 500 och VIX."""
        results = []
        for idx in self.INDICES:
            try:
                ticker = yf.Ticker(idx["symbol"])
                hist = ticker.history(period="5d")

                if hist.empty:
                    results.append({
                        "symbol": idx["symbol"],
                        "name": idx["name"],
                        "current_price": 0.0,
                        "change_percent": 0.0,
                        "trend": "neutral",
                        "currency": idx["currency"],
                    })
                    continue

                current = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2] if len(hist) > 1 else current
                change_pct = ((current - prev) / prev) * 100 if prev != 0 else 0.0

                if change_pct > 0.3:
                    trend = "up"
                elif change_pct < -0.3:
                    trend = "down"
                else:
                    trend = "neutral"

                results.append({
                    "symbol": idx["symbol"],
                    "name": idx["name"],
                    "current_price": round(float(current), 2),
                    "change_percent": round(float(change_pct), 2),
                    "trend": trend,
                    "currency": idx["currency"],
                })
            except Exception as e:
                print(f"Fel vid hämtning av {idx['symbol']}: {e}")
                results.append({
                    "symbol": idx["symbol"],
                    "name": idx["name"],
                    "current_price": 0.0,
                    "change_percent": 0.0,
                    "trend": "neutral",
                    "currency": idx["currency"],
                })

        return results

    def aggregate_internal_signals(self, stock_data_list: list) -> dict:
        """
        Räknar BUY/SELL/WATCH/HOLD/AVOID-fördelning från aktiedata.

        Args:
            stock_data_list: Lista med aktieanalys-dicts som har 'signal' och 'stock_data'
        """
        buy = sell = watch = hold = avoid = 0
        changes = []
        high_volume = 0

        for stock in stock_data_list:
            signal = stock.get("signal", {})
            score = signal.get("score", 0)

            # Klassificera med samma logik som briefing_engine
            if score >= 2:
                buy += 1
            elif score == 1:
                watch += 1
            elif score == 0:
                hold += 1
            elif score == -1:
                watch += 1
            else:
                avoid += 1

            # Samla förändringsdata
            data = stock.get("stock_data", {})
            change = data.get("change_percent", 0)
            if change and isinstance(change, (int, float)):
                changes.append(change)

            volume_ratio = data.get("volume_vs_avg", 1)
            if isinstance(volume_ratio, (int, float)) and volume_ratio > 1.5:
                high_volume += 1

        total = buy + sell + watch + hold + avoid
        avg_change = sum(changes) / len(changes) if changes else 0.0

        if buy > avoid and avg_change > 0.5:
            sentiment = "bullish"
        elif avoid > buy and avg_change < -0.5:
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        return {
            "signal_distribution": {
                "total_stocks": total,
                "buy": buy,
                "sell": sell,
                "watch": watch,
                "hold": hold,
                "avoid": avoid,
            },
            "avg_change_percent": round(avg_change, 2),
            "high_volume_count": high_volume,
            "overall_sentiment": sentiment,
        }

    # Mapping av DI:s typ-kolumn till kategori
    DI_TYPE_MAP = {
        "årsrapport": "earnings_report",
        "kvartalsrapport": "earnings_report",
        "delårsrapport": "earnings_report",
        "halvårsrapport": "earnings_report",
        "bokslutskommuniké": "earnings_report",
        "årsstämma": "annual_meeting",
        "extrainsatt årsstämma": "annual_meeting",
        "utdelning": "dividend",
    }

    def scrape_di_calendar(self) -> list:
        """
        Scrapar DI:s företagskalender (rapporter, stämmor, utdelningar).
        Strukturen är table.instrument-table med tr/td-rader.
        Returnerar tom lista vid fel (graceful fallback).
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
            }
            response = requests.get(self.DI_CALENDAR_URL, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            events = []

            # DI har flera instrument-table: Rapporter, Stämmor, Utdelningar
            for table in soup.select("table.instrument-table"):
                # Identifiera kolumner från headers
                thead = table.select_one("thead")
                if not thead:
                    continue

                col_names = [th.get_text(strip=True).lower() for th in thead.select("th")]

                # Rapporter/Stämmor: [datum, bolag, typ]
                # Utdelningar: [x-datum, aktie, utdelning, typ, utdelningsdatum]
                is_dividend = "utdelning" in " ".join(col_names) or "x-datum" in " ".join(col_names)

                for row in table.select("tbody tr"):
                    cells = row.select("td")
                    if len(cells) < 3:
                        continue

                    cell_texts = [td.get_text(strip=True) for td in cells]

                    if is_dividend:
                        # Utdelningstabell: x-datum, aktie, belopp, typ, utd.datum
                        event_date = cell_texts[0]
                        company = cell_texts[1]
                        amount = cell_texts[2] if len(cell_texts) > 2 else ""
                        event_type = cell_texts[3] if len(cell_texts) > 3 else "Utdelning"
                        title = f"{company} - {event_type} ({amount} SEK)"
                        category = "dividend"
                    else:
                        # Rapport/Stämma-tabell: datum, bolag, typ
                        event_date = cell_texts[0]
                        company = cell_texts[1]
                        event_type = cell_texts[2] if len(cell_texts) > 2 else ""
                        title = f"{company} - {event_type}"
                        category = self.DI_TYPE_MAP.get(event_type.lower(), "earnings_report")

                    # Validera datum
                    try:
                        parsed_date = self._parse_date(event_date)
                    except ValueError:
                        continue

                    event_id = hashlib.md5(f"di-{parsed_date}-{company}".encode()).hexdigest()[:12]

                    events.append({
                        "id": f"di-{event_id}",
                        "date": parsed_date,
                        "title": title,
                        "category": category,
                        "source": "DI",
                        "impact": "low",
                    })

            return events

        except Exception as e:
            print(f"Fel vid scraping av DI-kalender: {e}")
            return []

    def _parse_date(self, date_str: str) -> str:
        """Försök tolka olika datumformat till YYYY-MM-DD."""
        date_str = date_str.strip()

        # ISO-format (2026-01-15)
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%d %B %Y", "%d %b %Y"):
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue

        # Svenska månadsnamn
        swedish_months = {
            "januari": "01", "februari": "02", "mars": "03", "april": "04",
            "maj": "05", "juni": "06", "juli": "07", "augusti": "08",
            "september": "09", "oktober": "10", "november": "11", "december": "12",
        }
        lower = date_str.lower()
        for month_name, month_num in swedish_months.items():
            if month_name in lower:
                parts = lower.replace(month_name, "").strip().split()
                day = parts[0] if parts else "1"
                year = parts[1] if len(parts) > 1 else str(datetime.now().year)
                return f"{year}-{month_num}-{int(day):02d}"

        raise ValueError(f"Kunde inte tolka datum: {date_str}")

    def _categorize_event(self, title: str) -> str:
        """Kategorisera event baserat på titel."""
        title_lower = title.lower()

        if any(w in title_lower for w in ["ränta", "reporänta", "styrränta", "riksbank", "fed", "ecb"]):
            return "rate_decision"
        if any(w in title_lower for w in ["bnp", "gdp", "tillväxt"]):
            return "gdp"
        if any(w in title_lower for w in ["arbetsmarknad", "arbetslöshet", "sysselsättning", "jobb"]):
            return "employment"
        if any(w in title_lower for w in ["rapport", "resultat", "vinst", "earnings"]):
            return "earnings_season"
        if any(w in title_lower for w in ["inflation", "kpi", "cpi", "pmi", "index"]):
            return "macro_data"

        return "macro_data"

    def get_riksbank_events(self) -> list:
        """Returnerar kända Riksbanken-datum för 2026."""
        events = []
        for rb in self.RIKSBANK_2026:
            event_id = hashlib.md5(f"rb-{rb['date']}".encode()).hexdigest()[:12]
            events.append({
                "id": f"rb-{event_id}",
                "date": rb["date"],
                "title": rb["title"],
                "category": "rate_decision",
                "source": "Riksbanken",
                "impact": "high",
            })
        return events

    def get_manual_events(self) -> list:
        """Läser events från manuell JSON-kalender."""
        try:
            with open(self._calendar_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("events", [])
        except Exception as e:
            print(f"Fel vid läsning av manuell kalender: {e}")
            return []

    def get_all_events(self, di_events: list = None) -> list:
        """
        Slår ihop events från alla tre källor, deduplicerar och sorterar.

        Args:
            di_events: Förscrapade DI-events (för att kunna cacha separat)
        """
        all_events = []

        # 1. DI-events
        if di_events is not None:
            all_events.extend(di_events)
        else:
            all_events.extend(self.scrape_di_calendar())

        # 2. Riksbanken
        all_events.extend(self.get_riksbank_events())

        # 3. Manuella events
        all_events.extend(self.get_manual_events())

        # Deduplicera baserat på datum + liknande titel
        seen = set()
        unique_events = []
        for event in all_events:
            key = f"{event['date']}-{event.get('title', '').lower()[:30]}"
            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        # Räkna dagar till varje event och markera aktiva
        today = date.today()
        for event in unique_events:
            try:
                event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
                event["days_until"] = (event_date - today).days
                event["is_active"] = -1 <= event["days_until"] <= 7
            except (ValueError, KeyError):
                event["days_until"] = 999
                event["is_active"] = False

        # Sortera på datum, visa bara framtida och nyligen passerade events (-7 dagar)
        unique_events = [e for e in unique_events if e["days_until"] >= -7]
        unique_events.sort(key=lambda e: e["date"])

        return unique_events
