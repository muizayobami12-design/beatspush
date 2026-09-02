'use client';

import { useState, useEffect } from 'react';
import { UserPlus, UserMinus, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import socialService from '@/services/socialService';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

interface FollowButtonProps {
  userId: string;
  initialIsFollowing?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'outline' | 'ghost';
  showIcon?: boolean;
  showText?: boolean;
  className?: string;
  onFollowChange?: (isFollowing: boolean) => void;
}

export default function FollowButton({
  userId,
  initialIsFollowing = false,
  size = 'md',
  variant = 'default',
  showIcon = true,
  showText = true,
  className,
  onFollowChange,
}: FollowButtonProps) {
  const { user } = useAuthStore();
  const [isFollowing, setIsFollowing] = useState(initialIsFollowing);
  const [loading, setLoading] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    if (user && user.id !== userId) {
      checkFollowStatus();
    }
  }, [userId, user]);

  const checkFollowStatus = async () => {
    try {
      const result = await socialService.isFollowing(userId);
      setIsFollowing(result.is_following);
    } catch (error) {
      console.error('Failed to check follow status:', error);
    }
  };

  // Don't show follow button for own profile
  if (user?.id === userId) {
    return null;
  }

  const handleClick = async () => {
    if (!user || loading) {
      if (!user) {
        alert('Please sign in to follow users');
      }
      return;
    }

    const previousState = isFollowing;

    // Optimistic update
    setIsFollowing(!isFollowing);
    onFollowChange?.(!isFollowing);

    try {
      setLoading(true);

      if (isFollowing) {
        await socialService.unfollowUser(userId);
      } else {
        await socialService.followUser(userId);
      }
    } catch (error) {
      console.error('Failed to toggle follow:', error);
      // Revert on error
      setIsFollowing(previousState);
      onFollowChange?.(previousState);
      alert('Failed to update follow status');
    } finally {
      setLoading(false);
    }
  };

  const buttonSize = size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'default';
  const iconSize = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5';

  const getButtonContent = () => {
    if (isFollowing) {
      if (isHovered) {
        return (
          <>
            {showIcon && <UserMinus className={cn(iconSize, showText && 'mr-2')} />}
            {showText && <span>Unfollow</span>}
          </>
        );
      }
      return (
        <>
          {showIcon && <Check className={cn(iconSize, showText && 'mr-2')} />}
          {showText && <span>Following</span>}
        </>
      );
    }

    return (
      <>
        {showIcon && <UserPlus className={cn(iconSize, showText && 'mr-2')} />}
        {showText && <span>Follow</span>}
      </>
    );
  };

  return (
    <Button
      variant={isFollowing ? (isHovered ? 'destructive' : 'outline') : variant}
      size={buttonSize}
      onClick={handleClick}
      disabled={loading}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={cn(
        'transition-all',
        isFollowing && !isHovered && 'border-green-500 text-green-600 hover:text-green-700',
        className
      )}
    >
      {getButtonContent()}
    </Button>
  );
}
