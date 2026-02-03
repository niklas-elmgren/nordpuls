"use client";

import { useState, useMemo } from "react";
import { useAllStocks, useCapSizes, useTopMovers } from "@/hooks/useStockData";
import { useLatestBriefing } from "@/hooks/useBriefing";
import { StockCard } from "@/components/stock/StockCard";
import { StockCardSkeleton } from "@/components/ui/Skeleton";
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Search,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

const CAP_LABELS: Record<string, string> = {
  large: "Large Cap",
  mid: "Mid Cap",
  small: "Small Cap",
  first_north: "First North",
  us: "US Market",
};

export default function Dashboard() {
  const [selectedCap, setSelectedCap] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(0);
  const limit = 30;

  const { data: capsData } = useCapSizes();
  const { data: briefing } = useLatestBriefing();
  const { data: topMovers, isLoading: moversLoading } = useTopMovers();

  const { data: stocksData, error, isLoading } = useAllStocks({
    cap: selectedCap,
    search: searchQuery || undefined,
    limit,
    offset: page * limit,
    sortBy: "change_percent",
    sortDesc: true,
  });

  const stocks = stocksData?.stocks || [];
  const totalStocks = stocksData?.total || 0;
  const totalPages = Math.ceil(totalStocks / limit);

  const caps = capsData?.caps || [];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Page title */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Dashboard</h1>
        <p className="text-sm text-text-secondary mt-1">
          Alla aktier på OMX Stockholm + US Market
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

      {/* Top movers */}
      {!moversLoading && topMovers && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-signal-green" />
              <h3 className="text-sm font-medium text-text-primary">
                Dagens vinnare
              </h3>
            </div>
            <div className="space-y-2">
              {topMovers.gainers.slice(0, 5).map((stock) => (
                <Link
                  key={stock.symbol}
                  href={`/stock/${encodeURIComponent(stock.symbol)}`}
                  className="flex items-center justify-between text-sm hover:bg-bg-tertiary rounded px-2 py-1 -mx-2"
                >
                  <div>
                    <span className="text-text-primary font-medium">
                      {stock.symbol.replace(".ST", "")}
                    </span>
                    <span className="text-text-muted text-xs ml-2">
                      {stock.name}
                    </span>
                  </div>
                  <span className="text-signal-green font-mono text-xs">
                    +{stock.change_percent.toFixed(1)}%
                  </span>
                </Link>
              ))}
            </div>
          </div>

          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <TrendingDown className="w-4 h-4 text-signal-red" />
              <h3 className="text-sm font-medium text-text-primary">
                Dagens förlorare
              </h3>
            </div>
            <div className="space-y-2">
              {topMovers.losers.slice(0, 5).map((stock) => (
                <Link
                  key={stock.symbol}
                  href={`/stock/${encodeURIComponent(stock.symbol)}`}
                  className="flex items-center justify-between text-sm hover:bg-bg-tertiary rounded px-2 py-1 -mx-2"
                >
                  <div>
                    <span className="text-text-primary font-medium">
                      {stock.symbol.replace(".ST", "")}
                    </span>
                    <span className="text-text-muted text-xs ml-2">
                      {stock.name}
                    </span>
                  </div>
                  <span className="text-signal-red font-mono text-xs">
                    {stock.change_percent.toFixed(1)}%
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="bg-signal-red/5 border border-signal-red/20 rounded-lg p-4">
          <p className="text-sm text-signal-red">
            Kunde inte ansluta till API:et. Kontrollera att backend körs.
          </p>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Sök aktie..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(0);
            }}
            className="w-full bg-bg-secondary border border-border-subtle rounded-lg pl-10 pr-4 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent"
          />
        </div>

        {/* Cap filter */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => {
              setSelectedCap(null);
              setPage(0);
            }}
            className={cn(
              "px-3 py-2 text-xs rounded-lg border transition-colors",
              selectedCap === null
                ? "bg-accent text-white border-accent"
                : "bg-bg-secondary border-border-subtle text-text-secondary hover:text-text-primary"
            )}
          >
            Alla
          </button>
          {caps.map((cap) => (
            <button
              key={cap.id}
              onClick={() => {
                setSelectedCap(cap.id);
                setPage(0);
              }}
              className={cn(
                "px-3 py-2 text-xs rounded-lg border transition-colors",
                selectedCap === cap.id
                  ? "bg-accent text-white border-accent"
                  : "bg-bg-secondary border-border-subtle text-text-secondary hover:text-text-primary"
              )}
            >
              {cap.name} ({cap.count})
            </button>
          ))}
        </div>
      </div>

      {/* Results info */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-text-muted">
          Visar {stocks.length} av {totalStocks} aktier
          {selectedCap && ` i ${CAP_LABELS[selectedCap] || selectedCap}`}
          {searchQuery && ` matchande "${searchQuery}"`}
        </p>
      </div>

      {/* Stock grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 9 }).map((_, i) => <StockCardSkeleton key={i} />)
          : stocks.map((stock, i) => (
              <StockCard key={stock.symbol} stock={stock} index={i} />
            ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="p-2 rounded-lg bg-bg-secondary border border-border-subtle text-text-secondary hover:text-text-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-sm text-text-secondary px-4">
            Sida {page + 1} av {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="p-2 rounded-lg bg-bg-secondary border border-border-subtle text-text-secondary hover:text-text-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Quick links to briefings */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
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
