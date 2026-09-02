# AI Chat Interface

A Gemini-style conversational AI component that provides contextually-aware assistance throughout the BeatPush platform.

## Directory Structure

```
chat/
├── components/          # UI components (to be implemented)
│   ├── ChatInterface.tsx
│   ├── MessageBubble.tsx
│   ├── TypingIndicator.tsx
│   ├── QuickActionButton.tsx
│   ├── QuotaDisplay.tsx
│   ├── CopyButton.tsx
│   ├── ChatHeader.tsx
│   ├── MessageInput.tsx
│   └── UpgradePrompt.tsx
├── hooks/              # Custom React hooks (to be implemented)
│   ├── useChatWebSocket.ts
│   ├── useChatStore.ts
│   └── usePageContext.ts
├── utils/              # Utility functions (to be implemented)
│   ├── ChatWebSocketClient.ts
│   ├── messageUtils.ts
│   ├── contextUtils.ts
│   └── sessionUtils.ts
├── store/              # Zustand store (to be implemented)
│   └── chatStore.ts
├── types/              # TypeScript type definitions
│   └── index.ts        ✓ Completed
├── constants/          # Configuration and constants
│   └── index.ts        ✓ Completed
├── index.ts            # Main export file ✓ Completed
└── README.md           # This file
```

## Core TypeScript Interfaces

### Message and Conversation Types
- `Message` - Individual chat message with role, content, timestamp, and metadata
- `MessageRole` - 'user' | 'assistant' | 'system'
- `MessageMetadata` - Performance metrics, AI provider info, context info, user feedback
- `Conversation` - Complete conversation with messages and metadata
- `ConversationMetadata` - Aggregate conversation statistics

### Chat State Types
- `ChatState` - Current state of the chat interface
- `ConnectionStatus` - 'connected' | 'connecting' | 'disconnected'

### WebSocket Message Protocol Types
- `ChatMessagePayload` - Client → Server message format
- `StreamingChunk` - Server → Client streaming response format
- `StreamingChunkType` - 'chunk' | 'done' | 'error'

### Page Context Types
- `PageContext` - Current page information for context-aware AI responses
- `PageType` - Supported page types (beat_upload, campaign_dashboard, analytics, etc.)
- `PageContextDefinition` - Configuration for context extraction per page type

### Quick Action Types
- `QuickActionType` - Available quick action IDs
- `QuickActionDefinition` - Configuration for quick action buttons

### Quota Types
- `QuotaStatus` - User's AI quota information
- `UserTier` - 'free' | 'premium'

### Error Types
- `ChatError` - Structured error information
- `ChatErrorType` - Enum of possible error types
- `ErrorAction` - Recommended actions for errors

### Component Props Types
- All component prop interfaces defined for type safety

## Configuration Constants

### WebSocket Configuration
- Reconnection delays and retry limits
- Timeout and heartbeat settings

### Chat Configuration
- Message limits and storage settings
- Animation timing and debounce values

### UI Configuration
- Responsive breakpoints
- Animation durations
- Component dimensions

### Quick Actions
- Pre-configured quick action definitions
- Mapped to specific page types
- Includes prompt templates

### Page Context Extractors
- Functions to extract context from each page type
- Maps context data to AI prompts

### Error Messages
- User-friendly error messages for all error types

### Color Palette
- Platform colors (purple, blue gradient)
- Semantic colors (success, warning, error)
- Text and background colors

### Storage Keys
- SessionStorage key names

### API Endpoints
- WebSocket and REST endpoints

## Usage

Once implemented, the chat interface can be used as follows:

```typescript
import { ChatInterface } from '@/components/chat';
import type { PageContext } from '@/components/chat';

function MyPage() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  
  const pageContext: PageContext = {
    pageType: 'beat_upload',
    pageUrl: '/beats/upload',
    contextData: {
      genre: 'Hip Hop',
      bpm: 140,
      mood: 'energetic',
    },
  };
  
  return (
    <>
      <button onClick={() => setIsChatOpen(true)}>
        Open AI Chat
      </button>
      
      <ChatInterface
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        initialContext={pageContext}
      />
    </>
  );
}
```

## Implementation Status

### ✓ Completed
- [x] TypeScript type definitions (`types/index.ts`)
- [x] Configuration constants (`constants/index.ts`)
- [x] Main export file (`index.ts`)
- [x] Directory structure setup

### 🚧 In Progress
- None yet

### 📋 To Do
- [ ] WebSocket client implementation
- [ ] Chat state management with Zustand
- [ ] UI components
- [ ] Hooks for WebSocket and state
- [ ] Utility functions
- [ ] Integration with existing useAI hook
- [ ] Testing

## Design References

- **Design Document**: `.kiro/specs/ai-chat-interface/design.md`
- **Requirements**: `.kiro/specs/ai-chat-interface/requirements.md`
- **Tasks**: `.kiro/specs/ai-chat-interface/tasks.md`

## Next Steps

The next task (Task 2) will implement the WebSocket client with reconnection logic, which will use the types and constants defined here.
