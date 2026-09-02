# Design Document: AI Chat Interface

## Overview

The AI Chat Interface is a Gemini-style conversational AI component that provides contextually-aware assistance throughout the BeatPush platform. The system consists of four main layers:

1. **UI Layer**: Glassmorphism-styled chat interface with responsive design (400px sidebar on desktop, full-screen on mobile)
2. **Communication Layer**: WebSocket-based streaming with fallback HTTP endpoints
3. **State Management Layer**: React Context/Zustand for chat state with sessionStorage persistence
4. **Integration Layer**: Context providers that inject page-specific data into AI prompts

The design prioritizes real-time user experience, seamless integration with existing infrastructure, and transparent quota management. The interface will be accessible from every page in the platform and maintain conversation context across navigation.

## Architecture

### System Architecture Diagram

```mermaid
graph TD
    A[User Interface] --> B[ChatInterface Component]
    B --> C[WebSocket Client]
    B --> D[Chat State Manager]
    B --> E[Context Provider]
    
    C --> F[/api/v1/ai/ws]
    F --> G[WebSocket Manager]
    G --> H[AI Service]
    
    D --> I[sessionStorage]
    E --> J[Page Context]
    
    H --> K[Hugging Face API]
    H --> L[Response Cache]
    
    B --> M[useAI Hook]
    M --> N[AI Service Client]
    N --> O[/api/v1/ai/generate]
    
    style B fill:#8B5CF6
    style F fill:#3B82F6
    style H fill:#8B5CF6
```

### Component Hierarchy

```
App
├── Layout
│   ├── MainNav
│   └── ChatTriggerButton
└── ChatInterface (Global Portal)
    ├── ChatHeader
    │   ├── QuotaDisplay
    │   ├── ContextBadge
    │   └── CloseButton
    ├── MessageList (ScrollArea)
    │   ├── MessageBubble (User)
    │   ├── MessageBubble (AI)
    │   │   ├── MarkdownRenderer
    │   │   └── CopyButton
    │   └── TypingIndicator
    ├── QuickActionBar
    │   └── QuickActionButton[]
    └── MessageInput
        ├── TextArea
        └── SendButton
```

### Data Flow

1. **User sends message** → MessageInput → ChatState → WebSocket
2. **WebSocket receives chunks** → StreamingBuffer → MessageList → MarkdownRenderer
3. **Context injection** → ContextProvider → WebSocket payload → AI Service
4. **Quota updates** → useAI hook → QuotaDisplay
5. **Session persistence** → ChatState → sessionStorage

## Components and Interfaces

### Core Components

#### 1. ChatInterface Component

**Purpose**: Root component managing chat UI and orchestrating sub-components

**Props**:
```typescript
interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
  initialContext?: PageContext;
}
```

**State**:
```typescript
interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  connectionStatus: 'connected' | 'connecting' | 'disconnected';
  error: string | null;
}
```

**Responsibilities**:
- Manage WebSocket connection lifecycle
- Coordinate message sending/receiving
- Handle responsive layout (sidebar vs full-screen)
- Persist conversation to sessionStorage
- Apply glassmorphism styling

#### 2. MessageBubble Component

**Purpose**: Display individual chat messages with formatting

**Props**:
```typescript
interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
  onCopy?: () => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    quotaUsed?: number;
    responseTime?: number;
  };
}
```

**Features**:
- Markdown rendering with syntax highlighting
- Copy-to-clipboard button (AI messages only)
- Smooth fade-in animation
- Distinct styling for user vs AI messages

#### 3. TypingIndicator Component

**Purpose**: Show animated dots while AI is processing

**Props**:
```typescript
interface TypingIndicatorProps {
  visible: boolean;
}
```

**Animation**: Pulse animation (1.5s infinite) with 3 dots

#### 4. QuickActionButton Component

**Purpose**: Pre-configured buttons for common AI tasks

**Props**:
```typescript
interface QuickActionButtonProps {
  label: string;
  icon: ReactNode;
  action: QuickAction;
  context: PageContext;
  disabled?: boolean;
}

type QuickAction =
  | 'generate_title'
  | 'write_description'
  | 'create_tags'
  | 'generate_captions'
  | 'analyze_performance'
  | 'suggest_optimizations'
  | 'explain_trends'
  | 'write_bio';
```

