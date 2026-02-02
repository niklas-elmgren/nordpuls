import { cn, getSignalColor } from "@/lib/utils";

interface SignalBadgeProps {
  action: string;
  confidence?: string;
  className?: string;
}

export function SignalBadge({ action, confidence, className }: SignalBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border",
        getSignalColor(action),
        className
      )}
    >
      {action}
      {confidence && (
        <span className="opacity-60 font-normal">({confidence})</span>
      )}
    </span>
  );
}
