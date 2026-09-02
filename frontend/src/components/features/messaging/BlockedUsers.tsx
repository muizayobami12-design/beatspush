'use client';

import React, { useState, useEffect } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

interface BlockedUser {
  id: string;
  blocker_id: string;
  blocked_id: string;
  blocked_user: {
    id: string;
    username: string;
    full_name: string;
    avatar_url?: string;
  };
  blocked_at: string;
  reason?: string;
}

interface BlockedUsersProps {
  className?: string;
}

/**
 * BlockedUsers — displays list of blocked users with unblock buttons.
 * Fetch from GET /api/v1/messaging/blocked-users
 * Delete via DELETE /api/v1/messaging/block/{user_id}
 * Requirements: 6.1, 6.2, 6.4, 6.5
 */
export function BlockedUsers({ className }: BlockedUsersProps) {
  const { toast } = useToast();
  const [blockedUsers, setBlockedUsers] = useState<BlockedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [unblockingId, setUnblockingId] = useState<string | null>(null);
  const [unblockConfirm, setUnblockConfirm] = useState<string | null>(null);

  useEffect(() => {
    loadBlockedUsers();
  }, []);

  const loadBlockedUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/messaging/blocked-users', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load blocked users');
      }

      const data = await response.json();
      setBlockedUsers(data.blocked_users || []);
    } catch (error) {
      console.error('Error loading blocked users:', error);
      toast({
        title: 'Error',
        description: 'Failed to load blocked users',
        variant: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUnblock = async (userId: string) => {
    setUnblockingId(userId);
    try {
      const response = await fetch(
        `/api/v1/messaging/block/${userId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to unblock user');
      }

      setBlockedUsers((prev) =>
        prev.filter((blocked) => blocked.blocked_id !== userId)
      );
      setUnblockConfirm(null);
      toast({
        title: 'User unblocked',
        description: 'You can now message this user again',
        variant: 'success',
      });
    } catch (error) {
      console.error('Error unblocking user:', error);
      toast({
        title: 'Error',
        description: 'Failed to unblock user',
        variant: 'error',
      });
    } finally {
      setUnblockingId(null);
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
            d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.172l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
      </div>
      <p className="text-sm font-medium">No blocked users</p>
      <p className="text-xs text-muted-foreground mt-1">
        You haven&apos;t blocked anyone yet
      </p>
    </div>
  );

  const renderBlockedUser = (blocked: BlockedUser) => {
    const user = blocked.blocked_user;
    const displayName = user.full_name || user.username || 'Unknown User';
    const initials = displayName
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);

    const blockedTime = formatDistanceToNow(new Date(blocked.blocked_at), {
      addSuffix: true,
    });

    const isUnblocking = unblockingId === user.id;

    return (
      <div
        key={blocked.id}
        className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors"
      >
        {/* User Info */}
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <Avatar className="h-10 w-10 flex-shrink-0">
            <AvatarImage src={user.avatar_url} alt={displayName} />
            <AvatarFallback className="text-xs font-medium">
              {initials}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate">{displayName}</p>
            <p className="text-xs text-muted-foreground">
              Blocked {blockedTime}
            </p>
            {blocked.reason && (
              <p className="text-xs text-muted-foreground mt-1">
                Reason: {blocked.reason}
              </p>
            )}
          </div>
        </div>

        {/* Unblock Button */}
        <Button
          size="sm"
          variant="outline"
          onClick={() => setUnblockConfirm(user.id)}
          disabled={isUnblocking}
          className="flex-shrink-0 ml-2"
        >
          {isUnblocking ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            'Unblock'
          )}
        </Button>

        {/* Confirmation Dialog */}
        <Dialog
          open={unblockConfirm === user.id}
          onOpenChange={(open) => {
            if (!open) setUnblockConfirm(null);
          }}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Unblock {displayName}?</DialogTitle>
              <DialogDescription>
                After unblocking, {displayName} will be able to message you and
                you&apos;ll see their messages in your inbox.
              </DialogDescription>
            </DialogHeader>
            <div className="flex gap-3 justify-end">
              <Button
                variant="outline"
                onClick={() => setUnblockConfirm(null)}
              >
                Cancel
              </Button>
              <Button
                onClick={() => handleUnblock(user.id)}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                Unblock
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    );
  };

  return (
    <div className={cn('space-y-4', className)}>
      <div>
        <h3 className="text-lg font-semibold">Blocked Users</h3>
        <p className="text-sm text-muted-foreground mt-1">
          Manage users you&apos;ve blocked. They won&apos;t be able to message you.
        </p>
      </div>

      <div className="space-y-2 max-h-[500px] overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        ) : blockedUsers.length === 0 ? (
          renderEmpty()
        ) : (
          blockedUsers.map((blocked) => renderBlockedUser(blocked))
        )}
      </div>
    </div>
  );
}

export default BlockedUsers;
