# Requirements Document: AI Chat Interface

## Introduction

The AI Chat Interface is a Gemini-style conversational AI component that provides contextually-aware assistance throughout the BeatPush platform. Unlike task-specific AI endpoints, this feature delivers a unified chat experience where users can have natural conversations with an AI assistant that understands their current context (page, content, goals) and provides personalized guidance for music promotion, beat metadata generation, campaign optimization, and platform navigation. The interface must be accessible as a sidebar/panel on every page, support real-time streaming responses, display quota information transparently, provide quick action buttons for common tasks, and seamlessly integrate with existing backend AI services and WebSocket infrastructure.

## Glossary

- **Chat_Interface**: The Gemini-style sidebar/panel UI component that displays conversation history and input controls
- **Conversation_Session**: A single chat session that persists until the user closes the interface or navigates away
- **Message_Bubble**: Individual chat message display component (user messages on right, AI responses on left)
- **Streaming_Response**: Real-time display of AI responses as they are generated, character-by-character or chunk-by-chunk
- **Typing_Indicator**: Visual feedback (animated dots) showing that the AI is processing a response
- **Quick_Action_Button**: Pre-configured button that triggers common AI tasks (Generate Title, Create Description, etc.)
- **Context_Provider**: Service that automatically injects current page data into AI prompts
- **Quota_Display**: UI component showing remaining AI requests for free-tier users
- **Copy_Button**: Button on AI response bubbles that copies content to clipboard
- **Upgrade_Prompt**: Modal or banner encouraging free users to upgrade when quota is low or exceeded
- **Mobile_Responsive**: Interface adapts layout for mobile devices (full-screen overlay instead of sidebar)
- **Glassmorphism**: Visual design style with frosted glass effect (backdrop blur, transparency)
- **Markdown_Renderer**: Component that parses and displays markdown formatting in AI responses

## Requirements

### Requirement 1: Persistent Sidebar Chat Interface

**User Story:** As a user, I want the AI chat interface available as a sidebar on every page, so that I can get help whenever I need it without leaving my current context.

#### Acceptance Criteria

1. THE Chat_Interface SHALL display as a collapsible sidebar on desktop viewports (1024px+)
2. WHEN the user clicks the AI chat trigger button, THE Chat_Interface SHALL slide in from the right with smooth animation
3. THE Chat_Interface SHALL occupy 400px width on desktop with a minimum of 320px
4. WHEN the Chat_Interface is open, THE main content SHALL remain visible and interactive
5. THE Chat_Interface SHALL persist across page navigation within the same session
6. WHEN the user closes the Chat_Interface, THE system SHALL save the conversation session for 1 hour
7. THE Chat_Interface SHALL include a header with close button, quota display, and minimize button

### Requirement 2: Mobile-Responsive Full-Screen Mode

**User Story:** As a mobile user, I want the chat interface to use my full screen, so that I have enough space for comfortable conversation without UI clutter.

#### Acceptance Criteria

1. WHEN viewport width is below 768px, THE Chat_Interface SHALL display as a full-screen overlay
2. THE Chat_Interface SHALL include a back button to close and return to the main content
3. THE Chat_Interface SHALL disable body scroll when open on mobile devices
4. THE Chat_Interface SHALL support swipe-down gesture to close on mobile
5. WHEN keyboard opens on mobile, THE Chat_Interface SHALL adjust layout to keep input visible
6. THE Chat_Interface SHALL maintain touch target sizes of at least 44x44px for all interactive elements

### Requirement 3: Real-Time Streaming Responses with Typing Indicator

**User Story:** As a user, I want to see AI responses appear in real-time, so that I know the system is working and don't have to wait for complete generation.

#### Acceptance Criteria

1. WHEN the user sends a message, THE Chat_Interface SHALL display a Typing_Indicator within 200ms
2. WHEN the AI starts generating a response, THE Chat_Interface SHALL stream text chunks as they arrive
3. THE Streaming_Response SHALL display with smooth character-by-character animation at 50ms per character
4. WHEN streaming is active, THE Chat_Interface SHALL auto-scroll to keep the latest content visible
5. THE Typing_Indicator SHALL disappear when the first response chunk arrives
6. WHEN streaming fails or times out (30s), THE Chat_Interface SHALL display an error message with retry option

