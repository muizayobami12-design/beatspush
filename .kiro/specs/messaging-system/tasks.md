# Implementation Plan: Messaging System

## Overview

This implementation plan breaks down the messaging system for BeatPush into discrete, actionable coding tasks. The system enables direct communication between users with real-time messaging, file attachments, privacy controls, and blocking functionality. Implementation follows a bottom-up approach: database schema → backend models and services → API endpoints → WebSocket real-time features → frontend components.

**Tech Stack:**
- Backend: Python with FastAPI, SQLAlchemy ORM, PostgreSQL
- Frontend: Next.js with TypeScript
- Real-Time: WebSockets (FastAPI native WebSocket support)
- File Storage: Existing FileStorageService (Cloudflare R2/S3)
- Caching: Redis for performance optimization

**Key Features:**
- Direct messaging between users with pagination
- File attachments (images, audio, documents, voice notes)
- Message requests for non-followers
- Privacy controls and message filtering
- User blocking with conversation hiding
- Real-time delivery with WebSocket
- Read receipts and typing indicators
- Message search and filtering
- Notification integration

## Tasks

- [x] 1. Database Schema Setup
  - [x] 1.1 Create Alembic migration for messaging tables
    - Create migration file with all messaging-related tables: `conversations`, `conversation_participants`, `messages`, `message_read_receipts`, `message_attachments`, `blocked_users`, `message_reports`, `user_message_settings`
    - Add all indexes for query performance (conversation list, message pagination, unread counts, block checks, search)
    - Add foreign key constraints with appropriate cascade behaviors
    - Add check constraints for content length (2000 chars), file sizes, enum values
    - Test migration up/down without data loss
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 4.1, 4.6, 5.1, 5.2, 6.1, 6.6_

- [x] 2. Backend Data Models (SQLAlchemy)
  - [x] 2.1 Create Conversation and ConversationParticipant models
    - Implement `Conversation` model with fields: id, created_at, updated_at, last_activity_at, last_message_preview, is_message_request, request_status
    - Implement `ConversationParticipant` model with fields: id, conversation_id, user_id, joined_at, left_at, unread_count, last_read_at, is_archived, is_muted
    - Define SQLAlchemy relationships between Conversation, ConversationParticipant, Message, and User
    - Add model methods for common operations (get_other_participant, is_participant, etc.)
    - _Requirements: 1.1, 1.2, 1.3, 1.7, 1.8_
  
  - [x] 2.2 Create Message and MessageReadReceipt models
    - Implement `Message` model with fields: id, conversation_id, sender_id, content, created_at, updated_at, deleted_at, is_edited
    - Add AI feature fields: language_code, spam_score, ai_processed, smart_reply_suggestions (for future use)
    - Implement `MessageReadReceipt` model with fields: id, message_id, user_id, read_at
    - Define relationships between Message, MessageReadReceipt, MessageAttachment, and User
    - Add validation for content length and sanitization
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.9, 3.1, 3.2, 3.3, 9.1, 9.2, 9.3, 9.4, 9.6_
  
  - [x] 2.3 Create MessageAttachment model
    - Implement `MessageAttachment` model with fields: id, message_id, file_type, original_filename, storage_url, file_size, mime_type, duration, width, height, thumbnail_url
    - Add relationship to Message model
    - Add file type enum: image, audio, document, voice_note
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6, 4.7, 4.8, 4.9_
  
  - [x] 2.4 Create BlockedUser model
    - Implement `BlockedUser` model with fields: id, blocker_id, blocked_id, blocked_at, reason
    - Add unique constraint on (blocker_id, blocked_id)
    - Define relationships to User model (blocker and blocked foreign keys)
    - _Requirements: 6.1, 6.2, 6.4_
  
  - [x] 2.5 Create MessageReport and UserMessageSettings models
    - Implement `MessageReport` model with fields: id, message_id, reporter_id, reason, details, created_at, reviewed, reviewed_at, reviewed_by, action_taken
    - Add reason enum: spam, harassment, inappropriate, other
    - Implement `UserMessageSettings` model with fields: id, user_id, message_filter, read_receipts_enabled, typing_indicators_enabled
    - Add message_filter enum: everyone, followers, verified, none
    - _Requirements: 5.6, 5.7, 5.9, 6.6, 6.7, 6.8, 6.9_

- [x] 3. Pydantic Schemas (Request/Response DTOs)
  - [x] 3.1 Create message request/response schemas
    - Implement `SendMessageRequest` with validation: recipient_id or conversation_id (one required), content (1-2000 chars, stripped)
    - Implement `UpdateMessageRequest` with content validation
    - Implement `MessageResponse` with fields: id, conversation_id, sender_id, sender (UserBasicInfo), content, created_at, updated_at, is_edited, read_by, attachments
    - Implement `MessageListResponse` with pagination: messages, has_more, next_cursor
    - _Requirements: 2.1, 2.2, 2.4, 2.8, 2.9_
  
  - [x] 3.2 Create conversation request/response schemas
    - Implement `CreateConversationRequest` with recipient_id validation (UUID format)
    - Implement `LastMessagePreview` with fields: id, content, sender_id, created_at, has_attachment
    - Implement `ConversationResponse` with fields: id, participants, last_message, unread_count, is_message_request, request_status, last_activity_at, is_archived, is_muted
    - Implement `ConversationListResponse` with pagination: conversations, total, page, page_size, total_pages
    - _Requirements: 1.1, 1.3, 1.4, 1.7, 1.8, 1.9_
  
  - [x] 3.3 Create privacy and settings schemas
    - Implement `UpdateSettingsRequest` with optional fields: message_filter, read_receipts_enabled, typing_indicators_enabled
    - Implement `SettingsResponse` matching UserMessageSettings model fields
    - Implement `BlockUserRequest` with user_id and optional reason (max 500 chars)
    - Implement `ReportMessageRequest` with reason enum validation and details (max 500 chars)
    - Implement `AttachmentResponse` with all file metadata fields
    - _Requirements: 4.6, 4.9, 5.6, 5.9, 6.1, 6.6, 6.7, 6.8_

