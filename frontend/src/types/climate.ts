export interface MarketIndex {
  symbol: string;
  name: string;
  current_price: number;
  change_percent: number;
  trend: "up" | "down" | "neutral";
  currency: string;
}

export interface SignalDistribution {
  total_stocks: number;
  buy: number;
  sell: number;
  watch: number;
  hold: number;
  avoid: number;
}

export interface InternalSignals {
  signal_distribution: SignalDistribution;
  avg_change_percent: number;
  high_volume_count: number;
  overall_sentiment: "bullish" | "bearish" | "neutral";
}

export interface CalendarEvent {
  id: string;
  date: string;
  title: string;
  category: string;
  source: string;
  impact: "high" | "medium" | "low";
  days_until: number;
  is_active: boolean;
}

export interface ClimateOverview {
  indices: MarketIndex[];
  signals: InternalSignals;
  events: CalendarEvent[];
  timestamp: string;
}
