/**
 * React Hook for WebSocket Management
 * Provides real-time updates for notifications, messages, and live streams
 */

import { useEffect, useCallback, useRef } from 'react';
import { wsManager, WebSocketEventType, WebSocketMessage } from '@/lib/websocket/manager';
import { useAuthStore } from '@/store/authStore';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Main hook to initialize and manage WebSocket connection
 */
export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { autoConnect = true, onConnected, onDisconnected, onError } = options;
  const { user, accessToken } = useAuthStore();
  const connectionAttempted = useRef(false);

  useEffect(() => {
    if (!autoConnect || !user || !accessToken || connectionAttempted.current) {
      return;
    }

    connectionAttempted.current = true;

    const handleConnected = () => {
      console.log('[useWebSocket] Connected');
      onConnected?.();
    };

    const handleDisconnected = () => {
      console.log('[useWebSocket] Disconnected');
      onDisconnected?.();
    };

    const handleError = (message: WebSocketMessage) => {
      console.error('[useWebSocket] Error:', message.data);
      onError?.(new Error(message.data.error || 'WebSocket error'));
    };

    // Subscribe to connection events
    const unsubConnected = wsManager.subscribe(WebSocketEventType.CONNECTED, handleConnected);
    const unsubDisconnected = wsManager.subscribe(WebSocketEventType.DISCONNECTED, handleDisconnected);
    const unsubError = wsManager.subscribe(WebSocketEventType.ERROR, handleError);

    // Connect to WebSocket
    wsManager.connect(accessToken).catch((error) => {
      console.error('[useWebSocket] Failed to connect:', error);
      onError?.(error);
    });

    // Cleanup
    return () => {
      unsubConnected();
      unsubDisconnected();
      unsubError();
    };
  }, [user, accessToken, autoConnect, onConnected, onDisconnected, onError]);

  return {
    isConnected: wsManager.isConnected(),
    isReconnecting: wsManager.isReconnecting(),
    send: wsManager.send.bind(wsManager),
  };
}

/**
 * Hook to subscribe to notifications
 */
export function useNotifications(
  onNewNotification?: (notification: any) => void,
  onNotificationRead?: (notificationId: string) => void,
  enabled: boolean = true
) {
  useEffect(() => {
    if (!enabled) return;

    const unsubNew = wsManager.subscribe(WebSocketEventType.NOTIFICATION_NEW, (message) => {
      onNewNotification?.(message.data);
    });

    const unsubRead = wsManager.subscribe(WebSocketEventType.NOTIFICATION_READ, (message) => {
      onNotificationRead?.(message.data.notificationId);
    });

    return () => {
      unsubNew();
      unsubRead();
    };
  }, [onNewNotification, onNotificationRead, enabled]);
}

/**
 * Hook to subscribe to messages
 */
export function useMessages(
  conversationId: string,
  onNewMessage?: (message: any) => void,
  onTypingIndicator?: (data: any) => void,
  enabled: boolean = true
) {
  useEffect(() => {
    if (!enabled || !conversationId) return;

    const unsubMessage = wsManager.subscribe(WebSocketEventType.MESSAGE_NEW, (message) => {
      if (message.data.conversationId === conversationId) {
        onNewMessage?.(message.data);
      }
    });

    const unsubTyping = wsManager.subscribe(WebSocketEventType.TYPING_INDICATOR, (message) => {
      if (message.data.conversationId === conversationId) {
        onTypingIndicator?.(message.data);
      }
    });

    return () => {
      unsubMessage();
      unsubTyping();
    };
  }, [conversationId, onNewMessage, onTypingIndicator, enabled]);
}

/**
 * Hook to subscribe to live stream updates
 */
export function useLiveStreamUpdates(
  streamId: string | undefined,
  onStreamUpdate?: (update: any) => void,
  onStreamComment?: (comment: any) => void,
  enabled: boolean = true
) {
  useEffect(() => {
    if (!enabled || !streamId) return;

    const unsubUpdate = wsManager.subscribe(WebSocketEventType.STREAM_VIEWER_COUNT, (message) => {
      if (message.data.streamId === streamId) {
        onStreamUpdate?.(message.data);
      }
    });

    const unsubComment = wsManager.subscribe(WebSocketEventType.STREAM_COMMENT, (message) => {
      if (message.data.streamId === streamId) {
        onStreamComment?.(message.data);
      }
    });

    return () => {
      unsubUpdate();
      unsubComment();
    };
  }, [streamId, onStreamUpdate, onStreamComment, enabled]);
}

/**
 * Hook to subscribe to user presence
 */
