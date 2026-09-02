# Error Handling System - AI Chat Interface

## Overview

The AI Chat Interface implements a comprehensive error handling system that provides:
- User-friendly error messages
- Automatic retry logic for transient failures
- Specific actions for different error types (retry, upgrade, login, wait)
- Graceful degradation and recovery
- Error classification and transformation utilities

## Architecture

The error handling system consists of four main components:

### 1. Error Types and Interfaces (`types/index.ts`)

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

### 2. Error Constants (`constants/index.ts`)

Defines user-friendly error messages for each error type:

```typescript
const ERROR_MESSAGES: Record<ChatErrorType, string> = {
  [ChatErrorType.CONNECTION_FAILED]: 'Connection lost. Retrying in {seconds}s...',
  [ChatErrorType.QUOTA_EXCEEDED]: "You've used all 20 free AI requests today...",
  // ... more messages
};
```

### 3. Error Utilities (`utils/errorUtils.ts`)

Provides helper functions for creating, classifying, and transforming errors:

- `createChatError()` - Create a ChatError with proper defaults
- `classifyError()` - Map status codes and messages to ChatErrorType
- `fromError()` - Convert generic errors to ChatError
- `isRetryable()` - Check if error can be retried
- `shouldAutoRetry()` - Check if error should trigger auto-retry
- `extractRetryDelay()` - Get retry delay from error
- `formatErrorMessage()` - Replace placeholders in error messages
- Helper functions: `isQuotaError()`, `isAuthError()`, `isConnectionError()`, `isTimeoutError()`

### 4. Error UI Component (`components/ErrorMessage.tsx`)

Displays errors with appropriate styling and actions:

- Shows error icon based on type
- Displays user-friendly error message
- Renders action buttons (retry, upgrade, login, wait)
- Handles countdowns for auto-retry
- Shows cooldown timers for rate limits
- Provides additional context for specific errors

## Error Flow

### 1. WebSocket Client Level (`utils/ChatWebSocketClient.ts`)

```
WebSocket Error
    ↓
handleError() callback
    ↓
useChatWebSocket hook receives error
```

### 2. Hook Level (`hooks/useChatWebSocket.ts`)

```
Receives error/chunk
    ↓
Classify error type
    ↓
Create ChatError with createChatError()
    ↓
Check if auto-retry should happen (shouldAutoRetry)
    ↓
If auto-retry: increment retry count, wait 2s, resend
    ↓
If max retries reached: setError in store
```

### 3. Store Level (`store/chatStore.ts`)

```
setError(chatError)
    ↓
Store error in state
    ↓
Stop streaming if active
```

### 4. UI Level (`components/ChatInterface.tsx` + `components/ErrorMessage.tsx`)

```
Error in store
    ↓
ChatInterface renders ErrorMessage component
    ↓
ErrorMessage shows:
  - Error icon
  - Error message with dynamic values
  - Action button (retry/upgrade/login/wait)
  - Countdown/cooldown timer
  - Additional context
```

## Error Types and Handling

### CONNECTION_FAILED

**Trigger**: WebSocket connection fails to establish or drops

**Behavior**:
- Automatic reconnection with exponential backoff (1s, 2s, 4s, 8s, 16s)
- Up to 5 reconnection attempts at WebSocket client level
- Auto-retry up to 2 times at hook level
- Shows countdown: "Connection lost. Retrying in 5s..."
- Action: Auto-retry with countdown display

**User Experience**:
- User sees error message with countdown
- Connection attempts happen automatically
- If all retries fail, manual retry button appears

**Code Example**:
```typescript
const error = createChatError(
  ChatErrorType.CONNECTION_FAILED,
  'Failed to connect to server'
);
```

### WEBSOCKET_CLOSED

**Trigger**: WebSocket connection closes unexpectedly

**Behavior**:
- Similar to CONNECTION_FAILED
- Triggers reconnection logic
- Queues pending messages for redelivery

**User Experience**:
- "Connection closed. Click retry to reconnect."
- Manual retry button

### MESSAGE_SEND_FAILED

**Trigger**: Failed to send message through WebSocket

**Behavior**:
- Auto-retry up to 2 times (2 second delay between attempts)
- Stores failed message in `lastFailedMessage`
- Action: 'retry'

**User Experience**:
- "Failed to send message. Please try again."
- Retry button to manually resend

**Code Example**:
```typescript
const error = createChatError(
  ChatErrorType.MESSAGE_SEND_FAILED,
  'Network error while sending'
);
```

### STREAMING_INTERRUPTED

**Trigger**: Streaming response is interrupted mid-stream

**Behavior**:
- Saves partial response if available (calls `finalizeStreamingMessage`)
- Auto-retry up to 2 times
- Action: 'retry'