**Behavior**:
- Auto-populate prompt with context
- Show loading state during execution
- Offer "Use This" button on AI response

#### 5. QuotaDisplay Component

**Purpose**: Show remaining AI requests for free users

**Props**:
```typescript
interface QuotaDisplayProps {
  quota: QuotaStatus;
  onUpgradeClick: () => void;
}

interface QuotaStatus {
  tier: 'free' | 'premium';
  remaining: number | null;
  resetAt: string | null;
  allowed: boolean;
}
```

**Display Logic**:
- Free tier: "X/20" with warning colors
- Premium: "Unlimited ⚡"
- Tooltip shows reset time on hover

#### 6. ContextProvider Component

**Purpose**: Inject page-specific context into AI prompts

**Interface**:
```typescript
interface PageContext {
  pageType: PageType;
  pageUrl: string;
  contextData: Record<string, any>;
}

type PageType =
  | 'beat_upload'
  | 'beat_edit'
  | 'campaign_dashboard'
  | 'analytics'
  | 'profile_edit'
  | 'social_feed'
  | 'messaging';
```

**Context Extraction Examples**:
- **Beat Upload**: `{ genre, bpm, mood, fileName, fileSize, duration }`
- **Campaign Dashboard**: `{ campaignId, metrics, budget, targetAudience }`
- **Analytics**: `{ timeRange, revenue, plays, engagement, trends }`
- **Profile Edit**: `{ existingBio, genres, location, socialLinks }`

### WebSocket Client

**Connection Management**:
```typescript
class ChatWebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private messageQueue: string[] = [];
  
  connect(token: string): Promise<void>;
  disconnect(): void;
  send(message: ChatMessage): void;
  onMessage(callback: (chunk: string) => void): void;
  onError(callback: (error: Error) => void): void;
  onClose(callback: () => void): void;
  
  private reconnect(): void;
  private flushQueue(): void;
}
```

**WebSocket Message Protocol**:
```typescript
// Client → Server
interface ChatMessagePayload {
  type: 'chat_message';
  content: string;
  context: PageContext;
  conversationId?: string;
}

// Server → Client
interface StreamingChunk {
  type: 'chunk' | 'done' | 'error';
  content?: string;
  error?: string;
  metadata?: {
    quotaRemaining: number;
    responseTimeMs: number;
  };
}
```

**Reconnection Strategy**:
- Exponential backoff: 1s, 2s, 4s, 8s, 16s (max 5 attempts)
- Preserve message queue during reconnection
- Display connection status to user
- Auto-retry failed messages after reconnection

### State Management

**Chat State Structure**:
```typescript
interface ChatStore {
  // State
  isOpen: boolean;
  messages: Message[];
  streamingContent: string;
  isStreaming: boolean;
  connectionStatus: ConnectionStatus;
  quota: QuotaStatus | null;
  
  // Actions
  openChat: () => void;
  closeChat: () => void;
  sendMessage: (content: string) => void;
  appendStreamingChunk: (chunk: string) => void;
  finalizeStreamingMessage: () => void;
  clearConversation: () => void;
  updateQuota: (quota: QuotaStatus) => void;
  
  // Persistence
  loadFromSession: () => void;
  saveToSession: () => void;
}
```

**SessionStorage Schema**:
```typescript
interface ChatSession {
  conversationId: string;
  messages: Message[];
  lastUpdated: string;
  expiresAt: string; // 1 hour from creation
}
```

**Storage Limits**:
- Maximum 50 messages per session
- Maximum 5MB total storage
- Auto-cleanup expired sessions on load

### Integration with useAI Hook

**Hook Usage Pattern**:
```typescript
const ChatInterfaceWithAI = () => {
  const {
    quota,
    loading,
    error,
    loadQuota,
    isQuotaExceeded,
    isPremium,
  } = useAI({ autoLoadQuota: true });
  
  const handleQuickAction = async (action: QuickAction, params: any) => {
    // Quick actions use existing useAI methods
    // WebSocket chat uses direct WebSocket connection
  };
  
  return (
    <ChatInterface
      quota={quota}
      onQuotaRefresh={loadQuota}
      showUpgradePrompt={isQuotaExceeded}
    />
  );
};
```

