/**
 * Main export file for AI Chat Interface
 * Provides clean imports for all chat-related components, types, and utilities
 */

// ============================================================================
// Types and Interfaces
// ============================================================================

export type {
  // Core types
  Message,
  MessageRole,
  MessageMetadata,
  Conversation,
  ConversationMetadata,
  ChatState,
  ConnectionStatus,
  
  // WebSocket types
  ChatMessagePayload,
  StreamingChunk,
  StreamingChunkType,
  WebSocketClientConfig,
  WebSocketCallbacks,
  
  // Context types
  PageContext,
  PageType,
  PageContextDefinition,
  
  // Quick action types
  QuickActionType,
  QuickActionDefinition,
  
  // Quota types
  QuotaStatus,
  UserTier,
  
  // Error types
  ChatError,
  ErrorAction,
  
  // Session types
  ChatSession,
  
  // Component props
  ChatInterfaceProps,
  MessageBubbleProps,
  TypingIndicatorProps,
  QuickActionButtonProps,
  QuotaDisplayProps,
  CopyButtonProps,
  ChatHeaderProps,
  MessageInputProps,
  UpgradePromptProps,
  
  // Store types
  ChatStore,
} from './types';

export { ChatErrorType } from './types';

// ============================================================================
// Constants and Configuration
// ============================================================================

export {
  WEBSOCKET_CONFIG,
  CHAT_CONFIG,
  UI_CONFIG,
  QUICK_ACTIONS,
  CONTEXT_EXTRACTORS,
  ERROR_MESSAGES,
  COLORS,
  STORAGE_KEYS,
  API_ENDPOINTS,
} from './constants';

// ============================================================================
// Components (will be exported as they are implemented)
// ============================================================================

// Main component
export { ChatInterface } from './components/ChatInterface';

// Sub-components
export { MessageBubble } from './components/MessageBubble';
export { TypingIndicator } from './components/TypingIndicator';
export { CopyButton } from './components/CopyButton';
export { ChatHeader } from './components/ChatHeader';
export { MessageList } from './components/MessageList';
export { MessageInput } from './components/MessageInput';
export { QuotaDisplay } from './components/QuotaDisplay';
export { QuickActionButton } from './components/QuickActionButton';
export { QuickActionBar } from './components/QuickActionBar';
export { UpgradePrompt } from './components/UpgradePrompt';
export { ChatProvider, useChatContext } from './components/ChatProvider';
export { ChatTriggerButton } from './components/ChatTriggerButton';

// ============================================================================
// Hooks (will be exported as they are implemented)
// ============================================================================

export { useChatWebSocket } from './hooks/useChatWebSocket';
export { usePageContext } from './hooks/usePageContext';
export { useChatStore } from './store/chatStore';

// ============================================================================
// Utils (will be exported as they are implemented)
// ============================================================================

export * from './utils/contextUtils';
export * from './utils/errorUtils';
export { ErrorMessage } from './components/ErrorMessage';
