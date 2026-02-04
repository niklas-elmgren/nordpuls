"use client";

import { useInvestmentSimulation } from "@/hooks/useBriefing";
import { BriefingSkeleton } from "@/components/ui/Skeleton";
import {
  Rocket,
  TrendingUp,
  TrendingDown,
  Calculator,
  Wallet,
  PiggyBank,
  ArrowRight,
  Calendar,
} from "lucide-react";
import { cn, formatPrice, getChangeColor } from "@/lib/utils";
import Link from "next/link";
import type { SimulationTrade, SimulationTotals } from "@/types/briefing";

function formatKr(value: number): string {
  return value.toLocaleString("sv-SE", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }) + " kr";
}

interface RocketTableProps {
  title: string;
  rocketNumber: 1 | 2;
  trades: SimulationTrade[];
  totals: SimulationTotals;
}

function RocketTable({ title, rocketNumber, trades, totals }: RocketTableProps) {
  const isProfit = totals.profit_1000 >= 0;
  const bgGradient = rocketNumber === 1
    ? "from-accent/10 to-signal-green/10"
    : "from-signal-amber/10 to-accent/10";

  return (
    <div className="space-y-4">
      {/* Header with totals */}
      <div className={cn(
        "bg-gradient-to-r rounded-xl p-5 border border-border-subtle",
        bgGradient
      )}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
            <Rocket className={cn(
              "w-5 h-5",
              rocketNumber === 1 ? "text-accent" : "text-signal-amber"
            )} />
            {title}
          </h2>
          <span className="text-xs text-text-muted bg-bg-secondary px-2 py-1 rounded">
            {totals.trade_count} trades
          </span>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* 1000 kr */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-text-muted">
              <Wallet className="w-3 h-3" />
              Investerat: 1 000 kr
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-text-secondary">
                {formatKr(totals.start_1000)}
              </span>
              <ArrowRight className="w-4 h-4 text-text-muted" />
              <span className={cn(
                "text-xl font-bold font-mono",
                isProfit ? "text-signal-green" : "text-signal-red"
              )}>
                {formatKr(totals.end_1000)}
              </span>
            </div>
            <div className={cn(
              "text-sm font-mono",
              isProfit ? "text-signal-green" : "text-signal-red"
            )}>
              {isProfit ? "+" : ""}{formatKr(totals.profit_1000)} ({isProfit ? "+" : ""}{totals.return_percent}%)
            </div>
          </div>

          {/* 10000 kr */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs text-text-muted">
              <PiggyBank className="w-3 h-3" />
              Investerat: 10 000 kr
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-text-secondary">
                {formatKr(totals.start_10000)}
              </span>
              <ArrowRight className="w-4 h-4 text-text-muted" />
              <span className={cn(
                "text-xl font-bold font-mono",
                isProfit ? "text-signal-green" : "text-signal-red"
              )}>
                {formatKr(totals.end_10000)}
              </span>
            </div>
            <div className={cn(
              "text-sm font-mono",
              isProfit ? "text-signal-green" : "text-signal-red"
            )}>
              {isProfit ? "+" : ""}{formatKr(totals.profit_10000)} ({isProfit ? "+" : ""}{totals.return_percent}%)
            </div>
          </div>
        </div>
      </div>

      {/* Trade history table */}
      {trades.length > 0 && (
        <div className="bg-bg-secondary border border-border-subtle rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-border-subtle">
            <span className="text-sm font-medium text-text-primary flex items-center gap-2">
              <Calendar className="w-4 h-4 text-text-muted" />
              Trade-historik
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-bg-tertiary">
                <tr>
                  <th className="px-4 py-2 text-left text-xs text-text-muted font-medium">Datum</th>
                  <th className="px-4 py-2 text-left text-xs text-text-muted font-medium">Aktie</th>
                  <th className="px-4 py-2 text-right text-xs text-text-muted font-medium">Kurs</th>
                  <th className="px-4 py-2 text-right text-xs text-text-muted font-medium">%</th>
                  <th className="px-4 py-2 text-right text-xs text-text-muted font-medium">1000 kr</th>
                  <th className="px-4 py-2 text-right text-xs text-text-muted font-medium">10000 kr</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle">
                {trades.map((trade, idx) => {
                  const isWin = trade.change_percent >= 0;
                  return (
                    <tr
                      key={`${trade.date}-${trade.symbol}`}
                      className="hover:bg-bg-tertiary transition-colors"
                    >
                      <td className="px-4 py-3 text-text-secondary whitespace-nowrap">
                        {trade.date}
                      </td>
                      <td className="px-4 py-3">
                        <Link
                          href={`/stock/${encodeURIComponent(trade.symbol)}`}
                          className="hover:text-accent transition-colors"
                        >
                          <span className="font-medium text-text-primary">
                            {trade.name}
                          </span>
                          <span className="text-xs text-text-muted ml-2">
                            {trade.symbol}
                          </span>
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-right text-text-secondary whitespace-nowrap">
                        <span className="text-xs">
                          {formatPrice(trade.morning_price, "SEK")} → {formatPrice(trade.evening_price, "SEK")}
                        </span>
                      </td>
                      <td className={cn(
                        "px-4 py-3 text-right font-mono whitespace-nowrap",
                        getChangeColor(trade.change_percent)
                      )}>
                        {isWin ? "+" : ""}{trade.change_percent.toFixed(1)}%
                      </td>
                      <td className={cn(
                        "px-4 py-3 text-right font-mono whitespace-nowrap",
                        trade.profit_1000 >= 0 ? "text-signal-green" : "text-signal-red"
                      )}>
                        <div>{trade.profit_1000 >= 0 ? "+" : ""}{trade.profit_1000.toFixed(0)} kr</div>
                        <div className="text-xs text-text-muted">= {formatKr(trade.cumulative_1000)}</div>
                      </td>
                      <td className={cn(
                        "px-4 py-3 text-right font-mono whitespace-nowrap",
                        trade.profit_10000 >= 0 ? "text-signal-green" : "text-signal-red"
                      )}>
                        <div>{trade.profit_10000 >= 0 ? "+" : ""}{trade.profit_10000.toFixed(0)} kr</div>
                        <div className="text-xs text-text-muted">= {formatKr(trade.cumulative_10000)}</div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default function SimulatorPage() {
  const { data, isLoading, error } = useInvestmentSimulation(30);

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <BriefingSkeleton />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-signal-amber/5 border border-signal-amber/20 rounded-lg p-4">
          <p className="text-sm text-signal-amber">
            Kunde inte ladda simuleringsdata.
          </p>
        </div>
      </div>
    );
  }

  const { rocket_1, rocket_2, combined } = data;
  const hasTrades = rocket_1.trades.length > 0 || rocket_2.trades.length > 0;
  const combinedProfit = combined.totals.profit_1000 >= 0;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-gradient-to-br from-accent/20 to-signal-green/20 rounded-xl flex items-center justify-center shrink-0">
          <Calculator className="w-6 h-6 text-accent" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Investeringssimulator
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Vad hade du tjänat om du investerat i kursraketerna?
          </p>
          <p className="text-xs text-text-muted mt-1">
            Simulerar att du köper vid öppning och säljer vid stängning varje dag
          </p>
        </div>
      </div>

      {hasTrades ? (
        <>
          {/* Combined summary */}
          <div className="bg-bg-secondary border border-border-subtle rounded-xl p-6">
            <h2 className="text-sm font-medium text-text-muted mb-4 uppercase tracking-wider">
              Total avkastning (båda raketerna)
            </h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Wallet className="w-4 h-4" />
                  2 x 1 000 kr = 2 000 kr investerat
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-lg text-text-secondary">
                    {formatKr(combined.totals.start_1000)}
                  </span>
                  <ArrowRight className="w-5 h-5 text-text-muted" />
                  <span className={cn(
                    "text-3xl font-bold font-mono",
                    combinedProfit ? "text-signal-green" : "text-signal-red"
                  )}>
                    {formatKr(combined.totals.end_1000)}
                  </span>
                </div>
                <div className={cn(
                  "text-lg font-mono",
                  combinedProfit ? "text-signal-green" : "text-signal-red"
                )}>
                  {combinedProfit ? "+" : ""}{formatKr(combined.totals.profit_1000)}
                  <span className="text-sm ml-2">
                    ({combinedProfit ? "+" : ""}{combined.totals.return_percent}%)
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <PiggyBank className="w-4 h-4" />
                  2 x 10 000 kr = 20 000 kr investerat
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-lg text-text-secondary">
                    {formatKr(combined.totals.start_10000)}
                  </span>
                  <ArrowRight className="w-5 h-5 text-text-muted" />
                  <span className={cn(
                    "text-3xl font-bold font-mono",
                    combinedProfit ? "text-signal-green" : "text-signal-red"
                  )}>
                    {formatKr(combined.totals.end_10000)}
                  </span>
                </div>
                <div className={cn(
                  "text-lg font-mono",
                  combinedProfit ? "text-signal-green" : "text-signal-red"
                )}>
                  {combinedProfit ? "+" : ""}{formatKr(combined.totals.profit_10000)}
                  <span className="text-sm ml-2">
                    ({combinedProfit ? "+" : ""}{combined.totals.return_percent}%)
                  </span>
                </div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-border-subtle text-xs text-text-muted">
              Baserat på {combined.totals.total_trades} trades under de senaste 30 dagarna
            </div>
          </div>

          {/* Individual rocket tables */}
          <div className="space-y-8">
            <RocketTable
              title="Kursraket #1"
              rocketNumber={1}
              trades={rocket_1.trades}
              totals={rocket_1.totals}
            />

            <RocketTable
              title="Kursraket #2"
              rocketNumber={2}
              trades={rocket_2.trades}
              totals={rocket_2.totals}
            />
          </div>
        </>
      ) : (
        <div className="bg-bg-secondary border border-border-subtle rounded-lg p-8 text-center">
          <Calculator className="w-12 h-12 text-text-muted mx-auto mb-4" />
          <p className="text-text-secondary mb-2">
            Ingen rakethistorik att simulera ännu.
          </p>
          <p className="text-sm text-text-muted">
            Kom tillbaka efter några dagar med kursraketer!
          </p>
        </div>
      )}

      {/* Navigation links */}
      <div className="grid md:grid-cols-3 gap-4 pt-4">
        <Link
          href="/rockets"
          className="bg-bg-secondary border border-border-subtle rounded-lg p-4 hover:border-border-default transition-colors"
        >
          <p className="text-sm font-medium text-text-primary">Raket-historik</p>
          <p className="text-xs text-text-secondary">
            Se alla tidigare raketer
          </p>
        </Link>
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
            Se hur raketerna gick
          </p>
        </Link>
      </div>

      {/* Disclaimer */}
      <div className="bg-bg-secondary border border-border-subtle rounded-lg p-4 text-xs text-text-muted">
        <strong className="text-text-secondary">OBS:</strong> Detta är en simulering baserad på historiska data.
        Tidigare resultat garanterar inte framtida avkastning. Courtage och andra avgifter ingår inte i beräkningen.
        Investera aldrig mer än du har råd att förlora.
      </div>
    </div>
  );
}