### Requirement 4: Conversation History and Session Persistence

**User Story:** As a user, I want to see my conversation history within the current session, so that I can reference previous AI responses and maintain context.

#### Acceptance Criteria

1. THE Chat_Interface SHALL display all messages from the current Conversation_Session in chronological order
2. THE Chat_Interface SHALL persist conversation history in browser sessionStorage
3. WHEN the user refreshes the page, THE Chat_Interface SHALL restore conversation history from sessionStorage
4. THE Chat_Interface SHALL limit conversation history to the most recent 50 messages
5. WHEN conversation history exceeds 50 messages, THE Chat_Interface SHALL remove oldest messages
6. THE Chat_Interface SHALL include a "Clear Conversation" button in the interface header
7. WHEN the user clears conversation, THE Chat_Interface SHALL remove all messages and clear sessionStorage

### Requirement 5: Quota Display for Free-Tier Users

**User Story:** As a free-tier user, I want to see my remaining AI requests clearly displayed, so that I can manage my usage and know when to upgrade.

#### Acceptance Criteria

1. THE Quota_Display SHALL show remaining requests as "X/20" for free-tier users
2. THE Quota_Display SHALL update after each successful AI request
3. WHEN remaining quota is 5 or fewer, THE Quota_Display SHALL change to warning color (amber)
4. WHEN remaining quota is 0, THE Quota_Display SHALL change to error color (red)
5. THE Quota_Display SHALL show "Unlimited ⚡" for premium users
6. WHEN the user hovers over the Quota_Display, THE Chat_Interface SHALL show a tooltip with reset time
7. THE Quota_Display SHALL be positioned in the Chat_Interface header

### Requirement 6: Quick Action Buttons for Common Tasks

**User Story:** As a user, I want quick action buttons for common AI tasks, so that I can generate content without typing full instructions.

#### Acceptance Criteria

1. THE Chat_Interface SHALL display Quick_Action_Buttons below the message input field
2. THE Chat_Interface SHALL include buttons: "Generate Title", "Write Description", "Create Tags", "Generate Captions"
3. WHEN a user clicks a Quick_Action_Button, THE Chat_Interface SHALL auto-populate a contextual prompt
4. THE Quick_Action_Button prompts SHALL include relevant page context automatically
5. WHEN context is insufficient (e.g., no beat selected), THE Chat_Interface SHALL request missing information before proceeding
6. THE Quick_Action_Buttons SHALL be scrollable horizontally on mobile devices
7. THE Quick_Action_Buttons SHALL show loading state when clicked until response starts

### Requirement 7: Contextual AI Integration

**User Story:** As a user, I want the AI to understand what page I'm on and what content I'm viewing, so that I get relevant suggestions without explaining my context every time.

#### Acceptance Criteria

1. WHEN the user is on a beat upload page, THE Context_Provider SHALL inject beat metadata into AI prompts
2. WHEN the user is on a campaign page, THE Context_Provider SHALL inject campaign data into AI prompts
3. WHEN the user is on an analytics page, THE Context_Provider SHALL inject performance metrics into AI prompts
4. THE Context_Provider SHALL include current page URL and page type in every AI request
5. WHEN the user is editing content, THE Context_Provider SHALL include the content being edited
6. THE Context_Provider SHALL NOT include sensitive data (passwords, tokens, payment info) in prompts
7. THE Chat_Interface SHALL display current context in the header (e.g., "Helping with: Beat Upload")

### Requirement 8: Markdown Formatting in AI Responses

**User Story:** As a user, I want AI responses to include formatted text (bold, lists, code), so that information is easier to read and understand.

#### Acceptance Criteria

