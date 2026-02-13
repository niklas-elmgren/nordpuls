"""
db.py - PostgreSQL-lagring för raketdata.

Ersätter JSON-filerna daily_rockets.json och rockets_history.json
med persistent lagring i PostgreSQL (Railway).

Ansluter via DATABASE_URL env var.
"""

import os
import json
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor


def _get_conn():
    """Hämta en databasanslutning via DATABASE_URL."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg2.connect(url)


def init_db():
    """Skapa tabeller om de inte finns."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS rocket_picks (
                    date TEXT PRIMARY KEY,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS rockets_history (
                    date TEXT PRIMARY KEY,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()
        print("DB tables ready")
    finally:
        conn.close()


def save_rocket_picks(data: dict):
    """UPSERT dagens raketval."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO rocket_picks (date, data)
                VALUES (%s, %s)
                ON CONFLICT (date) DO UPDATE SET data = EXCLUDED.data, created_at = NOW()
            """, (data["date"], json.dumps(data)))
        conn.commit()
    finally:
        conn.close()


def load_rocket_picks() -> dict | None:
    """Hämta dagens raketval. Returnerar None om det inte finns data för idag."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT data FROM rocket_picks WHERE date = %s", (today,))
            row = cur.fetchone()
            if row:
                return row["data"]
            return None
    finally:
        conn.close()


def save_history_day(day_entry: dict):
    """UPSERT en dags historik."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO rockets_history (date, data)
                VALUES (%s, %s)
                ON CONFLICT (date) DO UPDATE SET data = EXCLUDED.data, created_at = NOW()
            """, (day_entry["date"], json.dumps(day_entry)))
        conn.commit()
    finally:
        conn.close()


def load_rockets_history() -> list:
    """Hämta senaste 90 dagarna, sorterade med nyast först."""
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT data FROM rockets_history
                ORDER BY date DESC
                LIMIT 90
            """)
            rows = cur.fetchall()
            return [row["data"] for row in rows]
    finally:
        conn.close()