**User Experience**:
- Sees partial response (if any)
- "Response interrupted. Click retry to continue."
- Retry button

### QUOTA_EXCEEDED

**Trigger**: User has used all daily AI requests (free tier)

**Behavior**:
- NO auto-retry (not a transient error)
- Shows upgrade modal
- Action: 'upgrade'

**User Experience**:
- "You've used all 20 free AI requests today. Upgrade to Premium!"
- "Upgrade Now" button → navigates to /subscription
- Shows quota reset time
- Additional info: "Your daily quota will reset at midnight"

**Code Example**:
```typescript
const error = createChatError(
  ChatErrorType.QUOTA_EXCEEDED
);
// Automatically shows upgrade modal in ChatInterface
```

### AUTHENTICATION_FAILED

**Trigger**: JWT token expired or invalid

**Behavior**:
- NO auto-retry
- Saves conversation to sessionStorage
- Action: 'login'

**User Experience**:
- "Session expired. Please log in again."
- "Log In" button → navigates to /login
- Conversation restored after re-authentication

**Code Example**:
```typescript
const error = createChatError(
  ChatErrorType.AUTHENTICATION_FAILED,
  'Your session has expired'
);
```

### TIMEOUT

**Trigger**: No response received within 30 seconds

**Behavior**:
- Saves partial response if available
- Auto-retry up to 2 times
- Action: 'retry'

**User Experience**:
- "AI is taking longer than usual. Please try again."
- Retry button
- Additional info: "Try asking a simpler question or break your request into smaller parts"

**Code Example**:
```typescript
// Timeout is handled automatically in useChatWebSocket
// Set after 30 seconds of no response
```

### RATE_LIMIT

**Trigger**: Too many requests in short time period (429 status)

**Behavior**:
- NO auto-retry
- Shows cooldown timer (default 60 seconds)
- Extracts retry-after from error message if available
- Action: 'wait'

**User Experience**:
- "Too many requests. Please wait 60 seconds."
- Disabled send button
- Countdown timer showing remaining seconds
- Automatically re-enables when countdown reaches 0

**Code Example**:
```typescript
const error = createChatError(
  ChatErrorType.RATE_LIMIT,
  'Please wait 30 seconds before trying again'
);
// extractRetryDelay(error) returns 30
```

### SERVER_ERROR

**Trigger**: Backend service unavailable (500, 503 status)

**Behavior**:
- Auto-retry up to 2 times
- Action: 'retry'

**User Experience**:
- "Our AI service is temporarily unavailable. We're working on it!"
- Retry button

**Code Example**:
```typescript
const error = createChatError(
  ChatErrorType.SERVER_ERROR,
  'Backend service is down'
);
```

## Auto-Retry Logic

### Two-Level Retry System

#### Level 1: WebSocket Client Reconnection
- Handles connection-level failures
- Exponential backoff: [1s, 2s, 4s, 8s, 16s]
- Maximum 5 reconnection attempts
- Queues messages during reconnection

#### Level 2: Hook-Level Message Retry
- Handles message send failures
- Fixed 2-second delay between retries
- Maximum 2 retry attempts
- Only retries specific error types

### Auto-Retry Logic (`useChatWebSocket.ts`)

```typescript
const MAX_AUTO_RETRIES = 2;

const handleAutoRetry = (errorType: ChatErrorType) => {
  // Check if error is retryable
  if (!shouldAutoRetry(error)) {
    return;
  }

  // Check retry count
  if (retryCount < MAX_AUTO_RETRIES) {
    incrementRetryCount();
    
    // Wait 2 seconds
    setTimeout(() => {
      setError(null);
      // Resend last failed message
      sendMessage(lastFailedMessage);
    }, 2000);
  } else {
    // Max retries reached
    setError({
      type: errorType,
      message: 'Failed after multiple attempts',
      retryable: true,
      action: 'retry',
    });
  }
};
```

### Retriable vs Non-Retriable Errors

**Auto-Retriable** (up to 2 attempts):
- CONNECTION_FAILED
- STREAMING_INTERRUPTED
- MESSAGE_SEND_FAILED
- TIMEOUT

**Manually Retriable** (user clicks retry button):
- All auto-retriable errors (after max attempts)
- WEBSOCKET_CLOSED
- SERVER_ERROR

**Non-Retriable** (require user action):
- QUOTA_EXCEEDED → upgrade
- AUTHENTICATION_FAILED → login
- RATE_LIMIT → wait

## Error Utilities Usage

### Creating Errors

```typescript
import { createChatError, ChatErrorType } from '@/components/chat';

// Simple error creation
const error = createChatError(ChatErrorType.SERVER_ERROR);

// With custom message
const error = createChatError(
  ChatErrorType.TIMEOUT,
  'Request took too long to complete'
);

// With metadata
const error = createChatError(
  ChatErrorType.RATE_LIMIT,
  'Rate limit exceeded',
  { retryAfter: 60 }
);
```

