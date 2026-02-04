"use client";

import { useEveningBriefing } from "@/hooks/useBriefing";
import { BriefingSkeleton } from "@/components/ui/Skeleton";
import { SignalBadge } from "@/components/stock/SignalBadge";
import { Moon, Landmark, AlertTriangle, Shield, Rocket, TrendingUp, TrendingDown, Target, CheckCircle, XCircle, DollarSign } from "lucide-react";
import {
  cn,
  formatPrice,
  formatChange,
  getChangeColor,
  formatTimestamp,
} from "@/lib/utils";

export default function EveningBriefingPage() {
  const { data: briefing, isLoading, error } = useEveningBriefing();

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
        <div className="bg-accent/5 border border-accent/20 rounded-lg p-4">
          <p className="text-sm text-accent">
            Kvällsbriefen genereras... Första gången kan ta upp till 30 sekunder.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center shrink-0">
          <Moon className="w-6 h-6 text-accent" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Kvällsbrief
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            17:15 CET - Inför börsstängning
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

      {/* Dagens Resultat - Trade Followup */}
      {briefing.rocket_followup && briefing.rocket_followup.length > 0 && (
        <div className="space-y-4">
          {/* Summary stats */}
          {(() => {
            const total = briefing.rocket_followup.length;
            const winners = briefing.rocket_followup.filter(r => (r.day_change_percent || 0) >= 0).length;
            const totalReturn = briefing.rocket_followup.reduce((sum, r) => sum + (r.day_change_percent || 0), 0);
            const avgReturn = totalReturn / total;

            return (
              <div className="bg-gradient-to-r from-bg-secondary to-bg-tertiary border border-border-subtle rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-accent" />
                    Dagens Resultat
                  </h2>
                  <div className="flex items-center gap-2">
                    {totalReturn >= 0 ? (
                      <CheckCircle className="w-5 h-5 text-signal-green" />
                    ) : (
                      <XCircle className="w-5 h-5 text-signal-red" />
                    )}
                    <span className={cn(
                      "text-2xl font-bold font-mono",
                      totalReturn >= 0 ? "text-signal-green" : "text-signal-red"
                    )}>
                      {totalReturn >= 0 ? "+" : ""}{totalReturn.toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-text-primary">{winners}/{total}</p>
                    <p className="text-xs text-text-muted">Vinnare</p>
                  </div>
                  <div>
                    <p className={cn(
                      "text-2xl font-bold font-mono",
                      avgReturn >= 0 ? "text-signal-green" : "text-signal-red"
                    )}>
                      {avgReturn >= 0 ? "+" : ""}{avgReturn.toFixed(1)}%
                    </p>
                    <p className="text-xs text-text-muted">Snitt/trade</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-text-primary">
                      {Math.round((winners / total) * 100)}%
                    </p>
                    <p className="text-xs text-text-muted">Win rate</p>
                  </div>
                </div>
              </div>
            );
          })()}

          {/* Individual trades */}
          <div className="space-y-3">
            {briefing.rocket_followup.map((rocket) => {
              const isProfit = (rocket.day_change_percent || 0) >= 0;
              const isTargetHit = rocket.status === "TARGET_HIT";
              const isStopLoss = rocket.status === "STOP_LOSS";

              return (
                <div
                  key={rocket.symbol}
                  className={cn(
                    "border rounded-xl p-4 transition-all",
                    isTargetHit && "bg-signal-green/5 border-signal-green/40",
                    isStopLoss && "bg-signal-red/5 border-signal-red/40",
                    !isTargetHit && !isStopLoss && isProfit && "bg-signal-green/5 border-signal-green/20",
                    !isTargetHit && !isStopLoss && !isProfit && "bg-signal-red/5 border-signal-red/20"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "w-10 h-10 rounded-full flex items-center justify-center",
                        isProfit ? "bg-signal-green/20" : "bg-signal-red/20"
                      )}>
                        {isTargetHit ? (
                          <Target className="w-5 h-5 text-signal-green" />
                        ) : isProfit ? (
                          <TrendingUp className="w-5 h-5 text-signal-green" />
                        ) : (
                          <TrendingDown className="w-5 h-5 text-signal-red" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-text-primary">{rocket.name}</p>
                        <p className="text-xs text-text-muted">{rocket.symbol}</p>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className={cn(
                        "text-xl font-bold font-mono",
                        isProfit ? "text-signal-green" : "text-signal-red"
                      )}>
                        {(rocket.day_change_percent || 0) >= 0 ? "+" : ""}
                        {(rocket.day_change_percent || 0).toFixed(1)}%
                      </p>
                      <p className="text-xs text-text-muted">
                        {formatPrice(rocket.morning_price, "SEK")} → {formatPrice(rocket.current_price, "SEK")}
                      </p>
                    </div>
                  </div>

                  {/* Recommendation */}
                  <div className={cn(
                    "mt-3 rounded-lg p-3",
                    isTargetHit && "bg-signal-green/10",
                    isStopLoss && "bg-signal-red/10",
                    !isTargetHit && !isStopLoss && "bg-bg-tertiary"
                  )}>
                    <p className={cn(
                      "text-sm font-semibold",
                      isTargetHit && "text-signal-green",
                      isStopLoss && "text-signal-red",
                      !isTargetHit && !isStopLoss && "text-text-primary"
                    )}>
                      {rocket.recommendation}
                    </p>
                    <p className="text-xs text-text-secondary mt-1">{rocket.message}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Highlights */}
      {briefing.highlights && briefing.highlights.length > 0 && (
        <div className="bg-signal-amber/5 border border-signal-amber/20 rounded-lg p-5">
          <h2 className="text-sm font-medium text-signal-amber mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Dagens signaler
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
          Kvällsanalys
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
