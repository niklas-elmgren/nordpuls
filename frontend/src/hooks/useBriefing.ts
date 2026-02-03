"use client";

import useSWR from "swr";
import { fetchAPI } from "@/lib/api";
import type { Briefing, RocketsHistory } from "@/types/briefing";

const fetcher = <T>(path: string) => fetchAPI<T>(path);

export function useMorningBriefing() {
  return useSWR<Briefing>("/api/briefings/morning", fetcher, {
    refreshInterval: 300_000,
  });
}

export function useEveningBriefing() {
  return useSWR<Briefing>("/api/briefings/evening", fetcher, {
    refreshInterval: 300_000,
  });
}

export function useLatestBriefing() {
  return useSWR<Briefing>("/api/briefings/latest", fetcher, {
    refreshInterval: 300_000,
  });
}

export function useRocketsHistory(days: number = 30) {
  return useSWR<RocketsHistory>(
    `/api/briefings/rockets/history?days=${days}`,
    fetcher,
    { refreshInterval: 300_000 }
  );
}
