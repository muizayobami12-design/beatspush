'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Heart, Play, Pause, ShoppingCart, Music2, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAudioStore } from '@/store/audioStore';
import { useCartStore } from '@/store/cartStore';
import type { Beat } from '@/types';
import { toast } from 'sonner';

interface BeatCardProps {
  beat: Beat;
}

export function BeatCard({ beat }: BeatCardProps) {
  const [isFavorited, setIsFavorited] = useState(beat.isFavorited || false);
  const { currentBeat, isPlaying, playBeat, pauseBeat } = useAudioStore();
  const { addToCart } = useCartStore();
  
  const isCurrentBeat = currentBeat?.id === beat.id;
  const isThisPlaying = isCurrentBeat && isPlaying;

  const handlePlayPause = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isThisPlaying) {
      pauseBeat();
    } else {
      playBeat(beat);
    }
  };

  const handleFavorite = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      const newFavoriteState = !isFavorited;
      setIsFavorited(newFavoriteState);
      
      if (newFavoriteState) {
        // API call to favorite
        await fetch(`/api/v1/beats/${beat.id}/favorite`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        toast.success(`Added "${beat.title}" to favorites`);
      } else {
        // API call to unfavorite
        await fetch(`/api/v1/beats/${beat.id}/favorite`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
        });
        toast.info(`Removed "${beat.title}" from favorites`);
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
      setIsFavorited(isFavorited); // Revert state
      toast.error('Failed to update favorite');
    }
  };

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(beat, 'lease');
    
    toast.success(`Added "${beat.title}" to cart`, {
      action: {
        label: 'View Cart',
        onClick: () => window.location.href = '/cart',
      },
    });
    
    console.log('Added to cart:', beat.title);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Link href={`/beats/${beat.id}`}>
      <div className="group relative bg-card rounded-lg border hover:border-primary/50 transition-all hover:shadow-lg overflow-hidden">
        {/* Cover Art / Thumbnail */}
        <div className="relative aspect-square overflow-hidden">
          {beat.thumbnailUrl ? (
            <div className="relative w-full h-full bg-gradient-to-br from-primary/20 to-primary/5">
              <img
                src={beat.thumbnailUrl}
                alt={beat.title}
                className="w-full h-full object-cover transition-transform group-hover:scale-105"
              />
            </div>
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-cyan-500/20 flex items-center justify-center">
              <div className="p-6 rounded-full bg-gradient-to-br from-purple-500 to-pink-500">
                <Music2 className="h-12 w-12 text-white" />
              </div>
            </div>
          )}
          
          {/* Play Button Overlay */}
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <Button
              size="lg"
              onClick={handlePlayPause}
              className="rounded-full h-16 w-16 p-0"
            >
              {isThisPlaying ? (
                <Pause className="h-8 w-8" fill="currentColor" />
              ) : (
                <Play className="h-8 w-8" fill="currentColor" />
              )}
            </Button>
          </div>

          {/* Favorite Button */}
          <button
            onClick={handleFavorite}
            className="absolute top-2 right-2 p-2 rounded-full bg-background/80 backdrop-blur-sm hover:bg-background transition-colors"
          >
            <Heart
              className={`h-5 w-5 ${
                isFavorited ? 'fill-red-500 text-red-500' : 'text-foreground'
              }`}
            />
          </button>

          {/* Duration */}
          <div className="absolute bottom-2 left-2 px-2 py-1 rounded-md bg-background/80 backdrop-blur-sm text-xs font-medium">
            {formatDuration(beat.duration)}
          </div>

          {/* Purchased Badge */}
          {beat.isPurchased && (
            <div className="absolute top-2 left-2 px-2 py-1 rounded-md bg-green-500 text-white text-xs font-medium flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3" />
              Owned
            </div>
          )}
        </div>

        {/* Beat Info */}
        <div className="p-4">
          {/* Title */}
          <h3 className="font-semibold text-lg mb-1 line-clamp-1 group-hover:text-primary transition-colors">
            {beat.title}
          </h3>

          {/* Producer */}
          <div className="flex items-center gap-1 mb-3">
            <p className="text-sm text-muted-foreground line-clamp-1">
              by {beat.creator.fullName}
            </p>
            {beat.creator.isVerified && (
              <CheckCircle2 className="h-3 w-3 text-blue-500 flex-shrink-0" />
            )}
          </div>

          {/* Details */}
          <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3">
            <span className="px-2 py-1 rounded-md bg-primary/10 text-primary font-medium">
              {beat.genre}
            </span>
            <span>{beat.tempo} BPM</span>
            <span>{beat.key}</span>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
            <span className="flex items-center gap-1">
              <Play className="h-3 w-3" />
              {beat.playCount.toLocaleString()}
            </span>
            <span className="flex items-center gap-1">
              <Heart className="h-3 w-3" />
              {beat.favoriteCount}
            </span>
          </div>

          {/* Price and Action */}
          <div className="flex items-center justify-between gap-2">
            <div>
              <p className="text-2xl font-bold text-primary">
                {formatPrice(beat.price)}
              </p>
              <p className="text-xs text-muted-foreground">Lease Price</p>
            </div>
            
            <Button
              size="sm"
              onClick={handleAddToCart}
              className="gap-1.5"
            >
              <ShoppingCart className="h-4 w-4" />
              Add
            </Button>
          </div>
        </div>
      </div>
    </Link>
  );
}
