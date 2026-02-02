"""
Stock Research Agent - Webb-UI

Kör med: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

from agents.stock_data import StockDataFetcher
from agents.news_fetcher import NewsFetcher
from agents.congress_trades import CongressTradesFetcher

# Sidkonfiguration
st.set_page_config(
    page_title="Stock Research Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
    }
    .bullish {
        color: #10b981;
        font-weight: 600;
    }
    .bearish {
        color: #ef4444;
        font-weight: 600;
    }
    .neutral {
        color: #6b7280;
        font-weight: 600;
    }
    .congress-badge {
        background: #3b82f6;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# Cachea data för att undvika onödiga API-anrop
@st.cache_data(ttl=300)  # Cache i 5 minuter
def load_config():
    config_path = Path(__file__).parent / "config" / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@st.cache_resource
def get_fetchers():
    return {
        "stock": StockDataFetcher(),
        "news": NewsFetcher(),
        "congress": CongressTradesFetcher()
    }


@st.cache_data(ttl=300)
def fetch_stock_data(symbol: str):
    fetchers = get_fetchers()
    return fetchers["stock"].get_stock_info(symbol)


@st.cache_data(ttl=300)
def fetch_unusual_activity(symbol: str):
    fetchers = get_fetchers()
    return fetchers["stock"].check_unusual_activity(symbol)


@st.cache_data(ttl=600)
def fetch_news(company_name: str, symbol: str):
    fetchers = get_fetchers()
    return fetchers["news"].get_news_summary(company_name, symbol)


@st.cache_data(ttl=600)
def fetch_congress_activity(ticker: str):
    fetchers = get_fetchers()
    return fetchers["congress"].check_ticker_congress_activity(ticker)


@st.cache_data(ttl=600)
def fetch_congress_stats(days: int):
    fetchers = get_fetchers()
    return fetchers["congress"].get_summary_stats(days)


@st.cache_data(ttl=600)
def fetch_recent_congress_trades(days: int, min_amount: str):
    fetchers = get_fetchers()
    return fetchers["congress"].get_recent_trades(days, min_amount)


def render_header():
    """Renderar sidhuvud."""
    st.markdown('<p class="main-header">📊 Stock Research Agent</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Aktieanalys • Nyheter • Kongresshandel</p>', unsafe_allow_html=True)


def render_sidebar():
    """Renderar sidopanel med inställningar."""
    with st.sidebar:
        st.header("⚙️ Inställningar")
        
        # Watchlist
        config = load_config()
        watchlist = config.get("watchlist", [])
        
        st.subheader("📋 Watchlist")
        selected_stocks = st.multiselect(
            "Välj aktier att analysera",
            options=[f"{s['name']} ({s['symbol']})" for s in watchlist],
            default=[f"{s['name']} ({s['symbol']})" for s in watchlist[:3]]
        )
        
        st.divider()
        
        # Kongressinställningar
        st.subheader("🏛️ Kongressfilter")
        congress_days = st.slider("Antal dagar tillbaka", 7, 90, 30)
        min_amount = st.selectbox(
            "Minsta transaktionsbelopp",
            options=[
                "$1,001 -",
                "$15,001 - $50,000",
                "$50,001 - $100,000",
                "$100,001 - $250,000",
                "$250,001 - $500,000"
            ],
            index=2
        )
        
        st.divider()
        
        # Info
        st.caption(f"Senast uppdaterad: {datetime.now().strftime('%H:%M')}")
        st.caption("Data uppdateras var 5:e minut")
        
        return selected_stocks, congress_days, min_amount


def render_stock_card(stock_info: dict, news_info: dict, congress_info: dict, activity_info: dict):
    """Renderar ett kort för en aktie."""
    
    # Hantera fel
    if "error" in stock_info:
        st.error(f"Kunde inte hämta data: {stock_info['error']}")
        return
    
    # Kursförändring
    change = stock_info.get("change_percent", 0)
    change_class = "bullish" if change > 0 else "bearish" if change < 0 else "neutral"
    change_arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
    
    # Huvudmetrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Kurs",
            value=f"{stock_info.get('current_price', 'N/A')} {stock_info.get('currency', '')}",
            delta=f"{change:+.2f}%"
        )
    
    with col2:
        vol_ratio = stock_info.get("volume_vs_avg", 1)
        vol_status = "🔥" if vol_ratio > 1.5 else ""
        st.metric(
            label="Volym vs snitt",
            value=f"{vol_ratio:.1f}x {vol_status}"
        )
    
    with col3:
        sentiment = news_info.get("overall_sentiment", "no_data")
        sentiment_emoji = {"positive": "🟢", "negative": "🔴", "neutral": "🟡", "no_data": "⚪"}.get(sentiment, "⚪")
        st.metric(
            label="Nyhetssentiment",
            value=f"{sentiment_emoji} {sentiment.title()}"
        )
    
    with col4:
        if congress_info.get("has_congress_activity"):
            cong_sentiment = congress_info.get("sentiment", "NEUTRAL 🟡")
            st.metric(
                label="🏛️ Kongressen",
                value=cong_sentiment.split()[0],
                delta=f"{congress_info.get('buys', 0)} köp, {congress_info.get('sells', 0)} sälj"
            )
        else:
            st.metric(
                label="🏛️ Kongressen",
                value="Ingen aktivitet"
            )
    
    # Expanderbar sektion med mer info
    with st.expander("Se detaljer"):
        tab1, tab2, tab3 = st.tabs(["📈 Marknadsdata", "📰 Nyheter", "🏛️ Kongresshandel"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.write("**52-veckors högsta:**", stock_info.get("high_52w", "N/A"))
                st.write("**52-veckors lägsta:**", stock_info.get("low_52w", "N/A"))
            with col2:
                if stock_info.get("market_cap"):
                    market_cap = stock_info["market_cap"]
                    if market_cap > 1e12:
                        cap_str = f"{market_cap/1e12:.1f}T"
                    elif market_cap > 1e9:
                        cap_str = f"{market_cap/1e9:.1f}B"
                    else:
                        cap_str = f"{market_cap/1e6:.1f}M"
                    st.write("**Börsvärde:**", cap_str)
                
                # Flaggor
                flags = activity_info.get("flags", [])
                if flags:
                    st.write("**Signaler:**")
                    for flag in flags:
                        st.write(f"  • {flag}")
        
        with tab2:
            articles = news_info.get("articles", [])
            if articles:
                for article in articles[:5]:
                    st.write(f"**{article.get('source', 'Okänd källa')}**")
                    st.write(article.get("title", ""))
                    sentiment = article.get("sentiment", {})
                    sent_emoji = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}.get(
                        sentiment.get("sentiment", "neutral"), "🟡"
                    )
                    st.caption(f"{sent_emoji} {sentiment.get('sentiment', 'neutral')} • {article.get('published', '')[:10]}")
                    st.divider()
            else:
                st.info("Inga nyheter hittades för detta bolag.")
        
        with tab3:
            if congress_info.get("has_congress_activity"):
                st.write(f"**{congress_info.get('sentiment_description', '')}**")
                st.write(f"Totalt {congress_info.get('total_trades', 0)} transaktioner senaste 90 dagarna")
                
                # Lista politiker som handlat
                politicians = congress_info.get("politicians_involved", [])
                if politicians:
                    st.write("**Politiker som handlat:**")
                    for pol in politicians[:10]:
                        st.write(f"  • {pol}")
                
                # Senaste transaktioner
                recent = congress_info.get("recent_trades", [])
                if recent:
                    st.write("**Senaste transaktioner:**")
                    for trade in recent[:5]:
                        trade_type = "🟢 Köp" if "purchase" in trade.get("type", "").lower() else "🔴 Sälj"
                        st.write(f"  • {trade.get('politician', 'Okänd')} ({trade.get('party', '')}) - {trade_type} - {trade.get('amount', '')}")
            else:
                st.info("Ingen kongressaktivitet för denna aktie senaste 90 dagarna.")


def render_dashboard_tab(selected_stocks: list):
    """Renderar dashboard-fliken."""
    st.header("📊 Dashboard")
    
    if not selected_stocks:
        st.info("Välj aktier i sidopanelen för att se analysen.")
        return
    
    config = load_config()
    watchlist = {f"{s['name']} ({s['symbol']})": s for s in config.get("watchlist", [])}
    
    for stock_str in selected_stocks:
        stock = watchlist.get(stock_str)
        if not stock:
            continue
        
        st.subheader(f"{stock['name']} ({stock['symbol']})")
        
        with st.spinner(f"Hämtar data för {stock['name']}..."):
            # Hämta all data
            stock_data = fetch_stock_data(stock["symbol"])
            activity_data = fetch_unusual_activity(stock["symbol"])
            news_data = fetch_news(stock["name"], stock["symbol"])
            
            # Extrahera ren ticker för kongressdata
            clean_ticker = stock["symbol"].replace(".ST", "").replace("-B", "").replace("-A", "").upper()
            congress_data = fetch_congress_activity(clean_ticker)
            
            # Rendera kortet
            render_stock_card(stock_data, news_data, congress_data, activity_data)
        
        st.divider()


def render_congress_tab(days: int, min_amount: str):
    """Renderar kongresshandel-fliken."""
    st.header("🏛️ Kongresshandel")
    
    st.markdown("""
    Amerikanska kongressmedlemmar måste enligt **STOCK Act** rapportera sina aktieaffärer inom 45 dagar.
    Här kan du se vad de köper och säljer.
    """)
    
    # Hämta statistik
    with st.spinner("Hämtar kongressdata..."):
        stats = fetch_congress_stats(days)
        trades = fetch_recent_congress_trades(days, min_amount)
    
    if "error" in stats:
        st.warning("Kunde inte hämta kongressdata. Kontrollera din internetanslutning.")
        return
    
    # Översiktsmetrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Totalt antal trades", stats.get("total_trades", 0))
    with col2:
        st.metric("Köp", stats.get("buys", 0))
    with col3:
        st.metric("Sälj", stats.get("sells", 0))
    with col4:
        ratio = stats.get("buy_sell_ratio", 0)
        sentiment = "🟢 Bullish" if ratio > 1.2 else "🔴 Bearish" if ratio < 0.8 else "🟡 Neutral"
        st.metric("Köp/Sälj-ratio", f"{ratio:.2f}", delta=sentiment)
    
    st.divider()
    
    # Tabs för olika vyer
    tab1, tab2, tab3 = st.tabs(["📈 Mest handlade aktier", "👤 Mest aktiva politiker", "📋 Senaste transaktioner"])
    
    with tab1:
        top_tickers = stats.get("top_tickers", [])
        if top_tickers:
            df = pd.DataFrame(top_tickers, columns=["Ticker", "Antal transaktioner"])
            st.bar_chart(df.set_index("Ticker"))
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Ingen data tillgänglig.")
    
    with tab2:
        top_pols = stats.get("top_politicians", [])
        if top_pols:
            df = pd.DataFrame(top_pols, columns=["Politiker", "Antal transaktioner"])
            st.bar_chart(df.set_index("Politiker").head(10))
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Ingen data tillgänglig.")
    
    with tab3:
        if trades:
            # Konvertera till DataFrame
            df = pd.DataFrame(trades)
            
            # Filtrera kolumner
            display_cols = ["politician", "party", "ticker", "type", "amount", "transaction_date", "chamber"]
            df_display = df[display_cols].copy()
            df_display.columns = ["Politiker", "Parti", "Ticker", "Typ", "Belopp", "Datum", "Kammare"]
            
            # Sortera
            df_display = df_display.sort_values("Datum", ascending=False)
            
            # Visa
            st.dataframe(
                df_display.head(50),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Parti": st.column_config.TextColumn(width="small"),
                    "Kammare": st.column_config.TextColumn(width="small"),
                }
            )
        else:
            st.info("Inga transaktioner hittades med valda filter.")
    
    # Partifördelning
    st.divider()
    st.subheader("Partifördelning")
    
    party = stats.get("party_breakdown", {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔵 Demokrater", party.get("D", 0))
    with col2:
        st.metric("🔴 Republikaner", party.get("R", 0))
    with col3:
        st.metric("⚪ Oberoende", party.get("I", 0))


def render_search_tab():
    """Renderar sökfliken."""
    st.header("🔍 Sök")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sök på aktie")
        ticker_search = st.text_input("Ange ticker (t.ex. AAPL, NVDA, MSFT)", key="ticker_search")
        
        if ticker_search:
            with st.spinner("Söker..."):
                congress_data = fetch_congress_activity(ticker_search.upper())
                
                if congress_data.get("has_congress_activity"):
                    st.success(f"Hittade kongressaktivitet för {ticker_search.upper()}")
                    st.write(f"**Sentiment:** {congress_data.get('sentiment', 'N/A')}")
                    st.write(congress_data.get("sentiment_description", ""))
                    st.write(f"**Totalt:** {congress_data.get('total_trades', 0)} transaktioner")
                    
                    # Visa politiker
                    pols = congress_data.get("politicians_involved", [])
                    if pols:
                        with st.expander(f"Politiker som handlat ({len(pols)} st)"):
                            for pol in pols:
                                st.write(f"• {pol}")
                else:
                    st.info(f"Ingen kongressaktivitet hittades för {ticker_search.upper()} senaste 90 dagarna.")
    
    with col2:
        st.subheader("Sök på politiker")
        politician_search = st.text_input("Ange namn (t.ex. Pelosi, Tuberville)", key="politician_search")
        
        if politician_search:
            with st.spinner("Söker..."):
                fetchers = get_fetchers()
                trades = fetchers["congress"].get_trades_by_politician(politician_search, days=365)
                
                if trades:
                    st.success(f"Hittade {len(trades)} transaktioner för '{politician_search}'")
                    
                    # Sammanfatta
                    buys = len([t for t in trades if "purchase" in t.get("type", "").lower()])
                    sells = len([t for t in trades if "sale" in t.get("type", "").lower()])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Köp", buys)
                    with col2:
                        st.metric("Sälj", sells)
                    
                    # Visa transaktioner
                    df = pd.DataFrame(trades)
                    if not df.empty:
                        display_cols = ["ticker", "type", "amount", "transaction_date"]
                        df_display = df[display_cols].copy()
                        df_display.columns = ["Ticker", "Typ", "Belopp", "Datum"]
                        st.dataframe(df_display.head(20), use_container_width=True, hide_index=True)
                else:
                    st.info(f"Inga transaktioner hittades för '{politician_search}'.")


def render_about_tab():
    """Renderar om-fliken."""
    st.header("ℹ️ Om verktyget")
    
    st.markdown("""
    ### Stock Research Agent
    
    Ett verktyg för att samla in och analysera aktiedata, nyheter och amerikanska kongressmedlemmars handel.
    
    **⚠️ Viktigt:** Detta är ett verktyg för research och information – **inte** finansiell rådgivning. 
    Gör alltid din egen analys innan du fattar investeringsbeslut.
    
    ---
    
    ### 📊 Datakällor
    
    | Data | Källa | Uppdatering |
    |------|-------|-------------|
    | Aktiekurser | Yahoo Finance | Realtid (15 min fördröjning) |
    | Nyheter | RSS-flöden (DI, SVD, Reuters) | Kontinuerligt |
    | Kongresshandel | House/Senate Stock Watcher | Dagligen |
    
    ---
    
    ### 🏛️ Om kongressdata
    
    Amerikanska kongressmedlemmar måste enligt **STOCK Act (2012)** rapportera sina aktieaffärer 
    inom 45 dagar. Denna data är offentlig och tillgänglig via:
    
    - [House Stock Watcher](https://housestockwatcher.com) (Representanthuset)
    - [Senate Stock Watcher](https://senatestockwatcher.com) (Senaten)
    
    **Tänk på:**
    - Rapportering sker med upp till 45 dagars fördröjning
    - Kongressmedlemmar kan ha legitima skäl för sina affärer
    - Korrelation ≠ kausalitet – deras trades garanterar inte framgång
    
    ---
    
    ### 🔧 Teknisk info
    
    - **Backend:** Python 3.10+
    - **Frontend:** Streamlit
    - **Aktiedata:** yfinance
    - **Nyheter:** feedparser + BeautifulSoup
    """)


def main():
    """Huvudfunktion."""
    render_header()
    
    # Sidopanel
    selected_stocks, congress_days, min_amount = render_sidebar()
    
    # Huvudinnehåll med tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🏛️ Kongresshandel", "🔍 Sök", "ℹ️ Om"])
    
    with tab1:
        render_dashboard_tab(selected_stocks)
    
    with tab2:
        render_congress_tab(congress_days, min_amount)
    
    with tab3:
        render_search_tab()
    
    with tab4:
        render_about_tab()


if __name__ == "__main__":
    main()
