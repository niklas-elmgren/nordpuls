"use client";

import { useState } from "react";
import { useCongressStats, useCongressTrades } from "@/hooks/useCongress";
import { Skeleton } from "@/components/ui/Skeleton";
import { Landmark, BarChart3, Users, List } from "lucide-react";
import { cn } from "@/lib/utils";

export default function CongressPage() {
  const [days, setDays] = useState(30);
  const { data: stats, isLoading: statsLoading } = useCongressStats(days);
  const { data: tradesData, isLoading: tradesLoading } = useCongressTrades(days);

  const trades = tradesData?.trades || [];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary flex items-center gap-3">
            <Landmark className="w-6 h-6 text-accent" />
            Kongresshandel
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Amerikanska kongressmedlemmars aktieaffärer (STOCK Act)
          </p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="bg-bg-secondary border border-border-subtle rounded-lg px-3 py-2 text-sm text-text-primary"
        >
          <option value={7}>7 dagar</option>
          <option value={30}>30 dagar</option>
          <option value={60}>60 dagar</option>
          <option value={90}>90 dagar</option>
        </select>
      </div>

      {/* Stats overview */}
      {statsLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
              <Skeleton className="h-3 w-20 mb-2" />
              <Skeleton className="h-8 w-16" />
            </div>
          ))}
        </div>
      ) : stats && !stats.error ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
              Totalt
            </p>
            <p className="text-2xl font-semibold font-mono font-tabular text-text-primary">
              {stats.total_trades}
            </p>
          </div>
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
              Köp
            </p>
            <p className="text-2xl font-semibold font-mono font-tabular text-signal-green">
              {stats.buys}
            </p>
          </div>
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
              Sälj
            </p>
            <p className="text-2xl font-semibold font-mono font-tabular text-signal-red">
              {stats.sells}
            </p>
          </div>
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
              Köp/Sälj ratio
            </p>
            <p
              className={cn(
                "text-2xl font-semibold font-mono font-tabular",
                stats.buy_sell_ratio > 1.2
                  ? "text-signal-green"
                  : stats.buy_sell_ratio < 0.8
                    ? "text-signal-red"
                    : "text-signal-amber"
              )}
            >
              {stats.buy_sell_ratio.toFixed(2)}
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-signal-red/5 border border-signal-red/20 rounded-lg p-4">
          <p className="text-sm text-signal-red">
            Kunde inte hämta kongressdata.
          </p>
        </div>
      )}

      {/* Party breakdown */}
      {stats && stats.party_breakdown && (
        <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-primary mb-4">
            Partifördelning
          </h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-semibold font-mono text-party-dem">
                {stats.party_breakdown.D || 0}
              </p>
              <p className="text-xs text-text-muted mt-1">Demokrater</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-semibold font-mono text-party-rep">
                {stats.party_breakdown.R || 0}
              </p>
              <p className="text-xs text-text-muted mt-1">Republikaner</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-semibold font-mono text-party-ind">
                {stats.party_breakdown.I || 0}
              </p>
              <p className="text-xs text-text-muted mt-1">Oberoende</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top tickers */}
        {stats && stats.top_tickers && (
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
            <h2 className="text-sm font-medium text-text-primary mb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-accent" />
              Mest handlade aktier
            </h2>
            <div className="space-y-2">
              {stats.top_tickers.slice(0, 10).map(([ticker, count], i) => (
                <div
                  key={ticker}
                  className="flex items-center justify-between text-sm"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-text-muted w-5 text-right text-xs">
                      {i + 1}.
                    </span>
                    <span className="text-text-primary font-medium font-mono">
                      {ticker}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div
                      className="h-1.5 bg-accent/30 rounded-full"
                      style={{
                        width: `${Math.min((count / (stats.top_tickers[0]?.[1] || 1)) * 80, 80)}px`,
                      }}
                    />
                    <span className="text-text-secondary text-xs font-mono w-8 text-right">
                      {count}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top politicians */}
        {stats && stats.top_politicians && (
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
            <h2 className="text-sm font-medium text-text-primary mb-4 flex items-center gap-2">
              <Users className="w-4 h-4 text-accent" />
              Mest aktiva politiker
            </h2>
            <div className="space-y-2">
              {stats.top_politicians.slice(0, 10).map(([name, count], i) => (
                <div
                  key={name}
                  className="flex items-center justify-between text-sm"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-text-muted w-5 text-right text-xs">
                      {i + 1}.
                    </span>
                    <span className="text-text-primary text-xs">
                      {name}
                    </span>
                  </div>
                  <span className="text-text-secondary text-xs font-mono">
                    {count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Recent trades table */}
      <div className="bg-bg-secondary border border-border-subtle rounded-lg overflow-hidden">
        <div className="p-5 border-b border-border-subtle">
          <h2 className="text-sm font-medium text-text-primary flex items-center gap-2">
            <List className="w-4 h-4 text-accent" />
            Senaste transaktioner
          </h2>
        </div>

        {tradesLoading ? (
          <div className="p-5 space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-8 w-full" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border-subtle">
                  <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                    Politiker
                  </th>
                  <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                    Parti
                  </th>
                  <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                    Ticker
                  </th>
                  <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                    Typ
                  </th>
                  <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                    Belopp
                  </th>
                  <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                    Datum
                  </th>
                </tr>
              </thead>
              <tbody>
                {trades.slice(0, 50).map((trade, i) => {
                  const isPurchase = trade.type
                    .toLowerCase()
                    .includes("purchase");
                  return (
                    <tr
                      key={i}
                      className="border-b border-border-subtle hover:bg-bg-tertiary transition-colors"
                    >
                      <td className="p-3 text-text-primary text-xs">
                        {trade.politician}
                      </td>
                      <td className="p-3">
                        <span
                          className={cn(
                            "text-xs font-medium",
                            trade.party === "D" || trade.party === "Democrat"
                              ? "text-party-dem"
                              : trade.party === "R" || trade.party === "Republican"
                                ? "text-party-rep"
                                : "text-party-ind"
                          )}
                        >
                          {trade.party}
                        </span>
                      </td>
                      <td className="p-3 text-text-primary font-mono text-xs font-medium">
                        {trade.ticker}
                      </td>
                      <td className="p-3">
                        <span
                          className={cn(
                            "text-xs",
                            isPurchase
                              ? "text-signal-green"
                              : "text-signal-red"
                          )}
                        >
                          {isPurchase ? "Köp" : "Sälj"}
                        </span>
                      </td>
                      <td className="p-3 text-text-secondary text-xs">
                        {trade.amount}
                      </td>
                      <td className="p-3 text-text-muted text-xs font-mono">
                        {trade.transaction_date?.slice(0, 10)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
