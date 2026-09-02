# Implementation Plan: AI Chat Interface

## Overview

This implementation plan breaks down the AI Chat Interface into discrete, manageable coding tasks. The approach follows an incremental development strategy: foundation layer → communication layer → UI components → integration → testing. Each task builds on previous work, ensuring continuous progress with early validation points.

## Tasks

- [x] 1. Set up project structure and core TypeScript interfaces
  - Create `frontend/src/components/chat/` directory structure
  - Define TypeScript interfaces for Message, Conversation, ChatState, PageContext
  - Define WebSocket message protocol types (ChatMessagePayload, StreamingChunk)
  - Set up index exports for clean imports
  - _Requirements: All requirements (foundation for entire feature)_

- [x] 2. Implement WebSocket client with reconnection logic
  - [x] 2.1 Create ChatWebSocketClient class
    - Implement connection management (connect, disconnect)
    - Add JWT authentication to WebSocket handshake
    - Create message queue for pending messages
    - _Requirements: 11.1, 11.2, 11.6_
  
  - [x] 2.2 Implement exponential backoff reconnection
    - Add reconnection logic with 1s, 2s, 4s, 8s, 16s delays
    - Limit reconnection attempts to 5 maximum
    - Flush message queue after successful reconnection
    - _Requirements: 11.3_
  
  - [x] 2.3 Add message handling and event callbacks
    - Implement onMessage, onError, onClose callbacks
    - Parse StreamingChunk messages from server
    - Handle 'chunk', 'done', 'error' message types
    - _Requirements: 11.4, 11.5, 11.7_

- [x] 3. Create chat state management with Zustand
  - [x] 3.1 Define ChatStore with Zustand
    - Create state: isOpen, messages, streamingContent, connectionStatus
    - Implement actions: sendMessage, appendStreamingChunk, finalizeStreamingMessage
    - Add openChat, closeChat, clearConversation actions
    - _Requirements: 4.1, 4.7_
  
  - [x] 3.2 Implement sessionStorage persistence
    - Add loadFromSession action to restore conversation on mount
    - Add saveToSession action (debounced 1000ms)
    - Implement 50-message limit with oldest-first removal
    - Add 1-hour expiration check and cleanup
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [x] 3.3 Integrate WebSocket client with ChatStore
    - Initialize WebSocket connection when chat opens
    - Connect WebSocket callbacks to ChatStore actions
    - Handle connection status updates in store
    - Close WebSocket when chat closes
    - _Requirements: 11.1, 11.6_

- [x] 4. Build core UI components with glassmorphism styling
  - [x] 4.1 Create ChatInterface root component
    - Implement responsive layout (400px sidebar on desktop, full-screen on mobile)
    - Add slide-in animation (300ms ease-in-out)
    - Implement portal rendering for global access
    - Add glassmorphism styling (backdrop-blur, 80% opacity)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 12.1, 12.2_
  
  - [x] 4.2 Create MessageBubble component
    - Render user messages (right-aligned, solid background)
    - Render AI messages (left-aligned, gradient border)
    - Add fade-in animation (200ms ease-in)
    - Style with purple-to-blue gradient for AI messages
    - _Requirements: 12.3, 12.4_
  
  - [x] 4.3 Create TypingIndicator component
    - Render 3 animated dots with pulse animation (1.5s infinite)
    - Add staggered animation delays (0s, 0.2s, 0.4s)
    - Show/hide based on isStreaming state
    - _Requirements: 3.2, 3.5_
  
  - [x] 4.4 Create ChatHeader component
    - Add close button with smooth hover effect
    - Position minimize button (desktop only)
    - Add context badge showing current page type
    - Style with glassmorphism header design
    - _Requirements: 1.7, 7.7_

