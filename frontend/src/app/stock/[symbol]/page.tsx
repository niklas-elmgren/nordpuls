"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useStockAnalysis } from "@/hooks/useStockData";
import { Skeleton } from "@/components/ui/Skeleton";
import { SignalBadge } from "@/components/stock/SignalBadge";
import { PriceChart } from "@/components/stock/PriceChart";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Newspaper,
  Landmark,
  Activity,
} from "lucide-react";
import {
  cn,
  formatPrice,
  formatChange,
  formatMarketCap,
  getChangeColor,
} from "@/lib/utils";

export default function StockDetailPage() {
  const params = useParams();
  const symbol = decodeURIComponent(params.symbol as string);
  const { data: analysis, isLoading, error } = useStockAnalysis(symbol);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto space-y-6">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-12 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-5xl mx-auto">
        <Link href="/" className="flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary mb-6">
          <ArrowLeft className="w-4 h-4" />
          Tillbaka
        </Link>
        <p className="text-signal-red">Kunde inte hämta data för {symbol}</p>
      </div>
    );
  }

  const stock = analysis.stock_data;
  const signal = analysis.signal;
  const congress = analysis.congress_activity;
  const changeColor = getChangeColor(stock.change_percent);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Back link */}
      <Link
        href="/"
        className="flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary"
      >
        <ArrowLeft className="w-4 h-4" />
        Dashboard
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-text-tertiary font-medium tracking-wider uppercase">
            {stock.symbol}
          </p>
          <h1 className="text-3xl font-semibold text-text-primary mt-1">
            {analysis.name}
          </h1>
        </div>
        {signal && (
          <SignalBadge
            action={signal.type.split(" ")[0]}
            className="text-sm"
          />
        )}
      </div>

      {/* Price section */}
      <div className="bg-bg-secondary border border-border-subtle rounded-lg p-6">
        <div className="flex items-baseline gap-4 mb-4">
          <span className="text-4xl font-semibold font-mono font-tabular text-text-primary">
            {formatPrice(stock.current_price, stock.currency)}
          </span>
          <span
            className={cn(
              "text-lg font-mono font-tabular font-medium flex items-center gap-1",
              changeColor
            )}
          >
            {stock.change_percent > 0 && (
              <TrendingUp className="w-5 h-5" />
            )}
            {stock.change_percent < 0 && (
              <TrendingDown className="w-5 h-5" />
            )}
            {formatChange(stock.change_percent)}
          </span>
        </div>

        {/* Metrics grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-border-subtle">
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
              Volym vs snitt
            </p>
            <p className={cn(
              "text-sm font-mono font-tabular font-medium",
              stock.volume_vs_avg > 1.5 ? "text-signal-amber" : "text-text-primary"
            )}>
              {stock.volume_vs_avg.toFixed(1)}x
              {stock.volume_vs_avg > 1.5 && (
                <Activity className="inline w-3 h-3 ml-1" />
              )}
            </p>
          </div>
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
              52v Hög
            </p>
            <p className="text-sm font-mono font-tabular text-text-primary">
              {stock.high_52w ?? "N/A"}
            </p>
          </div>
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
              52v Låg
            </p>
            <p className="text-sm font-mono font-tabular text-text-primary">
              {stock.low_52w ?? "N/A"}
            </p>
          </div>
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">
              Börsvärde
            </p>
            <p className="text-sm font-mono font-tabular text-text-primary">
              {formatMarketCap(stock.market_cap)}
            </p>
          </div>
        </div>
      </div>

      {/* Price chart */}
      <PriceChart symbol={symbol} />

      {/* Signal reasons */}
      {signal && signal.reasons.length > 0 && (
        <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-accent" />
            Signalanalys
          </h2>
          <ul className="space-y-2">
            {signal.reasons.map((reason, i) => (
              <li
                key={i}
                className="text-sm text-text-secondary flex items-start gap-2"
              >
                <span className="text-text-muted mt-0.5">-</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Unusual activity flags */}
      {analysis.unusual_activity.length > 0 && (
        <div className="bg-signal-amber/5 border border-signal-amber/20 rounded-lg p-5">
          <h2 className="text-sm font-medium text-signal-amber mb-3">
            Ovanlig aktivitet
          </h2>
          <ul className="space-y-1.5">
            {analysis.unusual_activity.map((flag, i) => (
              <li key={i} className="text-sm text-text-secondary">
                {flag}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Two-column layout: News + Congress */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* News */}
        <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
            <Newspaper className="w-4 h-4 text-accent" />
            Nyheter
            <span className="text-xs text-text-muted ml-auto">
              Sentiment:{" "}
              <span
                className={cn(
                  analysis.news_summary.sentiment === "positive" && "text-signal-green",
                  analysis.news_summary.sentiment === "negative" && "text-signal-red",
                  analysis.news_summary.sentiment === "neutral" && "text-text-secondary"
                )}
              >
                {analysis.news_summary.sentiment}
              </span>
            </span>
          </h2>
          {analysis.recent_headlines.length > 0 ? (
            <ul className="space-y-2">
              {analysis.recent_headlines.map((headline, i) => (
                <li
                  key={i}
                  className="text-sm text-text-secondary border-b border-border-subtle pb-2 last:border-0"
                >
                  {headline}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-text-muted">
              Inga nyheter hittades.
            </p>
          )}
        </div>

        {/* Congress */}
        <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
            <Landmark className="w-4 h-4 text-accent" />
            Kongresshandel
          </h2>
          {congress?.has_congress_activity ? (
            <div className="space-y-3">
              <p className="text-sm text-text-secondary">
                {congress.sentiment_description}
              </p>
              <div className="flex gap-4 text-sm">
                <span className="text-signal-green">
                  {congress.buys} köp
                </span>
                <span className="text-signal-red">
                  {congress.sells} sälj
                </span>
                <span className="text-text-muted">
                  {congress.total_trades} totalt
                </span>
              </div>
              {congress.politicians_involved &&
                congress.politicians_involved.length > 0 && (
                  <div>
                    <p className="text-xs text-text-muted mb-1">
                      Politiker:
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {congress.politicians_involved
                        .slice(0, 5)
                        .map((pol, i) => (
                          <span
                            key={i}
                            className="text-xs bg-bg-tertiary text-text-secondary px-2 py-0.5 rounded"
                          >
                            {pol}
                          </span>
                        ))}
                    </div>
                  </div>
                )}
            </div>
          ) : (
            <p className="text-sm text-text-muted">
              Ingen kongressaktivitet senaste 90 dagarna.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
