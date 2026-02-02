# Trading Agent Knowledge Base
## Kunskapsbas för Stock Research Agent

Detta dokument innehåller den samlade kunskapen som agenten ska använda för att analysera aktier, tolka data och ge insikter.

---

# DEL 1: TEKNISK ANALYS

## 1.1 Grundprinciper

Teknisk analys bygger på tre grundantaganden:
1. **Marknaden diskonterar allt** – All information är redan inprisad
2. **Priser rör sig i trender** – Trender fortsätter tills de bryts
3. **Historien upprepar sig** – Mönster återkommer

### Trendtyper
- **Upptrend**: Högre toppar och högre bottnar
- **Nedtrend**: Lägre toppar och lägre bottnar
- **Sidledes**: Priser rör sig inom ett intervall

## 1.2 Viktiga indikatorer

### Glidande medelvärden (Moving Averages)
- **SMA (Simple Moving Average)**: Genomsnitt av stängningspriser
- **EMA (Exponential Moving Average)**: Viktar nyare priser högre
- **Vanliga perioder**: 20, 50, 100, 200 dagar
- **Golden Cross**: 50-dagars korsar ÖVER 200-dagars = bullish
- **Death Cross**: 50-dagars korsar UNDER 200-dagars = bearish

### RSI (Relative Strength Index)
- Mäter momentum på skala 0-100
- **Över 70**: Överköpt – risk för nedgång
- **Under 30**: Översålt – möjlig uppgång
- **Divergens**: När RSI och pris går åt olika håll = potentiell vändning

### Volym
- **Hög volym + prisuppgång**: Bekräftar trenden (bullish)
- **Hög volym + prisnedgång**: Bekräftar trenden (bearish)
- **Låg volym**: Svag övertygelse, möjlig vändning
- **Volym 1.5x över genomsnittet**: Signifikant aktivitet

### MACD (Moving Average Convergence Divergence)
- Visar förhållandet mellan två EMA
- **MACD-linje korsar över signallinjen**: Köpsignal
- **MACD-linje korsar under signallinjen**: Säljsignal

## 1.3 Chartmönster

### Fortsättningsmönster
- **Flagga/Vimpel**: Kort paus i stark trend
- **Triangel**: Konsolidering före utbrott

### Vändningsmönster
- **Huvud-och-axlar**: Topp med tre peaks, mitten högst
- **Dubbel-topp/botten**: Två försök att bryta nivå misslyckas
- **Rounding bottom**: Gradvis vändning från nedtrend

## 1.4 Stöd och motstånd
- **Stöd**: Prisnivå där köpare historiskt kliver in
- **Motstånd**: Prisnivå där säljare historiskt kliver in
- När stöd bryts blir det ofta nytt motstånd (och vice versa)

---

# DEL 2: FUNDAMENTAL ANALYS

## 2.1 Nyckeltal att bevaka

### Värderingsmultiplar
| Nyckeltal | Formel | Tolkning |
|-----------|--------|----------|
| **P/E** | Pris / Vinst per aktie | Lågt = billig (men varför?) |
| **P/S** | Pris / Försäljning per aktie | Användbart för olönsamma bolag |
| **P/B** | Pris / Bokfört värde | Under 1 = under tillgångsvärde |
| **EV/EBITDA** | Enterprise Value / EBITDA | Jämförbart över branscher |

### Lönsamhet
| Nyckeltal | Vad det visar |
|-----------|---------------|
| **Bruttomarginal** | Effektivitet i produktion |
| **Rörelsemarginal** | Operativ effektivitet |
| **Nettomarginal** | Slutlig lönsamhet |
| **ROE** | Avkastning på eget kapital |
| **ROA** | Avkastning på tillgångar |

### Finansiell hälsa
- **Skuldsättningsgrad**: Skulder / Eget kapital
- **Current ratio**: Omsättningstillgångar / Kortfristiga skulder (>1 bra)
- **Quick ratio**: Som ovan men exkl. varulager
- **Räntetäckningsgrad**: EBIT / Räntekostnader (>3 säkert)

## 2.2 Kassaflödesanalys

- **Operativt kassaflöde**: Pengar från verksamheten
- **Fritt kassaflöde (FCF)**: Operativt - CapEx
- **Varning**: Vinst utan kassaflöde kan vara bokföringsknep

