'use client';

import { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { NotificationCenter, Notification } from './NotificationCenter';
import { cn } from '@/lib/utils';

interface NotificationBellProps {
  unreadCount?: number;
  notifications?: Notification[];
  onMarkAsRead?: (notificationId: string) => void;
  onMarkAllAsRead?: () => void;
  onDelete?: (notificationId: string) => void;
}

export function NotificationBell({
  unreadCount = 0,
  notifications = [],
  onMarkAsRead,
  onMarkAllAsRead,
  onDelete,
}: NotificationBellProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [badge, setBadge] = useState(unreadCount);

  useEffect(() => {
    setBadge(unreadCount);
  }, [unreadCount]);

  return (
    <>
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={cn(
          'relative p-2 rounded-lg',
          'hover:bg-surface-container-low',
          'text-on-surface-variant hover:text-on-surface',
          'transition-colors'
        )}
        aria-label="Notifications"
      >
        <Bell className="h-6 w-6" />

        {/* Badge */}
        {badge > 0 && (
          <span
            className={cn(
              'absolute top-0 right-0 w-5 h-5 rounded-full',
              'bg-destructive text-on-destructive',
              'flex items-center justify-center',
              'font-label-xs text-label-xs font-bold'
            )}
          >
            {badge > 9 ? '9+' : badge}
          </span>
        )}
      </button>

      {/* Notification Center */}
      <NotificationCenter
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        notifications={notifications}
        onMarkAsRead={onMarkAsRead}
        onMarkAllAsRead={onMarkAllAsRead}
        onDelete={onDelete}
      />
    </>
  );
}
