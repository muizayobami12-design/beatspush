'use client';

import React from 'react';
import { Message } from '@/services/messagingService';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { AttachmentPreview } from './AttachmentPreview';
import { format } from 'date-fns';
import { MoreVertical, Trash2, Copy, Flag, Pencil, Check, CheckCheck } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MessageBubbleProps {
  message: Message;
  isOwn: boolean;
  /** Called when user wants to delete this message */
  onDelete?: (messageId: string) => void;
  /** Called when user wants to edit (own messages only) — passes full message back */
  onEdit?: (message: Message) => void;
  /** Called when user wants to report (other's messages only) */
  onReport?: (messageId: string) => void;
}

/**
 * MessageBubble — renders a single chat message.
 * - Own messages: right-aligned, primary colour, edit/delete actions, read receipts (task 24.2, 26.1, 26.2)
 * - Other messages: left-aligned, muted colour, report action
 * - Attachment previews (task 20.2)
 * - Edited / deleted indicators
 */
export default React.memo(function MessageBubble({
  message,
  isOwn,
  onDelete,
  onEdit,
  onReport,
}: MessageBubbleProps) {
  const isDeleted = !!message.deleted_at;
  const isEdited = message.is_edited && !isDeleted;

  // Read receipt state (task 24.2)
  const isRead = (message.read_by?.length ?? 0) > 1; // > 1 means someone other than sender read it
  const isDelivered = true; // message exists in DB, so delivered

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content).catch(() => {});
  };

  const handleDelete = () => {
    if (onDelete && window.confirm('Delete this message?')) {
      onDelete(message.id);
    }
  };

  // Check if the message is within 15 minutes for editing
  const canEdit = isOwn && !isDeleted && (() => {
    const created = new Date(message.created_at).getTime();
    return Date.now() - created < 15 * 60 * 1000;
  })();

  return (
    <div
      className={cn('flex gap-2 group', isOwn ? 'flex-row-reverse' : 'flex-row')}
      role="listitem"
    >
      {/* Avatar (other user only) */}
      {!isOwn && (
        <Avatar className="h-7 w-7 flex-shrink-0 self-end mb-5">
          <AvatarImage src={message.sender?.avatar_url} />
          <AvatarFallback className="text-xs">
            {(message.sender?.username ?? 'U').slice(0, 2).toUpperCase()}
          </AvatarFallback>
        </Avatar>
      )}

      {/* Bubble column */}
      <div className={cn('flex flex-col gap-0.5 max-w-[72%]', isOwn && 'items-end')}>
        {/* Sender name (other only) */}
        {!isOwn && (
          <span className="text-xs text-muted-foreground font-medium px-1">
            {message.sender?.full_name || message.sender?.username}
          </span>
        )}

        {/* Bubble */}
        <div
          className={cn(
            'rounded-2xl px-3.5 py-2 break-words text-sm whitespace-pre-wrap',
            isOwn
              ? 'bg-primary text-primary-foreground rounded-br-sm'
              : 'bg-muted text-foreground rounded-bl-sm',
            isDeleted && 'italic opacity-50 text-xs'
          )}
        >
          {message.content}

          {/* Attachment previews */}
          {!isDeleted && message.attachments && message.attachments.length > 0 && (
            <div className="mt-2 space-y-2">
              {message.attachments.map((att) => (
                <AttachmentPreview key={att.id} attachment={att} />
              ))}
            </div>
          )}
        </div>

        {/* Metadata row */}
        <div
          className={cn(
            'flex items-center gap-1.5 px-1 text-xs text-muted-foreground',
            isOwn && 'flex-row-reverse'
          )}
        >
          <span>{format(new Date(message.created_at), 'HH:mm')}</span>
          {isEdited && <span>(edited)</span>}

          {/* Read receipts — own messages only (task 24.2) */}
          {isOwn && !isDeleted && (
            isRead
              ? <CheckCheck className="h-3.5 w-3.5 text-primary" aria-label="Read" />
              : <Check className="h-3.5 w-3.5" aria-label="Delivered" />
          )}

          {/* Actions menu — visible on hover */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-5 w-5 opacity-0 group-hover:opacity-100 transition-opacity"
                aria-label="Message options"
              >
                <MoreVertical className="h-3 w-3" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align={isOwn ? 'end' : 'start'} className="min-w-[140px]">
              <DropdownMenuItem onClick={handleCopy}>
                <Copy className="mr-2 h-4 w-4" /> Copy
              </DropdownMenuItem>
              {canEdit && onEdit && (
                <DropdownMenuItem onClick={() => onEdit(message)}>
                  <Pencil className="mr-2 h-4 w-4" /> Edit
                </DropdownMenuItem>
              )}
              {isOwn && !isDeleted && onDelete && (
                <DropdownMenuItem onClick={handleDelete} className="text-destructive">
                  <Trash2 className="mr-2 h-4 w-4" /> Delete
                </DropdownMenuItem>
              )}
              {!isOwn && onReport && (
                <DropdownMenuItem onClick={() => onReport(message.id)} className="text-destructive">
                  <Flag className="mr-2 h-4 w-4" /> Report
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  );
});
