"use client";

import Link from "next/link";
import { TrendingUp, TrendingDown, Minus, Activity } from "lucide-react";
import { cn, formatPrice, formatChange, getChangeColor } from "@/lib/utils";
import type { WatchlistStock } from "@/types/stock";

interface StockCardProps {
  stock: WatchlistStock;
  index: number;
}

export function StockCard({ stock, index }: StockCardProps) {
  const changeColor = getChangeColor(stock.change_percent);
  const isPositive = stock.change_percent > 0;
  const isNegative = stock.change_percent < 0;
  const highVolume = stock.volume_vs_avg > 1.5;

  if (stock.error) {
    return (
      <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5 opacity-50">
        <p className="text-sm text-text-muted">{stock.name}</p>
        <p className="text-xs text-signal-red mt-1">Kunde inte hämta data</p>
      </div>
    );
  }

  return (
    <Link
      href={`/stock/${encodeURIComponent(stock.symbol)}`}
      className={cn(
        "bg-bg-secondary border border-border-subtle rounded-lg p-5",
        "hover:border-border-default hover:bg-bg-tertiary transition-all duration-200",
        "animate-fade-in-up block"
      )}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="text-xs text-text-tertiary font-medium tracking-wider uppercase">
            {stock.symbol}
          </p>
          <p className="text-sm font-medium text-text-primary mt-0.5">
            {stock.name}
          </p>
        </div>
        <span className="text-xs text-text-muted bg-bg-tertiary px-2 py-0.5 rounded">
          {stock.market === "OMX Stockholm" ? "OMX" : stock.market}
        </span>
      </div>

      {/* Price */}
      <div className="mb-3">
        <p className="text-2xl font-semibold font-mono font-tabular text-text-primary">
          {formatPrice(stock.current_price, stock.currency)}
        </p>
      </div>

      {/* Change & volume */}
      <div className="flex items-center justify-between">
        <div className={cn("flex items-center gap-1.5 text-sm font-medium", changeColor)}>
          {isPositive && <TrendingUp className="w-3.5 h-3.5" />}
          {isNegative && <TrendingDown className="w-3.5 h-3.5" />}
          {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5" />}
          <span className="font-mono font-tabular">
            {formatChange(stock.change_percent)}
          </span>
        </div>

        {highVolume && (
          <div className="flex items-center gap-1 text-signal-amber text-xs">
            <Activity className="w-3 h-3" />
            <span>{stock.volume_vs_avg.toFixed(1)}x vol</span>
          </div>
        )}
      </div>
    </Link>
  );
}