### Converting Errors

```typescript
import { fromError, fromHttpResponse, classifyError } from '@/components/chat';

// From JavaScript Error
try {
  // ... code
} catch (err) {
  const chatError = fromError(err);
  setError(chatError);
}

// From HTTP Response
const response = await fetch('/api/ai/generate');
if (!response.ok) {
  const errorData = await response.json();
  const chatError = fromHttpResponse(response, errorData);
  setError(chatError);
}

// Classify generic error
const errorType = classifyError('Connection timeout');
// Returns: ChatErrorType.TIMEOUT
```

### Checking Error Properties

```typescript
import {
  isRetryable,
  isQuotaError,
  isAuthError,
  shouldAutoRetry,
  extractRetryDelay,
} from '@/components/chat';

// Check if error is retryable
if (isRetryable(error)) {
  // Show retry button
}

// Check for specific error types
if (isQuotaError(error)) {
  showUpgradeModal();
}

if (isAuthError(error)) {
  redirectToLogin();
}

// Check if auto-retry should happen
if (shouldAutoRetry(error)) {
  // Trigger auto-retry logic
}

// Get retry delay
const delay = extractRetryDelay(error);
// Returns delay in seconds or null
```

### Formatting Error Messages

```typescript
import { formatErrorMessage, getDisplayMessage } from '@/components/chat';

// Format with placeholders
const message = formatErrorMessage(
  'Connection lost. Retrying in {seconds}s...',
  { seconds: 5 }
);
// Returns: "Connection lost. Retrying in 5s..."

// Get display message from error
const displayMessage = getDisplayMessage(error, { seconds: 30 });
```

### Merging Multiple Errors

```typescript
import { mergeErrors } from '@/components/chat';

const errors = [
  createChatError(ChatErrorType.CONNECTION_FAILED),
  createChatError(ChatErrorType.QUOTA_EXCEEDED),
  createChatError(ChatErrorType.SERVER_ERROR),
];

// Returns the highest priority error (QUOTA_EXCEEDED in this case)
const mergedError = mergeErrors(errors);
```

## Error Display Component

### ErrorMessage Component Usage

```tsx
import { ErrorMessage } from '@/components/chat';

function MyComponent() {
  const { error, retryMessage } = useChatStore();
  
  return (
    <>
      {error && (
        <ErrorMessage
          error={error}
          onRetry={() => {
            setError(null);
            retryMessage();
          }}
          onUpgrade={() => router.push('/subscription')}
          onLogin={() => router.push('/login')}
        />
      )}
    </>
  );
}
```

### ErrorMessage Props

```typescript
interface ErrorMessageProps {
  error: ChatError;           // Required: The error to display
  onRetry?: () => void;       // Optional: Retry callback
  onUpgrade?: () => void;     // Optional: Upgrade callback
  onLogin?: () => void;       // Optional: Login callback
}
```

### ErrorMessage Features

- **Automatic Countdowns**: CONNECTION_FAILED shows 5-second countdown and auto-retries
- **Cooldown Timers**: RATE_LIMIT shows remaining cooldown time
- **Action Buttons**: Context-appropriate buttons based on error.action
- **Icons**: Different icons for each error type (AlertCircle, Zap, LogIn, Clock)
- **Additional Info**: Extra context for QUOTA_EXCEEDED and TIMEOUT errors
- **Timestamps**: Shows time when error occurred
- **Animations**: Fade-in animation for smooth appearance

## Integration Examples

### In a Component

```tsx
import { useChatStore } from '@/components/chat/store/chatStore';
import { ErrorMessage } from '@/components/chat/components/ErrorMessage';
import { createChatError, ChatErrorType } from '@/components/chat';

function ChatComponent() {
  const { error, setError } = useChatStore();
  
  const handleApiCall = async () => {
    try {
      const response = await fetch('/api/ai/generate');
      if (!response.ok) {
        const chatError = fromHttpResponse(response);
        setError(chatError);
      }
    } catch (err) {
      const chatError = fromError(err);
      setError(chatError);
    }
  };
  
  return (
    <div>
      {error && (
        <ErrorMessage
          error={error}
          onRetry={() => {
            setError(null);
            handleApiCall();
          }}
        />
      )}
    </div>
  );
}
```

### In WebSocket Hook

```tsx
// Already implemented in useChatWebSocket.ts
const { sendMessage, retryMessage } = useChatWebSocket({
  token: authToken,
  enabled: isOpen,
  context: pageContext,
});

// Errors are automatically handled:
// 1. WebSocket errors → CONNECTION_FAILED
// 2. Streaming errors → STREAMING_INTERRUPTED
// 3. Timeout (30s) → TIMEOUT
// 4. Send failures → MESSAGE_SEND_FAILED
```

