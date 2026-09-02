'use client';

import { useState, useMemo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Bell,
  Heart,
  MessageSquare,
  Clock,
  User,
  Share2,
  Music,
  Trash2,
  CheckCircle2,
} from 'lucide-react';
import { motion } from 'framer-motion';

interface Notification {
  id: string;
  type: 'tip' | 'message' | 'booking' | 'comment' | 'like' | 'follow' | 'share' | 'purchase';
  title: string;
  description: string;
  actor: {
    id: string;
    name: string;
  };
  read: boolean;
  timestamp: string;
}

interface NotificationGroup {
  date: string;
  notifications: Notification[];
}

const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: '1',
    type: 'tip',
    title: 'DJ Thunder sent a tip',
    description: '₦10,000 - "Fire beat! 🔥"',
    actor: { id: 'user-1', name: 'DJ Thunder' },
    read: false,
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
  },
  {
    id: '2',
    type: 'message',
    title: 'Producer Alex sent a message',
    description: '"Interested in your beat..."',
    actor: { id: 'user-2', name: 'Producer Alex' },
    read: false,
    timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
  },
  {
    id: '3',
    type: 'booking',
    title: 'Booking confirmed',
    description: 'Your session with Sarah Music is confirmed',
    actor: { id: 'user-3', name: 'Sarah Music' },
    read: false,
    timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
  },
];

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'tip':
      return <Heart className="w-5 h-5 text-red-500" />;
    case 'message':
      return <MessageSquare className="w-5 h-5 text-blue-500" />;
    case 'booking':
      return <Clock className="w-5 h-5 text-purple-500" />;
    case 'like':
      return <Heart className="w-5 h-5 text-pink-500" />;
    case 'follow':
      return <User className="w-5 h-5 text-blue-500" />;
    case 'share':
      return <Share2 className="w-5 h-5 text-orange-500" />;
    case 'purchase':
      return <Music className="w-5 h-5 text-green-500" />;
    default:
      return <Bell className="w-5 h-5 text-gray-500" />;
  }
};

const formatTime = (timestamp: string) => {
  const notifTime = new Date(timestamp);
  const diffMs = new Date().getTime() - notifTime.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return notifTime.toLocaleDateString();
};

const formatDate = (date: string) => {
  const notifDate = new Date(date);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (notifDate.toDateString() === today.toDateString()) return 'Today';
  if (notifDate.toDateString() === yesterday.toDateString()) return 'Yesterday';
  return notifDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const groupNotificationsByDate = (notifs: Notification[]): NotificationGroup[] => {
  const groups: Record<string, Notification[]> = {};

  notifs.forEach((notif) => {
    const date = formatDate(notif.timestamp);
    if (!groups[date]) groups[date] = [];
    groups[date].push(notif);
  });

  const sortedKeys = ['Today', 'Yesterday', ...Object.keys(groups).filter(k => k !== 'Today' && k !== 'Yesterday')];
  const result: NotificationGroup[] = [];

  sortedKeys.forEach((key) => {
    if (groups[key]) result.push({ date: key, notifications: groups[key] });
  });

  return result;
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>(MOCK_NOTIFICATIONS);
  const [activeTab, setActiveTab] = useState<'all' | 'unread'>('all');

  const unreadCount = notifications.filter((n) => !n.read).length;

  const filteredNotifications = useMemo(() => {
    return activeTab === 'unread' ? notifications.filter((n) => !n.read) : notifications;
  }, [notifications, activeTab]);

  const groupedNotifications = useMemo(
    () => groupNotificationsByDate(filteredNotifications),
    [filteredNotifications]
  );

  const handleMarkAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const handleMarkAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const handleDelete = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  return (
    <div className="w-full">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-2">
          <div className="flex items-center gap-3">
            <motion.div
              whileHover={{ scale: 1.1 }}
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-400 to-purple-600 flex items-center justify-center"
            >
              <Bell className="w-6 h-6 text-black" />
            </motion.div>
            <h1 className="text-3xl md:text-4xl font-black text-gradient-neon">Notifications</h1>
            {unreadCount > 0 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full"
              >
                {unreadCount} new
              </motion.span>
            )}
          </div>
          {unreadCount > 0 && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleMarkAllAsRead}
              className="gap-2 bg-gradient-to-r from-yellow-400 to-purple-600 hover:shadow-lg hover:shadow-yellow-400/30 text-black px-4 py-2 rounded-xl flex items-center font-bold transition-all duration-300 w-full sm:w-auto justify-center"
            >
              <CheckCircle2 className="w-4 h-4" />
              Mark all as read
            </motion.button>
          )}
        </div>
        <p className="text-muted-foreground">Stay updated with tips, messages, and activity</p>
      </motion.div>

      {/* Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="mb-6"
      >
        <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)}>
          <TabsList className="grid w-full grid-cols-2 bg-card border border-yellow-400/20 rounded-xl">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="unread">Unread ({unreadCount})</TabsTrigger>
          </TabsList>
        </Tabs>
      </motion.div>

      {/* Notifications List */}
      {groupedNotifications.length > 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="space-y-6"
        >
          {groupedNotifications.map((group, groupIdx) => (
            <div key={group.date}>
              <motion.h3
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: groupIdx * 0.05 }}
                className="text-lg font-bold text-yellow-400 mb-3"
              >
                {group.date}
              </motion.h3>

              <div className="space-y-3">
                {group.notifications.map((notif, idx) => (
                  <motion.div
                    key={notif.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: groupIdx * 0.05 + idx * 0.02 }}
                    whileHover={{ x: 5 }}
                    className={`p-4 md:p-5 rounded-xl border transition-all hover:border-yellow-400/50 group cursor-pointer ${
                      notif.read
                        ? 'bg-muted/50 border-border opacity-75'
                        : 'bg-card border-yellow-400/20 hover:bg-yellow-400/5'
                    }`}
                  >
                    <div className="flex items-start gap-3 md:gap-4">
                      <motion.div whileHover={{ scale: 1.1 }} className="mt-1 flex-shrink-0">
                        {getNotificationIcon(notif.type)}
                      </motion.div>

                      <div className="flex-1 min-w-0">
                        <p className={`font-semibold text-sm md:text-base break-words ${notif.read ? 'text-muted-foreground' : 'text-foreground'}`}>
                          {notif.title}
                        </p>
                        <p className="text-muted-foreground text-sm mt-1">{notif.description}</p>
                        <p className="text-muted-foreground text-xs mt-2">{formatTime(notif.timestamp)}</p>
                      </div>

                      {!notif.read && (
                        <motion.div
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                          className="w-2.5 h-2.5 rounded-full bg-yellow-400 flex-shrink-0 mt-1"
                        />
                      )}

                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                        {!notif.read && (
                          <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMarkAsRead(notif.id);
                            }}
                            className="p-2 hover:bg-yellow-400/20 rounded transition"
                            title="Mark as read"
                          >
                            <CheckCircle2 className="w-4 h-4 text-yellow-400" />
                          </motion.button>
                        )}
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(notif.id);
                          }}
                          className="p-2 hover:bg-red-500/20 rounded transition"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          ))}
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center py-12"
        >
          <motion.div
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="mb-4"
          >
            <Bell className="w-16 h-16 text-yellow-400/30 mx-auto opacity-50" />
          </motion.div>
          <p className="text-foreground text-lg font-semibold">No notifications</p>
          <p className="text-muted-foreground text-sm mt-2">
            {activeTab === 'unread' ? "You're all caught up!" : 'Check back later for updates'}
          </p>
        </motion.div>
      )}
    </div>
  );
}