- [x] 4. Core MessagingService Implementation
  - [x] 4.1 Implement conversation management methods
    - Write `get_or_create_conversation(user_id, recipient_id)` that checks for existing conversation or creates new one
    - Write `list_conversations(user_id, page, page_size, unread_only, search)` with pagination and filtering
    - Write `get_conversation(conversation_id, user_id)` with access control verification
    - Write `search_conversations(user_id, query, page)` using case-insensitive partial matching on participant names
    - Implement query optimization with joins and denormalized data
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.7, 1.9, 8.1, 8.6, 8.8_
  
  - [x] 4.2 Implement message sending and retrieval methods
    - Write `send_message(sender_id, recipient_id, content, conversation_id)` with validation and privacy checks
    - Write `get_messages(conversation_id, user_id, page, page_size, cursor)` with cursor-based pagination
    - Write `get_messages_since(conversation_id, user_id, since_timestamp)` for polling fallback
    - Write `search_messages(user_id, query, page)` with case-insensitive content matching
    - Update conversation `last_activity_at` and `last_message_preview` on new message
    - _Requirements: 1.4, 1.5, 1.6, 2.1, 2.2, 2.4, 2.8, 2.9, 8.2, 8.5, 11.4_
  
  - [x] 4.3 Implement read receipts and message status methods
    - Write `mark_message_read(message_id, user_id)` to create read receipt with timestamp
    - Write `mark_conversation_read(conversation_id, user_id)` to mark all unread messages as read
    - Write `get_unread_count(user_id, conversation_id)` for specific conversation
    - Write `get_total_unread_count(user_id)` across all conversations
    - Update `ConversationParticipant.unread_count` when messages are read
    - Handle read receipt visibility based on user settings (read_receipts_enabled)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [x] 4.4 Implement message editing and deletion
    - Write `edit_message(message_id, user_id, new_content)` with 15-minute time window check and sender verification
    - Set `is_edited` flag and `updated_at` timestamp on edit
    - Write `delete_message(message_id, user_id)` for soft delete (set deleted_at timestamp)
    - Replace deleted message content with "[Message deleted]" in responses
    - _Requirements: 2.1, 2.2_

- [x] 5. PrivacyService Implementation
  - [x] 5.1 Implement privacy settings management
    - Write `get_user_settings(user_id)` to retrieve or create default settings
    - Write `update_user_settings(user_id, settings_dict)` to update message_filter, read_receipts_enabled, typing_indicators_enabled
    - Create default settings on user registration: message_filter=everyone, read_receipts_enabled=true, typing_indicators_enabled=true
    - _Requirements: 5.9_
  
  - [x] 5.2 Implement message request logic
    - Write `should_create_message_request(sender_id, recipient_id)` that checks: existing conversation, block status, recipient's message_filter setting
    - Handle filters: everyone (no request), followers (check social graph), verified (check sender.is_verified), none (reject)
    - Return boolean indicating if message request needed
    - Write `accept_message_request(conversation_id, user_id)` to update request_status to 'accepted'
    - Write `decline_message_request(conversation_id, user_id)` to update request_status to 'declined'
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.10_
  
  - [x] 5.3 Implement blocking functionality
    - Write `block_user(blocker_id, blocked_id, reason)` to create BlockedUser record
    - Find all conversations between users and set `left_at` timestamp for both participants (soft hide)
    - Write `unblock_user(blocker_id, blocked_id)` to delete BlockedUser record and clear `left_at` timestamps
    - Write `is_blocked(user_id, target_id)` to check if block exists in either direction
    - Write `get_blocked_users(user_id, page)` with pagination
    - Write `can_send_message(sender_id, recipient_id)` returning (bool, error_message)
    - _Requirements: 2.6, 2.7, 6.1, 6.2, 6.3, 6.4, 6.5, 6.10_
  
  - [x] 5.4 Implement message reporting
    - Write `report_message(reporter_id, message_id, reason, details)` to create MessageReport record
    - Validate reason enum: spam, harassment, inappropriate, other
    - Store report without notifying reported user
    - _Requirements: 6.6, 6.7, 6.8, 6.9_

- [x] 6. FileAttachmentService Implementation
  - [x] 6.1 Create file validation and configuration
    - Define `ATTACHMENT_CONFIG` dict with file types (image, audio, document, voice_note), allowed extensions, max sizes, and mime types
    - Write `validate_file_upload(file, file_type)` checking: extension, MIME type, file size
    - Raise HTTPException with specific error details on validation failure
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.10_
  
  - [x] 6.2 Implement file upload and storage
    - Write `upload_message_attachment(file, message_id, file_type)` integrating with existing FileStorageService
    - Generate unique filename and storage path: `messages/{message_id}/{filename}`
    - Upload file to Cloudflare R2/S3 and get storage URL
    - Extract metadata: file_size, mime_type
    - For images: extract dimensions (width, height) and generate thumbnail (200x200, <50KB)
    - For audio: extract duration in seconds
    - Return AttachmentResponse with all metadata
    - _Requirements: 4.5, 4.6, 4.7, 4.8, 4.9, 11.9_
  
  - [x] 6.3 Implement file deletion and cleanup
    - Write `delete_message_attachment(attachment_id)` to remove file from storage
    - Delete both main file and thumbnail for images
    - Handle storage errors gracefully
    - _Requirements: 4.5_