**Integration Points**:
- Quota status: Read from `useAI.quota`
- Quick actions: Use `useAI.generate()` methods
- Streaming chat: Direct WebSocket (bypasses useAI for real-time)
- Error handling: Use `useAI.error` for quick actions

## Data Models

### Message Model

```typescript
interface Message {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata: MessageMetadata;
}

interface MessageMetadata {
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
```

### Conversation Model

```typescript
interface Conversation {
  id: string;
  userId: string;
  messages: Message[];
  createdAt: Date;
  lastUpdated: Date;
  expiresAt: Date;
  metadata: ConversationMetadata;
}

interface ConversationMetadata {
  totalMessages: number;
  quotaUsed: number;
  avgResponseTime: number;
  pageTypes: PageType[];
}
```

### Quick Action Model

```typescript
interface QuickActionDefinition {
  id: string;
  label: string;
  icon: string;
  promptTemplate: string;
  requiredContext: string[];
  availableOn: PageType[];
  useWebSocket: boolean; // true for chat, false for direct API
}

// Example quick actions
const QUICK_ACTIONS: QuickActionDefinition[] = [
  {
    id: 'generate_title',
    label: 'Generate Title',
    icon: 'Sparkles',
    promptTemplate: 'Generate 5 creative beat titles for a {genre} beat with {mood} mood at {bpm} BPM',
    requiredContext: ['genre'],
    availableOn: ['beat_upload', 'beat_edit'],
    useWebSocket: false, // Use existing AI service
  },
  {
    id: 'analyze_performance',
    label: 'Analyze Performance',
    icon: 'TrendingUp',
    promptTemplate: 'Analyze this campaign performance and provide insights: {metrics}',
    requiredContext: ['metrics'],
    availableOn: ['campaign_dashboard'],
    useWebSocket: true, // Use streaming WebSocket
  },
  // ... more actions
];
```

### Context Model

```typescript
interface PageContextDefinition {
  pageType: PageType;
  extractContext: (props: any) => Record<string, any>;
  quickActions: string[]; // Quick action IDs
  contextDisplay: string; // e.g., "Helping with: Beat Upload"
}

// Example context extractors
const CONTEXT_EXTRACTORS: Record<PageType, PageContextDefinition> = {
  beat_upload: {
    pageType: 'beat_upload',
    extractContext: (props) => ({
      genre: props.selectedGenre,
      bpm: props.bpmInput,
      mood: props.moodInput,
      fileName: props.uploadedFile?.name,
      fileSize: props.uploadedFile?.size,
      duration: props.audioDuration,
    }),
    quickActions: ['generate_title', 'write_description', 'create_tags', 'recommend_price'],
    contextDisplay: 'Helping with: Beat Upload',
  },
  campaign_dashboard: {
    pageType: 'campaign_dashboard',
    extractContext: (props) => ({
      campaignId: props.campaign.id,
      campaignName: props.campaign.name,
      metrics: {
        reach: props.metrics.reach,
        engagement: props.metrics.engagement,
        conversions: props.metrics.conversions,
        spent: props.metrics.spent,
      },
      budget: props.campaign.budget,
      targetAudience: props.campaign.targetAudience,
      duration: props.campaign.duration,
    }),
    quickActions: ['analyze_performance', 'suggest_optimizations', 'generate_ad_copy'],
    contextDisplay: 'Helping with: Campaign Analysis',
  },
  // ... more extractors
};
```

## Error Handling

### Error Types

```typescript
enum ChatErrorType {
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

interface ChatError {
  type: ChatErrorType;
  message: string;
  retryable: boolean;
  action?: 'retry' | 'upgrade' | 'login' | 'wait';
}
```

### Error Handling Strategy

**Connection Errors**:
- Display "Connection lost" banner with auto-reconnect countdown
- Queue messages during reconnection
- Show success message when reconnected
- Limit reconnection attempts to 5

**Quota Errors**:
- Show upgrade modal immediately
- Display remaining quota prominently
- Disable send button when quota = 0
- Show countdown to quota reset

**Streaming Errors**:
- Retry up to 2 times automatically
- Show "Retry" button after 2 failures
- Display partial response if available
- Log errors for monitoring

**Authentication Errors**:
- Redirect to login page
- Preserve conversation in sessionStorage
- Restore conversation after re-authentication

**Timeout Errors** (30s):
- Display "AI is taking longer than usual" message
- Offer cancel button
- Show retry button after timeout

