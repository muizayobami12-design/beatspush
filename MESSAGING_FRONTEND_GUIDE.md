# BeatPush Messaging Frontend - Integration Guide

## Overview

The messaging frontend is **fully implemented** and ready for production use. All components are React/TypeScript-based with proper state management, error handling, and real-time WebSocket integration.

---

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   └── messages/
│   │   │       └── page.tsx                 # Main messaging page
│   │   │       ├── requests/
│   │   │       │   └── page.tsx             # Message requests page
│   │   │       └── settings/
│   │   │           └── page.tsx             # Privacy settings
│   ├── components/
│   │   └── features/
│   │       └── messaging/
│   │           ├── ConversationList.tsx     # List of conversations
│   │           ├── ConversationListItem.tsx # Single conversation
│   │           ├── MessageThread.tsx        # Message display
│   │           ├── MessageBubble.tsx        # Single message
│   │           ├── MessageInput.tsx         # Message composer
│   │           ├── TypingIndicator.tsx      # Typing status
│   │           ├── AttachmentPreview.tsx    # File display
│   │           ├── FileAttachment.tsx       # File upload
│   │           ├── VoiceNoteRecorder.tsx    # Voice recording
│   │           ├── NewConversationModal.tsx # Start new chat
│   │           ├── MessageRequestsModal.tsx # Manage requests
│   │           ├── BlockUserModal.tsx       # Block dialog
│   │           ├── ReportMessageModal.tsx   # Report dialog
│   │           ├── MessagingSettings.tsx    # Privacy settings
│   │           ├── BlockedUsers.tsx         # Blocked list
│   │           ├── ConversationSearch.tsx   # Search convos
│   │           ├── MessageSearch.tsx        # Search messages
│   │           ├── ConversationFilters.tsx  # Filter tabs
│   │           ├── LoadingStates.tsx        # Skeletons
│   │           └── MessageErrorBoundary.tsx # Error boundary
│   ├── services/
│   │   └── messagingService.ts              # API integration
│   ├── hooks/
│   │   ├── useWebSocket.ts                  # WebSocket management
│   │   ├── useMessages.ts                   # Message state
│   │   └── useConversations.ts              # Conversation state
│   └── styles/
│       └── messaging.css                    # Component styles
```

---

## Main Components

### 1. MessagesPage (`app/(dashboard)/messages/page.tsx`)

**Location:** Main messaging interface

**Features:**
- Split view (conversation list + message thread)
- Mobile responsive (toggles between list/thread)
- Conversation filtering (All, Unread, Requests, Archived)
- Search by participant name
- WebSocket status indicator
- Unread count badge

**State:**
```typescript
- conversations: Conversation[] - List of conversations
- selectedConversation: Conversation | null - Active thread
- searchQuery: string - Search filter
- activeFilter: 'all' | 'unread' | 'requests' | 'archived'
- mobileView: 'list' | 'thread' - Mobile UI mode
```

**Key Methods:**
- `loadConversations()` - Fetch and filter conversations
- `handleSelectConversation()` - Open conversation thread
- `handleNewMessage()` - WebSocket event handler

---

### 2. ConversationList (`components/features/messaging/ConversationList.tsx`)

**Purpose:** Display list of conversations with infinite scroll

**Props:**
```typescript
interface ConversationListProps {
  conversations: Conversation[]
  selectedConversation: Conversation | null
  onSelectConversation: (conv: Conversation) => void
  currentUserId: string
  isConnected: boolean
}
```

**Features:**
- Infinite scroll pagination
- Highlight selected conversation
- Show unread count badge
- Show "Message Request" indicator
- Show online status for participants
- Last message preview truncated

---

### 3. MessageThread (`components/features/messaging/MessageThread.tsx`)

**Purpose:** Display messages in a conversation

**Props:**
```typescript
interface MessageThreadProps {
  conversation: Conversation
  onConversationUpdate?: () => void
  onBack?: () => void
}
```

**Features:**
- Cursor-based pagination (load older messages)
- Auto-scroll to newest message
- Typing indicator display
- Load messages on scroll to top
- Message grouping by sender
- Delete/Edit/Report actions

**State Management:**
- Uses `useMessages()` hook for message list
- Uses `useWebSocket()` for real-time updates
- Optimistic updates for message sending

---

### 4. MessageBubble (`components/features/messaging/MessageBubble.tsx`)

**Purpose:** Render single message with styling and actions

**Props:**
```typescript
interface MessageBubbleProps {
  message: Message
  isOwn: boolean - Is sender the current user?
  onDelete?: (messageId: string) => void
  onEdit?: (message: Message) => void
  onReport?: (messageId: string) => void
}
```

**Features:**
- Different styling for sent/received
- Timestamp display (on hover)
- "Edited" indicator
- Read receipt checkmarks (single/double)
- Attachment previews
- Context menu (edit/delete/copy/report)
- 15-minute edit window enforcement

**Read Receipts:**
- ✓ Single check = Delivered (exists in DB)
- ✓✓ Double check = Read (marked as read)

---

### 5. MessageInput (`components/features/messaging/MessageInput.tsx`)

**Purpose:** Compose and send messages

**Props:**
```typescript
interface MessageInputProps {
  onSend: (content: string) => void
  onTyping?: (isTyping: boolean) => void
  onFileAttach?: (file: File) => void
  disabled?: boolean
  placeholder?: string
  initialValue?: string - For edit mode
}
```

**Features:**
- Auto-resizing textarea
- Character counter (0/2000)
- File attachment button
- Voice note recorder button
- Typing indicator (3-second debounce)
- Send on Enter (Shift+Enter for newline)
- Emoji picker button
- Optimistic send feedback

---

### 6. AttachmentPreview (`components/features/messaging/AttachmentPreview.tsx`)

**Purpose:** Display file attachments in messages

**Props:**
```typescript
interface AttachmentPreviewProps {
  attachment: MessageAttachment
  onDownload?: () => void
}
```

**Features:**
- Images: Thumbnail + lightbox
- Audio: Inline player with progress bar
- Documents: Icon + download button
- Voice Notes: Waveform + player
- File size display
- MIME type detection
- Error handling for failed loads

---

### 7. VoiceNoteRecorder (`components/features/messaging/VoiceNoteRecorder.tsx`)

**Purpose:** Record voice notes using browser API

**Props:**
```typescript
interface VoiceNoteRecorderProps {
  onRecordingComplete: (file: File) => void
  onCancel?: () => void
  disabled?: boolean
}
```

**Features:**
- Browser MediaRecorder API
- Recording timer
- Waveform visualization
- Stop/Cancel buttons
- Microphone permission handling
- Audio playback preview
- Auto-save as .webm

---

### 8. TypingIndicator (`components/features/messaging/TypingIndicator.tsx`)

**Purpose:** Show "User is typing..." status

**Features:**
- Animated dots (. .. ...)
- Multiple users: "Alice and Bob are typing..."
- 3-second auto-timeout
- Minimal UI footprint

---

## Hooks

### useWebSocket

```typescript
const { isConnected, lastMessage, send } = useWebSocket({
  conversationId: 'conv_123',
  onNewMessage: (message) => { },
  onTypingIndicator: (user) => { },
  onMessageRead: (messageId) => { },
});
```

**Features:**
- Auto-connect on mount
- Reconnection with exponential backoff
- Event forwarding
- Auto-cleanup on unmount

---

### useMessages

```typescript
const {
  messages,
  isLoading,
  hasMore,
  addMessage,
  updateMessage,
  deleteMessage,
  loadMore,
} = useMessages(conversationId);
```

**Features:**
- Cursor-based pagination
- Optimistic updates
- Message caching
- Infinite scroll support

---

### useConversations

```typescript
const {
  conversations,
  isLoading,
  selectedConversation,
  select,
  deselect,
  refresh,
  search,
  updateUnreadCount,
} = useConversations();
```

**Features:**
- Conversation list management
- Filtering and search
- Unread count tracking
- Auto-refresh

---

## Services

### messagingService

```typescript
// Conversations
await messagingService.createConversation(recipientId)
await messagingService.listConversations({ page, search, unreadOnly })
await messagingService.getConversation(conversationId)
await messagingService.deleteConversation(conversationId)