- [x] 7. WebSocket Connection Manager Implementation
  - [x] 7.1 Create ConnectionManager class
    - Create `ConnectionManager` class with dictionaries: `active_connections` (user_id → list of WebSocket), `active_conversations` (conversation_id → set of user_ids), `typing_timers` (conversation_user_key → asyncio.Task)
    - Write `connect(user_id, websocket)` to accept connection and add to active_connections
    - Write `disconnect(user_id, websocket)` to remove connection and clean up if no more connections
    - Write `send_to_user(user_id, message_dict)` to send JSON to all user's connections
    - Write `broadcast_to_conversation(conversation_id, message_dict, exclude_user)` to send to all participants
    - _Requirements: 7.4, 7.6_
  
  - [x] 7.2 Implement typing indicator handling
    - Write `handle_typing_indicator(user_id, conversation_id, is_typing)` that broadcasts to conversation participants
    - Implement auto-timeout: cancel existing timer, broadcast typing status, create new 3-second timer if is_typing=true
    - Write `_typing_timeout(user_id, conversation_id, key)` async task that waits 3 seconds and broadcasts is_typing=false
    - Cancel typing indicator when message sent
    - _Requirements: 7.1, 7.2, 7.3, 7.8_
  
  - [x] 7.3 Implement message broadcasting
    - Write `broadcast_new_message(conversation_id, message)` to send new_message event to all participants
    - Write `broadcast_read_receipt(message_id, user_id, read_at)` to send message_read event to message sender
    - Write `broadcast_user_status(user_id, status)` for online/offline events
    - Handle WebSocket send failures gracefully (dead connections)
    - _Requirements: 7.6_

- [x] 8. REST API Endpoints - Conversations
  - [x] 8.1 Implement GET /api/v1/conversations endpoint
    - Create endpoint with query params: page, page_size, unread_only, search
    - Authenticate with existing get_current_user dependency
    - Call MessagingService.list_conversations() with parameters
    - Return ConversationListResponse with pagination metadata
    - Apply rate limit: 60 requests per minute
    - _Requirements: 1.7, 1.8, 1.9, 8.1, 8.3, 8.4, 8.6, 8.7_
  
  - [-] 8.2 Implement POST /api/v1/conversations endpoint
    - Create endpoint accepting CreateConversationRequest (recipient_id)
    - Authenticate current user
    - Check if conversation already exists or create new one via MessagingService
    - Check if message request needed via PrivacyService
    - Return ConversationResponse with appropriate is_message_request flag
    - _Requirements: 1.1, 1.2, 5.1, 5.2_
  
  - [-] 8.3 Implement GET /api/v1/conversations/{conversation_id} endpoint
    - Create endpoint with conversation_id path parameter
    - Authenticate and verify user has access to conversation
    - Return ConversationResponse with full details
    - _Requirements: 1.2, 1.3_
  
  - [-] 8.4 Implement DELETE /api/v1/conversations/{conversation_id} endpoint
    - Create endpoint for soft deleting conversation
    - Set left_at timestamp for current user in conversation_participants
    - Return success response
    - _Requirements: 1.9_

- [ ] 9. REST API Endpoints - Messages
  - [~] 9.1 Implement GET /api/v1/conversations/{conversation_id}/messages endpoint
    - Create endpoint with query params: page, page_size, cursor, before, after
    - Verify user has access to conversation
    - Call MessagingService.get_messages() with cursor-based pagination
    - Return MessageListResponse with messages ordered by created_at ASC
    - Support infinite scroll with next_cursor
    - _Requirements: 1.4, 1.5, 2.8, 11.3, 11.4_
  
  - [~] 9.2 Implement POST /api/v1/messages endpoint
    - Create endpoint accepting SendMessageRequest (recipient_id or conversation_id, content)
    - Authenticate current user as sender
    - Validate message content: sanitize HTML, check length (1-2000 chars)
    - Check privacy rules: can_send_message via PrivacyService
    - Call MessagingService.send_message()
    - Broadcast message via WebSocketManager if recipient online
    - Trigger notification via NotificationService for offline/inactive users
    - Apply rate limit: 30 messages per minute
    - Return MessageResponse with 201 status
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 10.1, 10.2_
  
  - [~] 9.3 Implement PUT /api/v1/messages/{message_id} endpoint
    - Create endpoint accepting UpdateMessageRequest (content)
    - Verify current user is message sender
    - Check message age (must be within 15 minutes)
    - Call MessagingService.edit_message()
    - Broadcast update via WebSocket
    - Return updated MessageResponse
    - _Requirements: 2.1, 2.2_
  
  - [~] 9.4 Implement DELETE /api/v1/messages/{message_id} endpoint
    - Create endpoint for soft deleting message
    - Verify current user is message sender
    - Call MessagingService.delete_message()
    - Broadcast deletion via WebSocket
    - Return success response
    - _Requirements: 2.1_
  
  - [~] 9.5 Implement POST /api/v1/messages/{message_id}/read endpoint
    - Create endpoint to mark message as read
    - Verify user is conversation participant
    - Call MessagingService.mark_message_read()
    - Broadcast read receipt via WebSocket if sender has read_receipts_enabled
    - Return success response
    - _Requirements: 3.1, 3.2, 3.6, 3.7_
  
  - [~] 9.6 Implement POST /api/v1/messages/{message_id}/attachments endpoint
    - Create endpoint accepting multipart file upload
    - Verify user owns the message
    - Validate file via FileAttachmentService
    - Upload file and create MessageAttachment record
    - Apply rate limit: 10 uploads per minute
    - Return AttachmentResponse
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.9, 4.10_
  
  - [~] 9.7 Implement GET /api/v1/conversations/{conversation_id}/poll endpoint
    - Create polling fallback endpoint with since timestamp parameter
    - Return new messages since timestamp and typing users
    - Support clients without WebSocket capability
    - _Requirements: 7.5, 7.7_

- [ ] 10. REST API Endpoints - Message Requests
  - [-] 10.1 Implement GET /api/v1/message-requests endpoint
    - Create endpoint with pagination: page, page_size
    - Filter conversations where is_message_request=true and request_status='pending'
    - Return ConversationListResponse
    - _Requirements: 5.2_
  
  - [~] 10.2 Implement POST /api/v1/message-requests/{conversation_id}/accept endpoint
    - Create endpoint to accept message request
    - Verify current user is recipient
    - Call PrivacyService.accept_message_request()
    - Notify sender via NotificationService
    - Return updated ConversationResponse
    - _Requirements: 5.3, 5.4_
  
  - [~] 10.3 Implement POST /api/v1/message-requests/{conversation_id}/decline endpoint
    - Create endpoint to decline message request
    - Verify current user is recipient
    - Call PrivacyService.decline_message_request()
    - Return success response
    - _Requirements: 5.3, 5.5_