### User-Friendly Error Messages

```typescript
const ERROR_MESSAGES: Record<ChatErrorType, string> = {
  [ChatErrorType.CONNECTION_FAILED]: 
    "Connection lost. Retrying in {seconds}s...",
  [ChatErrorType.QUOTA_EXCEEDED]: 
    "You've used all 20 free AI requests today. Upgrade to Premium for unlimited access!",
  [ChatErrorType.TIMEOUT]: 
    "AI is taking longer than usual. Please try again or rephrase your question.",
  [ChatErrorType.RATE_LIMIT]: 
    "Too many requests. Please wait {seconds} seconds.",
  [ChatErrorType.SERVER_ERROR]: 
    "Our AI service is temporarily unavailable. We're working on it!",
  [ChatErrorType.AUTHENTICATION_FAILED]: 
    "Session expired. Please log in again.",
};
```

## Testing Strategy

### Unit Tests

**Component Tests** (React Testing Library):
- ChatInterface renders correctly (open/closed states)
- MessageBubble displays markdown formatting
- QuickActionButton triggers correct prompts
- QuotaDisplay shows correct tier information
- TypingIndicator animation works
- CopyButton copies content to clipboard
- ContextProvider extracts correct context

**Hook Tests**:
- useChatWebSocket handles connection lifecycle
- useChatWebSocket reconnects with exponential backoff
- useChatWebSocket queues messages during reconnection
- useChatState persists to sessionStorage
- useChatState limits messages to 50
- useAI integration works correctly

**State Management Tests**:
- ChatStore sends messages correctly
- ChatStore appends streaming chunks
- ChatStore finalizes streaming messages
- ChatStore clears conversation
- ChatStore loads from sessionStorage
- ChatStore saves to sessionStorage
- SessionStorage cleanup works

### Integration Tests

**WebSocket Integration**:
- WebSocket connects successfully
- WebSocket authenticates with JWT
- WebSocket sends and receives messages
- WebSocket handles reconnection
- WebSocket gracefully disconnects

**Context Integration**:
- Beat upload context extraction works
- Campaign context extraction works
- Analytics context extraction works
- Profile context extraction works
- Quick actions use correct context

**useAI Hook Integration**:
- Quota updates after AI requests
- Quick actions use useAI methods
- Error handling works correctly
- Loading states work correctly

### End-to-End Tests

**User Flows**:
1. Open chat interface from any page
2. Send a message and receive streaming response
3. Copy AI response to clipboard
4. Use quick action button
5. Navigate between pages (conversation persists)
6. Close and reopen chat (conversation restores)
7. Exceed quota (upgrade modal appears)
8. Clear conversation
9. Handle connection loss and recovery

**Responsive Tests**:
- Desktop sidebar layout (400px width)
- Tablet layout (full-screen)
- Mobile layout (full-screen with swipe-down)
- Keyboard opening on mobile (input stays visible)
- Touch target sizes (minimum 44x44px)

### Accessibility Tests

**WCAG 2.1 AA Compliance**:
- Keyboard navigation (Tab, Enter, Escape)
- Focus trapping when open
- ARIA labels on all interactive elements
- Screen reader announcements for new messages
- High contrast mode support
- Color contrast ratios (4.5:1 minimum)

**Test Cases**:
- Navigate chat using keyboard only
- Verify screen reader announcements
- Test with high contrast mode
- Verify focus indicators visible
- Test with 200% zoom

## Performance Optimizations

### Rendering Optimizations

**Virtual Scrolling**:
- Use `react-window` for message list (handle 1000+ messages)
- Render only visible messages plus buffer
- Lazy load old messages on scroll up

**Memoization**:
```typescript
const MessageBubble = React.memo(MessageBubbleComponent);
const QuickActionButton = React.memo(QuickActionButtonComponent);
```

**Debouncing**:
- Debounce typing indicator (500ms)
- Throttle scroll events (100ms)
- Debounce sessionStorage saves (1000ms)

### Network Optimizations

**WebSocket Connection Pooling**:
- Reuse single WebSocket connection across app
- Share connection between multiple components
- Gracefully handle connection sharing

**Message Compression**:
- Compress large context payloads (gzip)
- Limit context data size (max 10KB)
- Send diffs for updated context

