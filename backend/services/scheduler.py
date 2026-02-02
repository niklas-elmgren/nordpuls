"""
APScheduler setup for morning/evening briefings.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import json
from pathlib import Path

from agents.briefing_engine import BriefingEngine

# In-memory store for generated briefings
_briefing_store: dict = {
    "morning": None,
    "evening": None,
    "history": [],
}

_scheduler: BackgroundScheduler = None
_engine: BriefingEngine = None


def _generate_morning():
    """Scheduled job: generate morning briefing at 08:15 CET."""
    global _briefing_store
    print(f"[{datetime.now()}] Generating morning briefing...")
    try:
        briefing = _engine.generate_briefing("morning")
        _briefing_store["morning"] = briefing
        _briefing_store["history"].insert(0, briefing)
        # Keep last 20 briefings
        _briefing_store["history"] = _briefing_store["history"][:20]
        print(f"[{datetime.now()}] Morning briefing generated successfully")
    except Exception as e:
        print(f"[{datetime.now()}] Error generating morning briefing: {e}")


def _generate_evening():
    """Scheduled job: generate evening briefing at 17:15 CET."""
    global _briefing_store
    print(f"[{datetime.now()}] Generating evening briefing...")
    try:
        briefing = _engine.generate_briefing("evening")
        _briefing_store["evening"] = briefing
        _briefing_store["history"].insert(0, briefing)
        _briefing_store["history"] = _briefing_store["history"][:20]
        print(f"[{datetime.now()}] Evening briefing generated successfully")
    except Exception as e:
        print(f"[{datetime.now()}] Error generating evening briefing: {e}")


def get_briefing(briefing_type: str) -> dict:
    """Get the latest briefing of a given type, generating if needed."""
    stored = _briefing_store.get(briefing_type)
    if stored:
        return stored

    # Generate on demand if none cached
    if _engine:
        briefing = _engine.generate_briefing(briefing_type)
        _briefing_store[briefing_type] = briefing
        _briefing_store["history"].insert(0, briefing)
        return briefing

    return {"error": "Briefing engine not initialized"}


def get_briefing_history(limit: int = 10) -> list:
    """Get past briefings."""
    return _briefing_store["history"][:limit]


def setup_scheduler():
    """Initialize and start the scheduler."""
    global _scheduler, _engine

    config_path = str(Path(__file__).parent.parent / "config" / "config.json")
    _engine = BriefingEngine(config_path)

    _scheduler = BackgroundScheduler()

    # Morning briefing at 08:15 Stockholm time
    _scheduler.add_job(
        _generate_morning,
        CronTrigger(hour=8, minute=15, timezone="Europe/Stockholm"),
        id="morning_briefing",
        name="Morning Briefing",
    )

    # Evening briefing at 17:15 Stockholm time
    _scheduler.add_job(
        _generate_evening,
        CronTrigger(hour=17, minute=15, timezone="Europe/Stockholm"),
        id="evening_briefing",
        name="Evening Briefing",
    )

    _scheduler.start()
    print("Scheduler started: morning briefing at 08:15, evening at 17:15 (Europe/Stockholm)")


def shutdown_scheduler():
    """Shut down the scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown()
