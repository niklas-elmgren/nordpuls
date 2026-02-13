"use client";

import { useMarketClimate } from "@/hooks/useClimate";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  Thermometer,
  TrendingUp,
  TrendingDown,
  Minus,
  Calendar,
  Activity,
  BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { MarketIndex, CalendarEvent } from "@/types/climate";

const categoryLabels: Record<string, string> = {
  rate_decision: "Räntebesked",
  macro_data: "Makrodata",
  earnings_season: "Rapportsäsong",
  earnings_report: "Rapport",
  annual_meeting: "Stämma",
  dividend: "Utdelning",
  employment: "Arbetsmarknad",
  gdp: "BNP",
};

const impactColors: Record<string, string> = {
  high: "bg-signal-red/10 text-signal-red border-signal-red/20",
  medium: "bg-signal-amber/10 text-signal-amber border-signal-amber/20",
  low: "bg-text-muted/10 text-text-muted border-text-muted/20",
};

function TrendIcon({ trend }: { trend: string }) {
  if (trend === "up") return <TrendingUp className="w-4 h-4 text-signal-green" />;
  if (trend === "down") return <TrendingDown className="w-4 h-4 text-signal-red" />;
  return <Minus className="w-4 h-4 text-text-muted" />;
}

function formatCountdown(days: number): string {
  if (days === 0) return "Idag";
  if (days === 1) return "Imorgon";
  if (days < 0) return `${Math.abs(days)} dagar sedan`;
  return `${days} dagar`;
}