**Caching**:
- Cache quick action responses (5 minutes)
- Cache quota status (30 seconds)
- Use stale-while-revalidate pattern

### Bundle Size Optimizations

**Code Splitting**:
```typescript
const ChatInterface = lazy(() => import('./components/ChatInterface'));
const MarkdownRenderer = lazy(() => import('./components/MarkdownRenderer'));
```

**Tree Shaking**:
- Import only required Shadcn components
- Use modular imports for markdown renderer
- Remove unused dependencies

**Target Bundle Sizes**:
- ChatInterface bundle: <80KB (gzipped)
- MarkdownRenderer bundle: <30KB (gzipped)
- Total added bundle size: <150KB (gzipped)

## Security Considerations

### Input Sanitization

**User Input**:
- Sanitize message content before sending
- Strip HTML tags (allow markdown only)
- Limit message length (max 4000 characters)
- Prevent prompt injection attacks

**AI Response**:
- Sanitize AI responses before rendering
- Use DOMPurify for markdown HTML output
- Escape code blocks properly
- Filter profanity and offensive content

### Authentication

**JWT Token Handling**:
- Retrieve token from HTTP-only cookie or localStorage
- Include token in WebSocket connection header
- Refresh token before expiration
- Handle token expiration gracefully

### Data Privacy

**Context Data**:
- Exclude sensitive data from context (passwords, tokens, payment info)
- Sanitize context before sending to backend
- Log context data for debugging (exclude PII)
- Comply with GDPR for conversation storage

**SessionStorage**:
- Encrypt sensitive conversation data
- Clear sessionStorage on logout
- Set 1-hour expiration for sessions
- Don't store credit card info

### Rate Limiting

**Client-Side Rate Limiting**:
- Max 1 message per 2 seconds
- Max 5 quick action clicks per minute
- Display cooldown timer to user

**Backend Rate Limiting** (already implemented):
- 20 AI requests per day (free tier)
- Unlimited requests (premium tier)
- Return 429 status on limit exceeded

## Deployment Considerations

### Environment Variables

```env
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.beatpush.com
NEXT_PUBLIC_WS_URL=wss://api.beatpush.com
NEXT_PUBLIC_AI_TIMEOUT_MS=30000
NEXT_PUBLIC_MAX_MESSAGE_LENGTH=4000
```

### Feature Flags

```typescript
interface ChatFeatureFlags {
  enableWebSocketStreaming: boolean;
  enableQuickActions: boolean;
  enableContextInjection: boolean;
  enableMarkdownFormatting: boolean;
  enableVirtualScrolling: boolean;
  maxMessagesPerSession: number;
}

const PRODUCTION_FLAGS: ChatFeatureFlags = {
  enableWebSocketStreaming: true,
  enableQuickActions: true,
  enableContextInjection: true,
  enableMarkdownFormatting: true,
  enableVirtualScrolling: true,
  maxMessagesPerSession: 50,
};
```

### Monitoring

**Metrics to Track**:
- WebSocket connection success rate
- Average message response time
- Streaming chunk latency
- Quota usage per user
- Error rates by type
- User engagement (messages per session)
- Quick action usage by type
- Conversion rate (free → premium)

**Logging**:
```typescript
interface ChatEventLog {
  eventType: 'message_sent' | 'response_received' | 'error' | 'quota_exceeded';
  userId: string;
  timestamp: Date;
  metadata: Record<string, any>;
}
```

### Rollout Strategy

**Phase 1: Beta (10% users)**
- Enable for premium users only
- Monitor performance metrics
- Gather user feedback
- Fix critical bugs

**Phase 2: Gradual Rollout (50% users)**
- Enable for all users
- Monitor quota usage patterns
- Optimize streaming performance
- Add more quick actions

**Phase 3: Full Release (100% users)**
- Enable all features
- Launch marketing campaign
- Monitor conversion rates
- Continuous improvements

## Design System Integration

### Glassmorphism Styling

**CSS Variables**:
```css
:root {
  --chat-bg-blur: 12px;
  --chat-bg-opacity: 0.8;
  --chat-border-radius: 16px;
  --chat-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  --chat-gradient-start: #8B5CF6;
  --chat-gradient-end: #3B82F6;
}
```

**Glassmorphism Component**:
```typescript
const glassStyle = {
  background: 'rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(12px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
};
```

