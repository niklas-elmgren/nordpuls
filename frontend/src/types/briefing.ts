export interface BriefingRecommendation {
  symbol: string;
  name: string;
  action: string;
  confidence: string;
  price: number;
  change_percent: number;
  reasons: string[];
  news_sentiment: string;
  congress_signal: string | null;
}

export interface RocketPick {
  symbol: string;
  name: string;
  morning_price: number;
  // Daytrading levels
  entry_price?: number;
  stoploss?: number;
  stoploss_pct?: number;
  target?: number;
  target_pct?: number;
  // Technical indicators
  rsi?: number;
  support?: number;
  resistance?: number;
  volume_spike?: number;
  trend?: "up" | "down" | "neutral";
  tech_signals?: string[];
  // Scoring
  signal_score: number;
  rocket_score: number;
  reasons: string[];
  news_sentiment: string;
  pick_time: string;
}

export interface RocketFollowup extends RocketPick {
  current_price: number;
  day_change_percent: number;
  status: "TARGET_HIT" | "PROFIT" | "FLAT" | "SMALL_LOSS" | "STOP_LOSS" | "NO_DATA";
  recommendation: string;
  message: string;
}

export interface Briefing {
  type: string;
  generated_at: string;
  market_status: string;
  summary: string;
  highlights: Array<{
    stock: string;
    signal?: string;
    alert?: string;
    reasons?: string[];
  }>;
  recommendations: BriefingRecommendation[];
  congress_notable: Array<{
    ticker: string;
    sentiment: string;
    description: string;
    total_trades: number;
  }>;
  rocket_picks?: RocketPick[];
  rocket_followup?: RocketFollowup[];
  disclaimer: string;
  error?: string;
}

export interface RocketHistoryEntry {
  symbol: string;
  name: string;
  morning_price: number;
  evening_price: number;
  change_percent: number;
  status: string;
  recommendation: string;
}

export interface RocketDayHistory {
  date: string;
  rockets: RocketHistoryEntry[];
  summary: {
    total_picks: number;
    winners: number;
    losers: number;
    total_return_percent: number;
    avg_return_percent: number;
  };
}

export interface RocketsHistoryStats {
  total_days: number;
  total_picks: number;
  total_winners: number;
  total_losers: number;
  win_rate: number;
  avg_return: number;
  total_return: number;
  best_pick: RocketHistoryEntry & { date: string } | null;
  worst_pick: RocketHistoryEntry & { date: string } | null;
}

export interface RocketsHistory {
  history: RocketDayHistory[];
  stats: RocketsHistoryStats;
}

// Investment Simulation Types
export interface SimulationTrade {
  date: string;
  symbol: string;
  name: string;
  morning_price: number;
  evening_price: number;
  change_percent: number;
  profit_1000: number;
  profit_10000: number;
  cumulative_1000: number;
  cumulative_10000: number;
}

export interface SimulationTotals {
  start_1000: number;
  start_10000: number;
  end_1000: number;
  end_10000: number;
  profit_1000: number;
  profit_10000: number;
  return_percent: number;
  trade_count: number;
}

export interface RocketSimulation {
  trades: SimulationTrade[];
  totals: SimulationTotals;
}

export interface CombinedTotals {
  start_1000: number;
  start_10000: number;
  end_1000: number;
  end_10000: number;
  profit_1000: number;
  profit_10000: number;
  return_percent: number;
  total_trades: number;
}

export interface InvestmentSimulation {
  rocket_1: RocketSimulation;
  rocket_2: RocketSimulation;
  combined: {
    totals: CombinedTotals;
  };
}
