"use client";

import useSWR from "swr";
import { fetchAPI } from "@/lib/api";
import type { WatchlistStock, StockAnalysis, OHLCVRecord } from "@/types/stock";

const fetcher = <T>(path: string) => fetchAPI<T>(path);

export function useWatchlist() {
  return useSWR<{ stocks: WatchlistStock[] }>(
    "/api/stocks/watchlist",
    fetcher,
    { refreshInterval: 60_000 }
  );
}

export function useStockAnalysis(symbol: string) {
  return useSWR<StockAnalysis>(
    symbol ? `/api/stocks/${encodeURIComponent(symbol)}/analysis` : null,
    fetcher,
    { refreshInterval: 60_000 }
  );
}

export function useStockHistory(symbol: string, days: number = 30) {
  return useSWR<{ symbol: string; data: OHLCVRecord[] }>(
    symbol ? `/api/stocks/${encodeURIComponent(symbol)}/history?days=${days}` : null,
    fetcher
  );
}
