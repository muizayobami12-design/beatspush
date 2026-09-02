'use client';

import { useState } from 'react';
import Image from 'next/image';
import { formatDistanceToNow } from 'date-fns';
import { Loader2, Send, Heart, MessageCircle, Trash2 } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { usePost, useCreateComment, useDeleteComment, useToggleLike } from '@/hooks/useSocial';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';
import type { Comment } from '@/types';

interface PostDetailModalProps {
  postId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function PostDetailModal({ postId, isOpen, onClose }: PostDetailModalProps) {
  const { user: currentUser } = useAuthStore();
  const { data: post, isLoading, error } = usePost(isOpen ? postId : null);
  const createComment = useCreateComment();
  const deleteComment = useDeleteComment();
  const toggleLike = useToggleLike();

  const [commentText, setCommentText] = useState('');
  const [replyingTo, setReplyingTo] = useState<string | null>(null);

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!commentText.trim()) return;

    try {
      await createComment.mutateAsync({
        postId,
        data: {
          content: commentText.trim(),
          parentCommentId: replyingTo || undefined,
        },
      });

      setCommentText('');
      setReplyingTo(null);
    } catch (error) {
      console.error('Failed to create comment:', error);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!confirm('Are you sure you want to delete this comment?')) return;

    try {
      await deleteComment.mutateAsync(commentId);
    } catch (error) {
      console.error('Failed to delete comment:', error);
    }
  };

  const handleLike = () => {
    toggleLike.mutate(postId);
  };

  const renderComment = (comment: Comment, isReply = false) => {
    const isOwnComment = currentUser?.id === comment.user.id;

    return (
      <div
        key={comment.id}
        className={cn('flex space-x-3', isReply && 'ml-12')}
      >
        {/* Avatar */}
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden">
            {comment.user.avatar ? (
              <Image
                src={comment.user.avatar}
                alt={comment.user.fullName}
                width={32}
                height={32}
                className="object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-white text-xs font-semibold">
                {comment?.user?.fullName?.charAt(0)?.toUpperCase() || comment?.user?.email?.charAt(0)?.toUpperCase() || 'U'}
              </div>
            )}
          </div>
        </div>

        {/* Comment Content */}
        <div className="flex-1 min-w-0">
          <div className="bg-muted rounded-lg p-3">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-sm">
                  {comment.user.fullName}
                </span>
                {comment.isEdited && (
                  <span className="text-xs text-muted-foreground">(edited)</span>
                )}
              </div>
              {isOwnComment && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => handleDeleteComment(comment.id)}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              )}
            </div>
            <p className="text-sm whitespace-pre-wrap break-words">
              {comment.content}
            </p>
          </div>

          <div className="flex items-center space-x-4 mt-1 text-xs text-muted-foreground">
            <span>
              {formatDistanceToNow(new Date(comment.createdAt), {
                addSuffix: true,
              })}
            </span>
            {!isReply && (
              <button
                onClick={() => setReplyingTo(comment.id)}
                className="hover:text-foreground transition-colors"
              >
                Reply
              </button>
            )}
          </div>

          {/* Replies */}
          {comment.replies && comment.replies.length > 0 && (
            <div className="mt-3 space-y-3">
              {comment.replies.map((reply) => renderComment(reply, true))}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="lg"
      showClose={true}
      closeOnBackdrop={true}
    >
      <div className="max-h-[80vh] overflow-y-auto">
        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center py-12">
            <p className="text-destructive">Failed to load post</p>
          </div>
        )}

        {/* Post Content */}
        {post && (
          <div className="space-y-4">
            {/* Post Header */}
            <div className="flex items-start space-x-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden flex-shrink-0">
                {post.user.avatar ? (
                  <Image
                    src={post.user.avatar}
                    alt={post.user.fullName}
                    width={48}
                    height={48}
                    className="object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-white font-semibold">
                    {post?.user?.fullName?.charAt(0)?.toUpperCase() || post?.user?.email?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold">{post.user.fullName}</span>
                  {post.user.isVerified && (
                    <svg
                      className="w-4 h-4 text-primary"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                    </svg>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  @{post.user.username || post.user.id.slice(0, 8)} •{' '}
                  {formatDistanceToNow(new Date(post.createdAt), {
                    addSuffix: true,
                  })}
                </p>
              </div>
            </div>

            {/* Post Content */}
            <div className="text-foreground whitespace-pre-wrap break-words">
              {post.content}
            </div>

            {/* Post Media */}
            {post.mediaUrl && (
              <div className="relative w-full rounded-lg overflow-hidden">
                <Image
                  src={post.mediaUrl}
                  alt="Post media"
                  width={600}
                  height={400}
                  className="object-cover w-full"
                />
              </div>
            )}

            {/* Like & Comment Stats */}
            <div className="flex items-center justify-between py-2 border-y">
              <div className="flex items-center space-x-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLike}
                  className={cn(
                    'flex items-center space-x-2',
                    post.isLiked && 'text-red-500'
                  )}
                >
                  <Heart
                    className={cn('w-5 h-5', post.isLiked && 'fill-current')}
                  />
                  <span>{post.likeCount}</span>
                </Button>

                <div className="flex items-center space-x-2 text-muted-foreground">
                  <MessageCircle className="w-5 h-5" />
                  <span>{post.commentCount}</span>
                </div>
              </div>
            </div>

            {/* Comments Section */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">
                Comments ({post.commentCount})
              </h3>

              {/* Comment Form */}
              {currentUser && (
                <form onSubmit={handleSubmitComment} className="space-y-2">
                  {replyingTo && (
                    <div className="flex items-center justify-between text-sm text-muted-foreground bg-muted px-3 py-2 rounded">
                      <span>Replying to comment</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setReplyingTo(null)}
                      >
                        Cancel
                      </Button>
                    </div>
                  )}

                  <div className="flex items-start space-x-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden flex-shrink-0">
                      {currentUser.avatar ? (
                        <Image
                          src={currentUser.avatar}
                          alt={currentUser.fullName}
                          width={32}
                          height={32}
                          className="object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-white text-xs font-semibold">
                          {currentUser?.fullName?.charAt(0)?.toUpperCase() || currentUser?.email?.charAt(0)?.toUpperCase() || 'U'}
                        </div>
                      )}
                    </div>

                    <Input
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      placeholder="Write a comment..."
                      className="flex-1"
                      disabled={createComment.isPending}
                    />

                    <Button
                      type="submit"
                      size="icon"
                      disabled={
                        !commentText.trim() || createComment.isPending
                      }
                    >
                      {createComment.isPending ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </form>
              )}

              {/* Comments List */}
              {post.comments && post.comments.length > 0 ? (
                <div className="space-y-4">
                  {post.comments.map((comment) => renderComment(comment))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No comments yet</p>
                  <p className="text-sm mt-1">Be the first to comment!</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}
