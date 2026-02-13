"""
Nordpuls - Stock Research API

FastAPI backend wrapping existing Python agents for stock data,
news analysis, congress trading, and morning/evening briefings.

Run with: uvicorn main:app --reload
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend directory is in path for imports
sys.path.insert(0, str(Path(__file__).parent))

from routers import stocks, news, congress, briefings, climate
from services.scheduler import setup_scheduler, shutdown_scheduler
from services.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    init_db()
    setup_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Nordpuls API",
    description="Svensk aktieanalys - data, nyheter, kongresshandel och briefingar",
    version="2.0.0",
    lifespan=lifespan,
)

import os

cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://nordpuls.vercel.app",
]

# Add additional frontend URLs from environment
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    cors_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api/stocks", tags=["Aktier"])
app.include_router(news.router, prefix="/api/news", tags=["Nyheter"])
app.include_router(congress.router, prefix="/api/congress", tags=["Kongresshandel"])
app.include_router(briefings.router, prefix="/api/briefings", tags=["Briefingar"])
app.include_router(climate.router, prefix="/api/climate", tags=["Aktieklimat"])


@app.get("/")
def root():
    return {
        "name": "Nordpuls API",
        "version": "2.0.0",
        "docs": "/docs",
    }