### Animation Specifications

**Slide-in Animation**:
```css
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.chat-interface {
  animation: slideInRight 300ms ease-in-out;
}
```

**Typing Indicator Animation**:
```css
@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}

.typing-dot {
  animation: pulse 1.5s infinite;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}
```

### Typography

**Font Specifications**:
- Font family: Inter (system fallback: -apple-system, BlinkMacSystemFont, "Segoe UI")
- Base size: 16px
- Line height: 1.5
- User messages: font-weight 500
- AI messages: font-weight 400
- Headers: font-weight 600

### Color Palette

**Primary Colors**:
- Purple: `#8B5CF6`
- Blue: `#3B82F6`
- Gradient: `linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)`

**Semantic Colors**:
- Success: `#10B981` (green)
- Warning: `#F59E0B` (amber)
- Error: `#EF4444` (red)
- Info: `#3B82F6` (blue)

**Text Colors**:
- Primary text: `#1F2937` (dark gray)
- Secondary text: `#6B7280` (medium gray)
- Placeholder: `#9CA3AF` (light gray)
- Inverted: `#FFFFFF` (white)

## Mobile Optimizations

### Touch Interactions

**Swipe Gestures**:
```typescript
const handleSwipeDown = (event: TouchEvent) => {
  const touch = event.touches[0];
  const deltaY = touch.clientY - startY;
  
  if (deltaY > 100) {
    closeChat();
  }
};
```

**Haptic Feedback**:
```typescript
const triggerHaptic = (type: 'light' | 'medium' | 'heavy') => {
  if (navigator.vibrate) {
    const duration = type === 'light' ? 10 : type === 'medium' ? 20 : 30;
    navigator.vibrate(duration);
  }
};
```

### Keyboard Handling

**Virtual Keyboard**:
```typescript
const handleKeyboardOpen = () => {
  // Adjust chat interface to keep input visible
  const keyboardHeight = window.visualViewport?.height ?? 0;
  chatContainerRef.current.style.paddingBottom = `${keyboardHeight}px`;
};

window.visualViewport?.addEventListener('resize', handleKeyboardOpen);
```

### Performance Targets (Mobile)

- First render: <800ms
- Message send to response start: <1000ms
- Smooth 60fps scrolling
- Touch response time: <100ms
- Memory usage: <30MB

## Internationalization (Future)

### Translation Keys

```typescript
const translations = {
  en: {
    'chat.title': 'AI Assistant',
    'chat.placeholder': 'Ask me anything...',
    'chat.quota.free': '{remaining}/20',
    'chat.quota.premium': 'Unlimited ⚡',
    'chat.error.connection': 'Connection lost. Retrying...',
    'chat.error.quota': 'Daily limit reached. Upgrade for unlimited!',
    'chat.action.generate_title': 'Generate Title',
    'chat.action.write_description': 'Write Description',
  },
  // Add more languages
};
```

## Notes

- **Existing Infrastructure**: This design leverages the existing WebSocket infrastructure (`websocket_manager.py`) and AI service (`ai_service.py`). The chat interface will connect to the same WebSocket endpoint used for messaging but with different message types.

- **useAI Hook Integration**: Quick actions will use the existing `useAI` hook for non-streaming requests, while the conversational chat will use WebSocket for streaming responses. This provides the best of both worlds: simple API calls for quick actions and real-time streaming for conversations.

- **Context Injection**: The context provider system allows the AI to understand what page the user is on and what content they're viewing, enabling truly contextual assistance without requiring users to explain their situation every time.

- **Quota Management**: Transparent quota display and upgrade prompts are critical for conversion. The design prioritizes showing quota information prominently and making the upgrade path clear when limits are reached.

- **Mobile-First Design**: The responsive design ensures the chat interface works seamlessly on mobile devices where most users will access the platform. The full-screen mobile layout provides enough space for comfortable conversation.

- **Performance**: Virtual scrolling, code splitting, and efficient state management ensure the chat interface remains performant even with long conversation histories.

- **Accessibility**: Full keyboard navigation, screen reader support, and WCAG 2.1 AA compliance ensure the chat interface is accessible to all users.

- **Scalability**: The component architecture, state management, and WebSocket connection pooling are designed to scale as the platform grows. The system can handle thousands of concurrent chat sessions efficiently.
