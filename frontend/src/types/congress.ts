export interface CongressTrade {
  chamber: string;
  politician: string;
  party: string;
  state: string;
  ticker: string;
  asset: string;
  type: string;
  amount: string;
  transaction_date: string;
  disclosure_date: string;
}

export interface CongressStats {
  period_days: number;
  total_trades: number;
  buys: number;
  sells: number;
  buy_sell_ratio: number;
  top_tickers: [string, number][];
  top_politicians: [string, number][];
  party_breakdown: Record<string, number>;
  timestamp: string;
  error?: string;
}
