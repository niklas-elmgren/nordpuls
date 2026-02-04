"""
Briefing API routes.
"""

from fastapi import APIRouter

from services.scheduler import get_briefing, get_briefing_history, get_rockets_history

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


@router.get("/rockets/history")
def get_rockets_history_endpoint(days: int = 30):
    """
    Get rocket picks history with performance statistics.

    Returns history of daily rocket picks and their outcomes,
    plus aggregated stats like win rate and average return.
    """
    return get_rockets_history(days)


@router.post("/regenerate/{briefing_type}")
def regenerate_briefing(briefing_type: str):
    """
    Force regenerate a briefing (morning or evening).
    Use this to get fresh data without waiting for scheduled time.
    """
    if briefing_type not in ["morning", "evening"]:
        return {"error": "Invalid briefing type. Use 'morning' or 'evening'"}

    from services.scheduler import _engine, _briefing_store

    if not _engine:
        return {"error": "Briefing engine not initialized"}

    try:
        briefing = _engine.generate_briefing(briefing_type)
        _briefing_store[briefing_type] = briefing
        _briefing_store["history"].insert(0, briefing)
        _briefing_store["history"] = _briefing_store["history"][:20]

        return {
            "success": True,
            "message": f"{briefing_type} briefing regenerated",
            "rocket_picks_count": len(briefing.get("rocket_picks", [])),
            "recommendations_count": len(briefing.get("recommendations", []))
        }
    except Exception as e:
        return {"error": str(e)}
