"use client";

import { useEveningBriefing } from "@/hooks/useBriefing";
import { BriefingSkeleton } from "@/components/ui/Skeleton";
import { SignalBadge } from "@/components/stock/SignalBadge";
import { Moon, Landmark, AlertTriangle, Shield, Rocket, TrendingUp, TrendingDown, Target } from "lucide-react";
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

      {/* Raket-uppföljning */}
      {briefing.rocket_followup && briefing.rocket_followup.length > 0 && (
        <div className="bg-gradient-to-r from-accent/10 to-signal-amber/10 border border-accent/30 rounded-lg p-5">
          <h2 className="text-base font-semibold text-accent mb-4 flex items-center gap-2">
            <Rocket className="w-5 h-5" />
            Raket-uppföljning
          </h2>
          <p className="text-xs text-text-secondary mb-4">
            Så gick morgonens raketval - rekommendation inför stängning
          </p>
          <div className="space-y-4">
            {briefing.rocket_followup.map((rocket) => {
              const isProfit = (rocket.day_change_percent || 0) >= 0;
              const StatusIcon = rocket.status === "TARGET_HIT" ? Target : isProfit ? TrendingUp : TrendingDown;
              const statusColor = rocket.status === "TARGET_HIT" ? "text-signal-green" :
                rocket.status === "STOP_LOSS" ? "text-signal-red" :
                isProfit ? "text-signal-green" : "text-signal-red";

              return (
                <div
                  key={rocket.symbol}
                  className={cn(
                    "bg-bg-primary/50 border rounded-lg p-4",
                    rocket.status === "TARGET_HIT" && "border-signal-green/40",
                    rocket.status === "STOP_LOSS" && "border-signal-red/40",
                    !["TARGET_HIT", "STOP_LOSS"].includes(rocket.status) && "border-border-subtle"
                  )}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-xs text-text-tertiary tracking-wider uppercase">
                        {rocket.symbol}
                      </p>
                      <p className="text-sm font-medium text-text-primary">
                        {rocket.name}
                      </p>
                    </div>
                    <div className={cn("flex items-center gap-1 text-sm font-semibold", statusColor)}>
                      <StatusIcon className="w-4 h-4" />
                      {rocket.day_change_percent !== undefined && (
                        <span>{rocket.day_change_percent >= 0 ? "+" : ""}{rocket.day_change_percent.toFixed(1)}%</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-baseline gap-4 mb-3 text-sm">
                    <div>
                      <span className="text-text-muted">Morgon: </span>
                      <span className="font-mono font-tabular text-text-secondary">
                        {formatPrice(rocket.morning_price, "SEK")}
                      </span>
                    </div>
                    <div>
                      <span className="text-text-muted">Nu: </span>
                      <span className="font-mono font-tabular text-text-primary font-medium">
                        {formatPrice(rocket.current_price, "SEK")}
                      </span>
                    </div>
                  </div>

                  <div className={cn(
                    "rounded-md p-3 text-sm",
                    rocket.status === "TARGET_HIT" && "bg-signal-green/10",
                    rocket.status === "STOP_LOSS" && "bg-signal-red/10",
                    !["TARGET_HIT", "STOP_LOSS"].includes(rocket.status) && "bg-bg-tertiary"
                  )}>
                    <p className="font-medium mb-1">{rocket.recommendation}</p>
                    <p className="text-xs text-text-secondary">{rocket.message}</p>
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