- [ ] 11. REST API Endpoints - Privacy and Blocking
  - [ ] 11.1 Implement GET /api/v1/messaging/settings endpoint
    - Create endpoint to retrieve user's message settings
    - Call PrivacyService.get_user_settings()
    - Return SettingsResponse
    - _Requirements: 5.9_
  
  - [~] 11.2 Implement PUT /api/v1/messaging/settings endpoint
    - Create endpoint accepting UpdateSettingsRequest
    - Call PrivacyService.update_user_settings()
    - Return updated SettingsResponse
    - _Requirements: 5.9_
  
  - [~] 11.3 Implement POST /api/v1/messaging/block endpoint
    - Create endpoint accepting BlockUserRequest (user_id, reason)
    - Verify not blocking self
    - Call PrivacyService.block_user()
    - Return success response
    - _Requirements: 6.1, 6.2, 6.3, 6.10_
  
  - [~] 11.4 Implement DELETE /api/v1/messaging/block/{user_id} endpoint
    - Create endpoint to unblock user
    - Call PrivacyService.unblock_user()
    - Return success response
    - _Requirements: 6.4, 6.5_
  
  - [~] 11.5 Implement GET /api/v1/messaging/blocked-users endpoint
    - Create endpoint with pagination
    - Call PrivacyService.get_blocked_users()
    - Return list of BlockedUserResponse
    - _Requirements: 6.1, 6.2_
  
  - [~] 11.6 Implement POST /api/v1/messages/{message_id}/report endpoint
    - Create endpoint accepting ReportMessageRequest (reason, details)
    - Validate reason enum
    - Call PrivacyService.report_message()
    - Return success response
    - _Requirements: 6.6, 6.7, 6.8, 6.9_

- [ ] 12. WebSocket Endpoint Implementation
  - [~] 12.1 Create WebSocket authentication dependency
    - Write `get_current_user_ws(websocket)` dependency function
    - Extract JWT token from query parameter or header
    - Decode and validate token
    - Close connection with WS_1008_POLICY_VIOLATION code if authentication fails
    - Return authenticated user
    - _Requirements: 7.4_
  
  - [~] 12.2 Implement WebSocket endpoint WS /ws/conversations
    - Create WebSocket endpoint at `/ws/conversations`
    - Authenticate via get_current_user_ws dependency
    - Register connection with ConnectionManager.connect()
    - Handle incoming events in loop: typing_start, typing_stop, join_conversation, leave_conversation
    - Dispatch events to appropriate ConnectionManager methods
    - Catch exceptions gracefully and log errors
    - On disconnect or error, call ConnectionManager.disconnect()
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.6_
  
  - [~] 12.3 Implement WebSocket rate limiting
    - Create `RateLimitedWebSocketManager` extending ConnectionManager
    - Add `message_counts` and `typing_counts` dictionaries tracking timestamps per user
    - Write `check_rate_limit(user_id, action, limit, window)` method
    - Apply limits: 60 messages per minute, 20 typing indicators per minute
    - Disconnect user if rate limit exceeded repeatedly
    - _Requirements: 7.1, 7.2_

- [ ] 13. Notification Integration
  - [~] 13.1 Integrate with existing NotificationService
    - Write helper function `create_message_notification(message, recipient_id)`
    - Call NotificationService with: type='new_message', sender_username, message_preview (first 50 chars), conversation_id
    - Write helper function `create_message_request_notification(conversation, recipient_id)`
    - Implement notification batching: if multiple unread messages in same conversation within 5 minutes, send single batched notification
    - Check user notification preferences via NotificationService
    - Skip notification if user is actively viewing the conversation (tracked in ConnectionManager.active_conversations)
    - Never send notification for user's own messages
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_

- [ ] 14. Performance Optimizations
  - [~] 14.1 Implement Redis caching layer
    - Create `MessagingCache` class with Redis client
    - Write methods: `cache_conversation()`, `get_conversation()`, `invalidate_conversation()`, `cache_user_settings()`, `get_unread_count()`, `increment_unread()`, `reset_unread()`
    - Set appropriate TTLs: conversations (5 min), settings (1 hour), unread counts (invalidate on read)
    - Integrate cache checks in MessagingService and PrivacyService
    - Invalidate cache on updates
    - _Requirements: 11.1, 11.7_
  
  - [~] 14.2 Add database query optimizations
    - Add indexes to migration: `idx_conv_participants_user_active`, `idx_messages_conv_created`, `idx_participants_unread`, `idx_blocks_both`, `idx_messages_content_gin` (GIN for full-text search)
    - Optimize conversation list query with joins and WHERE clauses
    - Use denormalized data: last_message_preview in conversations table
    - Implement cursor-based pagination for messages (avoid offset)
    - _Requirements: 11.1, 11.2, 11.3, 11.5, 11.6, 11.7, 11.8_
  
  - [~] 14.3 Implement bandwidth optimizations
    - Create minimal WebSocket message payload with shortened keys (id, cid, s, c, t, a)
    - Implement image optimization: generate 200x200 thumbnail (<50KB) and optimized full image (<500KB)
    - Implement audio compression: create 64kbps preview and full quality versions
    - Add support for resumable file uploads using chunked upload
    - _Requirements: 11.9, 11.10_

