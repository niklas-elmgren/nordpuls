import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(price: number, currency: string = "SEK"): string {
  if (currency === "USD") {
    return `$${price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
  return `${price.toLocaleString("sv-SE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency}`;
}

export function formatChange(change: number): string {
  const sign = change > 0 ? "+" : "";
  return `${sign}${change.toFixed(2)}%`;
}

export function formatVolume(ratio: number): string {
  return `${ratio.toFixed(1)}x`;
}

export function formatMarketCap(cap: number | null): string {
  if (!cap) return "N/A";
  if (cap >= 1e12) return `${(cap / 1e12).toFixed(1)}T`;
  if (cap >= 1e9) return `${(cap / 1e9).toFixed(1)}B`;
  if (cap >= 1e6) return `${(cap / 1e6).toFixed(1)}M`;
  return cap.toLocaleString();
}

export function getChangeColor(change: number): string {
  if (change > 0) return "text-signal-green";
  if (change < 0) return "text-signal-red";
  return "text-text-secondary";
}

export function getSignalColor(action: string): string {
  switch (action) {
    case "BUY":
      return "bg-signal-green/10 text-signal-green border-signal-green/20";
    case "SELL":
    case "AVOID":
      return "bg-signal-red/10 text-signal-red border-signal-red/20";
    case "WATCH":
      return "bg-signal-amber/10 text-signal-amber border-signal-amber/20";
    default:
      return "bg-bg-tertiary text-text-secondary border-border-subtle";
  }
}

export function getMarketStatus(): { status: string; label: string; color: string } {
  const now = new Date();
  const stockholmHour = parseInt(
    now.toLocaleString("sv-SE", { timeZone: "Europe/Stockholm", hour: "numeric", hour12: false })
  );
  const stockholmMinute = parseInt(
    now.toLocaleString("sv-SE", { timeZone: "Europe/Stockholm", minute: "numeric" })
  );
  const totalMinutes = stockholmHour * 60 + stockholmMinute;
  const day = parseInt(
    now.toLocaleString("sv-SE", { timeZone: "Europe/Stockholm", weekday: "narrow" })
  );

  // Weekend
  const dayOfWeek = now.toLocaleString("en-US", { timeZone: "Europe/Stockholm", weekday: "short" });
  if (dayOfWeek === "Sat" || dayOfWeek === "Sun") {
    return { status: "closed", label: "Stängt", color: "text-signal-red" };
  }

  if (totalMinutes < 540) {
    return { status: "pre_open", label: "Förmarknad", color: "text-signal-amber" };
  }
  if (totalMinutes < 1050) {
    return { status: "open", label: "Öppen", color: "text-signal-green" };
  }
  return { status: "closed", label: "Stängt", color: "text-signal-red" };
}

export function formatTimestamp(iso: string): string {
  try {
    const date = new Date(iso);
    return date.toLocaleString("sv-SE", {
      timeZone: "Europe/Stockholm",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}
