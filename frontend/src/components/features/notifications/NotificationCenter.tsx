'use client';

import { useState, useEffect, useCallback } from 'react';
import { X, Bell, MessageSquare, Heart, Zap, Gift, Users, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export type NotificationType = 'message' | 'follow' | 'purchase' | 'like' | 'tip' | 'system';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  timestamp: Date;
  actor?: {
    id: string;
    name: string;
    avatar?: string;
  };
  metadata?: Record<string, any>;
  action?: {
    label: string;
    href?: string;
  };
}

interface NotificationCenterProps {
  isOpen: boolean;
  onClose: () => void;
  notifications?: Notification[];
  onMarkAsRead?: (notificationId: string) => void;
  onMarkAllAsRead?: () => void;
  onDelete?: (notificationId: string) => void;
}

const NOTIFICATION_ICONS: Record<NotificationType, React.ReactNode> = {
  message: <MessageSquare className="h-5 w-5" />,
  follow: <Users className="h-5 w-5" />,
  purchase: <Gift className="h-5 w-5" />,
  like: <Heart className="h-5 w-5" />,
  tip: <Zap className="h-5 w-5" />,
  system: <Bell className="h-5 w-5" />,
};

const NOTIFICATION_COLORS: Record<NotificationType, string> = {
  message: 'bg-secondary/10 text-secondary border-secondary/30',
  follow: 'bg-tertiary/10 text-tertiary border-tertiary/30',
  purchase: 'bg-clay/10 text-clay border-clay/30',
  like: 'bg-destructive/10 text-destructive border-destructive/30',
  tip: 'bg-secondary-fixed/10 text-secondary-fixed border-secondary-fixed/30',
  system: 'bg-on-surface-variant/10 text-on-surface-variant border-on-surface-variant/30',
};

// Mock notifications data
const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: '1',
    type: 'message',
    title: 'New message from Oluwa Beats',
    message: 'Hey, interested in collaborating on a track?',
    read: false,
    timestamp: new Date(Date.now() - 5 * 60000),
    actor: {
      id: 'user1',
      name: 'Oluwa Beats',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=oluwa',
    },
    action: { label: 'View', href: '/messages' },
  },
  {
    id: '2',
    type: 'follow',
    title: 'Sound Engineer followed you',
    message: 'Sound Engineer just started following your profile',
    read: false,
    timestamp: new Date(Date.now() - 15 * 60000),
    actor: {
      id: 'user2',
      name: 'Sound Engineer',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=engineer',
    },
  },
  {
    id: '3',
    type: 'purchase',
    title: 'Your beat was purchased',
    message: 'Midnight Voyage has been purchased by a new customer',
    read: false,
    timestamp: new Date(Date.now() - 30 * 60000),
    metadata: { beatId: 'beat1', beatTitle: 'Midnight Voyage' },
    action: { label: 'View', href: '/earnings' },
  },
  {
    id: '4',
    type: 'like',
    title: 'Zaria liked your beat',
    message: 'Zaria liked Lagos Nights',
    read: true,
    timestamp: new Date(Date.now() - 60 * 60000),
    actor: {
      id: 'user3',
      name: 'Zaria',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=zaria',
    },
  },
  {
    id: '5',
    type: 'tip',
    title: 'You received a tip',
    message: 'Producer Alex sent you a tip of ₦5,000',
    read: true,
    timestamp: new Date(Date.now() - 120 * 60000),
    actor: {
      id: 'user4',
      name: 'Producer Alex',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=alex',
    },
  },
  {
    id: '6',
    type: 'system',
    title: 'System maintenance',
    message: 'We have scheduled maintenance on Sunday at 2 AM UTC',
    read: true,
    timestamp: new Date(Date.now() - 240 * 60000),
  },
];