## 2.3 Kvalitativa faktorer

- **Konkurrensfördel (moat)**: Patent, varumärke, nätverkseffekter
- **Ledning**: Track record, insider-ägande, kompensation
- **Branschposition**: Marknadsledare eller utmanare?
- **Makrofaktorer**: Räntor, inflation, regulatoriska risker

---

# DEL 3: KONGRESSHANDEL - TOLKNING OCH ANALYS

## 3.1 Bakgrund: STOCK Act

- **Införd**: 2012, efter 60 Minutes-avslöjande
- **Krav**: Kongressmedlemmar måste rapportera aktieaffärer >$1,000 inom 45 dagar
- **Straff**: Endast $200 böter för sen rapportering
- **Verklighet**: Ingen har åtalats under lagen

## 3.2 Vad forskningen säger

### Före STOCK Act (1993-2008)
- Studie Ziobrowski (2004): Senatorer överträffade marknaden med ~10%/år
- Studie Ziobrowski (2011): Representanter överträffade med ~6%/år

### Efter STOCK Act (2012-2020)
- Studie Belmont (2022): Ingen signifikant överavkastning, "random stock picking"
- Studie Hanousek (2023): Senatorer fortfarande ~5% abnormal avkastning
- **Slutsats**: Forskningsresultaten är blandade

## 3.3 Hur man tolkar kongressdata

### Starkt signal (värt att notera)
- **Stora transaktioner**: >$100,000
- **Kluster**: Flera kongressmedlemmar köper samma aktie
- **Timing**: Strax före viktiga lagstiftningsbeslut
- **Kommittérelevans**: Medlem i relevant kommitté köper

### Svag signal (var skeptisk)
- **Små belopp**: <$15,000 (kan vara automatiskt sparande)
- **Enskilda transaktioner**: En person, en gång
- **Lång fördröjning**: Rapporterat sent, marknaden har redan reagerat

### Röda flaggor
- **Sälj före dåliga nyheter**: Som COVID-briefing i februari 2020
- **Köp före positiv lagstiftning**: T.ex. infrastruktur, chips-act
- **Familjetransaktioner**: Make/makas handel kan dölja mönster

## 3.4 Viktiga personer att bevaka

Historiskt aktiva traders:
- **Nancy Pelosi**: Välkänd för teknikaffärer (make Paul Pelosi)
- **Dan Crenshaw**: Aktiv inom energi
- **Tommy Tuberville**: Många och stora transaktioner

## 3.5 Begränsningar

- **45-dagars fördröjning**: Informationen är inte realtid
- **Orsak ≠ effekt**: Korrelation bevisar inte insider-trading
- **Legitima skäl**: Portföljbalansering, skatteoptimering
- **Trusts/rådgivare**: Vissa har "blind trusts" som handlar åt dem

---

# DEL 4: RISKHANTERING

## 4.1 Grundregler

### 1-2% regeln
- Riskera ALDRIG mer än 1-2% av kontot på en enskild trade
- Med $10,000 konto = max $100-200 risk per trade

### Position sizing formel
```
Position storlek = (Konto × Risk%) / (Entry - Stop-loss)

Exempel:
- Konto: $10,000
- Risk: 1% = $100
- Entry: $50
- Stop-loss: $47 (risk $3/aktie)
- Position: $100 / $3 = 33 aktier
```

## 4.2 Stop-loss strategier

### Typer
- **Fast stop**: Förutbestämd prisnivå
- **Trailing stop**: Följer priset uppåt
- **Procent-stop**: T.ex. 5% under inköp
- **ATR-baserad**: Baserad på volatilitet

### Placering
- Under stöd (för långa positioner)
- Över motstånd (för korta positioner)
- Anpassa efter volatilitet – mer volatil = bredare stop

## 4.3 Risk/Reward ratio

- **Minimum 1:2**: Riskera $1 för att tjäna $2
- **Idealt 1:3 eller bättre**
- Med 1:2 ratio och 40% träffgrad är du fortfarande lönsam

### Beräkning
```
Risk = Entry - Stop-loss
Reward = Take-profit - Entry
Ratio = Reward / Risk

Exempel:
Entry: $100, Stop: $95, Target: $115
Risk: $5, Reward: $15
Ratio: 15/5 = 3:1 ✓
```

