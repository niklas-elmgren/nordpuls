"use client";

import { useEffect, useState } from "react";
import { Clock, Circle } from "lucide-react";
import { getMarketStatus } from "@/lib/utils";

export function Header() {
  const [time, setTime] = useState("");
  const [market, setMarket] = useState({ status: "", label: "", color: "" });

  useEffect(() => {
    function update() {
      setTime(
        new Date().toLocaleTimeString("sv-SE", {
          timeZone: "Europe/Stockholm",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      );
      setMarket(getMarketStatus());
    }
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-12 bg-bg-secondary border-b border-border-subtle flex items-center justify-between px-6 shrink-0">
      <div />

      <div className="flex items-center gap-6">
        {/* Market status */}
        <div className="flex items-center gap-2 text-sm">
          <Circle
            className={`w-2.5 h-2.5 fill-current ${market.color}`}
          />
          <span className="text-text-secondary">
            OMX Stockholm:{" "}
            <span className={market.color}>{market.label}</span>
          </span>
        </div>

        {/* Clock */}
        <div className="flex items-center gap-2 text-sm text-text-secondary">
          <Clock className="w-3.5 h-3.5" />
          <span className="font-mono text-xs">{time}</span>
          <span className="text-text-muted">CET</span>
        </div>
      </div>
    </header>
  );
}
