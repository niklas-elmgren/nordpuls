"use client";

import useSWR from "swr";
import { fetchAPI } from "@/lib/api";
import type { ClimateOverview } from "@/types/climate";

const fetcher = <T>(path: string) => fetchAPI<T>(path);

export function useMarketClimate() {
  return useSWR<ClimateOverview>("/api/climate/overview", fetcher, {
    refreshInterval: 300_000,
    revalidateOnFocus: false,
  });
}
