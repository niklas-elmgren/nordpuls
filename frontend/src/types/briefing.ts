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
  disclaimer: string;
  error?: string;
}
