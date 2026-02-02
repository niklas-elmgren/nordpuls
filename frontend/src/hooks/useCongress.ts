"use client";

import useSWR from "swr";
import { fetchAPI } from "@/lib/api";
import type { CongressStats, CongressTrade } from "@/types/congress";

const fetcher = <T>(path: string) => fetchAPI<T>(path);

export function useCongressStats(days: number = 30) {
  return useSWR<CongressStats>(`/api/congress/stats?days=${days}`, fetcher, {
    refreshInterval: 600_000,
  });
}

export function useCongressTrades(days: number = 30, minAmount: string = "$1,001 -") {
  return useSWR<{ trades: CongressTrade[]; total: number }>(
    `/api/congress/recent?days=${days}&min_amount=${encodeURIComponent(minAmount)}`,
    fetcher,
    { refreshInterval: 600_000 }
  );
}
