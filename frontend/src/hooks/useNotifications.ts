import { useState, useCallback, useEffect } from 'react';
import type { Notification } from '@/components/features/notifications/NotificationCenter';

interface UseNotificationsOptions {
  realtime?: boolean;
  onNewNotification?: (notification: Notification) => void;
}

export function useNotifications(options: UseNotificationsOptions = {}) {
  const { realtime = false, onNewNotification } = options;

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Calculate unread count
  useEffect(() => {
    const count = notifications.filter((n) => !n.read).length;
    setUnreadCount(count);
  }, [notifications]);

  // Mark as read
  const markAsRead = useCallback((notificationId: string) => {
    setNotifications((prev) =>
      prev.map((n) =>
        n.id === notificationId ? { ...n, read: true } : n
      )
    );
  }, []);

  // Mark all as read
  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  // Delete notification
  const deleteNotification = useCallback((notificationId: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== notificationId));
  }, []);

  // Add notification (for real-time)
  const addNotification = useCallback(
    (notification: Notification) => {
      setNotifications((prev) => [notification, ...prev]);
      onNewNotification?.(notification);
    },
    [onNewNotification]
  );

  // Fetch notifications (mock implementation)
  const fetchNotifications = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Mock fetch - replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Mock notifications would be set here
      // const response = await fetch('/api/notifications');
      // const data = await response.json();
      // setNotifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch notifications');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Setup real-time listeners
  useEffect(() => {
    if (!realtime) return;

    // Mock WebSocket connection
    // In production, connect to actual WebSocket server
    // const socket = io('/notifications');
    // socket.on('notification', (notification: Notification) => {
    //   addNotification(notification);
    // });
    // return () => socket.disconnect();
  }, [realtime, addNotification]);

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    addNotification,
    fetchNotifications,
  };
}
