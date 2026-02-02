export interface WatchlistStock {
  symbol: string;
  name: string;
  market: string;
  current_price: number;
  change_percent: number;
  volume_vs_avg: number;
  currency: string;
  error?: string;
}

export interface StockInfo {
  symbol: string;
  name: string;
  current_price: number;
  change_percent: number;
  volume: number;
  volume_vs_avg: number;
  high_52w: number | null;
  low_52w: number | null;
  market_cap: number | null;
  currency: string;
  timestamp: string;
  error?: string;
}

export interface Signal {
  type: string;
  score: number;
  reasons: string[];
}

export interface StockAnalysis {
  symbol: string;
  name: string;
  stock_data: StockInfo;
  unusual_activity: string[];
  news_summary: {
    count: number;
    sentiment: string;
    score: number;
  };
  recent_headlines: string[];
  congress_activity: {
    has_congress_activity?: boolean;
    sentiment?: string;
    sentiment_description?: string;
    total_trades?: number;
    buys?: number;
    sells?: number;
    politicians_involved?: string[];
  };
  signal: Signal;
  timestamp: string;
}

export interface OHLCVRecord {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}
