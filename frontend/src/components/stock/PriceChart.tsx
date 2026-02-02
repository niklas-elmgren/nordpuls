"use client";

import { useEffect, useRef, useState } from "react";
import {
  createChart,
  ColorType,
  CandlestickSeries,
  HistogramSeries,
  type IChartApi,
} from "lightweight-charts";
import { useStockHistory } from "@/hooks/useStockData";
import { Skeleton } from "@/components/ui/Skeleton";
import { cn } from "@/lib/utils";

const PERIOD_OPTIONS = [
  { label: "1V", days: 7 },
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "6M", days: 180 },
  { label: "1Å", days: 365 },
];

interface PriceChartProps {
  symbol: string;
}

export function PriceChart({ symbol }: PriceChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [days, setDays] = useState(90);
  const { data, isLoading } = useStockHistory(symbol, days);

  useEffect(() => {
    if (!chartContainerRef.current || !data?.data || data.data.length === 0)
      return;

    const container = chartContainerRef.current;

    const chart = createChart(container, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#94A3B8",
        fontSize: 11,
        fontFamily: "'JetBrains Mono', monospace",
      },
      grid: {
        vertLines: { color: "rgba(255,255,255,0.03)" },
        horzLines: { color: "rgba(255,255,255,0.03)" },
      },
      crosshair: {
        vertLine: {
          color: "rgba(59,130,246,0.3)",
          labelBackgroundColor: "#3B82F6",
        },
        horzLine: {
          color: "rgba(59,130,246,0.3)",
          labelBackgroundColor: "#3B82F6",
        },
      },
      rightPriceScale: {
        borderColor: "rgba(255,255,255,0.06)",
      },
      timeScale: {
        borderColor: "rgba(255,255,255,0.06)",
        timeVisible: false,
      },
      width: container.clientWidth,
      height: 320,
    });

    chartRef.current = chart;

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#22C55E",
      downColor: "#EF4444",
      borderUpColor: "#22C55E",
      borderDownColor: "#EF4444",
      wickUpColor: "#22C55E",
      wickDownColor: "#EF4444",
    });

    const chartData = data.data.map((d) => ({
      time: d.time as string,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    candleSeries.setData(chartData);

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });

    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.85, bottom: 0 },
    });

    const volumeData = data.data.map((d) => ({
      time: d.time as string,
      value: d.volume,
      color:
        d.close >= d.open
          ? "rgba(34,197,94,0.15)"
          : "rgba(239,68,68,0.15)",
    }));

    volumeSeries.setData(volumeData);

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
    };
  }, [data]);

  if (isLoading) {
    return (
      <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
        <Skeleton className="h-5 w-32 mb-4" />
        <Skeleton className="h-[320px] w-full" />
      </div>
    );
  }

  return (
    <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-medium text-text-primary">
          Kursutveckling
        </h2>
        <div className="flex gap-1">
          {PERIOD_OPTIONS.map((opt) => (
            <button
              key={opt.days}
              onClick={() => setDays(opt.days)}
              className={cn(
                "px-2.5 py-1 text-xs rounded-md transition-colors",
                days === opt.days
                  ? "bg-accent text-white"
                  : "text-text-muted hover:text-text-secondary hover:bg-bg-tertiary"
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
      <div ref={chartContainerRef} />
    </div>
  );
}