- [ ] 15. Security Implementation
  - [~] 15.1 Implement input validation and sanitization
    - Write `sanitize_message_content(content)` using bleach: strip HTML tags, escape entities, trim whitespace, validate length
    - Integrate sanitization in SendMessageRequest validation
    - Add file validation for malicious content (optional ClamAV integration)
    - _Requirements: 2.4, 4.1_
  
  - [~] 15.2 Implement access control and authorization
    - Write `verify_conversation_access(conversation_id, user_id)` checking conversation_participants table
    - Apply access check in all conversation and message endpoints
    - Verify message sender for edit/delete operations
    - Enforce block rules at API layer before service calls
    - _Requirements: 1.9, 2.6, 2.7_
  
  - [~] 15.3 Add rate limiting to API endpoints
    - Install and configure slowapi rate limiter
    - Apply limits: 30/min for POST /messages, 10/min for file uploads, 60/min for GET /conversations
    - Return 429 Too Many Requests with Retry-After header
    - _Requirements: 2.5_
  
  - [~] 15.4 Implement error handling and logging
    - Create `ErrorResponse` Pydantic model with fields: error, detail, code, timestamp, request_id
    - Define `MessageError` enum with error codes: BLOCKED_USER, USER_NOT_ACCEPTING_MESSAGES, CONVERSATION_NOT_FOUND, etc.
    - Add exception handlers for HTTPException and general Exception
    - Implement `websocket_error_handler()` for graceful WebSocket errors
    - Add structured logging (never log message content in production)
    - Redact sensitive data in error traces
    - _Requirements: 2.6, 2.7, 4.10, 6.10_

- [~] 16. Checkpoint - Backend Complete
  - Ensure all backend tests pass, verify API endpoints with Postman/Insomnia, check WebSocket connections, ask user if questions arise.

- [ ] 17. Frontend - Conversation List Component
  - [~] 17.1 Create ConversationList component
    - Create Next.js component: `components/messaging/ConversationList.tsx`
    - Fetch conversations from GET /api/v1/conversations with pagination
    - Display conversation items with: participant avatar, name, last message preview, timestamp, unread count badge
    - Implement infinite scroll pagination (load more on scroll)
    - Add search input for filtering conversations
    - Add filter toggle for unread-only view
    - Handle loading, empty, and error states
    - _Requirements: 1.7, 1.8, 8.1, 8.3, 8.4, 8.6_
  
  - [~] 17.2 Create ConversationListItem component
    - Extract conversation item to separate component: `ConversationListItem.tsx`
    - Display participant info, last message text, timestamp (formatted relative time)
    - Show unread count badge if unread_count > 0
    - Show "Message Request" badge if is_message_request=true
    - Add visual indicator for archived/muted conversations
    - Make clickable to open conversation thread
    - _Requirements: 1.7, 1.8, 5.1, 5.2_

- [ ] 18. Frontend - Message Thread Component
  - [~] 18.1 Create MessageThread component
    - Create component: `components/messaging/MessageThread.tsx`
    - Fetch messages from GET /api/v1/conversations/{id}/messages with cursor-based pagination
    - Display messages in chronological order (oldest to newest)
    - Group messages by sender with avatar
    - Show message content, timestamp, edited indicator, read receipts
    - Implement "Load older messages" button for pagination
    - Auto-scroll to bottom on new message
    - _Requirements: 1.4, 1.5, 2.8, 3.6, 11.4_
  
  - [~] 18.2 Create MessageBubble component
    - Extract message bubble to component: `MessageBubble.tsx`
    - Render different styles for sent vs received messages
    - Display message content with proper text wrapping
    - Show timestamp on hover or below message
    - Show "Edited" label if is_edited=true
    - Display read receipt checkmarks for sent messages (single check=delivered, double check=read)
    - Show attachment previews (thumbnails for images, player for audio)
    - Add context menu for edit/delete (show for own messages only)
    - _Requirements: 2.8, 3.6, 4.9_
  
  - [~] 18.3 Create MessageInput component
    - Create component: `MessageInput.tsx` with textarea
    - Implement auto-resize textarea (grows with content)
    - Add character counter (0/2000)
    - Add file attachment button with icon
    - Send message on Enter (Shift+Enter for new line)
    - Clear input after send
    - Show loading state during send
    - _Requirements: 2.1, 2.4_
  
  - [~] 18.4 Implement typing indicator display
    - Add typing indicator UI: "User is typing..." with animated dots
    - Display at bottom of message thread
    - Show/hide based on WebSocket typing_indicator events
    - Handle multiple users typing: "User1 and User2 are typing..."
    - _Requirements: 7.1, 7.2_

- [ ] 19. Frontend - WebSocket Integration
  - [~] 19.1 Create WebSocket hook and context
    - Create React hook: `hooks/useWebSocket.ts`
    - Establish WebSocket connection to /ws/conversations with JWT token
    - Create WebSocket context provider for global connection management
    - Handle connection, disconnection, and reconnection logic
    - Implement exponential backoff for reconnection attempts
    - _Requirements: 7.4_
  
  - [~] 19.2 Implement WebSocket event handling
    - Create `useMessagingEvents(conversationId)` hook
    - Listen for WebSocket events: new_message, typing_indicator, message_read, user_online, user_offline
    - Update local state on new_message: append to message list, update conversation last_activity
    - Update typing state on typing_indicator events
    - Update read receipts on message_read events
    - _Requirements: 7.1, 7.6_
  
  - [~] 19.3 Implement typing indicator sending
    - Send typing_start event when user begins typing in MessageInput
    - Send typing_stop event when user stops typing for 3 seconds or sends message
    - Debounce typing events to avoid excessive WebSocket traffic
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [~] 19.4 Implement polling fallback
    - Detect WebSocket connection failure
    - Fall back to polling GET /api/v1/conversations/{id}/poll every 3 seconds
    - Display "Offline mode" indicator in UI
    - Switch back to WebSocket when connection restored
    - _Requirements: 7.5, 7.7_