export function useUserPresence(
  userId: string | undefined,
  onStatusChange?: (status: 'online' | 'offline' | 'away') => void,
  enabled: boolean = true
) {
  useEffect(() => {
    if (!enabled || !userId) return;

    const unsubOnline = wsManager.subscribe(WebSocketEventType.USER_ONLINE, (message) => {
      if (message.data.userId === userId) {
        onStatusChange?.('online');
      }
    });

    const unsubOffline = wsManager.subscribe(WebSocketEventType.USER_OFFLINE, (message) => {
      if (message.data.userId === userId) {
        onStatusChange?.('offline');
      }
    });

    const unsubStatusChanged = wsManager.subscribe(WebSocketEventType.USER_STATUS_CHANGED, (message) => {
      if (message.data.userId === userId) {
        onStatusChange?.(message.data.status);
      }
    });

    return () => {
      unsubOnline();
      unsubOffline();
      unsubStatusChanged();
    };
  }, [userId, onStatusChange, enabled]);
}

/**
 * Hook to subscribe to beat events
 */
export function useBeatEvents(
  onBeatPublished?: (beat: any) => void,
  onBeatFeatured?: (beat: any) => void,
  onBeatTrending?: (beat: any) => void,
  enabled: boolean = true
) {
  useEffect(() => {
    if (!enabled) return;

    const unsubPublished = wsManager.subscribe(WebSocketEventType.BEAT_PUBLISHED, (message) => {
      onBeatPublished?.(message.data);
    });

    const unsubFeatured = wsManager.subscribe(WebSocketEventType.BEAT_FEATURED, (message) => {
      onBeatFeatured?.(message.data);
    });

    const unsubTrending = wsManager.subscribe(WebSocketEventType.BEAT_TRENDING, (message) => {
      onBeatTrending?.(message.data);
    });

    return () => {
      unsubPublished();
      unsubFeatured();
      unsubTrending();
    };
  }, [onBeatPublished, onBeatFeatured, onBeatTrending, enabled]);
}

/**
 * Hook to subscribe to social events
 */
export function useSocialEvents(
  onFollowUser?: (data: any) => void,
  onLikeBeat?: (data: any) => void,
  onCommentBeat?: (data: any) => void,
  enabled: boolean = true
) {
  useEffect(() => {
    if (!enabled) return;

    const unsubFollow = wsManager.subscribe(WebSocketEventType.FOLLOW_USER, (message) => {
      onFollowUser?.(message.data);
    });

    const unsubLike = wsManager.subscribe(WebSocketEventType.LIKE_BEAT, (message) => {
      onLikeBeat?.(message.data);
    });

    const unsubComment = wsManager.subscribe(WebSocketEventType.COMMENT_BEAT, (message) => {
      onCommentBeat?.(message.data);
    });

    return () => {
      unsubFollow();
      unsubLike();
      unsubComment();
    };
  }, [onFollowUser, onLikeBeat, onCommentBeat, enabled]);
}

/**
 * Hook to subscribe to payment events
 */
export function usePaymentEvents(
  onPaymentReceived?: (payment: any) => void,
  onOrderCompleted?: (order: any) => void,
  onRefundProcessed?: (refund: any) => void,
  enabled: boolean = true
) {
  useEffect(() => {
    if (!enabled) return;

    const unsubPayment = wsManager.subscribe(WebSocketEventType.PAYMENT_RECEIVED, (message) => {
      onPaymentReceived?.(message.data);
    });

    const unsubOrder = wsManager.subscribe(WebSocketEventType.ORDER_COMPLETED, (message) => {
      onOrderCompleted?.(message.data);
    });

    const unsubRefund = wsManager.subscribe(WebSocketEventType.REFUND_PROCESSED, (message) => {
      onRefundProcessed?.(message.data);
    });

    return () => {
      unsubPayment();
      unsubOrder();
      unsubRefund();
    };
  }, [onPaymentReceived, onOrderCompleted, onRefundProcessed, enabled]);
}

/**
 * Hook to send typing indicator
 */
export function useSendTypingIndicator(conversationId: string) {
  const typingTimeout = useRef<NodeJS.Timeout | null>(null);

  const sendTypingIndicator = useCallback(() => {
    // Clear previous timeout
    if (typingTimeout.current) {
      clearTimeout(typingTimeout.current);
    }

    // Send typing indicator
    wsManager.send({
      type: WebSocketEventType.TYPING_INDICATOR,
      data: { conversationId },
      timestamp: Date.now(),
    });

    // Clear indicator after 3 seconds of inactivity
    typingTimeout.current = setTimeout(() => {
      typingTimeout.current = null;
    }, 3000);
  }, [conversationId]);

  return sendTypingIndicator;
}

export default useWebSocket;