## Best Practices

### 1. Always Use createChatError

```typescript
// ✅ Good
const error = createChatError(ChatErrorType.TIMEOUT);

// ❌ Bad
const error = { type: 'timeout', message: 'Timeout' };
```

### 2. Let Auto-Retry Handle Transient Failures

```typescript
// ✅ Good - auto-retry handles it
if (shouldAutoRetry(error)) {
  // Hook handles retry automatically
}

// ❌ Bad - don't bypass auto-retry
setError(error);
showRetryButton();
```

### 3. Classify Unknown Errors

```typescript
// ✅ Good
try {
  await someOperation();
} catch (err) {
  const chatError = fromError(err);
  setError(chatError);
}

// ❌ Bad
catch (err) {
  setError({ type: 'error', message: String(err) });
}
```

### 4. Provide Context in Error Messages

```typescript
// ✅ Good
const error = createChatError(
  ChatErrorType.MESSAGE_SEND_FAILED,
  'Failed to send message to beat upload AI'
);

// ❌ Bad
const error = createChatError(ChatErrorType.MESSAGE_SEND_FAILED);
```

### 5. Use Helper Functions for Error Checking

```typescript
// ✅ Good
if (isQuotaError(error)) {
  showUpgradeModal();
}

// ❌ Bad
if (error.type === 'quota_exceeded') {
  showUpgradeModal();
}
```

## Testing

### Unit Testing Error Utilities

```typescript
import { createChatError, classifyError, shouldAutoRetry } from './errorUtils';

describe('Error Utilities', () => {
  it('should create retryable error', () => {
    const error = createChatError(ChatErrorType.CONNECTION_FAILED);
    expect(error.retryable).toBe(true);
    expect(error.action).toBe('retry');
  });

  it('should classify 429 as RATE_LIMIT', () => {
    const type = classifyError({ status: 429 });
    expect(type).toBe(ChatErrorType.RATE_LIMIT);
  });

  it('should auto-retry CONNECTION_FAILED', () => {
    const error = createChatError(ChatErrorType.CONNECTION_FAILED);
    expect(shouldAutoRetry(error)).toBe(true);
  });
});
```

### Testing ErrorMessage Component

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorMessage } from './ErrorMessage';

it('should show retry button', () => {
  const mockRetry = vi.fn();
  const error = createChatError(ChatErrorType.MESSAGE_SEND_FAILED);
  
  render(<ErrorMessage error={error} onRetry={mockRetry} />);
  
  const button = screen.getByRole('button', { name: /try again/i });
  fireEvent.click(button);
  
  expect(mockRetry).toHaveBeenCalled();
});
```

## Debugging

### Enable Error Logging

```typescript
// In errorUtils.ts
export function logError(error: ChatError, context?: string) {
  const loggable = toLoggableError(error);
  console.error(`[Chat Error ${context ? `- ${context}` : ''}]:`, loggable);
}

// Usage
logError(error, 'WebSocket send');
```

### Inspect Error in DevTools

```typescript
// All errors are stored in ChatStore
const { error } = useChatStore();
console.log('Current error:', error);
```

### Monitor Auto-Retry Attempts

```typescript
// Check retry count
const { retryCount } = useChatStore();
console.log('Auto-retry attempts:', retryCount);
```

## Future Enhancements

1. **Error Analytics**: Track error frequency and types
2. **Custom Error Recovery**: Allow pages to register custom error handlers
3. **Error Boundaries**: React error boundaries for component errors
4. **Offline Mode**: Detect offline state and queue messages
5. **Error Notifications**: Toast notifications for non-blocking errors
6. **Detailed Error Codes**: Sub-codes for more specific error classification
7. **Error History**: Keep history of errors for debugging
8. **Retry Strategies**: Configurable retry strategies per error type

## Summary

The error handling system provides:

✅ **Comprehensive Error Types** - 9 distinct error types covering all failure modes
✅ **Auto-Retry Logic** - Automatic retry for transient failures (up to 2 attempts)
✅ **User-Friendly Messages** - Clear, actionable error messages
✅ **Specific Actions** - Context-appropriate buttons (retry, upgrade, login, wait)
✅ **Error Utilities** - Helper functions for creating, classifying, and transforming errors
✅ **UI Component** - Polished ErrorMessage component with countdowns and animations
✅ **Two-Level Retry** - WebSocket reconnection + message-level retry
✅ **Graceful Degradation** - Saves partial responses, preserves context
✅ **Test Coverage** - Comprehensive unit tests for utilities and components

The system ensures users always understand what went wrong and what they can do about it.
