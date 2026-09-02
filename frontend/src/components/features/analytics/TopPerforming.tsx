'use client';

import { Music, Play, Heart, DollarSign, TrendingUp } from 'lucide-react';
import Image from 'next/image';

interface PerformingContent {
  id: string;
  title: string;
  coverUrl?: string;
  artist?: string;
  plays: number;
  likes: number;
  revenue: number;
  growth: number; // percentage
  type: 'beat' | 'track' | 'mix';
}

interface TopPerformingProps {
  content: PerformingContent[];
  period?: 'week' | 'month' | 'all-time';
}

export function TopPerforming({ content, period = 'month' }: TopPerformingProps) {
  // Format number with K, M suffix
  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  // Format currency in Naira
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Get type label
  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'beat':
        return 'Beat';
      case 'track':
        return 'Track';
      case 'mix':
        return 'Mix';
      default:
        return 'Content';
    }
  };

  // Get type color
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'beat':
        return 'from-purple-500 to-pink-500';
      case 'track':
        return 'from-cyan-500 to-blue-500';
      case 'mix':
        return 'from-orange-500 to-amber-500';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  // Calculate total stats
  const totalPlays = content.reduce((sum, item) => sum + item.plays, 0);
  const totalRevenue = content.reduce((sum, item) => sum + item.revenue, 0);
  const totalLikes = content.reduce((sum, item) => sum + item.likes, 0);

  return (
    <div className="bg-card rounded-xl border p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold mb-1">Top Performing Content</h3>
          <p className="text-sm text-muted-foreground">
            Your best {period === 'all-time' ? 'all-time' : `this ${period}`}
          </p>
        </div>
        <div className="p-3 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500">
          <TrendingUp className="h-6 w-6 text-white" />
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="p-3 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
          <div className="flex items-center gap-2 mb-1">
            <Play className="h-4 w-4 text-purple-500" />
            <span className="text-xs font-medium text-muted-foreground">Total Plays</span>
          </div>
          <div className="text-xl font-bold">{formatNumber(totalPlays)}</div>
        </div>

        <div className="p-3 rounded-lg bg-gradient-to-br from-pink-500/10 to-rose-500/10 border border-pink-500/20">
          <div className="flex items-center gap-2 mb-1">
            <Heart className="h-4 w-4 text-pink-500" />
            <span className="text-xs font-medium text-muted-foreground">Total Likes</span>
          </div>
          <div className="text-xl font-bold">{formatNumber(totalLikes)}</div>
        </div>

        <div className="p-3 rounded-lg bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20">
          <div className="flex items-center gap-2 mb-1">
            <DollarSign className="h-4 w-4 text-green-500" />
            <span className="text-xs font-medium text-muted-foreground">Total Revenue</span>
          </div>
          <div className="text-xl font-bold">{formatCurrency(totalRevenue)}</div>
        </div>
      </div>

      {/* Content List */}
      <div className="space-y-3">
        {content.map((item, index) => (
          <div
            key={item.id}
            className="group relative p-4 rounded-lg border bg-card hover:bg-muted/50 transition-all duration-200 hover:shadow-lg"
          >
            {/* Rank Badge */}
            <div className="absolute -top-2 -left-2 flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-amber-500 text-white text-sm font-bold shadow-lg">
              {index + 1}
            </div>

            <div className="flex items-center gap-4">
              {/* Cover Image */}
              <div className="relative w-16 h-16 rounded-lg overflow-hidden bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex-shrink-0">
                {item.coverUrl ? (
                  <Image
                    src={item.coverUrl}
                    alt={item.title}
                    fill
                    className="object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Music className="h-6 w-6 text-muted-foreground" />
                  </div>
                )}
                
                {/* Type Badge */}
                <div className={`absolute top-1 right-1 px-2 py-0.5 rounded text-[10px] font-semibold text-white bg-gradient-to-r ${getTypeColor(item.type)}`}>
                  {getTypeLabel(item.type)}
                </div>
              </div>

              {/* Content Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold truncate group-hover:text-primary transition-colors">
                      {item.title}
                    </h4>
                    {item.artist && (
                      <p className="text-sm text-muted-foreground truncate">
                        {item.artist}
                      </p>
                    )}
                  </div>
                  
                  {/* Growth Badge */}
                  {item.growth > 0 && (
                    <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-green-500/10 text-green-600 dark:text-green-400">
                      <TrendingUp className="h-3 w-3" />
                      <span className="text-xs font-semibold">+{item.growth}%</span>
                    </div>
                  )}
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-3 gap-4 mt-3">
                  <div className="flex items-center gap-2">
                    <Play className="h-4 w-4 text-purple-500" />
                    <div>
                      <div className="text-sm font-semibold">{formatNumber(item.plays)}</div>
                      <div className="text-xs text-muted-foreground">Plays</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Heart className="h-4 w-4 text-pink-500" />
                    <div>
                      <div className="text-sm font-semibold">{formatNumber(item.likes)}</div>
                      <div className="text-xs text-muted-foreground">Likes</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-green-500" />
                    <div>
                      <div className="text-sm font-semibold">{formatCurrency(item.revenue)}</div>
                      <div className="text-xs text-muted-foreground">Revenue</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {content.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="p-4 rounded-full bg-muted mb-4">
            <Music className="h-8 w-8 text-muted-foreground" />
          </div>
          <h4 className="text-lg font-semibold mb-2">No content yet</h4>
          <p className="text-sm text-muted-foreground max-w-sm">
            Upload your first beat or track to see performance insights
          </p>
        </div>
      )}
    </div>
  );
}
