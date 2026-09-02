import { Skeleton } from '@/components/ui/skeleton';

export function BeatCardSkeleton() {
  return (
    <div className="bg-card rounded-lg border overflow-hidden">
      {/* Cover Art Skeleton */}
      <Skeleton className="aspect-square w-full" />
      
      {/* Beat Info Skeleton */}
      <div className="p-4 space-y-3">
        {/* Title */}
        <Skeleton className="h-6 w-3/4" />
        
        {/* Producer */}
        <Skeleton className="h-4 w-1/2" />
        
        {/* Details (Genre, BPM, Key) */}
        <div className="flex items-center gap-3">
          <Skeleton className="h-6 w-16" />
          <Skeleton className="h-4 w-12" />
          <Skeleton className="h-4 w-12" />
        </div>
        
        {/* Stats */}
        <div className="flex items-center gap-4">
          <Skeleton className="h-4 w-12" />
          <Skeleton className="h-4 w-12" />
        </div>
        
        {/* Price and Button */}
        <div className="flex items-center justify-between gap-2 pt-2">
          <div className="space-y-1">
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-3 w-16" />
          </div>
          <Skeleton className="h-9 w-20" />
        </div>
      </div>
    </div>
  );
}

export function BeatGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <BeatCardSkeleton key={i} />
      ))}
    </div>
  );
}