- [ ] 20. Frontend - File Attachments
  - [~] 20.1 Create FileUpload component
    - Create component: `FileUpload.tsx` with file input
    - Support drag-and-drop and click-to-browse
    - Validate file type and size on client side before upload
    - Show upload progress bar
    - Preview selected file before sending (thumbnail for images)
    - Upload via POST /api/v1/messages/{id}/attachments
    - Handle upload errors with user-friendly messages
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.10_
  
  - [~] 20.2 Create AttachmentPreview component
    - Create component: `AttachmentPreview.tsx`
    - Display image attachments with thumbnail and lightbox for full view
    - Display audio attachments with inline player (play/pause, progress bar, duration)
    - Display document attachments with icon and download button
    - Display voice notes with waveform visualization (optional) and player
    - Show file size and original filename
    - _Requirements: 4.6, 4.8, 4.9_
  
  - [~] 20.3 Implement voice note recording
    - Create component: `VoiceNoteRecorder.tsx`
    - Use browser MediaRecorder API to capture audio
    - Show recording timer and waveform visualization during recording
    - Add stop/cancel buttons
    - Save recorded audio as file and upload via FileUpload component
    - Handle browser permission requests for microphone access
    - _Requirements: 4.8_

- [ ] 21. Frontend - Message Requests
  - [~] 21.1 Create MessageRequests component
    - Create component: `MessageRequests.tsx`
    - Fetch pending message requests from GET /api/v1/message-requests
    - Display list of requests with sender info and first message preview
    - Add "Accept" and "Decline" buttons for each request
    - Call POST /api/v1/message-requests/{id}/accept or decline endpoints
    - Remove request from list after action
    - Show empty state if no pending requests
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [~] 21.2 Add message request indicator to ConversationList
    - Show "Message Requests" section at top of conversation list
    - Display count badge: "Message Requests (3)"
    - Navigate to MessageRequests component on click
    - _Requirements: 5.1, 5.2_

- [ ] 22. Frontend - Privacy Settings
  - [~] 22.1 Create MessagingSettings component
    - Create settings page: `pages/settings/messaging.tsx`
    - Fetch settings from GET /api/v1/messaging/settings
    - Display form with: message_filter dropdown (everyone, followers, verified, none), read_receipts_enabled toggle, typing_indicators_enabled toggle
    - Save changes via PUT /api/v1/messaging/settings
    - Show success/error feedback
    - _Requirements: 5.6, 5.7, 5.9, 3.6, 3.7_
  
  - [~] 22.2 Create BlockedUsers component
    - Create component: `BlockedUsers.tsx`
    - Fetch blocked users from GET /api/v1/messaging/blocked-users
    - Display list with avatar, name, blocked date, reason
    - Add "Unblock" button for each user
    - Call DELETE /api/v1/messaging/block/{user_id} on unblock
    - Show confirmation dialog before unblocking
    - _Requirements: 6.1, 6.2, 6.4, 6.5_
  
  - [~] 22.3 Implement block and report actions
    - Add "Block" and "Report" options to message context menu and conversation header
    - Create BlockUserModal with reason input
    - Create ReportMessageModal with reason dropdown and details textarea
    - Call POST /api/v1/messaging/block and POST /api/v1/messages/{id}/report
    - Show confirmation feedback
    - Hide conversation immediately after blocking
    - _Requirements: 6.1, 6.3, 6.6, 6.7, 6.8, 6.10_

- [ ] 23. Frontend - Search and Filtering
  - [~] 23.1 Implement conversation search
    - Add search input to ConversationList header
    - Debounce search input (500ms)
    - Call GET /api/v1/conversations?search={query}
    - Highlight matching participant names in results
    - Show "No results" state
    - Clear search button (X icon)
    - _Requirements: 8.1, 8.5, 8.6, 8.8_
  
  - [~] 23.2 Implement message search
    - Add "Search in conversation" feature to MessageThread
    - Create SearchMessages component with search input
    - Call GET endpoint for message search (implement backend endpoint if needed)
    - Highlight matching messages in thread
    - Show count of results
    - Navigate between matches with prev/next buttons
    - _Requirements: 8.2, 8.5_
  
  - [~] 23.3 Add conversation filters
    - Add filter chips to ConversationList: All, Unread, Message Requests, Archived
    - Update API call based on selected filter
    - Show active filter visually
    - _Requirements: 8.3, 8.4, 5.2_

- [ ] 24. Frontend - Read Receipts and Status
  - [~] 24.1 Implement read receipt tracking
    - Mark conversation as read when user opens MessageThread
    - Call POST /api/v1/messages/{id}/read for each unread message
    - Update local unread_count in conversation list
    - Clear unread badge in ConversationList
    - _Requirements: 3.1, 3.4, 3.5_
  
  - [~] 24.2 Display read receipts on messages
    - Show checkmark indicators on sent MessageBubbles: single check (delivered), double check (read)
    - Update checkmark when read_by list includes recipient
    - Respect sender's read_receipts_enabled setting (hide if disabled)
    - _Requirements: 3.3, 3.6, 3.7_
  
  - [~] 24.3 Show online/offline status
    - Display status indicator (green dot) on participant avatar if online
    - Update based on WebSocket user_online/user_offline events
    - Show "Last active" timestamp for offline users
    - _Requirements: 7.6_

- [ ] 25. Frontend - Responsive Design and Mobile
  - [~] 25.1 Implement responsive layout
    - Create mobile-first responsive design for messaging interface
    - On mobile: show conversation list OR message thread (toggle with back button)
    - On tablet/desktop: show split view with conversation list (30%) and message thread (70%)
    - Make all components touch-friendly (larger tap targets)
    - Test on various screen sizes: mobile (320px+), tablet (768px+), desktop (1024px+)
  
  - [~] 25.2 Optimize for low bandwidth
    - Implement lazy loading for images (load on scroll into view)
    - Show low-res thumbnails first, load full resolution on click
    - Add "Download" option for large files instead of auto-loading
    - Compress images before upload on client side
    - Show data usage indicator
    - _Requirements: 11.9_
  
  - [~] 25.3 Add progressive web app features
    - Enable service worker for offline message queue
    - Cache conversation list for offline viewing
    - Queue messages when offline and send when connection restored
    - Show "Offline" badge in UI when disconnected
    - Add push notification support for new messages (via NotificationService)

