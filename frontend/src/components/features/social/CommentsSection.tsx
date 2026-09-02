'use client';

import { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { MessageSquare, Send, Heart, MoreVertical, Reply, Edit, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import socialService, { Comment } from '@/services/socialService';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

interface CommentsSectionProps {
  contentType: 'beat' | 'track' | 'mix';
  contentId: string;
  className?: string;
}

export default function CommentsSection({ contentType, contentId, className }: CommentsSectionProps) {
  const { user } = useAuthStore();
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [posting, setPosting] = useState(false);

  useEffect(() => {
    loadComments();
  }, [contentType, contentId]);

  const loadComments = async () => {
    try {
      setLoading(true);
      const result = await socialService.getComments({
        content_type: contentType,
        content_id: contentId,
        page: 1,
        page_size: 50,
      });
      setComments(result.comments);
    } catch (error) {
      console.error('Failed to load comments:', error);
      setComments([]);
    } finally {
      setLoading(false);
    }
  };

  const handlePostComment = async (parentId?: string) => {
    const content = parentId ? editContent : newComment;
    if (!content.trim() || posting) return;

    try {
      setPosting(true);
      const comment = await socialService.postComment({
        content_type: contentType,
        content_id: contentId,
        content: content.trim(),
        parent_id: parentId,
      });

      if (parentId) {
        // Add reply to parent comment
        setComments(prev =>
          prev.map(c =>
            c.id === parentId
              ? { ...c, replies: [...(c.replies || []), comment] }
              : c
          )
        );
        setReplyingTo(null);
        setEditContent('');
      } else {
        // Add new comment
        setComments(prev => [comment, ...prev]);
        setNewComment('');
      }
    } catch (error) {
      console.error('Failed to post comment:', error);
      alert('Failed to post comment');
    } finally {
      setPosting(false);
    }
  };

  const handleUpdateComment = async (commentId: string) => {
    if (!editContent.trim()) return;

    try {
      const updated = await socialService.updateComment(commentId, editContent.trim());
      setComments(prev =>
        prev.map(c => (c.id === commentId ? { ...c, content: updated.content } : c))
      );
      setEditingId(null);
      setEditContent('');
    } catch (error) {
      console.error('Failed to update comment:', error);
      alert('Failed to update comment');
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!window.confirm('Delete this comment?')) return;

    try {
      await socialService.deleteComment(commentId);
      setComments(prev => prev.filter(c => c.id !== commentId));
    } catch (error) {
      console.error('Failed to delete comment:', error);
      alert('Failed to delete comment');
    }
  };

  const handleLikeComment = async (commentId: string) => {
    try {
      await socialService.like({
        content_type: 'comment',
        content_id: commentId,
      });
      setComments(prev =>
        prev.map(c =>
          c.id === commentId
            ? { ...c, likes_count: c.likes_count + 1, is_liked: true }
            : c
        )
      );
    } catch (error) {
      console.error('Failed to like comment:', error);
    }
  };

  const handleUnlikeComment = async (commentId: string) => {
    try {
      await socialService.unlike({
        content_type: 'comment',
        content_id: commentId,
      });
      setComments(prev =>
        prev.map(c =>
          c.id === commentId
            ? { ...c, likes_count: Math.max(0, c.likes_count - 1), is_liked: false }
            : c
        )
      );
    } catch (error) {
      console.error('Failed to unlike comment:', error);
    }
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center gap-2">
        <MessageSquare className="h-5 w-5" />
        <h3 className="text-lg font-semibold">
          Comments {comments.length > 0 && `(${comments.length})`}
        </h3>
      </div>

      {/* New Comment Input */}
      {user && (
        <div className="flex gap-3">
          <Avatar className="h-10 w-10 flex-shrink-0">
            <AvatarImage src={user.avatar_url} />
            <AvatarFallback>
              {user.fullName?.charAt(0) || user.email?.charAt(0) || 'U'}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 space-y-2">
            <Textarea
              placeholder="Add a comment..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              className="min-h-[80px] resize-none"
              maxLength={1000}
            />
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">
                {newComment.length}/1000
              </span>
              <Button
                size="sm"
                onClick={() => handlePostComment()}
                disabled={!newComment.trim() || posting}
              >
                <Send className="h-4 w-4 mr-2" />
                Comment
              </Button>
            </div>
          </div>
        </div>
      )}

      {!user && (
        <div className="p-4 border rounded-lg bg-muted/30 text-center">
          <p className="text-sm text-muted-foreground">
            Sign in to comment
          </p>
        </div>
      )}

      {/* Comments List */}
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : comments.length === 0 ? (
        <div className="text-center py-8">
          <MessageSquare className="h-12 w-12 text-muted-foreground opacity-50 mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">No comments yet</p>
          <p className="text-xs text-muted-foreground">Be the first to comment!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {comments.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              currentUserId={user?.id}
              onReply={() => {
                setReplyingTo(comment.id);
                setEditContent('');
              }}
              onEdit={() => {
                setEditingId(comment.id);
                setEditContent(comment.content);
              }}
              onDelete={() => handleDeleteComment(comment.id)}
              onLike={() =>
                comment.is_liked
                  ? handleUnlikeComment(comment.id)
                  : handleLikeComment(comment.id)
              }
              isEditing={editingId === comment.id}
              editContent={editContent}
              setEditContent={setEditContent}
              onSaveEdit={() => handleUpdateComment(comment.id)}
              onCancelEdit={() => {
                setEditingId(null);
                setEditContent('');
              }}
              isReplying={replyingTo === comment.id}
              replyContent={replyingTo === comment.id ? editContent : ''}
              setReplyContent={setEditContent}
              onSendReply={() => handlePostComment(comment.id)}
              onCancelReply={() => {
                setReplyingTo(null);
                setEditContent('');
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Comment Item Component
interface CommentItemProps {
  comment: Comment;
  currentUserId?: string;
  onReply: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onLike: () => void;
  isEditing: boolean;
  editContent: string;
  setEditContent: (content: string) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  isReplying: boolean;
  replyContent: string;
  setReplyContent: (content: string) => void;
  onSendReply: () => void;
  onCancelReply: () => void;
}

function CommentItem({
  comment,
  currentUserId,
  onReply,
  onEdit,
  onDelete,
  onLike,
  isEditing,
  editContent,
  setEditContent,
  onSaveEdit,
  onCancelEdit,
  isReplying,
  replyContent,
  setReplyContent,
  onSendReply,
  onCancelReply,
}: CommentItemProps) {
  const isOwner = currentUserId === comment.user_id;

  return (
    <div className="flex gap-3">
      <Avatar className="h-10 w-10 flex-shrink-0">
        <AvatarImage src={comment.user.avatar_url} />
        <AvatarFallback>
          {comment.user.username?.charAt(0).toUpperCase() || 'U'}
        </AvatarFallback>
      </Avatar>

      <div className="flex-1 min-w-0 space-y-2">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-semibold text-sm">{comment.user.full_name}</span>
              <span className="text-xs text-muted-foreground">
                @{comment.user.username}
              </span>
              <span className="text-xs text-muted-foreground">•</span>
              <span className="text-xs text-muted-foreground">
                {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
              </span>
            </div>
          </div>

          {/* Actions Menu */}
          {isOwner && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 flex-shrink-0">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={onEdit}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onDelete} className="text-destructive">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>

        {/* Content */}
        {isEditing ? (
          <div className="space-y-2">
            <Textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="min-h-[60px]"
              maxLength={1000}
            />
            <div className="flex gap-2">
              <Button size="sm" onClick={onSaveEdit}>
                Save
              </Button>
              <Button size="sm" variant="outline" onClick={onCancelEdit}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <p className="text-sm whitespace-pre-wrap break-words">{comment.content}</p>
        )}

        {/* Actions */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onLike}
            className={cn(
              'h-8 gap-1 text-xs',
              comment.is_liked && 'text-red-500 hover:text-red-600'
            )}
          >
            <Heart className={cn('h-4 w-4', comment.is_liked && 'fill-current')} />
            {comment.likes_count > 0 && comment.likes_count}
          </Button>

          <Button variant="ghost" size="sm" onClick={onReply} className="h-8 gap-1 text-xs">
            <Reply className="h-4 w-4" />
            Reply
          </Button>
        </div>

        {/* Reply Input */}
        {isReplying && (
          <div className="pt-2 space-y-2">
            <Textarea
              placeholder="Write a reply..."
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              className="min-h-[60px]"
              maxLength={1000}
            />
            <div className="flex gap-2">
              <Button size="sm" onClick={onSendReply}>
                <Send className="h-4 w-4 mr-2" />
                Reply
              </Button>
              <Button size="sm" variant="outline" onClick={onCancelReply}>
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Replies */}
        {comment.replies && comment.replies.length > 0 && (
          <div className="mt-4 space-y-4 pl-4 border-l-2">
            {comment.replies.map((reply) => (
              <div key={reply.id} className="flex gap-3">
                <Avatar className="h-8 w-8 flex-shrink-0">
                  <AvatarImage src={reply.user.avatar_url} />
                  <AvatarFallback>
                    {reply.user.username?.charAt(0).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-sm">{reply.user.full_name}</span>
                    <span className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(reply.created_at), { addSuffix: true })}
                    </span>
                  </div>
                  <p className="text-sm mt-1 whitespace-pre-wrap break-words">{reply.content}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
