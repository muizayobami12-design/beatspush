'use client';

import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import type { Conversation } from '@/services/messagingService';

interface ConversationListItemProps {
  conversation: Conversation;
  currentUserId?: string;
  isSelected?: boolean;
  onClick: (conversation: Conversation) => void;
}

/**
 * ConversationListItem — individual conversation row.
 * Uses snake_case fields from messagingService types.
 * Wrapped with React.memo to prevent unnecessary re-renders.
 */
export const ConversationListItem = React.memo(function ConversationListItem({
  conversation,
  currentUserId,
  isSelected = false,
  onClick,
}: ConversationListItemProps) {
  // Get the other participant (not the current user)
  const otherParticipant =
    conversation.participants?.find((p) => p.id !== currentUserId) ??
    conversation.participants?.[0];

  const displayName =
    otherParticipant?.full_name || otherParticipant?.username || 'Unknown User';
  const avatarUrl = otherParticipant?.avatar_url;
  const initials = displayName
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  const lastMessage = conversation.last_message;
  const unreadCount = conversation.unread_count ?? 0;
  const isMessageRequest = conversation.is_message_request;

  const timeAgo = lastMessage?.created_at
    ? formatDistanceToNow(new Date(lastMessage.created_at), { addSuffix: true })
    : '';

  const previewText = lastMessage?.content
    ? lastMessage.content.length > 60
      ? lastMessage.content.slice(0, 60) + '...'
      : lastMessage.content
    : 'No messages yet';

  return (
    <button
      onClick={() => onClick(conversation)}
      className={cn(
        'w-full flex items-center gap-3 px-4 py-3 text-left transition-colors',
        'hover:bg-muted/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        isSelected && 'bg-muted'
      )}
      aria-label={`Conversation with ${displayName}${unreadCount > 0 ? `, ${unreadCount} unread messages` : ''}`}
    >
      {/* Avatar */}
      <div className="relative flex-shrink-0">
        <Avatar className="h-10 w-10">
          <AvatarImage src={avatarUrl} alt={displayName} />
          <AvatarFallback className="text-xs font-medium">{initials}</AvatarFallback>
        </Avatar>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span className={cn('font-medium text-sm truncate', unreadCount > 0 && 'font-semibold')}>
            {displayName}
          </span>
          {timeAgo && (
            <span className="text-xs text-muted-foreground flex-shrink-0">{timeAgo}</span>
          )}
        </div>

        <div className="flex items-center justify-between gap-2 mt-0.5">
          <p
            className={cn(
              'text-xs truncate',
              unreadCount > 0 ? 'text-foreground font-medium' : 'text-muted-foreground'
            )}
          >
            {previewText}
          </p>

          <div className="flex items-center gap-1 flex-shrink-0">
            {isMessageRequest && (
              <Badge variant="outline" className="text-xs px-1.5 py-0 h-4">
                Request
              </Badge>
            )}
            {conversation.is_muted && (
              <Badge variant="secondary" className="text-xs px-1.5 py-0 h-4">
                Muted
              </Badge>
            )}
            {unreadCount > 0 && (
              <Badge className="text-xs px-1.5 py-0 h-4 min-w-[1rem] bg-primary text-primary-foreground">
                {unreadCount > 99 ? '99+' : unreadCount}
              </Badge>
            )}
          </div>
        </div>
      </div>
    </button>
  );
});

export default ConversationListItem;
