"""
Briefing API routes.
"""

from fastapi import APIRouter

from services.scheduler import get_briefing, get_briefing_history

router = APIRouter()


@router.get("/morning")
def get_morning_briefing():
    """Get the latest morning briefing (08:15 CET)."""
    return get_briefing("morning")


@router.get("/evening")
def get_evening_briefing():
    """Get the latest evening briefing (17:15 CET)."""
    return get_briefing("evening")


@router.get("/latest")
def get_latest_briefing():
    """Get the most recent briefing of any type."""
    history = get_briefing_history(limit=1)
    if history:
        return history[0]
    # Generate morning briefing on demand
    return get_briefing("morning")


@router.get("/history")
def get_history(limit: int = 10):
    """Get past briefings."""
    return {"briefings": get_briefing_history(limit)}