// Messages
await messagingService.sendMessage(conversationId, content)
await messagingService.editMessage(messageId, content)
await messagingService.deleteMessage(messageId)
await messagingService.getMessages(conversationId, { page, cursor })
await messagingService.markMessageRead(messageId)
await messagingService.markConversationRead(conversationId)

// Files
await messagingService.uploadAttachment(messageId, file, onProgress)

// Search
await messagingService.searchConversations(query)
await messagingService.searchMessages(conversationId, query)

// Settings
await messagingService.getSettings()
await messagingService.updateSettings(settings)

// Blocking
await messagingService.blockUser(userId, reason)
await messagingService.unblockUser(userId)
await messagingService.getBlockedUsers()

// Reporting
await messagingService.reportMessage(messageId, reason, details)

// Requests
await messagingService.getMessageRequests()
await messagingService.acceptRequest(conversationId)
await messagingService.declineRequest(conversationId)
```

---

## State Management Pattern

### Redux-like Pattern (Not Redux)

```typescript
// Hook manages state, reducer-like dispatch
const [state, dispatch] = useState(initialState);

// Updates via action objects
dispatch({ type: 'ADD_MESSAGE', payload: message });
dispatch({ type: 'UPDATE_UNREAD', payload: { conversationId, count } });
```

### Context API

```typescript
// WebSocket context
<WebSocketProvider>
  <MessagesPage />
