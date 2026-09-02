'use client';

import { Play, Pause, Heart, Download, Crown } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useAudioStore } from '@/store/audioStore';
import { trackService, type Track } from '@/services/trackService';
import { useState } from 'react';

interface TrackCardProps {
  track: Track;
}

export function TrackCard({ track }: TrackCardProps) {
  const { currentTrack, isPlaying, play, pause } = useAudioStore();
  const [isLiked, setIsLiked] = useState(track.is_liked || false);
  const [likeCount, setLikeCount] = useState(track.like_count);

  const isThisPlaying = currentTrack?.id === track.id && isPlaying;

  const handlePlayPause = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (isThisPlaying) {
      pause();
    } else {
      play({
        id: track.id,
        title: track.title,
        artist: track.artist_name,
        audioUrl: track.audio_url,
        coverUrl: track.cover_art_url,
        duration: track.duration,
      });
      
      // Track play count
      try {
        await trackService.playTrack(track.id);
      } catch (error) {
        console.error('Failed to track play:', error);
      }
    }
  };

  const handleLike = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    try {
      if (isLiked) {
        await trackService.unlikeTrack(track.id);
        setLikeCount((prev) => prev - 1);
      } else {
        await trackService.likeTrack(track.id);
        setLikeCount((prev) => prev + 1);
      }
      setIsLiked(!isLiked);
    } catch (error) {
      console.error('Failed to like track:', error);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  return (
    <Link href={`/tracks/${track.id}`}>
      <div className="group bg-card rounded-lg border hover:border-primary/50 transition-all hover:shadow-md p-4">
        <div className="flex items-center gap-4">
          {/* Play Button */}
          <Button
            size="icon"
            onClick={handlePlayPause}
            className="rounded-full h-12 w-12 flex-shrink-0"
          >
            {isThisPlaying ? (
              <Pause className="h-5 w-5" fill="currentColor" />
            ) : (
              <Play className="h-5 w-5" fill="currentColor" />
            )}
          </Button>

          {/* Cover Art */}
          <div className="w-12 h-12 rounded-md overflow-hidden bg-gradient-to-br from-primary/20 to-primary/5 flex-shrink-0">
            {track.cover_art_url ? (
              <img
                src={track.cover_art_url}
                alt={track.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Play className="h-6 w-6 text-muted-foreground opacity-50" />
              </div>
            )}
          </div>

          {/* Track Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-base line-clamp-1 group-hover:text-primary transition-colors">
                {track.title}
              </h3>
              {track.is_premium && (
                <Crown className="h-4 w-4 text-yellow-500 flex-shrink-0" />
              )}
            </div>
            <p className="text-sm text-muted-foreground line-clamp-1">
              {track.artist_name}
            </p>
          </div>

          {/* Genre & Duration */}
          <div className="hidden md:flex items-center gap-4 text-sm text-muted-foreground">
            <span className="px-2 py-1 rounded-md bg-primary/10 text-primary font-medium">
              {track.genre}
            </span>
            <span>{formatDuration(track.duration)}</span>
          </div>

          {/* Stats */}
          <div className="hidden lg:flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <Play className="h-4 w-4" />
              {track.play_count.toLocaleString()}
            </span>
            <span className="flex items-center gap-1">
              <Heart className="h-4 w-4" />
              {likeCount}
            </span>
          </div>

          {/* Price */}
          {track.is_premium && track.price && (
            <div className="hidden xl:block text-right">
              <p className="text-lg font-bold text-primary">{formatPrice(track.price)}</p>
              <p className="text-xs text-muted-foreground">Premium</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button
              size="icon"
              variant="ghost"
              onClick={handleLike}
            >
              <Heart
                className={`h-5 w-5 ${
                  isLiked ? 'fill-red-500 text-red-500' : 'text-foreground'
                }`}
              />
            </Button>
          </div>
        </div>
      </div>
    </Link>
  );
}