- [ ] 26. Frontend - Message Editing and Deletion
  - [~] 26.1 Implement message editing UI
    - Add "Edit" option to message context menu (own messages only)
    - Show edit mode in MessageInput with current message content
    - Call PUT /api/v1/messages/{id} with new content
    - Show "Edited" label on edited messages
    - Disable editing if message older than 15 minutes
    - _Requirements: 2.1, 2.2_
  
  - [~] 26.2 Implement message deletion UI
    - Add "Delete" option to message context menu (own messages only)
    - Show confirmation dialog before deleting
    - Call DELETE /api/v1/messages/{id}
    - Replace message content with "[Message deleted]" locally
    - Show tombstone indicator for deleted messages
    - _Requirements: 2.1_

- [ ] 27. Frontend - Error Handling and Loading States
  - [~] 27.1 Implement error boundaries
    - Create ErrorBoundary component for messaging routes
    - Show user-friendly error messages for API failures
    - Add retry buttons for failed actions
    - Log errors to monitoring service (Sentry, etc.)
  
  - [~] 27.2 Add loading states
    - Show skeleton loaders for conversation list and message thread
    - Add loading spinners for message send, file upload, action buttons
    - Implement optimistic updates for message sending (show immediately, mark if failed)
    - Show progress indicators for file uploads
  
  - [~] 27.3 Handle edge cases
    - Show empty states: "No conversations yet", "No messages", "No blocked users"
    - Handle blocked user scenario: show "Cannot message this user" message
    - Handle deleted conversation: show "Conversation no longer available"
    - Handle network errors: show "Connection lost" banner with retry
    - Handle rate limit errors: show "Slow down, too many messages" warning

- [ ] 28. Integration Testing
  - [ ]* 28.1 Write API integration tests
    - Write pytest tests for all conversation endpoints
    - Write pytest tests for all message endpoints
    - Write pytest tests for privacy and blocking endpoints
    - Test message request flow end-to-end
    - Test file attachment upload and retrieval
    - Use test database with fixtures
    - Achieve >80% code coverage
    - _Requirements: All backend requirements_
  
  - [ ]* 28.2 Write unit tests for services
    - Write tests for MessagingService: conversation creation, message sending, read receipts, search
    - Write tests for PrivacyService: message requests, blocking, filtering, reporting
    - Write tests for FileAttachmentService: validation, upload, metadata extraction
    - Mock database and external dependencies
    - Test edge cases and error conditions
    - _Requirements: All service-related requirements_
  
  - [ ]* 28.3 Write WebSocket tests
    - Write tests for ConnectionManager: connect, disconnect, broadcasting
    - Write tests for typing indicator: start, stop, auto-timeout
    - Write tests for message broadcasting to conversation participants
    - Test rate limiting enforcement
    - Mock WebSocket connections
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.6, 7.8_
  
  - [ ]* 28.4 Write frontend component tests
    - Write React Testing Library tests for ConversationList, MessageThread, MessageInput
    - Write tests for file upload component
    - Write tests for message request flow
    - Write tests for privacy settings
    - Mock API calls and WebSocket events
    - Test user interactions and state updates
    - _Requirements: Frontend requirements_

- [ ] 29. Performance Testing
  - [ ]* 29.1 Run load testing with Locust
    - Write Locust test scenarios: send messages, list conversations, get messages
    - Simulate 100 concurrent users
    - Verify API response times: <200ms for conversation list, <300ms for message list
    - Verify WebSocket latency: <100ms for message broadcast
    - Test database query performance with 10,000+ messages
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [ ]* 29.2 Test file upload performance
    - Test upload of 10MB image (target: <5s)
    - Test upload of 25MB audio (target: <10s)
    - Test concurrent uploads from multiple users
    - Verify thumbnail generation speed
    - Test resumable upload with connection interruption
    - _Requirements: 4.2, 4.3, 4.5, 11.10_
  
  - [ ]* 29.3 Optimize slow queries
    - Use EXPLAIN ANALYZE on all major queries
    - Add missing indexes identified during testing
    - Optimize conversation list query (target: <50ms)
    - Optimize message pagination query (target: <50ms)
    - Test with large dataset (10,000 conversations, 100,000 messages)
    - _Requirements: 11.5, 11.6, 11.7, 11.8_

- [ ] 30. Security Testing
  - [ ]* 30.1 Test authentication and authorization
    - Test unauthorized access to conversations (expect 403)
    - Test accessing other user's messages (expect 403)
    - Test WebSocket authentication with invalid token (expect disconnect)
    - Test editing/deleting other user's messages (expect 403)
    - Verify block enforcement prevents messaging
    - _Requirements: 2.6, 2.7, 6.2, 6.3_
  
  - [ ]* 30.2 Test input validation and XSS prevention
    - Test sending HTML/script tags in message content (should be escaped)
    - Test SQL injection attempts in search queries
    - Test file upload with malicious filenames
    - Test oversized message content (>2000 chars, expect 400)
    - Test oversized file upload (expect 400)
    - Test invalid file types (expect 400)
    - _Requirements: 2.4, 4.1, 4.2, 4.3, 4.4, 4.10_
  
  - [ ]* 30.3 Test rate limiting
    - Test sending >30 messages per minute (expect 429)
    - Test uploading >10 files per minute (expect 429)
    - Test excessive WebSocket typing events (expect disconnect)
    - Verify rate limit headers in response
    - _Requirements: 7.1, 7.2_

