'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Conversation, Message } from '@/services/messagingService';
import messagingService from '@/services/messagingService';
import { useWebSocket } from '@/hooks/useWebSocket';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import BlockUserModal from './BlockUserModal';
import ReportMessageModal from './ReportMessageModal';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ArrowLeft, MoreVertical, Phone, Video, ChevronUp,
  WifiOff, Shield
} from 'lucide-react';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useRouter } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';

interface MessageThreadProps {
  conversation: Conversation;
  onConversationUpdate: () => void;
}

const POLLING_INTERVAL_MS = 3000;

export default function MessageThread({
  conversation,
  onConversationUpdate,
}: MessageThreadProps) {
  const router = useRouter();

  // ── State ────────────────────────────────────────────────────────────────
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingOlder, setLoadingOlder] = useState(false);
  const [hasOlderMessages, setHasOlderMessages] = useState(false);
  const [nextCursor, setNextCursor] = useState<string | undefined>();
  const [sending, setSending] = useState(false);
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set());
  const [currentUserId, setCurrentUserId] = useState('');
  const [editingMessage, setEditingMessage] = useState<Message | null>(null);
  const [onlineUsers, setOnlineUsers] = useState<Set<string>>(new Set());
  const [blockModal, setBlockModal] = useState(false);
  const [reportMessageId, setReportMessageId] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const pollingTimerRef = useRef<NodeJS.Timeout | null>(null);

  // ── Get current user from JWT ─────────────────────────────────────────────
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          setCurrentUserId(payload.sub || payload.user_id || '');
        } catch { /* invalid jwt */ }
      }
    }
  }, []);

  const otherParticipant = conversation.participants.find(
    (p) => p.id !== currentUserId
  ) ?? conversation.participants[0];

  const isOtherOnline = onlineUsers.has(otherParticipant?.id ?? '');

  // ── WebSocket ─────────────────────────────────────────────────────────────
  const { isConnected, sendTypingIndicator, joinConversation, leaveConversation } = useWebSocket({
    onNewMessage: (event) => {
      if (event.conversation_id !== conversation.id) return;
      setMessages((prev) => {
        if (prev.some((m) => m.id === event.message.id)) return prev;
        return [...prev, event.message];
      });
      scrollToBottom();
      // Auto-mark as read
      messagingService.markConversationRead(conversation.id).catch(() => {});
      onConversationUpdate();
    },
    onTyping: (event) => {
      if (event.conversation_id !== conversation.id) return;
      setTypingUsers((prev) => {
        const next = new Set(prev);
        if (event.is_typing) next.add(event.user_id);
        else next.delete(event.user_id);
        return next;
      });
    },
    onMessageEdited: (event) => {
      if (event.conversation_id !== conversation.id) return;
      setMessages((prev) =>
        prev.map((m) => (m.id === event.message.id ? event.message : m))
      );
    },
    onMessageDeleted: (event) => {
      if (event.conversation_id !== conversation.id) return;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === event.message_id
            ? { ...m, content: '[Message deleted]', deleted_at: new Date().toISOString() }
            : m
        )
      );
    },
    onMessageRead: (event) => {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === event.message_id && !m.read_by.includes(event.read_by)
            ? { ...m, read_by: [...m.read_by, event.read_by] }
            : m
        )
      );
    },
    onUserStatus: (event) => {
      setOnlineUsers((prev) => {
        const next = new Set(prev);
        if (event.type === 'user_online') next.add(event.user_id);
        else next.delete(event.user_id);
        return next;
      });
    },
    onConnect: () => {
      // Stop polling once WS is up
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
        pollingTimerRef.current = null;
      }
    },
  });

  // ── Polling fallback (task 19.4) ──────────────────────────────────────────
  const startPolling = useCallback(() => {
    if (pollingTimerRef.current) return;
    pollingTimerRef.current = setInterval(async () => {
      try {
        const since = messages[messages.length - 1]?.created_at;
        const result = await messagingService.getMessages(conversation.id, {
          page_size: 20,
          cursor: since ? undefined : undefined,
        });
        if (result.messages.length > 0) {
          setMessages((prev) => {
            const existingIds = new Set(prev.map((m) => m.id));
            const newOnes = result.messages.filter((m) => !existingIds.has(m.id));
            return newOnes.length > 0 ? [...prev, ...newOnes] : prev;
          });
        }
      } catch { /* silent */ }
    }, POLLING_INTERVAL_MS);
  }, [conversation.id, messages]);

  useEffect(() => {
    if (!isConnected) startPolling();
    return () => {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
        pollingTimerRef.current = null;
      }
    };
  }, [isConnected, startPolling]);

  // ── Load initial messages ─────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      try {
        const result = await messagingService.getMessages(conversation.id, { page_size: 50 });
        if (!cancelled) {
          setMessages(result.messages);
          setHasOlderMessages(result.has_more);
          setNextCursor(result.next_cursor);
          scrollToBottom();
          // Mark as read (task 24.1)
          await messagingService.markConversationRead(conversation.id);
          onConversationUpdate();
        }
      } catch (err) {
        console.error('Failed to load messages', err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => { cancelled = true; };
  }, [conversation.id]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Join / leave conversation via WS ─────────────────────────────────────
  useEffect(() => {
    if (isConnected) joinConversation(conversation.id);
    return () => {
      if (isConnected) leaveConversation(conversation.id);
    };
  }, [conversation.id, isConnected, joinConversation, leaveConversation]);

  // ── Helpers ───────────────────────────────────────────────────────────────
  const scrollToBottom = () => {
    setTimeout(() => scrollRef.current?.scrollIntoView({ behavior: 'smooth' }), 80);
  };

  const loadOlderMessages = async () => {
    if (!hasOlderMessages || loadingOlder) return;
    setLoadingOlder(true);
    try {
      const result = await messagingService.getMessages(conversation.id, {
        page_size: 50,
        cursor: nextCursor,
      });
      setMessages((prev) => [...result.messages, ...prev]);
      setHasOlderMessages(result.has_more);
      setNextCursor(result.next_cursor);
    } catch (err) {
      console.error('Failed to load older messages', err);
    } finally {
      setLoadingOlder(false);
    }
  };

  // ── Send / edit ───────────────────────────────────────────────────────────
  const handleSend = async (content: string) => {
    if (!content.trim()) return;
    setSending(true);
    try {
      if (editingMessage) {
        // Edit existing message (task 26.1)
        const updated = await messagingService.editMessage(editingMessage.id, content.trim());
        setMessages((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
        setEditingMessage(null);
      } else {
        const message = await messagingService.sendMessage({
          conversation_id: conversation.id,
          content: content.trim(),
        });
        setMessages((prev) => [...prev, message]);
        scrollToBottom();
        onConversationUpdate();
      }
      sendTypingIndicator(conversation.id, false);
    } catch (err) {
      console.error('Failed to send message', err);
    } finally {
      setSending(false);
    }
  };

  const handleTyping = (isTyping: boolean) => {
    if (isConnected) sendTypingIndicator(conversation.id, isTyping);
  };

  const handleDeleteMessage = async (messageId: string) => {
    try {
      await messagingService.deleteMessage(messageId);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === messageId
            ? { ...m, content: '[Message deleted]', deleted_at: new Date().toISOString() }
            : m
        )
      );
    } catch (err) {
      console.error('Failed to delete message', err);
    }
  };

  // ── Typing display text ───────────────────────────────────────────────────
  const typingText = (() => {
    const ids = [...typingUsers].filter((id) => id !== currentUserId);
    if (ids.length === 0) return null;
    if (ids.length === 1) return `${otherParticipant?.full_name || 'Someone'} is typing…`;
    return 'Several people are typing…';
  })();

  // ── Loading ───────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Loading messages…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* ── Header ── */}
      <div className="p-4 border-b flex items-center gap-3 flex-shrink-0">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push('/messages')}
          className="md:hidden"
          aria-label="Back to conversations"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>

        <div className="relative">
          <Avatar className="h-10 w-10">
            <AvatarImage src={otherParticipant?.avatar_url} />
            <AvatarFallback>
              {(otherParticipant?.username ?? 'U').slice(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          {/* Online dot (task 24.3) */}
          {isOtherOnline && (
            <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full bg-green-500 border-2 border-background" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <h2 className="font-semibold truncate">
            {otherParticipant?.full_name || otherParticipant?.username || 'Unknown User'}
          </h2>
          <p className="text-xs text-muted-foreground">
            {typingText ?? (isOtherOnline ? 'Online' : `Active ${
              otherParticipant?.username ? formatDistanceToNow(new Date(), { addSuffix: true }) : 'recently'
            }`)}
          </p>
        </div>

        <div className="flex items-center gap-1 flex-shrink-0">
          {!isConnected && (
            <span className="flex items-center gap-1 text-xs text-amber-600 mr-2" title="Offline mode — using polling">
              <WifiOff className="h-3 w-3" /> Offline
            </span>
          )}
          {conversation.is_message_request && (
            <Badge variant="outline" className="text-xs">Request</Badge>
          )}
          <Button variant="ghost" size="icon" disabled title="Call (coming soon)">
            <Phone className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" disabled title="Video (coming soon)">
            <Video className="h-5 w-5" />
          </Button>

          {/* Block / more actions (task 22.3) */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="More options">
                <MoreVertical className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                className="text-destructive"
                onClick={() => setBlockModal(true)}
              >
                <Shield className="mr-2 h-4 w-4" /> Block user
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* ── Messages ── */}
      <ScrollArea className="flex-1 p-4">
        {/* Load older (task 18.1) */}
        {hasOlderMessages && (
          <div className="flex justify-center mb-4">
            <Button
              variant="outline"
              size="sm"
              onClick={loadOlderMessages}
              disabled={loadingOlder}
              className="gap-1"
            >
              <ChevronUp className="h-4 w-4" />
              {loadingOlder ? 'Loading…' : 'Load older messages'}
            </Button>
          </div>
        )}

        <div className="space-y-3">
          {messages.length === 0 ? (
            <p className="text-center text-muted-foreground py-12 text-sm">
              No messages yet. Say hello! 👋
            </p>
          ) : (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                isOwn={message.sender_id === currentUserId}
                onDelete={handleDeleteMessage}
                onEdit={(msg) => setEditingMessage(msg)}
                onReport={(msgId) => setReportMessageId(msgId)}
              />
            ))
          )}
        </div>

        {/* Typing indicator (task 18.4) */}
        {typingText && (
          <div className="flex items-center gap-2 mt-2 px-2 text-xs text-muted-foreground">
            <span className="flex gap-0.5">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-bounce"
                  style={{ animationDelay: `${i * 150}ms` }}
                />
              ))}
            </span>
            {typingText}
          </div>
        )}

        <div ref={scrollRef} />
      </ScrollArea>

      {/* ── Edit indicator banner ── */}
      {editingMessage && (
        <div className="px-4 py-2 bg-primary/5 border-t border-primary/20 flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            Editing: <em className="text-foreground line-clamp-1 max-w-xs">{editingMessage.content}</em>
          </span>
          <Button variant="ghost" size="sm" onClick={() => setEditingMessage(null)}>Cancel</Button>
        </div>
      )}

      {/* ── Input ── */}
      <div className="border-t p-4 flex-shrink-0">
        <MessageInput
          onSend={handleSend}
          onTyping={handleTyping}
          disabled={sending || conversation.is_message_request}
          placeholder={
            conversation.is_message_request
              ? 'Accept message request to reply'
              : editingMessage
              ? 'Edit your message…'
              : 'Type a message…'
          }
          initialValue={editingMessage?.content}
          key={editingMessage?.id ?? 'new'}
        />
      </div>

      {/* ── Modals ── */}
      {otherParticipant && (
        <BlockUserModal
          isOpen={blockModal}
          onClose={() => setBlockModal(false)}
          userId={otherParticipant.id}
          userName={otherParticipant.full_name || otherParticipant.username}
          onBlocked={onConversationUpdate}
        />
      )}

      {reportMessageId && (
        <ReportMessageModal
          isOpen
          onClose={() => setReportMessageId(null)}
          messageId={reportMessageId}
        />
      )}
    </div>
  );
}