## 4.4 Portföljnivå

- **Max 10-20% i en sektor**
- **Korrelerade positioner**: Räkna som en risk
- **Daglig förlustgräns**: Sluta handla efter t.ex. -3%
- **Aldrig all-in**: Behåll alltid kontant buffert

---

# DEL 5: SIGNALVÄRDERING - HUR AGENTEN SKA TÄNKA

## 5.1 Signalhierarki

### Primära signaler (starkast)
1. Stark fundamental värdering + positiv prisrörelse
2. Ovanligt hög volym + kongressköp (kluster)
3. Golden cross + förbättrad vinst

### Sekundära signaler
1. Enskild indikator (RSI, MACD)
2. Enstaka kongresstransaktion
3. Positiva nyheter utan volymbekräftelse

### Varningssignaler
1. Hög värdering + insider-sälj
2. Vinst utan kassaflöde
3. Kongress-sälj före earnings

## 5.2 Kombinera datakällor

Agenten ska väga samman:

| Källa | Vikt | Kommentar |
|-------|------|-----------|
| Prisdata | 30% | Faktisk marknadsrörelse |
| Fundamental | 30% | Bolagets verkliga värde |
| Nyheter/sentiment | 20% | Kortsiktig katalysator |
| Kongressdata | 20% | "Smart money" indikator |

## 5.3 Formulera output

### Vid BULLISH signal
> "[Aktie] visar flera positiva tecken: [lista faktorer]. 
> Kongressen har gjort [X] köp senaste 90 dagarna vs [Y] sälj.
> Tänk på: [risker/begränsningar]"

### Vid BEARISH signal
> "[Aktie] har flera varningsflaggor: [lista faktorer].
> Noterbart: [specifik observation].
> Om du äger: överväg [åtgärd]"

### Vid NEUTRAL/OSÄKER
> "Blandade signaler för [Aktie]: 
> Positivt: [X]. Negativt: [Y].
> Rekommendation: Avvakta tydligare signal."

---

# DEL 6: KÄLLOR OCH LÄSNING

## Teknisk analys
- Corporate Finance Institute: https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/technical-analysis/
- Investopedia Technical Analysis: https://www.investopedia.com/technical-analysis-4689657
- Fidelity Learning Center: https://www.fidelity.com/learning-center/trading-investing/technical-analysis/

## Fundamental analys
- Investopedia Fundamental Analysis: https://www.investopedia.com/terms/f/fundamentalanalysis.asp
- Wikipedia: https://en.wikipedia.org/wiki/Fundamental_analysis

## Kongresshandel
- STOCK Act (Wikipedia): https://en.wikipedia.org/wiki/STOCK_Act
- Brennan Center: https://www.brennancenter.org/our-work/research-reports/congressional-stock-trading-explained
- Campaign Legal Center: https://campaignlegal.org/update/congressional-stock-trading-and-stock-act
- Akademisk studie: https://www.sciencedirect.com/science/article/abs/pii/S0047272722000044

## Riskhantering
- Britannica Position Sizing: https://www.britannica.com/money/calculating-position-size
- TraderLion Position Sizing: https://traderlion.com/risk-management/position-sizing-strategies/

## Datakällor (API:er)
- House Stock Watcher: https://housestockwatcher.com/api
- Senate Stock Watcher: https://senatestockwatcher.com/api
- Yahoo Finance (yfinance): https://pypi.org/project/yfinance/
- Quiver Quantitative: https://www.quiverquant.com/

---

# DEL 7: DISCLAIMER (ALLTID INKLUDERA)

> **⚠️ VIKTIG INFORMATION**
> 
> Denna analys är endast för informations- och utbildningssyfte. Den utgör INTE:
> - Finansiell rådgivning
> - Investeringsrekommendation  
> - Köp- eller säljsignal
>
> All handel innebär risk. Du kan förlora hela ditt investerade kapital.
> Gör alltid din egen research (DYOR) innan du fattar investeringsbeslut.
> Tidigare resultat garanterar inte framtida avkastning.
>
> Om kongressdata specifikt: Korrelation innebär inte kausalitet.
> Kongressmedlemmars trades kan ha legitima förklaringar.

---

*Dokumentversion: 1.0*
*Senast uppdaterad: 2026-02-02*