1. THE Markdown_Renderer SHALL support bold (**text**), italic (*text*), and code (`code`) formatting
2. THE Markdown_Renderer SHALL support bullet lists (- item) and numbered lists (1. item)
3. THE Markdown_Renderer SHALL support headings (# H1, ## H2, ### H3)
4. THE Markdown_Renderer SHALL support links ([text](url)) as clickable elements
5. THE Markdown_Renderer SHALL sanitize HTML to prevent XSS attacks
6. THE Markdown_Renderer SHALL apply appropriate typography styles consistent with platform design

### Requirement 9: Copy-to-Clipboard Functionality

**User Story:** As a user, I want to copy AI-generated content with one click, so that I can easily use suggestions in my beat descriptions, posts, and campaigns.

#### Acceptance Criteria

1. WHEN the AI response is complete, THE Message_Bubble SHALL display a Copy_Button in the top-right corner
2. WHEN the user clicks the Copy_Button, THE system SHALL copy the message content to clipboard
3. THE Copy_Button SHALL show visual feedback (checkmark) for 2 seconds after successful copy
4. WHEN clipboard copy fails, THE Copy_Button SHALL display an error message
5. THE Copy_Button SHALL copy plain text (markdown formatting converted to plain text)
6. THE Copy_Button SHALL have a tooltip "Copy to clipboard" on hover

### Requirement 10: Upgrade Prompts for Quota Exceeded

**User Story:** As a free-tier user who has exceeded my quota, I want clear information about premium benefits, so that I can make an informed decision about upgrading.

#### Acceptance Criteria

1. WHEN a free-tier user exceeds their daily quota, THE Chat_Interface SHALL display an Upgrade_Prompt modal
2. THE Upgrade_Prompt SHALL list premium benefits: unlimited requests, priority processing, advanced features
3. THE Upgrade_Prompt SHALL include pricing information and a "Upgrade Now" call-to-action button
4. THE Upgrade_Prompt SHALL include a "Maybe Later" option that closes the modal
5. WHEN the user clicks "Upgrade Now", THE system SHALL navigate to the subscription page
6. THE Upgrade_Prompt SHALL display when remaining quota is 0 and user attempts to send a message
7. WHEN quota resets, THE Chat_Interface SHALL show a notification banner for 5 seconds

### Requirement 11: WebSocket Integration for Streaming

**User Story:** As a platform operator, I want the chat interface to use WebSocket for streaming responses, so that we provide real-time feedback without polling overhead.

#### Acceptance Criteria

1. THE Chat_Interface SHALL establish a WebSocket connection to `/api/v1/ai/ws` when opened
2. WHEN the WebSocket connection is established, THE Chat_Interface SHALL authenticate using JWT token
3. THE Chat_Interface SHALL automatically reconnect with exponential backoff (1s, 2s, 4s, 8s) if connection drops
4. WHEN the user sends a message, THE Chat_Interface SHALL transmit via WebSocket
5. THE Chat_Interface SHALL receive response chunks via WebSocket and display them incrementally
6. WHEN the Chat_Interface is closed, THE system SHALL gracefully disconnect the WebSocket
7. THE Chat_Interface SHALL handle WebSocket errors and display user-friendly error messages

### Requirement 12: Glassmorphism Visual Design

**User Story:** As a user, I want a modern, visually appealing chat interface, so that the experience feels premium and aligned with the BeatPush brand.

#### Acceptance Criteria

1. THE Chat_Interface SHALL use glassmorphism design with backdrop-blur effect
2. THE Chat_Interface background SHALL have 80% opacity with blur radius of 12px
3. THE Message_Bubbles SHALL have gradient borders (purple to blue) for AI messages
4. THE Message_Bubbles SHALL have solid background for user messages (aligned right)
5. THE Chat_Interface SHALL use smooth animations (300ms ease-in-out) for all transitions
6. THE Quick_Action_Buttons SHALL have hover effects with scale transform (1.05x)
7. THE Chat_Interface SHALL follow BeatPush color scheme: purple (#8B5CF6), blue (#3B82F6)

### Requirement 13: Error Handling and Retry Logic

**User Story:** As a user, I want clear error messages and retry options when AI requests fail, so that temporary issues don't prevent me from getting help.

#### Acceptance Criteria

1. WHEN an AI request fails, THE Chat_Interface SHALL display an error message in the conversation
2. THE error message SHALL include a "Retry" button that resends the failed message
3. WHEN the backend is unavailable (503), THE error message SHALL indicate "AI service temporarily unavailable"
4. WHEN rate limit is exceeded (429), THE error message SHALL show Upgrade_Prompt
5. WHEN the user's internet connection is lost, THE Chat_Interface SHALL display "Connection lost" banner
6. THE Chat_Interface SHALL automatically retry failed requests up to 2 times before showing error
7. THE error messages SHALL include timestamps and be dismissible

### Requirement 14: Accessibility Compliance

**User Story:** As a user with accessibility needs, I want the chat interface to be fully accessible via keyboard and screen readers, so that I can use AI features independently.

#### Acceptance Criteria

1. THE Chat_Interface SHALL be fully navigable using keyboard (Tab, Enter, Escape keys)
2. THE Chat_Interface SHALL trap focus within the interface when open
3. WHEN the Chat_Interface opens, THE system SHALL set focus to the message input field
4. THE Chat_Interface SHALL include ARIA labels on all interactive elements
5. THE Chat_Interface SHALL announce new AI messages to screen readers using aria-live regions
6. THE Chat_Interface SHALL support high contrast mode with visible focus indicators
7. THE Chat_Interface SHALL be WCAG 2.1 AA compliant

### Requirement 15: Integration with Existing useAI Hook

**User Story:** As a frontend developer, I want the chat interface to use the existing useAI hook, so that quota management and API calls are centralized and consistent.

#### Acceptance Criteria

1. THE Chat_Interface SHALL use the useAI hook from `@/hooks/useAI.ts` for all AI operations
2. THE Chat_Interface SHALL access quota status via `quota` property from useAI hook
3. THE Chat_Interface SHALL display loading state based on `loading` property from useAI hook
4. THE Chat_Interface SHALL handle errors using `error` property from useAI hook
5. THE Chat_Interface SHALL refresh quota after each successful request using `loadQuota()` method
6. THE Chat_Interface SHALL NOT make direct API calls to backend (all requests via useAI hook)

### Requirement 16: Beat Upload Page Integration

**User Story:** As a user uploading a beat, I want the AI chat to help me generate title, description, and tags without leaving the upload page, so that I can complete the upload process efficiently.

#### Acceptance Criteria

1. WHEN the user is on the beat upload page, THE Quick_Action_Buttons SHALL include: "Generate Title", "Write Description", "Suggest Tags", "Recommend Price"
2. WHEN the user clicks "Generate Title", THE Chat_Interface SHALL request beat genre, mood, and BPM if not already provided
3. WHEN title generation completes, THE Chat_Interface SHALL offer a "Use This Title" button that auto-fills the upload form
4. WHEN description generation completes, THE Chat_Interface SHALL offer a "Use This Description" button
5. THE Chat_Interface SHALL support multi-step interactions (e.g., "Tell me more about the beat first")
6. THE Context_Provider SHALL include uploaded file metadata (filename, duration, size) in prompts

### Requirement 17: Campaign Page Integration

**User Story:** As a user managing campaigns, I want the AI to analyze my campaign performance and suggest optimizations, so that I can improve results without hiring a marketing expert.

#### Acceptance Criteria

1. WHEN the user is on a campaign page, THE Quick_Action_Buttons SHALL include: "Analyze Performance", "Suggest Optimizations", "Generate Ad Copy"
2. WHEN the user clicks "Analyze Performance", THE Context_Provider SHALL include campaign metrics (reach, engagement, conversions)
3. THE Chat_Interface SHALL display performance insights with formatted lists and bold highlights
4. WHEN the user requests optimizations, THE Chat_Interface SHALL provide 3-5 actionable suggestions
5. THE Chat_Interface SHALL support follow-up questions about specific metrics
6. THE Context_Provider SHALL include campaign budget, duration, and target audience in prompts

### Requirement 18: Analytics Page Integration

**User Story:** As a user viewing analytics, I want the AI to explain trends and patterns in my data, so that I understand what's working and what needs improvement.

#### Acceptance Criteria

1. WHEN the user is on the analytics page, THE Quick_Action_Buttons SHALL include: "Explain Trends", "Compare Performance", "Get Recommendations"
2. WHEN the user clicks "Explain Trends", THE Context_Provider SHALL include chart data and time periods
3. THE Chat_Interface SHALL generate natural language explanations of data patterns
4. THE Chat_Interface SHALL highlight significant changes (e.g., "Your plays increased 45% this week")
5. WHEN the user requests comparisons, THE Chat_Interface SHALL compare current period to previous period
6. THE Context_Provider SHALL include revenue, plays, engagement rate, and growth metrics in prompts

### Requirement 19: Profile Page Integration

**User Story:** As a user editing my profile, I want the AI to help me write a compelling bio and artist statement, so that my profile attracts more followers and collaborators.

#### Acceptance Criteria

1. WHEN the user is on the profile page, THE Quick_Action_Buttons SHALL include: "Write Bio", "Craft Artist Statement", "Suggest Improvements"
2. WHEN the user clicks "Write Bio", THE Chat_Interface SHALL request information about music style, achievements, and goals
3. THE Chat_Interface SHALL generate 3 bio variations (short, medium, long)
4. WHEN bio generation completes, THE Chat_Interface SHALL offer a "Use This Bio" button that auto-fills the profile form
5. THE Context_Provider SHALL include existing profile data (genres, location, social links) in prompts
6. THE Chat_Interface SHALL support iterative refinement ("Make it more professional", "Add humor")

### Requirement 20: Social Media Caption Generation

**User Story:** As a user sharing content on social media, I want the AI to generate platform-specific captions, so that I can maintain consistent social presence without spending hours writing.

#### Acceptance Criteria

1. WHEN the user opens the share modal, THE Chat_Interface SHALL offer "Generate Caption" quick action
2. THE Chat_Interface SHALL generate captions for Instagram (2200 chars), Twitter (280 chars), and TikTok (150 chars)
3. THE Chat_Interface SHALL generate 5 caption variations with different tones (hype, professional, emotional, fun, mysterious)
4. THE Chat_Interface SHALL generate relevant hashtags separately from caption text
5. WHEN caption generation completes, THE Chat_Interface SHALL offer a "Use This Caption" button that auto-fills the share form
6. THE Context_Provider SHALL include content type (beat, post, achievement) and content metadata in prompts

## Technical Constraints

### WebSocket Requirements
- Must use existing WebSocket infrastructure at `/api/v1/ai/ws`
- Must authenticate WebSocket connections using JWT token from HTTP-only cookie or Authorization header
- Must handle WebSocket reconnection with exponential backoff
- Must close WebSocket connection when Chat_Interface is unmounted

### State Management
- Must use React Context or Zustand for chat state management
- Must persist conversation history in browser sessionStorage (not localStorage)
- Must clear sessionStorage on logout or session expiration
- Must limit sessionStorage to 5MB maximum

### Component Architecture
- Must create reusable components: ChatInterface, MessageBubble, QuickActionButton, TypingIndicator
- Must use Shadcn UI components for modals, buttons, and inputs
- Must follow atomic design principles (atoms, molecules, organisms)
- Must support lazy loading for improved performance

### Responsive Design
- Breakpoints: mobile (<768px), tablet (768-1024px), desktop (>1024px)
- Must use Tailwind CSS for all styling
- Must support landscape and portrait orientations on mobile
- Must test on iOS Safari, Android Chrome, and desktop browsers

### Performance Requirements
- Initial Chat_Interface render: <500ms
- Message send to response start: <800ms
- Streaming chunk display latency: <100ms
- Smooth 60fps animations for all transitions
- Memory usage: <50MB for conversation history

### Integration Requirements
- Must use useAI hook for all AI operations
- Must respect quota limits enforced by backend
- Must handle all error responses from backend (400, 401, 429, 500, 503)
- Must include request timeout of 30 seconds for AI generation

## User Experience Requirements

### Visual Design
- Gradient theme: Purple (#8B5CF6) to Blue (#3B82F6)
- Glassmorphism effects: backdrop-blur(12px), opacity 80%
- Border radius: 16px for Chat_Interface, 12px for Message_Bubbles
- Shadows: soft shadows for depth (0 4px 12px rgba(0,0,0,0.1))
- Typography: Inter font family, 16px base size, 1.5 line height

### Animation Specifications
- Slide-in animation: 300ms ease-in-out from right
- Message fade-in: 200ms ease-in
- Typing indicator pulse: 1.5s infinite
- Button hover scale: transform scale(1.05) 150ms ease
- Scroll animation: smooth behavior with 300ms duration

### Accessibility
- Color contrast ratio: minimum 4.5:1 (WCAG AA)
- Focus indicators: 2px solid ring with offset
- Touch targets: minimum 44x44px
- Screen reader announcements for all state changes
- Keyboard shortcuts: Ctrl/Cmd+K to open chat, Escape to close

### Mobile Optimizations
- Pull-to-refresh gesture support
- Swipe-down to close gesture
- Virtual keyboard handling (adjust layout when keyboard opens)
- Prevent body scroll when interface is open
- Haptic feedback on quick action button press (if supported)

## Integration Points

### Pages with Chat Integration
1. **Beat Upload Page** (`/beats/upload`)
   - Quick actions: Generate Title, Write Description, Suggest Tags, Recommend Price
   - Context: uploaded file metadata, selected genre, BPM input

2. **Beat Edit Page** (`/beats/[id]/edit`)
   - Quick actions: Improve Description, Add Tags, Suggest Price Changes
   - Context: existing beat data, performance metrics

3. **Campaign Dashboard** (`/campaigns/[id]`)
   - Quick actions: Analyze Performance, Suggest Optimizations, Generate Ad Copy
   - Context: campaign metrics, budget, target audience

4. **Analytics Page** (`/analytics`)
   - Quick actions: Explain Trends, Compare Performance, Get Recommendations
   - Context: revenue data, play counts, engagement rates

5. **Profile Page** (`/profile/edit`)
   - Quick actions: Write Bio, Craft Artist Statement, Suggest Improvements
   - Context: existing profile data, genres, achievements

6. **Social Feed** (`/feed`)
   - Quick actions: Generate Caption, Suggest Hashtags
   - Context: post content, images, links

7. **Messaging** (`/messages`)
   - Quick actions: Suggest Reply, Write Professional Message
   - Context: conversation history, message thread

### Backend API Dependencies
- `POST /api/v1/ai/generate` - REST endpoint for one-shot AI requests
- `WS /api/v1/ai/ws` - WebSocket endpoint for streaming responses
- `GET /api/v1/ai/quota` - Fetch current quota status
- `GET /api/v1/users/me` - Get current user tier (free/premium)

### Frontend Dependencies
- `useAI` hook from `@/hooks/useAI.ts`
- Shadcn UI components (Button, Modal, Tooltip, ScrollArea)
- Markdown renderer library (react-markdown or similar)
- WebSocket client library (native WebSocket API)
- Clipboard API (native browser API)

## Privacy and Security

### Data Handling
- Must NOT send sensitive data (passwords, payment info, tokens) to AI
- Must sanitize user inputs to prevent prompt injection
- Must filter AI responses for inappropriate content
- Must log all AI interactions for abuse monitoring
- Must comply with GDPR for conversation data storage

### Authentication
- Must require authenticated users for all AI operations
- Must validate JWT tokens on every WebSocket message
- Must handle token expiration gracefully (show login prompt)
- Must enforce rate limits at both frontend and backend

### Content Safety
- Must filter profanity and offensive language from AI responses
- Must reject user inputs containing malicious prompts
- Must provide user reporting mechanism for inappropriate AI responses
- Must maintain audit logs for content moderation
