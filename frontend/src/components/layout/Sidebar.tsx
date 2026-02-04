"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Sun,
  Moon,
  Landmark,
  TrendingUp,
  Rocket,
  Calculator,
} from "lucide-react";
import { cn } from "@/lib/utils";
import Image from "next/image";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/briefing/morning", label: "Morgonbrief", icon: Sun },
  { href: "/briefing/evening", label: "Kvällsbrief", icon: Moon },
  { href: "/rockets", label: "Raket-historik", icon: Rocket },
  { href: "/rockets/simulator", label: "Simulator", icon: Calculator },
  { href: "/congress", label: "Kongresshandel", icon: Landmark },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-bg-secondary border-r border-border-subtle flex flex-col shrink-0">
      {/* Logo */}
      <div className="p-5 border-b border-border-subtle">
        <Link href="/" className="flex items-center gap-3">
          <TrendingUp className="w-6 h-6 text-accent" />
          <span className="font-semibold text-lg tracking-wide text-text-primary">
            NORDPULS
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent/10 text-accent"
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary"
              )}
            >
              <item.icon className="w-4.5 h-4.5" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border-subtle">
        <p className="text-xs text-text-muted">
          Data: Yahoo Finance (15 min fördröjning)
        </p>
      </div>
    </aside>
  );
}
