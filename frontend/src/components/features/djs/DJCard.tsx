'use client';

import { Radio, Users, CheckCircle2, TrendingUp, Clock } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import type { DJ } from '@/services/djSubmissionService';

interface DJCardProps {
  dj: DJ;
  trackId?: string | null;
}

export function DJCard({ dj, trackId }: DJCardProps) {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="bg-card rounded-lg border hover:border-primary/50 transition-all hover:shadow-md overflow-hidden">
      {/* Avatar */}
      <div className="relative h-48 bg-gradient-to-br from-primary/20 to-primary/5">
        {dj.avatar_url ? (
          <img
            src={dj.avatar_url}
            alt={dj.full_name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Radio className="h-16 w-16 text-muted-foreground opacity-30" />
          </div>
        )}
        
        {dj.is_verified && (
          <div className="absolute top-3 right-3 p-1.5 rounded-full bg-blue-500">
            <CheckCircle2 className="h-4 w-4 text-white" />
          </div>
        )}
      </div>

      <div className="p-4">
        {/* Name & Username */}
        <div className="mb-3">
          <h3 className="text-lg font-bold mb-1 line-clamp-1">{dj.full_name}</h3>
          <p className="text-sm text-muted-foreground">@{dj.username}</p>
        </div>

        {/* Bio */}
        {dj.bio && (
          <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{dj.bio}</p>
        )}

        {/* Genres */}
        <div className="flex flex-wrap gap-1 mb-4">
          {dj.genres.slice(0, 3).map((genre) => (
            <span
              key={genre}
              className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium"
            >
              {genre}
            </span>
          ))}
          {dj.genres.length > 3 && (
            <span className="px-2 py-0.5 rounded-full bg-muted text-muted-foreground text-xs font-medium">
              +{dj.genres.length - 3}
            </span>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-2 mb-4 text-xs">
          <div className="text-center p-2 rounded-lg bg-muted/50">
            <Users className="h-4 w-4 mx-auto mb-1 text-muted-foreground" />
            <p className="font-semibold">{dj.follower_count.toLocaleString()}</p>
            <p className="text-muted-foreground">Followers</p>
          </div>
          <div className="text-center p-2 rounded-lg bg-muted/50">
            <TrendingUp className="h-4 w-4 mx-auto mb-1 text-muted-foreground" />
            <p className="font-semibold">{Math.round(dj.acceptance_rate * 100)}%</p>
            <p className="text-muted-foreground">Accept</p>
          </div>
          <div className="text-center p-2 rounded-lg bg-muted/50">
            <Clock className="h-4 w-4 mx-auto mb-1 text-muted-foreground" />
            <p className="font-semibold">{dj.avg_response_time_hours}h</p>
            <p className="text-muted-foreground">Response</p>
          </div>
        </div>

        {/* Price & Action */}
        <div className="flex items-center justify-between gap-2 pt-4 border-t">
          <div>
            <p className="text-xl font-bold text-primary">
              {formatPrice(dj.submission_price)}
            </p>
            <p className="text-xs text-muted-foreground">per submission</p>
          </div>
          
          <Link href={trackId ? `/djs/${dj.id}/submit?track=${trackId}` : `/djs/${dj.id}`}>
            <Button size="sm" disabled={!dj.accepts_submissions}>
              {trackId ? 'Submit' : 'View Profile'}
            </Button>
          </Link>
        </div>

        {!dj.accepts_submissions && (
          <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-2 text-center">
            Not accepting submissions
          </p>
        )}
      </div>
    </div>
  );
}