</WebSocketProvider>
```

---

## Real-Time Features

### WebSocket Connection

```typescript
const ws = new WebSocket(`${WS_URL}/conversations?token=${token}`);

// Listen for events
ws.onmessage = (event) => {
  const { event: eventType, data } = JSON.parse(event.data);
  
  if (eventType === 'new_message') {
    // Update UI
  } else if (eventType === 'typing_indicator') {
    // Show typing status
  }
};

// Send events
ws.send(JSON.stringify({
  event: 'typing_start',
  conversation_id: 'conv_123'
}));
```

### Polling Fallback

When WebSocket unavailable:
```typescript
// Poll every 3 seconds
setInterval(async () => {
  const { messages, typing_users } = await fetch(
    `/api/v1/messaging/conversations/${conversationId}/poll?since=${lastUpdate}`
  ).then(r => r.json());
  
  // Update UI
}, 3000);
```

---

## User Flows

### Send Message Flow
```
User types message
  ↓
onTyping fires (debounced 3s)
  ↓
WebSocket: typing_start event
  ↓
User presses Enter
  ↓
onSend fires
  ↓
Show optimistic UI (message appears immediately)
  ↓
POST /api/v1/messaging/messages
  ↓
API response with real message ID
  ↓
Update optimistic message with real data
  ↓
WebSocket broadcast to other users
```

### Read Receipt Flow
```
User opens conversation
  ↓
Auto-mark all messages as read
  ↓
POST /api/v1/messaging/{conversationId} read
  ↓
MessageReadReceipt created in DB
  ↓
WebSocket: message_read event
  ↓
Update checkmarks on sender's side (if read_receipts_enabled)
  ↓
Unread count updates in UI
```

### Block User Flow
```
User clicks "Block" on message
  ↓
BlockUserModal opens
  ↓
User enters reason (optional)
  ↓
User clicks "Block"
  ↓
POST /api/v1/messaging/block
  ↓
Conversation hidden immediately
  ↓
User added to BlockedUsers list
  ↓
