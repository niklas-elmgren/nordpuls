import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-bg-tertiary",
        className
      )}
    />
  );
}

export function StockCardSkeleton() {
  return (
    <div className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
      <div className="flex justify-between mb-3">
        <div>
          <Skeleton className="h-3 w-16 mb-2" />
          <Skeleton className="h-4 w-24" />
        </div>
        <Skeleton className="h-5 w-10" />
      </div>
      <Skeleton className="h-8 w-32 mb-3" />
      <Skeleton className="h-4 w-20" />
    </div>
  );
}

export function BriefingSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-6 w-64" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
      <div className="grid gap-4 mt-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-bg-secondary border border-border-subtle rounded-lg p-5">
            <Skeleton className="h-5 w-32 mb-3" />
            <Skeleton className="h-8 w-24 mb-2" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3 mt-1" />
          </div>
        ))}
      </div>
    </div>
  );
}
