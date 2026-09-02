'use client';

import { useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';
import { PostCard } from './PostCard';
import { useFeed } from '@/hooks/useSocial';

interface FeedProps {
  feedType?: 'following' | 'discover' | 'trending';
  onPostClick?: (postId: string) => void;
}

export function Feed({ feedType = 'following', onPostClick }: FeedProps) {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useFeed(feedType);

  const observerTarget = useRef<HTMLDivElement>(null);

  // Infinite scroll with Intersection Observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-lg font-medium text-destructive">
          Failed to load feed
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          {error instanceof Error ? error.message : 'Please try again'}
        </p>
      </div>
    );
  }

  // Get all posts from pages
  const posts = data?.pages.flatMap((page: any) => page.posts) || [];

  // Empty state
  if (posts.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-lg font-medium text-foreground">No posts yet</p>
        <p className="text-sm text-muted-foreground mt-1">
          {feedType === 'following'
            ? 'Follow creators to see their posts here'
            : 'Be the first to post something!'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          onCommentClick={() => onPostClick?.(post.id)}
        />
      ))}

      {/* Infinite scroll trigger */}
      <div ref={observerTarget} className="py-4">
        {isFetchingNextPage && (
          <div className="flex items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
          </div>
        )}
        {!hasNextPage && posts.length > 0 && (
          <p className="text-center text-sm text-muted-foreground">
            You're all caught up!
          </p>
        )}
      </div>
    </div>
  );
}