export default function KlimatPage() {
  const { data, isLoading } = useMarketClimate();

  const indices = data?.indices || [];
  const signals = data?.signals;
  const events = data?.events || [];
  const dist = signals?.signal_distribution;
  const nextEvent = events.find((e) => e.days_until >= 0);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary flex items-center gap-3">
          <Thermometer className="w-6 h-6 text-accent" />
          Aktieklimat
        </h1>
        <p className="text-sm text-text-secondary mt-1">
          Marknadsöversikt, signalfördelning och kommande ekonomiska events
        </p>
      </div>

      {/* Marknadsindex */}
      <section>
        <h2 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
          <Activity className="w-4 h-4 text-accent" />
          Marknadsindex
        </h2>
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
                <Skeleton className="h-3 w-24 mb-2" />
                <Skeleton className="h-8 w-32 mb-2" />
                <Skeleton className="h-4 w-16" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {indices.map((idx: MarketIndex) => {
              const isVix = idx.symbol === "^VIX";
              // VIX inverterar färg: hög VIX = dåligt (rött)
              const changeColor = isVix
                ? idx.change_percent > 0
                  ? "text-signal-red"
                  : idx.change_percent < 0
                    ? "text-signal-green"
                    : "text-text-muted"
                : idx.change_percent > 0
                  ? "text-signal-green"
                  : idx.change_percent < 0
                    ? "text-signal-red"
                    : "text-text-muted";

              return (
                <div
                  key={idx.symbol}
                  className="bg-bg-secondary border border-border-subtle rounded-lg p-5"
                >
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-xs text-text-muted uppercase tracking-wider">
                      {idx.symbol.replace("^", "")}
                    </p>
                    <TrendIcon trend={isVix ? (idx.trend === "up" ? "down" : idx.trend === "down" ? "up" : "neutral") : idx.trend} />
                  </div>
                  <p className="text-lg font-semibold text-text-primary truncate">
                    {idx.name}
                  </p>
                  <div className="flex items-baseline gap-3 mt-2">
                    <span className="text-2xl font-semibold font-mono font-tabular text-text-primary">
                      {idx.current_price.toLocaleString("sv-SE", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </span>
                    <span
                      className={cn(
                        "text-sm font-medium font-mono font-tabular",
                        changeColor
                      )}
                    >
                      {idx.change_percent > 0 ? "+" : ""}
                      {idx.change_percent.toFixed(2)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Signalöversikt */}
      <section>
        <h2 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-accent" />
          Signalöversikt
        </h2>
        {isLoading || !signals ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
                <Skeleton className="h-3 w-20 mb-2" />
                <Skeleton className="h-8 w-16" />
              </div>
            ))}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
                <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
                  Sentiment
                </p>
                <p
                  className={cn(
                    "text-xl font-semibold",
                    signals.overall_sentiment === "bullish"
                      ? "text-signal-green"
                      : signals.overall_sentiment === "bearish"
                        ? "text-signal-red"
                        : "text-signal-amber"
                  )}
                >
                  {signals.overall_sentiment === "bullish"
                    ? "Positivt"
                    : signals.overall_sentiment === "bearish"
                      ? "Negativt"
                      : "Neutralt"}
                </p>
              </div>
              <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
                <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
                  Snittförändring
                </p>
                <p
                  className={cn(
                    "text-xl font-semibold font-mono font-tabular",
                    signals.avg_change_percent > 0
                      ? "text-signal-green"
                      : signals.avg_change_percent < 0
                        ? "text-signal-red"
                        : "text-text-muted"
                  )}
                >
                  {signals.avg_change_percent > 0 ? "+" : ""}
                  {signals.avg_change_percent.toFixed(2)}%
                </p>
              </div>
              <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
                <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
                  Hög volym
                </p>
                <p className="text-xl font-semibold font-mono font-tabular text-text-primary">
                  {signals.high_volume_count}
                </p>
              </div>
              <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
                <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
                  Analyserade
                </p>
                <p className="text-xl font-semibold font-mono font-tabular text-text-primary">
                  {dist?.total_stocks || 0}
                </p>
              </div>
            </div>

            {/* Signalfördelning stapel */}
            {dist && dist.total_stocks > 0 && (
              <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5 mt-4">
                <p className="text-xs text-text-muted uppercase tracking-wider mb-3">
                  Signalfördelning
                </p>
                <div className="flex h-4 rounded-full overflow-hidden">
                  {dist.buy > 0 && (
                    <div
                      className="bg-signal-green"
                      style={{ width: `${(dist.buy / dist.total_stocks) * 100}%` }}
                      title={`BUY: ${dist.buy}`}
                    />
                  )}
                  {dist.watch > 0 && (
                    <div
                      className="bg-signal-amber"
                      style={{ width: `${(dist.watch / dist.total_stocks) * 100}%` }}
                      title={`WATCH: ${dist.watch}`}
                    />
                  )}
                  {dist.hold > 0 && (
                    <div
                      className="bg-text-muted/40"
                      style={{ width: `${(dist.hold / dist.total_stocks) * 100}%` }}
                      title={`HOLD: ${dist.hold}`}
                    />
                  )}
                  {dist.avoid > 0 && (
                    <div
                      className="bg-signal-red"
                      style={{ width: `${(dist.avoid / dist.total_stocks) * 100}%` }}
                      title={`AVOID: ${dist.avoid}`}
                    />
                  )}
                </div>
                <div className="flex items-center gap-4 mt-2 text-xs text-text-secondary">
                  {dist.buy > 0 && (
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-signal-green" />
                      BUY {dist.buy}
                    </span>
                  )}
                  {dist.watch > 0 && (
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-signal-amber" />
                      WATCH {dist.watch}
                    </span>
                  )}
                  {dist.hold > 0 && (
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-text-muted/40" />
                      HOLD {dist.hold}
                    </span>
                  )}
                  {dist.avoid > 0 && (
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-signal-red" />
                      AVOID {dist.avoid}
                    </span>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </section>

      {/* Nästa event */}
      {!isLoading && nextEvent && (
        <section>
          <div className="bg-accent/5 border border-accent/20 rounded-lg p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-accent uppercase tracking-wider mb-1">
                  Nästa event
                </p>
                <p className="text-lg font-semibold text-text-primary">
                  {nextEvent.title}
                </p>
                <div className="flex items-center gap-3 mt-2 text-sm text-text-secondary">
                  <span>{nextEvent.date}</span>
                  <span className="text-text-muted">|</span>
                  <span>{nextEvent.source}</span>
                  <span
                    className={cn(
                      "text-xs px-2 py-0.5 rounded-full border",
                      impactColors[nextEvent.impact] || impactColors.medium
                    )}
                  >
                    {nextEvent.impact === "high"
                      ? "Hög påverkan"
                      : nextEvent.impact === "medium"
                        ? "Medium"
                        : "Låg"}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-semibold font-mono font-tabular text-accent">
                  {formatCountdown(nextEvent.days_until)}
                </p>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Kommande events */}
      <section>
        <h2 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
          <Calendar className="w-4 h-4 text-accent" />
          Kommande events
        </h2>

        {isLoading ? (
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5 space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-8 w-full" />
            ))}
          </div>
        ) : events.length === 0 ? (
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
            <p className="text-sm text-text-muted">Inga kommande events hittades.</p>
          </div>
        ) : (
          <div className="bg-bg-secondary border border-border-subtle rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border-subtle">
                    <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                      Datum
                    </th>
                    <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                      Event
                    </th>
                    <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                      Källa
                    </th>
                    <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                      Kategori
                    </th>
                    <th className="text-left text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                      Påverkan
                    </th>
                    <th className="text-right text-xs text-text-muted uppercase tracking-wider p-3 font-medium">
                      Countdown
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((event: CalendarEvent) => (
                    <tr
                      key={event.id}
                      className={cn(
                        "border-b border-border-subtle hover:bg-bg-tertiary transition-colors",
                        event.is_active && "bg-accent/5"
                      )}
                    >
                      <td className="p-3 text-text-primary font-mono text-xs">
                        {event.date}
                      </td>
                      <td className="p-3 text-text-primary text-xs font-medium">
                        {event.title}
                      </td>
                      <td className="p-3 text-text-secondary text-xs">
                        {event.source}
                      </td>
                      <td className="p-3">
                        <span className="text-xs px-2 py-0.5 rounded-full bg-bg-tertiary text-text-secondary">
                          {categoryLabels[event.category] || event.category}
                        </span>
                      </td>
                      <td className="p-3">
                        <span
                          className={cn(
                            "text-xs px-2 py-0.5 rounded-full border",
                            impactColors[event.impact] || impactColors.medium
                          )}
                        >
                          {event.impact === "high"
                            ? "Hög"
                            : event.impact === "medium"
                              ? "Medium"
                              : "Låg"}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <span
                          className={cn(
                            "text-xs font-mono font-tabular",
                            event.days_until <= 1
                              ? "text-accent font-medium"
                              : "text-text-muted"
                          )}
                        >
                          {formatCountdown(event.days_until)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
