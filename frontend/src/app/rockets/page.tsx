"use client";

import { useRocketsHistory } from "@/hooks/useBriefing";
import { BriefingSkeleton } from "@/components/ui/Skeleton";
import {
  Rocket,
  TrendingUp,
  TrendingDown,
  Trophy,
  Target,
  AlertTriangle,
  Calendar,
  BarChart3,
} from "lucide-react";
import { cn, formatPrice, formatChange, getChangeColor } from "@/lib/utils";
import Link from "next/link";

export default function RocketsHistoryPage() {
  const { data, isLoading, error } = useRocketsHistory(30);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <BriefingSkeleton />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-signal-amber/5 border border-signal-amber/20 rounded-lg p-4">
          <p className="text-sm text-signal-amber">
            Kunde inte ladda rakethistorik.
          </p>
        </div>
      </div>
    );
  }

  const { history, stats } = data;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-gradient-to-br from-signal-green/20 to-accent/20 rounded-xl flex items-center justify-center shrink-0">
          <Rocket className="w-6 h-6 text-signal-green" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Raket-historik
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Så har morgonens raketval presterat
          </p>
        </div>
      </div>

      {/* Stats overview */}
      {stats.total_picks > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-4 h-4 text-text-muted" />
              <span className="text-xs text-text-muted uppercase">Totalt</span>
            </div>
            <p className="text-2xl font-semibold text-text-primary">
              {stats.total_picks}
            </p>
            <p className="text-xs text-text-secondary">
              raketer ({stats.total_days} dagar)
            </p>
          </div>

          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-signal-green" />
              <span className="text-xs text-text-muted uppercase">Win Rate</span>
            </div>
            <p className={cn(
              "text-2xl font-semibold",
              stats.win_rate >= 50 ? "text-signal-green" : "text-signal-red"
            )}>
              {stats.win_rate}%
            </p>
            <p className="text-xs text-text-secondary">
              {stats.total_winners}W / {stats.total_losers}L
            </p>
          </div>

          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-accent" />
              <span className="text-xs text-text-muted uppercase">Snitt/raket</span>
            </div>
            <p className={cn(
              "text-2xl font-semibold font-mono",
              getChangeColor(stats.avg_return)
            )}>
              {stats.avg_return >= 0 ? "+" : ""}{stats.avg_return}%
            </p>
            <p className="text-xs text-text-secondary">
              genomsnittlig avkastning
            </p>
          </div>

          <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-4 h-4 text-signal-amber" />
              <span className="text-xs text-text-muted uppercase">Total</span>
            </div>
            <p className={cn(
              "text-2xl font-semibold font-mono",
              getChangeColor(stats.total_return)
            )}>
              {stats.total_return >= 0 ? "+" : ""}{stats.total_return}%
            </p>
            <p className="text-xs text-text-secondary">
              sammanlagd avkastning
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-bg-secondary border border-border-subtle rounded-lg p-6 text-center">
          <Rocket className="w-12 h-12 text-text-muted mx-auto mb-3" />
          <p className="text-text-secondary">
            Ingen rakethistorik ännu. Första raketarna valdes idag -
            kom tillbaka efter kvällsbriefet för att se resultatet!
          </p>
        </div>
      )}

      {/* Best/Worst picks */}
      {stats.best_pick && stats.worst_pick && (
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-signal-green/5 border border-signal-green/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Trophy className="w-4 h-4 text-signal-green" />
              <span className="text-sm font-medium text-signal-green">Bästa raketen</span>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-primary">
                  {stats.best_pick.name}
                </p>
                <p className="text-xs text-text-muted">{stats.best_pick.date}</p>
              </div>
              <span className="text-lg font-semibold font-mono text-signal-green">
                +{stats.best_pick.change_percent.toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="bg-signal-red/5 border border-signal-red/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-signal-red" />
              <span className="text-sm font-medium text-signal-red">Sämsta raketen</span>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-primary">
                  {stats.worst_pick.name}
                </p>
                <p className="text-xs text-text-muted">{stats.worst_pick.date}</p>
              </div>
              <span className="text-lg font-semibold font-mono text-signal-red">
                {stats.worst_pick.change_percent.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* History by day */}
      {history.length > 0 && (
        <div>
          <h2 className="text-lg font-medium text-text-primary mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-text-muted" />
            Daglig historik
          </h2>
          <div className="space-y-4">
            {history.map((day) => (
              <div
                key={day.date}
                className="bg-bg-secondary border border-border-subtle rounded-lg overflow-hidden"
              >
                <div className="px-4 py-3 border-b border-border-subtle flex items-center justify-between">
                  <span className="text-sm font-medium text-text-primary">
                    {day.date}
                  </span>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-signal-green">
                      {day.summary.winners}W
                    </span>
                    <span className="text-signal-red">
                      {day.summary.losers}L
                    </span>
                    <span className={cn(
                      "font-mono font-semibold",
                      getChangeColor(day.summary.total_return_percent)
                    )}>
                      {day.summary.total_return_percent >= 0 ? "+" : ""}
                      {day.summary.total_return_percent.toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div className="divide-y divide-border-subtle">
                  {day.rockets.map((rocket) => (
                    <Link
                      key={rocket.symbol}
                      href={`/stock/${encodeURIComponent(rocket.symbol)}`}
                      className="flex items-center justify-between px-4 py-3 hover:bg-bg-tertiary transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          "w-8 h-8 rounded-full flex items-center justify-center",
                          rocket.change_percent >= 0
                            ? "bg-signal-green/10"
                            : "bg-signal-red/10"
                        )}>
                          {rocket.change_percent >= 0 ? (
                            <TrendingUp className="w-4 h-4 text-signal-green" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-signal-red" />
                          )}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-text-primary">
                            {rocket.name}
                          </p>
                          <p className="text-xs text-text-muted">
                            {rocket.symbol}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={cn(
                          "text-sm font-semibold font-mono",
                          getChangeColor(rocket.change_percent)
                        )}>
                          {rocket.change_percent >= 0 ? "+" : ""}
                          {rocket.change_percent.toFixed(1)}%
                        </p>
                        <p className="text-xs text-text-muted">
                          {formatPrice(rocket.morning_price, "SEK")} → {formatPrice(rocket.evening_price, "SEK")}
                        </p>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Link back to briefings */}
      <div className="grid md:grid-cols-2 gap-4 pt-4">
        <Link
          href="/briefing/morning"
          className="bg-bg-secondary border border-border-subtle rounded-lg p-4 hover:border-border-default transition-colors"
        >
          <p className="text-sm font-medium text-text-primary">Morgonbrief</p>
          <p className="text-xs text-text-secondary">
            Se dagens raketval
          </p>
        </Link>
        <Link
          href="/briefing/evening"
          className="bg-bg-secondary border border-border-subtle rounded-lg p-4 hover:border-border-default transition-colors"
        >
          <p className="text-sm font-medium text-text-primary">Kvällsbrief</p>
          <p className="text-xs text-text-secondary">
            Se hur raketarna gick
          </p>
        </Link>
      </div>
    </div>
  );
}
