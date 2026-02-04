"""
briefing_engine.py - Genererar morgon- och kvällsbriefingar

Morgon (08:15 CET): Analys inför börsöppning, fokus på köpmöjligheter
Kväll (17:15 CET): Analys inför börsstängning, fokus på riskhantering
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from .research_agent import ResearchAgent
from .stock_data import StockDataFetcher


class BriefingEngine:
    """Genererar strukturerade morgon- och kvällsbriefingar."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "config" / "config.json")
        self.config_path = config_path
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        # Load all OMX Stockholm stocks
        omx_path = Path(__file__).parent.parent / "config" / "omx_stockholm.json"
        with open(omx_path, "r", encoding="utf-8") as f:
            self.omx_data = json.load(f)

        # Path for storing daily rocket picks
        self.rockets_path = Path(__file__).parent.parent / "data" / "daily_rockets.json"
        self.rockets_path.parent.mkdir(parents=True, exist_ok=True)

        # Path for rocket history
        self.rockets_history_path = Path(__file__).parent.parent / "data" / "rockets_history.json"

    def _get_agent(self) -> ResearchAgent:
        return ResearchAgent(self.config_path)

    def _classify_recommendation(self, score: int, briefing_type: str) -> tuple:
        """Classify signal score into action and confidence."""
        if briefing_type == "morning":
            if score >= 2:
                return "BUY", "HIGH"
            elif score == 1:
                return "WATCH", "MEDIUM"
            elif score == 0:
                return "HOLD", "LOW"
            elif score == -1:
                return "WATCH", "MEDIUM"
            else:
                return "AVOID", "HIGH"
        else:  # evening
            if score >= 2:
                return "HOLD", "HIGH"
            elif score == 1:
                return "HOLD", "MEDIUM"
            elif score == 0:
                return "HOLD", "LOW"
            elif score == -1:
                return "WATCH", "MEDIUM"
            else:
                return "SELL", "HIGH"

    def _get_market_status(self) -> str:
        """Determine current market status based on Stockholm time."""
        now = datetime.now()
        hour = now.hour
        if hour < 9:
            return "pre_open"
        elif hour < 17 or (hour == 17 and now.minute < 30):
            return "open"
        else:
            return "closed"

    def _select_rocket_picks(self, analyses: list) -> list:
        """
        Välj 2 'kursraketer' för daytrading baserat på teknisk analys.

        Kriterier:
        - Positiv signal score
        - Tekniska indikatorer (RSI, volym, trend)
        - Entry/stoploss/target beräknas automatiskt
        """
        stock_fetcher = StockDataFetcher()

        # Filtrera svenska aktier med positiva signaler och pris > 0
        candidates = [
            a for a in analyses
            if a["symbol"].endswith(".ST")
            and a["signal"]["score"] >= 0
            and a["stock_data"].get("current_price", 0) > 0
        ]

        # Poängsätt kandidater
        scored = []
        for a in candidates:
            symbol = a["symbol"]
            score = a["signal"]["score"] * 2  # Bas från signal

            # Försök hämta teknisk analys
            ta = stock_fetcher.get_technical_analysis(symbol)
            has_ta = "error" not in ta

            if has_ta:
                # === Teknisk poängsättning ===
                rsi = ta.get("rsi", 50)
                if rsi < 35:
                    score += 3
                elif rsi < 45:
                    score += 1
                elif rsi > 70:
                    score -= 2

                vol_spike = ta.get("volume_spike", 1)
                if vol_spike > 2.0:
                    score += 2
                elif vol_spike > 1.5:
                    score += 1

                if ta.get("trend") == "up":
                    score += 1

                target_pct = ta.get("target_pct", 0)
                stoploss_pct = abs(ta.get("stoploss_pct", -4))
                if target_pct > 0 and stoploss_pct > 0:
                    rr_ratio = target_pct / stoploss_pct
                    if rr_ratio >= 2:
                        score += 1
            else:
                # Fallback: använd enkel volymdata
                vol_ratio = a["stock_data"].get("volume_vs_avg", 1)
                if vol_ratio > 2.0:
                    score += 2
                elif vol_ratio > 1.5:
                    score += 1

            # Bonus för positivt nyhetssentiment
            news_score = a.get("news_summary", {}).get("score", 0)
            if news_score > 0:
                score += 1

            # Bonus för kongressköp
            congress = a.get("congress_activity", {})
            if congress.get("has_congress_activity") and congress.get("buys", 0) > congress.get("sells", 0):
                score += 1

            tech_signals = ta.get("signals", []) if has_ta else []

            scored.append({
                "analysis": a,
                "technical": ta if has_ta else None,
                "rocket_score": score,
                "tech_signals": tech_signals
            })

        # Sortera efter poäng och ta topp 2
        scored.sort(key=lambda x: x["rocket_score"], reverse=True)

        rockets = []
        for item in scored[:2]:
            a = item["analysis"]
            ta = item["technical"]
            price = a["stock_data"].get("current_price", 0)

            if ta:
                # Med teknisk analys
                rockets.append({
                    "symbol": a["symbol"],
                    "name": a["name"],
                    "morning_price": ta.get("current_price", price),
                    "entry_price": ta.get("entry_price", price),
                    "stoploss": ta.get("stoploss", round(price * 0.96, 2)),
                    "stoploss_pct": ta.get("stoploss_pct", -4),
                    "target": ta.get("target", round(price * 1.05, 2)),
                    "target_pct": ta.get("target_pct", 5),
                    "rsi": ta.get("rsi", 50),
                    "support": ta.get("support", 0),
                    "resistance": ta.get("resistance", 0),
                    "volume_spike": ta.get("volume_spike", 1),
                    "trend": ta.get("trend", "neutral"),
                    "signal_score": a["signal"]["score"],
                    "rocket_score": item["rocket_score"],
                    "reasons": a["signal"]["reasons"][:2],
                    "tech_signals": item["tech_signals"][:3],
                    "news_sentiment": a.get("news_summary", {}).get("sentiment", "neutral"),
                    "pick_time": datetime.now().isoformat(),
                })
            else:
                # Utan teknisk analys - enklare format
                rockets.append({
                    "symbol": a["symbol"],
                    "name": a["name"],
                    "morning_price": price,
                    "entry_price": price,
                    "stoploss": round(price * 0.96, 2),
                    "stoploss_pct": -4,
                    "target": round(price * 1.05, 2),
                    "target_pct": 5,
                    "rsi": None,
                    "support": None,
                    "resistance": None,
                    "volume_spike": a["stock_data"].get("volume_vs_avg", 1),
                    "trend": "neutral",
                    "signal_score": a["signal"]["score"],
                    "rocket_score": item["rocket_score"],
                    "reasons": a["signal"]["reasons"][:2],
                    "tech_signals": [],
                    "news_sentiment": a.get("news_summary", {}).get("sentiment", "neutral"),
                    "pick_time": datetime.now().isoformat(),
                })

        return rockets

    def _save_rocket_picks(self, rockets: list):
        """Spara dagens raketval för uppföljning på kvällen."""
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "picks": rockets,
            "generated_at": datetime.now().isoformat()
        }
        with open(self.rockets_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_rocket_picks(self) -> dict:
        """Ladda morgonens raketval."""
        if not self.rockets_path.exists():
            return None

        with open(self.rockets_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Kontrollera att det är från idag
        if data.get("date") != datetime.now().strftime("%Y-%m-%d"):
            return None

        return data

    def _load_rockets_history(self) -> list:
        """Ladda rakethistorik."""
        if not self.rockets_history_path.exists():
            return []

        with open(self.rockets_history_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_rockets_history(self, history: list):
        """Spara rakethistorik."""
        with open(self.rockets_history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def _add_to_history(self, rocket_results: list):
        """Lägg till dagens raketresultat i historiken."""
        if not rocket_results:
            return

        history = self._load_rockets_history()
        today = datetime.now().strftime("%Y-%m-%d")

        # Kolla om vi redan har data för idag
        existing_idx = next((i for i, h in enumerate(history) if h["date"] == today), None)

        day_entry = {
            "date": today,
            "rockets": [],
            "summary": {
                "total_picks": len(rocket_results),
                "winners": 0,
                "losers": 0,
                "total_return_percent": 0,
            }
        }

        total_return = 0
        for r in rocket_results:
            change = r.get("day_change_percent", 0)
            if change >= 0:
                day_entry["summary"]["winners"] += 1
            else:
                day_entry["summary"]["losers"] += 1
            total_return += change

            day_entry["rockets"].append({
                "symbol": r["symbol"],
                "name": r["name"],
                "morning_price": r["morning_price"],
                "evening_price": r.get("current_price", 0),
                "change_percent": change,
                "status": r.get("status", "UNKNOWN"),
                "recommendation": r.get("recommendation", ""),
            })

        day_entry["summary"]["total_return_percent"] = round(total_return, 2)
        day_entry["summary"]["avg_return_percent"] = round(total_return / len(rocket_results), 2) if rocket_results else 0

        if existing_idx is not None:
            history[existing_idx] = day_entry
        else:
            history.append(day_entry)

        # Sortera efter datum (nyast först) och behåll max 90 dagar
        history.sort(key=lambda x: x["date"], reverse=True)
        history = history[:90]

        self._save_rockets_history(history)
        print(f"Sparade raketresultat för {today} i historiken")

    def get_rockets_history(self, days: int = 30) -> dict:
        """
        Hämta rakethistorik med sammanfattande statistik.

        Args:
            days: Antal dagar att hämta

        Returns:
            Dict med historik och statistik
        """
        history = self._load_rockets_history()[:days]

        if not history:
            return {
                "history": [],
                "stats": {
                    "total_picks": 0,
                    "total_winners": 0,
                    "total_losers": 0,
                    "win_rate": 0,
                    "avg_return": 0,
                    "best_pick": None,
                    "worst_pick": None,
                }
            }

        # Beräkna övergripande statistik
        total_picks = 0
        total_winners = 0
        total_losers = 0
        all_returns = []
        best_pick = None
        worst_pick = None

        for day in history:
            for rocket in day.get("rockets", []):
                total_picks += 1
                change = rocket.get("change_percent", 0)
                all_returns.append(change)

                if change >= 0:
                    total_winners += 1
                else:
                    total_losers += 1

                if best_pick is None or change > best_pick["change_percent"]:
                    best_pick = {**rocket, "date": day["date"]}
                if worst_pick is None or change < worst_pick["change_percent"]:
                    worst_pick = {**rocket, "date": day["date"]}

        avg_return = sum(all_returns) / len(all_returns) if all_returns else 0
        win_rate = (total_winners / total_picks * 100) if total_picks > 0 else 0

        return {
            "history": history,
            "stats": {
                "total_days": len(history),
                "total_picks": total_picks,
                "total_winners": total_winners,
                "total_losers": total_losers,
                "win_rate": round(win_rate, 1),
                "avg_return": round(avg_return, 2),
                "total_return": round(sum(all_returns), 2),
                "best_pick": best_pick,
                "worst_pick": worst_pick,
            }
        }

    def _evaluate_rocket_performance(self, picks: list, current_analyses: dict) -> list:
        """
        Utvärdera hur morgonens raketer har presterat.

        Returns lista med resultat och rekommendationer.
        """
        results = []

        for pick in picks:
            symbol = pick["symbol"]
            morning_price = pick["morning_price"]

            # Hitta aktuell analys
            current = current_analyses.get(symbol)
            if not current:
                results.append({
                    **pick,
                    "status": "NO_DATA",
                    "recommendation": "OKÄND",
                    "message": "Kunde inte hämta aktuell data"
                })
                continue

            current_price = current["stock_data"].get("current_price", 0)
            if current_price <= 0 or morning_price <= 0:
                continue

            # Beräkna dagsförändring
            day_change = ((current_price - morning_price) / morning_price) * 100

            # Bestäm rekommendation
            if day_change >= 3.0:
                recommendation = "SÄLJ - TA HEM VINST"
                status = "TARGET_HIT"
                message = f"🎯 Upp {day_change:.1f}% - Ta hem vinsten!"
            elif day_change >= 1.5:
                recommendation = "BEHÅLL ELLER SÄLJ HALVA"
                status = "PROFIT"
                message = f"📈 Upp {day_change:.1f}% - Bra dag, överväg att sälja halva positionen"
            elif day_change >= 0:
                recommendation = "BEHÅLL"
                status = "FLAT"
                message = f"➡️ Oförändrad ({day_change:+.1f}%) - Behåll till imorgon"
            elif day_change >= -2.0:
                recommendation = "BEHÅLL"
                status = "SMALL_LOSS"
                message = f"📉 Ned {day_change:.1f}% - Mindre dipp, behåll"
            else:
                recommendation = "SÄLJ - STOPLOSS"
                status = "STOP_LOSS"
                message = f"🛑 Ned {day_change:.1f}% - Överväg att ta förlusten"

            results.append({
                **pick,
                "current_price": current_price,
                "day_change_percent": round(day_change, 2),
                "status": status,
                "recommendation": recommendation,
                "message": message
            })

        return results

    def _build_summary(self, analyses: list, briefing_type: str) -> str:
        """Build a human-readable summary."""
        positive = sum(1 for a in analyses if a["signal"]["score"] > 0)
        negative = sum(1 for a in analyses if a["signal"]["score"] < 0)
        neutral = len(analyses) - positive - negative

        date_str = datetime.now().strftime("%Y-%m-%d")

        if briefing_type == "morning":
            return (
                f"Morgonbrief {date_str}. "
                f"Av {len(analyses)} bevakade aktier visar "
                f"{positive} positiva signaler, "
                f"{negative} negativa och "
                f"{neutral} neutrala. "
                f"Analysen baseras på kursdata, nyhetssentiment och kongressaktivitet."
            )
        else:
            return (
                f"Kvällsbrief {date_str}. "
                f"Dagens handel visar "
                f"{positive} aktier med positiv utveckling, "
                f"{negative} med negativ och "
                f"{neutral} utan tydlig riktning. "
                f"Nedan följer rekommendationer inför morgondagen."
            )

    def _get_all_stocks(self) -> list:
        """Get all stocks from OMX Stockholm config."""
        stocks_config = self.omx_data.get("stocks", {})
        all_stocks = []

        # Add Swedish stocks (Large + Mid Cap for briefings - most liquid)
        for stock in stocks_config.get("large_cap", []):
            all_stocks.append({**stock, "market": "OMX Stockholm"})
        for stock in stocks_config.get("mid_cap", []):
            all_stocks.append({**stock, "market": "OMX Stockholm"})

        # Add First North stocks
        for stock in stocks_config.get("first_north", []):
            all_stocks.append({**stock, "market": "First North"})

        # Add US watchlist for congress tracking
        for stock in stocks_config.get("us_watchlist", []):
            all_stocks.append(stock)

        return all_stocks

    def _analyze_stock(self, agent: ResearchAgent, stock: dict) -> dict:
        """Analyze a single stock with error handling."""
        try:
            return agent.analyze_stock(stock["symbol"], stock["name"])
        except Exception as e:
            return {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "stock_data": {"error": str(e)},
                "signal": {"type": "NEUTRAL", "score": 0, "reasons": [f"Fel: {e}"]},
                "news_summary": {"sentiment": "no_data", "count": 0, "score": 0},
                "congress_activity": {},
                "unusual_activity": [],
                "recent_headlines": [],
            }

    def generate_briefing(self, briefing_type: str = "morning") -> dict:
        """
        Generate a briefing.

        Args:
            briefing_type: "morning" or "evening"

        Returns:
            Complete briefing dict
        """
        agent = self._get_agent()
        all_stocks = self._get_all_stocks()

        print(f"Genererar {briefing_type} briefing för {len(all_stocks)} aktier...")

        # Analyze all stocks in parallel for speed
        analyses = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(self._analyze_stock, agent, stock): stock
                for stock in all_stocks
            }
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        analyses.append(result)
                except Exception as e:
                    stock = futures[future]
                    analyses.append({
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "stock_data": {"error": str(e)},
                        "signal": {"type": "NEUTRAL", "score": 0, "reasons": [f"Fel: {e}"]},
                        "news_summary": {"sentiment": "no_data", "count": 0, "score": 0},
                        "congress_activity": {},
                        "unusual_activity": [],
                        "recent_headlines": [],
                    })

        print(f"Analyserade {len(analyses)} aktier")

        # Separate Swedish and US stocks
        swedish = [a for a in analyses if a["symbol"].endswith(".ST")]
        us = [a for a in analyses if not a["symbol"].endswith(".ST")]

        # Sort by signal score
        if briefing_type == "morning":
            swedish.sort(key=lambda x: x["signal"]["score"], reverse=True)
            us.sort(key=lambda x: x["signal"]["score"], reverse=True)
        else:
            swedish.sort(key=lambda x: x["signal"]["score"])
            us.sort(key=lambda x: x["signal"]["score"])

        all_sorted = swedish + us

        # Build recommendations
        recommendations = []
        for a in all_sorted:
            score = a["signal"]["score"]
            action, confidence = self._classify_recommendation(score, briefing_type)

            recommendations.append({
                "symbol": a["symbol"],
                "name": a["name"],
                "action": action,
                "confidence": confidence,
                "price": a["stock_data"].get("current_price", 0),
                "change_percent": a["stock_data"].get("change_percent", 0),
                "reasons": a["signal"]["reasons"],
                "news_sentiment": a.get("news_summary", {}).get("sentiment", "neutral"),
                "congress_signal": a.get("congress_activity", {}).get("sentiment"),
            })

        # Extract highlights
        highlights = []
        for a in all_sorted:
            if a["signal"]["type"] != "NEUTRAL ➖":
                highlights.append({
                    "stock": a["name"],
                    "signal": a["signal"]["type"],
                    "reasons": a["signal"]["reasons"],
                })
            for flag in a.get("unusual_activity", []):
                highlights.append({
                    "stock": a["name"],
                    "alert": flag,
                })

        # Get notable congress activity
        congress_notable = []
        for a in all_sorted:
            ca = a.get("congress_activity", {})
            if ca.get("has_congress_activity"):
                congress_notable.append({
                    "ticker": ca.get("ticker", a["symbol"]),
                    "sentiment": ca.get("sentiment", ""),
                    "description": ca.get("sentiment_description", ""),
                    "total_trades": ca.get("total_trades", 0),
                })

        # === DAGENS RAKETER ===
        rocket_picks = []
        rocket_followup = []

        if briefing_type == "morning":
            # Välj och spara dagens raketer
            rocket_picks = self._select_rocket_picks(all_sorted)
            if rocket_picks:
                self._save_rocket_picks(rocket_picks)
                print(f"Valde {len(rocket_picks)} raketer: {[r['symbol'] for r in rocket_picks]}")

        elif briefing_type == "evening":
            # Följ upp morgonens raketer
            morning_data = self._load_rocket_picks()
            if morning_data and morning_data.get("picks"):
                # Skapa lookup för aktuella analyser
                analyses_lookup = {a["symbol"]: a for a in all_sorted}
                rocket_followup = self._evaluate_rocket_performance(
                    morning_data["picks"],
                    analyses_lookup
                )
                print(f"Följde upp {len(rocket_followup)} raketer")

                # Spara till historik
                self._add_to_history(rocket_followup)

        return {
            "type": briefing_type,
            "generated_at": datetime.now().isoformat(),
            "market_status": self._get_market_status(),
            "summary": self._build_summary(all_sorted, briefing_type),
            "highlights": highlights,
            "recommendations": recommendations,
            "congress_notable": congress_notable,
            "rocket_picks": rocket_picks,  # Morgonens raketval
            "rocket_followup": rocket_followup,  # Kvällens uppföljning
            "disclaimer": (
                "OBS: Detta är inte finansiell rådgivning. Informationen är baserad på "
                "automatiserad analys och ska inte användas som enda underlag för "
                "investeringsbeslut. Gör alltid din egen research."
            ),
        }
