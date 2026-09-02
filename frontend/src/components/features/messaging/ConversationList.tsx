'use client';

import { useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageSquare } from 'lucide-react';
import type { Conversation } from '@/services/messagingService';
import { ConversationListItem } from './ConversationListItem';

interface ConversationListProps {
  conversations: Conversation[];
  selectedConversation: Conversation | null;
  onSelectConversation: (conversation: Conversation) => void;
  currentUserId?: string;
  /** Whether a real-time WebSocket connection is active */
  isConnected?: boolean;
}

/**
 * ConversationList — renders the scrollable list of conversation items.
 * Receives live-updated `conversations` from the parent (MessagesPage),
 * which re-fetches / patches state on WebSocket events.
 */
export default function ConversationList({
  conversations,
  selectedConversation,
  onSelectConversation,
  currentUserId,
  isConnected,
}: ConversationListProps) {
  // Keep a ref to the previously-selected conversation so the list can
  // scroll the selected item into view when the selection changes via URL.
  const selectedRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    selectedRef.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [selectedConversation?.id]);

  if (conversations.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-center">
        <div>
          <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
          <p className="font-medium text-muted-foreground">No conversations yet</p>
          <p className="text-sm text-muted-foreground mt-1">
            Start a new conversation to get going
          </p>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1">
      <div role="list" className="divide-y">
        {conversations.map((conversation) => {
          const isSelected = selectedConversation?.id === conversation.id;
          return (
            <div
              key={conversation.id}
              role="listitem"
              ref={isSelected ? selectedRef : undefined}
            >
              <ConversationListItem
                conversation={conversation}
                currentUserId={currentUserId}
                isSelected={isSelected}
                onClick={onSelectConversation}
              />
            </div>
          );
        })}
      </div>
    </ScrollArea>
  );
}
