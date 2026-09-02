'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import messagingService, { Conversation } from '@/services/messagingService';
import ConversationList from '@/components/features/messaging/ConversationList';
import MessageThread from '@/components/features/messaging/MessageThread';
import { NewConversationModal } from '@/components/features/messaging/NewConversationModal';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MessageSquarePlus, Settings, Inbox, Search } from 'lucide-react';
import { cn } from '@/lib/utils';

// ── Filter tabs (task 23.3) ─────────────────────────────────────────────────
type FilterTab = 'all' | 'unread' | 'requests' | 'archived';

const FILTER_TABS: { value: FilterTab; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'unread', label: 'Unread' },
  { value: 'requests', label: 'Requests' },
  { value: 'archived', label: 'Archived' },
];

export default function MessagesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const conversationId = searchParams.get('conversation');

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState<FilterTab>('all');
  const [unreadCount, setUnreadCount] = useState(0);
  const [currentUserId, setCurrentUserId] = useState('');
  const [showNewModal, setShowNewModal] = useState(false);
  // Mobile: show list or thread
  const [mobileView, setMobileView] = useState<'list' | 'thread'>('list');

  const selectedConvRef = useRef<Conversation | null>(null);
  selectedConvRef.current = selectedConversation;

  const filterRef = useRef(activeFilter);
  filterRef.current = activeFilter;

  const searchRef = useRef(searchQuery);
  searchRef.current = searchQuery;

  // ─── Fetchers ────────────────────────────────────────────────────────────

  const loadConversations = useCallback(async () => {
    try {
      const unread_only = filterRef.current === 'unread';
      const result = await messagingService.listConversations({
        page: 1,
        page_size: 50,
        unread_only,
        search: searchRef.current || undefined,
      });
      // Client-side filter for requests / archived tabs
      let convs = result.conversations;
      if (filterRef.current === 'requests') {
        convs = convs.filter((c) => c.is_message_request);
      } else if (filterRef.current === 'archived') {
        convs = convs.filter((c) => c.is_archived);
      }
      setConversations(convs);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  }, []);

  const loadUnreadCount = useCallback(async () => {
    try {
      const result = await messagingService.getUnreadCount();
      setUnreadCount(result.unread_count);
    } catch { /* silent */ }
  }, []);

  // ─── WebSocket ────────────────────────────────────────────────────────────

  const handleNewMessage = useCallback(
    (event: { conversation_id: string }) => {
      setConversations((prev) =>
        prev.map((conv) => {
          if (conv.id !== event.conversation_id) return conv;
          if (selectedConvRef.current?.id === conv.id) {
            messagingService.markConversationRead(conv.id).catch(console.error);
            return conv;
          }
          return { ...conv, unread_count: conv.unread_count + 1 };
        })
      );
      setUnreadCount((n) => n + 1);
      loadConversations();
    },
    [loadConversations]
  );

  const handleMessageRead = useCallback(() => {
    loadUnreadCount();
  }, [loadUnreadCount]);

  const { isConnected } = useWebSocket({
    onNewMessage: handleNewMessage,
    onMessageRead: handleMessageRead,
  });

  // ─── Bootstrap ───────────────────────────────────────────────────────────

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const p = JSON.parse(atob(token.split('.')[1]));
          setCurrentUserId(p.sub || p.user_id || '');
        } catch { /* invalid jwt */ }
      }
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([loadConversations(), loadUnreadCount()]);
      setLoading(false);
    };
    init();
  }, [activeFilter, searchQuery, loadConversations, loadUnreadCount]);

  // Sync URL param → selected conversation
  useEffect(() => {
    if (!conversationId) return;
    const conv = conversations.find((c) => c.id === conversationId);
    if (conv) {
      setSelectedConversation(conv);
      setMobileView('thread');
    } else if (conversationId) {
      messagingService.getConversation(conversationId)
        .then((c) => { setSelectedConversation(c); setMobileView('thread'); })
        .catch(console.error);
    }
  }, [conversationId, conversations]);

  // ─── Handlers ─────────────────────────────────────────────────────────────

  const handleSelectConversation = (conv: Conversation) => {
    setSelectedConversation(conv);
    setMobileView('thread');
    router.push(`/messages?conversation=${conv.id}`, { scroll: false });

    if (conv.unread_count > 0) {
      messagingService.markConversationRead(conv.id)
        .then(() => {
          setConversations((prev) =>
            prev.map((c) => c.id === conv.id ? { ...c, unread_count: 0 } : c)
          );
          loadUnreadCount();
        })
        .catch(console.error);
    }
  };

  const handleBackToList = () => {
    setMobileView('list');
    setSelectedConversation(null);
    router.push('/messages', { scroll: false });
  };

  // ─── Loading ─────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading messages…</p>
        </div>
      </div>
    );
  }

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background">

      {/* ── Sidebar (hidden on mobile when thread open) ── */}
      <div className={cn(
        'flex flex-col border-r bg-background',
        // On mobile: full width, toggle with thread
        'w-full md:w-96',
        mobileView === 'thread' ? 'hidden md:flex' : 'flex'
      )}>
        {/* Header */}
        <div className="p-4 border-b space-y-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold">Messages</h1>
              {unreadCount > 0 && (
                <p className="text-xs text-muted-foreground">{unreadCount} unread</p>
              )}
            </div>
            <div className="flex gap-1">
              <Button variant="ghost" size="icon" onClick={() => router.push('/messages/requests')} title="Message Requests">
                <Inbox className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" onClick={() => router.push('/messages/settings')} title="Settings">
                <Settings className="h-5 w-5" />
              </Button>
              <Button size="icon" onClick={() => setShowNewModal(true)} title="New Message">
                <MessageSquarePlus className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* Search (task 23.1) */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              type="search"
              placeholder="Search conversations…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Filter chips (task 23.3) */}
          <div className="flex gap-1 overflow-x-auto no-scrollbar" role="tablist">
            {FILTER_TABS.map((tab) => (
              <button
                key={tab.value}
                role="tab"
                aria-selected={activeFilter === tab.value}
                onClick={() => setActiveFilter(tab.value)}
                className={cn(
                  'flex-shrink-0 px-3 py-1 rounded-full text-xs font-medium transition-colors',
                  activeFilter === tab.value
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                )}
              >
                {tab.label}
                {tab.value === 'unread' && unreadCount > 0 && (
                  <span className="ml-1 bg-destructive text-destructive-foreground rounded-full px-1 text-[10px]">
                    {unreadCount}
                  </span>
                )}
              </button>
            ))}
            <div className="ml-auto flex items-center gap-1 flex-shrink-0">
              <span className={cn('h-2 w-2 rounded-full', isConnected ? 'bg-green-500' : 'bg-amber-500')} />
              <span className="text-xs text-muted-foreground">{isConnected ? 'Live' : 'Offline'}</span>
            </div>
          </div>
        </div>

        {/* Conversation list */}
        <ConversationList
          conversations={conversations}
          selectedConversation={selectedConversation}
          onSelectConversation={handleSelectConversation}
          currentUserId={currentUserId}
          isConnected={isConnected}
        />
      </div>

      {/* ── Message Thread (hidden on mobile when list shown) ── */}
      <div className={cn(
        'flex-1 flex flex-col',
        mobileView === 'list' ? 'hidden md:flex' : 'flex'
      )}>
        {selectedConversation ? (
          <MessageThread
            conversation={selectedConversation}
            onConversationUpdate={() => { loadConversations(); loadUnreadCount(); }}
            onBack={handleBackToList}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center text-center p-8">
            <div>
              <MessageSquarePlus className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h2 className="text-2xl font-semibold mb-2">Select a conversation</h2>
              <p className="text-muted-foreground mb-6">
                Choose from the list or start a new one
              </p>
              <Button onClick={() => setShowNewModal(true)}>
                <MessageSquarePlus className="mr-2 h-4 w-4" />
                New Message
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* New conversation modal */}
      <NewConversationModal
        isOpen={showNewModal}
        onClose={() => setShowNewModal(false)}
        onConversationCreated={(id) => {
          setShowNewModal(false);
          router.push(`/messages?conversation=${id}`);
          loadConversations();
        }}
      />
    </div>
  );
}
