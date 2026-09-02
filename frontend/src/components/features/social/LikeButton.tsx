'use client';

import { useState, useEffect } from 'react';
import { Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import socialService from '@/services/socialService';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

interface LikeButtonProps {
  contentType: 'beat' | 'track' | 'mix';
  contentId: string;
  initialLikes?: number;
  initialIsLiked?: boolean;
  size?: 'sm' | 'md' | 'lg';
  showCount?: boolean;
  className?: string;
}

export default function LikeButton({
  contentType,
  contentId,
  initialLikes = 0,
  initialIsLiked = false,
  size = 'md',
  showCount = true,
  className,
}: LikeButtonProps) {
  const { user } = useAuthStore();
  const [likes, setLikes] = useState(initialLikes);
  const [isLiked, setIsLiked] = useState(initialIsLiked);
  const [loading, setLoading] = useState(false);
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    if (user) {
      loadLikeStatus();
    }
  }, [contentType, contentId, user]);

  const loadLikeStatus = async () => {
    try {
      const result = await socialService.getLikesCount({
        content_type: contentType,
        content_id: contentId,
      });
      setLikes(result.count);
      setIsLiked(result.is_liked);
    } catch (error) {
      console.error('Failed to load like status:', error);
    }
  };

  const handleClick = async () => {
    if (!user || loading) {
      if (!user) {
        alert('Please sign in to like');
      }
      return;
    }

    const previousLikes = likes;
    const previousIsLiked = isLiked;

    // Optimistic update
    setIsLiked(!isLiked);
    setLikes(isLiked ? likes - 1 : likes + 1);
    setAnimating(true);

    try {
      setLoading(true);

      if (isLiked) {
        await socialService.unlike({
          content_type: contentType,
          content_id: contentId,
        });
      } else {
        await socialService.like({
          content_type: contentType,
          content_id: contentId,
        });
      }
    } catch (error) {
      console.error('Failed to toggle like:', error);
      // Revert on error
      setIsLiked(previousIsLiked);
      setLikes(previousLikes);
    } finally {
      setLoading(false);
      setTimeout(() => setAnimating(false), 300);
    }
  };

  const buttonSize = size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'default';
  const iconSize = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5';

  return (
    <Button
      variant={isLiked ? 'default' : 'outline'}
      size={buttonSize}
      onClick={handleClick}
      disabled={loading}
      className={cn(
        'gap-2 transition-all',
        isLiked && 'bg-red-500 hover:bg-red-600 text-white border-red-500',
        animating && 'scale-110',
        className
      )}
    >
      <Heart
        className={cn(
          iconSize,
          'transition-all',
          isLiked && 'fill-current',
          animating && 'animate-ping'
        )}
      />
      {showCount && likes > 0 && (
        <span className={cn('font-semibold', size === 'sm' && 'text-xs')}>
          {likes > 999 ? `${(likes / 1000).toFixed(1)}k` : likes}
        </span>
      )}
    </Button>
  );
}
