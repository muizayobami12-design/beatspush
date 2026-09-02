/**
 * Core TypeScript interfaces for AI Chat Interface
 * Based on design.md specifications
 */

// ============================================================================
// Message and Conversation Types
// ============================================================================

export type MessageRole = 'user' | 'assistant' | 'system';

export interface MessageMetadata {
  // Performance metrics
  responseTimeMs?: number;
  quotaUsed?: number;
  
  // AI provider info
  provider?: string;
  model?: string;
  cached?: boolean;
  
  // Context info
  pageType?: PageType;
  contextData?: Record<string, any>;
  
  // User feedback
  liked?: boolean;
  copied?: boolean;
}

export interface Message {
  id: string;
  conversationId?: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  metadata?: MessageMetadata;
}

export interface ConversationMetadata {
  totalMessages: number;
  quotaUsed: number;
  avgResponseTime: number;
  pageTypes: PageType[];
}

export interface Conversation {
  id: string;
  userId: string;
  messages: Message[];
  createdAt: Date;
  lastUpdated: Date;
  expiresAt: Date;
  metadata: ConversationMetadata;
}

// ============================================================================
// Chat State Types
// ============================================================================

export type ConnectionStatus = 'connected' | 'connecting' | 'disconnected';

export interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  connectionStatus: ConnectionStatus;
  error: string | null;
}

// ============================================================================
// WebSocket Message Protocol Types
// ============================================================================

export interface ChatMessagePayload {
  type: 'chat_message';
  content: string;
  context: PageContext;
  conversationId?: string;
}

export type StreamingChunkType = 'chunk' | 'done' | 'error';

export interface StreamingChunk {
  type: StreamingChunkType;
  content?: string;
  error?: string;
  metadata?: {
    quotaRemaining: number;
    responseTimeMs: number;
  };
}

// ============================================================================
// Page Context Types
// ============================================================================

export type PageType =
  | 'beat_upload'
  | 'beat_edit'
  | 'campaign_dashboard'
  | 'analytics'
  | 'profile_edit'
  | 'social_feed'
  | 'messaging'
  | 'general';

export interface PageContext {
  pageType: PageType;
  pageUrl: string;
  contextData: Record<string, any>;
}

export interface PageContextDefinition {
  pageType: PageType;
  extractContext: (props: any) => Record<string, any>;
  quickActions: string[]; // Quick action IDs
  contextDisplay: string; // e.g., "Helping with: Beat Upload"
}

// ============================================================================
// Quick Action Types
// ============================================================================

export type QuickActionType =
  | 'generate_title'
  | 'write_description'
  | 'create_tags'
  | 'generate_captions'
  | 'analyze_performance'
  | 'suggest_optimizations'
  | 'explain_trends'
  | 'write_bio'
  | 'recommend_price'
  | 'improve_description'
  | 'suggest_price_changes'
  | 'generate_ad_copy'
  | 'compare_performance'
  | 'get_recommendations'
  | 'craft_artist_statement'
  | 'suggest_improvements'
  | 'suggest_hashtags'
  | 'suggest_reply'
  | 'write_professional_message';

export interface QuickActionDefinition {
  id: QuickActionType;
  label: string;
  icon: string;
  promptTemplate: string;
  requiredContext: string[];
  availableOn: PageType[];
  useWebSocket: boolean; // true for chat, false for direct API
}

// ============================================================================
// Quota Types
// ============================================================================

export type UserTier = 'free' | 'premium';

export interface QuotaStatus {
  tier: UserTier;
  remaining: number | null; // null for unlimited (premium)
  resetAt: string | null;
  allowed: boolean;
}

// ============================================================================
// Error Types
// ============================================================================

export enum ChatErrorType {
  CONNECTION_FAILED = 'connection_failed',
  WEBSOCKET_CLOSED = 'websocket_closed',
  MESSAGE_SEND_FAILED = 'message_send_failed',
  STREAMING_INTERRUPTED = 'streaming_interrupted',
  QUOTA_EXCEEDED = 'quota_exceeded',
  AUTHENTICATION_FAILED = 'authentication_failed',
  TIMEOUT = 'timeout',
  RATE_LIMIT = 'rate_limit',
  SERVER_ERROR = 'server_error',
}

export type ErrorAction = 'retry' | 'upgrade' | 'login' | 'wait';

export interface ChatError {
  type: ChatErrorType;
  message: string;
  retryable: boolean;
  action?: ErrorAction;
}

// ============================================================================
// Session Storage Types
// ============================================================================

export interface ChatSession {
  conversationId: string;
  messages: Message[];
  lastUpdated: string;
  expiresAt: string; // 1 hour from creation
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
  initialContext?: PageContext;
}

export interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
  onCopy?: () => void;
}

export interface TypingIndicatorProps {
  visible: boolean;
}

export interface QuickActionButtonProps {
  label: string;
  icon: React.ReactNode;
  action: QuickActionType;
  context: PageContext;
  disabled?: boolean;
  onClick?: () => void;
}

export interface QuotaDisplayProps {
  quota: QuotaStatus;
  onUpgradeClick: () => void;
}

export interface CopyButtonProps {
  content: string;
  onCopy?: () => void;
}

export interface ChatHeaderProps {
  onClose: () => void;
  onMinimize?: () => void;
  quota: QuotaStatus | null;
  context?: PageContext;
}

export interface MessageInputProps {
  onSend: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export interface UpgradePromptProps {
  isOpen: boolean;
  onClose: () => void;
  onUpgrade: () => void;
}

// ============================================================================
// Chat Store Types
// ============================================================================

export interface ChatStore {
  // State
  isOpen: boolean;
  messages: Message[];
  streamingContent: string;
  isStreaming: boolean;
  connectionStatus: ConnectionStatus;
  quota: QuotaStatus | null;
  error: ChatError | null;
  retryCount: number;
  lastFailedMessage: string | null;
  autoFillCallbacks: Record<string, (...args: any[]) => void>;
  
  // Actions
  openChat: () => void;
  closeChat: () => void;
  sendMessage: (content: string) => void;
  appendStreamingChunk: (chunk: string) => void;
  finalizeStreamingMessage: () => void;
  clearConversation: () => void;
  updateQuota: (quota: QuotaStatus) => void;
  setError: (error: ChatError | null) => void;
  setConnectionStatus: (status: ConnectionStatus) => void;
  retryLastMessage: () => void;
  incrementRetryCount: () => void;
  resetRetryCount: () => void;
  
  // Auto-fill callbacks
  setAutoFillCallback: (key: string, callback: (...args: any[]) => void) => void;
  getAutoFillCallback: (key: string) => ((...args: any[]) => void) | undefined;
  clearAutoFillCallbacks: () => void;
  
  // Persistence
  loadFromSession: () => void;
  saveToSession: () => void;
}

// ============================================================================
// WebSocket Client Types
// ============================================================================

export interface WebSocketClientConfig {
  url: string;
  token: string;
  maxReconnectAttempts?: number;
  reconnectDelays?: number[]; // [1000, 2000, 4000, 8000, 16000]
}

export interface WebSocketCallbacks {
  onMessage?: (chunk: StreamingChunk) => void;
  onError?: (error: Error) => void;
  onClose?: () => void;
  onOpen?: () => void;
}