- [x] 5. Implement markdown rendering and copy functionality
  - [x] 5.1 Integrate markdown renderer (react-markdown)
    - Support bold (**text**), italic (*text*), code (`code`)
    - Support bullet lists (-), numbered lists (1.)
    - Support headings (#, ##, ###)
    - Support clickable links ([text](url))
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [x] 5.2 Add HTML sanitization with DOMPurify
    - Sanitize markdown HTML output to prevent XSS
    - Allow safe markdown elements only
    - Apply platform typography styles
    - _Requirements: 8.5, 8.6_
  
  - [x] 5.3 Implement CopyButton component
    - Position in top-right corner of AI message bubbles
    - Copy message content to clipboard on click
    - Show checkmark feedback for 2 seconds after copy
    - Display error message if clipboard API fails
    - Add "Copy to clipboard" tooltip on hover
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 6. Build QuotaDisplay component with upgrade prompt
  - [x] 6.1 Create QuotaDisplay component
    - Display "X/20" for free-tier users
    - Display "Unlimited ⚡" for premium users
    - Change to amber color when remaining ≤ 5
    - Change to red color when remaining = 0
    - Add tooltip showing reset time on hover
    - Position in ChatHeader
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [x] 6.2 Create UpgradePrompt modal component
    - Show modal when quota = 0 and user tries to send message
    - List premium benefits (unlimited requests, priority, advanced features)
    - Include pricing information and "Upgrade Now" CTA
    - Add "Maybe Later" option to close modal
    - Navigate to subscription page on "Upgrade Now" click
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 6.3 Add quota reset notification
    - Display banner for 5 seconds when quota resets
    - Style with success color (green)
    - Auto-dismiss after 5 seconds
    - _Requirements: 10.7_

- [x] 7. Checkpoint - Test core chat functionality
  - Ensure WebSocket connection establishes successfully
  - Verify messages send and receive correctly
  - Test streaming response display works
  - Confirm sessionStorage persistence works
  - Test reconnection logic with network interruption
  - Verify quota display updates correctly
  - Ask the user if questions arise.

- [x] 8. Implement real-time streaming with auto-scroll
  - [x] 8.1 Add streaming chunk handler
    - Append chunks to streamingContent in ChatStore
    - Display streaming content with character-by-character animation (50ms)
    - Finalize message when 'done' event received
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 8.2 Implement auto-scroll for MessageList
    - Auto-scroll to bottom when new chunk arrives
    - Use smooth scroll behavior (300ms duration)
    - Disable auto-scroll if user manually scrolled up
    - Re-enable auto-scroll when user scrolls to bottom
    - _Requirements: 3.4_
  
  - [x] 8.3 Add typing indicator with 200ms delay
    - Show TypingIndicator within 200ms of message send
    - Hide TypingIndicator when first chunk arrives
    - Handle timeout scenario (30s) with error display
    - _Requirements: 3.1, 3.5, 3.6_

- [x] 9. Build MessageInput component with send functionality
  - Create TextArea with auto-resize (max 5 lines)
  - Add SendButton with loading state
  - Disable input when quota exceeded
  - Add Enter key to send (Shift+Enter for new line)
  - Implement character limit (4000 chars) with counter
  - Clear input after successful send
  - _Requirements: 4.1_

- [x] 10. Create QuickActionButton system
  - [x] 10.1 Define quick action configurations
    - Create QUICK_ACTIONS array with definitions
    - Define prompt templates for each action
    - Map actions to page types (availableOn)
    - Specify required context fields
    - _Requirements: 6.1, 6.2_
  
  - [x] 10.2 Create QuickActionButton component
    - Render button with icon and label
    - Show loading state during execution
    - Auto-populate prompt with context on click
    - Display horizontally scrollable bar on mobile
    - _Requirements: 6.3, 6.4, 6.6, 6.7_
  
  - [x] 10.3 Add "Use This" functionality
    - Show "Use This" button on AI response completion
    - Auto-fill target form field when clicked (e.g., title input, description textarea)
    - Provide visual confirmation (toast notification)
    - _Requirements: 16.3, 16.4, 19.4, 20.5_

- [x] 11. Implement context provider system
  - [x] 11.1 Create PageContext extraction utilities
    - Define CONTEXT_EXTRACTORS for each page type
    - Extract beat upload context (genre, bpm, mood, file metadata)
    - Extract campaign context (metrics, budget, target audience)
    - Extract analytics context (time range, revenue, plays, trends)
    - Extract profile context (existing bio, genres, location)
    - _Requirements: 7.1, 7.2, 7.3, 7.5_
  
  - [x] 11.2 Create ContextProvider component
    - Detect current page type from URL
    - Extract context data automatically
    - Inject context into WebSocket messages
    - Filter sensitive data (passwords, tokens, payment info)
    - Display context badge in ChatHeader
    - _Requirements: 7.4, 7.6, 7.7_
  
  - [x] 11.3 Handle insufficient context scenarios
    - Detect missing required context fields
    - Prompt user for missing information via chat
    - Show helpful error message for quick actions
    - _Requirements: 6.5_

- [x] 12. Integrate with existing useAI hook
  - Wrap ChatInterface with useAI hook provider
  - Read quota status from useAI.quota
  - Use useAI.loadQuota() to refresh after messages
  - Use useAI.generate() for quick action requests
  - Handle useAI.error for quick actions
  - Display useAI.loading state for quick actions
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [x] 13. Add mobile-specific features
  - [x] 13.1 Implement responsive layout breakpoints
    - Apply sidebar layout for desktop (≥1024px)
    - Apply full-screen overlay for tablet (768-1024px)
    - Apply full-screen overlay for mobile (<768px)
    - _Requirements: 1.3, 2.1_
  
  - [x] 13.2 Add swipe-down-to-close gesture
    - Implement touch event handlers (touchstart, touchmove, touchend)
    - Calculate swipe distance (deltaY > 100px)
    - Close chat interface on valid swipe
    - _Requirements: 2.4_
  
  - [x] 13.3 Handle virtual keyboard on mobile
    - Listen to visualViewport resize events
    - Adjust chat container padding when keyboard opens
    - Keep MessageInput visible above keyboard
    - _Requirements: 2.5_
  
  - [x] 13.4 Add back button and disable body scroll
    - Show back button in header (mobile only)
    - Disable body scroll when chat is open
    - Ensure touch targets are minimum 44x44px
    - _Requirements: 2.2, 2.3, 2.6_

- [x] 14. Implement error handling and retry logic
  - [x] 14.1 Create error handling system
    - Define ChatErrorType enum and ChatError interface
    - Create ERROR_MESSAGES map for user-friendly messages
    - Display errors in conversation as system messages
    - Add retry button to error messages
    - _Requirements: 13.1, 13.2_
  
  - [x] 14.2 Handle specific error types
    - Handle CONNECTION_FAILED with auto-retry countdown
    - Handle QUOTA_EXCEEDED with upgrade modal
    - Handle TIMEOUT (30s) with "Try again" option
    - Handle RATE_LIMIT with cooldown timer
    - Handle AUTHENTICATION_FAILED with login redirect
    - _Requirements: 13.3, 13.4, 13.5, 13.7_
  
  - [x] 14.3 Implement automatic retry logic
    - Retry failed requests up to 2 times automatically
    - Show retry button after 2 failures
    - Display partial response if streaming interrupted
    - _Requirements: 13.6_

- [x] 15. Add page-specific integrations
  - [x] 15.1 Beat Upload Page integration
    - Add quick actions: Generate Title, Write Description, Suggest Tags, Recommend Price
    - Extract context: genre, bpm, mood, file metadata
    - Implement "Use This Title" auto-fill
    - Implement "Use This Description" auto-fill
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6_
  
  - [x] 15.2 Campaign Page integration
    - Add quick actions: Analyze Performance, Suggest Optimizations, Generate Ad Copy
    - Extract context: campaign metrics, budget, target audience
    - Display insights with formatted lists and bold highlights
    - Provide 3-5 actionable optimization suggestions
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6_
  
  - [x] 15.3 Analytics Page integration
    - Add quick actions: Explain Trends, Compare Performance, Get Recommendations
    - Extract context: chart data, time periods, metrics
    - Generate natural language explanations of trends
    - Highlight significant changes (e.g., "plays increased 45%")
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6_
  
  - [x] 15.4 Profile Page integration
    - Add quick actions: Write Bio, Craft Artist Statement, Suggest Improvements
    - Extract context: existing profile data, genres, location
    - Generate 3 bio variations (short, medium, long)
    - Implement "Use This Bio" auto-fill
    - Support iterative refinement
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6_
  
  - [x] 15.5 Social Media integration
    - Add quick action: Generate Caption
    - Generate platform-specific captions (Instagram, Twitter, TikTok)
    - Generate 5 caption variations with different tones
    - Generate relevant hashtags separately
    - Implement "Use This Caption" auto-fill
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6_

- [x] 16. Checkpoint - Test integrations and error handling
  - Test all page-specific context extractions
  - Verify quick actions work on each page
  - Test "Use This" auto-fill functionality
  - Verify error messages display correctly
  - Test retry functionality for failed requests
  - Test quota exceeded modal
  - Confirm mobile layout and gestures work
  - Ask the user if questions arise.

- [x] 17. Implement accessibility features
  - [x] 17.1 Add keyboard navigation
    - Implement Tab navigation through all interactive elements
    - Add focus trapping when chat is open (Tab cycles within chat)
    - Set focus to MessageInput when chat opens
    - Handle Escape key to close chat
    - Add Ctrl/Cmd+K shortcut to open chat
    - _Requirements: 14.1, 14.2, 14.3_
  
  - [x] 17.2 Add ARIA labels and screen reader support
    - Add aria-label to all buttons and interactive elements
    - Add aria-live region for new AI messages
    - Announce connection status changes to screen readers
    - Add role="dialog" to ChatInterface
    - _Requirements: 14.4, 14.5_
  
  - [x] 17.3 Add high contrast mode support
    - Add visible focus indicators (2px solid ring with offset)
    - Ensure 4.5:1 color contrast ratio (WCAG AA)
    - Test with browser high contrast mode enabled
    - _Requirements: 14.6, 14.7_

- [x] 18. Add performance optimizations
  - [x] 18.1 Implement virtual scrolling for messages
    - Integrate react-window for MessageList
    - Render only visible messages plus buffer
    - Lazy load old messages on scroll up
    - _Requirements: Performance (handle 1000+ messages)_
  
  - [x] 18.2 Add React.memo and memoization
    - Memoize MessageBubble component
    - Memoize QuickActionButton component
    - Use useMemo for expensive computations (markdown rendering)
    - Use useCallback for event handlers
    - _Requirements: Performance (smooth 60fps)_
  
  - [x] 18.3 Implement debouncing and throttling
    - Debounce sessionStorage saves (1000ms)
    - Throttle scroll events (100ms)
    - Debounce typing indicator (500ms)
    - _Requirements: Performance_

- [x] 19. Add code splitting and lazy loading
  - Use React.lazy for ChatInterface component
  - Use React.lazy for MarkdownRenderer component
  - Implement Suspense fallback loading state
  - Split quick action components by page type
  - _Requirements: Performance (bundle size < 150KB gzipped)_

- [x] 20. Create global chat trigger button
  - Add floating action button (FAB) to MainNav or global layout
  - Position in bottom-right corner on desktop
  - Position in navigation bar on mobile
  - Show unread indicator badge (if applicable)
  - Animate button on hover (scale 1.05x)
  - _Requirements: 1.1_

- [x] 21. Add conversation persistence across navigation
  - Maintain chat state when navigating between pages
  - Update context automatically when page changes
  - Preserve scroll position in message list
  - Update quick actions based on new page
  - _Requirements: 1.5_

- [x] 22. Implement clear conversation functionality
  - Add "Clear Conversation" button in ChatHeader menu
  - Show confirmation dialog before clearing
  - Clear messages from ChatStore
  - Clear sessionStorage
  - Reset conversation ID
  - Show success toast notification
  - _Requirements: 4.7_

- [x]* 23. Write unit tests for core components
  - Test ChatInterface renders correctly (open/closed states)
  - Test MessageBubble displays markdown formatting
  - Test QuickActionButton triggers correct prompts
  - Test QuotaDisplay shows correct tier information
  - Test TypingIndicator animation works
  - Test CopyButton copies content to clipboard
  - Test ContextProvider extracts correct context
  - _Requirements: Testing_

- [x]* 24. Write integration tests for WebSocket
  - Test WebSocket connects successfully
  - Test WebSocket authenticates with JWT
  - Test WebSocket sends and receives messages
  - Test WebSocket handles reconnection
  - Test WebSocket gracefully disconnects
  - _Requirements: Testing_

- [x]* 25. Write integration tests for useAI hook
  - Test quota updates after AI requests
  - Test quick actions use useAI methods
  - Test error handling works correctly
  - Test loading states work correctly
  - _Requirements: Testing_

- [x]* 26. Write end-to-end tests for user flows
  - Test: Open chat, send message, receive streaming response
  - Test: Copy AI response to clipboard
  - Test: Use quick action button
  - Test: Navigate between pages (conversation persists)
  - Test: Close and reopen chat (conversation restores)
  - Test: Exceed quota (upgrade modal appears)
  - Test: Clear conversation
  - Test: Handle connection loss and recovery
  - _Requirements: Testing_

- [x]* 27. Write accessibility tests
  - Test keyboard navigation (Tab, Enter, Escape)
  - Test screen reader announcements
  - Test high contrast mode support
  - Test focus indicators visible
  - Test with 200% zoom
  - Test touch target sizes (minimum 44x44px)
  - _Requirements: Testing (WCAG 2.1 AA compliance)_

- [x] 28. Final checkpoint - End-to-end verification
  - Test full user flow from all 7 pages
  - Verify all quick actions work correctly
  - Confirm auto-fill functionality works
  - Test mobile responsive design
  - Verify quota management works
  - Test upgrade flow for free users
  - Confirm WebSocket reconnection works
  - Verify accessibility compliance
  - Check performance metrics (bundle size, render time)
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at reasonable breakpoints
- The implementation follows a bottom-up approach: foundation → communication → UI → integration
- WebSocket integration reuses existing infrastructure (`websocket_manager.py`)
- useAI hook integration ensures consistency with existing AI features
- Mobile-first design ensures the interface works seamlessly on all devices
- Accessibility is integrated throughout, not added as an afterthought
- Performance optimizations (virtual scrolling, code splitting) are built in from the start
