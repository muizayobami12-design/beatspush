/**
 * ChatProvider - Global provider for chat interface
 * Manages chat visibility and provides context to children
 */

'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { ChatInterface } from './ChatInterface';
import { useChatStore } from '../store/chatStore';
import type { QuotaStatus as ChatQuotaStatus } from '../types';

interface ChatContextValue {
  openChat: () => void;
  closeChat: () => void;
  isOpen: boolean;
  quota: ChatQuotaStatus | null;
  refreshQuota: () => Promise<void>;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
}

interface ChatProviderProps {
  children: React.ReactNode;
}

export function ChatProvider({ children }: ChatProviderProps) {
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);
  const { isOpen, openChat: openChatStore, closeChat: closeChatStore } = useChatStore();

  const openChat = useCallback(() => {
    openChatStore();
  }, [openChatStore]);

  const closeChat = useCallback(() => {
    closeChatStore();
  }, [closeChatStore]);

  const refreshQuota = useCallback(async () => {
    // TODO: Implement quota refresh
  }, []);

  const contextValue: ChatContextValue = {
    openChat,
    closeChat,
    isOpen,
    quota: null,
    refreshQuota,
  };

  return (
    <ChatContext.Provider value={contextValue}>
      {children}
      
      {/* Chat Interface */}
      <ChatInterface
        isOpen={isOpen}
        onClose={closeChat}
        initialContext={undefined}
      />
    </ChatContext.Provider>
  );
}
