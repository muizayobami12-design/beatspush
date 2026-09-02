'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Loader2, X } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import type { Conversation } from '@/services/messagingService';

interface MessageRequestsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAccepted?: () => void;
}

/**
 * MessageRequestsModal — displays pending message requests.
 * Shows sender avatar, name, first message preview.
 * Allows accepting or declining requests.
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
 */
export function MessageRequestsModal({
  isOpen,
  onClose,
  onAccepted,
}: MessageRequestsModalProps) {
  const { toast } = useToast();
  const [requests, setRequests] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadRequests();
    }
  }, [isOpen]);

  const loadRequests = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/message-requests', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load message requests');
      }

      const data = await response.json();
      setRequests(data.conversations || []);
    } catch (error) {
      console.error('Error loading message requests:', error);
      toast({
        title: 'Error',
        description: 'Failed to load message requests',
        variant: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (conversationId: string) => {
    setProcessingId(conversationId);
    try {
      const response = await fetch(
        `/api/v1/message-requests/${conversationId}/accept`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to accept message request');
      }

      setRequests((prev) =>
        prev.filter((req) => req.id !== conversationId)
      );
      toast({
        title: 'Request accepted',
        description: 'You can now message this user',
        variant: 'success',
      });
      onAccepted?.();
    } catch (error) {
      console.error('Error accepting request:', error);
      toast({
        title: 'Error',
        description: 'Failed to accept message request',
        variant: 'error',
      });
    } finally {
      setProcessingId(null);
    }
  };

  const handleDecline = async (conversationId: string) => {
    setProcessingId(conversationId);
    try {
      const response = await fetch(
        `/api/v1/message-requests/${conversationId}/decline`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to decline message request');
      }

      setRequests((prev) =>
        prev.filter((req) => req.id !== conversationId)
      );
      toast({
        title: 'Request declined',
        variant: 'success',
      });
    } catch (error) {
      console.error('Error declining request:', error);
      toast({
        title: 'Error',
        description: 'Failed to decline message request',
        variant: 'error',
      });
    } finally {
      setProcessingId(null);
    }
  };

  const renderEmpty = () => (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <div className="text-muted-foreground mb-3">
        <svg
          className="w-12 h-12 mx-auto mb-2 opacity-50"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
      </div>
      <p className="text-sm font-medium">No pending requests</p>
      <p className="text-xs text-muted-foreground mt-1">
        You&apos;re all caught up!
      </p>
    </div>
  );

  const renderRequest = (request: Conversation) => {
    const sender =
      request.participants?.find(
        (p) => p.id !== localStorage.getItem('currentUserId')
      ) ?? request.participants?.[0];

    if (!sender) return null;

    const displayName = sender.full_name || sender.username || 'Unknown';
    const initials = displayName
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);

    const messagePreview = request.last_message?.content
      ? request.last_message.content.slice(0, 100) +
        (request.last_message.content.length > 100 ? '...' : '')
      : 'No message preview';

    const timeAgo = request.last_message?.created_at
      ? formatDistanceToNow(new Date(request.last_message.created_at), {
          addSuffix: true,
        })
      : 'Just now';

    const isProcessing = processingId === request.id;

    return (
      <div
        key={request.id}
        className="flex items-start gap-3 p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors"
      >
        {/* Avatar */}
        <Avatar className="h-10 w-10 flex-shrink-0 mt-1">
          <AvatarImage src={sender.avatar_url} alt={displayName} />
          <AvatarFallback className="text-xs font-medium">
            {initials}
          </AvatarFallback>
        </Avatar>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-semibold truncate">{displayName}</p>
            <span className="text-xs text-muted-foreground flex-shrink-0">
              {timeAgo}
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
            {messagePreview}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2 flex-shrink-0">
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleDecline(request.id)}
            disabled={isProcessing}
            className="h-8"
          >
            {isProcessing ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              'Decline'
            )}
          </Button>
          <Button
            size="sm"
            onClick={() => handleAccept(request.id)}
            disabled={isProcessing}
            className="h-8"
          >
            {isProcessing ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              'Accept'
            )}
          </Button>
        </div>
      </div>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Message Requests</DialogTitle>
        </DialogHeader>

        <div className="space-y-3 max-h-[400px] overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : requests.length === 0 ? (
            renderEmpty()
          ) : (
            requests.map((request) => renderRequest(request))
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default MessageRequestsModal;
