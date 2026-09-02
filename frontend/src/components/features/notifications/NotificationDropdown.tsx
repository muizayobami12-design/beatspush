'use client';

import { useRouter } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';
import { 
  MessageSquare, 
  UserPlus, 
  ShoppingCart, 
  DollarSign, 
  CheckCircle,
  XCircle,
  Bell,
  Settings
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useNotificationStore } from '@/store/notificationStore';
import notificationService, { NotificationType } from '@/services/notificationService';
import { cn } from '@/lib/utils';

interface NotificationDropdownProps {
  onClose: () => void;
}

const getNotificationIcon = (type: NotificationType) => {
  switch (type) {
    case 'new_message':
      return <MessageSquare className="h-5 w-5 text-blue-500" />;
    case 'new_follower':
      return <UserPlus className="h-5 w-5 text-green-500" />;
    case 'beat_purchase':
      return <ShoppingCart className="h-5 w-5 text-purple-500" />;
    case 'tip_received':
      return <DollarSign className="h-5 w-5 text-yellow-500" />;
    case 'dj_submission_accepted':
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    case 'dj_submission_declined':
      return <XCircle className="h-5 w-5 text-red-500" />;
    default:
      return <Bell className="h-5 w-5 text-muted-foreground" />;
  }
};

const getNotificationLink = (notification: any): string => {
  switch (notification.type) {
    case 'new_message':
      return notification.data?.conversation_id 
        ? `/messages?conversation=${notification.data.conversation_id}`
        : '/messages';
    case 'new_follower':
      return notification.data?.user_id 
        ? `/profile/${notification.data.user_id}`
        : '/profile';
    case 'beat_purchase':
      return notification.data?.beat_id 
        ? `/beats/${notification.data.beat_id}`
        : '/analytics';
    case 'tip_received':
      return '/analytics';
    case 'dj_submission_accepted':
    case 'dj_submission_declined':
      return '/dj/submissions';
    default:
      return '/notifications';
  }
};

export default function NotificationDropdown({ onClose }: NotificationDropdownProps) {
  const router = useRouter();
  const { notifications, markAsRead, markAllAsRead } = useNotificationStore();

  const handleNotificationClick = async (notification: any) => {
    // Mark as read
    if (!notification.read) {
      try {
        await notificationService.markAsRead(notification.id);
        markAsRead(notification.id);
      } catch (error) {
        console.error('Failed to mark as read:', error);
      }
    }

    // Navigate to relevant page
    const link = getNotificationLink(notification);
    router.push(link);
    onClose();
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllAsRead();
      markAllAsRead();
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const handleViewAll = () => {
    router.push('/notifications');
    onClose();
  };

  return (
    <div className="flex flex-col max-h-[500px]">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="font-semibold">Notifications</h3>
        <div className="flex items-center gap-2">
          {notifications.some(n => !n.read) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleMarkAllRead}
              className="text-xs"
            >
              Mark all read
            </Button>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push('/notifications/settings')}
            className="h-8 w-8"
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Notifications List */}
      <ScrollArea className="flex-1">
        {notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <Bell className="h-12 w-12 text-muted-foreground opacity-50 mb-3" />
            <p className="text-sm text-muted-foreground">No notifications yet</p>
            <p className="text-xs text-muted-foreground mt-1">
              We'll notify you when something happens
            </p>
          </div>
        ) : (
          <div className="divide-y">
            {notifications.slice(0, 5).map((notification) => (
              <button
                key={notification.id}
                onClick={() => handleNotificationClick(notification)}
                className={cn(
                  "w-full p-4 flex gap-3 hover:bg-accent transition-colors text-left",
                  !notification.read && "bg-primary/5"
                )}
              >
                {/* Icon */}
                <div className="flex-shrink-0 mt-1">
                  {getNotificationIcon(notification.type)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className={cn(
                    "text-sm mb-1",
                    !notification.read && "font-semibold"
                  )}>
                    {notification.title}
                  </p>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {notification.message}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatDistanceToNow(new Date(notification.created_at), {
                      addSuffix: true
                    })}
                  </p>
                </div>

                {/* Unread Indicator */}
                {!notification.read && (
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>
                  </div>
                )}
              </button>
            ))}
          </div>
        )}
      </ScrollArea>

      {/* Footer */}
      {notifications.length > 0 && (
        <div className="p-3 border-t">
          <Button
            variant="ghost"
            className="w-full"
            onClick={handleViewAll}
          >
            View all notifications
          </Button>
        </div>
      )}
    </div>
  );
}