export function NotificationCenter({
  isOpen,
  onClose,
  notifications = MOCK_NOTIFICATIONS,
  onMarkAsRead,
  onMarkAllAsRead,
  onDelete,
}: NotificationCenterProps) {
  const [localNotifications, setLocalNotifications] = useState<Notification[]>(notifications);
  const [filterType, setFilterType] = useState<NotificationType | 'all'>('all');

  // Update local notifications when prop changes
  useEffect(() => {
    setLocalNotifications(notifications);
  }, [notifications]);

  // Group notifications by type
  const groupedNotifications = useCallback(() => {
    return localNotifications.reduce(
      (acc, notif) => {
        if (!acc[notif.type]) {
          acc[notif.type] = [];
        }
        acc[notif.type].push(notif);
        return acc;
      },
      {} as Record<NotificationType, Notification[]>
    );
  }, [localNotifications]);

  // Filter notifications
  const filteredNotifications = useCallback(() => {
    if (filterType === 'all') {
      return localNotifications;
    }
    return localNotifications.filter((n) => n.type === filterType);
  }, [localNotifications, filterType]);

  // Count unread
  const unreadCount = localNotifications.filter((n) => !n.read).length;

  // Handle mark as read
  const handleMarkAsRead = (id: string) => {
    setLocalNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
    onMarkAsRead?.(id);
  };

  // Handle mark all as read
  const handleMarkAllAsRead = () => {
    setLocalNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    onMarkAllAsRead?.();
  };

  // Handle delete
  const handleDelete = (id: string) => {
    setLocalNotifications((prev) => prev.filter((n) => n.id !== id));
    onDelete?.(id);
  };

  // Format timestamp
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const displayNotifications = filteredNotifications();
  const grouped = groupedNotifications();

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          onClick={onClose}
          className={cn(
            'fixed inset-0 bg-black/50 z-40 transition-opacity',
            isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
          )}
        />
      )}

      {/* Drawer */}
      <div
        className={cn(
          'fixed right-0 top-0 bottom-0 w-full md:w-96 z-50',
          'bg-surface-container border-l border-outline-variant/30',
          'shadow-lg transition-transform duration-300',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        {/* Header */}
        <div
          className={cn(
            'flex items-center justify-between px-stack-md py-stack-md',
            'border-b border-outline-variant/30'
          )}
        >
          <div className="flex items-center gap-3">
            <div className={cn(
              'p-2 rounded-lg',
              'bg-surface-container-low'
            )}>
              <Bell className="h-5 w-5 text-secondary" />
            </div>
            <div>
              <h2 className={cn(
                'font-headline-sm text-headline-sm',
                'text-on-surface'
              )}>
                Notifications
              </h2>
              {unreadCount > 0 && (
                <p className={cn(
                  'font-body-sm text-body-sm',
                  'text-on-surface-variant'
                )}>
                  {unreadCount} unread
                </p>
              )}
            </div>
          </div>

          <button
            onClick={onClose}
            className={cn(
              'p-2 rounded-lg hover:bg-surface-container-low',
              'text-on-surface-variant hover:text-on-surface',
              'transition-colors'
            )}
            aria-label="Close notifications"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Toolbar */}
        <div
          className={cn(
            'flex items-center justify-between px-stack-md py-stack-sm',
            'border-b border-outline-variant/30 bg-surface-container-low/50'
          )}
        >
          <div className="flex gap-2 overflow-x-auto">
            <button
              onClick={() => setFilterType('all')}
              className={cn(
                'px-3 py-1 rounded-full font-label-sm text-label-sm',
                'whitespace-nowrap transition-all',
                filterType === 'all'
                  ? 'bg-secondary text-on-secondary'
                  : 'bg-surface-container text-on-surface-variant hover:text-on-surface'
              )}
            >
              All
            </button>
            {Object.keys(grouped).map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type as NotificationType)}
                className={cn(
                  'px-3 py-1 rounded-full font-label-sm text-label-sm',
                  'whitespace-nowrap transition-all',
                  filterType === type
                    ? 'bg-secondary text-on-secondary'
                    : 'bg-surface-container text-on-surface-variant hover:text-on-surface'
                )}
              >
                {type}
              </button>
            ))}
          </div>

          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllAsRead}
              className={cn(
                'px-2 py-1 text-right font-label-sm text-label-sm',
                'text-secondary hover:text-secondary-dim',
                'transition-colors'
              )}
            >
              Mark all
            </button>
          )}
        </div>

        {/* Notifications List */}
        <div className={cn(
          'h-[calc(100vh-180px)] overflow-y-auto',
          'divide-y divide-outline-variant/20'
        )}>
          {displayNotifications.length > 0 ? (
            displayNotifications.map((notification) => (
              <div
                key={notification.id}
                className={cn(
                  'p-stack-md transition-all',
                  !notification.read && 'bg-secondary/5'
                )}
              >
                <div className="flex gap-3">
                  {/* Avatar or Icon */}
                  <div
                    className={cn(
                      'flex-shrink-0 w-10 h-10 rounded-full',
                      'flex items-center justify-center',
                      'border',
                      NOTIFICATION_COLORS[notification.type]
                    )}
                  >
                    {notification.actor?.avatar ? (
                      <img
                        src={notification.actor.avatar}
                        alt={notification.actor.name}
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      NOTIFICATION_ICONS[notification.type]
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className={cn(
                          'font-body-md text-body-md',
                          !notification.read ? 'text-on-surface font-bold' : 'text-on-surface'
                        )}>
                          {notification.title}
                        </p>
                        <p className={cn(
                          'font-body-sm text-body-sm mt-1',
                          'text-on-surface-variant line-clamp-2'
                        )}>
                          {notification.message}
                        </p>

                        {/* Action button */}
                        {notification.action && (
                          <a
                            href={notification.action.href}
                            className={cn(
                              'inline-block mt-2 px-2 py-1 rounded',
                              'font-label-sm text-label-sm',
                              'bg-secondary/20 text-secondary hover:bg-secondary/30',
                              'transition-colors'
                            )}
                          >
                            {notification.action.label}
                          </a>
                        )}
                      </div>

                      {/* Unread indicator */}
                      {!notification.read && (
                        <div className="flex-shrink-0 w-2 h-2 rounded-full bg-secondary mt-1" />
                      )}
                    </div>

                    {/* Meta */}
                    <div className="flex items-center justify-between mt-2 gap-2">
                      <span className={cn(
                        'font-body-xs text-body-xs',
                        'text-on-surface-variant'
                      )}>
                        {formatTime(notification.timestamp)}
                      </span>

                      <div className="flex gap-1">
                        {!notification.read && (
                          <button
                            onClick={() => handleMarkAsRead(notification.id)}
                            className={cn(
                              'px-2 py-1 rounded text-xs font-label-xs',
                              'text-secondary hover:bg-secondary/10',
                              'transition-colors'
                            )}
                          >
                            Mark read
                          </button>
                        )}

                        <button
                          onClick={() => handleDelete(notification.id)}
                          className={cn(
                            'px-2 py-1 rounded text-xs font-label-xs',
                            'text-destructive hover:bg-destructive/10',
                            'transition-colors'
                          )}
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className={cn(
              'flex flex-col items-center justify-center h-64',
              'text-on-surface-variant'
            )}>
              <Bell className="h-12 w-12 mb-4 opacity-50" />
              <p className={cn(
                'font-body-md text-body-md',
                'text-center'
              )}>
                No notifications
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        {displayNotifications.length > 0 && (
          <div
            className={cn(
              'px-stack-md py-stack-sm',
              'border-t border-outline-variant/30',
              'bg-surface-container-low/50'
            )}
          >
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={onClose}
            >
              Close
            </Button>
          </div>
        )}
      </div>
    </>
  );
}
