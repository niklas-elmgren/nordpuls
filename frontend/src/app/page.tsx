"use client";

import { useWatchlist } from "@/hooks/useStockData";
import { useLatestBriefing } from "@/hooks/useBriefing";
import { StockCard } from "@/components/stock/StockCard";
import { StockCardSkeleton } from "@/components/ui/Skeleton";
import { AlertTriangle, TrendingUp } from "lucide-react";
import Link from "next/link";

export default function Dashboard() {
  const { data: watchlistData, error, isLoading } = useWatchlist();
  const { data: briefing } = useLatestBriefing();

  const stocks = watchlistData?.stocks || [];
  const swedish = stocks.filter((s) => s.market === "OMX Stockholm");
  const us = stocks.filter((s) => s.market !== "OMX Stockholm");

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Page title */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Dashboard</h1>
        <p className="text-sm text-text-secondary mt-1">
          Översikt av bevakade aktier och marknadsläge
        </p>
      </div>

      {/* Briefing highlight */}
      {briefing &&
        !briefing.error &&
        briefing.highlights &&
        briefing.highlights.length > 0 && (
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-signal-amber" />
              <h2 className="text-sm font-medium text-text-primary">
                Senaste signaler
              </h2>
              <Link
                href={`/briefing/${briefing.type === "morning" ? "morning" : "evening"}`}
                className="ml-auto text-xs text-accent hover:text-accent-light"
              >
                Se full brief
              </Link>
            </div>
            <div className="flex flex-wrap gap-2">
              {briefing.highlights.slice(0, 5).map((h, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 bg-bg-tertiary rounded-md px-3 py-1.5 text-xs"
                >
                  <span className="text-text-primary font-medium">
                    {h.stock}
                  </span>
                  {h.signal && (
                    <span className="text-signal-amber">{h.signal}</span>
                  )}
                  {h.alert && (
                    <span className="text-text-secondary">{h.alert}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

      {/* Error state */}
      {error && (
        <div className="bg-signal-red/5 border border-signal-red/20 rounded-lg p-4">
          <p className="text-sm text-signal-red">
            Kunde inte ansluta till API:et. Kontrollera att backend körs på port
            8000.
          </p>
        </div>
      )}

      {/* Swedish stocks */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-accent" />
          <h2 className="text-lg font-medium text-text-primary">
            OMX Stockholm
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {isLoading
            ? [1, 2, 3].map((i) => <StockCardSkeleton key={i} />)
            : swedish.map((stock, i) => (
                <StockCard key={stock.symbol} stock={stock} index={i} />
              ))}
        </div>
      </section>

      {/* US stocks */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-text-tertiary" />
          <h2 className="text-lg font-medium text-text-primary">US Market</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {isLoading
            ? [1, 2, 3].map((i) => <StockCardSkeleton key={i} />)
            : us.map((stock, i) => (
                <StockCard
                  key={stock.symbol}
                  stock={stock}
                  index={i + swedish.length}
                />
              ))}
        </div>
      </section>

      {/* Quick links to briefings */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link
          href="/briefing/morning"
          className="bg-bg-secondary border border-border-subtle rounded-lg p-5 hover:border-border-default transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-signal-amber/10 rounded-lg flex items-center justify-center">
              <span className="text-signal-amber text-sm font-mono">08:15</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-text-primary">
                Morgonbrief
              </h3>
              <p className="text-xs text-text-secondary">
                Analys inför börsöppning
              </p>
            </div>
          </div>
        </Link>
        <Link
          href="/briefing/evening"
          className="bg-bg-secondary border border-border-subtle rounded-lg p-5 hover:border-border-default transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
              <span className="text-accent text-sm font-mono">17:15</span>
            </div>
            <div>
              <h3 className="text-sm font-medium text-text-primary">
                Kvällsbrief
              </h3>
              <p className="text-xs text-text-secondary">
                Analys inför börsstängning
              </p>
            </div>
          </div>
        </Link>
      </section>
    </div>
  );
}
