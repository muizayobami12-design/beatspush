'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, Sparkles, Clock, ChevronRight } from 'lucide-react';
import { searchService } from '@/services/searchService';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import type { TrendingContent, RecommendedContent } from '@/services/searchService';

export function DiscoveryFeed() {
  const [trending, setTrending] = useState<TrendingContent[]>([]);
  const [recommended, setRecommended] = useState<RecommendedContent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchContent = async () => {
      setIsLoading(true);
      const [trendingData, recommendedData] = await Promise.all([
        searchService.getTrending(),
        searchService.getRecommended(),
      ]);
      setTrending(trendingData);
      setRecommended(recommendedData);
      setIsLoading(false);
    };

    fetchContent();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-8">
        <TrendingSkeleton />
        <RecommendedSkeleton />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Trending Section */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500 to-red-500">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Trending Now</h2>
              <p className="text-sm text-muted-foreground">What's hot in the community</p>
            </div>
          </div>
          <Link href="/trending">
            <Button variant="ghost" size="sm" className="gap-1">
              View All
              <ChevronRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {trending.map((item, index) => (
            <TrendingCard key={item.id} item={item} rank={index + 1} />
          ))}
        </div>
      </section>

      {/* Recommended Section */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Recommended For You</h2>
              <p className="text-sm text-muted-foreground">Based on your taste</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommended.map((item) => (
            <RecommendedCard key={item.id} item={item} />
          ))}
        </div>
      </section>

      {/* New Releases Section */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500">
              <Clock className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Fresh Drops</h2>
              <p className="text-sm text-muted-foreground">Latest releases from producers</p>
            </div>
          </div>
          <Link href="/beats?sort=newest">
            <Button variant="ghost" size="sm" className="gap-1">
              View All
              <ChevronRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>

        <div className="text-center py-12 text-muted-foreground">
          <p>Check out the latest beats in the marketplace!</p>
          <Link href="/beats?sort=newest">
            <Button className="mt-4">Browse New Releases</Button>
          </Link>
        </div>
      </section>
    </div>
  );
}

function TrendingCard({ item, rank }: { item: TrendingContent; rank: number }) {
  const getTrendIcon = () => {
    switch (item.trend) {
      case 'hot':
        return '🔥';
      case 'up':
        return '📈';
      case 'new':
        return '✨';
      default:
        return '🎵';
    }
  };

  return (
    <Link href={`/${item.type}s/${item.id}`}>
      <div className="group relative bg-card rounded-lg border p-4 hover:border-primary/50 hover:shadow-lg transition-all">
        {/* Rank Badge */}
        <div className="absolute -top-2 -left-2 w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-red-500 text-white font-bold flex items-center justify-center text-sm shadow-lg">
          {rank}
        </div>

        {/* Trend Badge */}
        <div className="absolute top-2 right-2 text-2xl">
          {getTrendIcon()}
        </div>

        <div className="mt-2">
          <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
            {item.title}
          </h3>
          <p className="text-sm text-muted-foreground capitalize">{item.type}</p>
          
          <div className="flex items-center gap-2 mt-3 text-sm text-muted-foreground">
            <TrendingUp className="h-4 w-4" />
            <span>{item.plays.toLocaleString()} plays</span>
          </div>
        </div>
      </div>
    </Link>
  );
}

function RecommendedCard({ item }: { item: RecommendedContent }) {
  return (
    <Link href={`/${item.type}s/${item.id}`}>
      <div className="group bg-card rounded-lg border p-4 hover:border-primary/50 hover:shadow-lg transition-all">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20">
            <Sparkles className="h-5 w-5 text-purple-500" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold group-hover:text-primary transition-colors">
              {item.title}
            </h3>
            <p className="text-xs text-muted-foreground mt-1">{item.reason}</p>
            
            <div className="mt-3 flex items-center gap-2">
              <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all"
                  style={{ width: `${item.score * 100}%` }}
                />
              </div>
              <span className="text-xs font-semibold text-muted-foreground">
                {Math.round(item.score * 100)}% match
              </span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}

function TrendingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-48 bg-muted rounded animate-pulse" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    </div>
  );
}

function RecommendedSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-64 bg-muted rounded animate-pulse" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    </div>
  );
}
