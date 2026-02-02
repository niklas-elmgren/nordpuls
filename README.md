# Stock Research Agent 📊

Ett Python-baserat verktyg för att samla in och analysera aktiedata, nyheter och amerikanska kongressmedlemmars handel. Tänkt som beslutsstöd – **inte** för automatiserad trading eller finansiell rådgivning.

## 🚀 Snabbstart - Webb-UI

```bash
# Installera beroenden
pip install -r requirements.txt

# Starta webb-gränssnittet
streamlit run app.py
```

Öppna sedan `http://localhost:8501` i din webbläsare.

![Dashboard Preview](docs/dashboard-preview.png)

## Vad gör den?

- Hämtar aktuell kursdata från Yahoo Finance
- Samlar nyheter från svenska och internationella RSS-flöden  
- Gör enkel sentimentanalys på nyheter
- **🏛️ Spårar amerikanska kongressmedlemmars aktiehandel** (via STOCK Act-rapporter)
- Flaggar ovanlig aktivitet (hög volym, stora kursrörelser)
- Genererar dagliga sammanfattningar

## 🏛️ Kongresshandel-funktionen

Amerikanska kongressmedlemmar måste enligt STOCK Act rapportera sina aktieaffärer inom 45 dagar. Verktyget hämtar denna data och:

- Visar vilka aktier kongressen köper/säljer
- Flaggar om kongressen har bullish/bearish sentiment för aktier i din watchlist
- Visar mest handlade aktier och mest aktiva politiker
- Integrerar kongressdata i den övergripande signalen för varje aktie

**Datakällor:**
- House Stock Watcher (representanthuset)
- Senate Stock Watcher (senaten)

## Installation

```bash
# Skapa virtuell miljö (valfritt men rekommenderat)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# eller: venv\Scripts\activate  # Windows

# Installera beroenden
pip install -r requirements.txt
```

## Användning

### Snabbstart

```bash
cd agents
python research_agent.py
```

Detta kör en analys av alla aktier i din watchlist och sparar en rapport i `output/`-mappen.

### Anpassa din watchlist

Redigera `config/config.json` och lägg till aktier:

```json
{
  "watchlist": [
    {
      "symbol": "VOLV-B.ST",    // Yahoo Finance-symbol
      "name": "Volvo B",         // Läsbart namn (används för nyhetssök)
      "market": "OMX Stockholm"
    }
  ]
}
```

**Tips för svenska aktier:**
- OMX Stockholm: Lägg till `.ST` (t.ex. `VOLV-B.ST`, `ERIC-B.ST`)
- A/B-aktier: Använd `-A` eller `-B` (t.ex. `HM-B.ST`)

### Lägg till nyhetskällor

```json
{
  "news_feeds": {
    "swedish": [
      {
        "name": "Dagens Industri",
        "url": "https://www.di.se/rss",
        "category": "business"
      }
    ]
  }
}
```

## 🖥️ Webb-UI Features

Gränssnittet har fyra huvudflikar:

### 📊 Dashboard
- Överblick över din watchlist
- Kurs, volym, sentiment och kongressaktivitet för varje aktie
- Expanderbara kort med detaljerad info

### 🏛️ Kongresshandel
- Statistik över köp/sälj-ratio
- Mest handlade aktier av kongressen
- Mest aktiva politiker
- Filtrera på tidsperiod och transaktionsbelopp
- Partifördelning (Demokrater vs Republikaner)

### 🔍 Sök
- Sök på ticker för att se kongressaktivitet
- Sök på politikernamn för att se deras alla trades

### ℹ️ Om
- Information om datakällor och begränsningar

## Projektstruktur

```
stock-research-agent/
├── app.py                 # 🚀 Streamlit webb-UI (kör denna!)
├── agents/
│   ├── stock_data.py      # Hämtar aktiedata från Yahoo Finance
│   ├── news_fetcher.py    # Hämtar och analyserar nyheter
│   ├── congress_trades.py # Hämtar kongressmedlemmars aktiehandel
│   └── research_agent.py  # Huvudagent som kombinerar allt
├── config/
│   └── config.json        # Watchlist och inställningar
├── data/                  # SQLite-databas (skapas automatiskt)
├── output/                # Genererade rapporter
├── requirements.txt
└── README.md
```

## Exempel på kongressfunktionen

```python
from agents import CongressTradesFetcher

fetcher = CongressTradesFetcher()

# Kolla om kongressen handlar NVDA
activity = fetcher.check_ticker_congress_activity("NVDA")
print(activity["sentiment"])  # "BULLISH 🟢" / "BEARISH 🔴" / "NEUTRAL 🟡"

# Hämta senaste transaktionerna
trades = fetcher.get_recent_trades(days=30, min_amount="$50,001 -")

# Statistik
stats = fetcher.get_summary_stats(days=30)
print(f"Mest handlade: {stats['top_tickers'][:5]}")
```

## Framtida utbyggnad

Idéer för vidareutveckling:

- [ ] **Schemaläggning** – Kör automatiskt varje morgon
- [ ] **E-postrapporter** – Skicka sammanfattning till din inbox
- [ ] **Teknisk analys** – RSI, glidande medelvärden, etc.
- [ ] **AI-sammanfattning** – Använd Claude/GPT för att skriva bättre analyser
- [ ] **Webb-UI** – Enkel dashboard med Streamlit
- [ ] **Alerts** – Push-notiser vid stora händelser

## Begränsningar

- **Fördröjd data**: Yahoo Finance ger fördröjd data (15-20 min)
- **Inte realtid**: Inte lämplig för daytrading
- **Enkel sentiment**: Nyckelordsbaserad analys – kan missa nyanser
- **RSS-beroende**: Nyheter beror på vad källorna publicerar

## Disclaimer ⚠️

Detta verktyg är endast för informations- och utbildningssyfte. Det utgör **inte** finansiell rådgivning. All handel sker på egen risk. Gör alltid din egen research innan du fattar investeringsbeslut.

---

Byggd som ett läroprojekt för att utforska aktieanalys med Python.
