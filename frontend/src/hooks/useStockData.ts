"use client";

import useSWR from "swr";
import { fetchAPI } from "@/lib/api";
import type { WatchlistStock, StockAnalysis, OHLCVRecord } from "@/types/stock";

const fetcher = <T>(path: string) => fetchAPI<T>(path);

interface AllStocksParams {
  cap?: string | null;
  search?: string;
  limit?: number;
  offset?: number;
  sortBy?: string;
  sortDesc?: boolean;
}

interface AllStocksResponse {
  stocks: WatchlistStock[];
  total: number;
  limit: number;
  offset: number;
}

interface TopMoversResponse {
  gainers: WatchlistStock[];
  losers: WatchlistStock[];
}

interface CapSize {
  id: string;
  name: string;
  count: number;
}

export function useAllStocks(params: AllStocksParams = {}) {
  const { cap, search, limit = 50, offset = 0, sortBy = "change_percent", sortDesc = true } = params;

  const queryParams = new URLSearchParams();
  if (cap) queryParams.set("cap", cap);
  if (search) queryParams.set("search", search);
  queryParams.set("limit", limit.toString());
  queryParams.set("offset", offset.toString());
  if (sortBy) queryParams.set("sort_by", sortBy);
  queryParams.set("sort_desc", sortDesc.toString());

  const key = `/api/stocks/all?${queryParams.toString()}`;

  return useSWR<AllStocksResponse>(key, fetcher, {
    refreshInterval: 60_000,
    revalidateOnFocus: false,
  });
}

export function useTopMovers() {
  return useSWR<TopMoversResponse>(
    "/api/stocks/top-movers",
    fetcher,
    { refreshInterval: 60_000 }
  );
}

export function useCapSizes() {
  return useSWR<{ caps: CapSize[] }>(
    "/api/stocks/caps",
    fetcher,
    { revalidateOnFocus: false }
  );
}

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
