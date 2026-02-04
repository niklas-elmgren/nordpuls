"use client";

import { useMorningBriefing } from "@/hooks/useBriefing";
import { BriefingSkeleton } from "@/components/ui/Skeleton";
import { SignalBadge } from "@/components/stock/SignalBadge";
import { Sun, Landmark, AlertTriangle, Shield, Rocket, Target, TrendingUp, TrendingDown, Activity } from "lucide-react";
import {
  cn,
  formatPrice,
  formatChange,
  getChangeColor,
  formatTimestamp,
} from "@/lib/utils";

export default function MorningBriefingPage() {
  const { data: briefing, isLoading, error } = useMorningBriefing();

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <BriefingSkeleton />
      </div>
    );
  }

  if (error || !briefing) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-signal-amber/5 border border-signal-amber/20 rounded-lg p-4">
          <p className="text-sm text-signal-amber">
            Morgonbriefen genereras... Första gången kan ta upp till 30 sekunder.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-signal-amber/10 rounded-xl flex items-center justify-center shrink-0">
          <Sun className="w-6 h-6 text-signal-amber" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Morgonbrief
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            08:15 CET - Inför börsöppning
          </p>
          {briefing.generated_at && (
            <p className="text-xs text-text-muted mt-0.5">
              Genererad: {formatTimestamp(briefing.generated_at)}
            </p>
          )}
        </div>
      </div>

      {/* Summary */}
      <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
        <p className="text-sm text-text-secondary leading-relaxed">
          {briefing.summary}
        </p>
      </div>

      {/* Dagens Trades - Daytrading picks */}
      {briefing.rocket_picks && briefing.rocket_picks.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Rocket className="w-5 h-5 text-signal-green" />
            <h2 className="text-lg font-semibold text-text-primary">
              Dagens Trades
            </h2>
          </div>
          <p className="text-sm text-text-secondary -mt-2">
            Köp vid öppning, sälj vid stängning. Följ stoploss!
          </p>

          <div className="grid gap-4 md:grid-cols-2">
            {briefing.rocket_picks.map((rocket, i) => (
              <div
                key={rocket.symbol}
                className="bg-gradient-to-br from-signal-green/5 to-bg-secondary border border-signal-green/30 rounded-xl p-5 space-y-4"
              >
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="bg-signal-green text-bg-primary text-xs font-bold px-2 py-0.5 rounded">
                        TRADE #{i + 1}
                      </span>
                      {rocket.trend === "up" ? (
                        <TrendingUp className="w-4 h-4 text-signal-green" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-signal-red" />
                      )}
                    </div>
                    <p className="text-lg font-semibold text-text-primary mt-1">
                      {rocket.name}
                    </p>
                    <p className="text-xs text-text-muted">{rocket.symbol}</p>
                  </div>
                  {rocket.rsi && (
                    <div className="text-right">
                      <p className="text-xs text-text-muted">RSI</p>
                      <p className={cn(
                        "text-lg font-mono font-semibold",
                        rocket.rsi < 30 ? "text-signal-green" :
                        rocket.rsi > 70 ? "text-signal-red" : "text-text-primary"
                      )}>
                        {rocket.rsi.toFixed(0)}
                      </p>
                    </div>
                  )}
                </div>

                {/* Price levels */}
                <div className="grid grid-cols-3 gap-3 bg-bg-primary/50 rounded-lg p-3">
                  <div className="text-center">
                    <p className="text-xs text-text-muted mb-1">Entry</p>
                    <p className="text-base font-mono font-semibold text-text-primary">
                      {rocket.entry_price?.toFixed(2) || rocket.morning_price?.toFixed(2)}
                    </p>
                    <p className="text-xs text-text-muted">kr</p>
                  </div>
                  <div className="text-center border-x border-border-subtle">
                    <p className="text-xs text-signal-red mb-1">Stoploss</p>
                    <p className="text-base font-mono font-semibold text-signal-red">
                      {rocket.stoploss?.toFixed(2) || "—"}
                    </p>
                    <p className="text-xs text-signal-red">
                      {rocket.stoploss_pct?.toFixed(1) || "-4"}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-signal-green mb-1">Target</p>
                    <p className="text-base font-mono font-semibold text-signal-green">
                      {rocket.target?.toFixed(2) || "—"}
                    </p>
                    <p className="text-xs text-signal-green">
                      +{rocket.target_pct?.toFixed(1) || "5"}%
                    </p>
                  </div>
                </div>

                {/* Technical signals */}
                <div className="space-y-2">
                  <p className="text-xs font-medium text-text-secondary flex items-center gap-1">
                    <Activity className="w-3 h-3" /> Teknisk analys
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {rocket.tech_signals?.slice(0, 3).map((signal, j) => (
                      <span
                        key={j}
                        className="text-xs bg-bg-tertiary text-text-secondary px-2 py-1 rounded"
                      >
                        {signal}
                      </span>
                    ))}
                    {rocket.volume_spike && rocket.volume_spike > 1.2 && (
                      <span className="text-xs bg-signal-amber/20 text-signal-amber px-2 py-1 rounded">
                        Volym: {rocket.volume_spike.toFixed(1)}x
                      </span>
                    )}
                  </div>
                </div>

                {/* Reasons */}
                {rocket.reasons && rocket.reasons.length > 0 && (
                  <div className="border-t border-border-subtle pt-3">
                    <ul className="space-y-1">
                      {rocket.reasons.slice(0, 2).map((reason, j) => (
                        <li key={j} className="text-xs text-text-secondary flex items-start gap-2">
                          <span className="text-signal-green mt-0.5">•</span>
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="bg-signal-amber/10 border border-signal-amber/30 rounded-lg p-3 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-signal-amber shrink-0 mt-0.5" />
            <p className="text-xs text-text-secondary">
              <strong className="text-signal-amber">Viktigt:</strong> Sälj ALLTID vid stoploss om kursen går emot dig.
              Följ upp i kvällsbriefet för säljrekommendation.
            </p>
          </div>
        </div>
      )}

      {/* Highlights */}
      {briefing.highlights && briefing.highlights.length > 0 && (
        <div className="bg-signal-amber/5 border border-signal-amber/20 rounded-lg p-5">
          <h2 className="text-sm font-medium text-signal-amber mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Viktiga signaler
          </h2>
          <div className="space-y-2">
            {briefing.highlights.map((h, i) => (
              <div key={i} className="text-sm text-text-secondary">
                <span className="text-text-primary font-medium">
                  {h.stock}
                </span>
                {" - "}
                {h.signal || h.alert}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div>
        <h2 className="text-lg font-medium text-text-primary mb-4">
          Rekommendationer
        </h2>
        <div className="space-y-3">
          {briefing.recommendations.map((rec, i) => (
            <div
              key={rec.symbol}
              className="bg-bg-secondary border border-border-subtle rounded-lg p-5 animate-fade-in-up"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-xs text-text-tertiary tracking-wider uppercase">
                    {rec.symbol}
                  </p>
                  <p className="text-sm font-medium text-text-primary">
                    {rec.name}
                  </p>
                </div>
                <SignalBadge action={rec.action} confidence={rec.confidence} />
              </div>

              <div className="flex items-baseline gap-3 mb-3">
                <span className="text-xl font-semibold font-mono font-tabular text-text-primary">
                  {formatPrice(rec.price, rec.symbol.endsWith(".ST") ? "SEK" : "USD")}
                </span>
                <span
                  className={cn(
                    "text-sm font-mono font-tabular",
                    getChangeColor(rec.change_percent)
                  )}
                >
                  {formatChange(rec.change_percent)}
                </span>
              </div>

              {rec.reasons.length > 0 && (
                <ul className="space-y-1">
                  {rec.reasons.map((reason, j) => (
                    <li
                      key={j}
                      className="text-xs text-text-secondary flex items-start gap-2"
                    >
                      <span className="text-text-muted mt-0.5">-</span>
                      {reason}
                    </li>
                  ))}
                </ul>
              )}

              <div className="flex items-center gap-4 mt-3 pt-3 border-t border-border-subtle text-xs text-text-muted">
                <span>
                  Nyhetssentiment:{" "}
                  <span
                    className={cn(
                      rec.news_sentiment === "positive" && "text-signal-green",
                      rec.news_sentiment === "negative" && "text-signal-red"
                    )}
                  >
                    {rec.news_sentiment}
                  </span>
                </span>
                {rec.congress_signal && (
                  <span>Kongress: {rec.congress_signal}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Congress notable */}
      {briefing.congress_notable && briefing.congress_notable.length > 0 && (
        <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
            <Landmark className="w-4 h-4 text-accent" />
            Kongressnoteringar
          </h2>
          <div className="space-y-2">
            {briefing.congress_notable.map((c, i) => (
              <div key={i} className="text-sm text-text-secondary">
                <span className="text-text-primary font-medium">
                  {c.ticker}
                </span>
                {" - "}
                {c.description} ({c.total_trades} transaktioner)
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4 flex items-start gap-3">
        <Shield className="w-4 h-4 text-text-muted shrink-0 mt-0.5" />
        <p className="text-xs text-text-muted leading-relaxed">
          {briefing.disclaimer}
        </p>
      </div>
    </div>
  );
}