Can view/unblock in MessagingSettings
```

---

## Error Handling

### API Errors

```typescript
try {
  await messagingService.sendMessage(conversationId, content);
} catch (error) {
  if (error.status === 403) {
    // User blocked or not accepting messages
    showError('Cannot message this user');
  } else if (error.status === 429) {
    // Rate limited
    showError('Slow down, too many messages');
  } else if (error.status === 400) {
    // Validation error
    showError(error.detail);
  }
}
```

### WebSocket Errors

```typescript
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  // Fall back to polling
  startPolling();
};

ws.onclose = () => {
  // Reconnect with exponential backoff
  reconnect();
};
```

### Error Boundary

```typescript
<MessageErrorBoundary>
  <MessageThread conversation={conversation} />
</MessageErrorBoundary>
```

---

## Performance Optimizations

### 1. Message Virtualization
```typescript
// Only render visible messages
import { FixedSizeList } from 'react-window';

<FixedSizeList
  itemCount={messages.length}
  itemSize={60}
  height={600}
>
  {({ index, style }) => (
    <MessageBubble message={messages[index]} style={style} />
  )}
</FixedSizeList>
```

### 2. Image Optimization
```typescript
// Lazy load images
<img src={attachmentThumb} loading="lazy" />
// Load full on click
onClick={() => loadFullImage()}
```

### 3. Debounce Typing
```typescript
const debouncedTyping = useCallback(
  debounce((isTyping) => {
    if (isTyping) ws.send({ event: 'typing_start' });
  }, 500),
  []
);
```

### 4. Memo Components
```typescript
export default React.memo(MessageBubble);
```

---

## Responsive Design

### Mobile (320px - 768px)
- Full-width conversation list
- Toggle to full-width message thread
- Single column layout
- Larger touch targets (44px min)

### Tablet (768px - 1024px)
- Narrow sidebar (25%)
- Main content (75%)
- Landscape and portrait support

### Desktop (1024px+)
- Fixed sidebar (300px)
- Main content (rest)
- Multi-column layout
- Keyboard shortcuts

---

## Configuration

### Environment Variables
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_UPLOAD_MAX_SIZE=10485760  # 10MB
```

### Feature Flags
```typescript
const FEATURES = {
  VOICE_NOTES: true,
  MESSAGE_SEARCH: true,
  MESSAGE_REACTIONS: false,  // Future
  GROUP_CHAT: false,          // Future
  E2E_ENCRYPTION: false,      // Future
};
```

---

## Testing

### Component Testing
```typescript
import { render, screen } from '@testing-library/react';
import MessageBubble from './MessageBubble';

it('should render message content', () => {
  const message = { id: '1', content: 'Hello' };
  render(<MessageBubble message={message} isOwn={true} />);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

### WebSocket Testing
```typescript
// Mock WebSocket
global.WebSocket = jest.fn(() => ({
  send: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
}));
```

---

## Deployment

### Build
```bash
npm run build
```

### Start
```bash
npm start
```

### Docker
```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

---

## Troubleshooting

### WebSocket Disconnects Immediately
- Check JWT token validity
- Verify WebSocket URL in config
- Check CORS headers on backend
- Check firewall rules

### Messages Not Sending
- Check network tab for errors
- Verify recipient not blocked
- Check message content (1-2000 chars)
- Check rate limits

### UI Not Updating
- Check console for errors
- Verify WebSocket events received
- Check component re-render logic
- Clear browser cache

### Performance Issues
- Reduce message virtualization threshold
- Optimize image sizes
- Enable code splitting
- Profile with Chrome DevTools

---

## Next Steps

1. **Integration Testing** - Test all user flows end-to-end
2. **Load Testing** - Test with 1000+ concurrent users
3. **Security Audit** - Review security practices
4. **A/B Testing** - Test UI variations
5. **Analytics** - Add usage tracking
6. **Push Notifications** - Integrate with NotificationService

---

## Support Resources

- **API Docs:** `MESSAGING_API_REFERENCE.md`
- **Backend:** `MESSAGING_SYSTEM_COMPLETION.md`
- **Tests:** `backend/test_messaging_system.py`

