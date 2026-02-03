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
        Välj 1-2 'kursraketer' baserat på starkaste köpsignaler.

        Kriterier:
        - Signal score >= 2 (stark köpsignal)
        - Hög volym vs genomsnitt (momentum)
        - Positivt nyhetssentiment
        - Svenska aktier prioriteras (handlas under dagen)
        """
        # Filtrera svenska aktier med starka signaler
        candidates = [
            a for a in analyses
            if a["symbol"].endswith(".ST")
            and a["signal"]["score"] >= 1
            and a["stock_data"].get("current_price", 0) > 0
        ]

        # Poängsätt kandidater
        scored = []
        for a in candidates:
            score = a["signal"]["score"] * 2  # Bas från signal

            # Bonus för hög volym (momentum)
            volume_ratio = a["stock_data"].get("volume_vs_avg", 1)
            if volume_ratio > 1.5:
                score += 1
            if volume_ratio > 2.0:
                score += 1

            # Bonus för positivt nyhetssentiment
            news_score = a.get("news_summary", {}).get("score", 0)
            if news_score > 0:
                score += 1

            # Bonus för kongressköp (om tillgängligt)
            congress = a.get("congress_activity", {})
            if congress.get("has_congress_activity") and congress.get("buys", 0) > congress.get("sells", 0):
                score += 1

            scored.append({
                "analysis": a,
                "rocket_score": score
            })

        # Sortera efter poäng och ta topp 2
        scored.sort(key=lambda x: x["rocket_score"], reverse=True)

        rockets = []
        for item in scored[:2]:
            a = item["analysis"]
            rockets.append({
                "symbol": a["symbol"],
                "name": a["name"],
                "morning_price": a["stock_data"].get("current_price", 0),
                "signal_score": a["signal"]["score"],
                "rocket_score": item["rocket_score"],
                "reasons": a["signal"]["reasons"][:3],  # Top 3 skäl
                "volume_vs_avg": a["stock_data"].get("volume_vs_avg", 1),
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
