/**
 * Chat Store - Zustand state management for AI Chat Interface
 * Handles chat state, messages, streaming, and sessionStorage persistence
 */

import { create } from 'zustand';
import type {
  ChatStore,
  Message,
  QuotaStatus,
  ChatError,
  ConnectionStatus,
} from '../types';
import { CHAT_CONFIG, STORAGE_KEYS } from '../constants';

/**
 * Create a unique message ID
 */
const createMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Create a unique conversation ID
 */
const createConversationId = (): string => {
  return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const useChatStore = create<ChatStore>((set, get) => ({
  // ============================================================================
  // State
  // ============================================================================
  isOpen: false,
  messages: [],
  streamingContent: '',
  isStreaming: false,
  connectionStatus: 'disconnected',
  quota: null,
  error: null,
  retryCount: 0,
  lastFailedMessage: null,
  autoFillCallbacks: {}, // Store callbacks for "Use This" functionality

  // ============================================================================
  // Actions
  // ============================================================================

  openChat: () => {
    set({ isOpen: true });
    get().loadFromSession();
  },

  closeChat: () => {
    set({ isOpen: false });
    get().saveToSession();
  },

  sendMessage: (content: string) => {
    const state = get();
    
    // Create user message
    const userMessage: Message = {
      id: createMessageId(),
      conversationId: state.messages[0]?.conversationId || createConversationId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    // Add to messages
    set((state) => ({
      messages: [...state.messages, userMessage],
      isStreaming: true,
      streamingContent: '',
      error: null,
      lastFailedMessage: content, // Store for retry
    }));

    // Save to session
    get().saveToSession();
  },

  appendStreamingChunk: (chunk: string) => {
    set((state) => ({
      streamingContent: state.streamingContent + chunk,
      isStreaming: true,
    }));
  },

  finalizeStreamingMessage: () => {
    const state = get();
    
    if (!state.streamingContent) {
      set({ isStreaming: false });
      return;
    }

    // Create AI message from streaming content
    const aiMessage: Message = {
      id: createMessageId(),
      conversationId: state.messages[0]?.conversationId || createConversationId(),
      role: 'assistant',
      content: state.streamingContent,
      timestamp: new Date(),
    };

    // Add to messages and clear streaming state
    set((state) => ({
      messages: [...state.messages, aiMessage],
      streamingContent: '',
      isStreaming: false,
    }));

    // Save to session
    get().saveToSession();
  },

  clearConversation: () => {
    set({
      messages: [],
      streamingContent: '',
      isStreaming: false,
      error: null,
    });

    // Clear sessionStorage
    try {
      sessionStorage.removeItem(STORAGE_KEYS.CHAT_SESSION);
    } catch (error) {
      console.error('Failed to clear sessionStorage:', error);
    }
  },

  updateQuota: (quota: QuotaStatus) => {
    set({ quota });
  },

  setError: (error: ChatError | null) => {
    set({ error });
    
    // If error is set, stop streaming
    if (error) {
      set({ isStreaming: false });
    }
  },

  setConnectionStatus: (status: ConnectionStatus) => {
    set({ connectionStatus: status });
  },

  retryLastMessage: () => {
    const state = get();
    
    // Clear error and reset retry count if this is a manual retry
    set({ 
      error: null,
      retryCount: 0,
    });
    
    // Retry is handled by the WebSocket hook which will resend
    // the last message stored in lastFailedMessage
  },

  incrementRetryCount: () => {
    set((state) => ({
      retryCount: state.retryCount + 1,
    }));
  },

  resetRetryCount: () => {
    set({ retryCount: 0 });
  },

  // ============================================================================
  // Auto-fill Callbacks (for "Use This" functionality)
  // ============================================================================

  setAutoFillCallback: (key: string, callback: (...args: any[]) => void) => {
    set((state) => ({
      autoFillCallbacks: {
        ...state.autoFillCallbacks,
        [key]: callback,
      },
    }));
  },

  getAutoFillCallback: (key: string) => {
    const state = get();
    return state.autoFillCallbacks[key];
  },

  clearAutoFillCallbacks: () => {
    set({ autoFillCallbacks: {} });
  },

  // ============================================================================
  // Persistence
  // ============================================================================

  loadFromSession: () => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEYS.CHAT_SESSION);
      
      if (!stored) {
        return;
      }

      const session = JSON.parse(stored);
      
      // Check if session has expired (1 hour)
      const expiresAt = new Date(session.expiresAt);
      const now = new Date();
      
      if (now > expiresAt) {
        // Session expired, clear it
        sessionStorage.removeItem(STORAGE_KEYS.CHAT_SESSION);
        return;
      }

      // Restore messages (limit to max)
      const messages: Message[] = (session.messages || [])
        .slice(-CHAT_CONFIG.MAX_MESSAGES_PER_SESSION)
        .map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));

      set({ messages });
    } catch (error) {
      console.error('Failed to load from sessionStorage:', error);
    }
  },

  saveToSession: () => {
    try {
      const state = get();
      
      // Limit messages to max
      const messagesToSave = state.messages.slice(-CHAT_CONFIG.MAX_MESSAGES_PER_SESSION);
      
      // Calculate expiry time (1 hour from now)
      const expiresAt = new Date();
      expiresAt.setHours(expiresAt.getHours() + CHAT_CONFIG.SESSION_EXPIRY_HOURS);

      const session = {
        conversationId: messagesToSave[0]?.conversationId || createConversationId(),
        messages: messagesToSave,
        lastUpdated: new Date().toISOString(),
        expiresAt: expiresAt.toISOString(),
      };

      sessionStorage.setItem(STORAGE_KEYS.CHAT_SESSION, JSON.stringify(session));
    } catch (error) {
      console.error('Failed to save to sessionStorage:', error);
      
      // Check if quota exceeded
      if (error instanceof Error && error.name === 'QuotaExceededError') {
        // Clear old messages to make space
        const state = get();
        const reducedMessages = state.messages.slice(-Math.floor(CHAT_CONFIG.MAX_MESSAGES_PER_SESSION / 2));
        set({ messages: reducedMessages });
        
        // Try saving again with reduced messages
        try {
          const session = {
            conversationId: reducedMessages[0]?.conversationId || createConversationId(),
            messages: reducedMessages,
            lastUpdated: new Date().toISOString(),
            expiresAt: new Date(Date.now() + CHAT_CONFIG.SESSION_EXPIRY_HOURS * 60 * 60 * 1000).toISOString(),
          };
          sessionStorage.setItem(STORAGE_KEYS.CHAT_SESSION, JSON.stringify(session));
        } catch {
          // If still fails, give up
          console.error('Failed to save even with reduced messages');
        }
      }
    }
  },
}));

// ============================================================================
// Debounced save helper (for auto-save)
// ============================================================================

let saveTimeout: NodeJS.Timeout | null = null;

export const debouncedSaveToSession = () => {
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }
  
  saveTimeout = setTimeout(() => {
    useChatStore.getState().saveToSession();
  }, CHAT_CONFIG.SAVE_DEBOUNCE_MS);
};
