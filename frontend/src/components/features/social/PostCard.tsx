'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import {
  Heart,
  MessageCircle,
  Share2,
  Bookmark,
  MoreVertical,
  Music,
  Calendar,
  TrendingUp,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToggleLike, useToggleBookmark } from '@/hooks/useSocial';
import { cn } from '@/lib/utils';
import type { Post } from '@/types';

interface PostCardProps {
  post: Post;
  onCommentClick?: () => void;
  onShareClick?: () => void;
  showActions?: boolean;
}

export function PostCard({
  post,
  onCommentClick,
  onShareClick,
  showActions = true,
}: PostCardProps) {
  const toggleLike = useToggleLike();
  const toggleBookmark = useToggleBookmark();
  const [isLiking, setIsLiking] = useState(false);

  const handleLike = async () => {
    if (isLiking) return;
    setIsLiking(true);
    try {
      await toggleLike.mutateAsync(post.id);
    } finally {
      setTimeout(() => setIsLiking(false), 300);
    }
  };

  const handleBookmark = () => {
    toggleBookmark.mutate(post.id);
  };

  // Get post type icon
  const getPostIcon = () => {
    switch (post.postType) {
      case 'track_share':
        return <Music className="w-4 h-4 text-primary" />;
      case 'event':
        return <Calendar className="w-4 h-4 text-blue-500" />;
      case 'milestone':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      default:
        return null;
    }
  };

  return (
    <article className="bg-card border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between p-4">
        <div className="flex items-start space-x-3 flex-1">
          {/* Avatar */}
          <Link href={`/${post.user.username || post.user.id}`}>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden flex-shrink-0">
              {post.user.avatar ? (
                <Image
                  src={post.user.avatar}
                  alt={post.user.fullName}
                  width={40}
                  height={40}
                  className="object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-white font-semibold text-sm">
                  {post?.user?.fullName?.charAt(0)?.toUpperCase() || post?.user?.email?.charAt(0)?.toUpperCase() || 'U'}
                </div>
              )}
            </div>
          </Link>

          {/* User Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <Link
                href={`/${post.user.username || post.user.id}`}
                className="font-semibold text-foreground hover:underline truncate"
              >
                {post.user.fullName}
              </Link>
              {post.user.isVerified && (
                <svg
                  className="w-4 h-4 text-primary flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                </svg>
              )}
              {getPostIcon()}
            </div>
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <span>@{post.user.username || post.user.id.slice(0, 8)}</span>
              <span>•</span>
              <span>
                {formatDistanceToNow(new Date(post.createdAt), {
                  addSuffix: true,
                })}
              </span>
              {post.visibility !== 'public' && (
                <>
                  <span>•</span>
                  <span className="capitalize">{post.visibility}</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* More Menu */}
        {showActions && (
          <Button variant="ghost" size="icon" className="flex-shrink-0">
            <MoreVertical className="w-5 h-5" />
          </Button>
        )}
      </div>

      {/* Content */}
      <div
        className="px-4 pb-3 cursor-pointer hover:bg-accent/5 transition-colors"
        onClick={onCommentClick}
      >
        <p className="text-foreground whitespace-pre-wrap break-words">
          {post.content}
        </p>
      </div>

      {/* Media */}
      {post.mediaUrl && (
        <div className="px-4 pb-3">
          <div className="relative w-full rounded-lg overflow-hidden bg-muted">
            <Image
              src={post.mediaUrl}
              alt="Post media"
              width={600}
              height={400}
              className="object-cover w-full"
            />
          </div>
        </div>
      )}

      {/* Track Share */}
      {post.postType === 'track_share' && post.track && (
        <Link href={`/beats/${post.track.id}`}>
          <div className="mx-4 mb-3 p-3 border rounded-lg hover:bg-accent transition-colors cursor-pointer">
            <div className="flex items-center space-x-3">
              {post.track.coverArtUrl ? (
                <Image
                  src={post.track.coverArtUrl}
                  alt={post.track.title}
                  width={48}
                  height={48}
                  className="rounded"
                />
              ) : (
                <div className="w-12 h-12 rounded bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center">
                  <Music className="w-6 h-6 text-white" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{post.track.title}</p>
                <p className="text-sm text-muted-foreground truncate">
                  {post.track.artistName}
                </p>
              </div>
            </div>
          </div>
        </Link>
      )}

      {/* Poll */}
      {post.postType === 'poll' && post.pollOptions && (
        <div className="px-4 pb-3 space-y-2">
          {post.pollOptions.map((option, index) => (
            <button
              key={index}
              className="w-full p-3 border rounded-lg text-left hover:bg-accent transition-colors"
            >
              {option}
            </button>
          ))}
          {post.pollEndsAt && (
            <p className="text-xs text-muted-foreground">
              Ends{' '}
              {formatDistanceToNow(new Date(post.pollEndsAt), {
                addSuffix: true,
              })}
            </p>
          )}
        </div>
      )}

      {/* Actions */}
      {showActions && (
        <>
          {/* Stats */}
          <div className="px-4 py-2 border-t flex items-center justify-between text-sm text-muted-foreground">
            <span>{post.likeCount} likes</span>
            <div className="flex items-center space-x-4">
              <span>{post.commentCount} comments</span>
              <span>{post.shareCount} shares</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="px-4 py-2 border-t flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLike}
              disabled={isLiking}
              className={cn(
                'flex items-center space-x-2',
                post.isLiked && 'text-red-500 hover:text-red-600'
              )}
            >
              <Heart
                className={cn('w-5 h-5', post.isLiked && 'fill-current')}
              />
              <span>Like</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={onCommentClick}
              className="flex items-center space-x-2"
            >
              <MessageCircle className="w-5 h-5" />
              <span>Comment</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={onShareClick}
              className="flex items-center space-x-2"
            >
              <Share2 className="w-5 h-5" />
              <span>Share</span>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleBookmark}
              className={cn(
                'flex items-center space-x-2',
                post.isBookmarked && 'text-primary'
              )}
            >
              <Bookmark
                className={cn('w-5 h-5', post.isBookmarked && 'fill-current')}
              />
            </Button>
          </div>
        </>
      )}
    </article>
  );
}