- [ ] 31. End-to-End Testing
  - [ ]* 31.1 Test complete messaging flow
    - User A creates conversation with User B
    - User A sends text message
    - User B receives message via WebSocket
    - User B reads message, User A sees read receipt
    - User B replies with message
    - Both users see typing indicators while typing
    - Conversation appears in both users' conversation lists
    - _Requirements: 1.1, 2.1, 2.5, 3.1, 7.1, 7.6_
  
  - [ ]* 31.2 Test message request flow
    - Non-follower User C messages User D (follower-only filter enabled)
    - Message appears as pending request for User D
    - User D accepts request
    - Conversation converts to normal conversation
    - User C can now send messages freely
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.10_
  
  - [ ]* 31.3 Test blocking flow
    - User E blocks User F
    - Existing conversation hidden for both users
    - User F cannot send new messages to User E (receives 403 error)
    - User E unblocks User F
    - Conversation reappears
    - Messaging restored
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 31.4 Test file attachment flow
    - User G sends image attachment to User H
    - Image uploads successfully with thumbnail generation
    - User H receives message with image preview
    - User H clicks to view full resolution image
    - User H downloads image file
    - Test with audio file and document file
    - _Requirements: 4.1, 4.5, 4.6, 4.7, 4.9_
  
  - [ ]* 31.5 Test notification integration
    - User I sends message to offline User J
    - Verify notification created via NotificationService
    - User J comes online and sees message
    - User K sends multiple messages to User L within 5 minutes
    - Verify single batched notification sent
    - User M views conversation while User N sends message
    - Verify notification suppressed (User M is active)
    - _Requirements: 10.1, 10.2, 10.3, 10.5, 10.6, 10.7_

- [ ] 32. Documentation
  - [~] 32.1 Write API documentation
    - Document all REST endpoints with request/response examples using OpenAPI/Swagger
    - Document WebSocket events and payloads
    - Document authentication requirements
    - Document rate limits
    - Add code examples for common operations
  
  - [~] 32.2 Write developer guide
    - Create README for messaging system setup
    - Document environment variables needed
    - Document database migration steps
    - Document Redis configuration
    - Document file storage configuration
    - Add troubleshooting section
  
  - [~] 32.3 Create user guide
    - Write user-facing documentation for messaging features
    - Document privacy settings and their effects
    - Document blocking and reporting
    - Document file attachment limits
    - Create FAQ section

- [ ] 33. Deployment Preparation
  - [~] 33.1 Configure production settings
    - Set up production database with appropriate pool size (20 connections)
    - Configure Redis for production with connection pool (50 connections)
    - Set up file storage with CDN (Cloudflare R2)
    - Configure WebSocket scaling (consider Redis pub/sub for multi-instance)
    - Set secure WebSocket (WSS) with TLS 1.3
    - Enable database encryption at rest (PostgreSQL TDE)
  
  - [~] 33.2 Set up monitoring and logging
    - Add application metrics: message send rate, WebSocket connections, API latency
    - Set up error tracking (Sentry integration)
    - Configure structured logging with correlation IDs
    - Add database query monitoring
    - Set up alerting for rate limit violations and errors
  
  - [~] 33.3 Prepare database migration for production
    - Test migration on staging environment with production-like data
    - Create rollback plan for migration
    - Schedule migration during low-traffic window
    - Prepare data backup before migration
    - Document migration steps and rollback procedures

- [~] 34. Final Checkpoint
  - Run full test suite (unit, integration, E2E), verify all features working, review performance benchmarks, ensure documentation complete, get user approval to deploy.

## Notes

- Tasks marked with `*` are optional test-related sub-tasks and can be skipped for faster MVP delivery
- All tasks reference specific requirements for traceability to the requirements document
- Backend tasks (1-16) can be developed independently from frontend tasks (17-27)
- WebSocket implementation (12-13, 19) requires coordination between backend and frontend
- Testing tasks (28-31) should be executed as features are completed, not all at the end
- Database migration (1.1) must be completed and tested before any model implementation
- Performance optimizations (14) can be added iteratively after core functionality works
- Security implementation (15) should be integrated throughout development, not as an afterthought
- Deployment tasks (33) should be prepared in parallel with final testing

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1", "2.2", "2.3", "2.4", "2.5"] },
    { "id": 2, "tasks": ["3.1", "3.2", "3.3"] },
    { "id": 3, "tasks": ["4.1", "5.1", "6.1", "7.1"] },
    { "id": 4, "tasks": ["4.2", "5.2", "6.2", "7.2"] },
    { "id": 5, "tasks": ["4.3", "5.3", "6.3", "7.3"] },
    { "id": 6, "tasks": ["4.4", "5.4"] },
    { "id": 7, "tasks": ["8.1", "8.2", "8.3", "8.4", "10.1", "11.1"] },
    { "id": 8, "tasks": ["9.1", "9.2", "9.3", "9.4", "10.2", "10.3", "11.2", "11.3"] },
    { "id": 9, "tasks": ["9.5", "9.6", "9.7", "11.4", "11.5", "11.6"] },
    { "id": 10, "tasks": ["12.1"] },
    { "id": 11, "tasks": ["12.2", "12.3"] },
    { "id": 12, "tasks": ["13.1", "14.1", "15.1"] },
    { "id": 13, "tasks": ["14.2", "14.3", "15.2", "15.3", "15.4"] },
    { "id": 14, "tasks": ["17.1", "17.2"] },
    { "id": 15, "tasks": ["18.1", "18.2", "18.3", "21.1"] },
    { "id": 16, "tasks": ["18.4", "19.1", "21.2"] },
    { "id": 17, "tasks": ["19.2", "19.3", "20.1"] },
    { "id": 18, "tasks": ["19.4", "20.2", "20.3", "22.1"] },
    { "id": 19, "tasks": ["22.2", "22.3", "23.1"] },
    { "id": 20, "tasks": ["23.2", "23.3", "24.1"] },
    { "id": 21, "tasks": ["24.2", "24.3", "25.1"] },
    { "id": 22, "tasks": ["25.2", "25.3", "26.1"] },
    { "id": 23, "tasks": ["26.2", "27.1", "27.2", "27.3"] },
    { "id": 24, "tasks": ["28.1", "28.2", "28.3", "28.4"] },
    { "id": 25, "tasks": ["29.1", "29.2", "29.3"] },
    { "id": 26, "tasks": ["30.1", "30.2", "30.3"] },
    { "id": 27, "tasks": ["31.1", "31.2", "31.3", "31.4", "31.5"] },
    { "id": 28, "tasks": ["32.1", "32.2", "32.3"] },
    { "id": 29, "tasks": ["33.1", "33.2", "33.3"] }
  ]
}
```
