# Design Document: Messaging System

## Overview

The Messaging System provides direct, real-time communication between BeatPush users across all roles (Artists, DJs, Producers, Fans). The system enables private conversations, file sharing (images, audio, documents), privacy controls, and notification integration. The architecture prioritizes performance for African markets with limited bandwidth through pagination, efficient queries, and optional file compression.

**Key Design Principles:**
- **Performance-First**: Optimized for limited bandwidth with pagination, lazy loading, and compressed files
- **Privacy-Focused**: Message requests, blocking, and granular privacy controls
- **Real-Time Capable**: WebSocket support with polling fallback for typing indicators and instant delivery
- **Extensible**: Database schema designed to support future AI features (smart replies, translation, spam detection)
- **Secure**: Message validation, file scanning, blocked user enforcement

**Technology Stack:**
- **Backend**: Python with FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-Time**: WebSockets (FastAPI WebSocket support) with Socket.IO as fallback
- **File Storage**: Existing FileStorageService (Cloudflare R2 or AWS S3)
- **Notifications**: Integration with existing NotificationService

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Conversation │  │   Message    │  │    File      │         │
│  │     List     │  │    Thread    │  │   Upload     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              WebSocket              REST API
                    │                   │
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  API Layer                                │  │
│  │  /api/v1/conversations   /api/v1/messages                │  │
│  │  /ws/conversations       /api/v1/message-requests        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Service Layer                                │  │
│  │  ┌────────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │   Messaging    │  │   Privacy   │  │ Notification │  │  │
│  │  │    Service     │  │   Service   │  │  Integration │  │  │
│  │  └────────────────┘  └─────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 Data Layer                                │  │
│  │  Conversations │ Messages │ Attachments │ Blocks          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              PostgreSQL         File Storage (R2/S3)
```

### Communication Patterns

**REST API** - Standard CRUD operations:
- Create conversations and messages
- Fetch conversation lists and message history
- Update read receipts and privacy settings
- Delete conversations (soft delete)

**WebSocket** - Real-time events:
- New message delivery
- Typing indicators
- Read receipt updates
- Online/offline status (future)

**Notification Integration** - Async alerts:
- New message notifications
- Message request notifications
- Batched notification for multiple messages

### Data Flow

**Sending a Message:**
1. User submits message via REST API (`POST /api/v1/messages`)
2. MessageService validates content, checks privacy rules, and blocks
3. Message stored in database with `unread` status for recipient
4. WebSocket broadcasts message to recipient if online
5. NotificationService creates notification for offline/inactive recipients
6. Return message confirmation to sender

**Receiving Messages (Real-Time):**
1. User connects via WebSocket on conversation view
2. Server maintains active connection in connection pool
3. New messages broadcast immediately to connected clients
4. Typing indicators transmitted with minimal payload
5. Read receipts updated when user views conversation

## Components and Interfaces

### 1. Database Schema

#### Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_preview TEXT,
    is_message_request BOOLEAN DEFAULT FALSE,
    request_status VARCHAR(20), -- 'pending', 'accepted', 'declined'
    
    -- Indexes
    INDEX idx_conversations_last_activity (last_activity_at DESC),
    INDEX idx_conversations_request (is_message_request, request_status)
);

-- Conversation participants (many-to-many)
CREATE TABLE conversation_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,
    unread_count INTEGER DEFAULT 0,
    last_read_at TIMESTAMP WITH TIME ZONE,
    is_archived BOOLEAN DEFAULT FALSE,
    is_muted BOOLEAN DEFAULT FALSE,
    
    UNIQUE(conversation_id, user_id),
    
    -- Indexes for performance
    INDEX idx_participant_user (user_id),
    INDEX idx_participant_conversation (conversation_id),
    INDEX idx_participant_unread (user_id, unread_count) WHERE unread_count > 0
);
```

#### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL CHECK (char_length(content) <= 2000),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_edited BOOLEAN DEFAULT FALSE,
    
    -- AI feature fields (future use)
    language_code VARCHAR(10),
    spam_score DECIMAL(3,2),
    ai_processed BOOLEAN DEFAULT FALSE,
    smart_reply_suggestions JSONB,
    
    -- Indexes
    INDEX idx_messages_conversation (conversation_id, created_at DESC),
    INDEX idx_messages_sender (sender_id),
    INDEX idx_messages_created (created_at DESC)
);
```


#### Message Read Receipts Table

```sql
CREATE TABLE message_read_receipts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(message_id, user_id),
    
    -- Indexes
    INDEX idx_receipts_message (message_id),
    INDEX idx_receipts_user (user_id)
);
```

#### Message Attachments Table

```sql
CREATE TABLE message_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    file_type VARCHAR(50) NOT NULL, -- 'image', 'audio', 'document', 'voice_note'
    original_filename VARCHAR(255) NOT NULL,
    storage_url TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    duration INTEGER, -- for audio/voice notes (seconds)
    width INTEGER, -- for images
    height INTEGER, -- for images
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_attachments_message (message_id),
    INDEX idx_attachments_type (file_type)
);
```

#### Blocked Users Table

```sql
CREATE TABLE blocked_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blocker_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blocked_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reason TEXT,
    
    UNIQUE(blocker_id, blocked_id),
    
    -- Indexes
    INDEX idx_blocks_blocker (blocker_id),
    INDEX idx_blocks_blocked (blocked_id)
);
```


#### Message Reports Table

```sql
CREATE TABLE message_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason VARCHAR(50) NOT NULL, -- 'spam', 'harassment', 'inappropriate', 'other'
    details TEXT CHECK (char_length(details) <= 500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES users(id),
    action_taken VARCHAR(100),
    
    -- Indexes
    INDEX idx_reports_message (message_id),
    INDEX idx_reports_status (reviewed, created_at DESC)
);
```

#### User Privacy Settings Table

```sql
CREATE TABLE user_message_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    message_filter VARCHAR(20) DEFAULT 'everyone', -- 'everyone', 'followers', 'verified', 'none'
    read_receipts_enabled BOOLEAN DEFAULT TRUE,
    typing_indicators_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_settings_user (user_id)
);
```

### 2. API Endpoints

#### Conversation Endpoints

**GET /api/v1/conversations**
- List user's conversations with pagination
- Query params: `page`, `page_size`, `unread_only`, `search`
- Returns conversation metadata with last message preview and unread count
- Ordered by `last_activity_at DESC`

```python
# Response Schema
{
    "conversations": [
        {
            "id": "uuid",
            "participants": [
                {
                    "user_id": "uuid",
                    "username": "string",
                    "full_name": "string",
                    "avatar_url": "string",
                    "is_verified": bool
                }
            ],
            "last_message": {
                "id": "uuid",
                "content": "string",
                "sender_id": "uuid",
                "created_at": "timestamp",
                "has_attachment": bool
            },
            "unread_count": int,
            "is_message_request": bool,
            "last_activity_at": "timestamp"
        }
    ],
    "total": int,
    "page": int,
    "page_size": int,
    "total_pages": int
}
```


**GET /api/v1/conversations/{conversation_id}**
- Get conversation details
- Returns full conversation metadata and participant info

**POST /api/v1/conversations**
- Create new conversation or retrieve existing
- Body: `{ "recipient_id": "uuid" }`
- Returns conversation object or creates message request if needed

**DELETE /api/v1/conversations/{conversation_id}**
- Soft delete conversation for current user
- Sets `left_at` timestamp for user in `conversation_participants`

#### Message Endpoints

**GET /api/v1/conversations/{conversation_id}/messages**
- List messages in conversation with pagination
- Query params: `page`, `page_size`, `cursor`, `before`, `after`
- Returns messages ordered by `created_at ASC`
- Supports cursor-based pagination for infinite scroll

```python
# Response Schema
{
    "messages": [
        {
            "id": "uuid",
            "conversation_id": "uuid",
            "sender_id": "uuid",
            "sender": {
                "username": "string",
                "full_name": "string",
                "avatar_url": "string"
            },
            "content": "string",
            "created_at": "timestamp",
            "is_edited": bool,
            "read_by": ["user_id1", "user_id2"],
            "attachments": [
                {
                    "id": "uuid",
                    "file_type": "image",
                    "original_filename": "string",
                    "storage_url": "string",
                    "file_size": int,
                    "thumbnail_url": "string",
                    "duration": int
                }
            ]
        }
    ],
    "has_more": bool,
    "next_cursor": "string"
}
```

**POST /api/v1/messages**
- Send new message
- Body: `{ "conversation_id": "uuid", "recipient_id": "uuid", "content": "string" }`
- Either `conversation_id` or `recipient_id` required
- Creates conversation if doesn't exist
- Returns created message

**POST /api/v1/messages/{message_id}/attachments**
- Upload file attachment to message
- Multipart form data with file
- Validates file type and size
- Returns attachment metadata


**PUT /api/v1/messages/{message_id}**
- Edit message content
- Body: `{ "content": "string" }`
- Sets `is_edited` flag and `updated_at` timestamp
- Only sender can edit within 15 minutes of creation

**DELETE /api/v1/messages/{message_id}**
- Soft delete message
- Sets `deleted_at` timestamp
- Message content replaced with "[Message deleted]" in UI

**POST /api/v1/messages/{message_id}/read**
- Mark message as read
- Creates read receipt entry
- Updates conversation unread count

#### Message Request Endpoints

**GET /api/v1/message-requests**
- List pending message requests
- Query params: `page`, `page_size`
- Returns conversations where `is_message_request=true` and `request_status='pending'`

**POST /api/v1/message-requests/{conversation_id}/accept**
- Accept message request
- Updates `request_status` to 'accepted'
- Converts to normal conversation

**POST /api/v1/message-requests/{conversation_id}/decline**
- Decline message request
- Updates `request_status` to 'declined'
- Hides conversation from both users

#### Privacy & Blocking Endpoints

**GET /api/v1/messaging/settings**
- Get user's message privacy settings
- Returns `message_filter`, `read_receipts_enabled`, `typing_indicators_enabled`

**PUT /api/v1/messaging/settings**
- Update message privacy settings
- Body: settings object

**POST /api/v1/messaging/block**
- Block a user
- Body: `{ "user_id": "uuid", "reason": "string" }`
- Hides existing conversations
- Prevents new messages

**DELETE /api/v1/messaging/block/{user_id}**
- Unblock a user
- Restores access to conversations

**GET /api/v1/messaging/blocked-users**
- List blocked users with pagination

**POST /api/v1/messages/{message_id}/report**
- Report a message
- Body: `{ "reason": "string", "details": "string" }`
- Creates report for admin review


#### WebSocket Endpoints

**WS /ws/conversations**
- WebSocket connection for real-time messaging
- Authentication via JWT token in query param or header
- Maintains persistent connection for active users

**WebSocket Events (Client → Server):**

```json
{
    "type": "typing_start",
    "conversation_id": "uuid"
}

{
    "type": "typing_stop",
    "conversation_id": "uuid"
}

{
    "type": "join_conversation",
    "conversation_id": "uuid"
}

{
    "type": "leave_conversation",
    "conversation_id": "uuid"
}
```

**WebSocket Events (Server → Client):**

```json
{
    "type": "new_message",
    "conversation_id": "uuid",
    "message": { /* message object */ }
}

{
    "type": "typing_indicator",
    "conversation_id": "uuid",
    "user_id": "uuid",
    "is_typing": true
}

{
    "type": "message_read",
    "message_id": "uuid",
    "read_by": "uuid",
    "read_at": "timestamp"
}

{
    "type": "user_online",
    "user_id": "uuid"
}

{
    "type": "user_offline",
    "user_id": "uuid"
}
```

### 3. Service Layer Architecture

#### MessagingService

Primary service handling conversation and message operations.

```python
class MessagingService:
    def __init__(self, db: Session, file_storage: FileStorageService):
        self.db = db
        self.file_storage = file_storage
    
    # Conversation Management
    async def get_or_create_conversation(
        self, user_id: str, recipient_id: str
    ) -> Conversation
    
    async def list_conversations(
        self, user_id: str, page: int = 1, page_size: int = 20,
        unread_only: bool = False, search: str = None
    ) -> Dict
    
    async def get_conversation(
        self, conversation_id: str, user_id: str
    ) -> Conversation
```

    
    # Message Management
    async def send_message(
        self, sender_id: str, recipient_id: str,
        content: str, conversation_id: str = None
    ) -> Message
    
    async def get_messages(
        self, conversation_id: str, user_id: str,
        page: int = 1, page_size: int = 50,
        cursor: str = None
    ) -> Dict
    
    async def mark_message_read(
        self, message_id: str, user_id: str
    ) -> bool
    
    async def mark_conversation_read(
        self, conversation_id: str, user_id: str
    ) -> int
    
    # Attachment Management
    async def attach_file(
        self, message_id: str, file: UploadFile,
        file_type: str
    ) -> MessageAttachment
    
    # Search
    async def search_conversations(
        self, user_id: str, query: str, page: int = 1
    ) -> Dict
    
    async def search_messages(
        self, user_id: str, query: str, page: int = 1
    ) -> Dict
```

#### PrivacyService

Handles privacy controls, blocking, and message filtering.

```python
class PrivacyService:
    def __init__(self, db: Session):
        self.db = db
    
    # Settings Management
    def get_user_settings(self, user_id: str) -> UserMessageSettings
    
    def update_user_settings(
        self, user_id: str, settings: Dict
    ) -> UserMessageSettings
    
    # Block Management
    def block_user(
        self, blocker_id: str, blocked_id: str, reason: str = None
    ) -> BlockedUser
    
    def unblock_user(self, blocker_id: str, blocked_id: str) -> bool
    
    def is_blocked(self, user_id: str, target_id: str) -> bool
    
    def get_blocked_users(
        self, user_id: str, page: int = 1
    ) -> Dict
    
    # Message Request Filtering
    def should_create_message_request(
        self, sender_id: str, recipient_id: str
    ) -> bool
    
    def can_send_message(
        self, sender_id: str, recipient_id: str
    ) -> Tuple[bool, str]
```

    
    # Reporting
    def report_message(
        self, reporter_id: str, message_id: str,
        reason: str, details: str = None
    ) -> MessageReport
```

#### WebSocketManager

Manages WebSocket connections and real-time event broadcasting.

```python
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.typing_timers: Dict[str, asyncio.Task] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """Register new WebSocket connection"""
        
    async def disconnect(self, user_id: str, websocket: WebSocket):
        """Remove WebSocket connection"""
    
    async def broadcast_to_conversation(
        self, conversation_id: str, event: Dict,
        exclude_user: str = None
    ):
        """Send event to all conversation participants"""
    
    async def send_to_user(self, user_id: str, event: Dict):
        """Send event to specific user"""
    
    async def handle_typing_indicator(
        self, user_id: str, conversation_id: str, is_typing: bool
    ):
        """Broadcast typing indicator with auto-timeout"""
    
    async def broadcast_new_message(
        self, conversation_id: str, message: Message
    ):
        """Broadcast new message to conversation participants"""
    
    async def broadcast_read_receipt(
        self, message_id: str, user_id: str, read_at: datetime
    ):
        """Broadcast read receipt to message sender"""
```

## Data Models

### SQLAlchemy Models

#### Conversation Model

```python
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity_at = Column(DateTime(timezone=True), 
                             server_default=func.now(), index=True)
    last_message_preview = Column(Text)
    is_message_request = Column(Boolean, default=False, index=True)
    request_status = Column(String(20))  # pending, accepted, declined
    
    # Relationships
    participants = relationship("ConversationParticipant", 
                               back_populates="conversation",
                               cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="conversation",
                           cascade="all, delete-orphan")
```


#### ConversationParticipant Model

```python
class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"
    
    id = Column(String(36), primary_key=True, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", 
                            ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                    nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))
    unread_count = Column(Integer, default=0, index=True)
    last_read_at = Column(DateTime(timezone=True))
    is_archived = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User")
```

#### Message Model

```python
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, index=True)
    conversation_id = Column(String(36), 
                            ForeignKey("conversations.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("users.id", 
                       ondelete="SET NULL"), index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), 
                       server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    is_edited = Column(Boolean, default=False)
    
    # AI feature fields
    language_code = Column(String(10))
    spam_score = Column(Numeric(3, 2))
    ai_processed = Column(Boolean, default=False)
    smart_reply_suggestions = Column(JSON)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User")
    attachments = relationship("MessageAttachment", 
                               back_populates="message",
                               cascade="all, delete-orphan")
    read_receipts = relationship("MessageReadReceipt",
                                back_populates="message",
                                cascade="all, delete-orphan")
```


#### MessageAttachment Model

```python
class MessageAttachment(Base):
    __tablename__ = "message_attachments"
    
    id = Column(String(36), primary_key=True, index=True)
    message_id = Column(String(36), ForeignKey("messages.id",
                        ondelete="CASCADE"), nullable=False, index=True)
    file_type = Column(String(50), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    storage_url = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100))
    duration = Column(Integer)  # Audio duration in seconds
    width = Column(Integer)  # Image width
    height = Column(Integer)  # Image height
    thumbnail_url = Column(Text)  # For images/videos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    message = relationship("Message", back_populates="attachments")
```

#### BlockedUser Model

```python
class BlockedUser(Base):
    __tablename__ = "blocked_users"
    
    id = Column(String(36), primary_key=True, index=True)
    blocker_id = Column(String(36), ForeignKey("users.id",
                        ondelete="CASCADE"), nullable=False, index=True)
    blocked_id = Column(String(36), ForeignKey("users.id",
                        ondelete="CASCADE"), nullable=False, index=True)
    blocked_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text)
    
    # Relationships
    blocker = relationship("User", foreign_keys=[blocker_id])
    blocked = relationship("User", foreign_keys=[blocked_id])
```

#### UserMessageSettings Model

```python
from sqlalchemy import Enum
import enum

class MessageFilter(str, enum.Enum):
    EVERYONE = "everyone"
    FOLLOWERS = "followers"
    VERIFIED = "verified"
    NONE = "none"

class UserMessageSettings(Base):
    __tablename__ = "user_message_settings"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                    unique=True, nullable=False, index=True)
    message_filter = Column(Enum(MessageFilter), 
                           default=MessageFilter.EVERYONE)
    read_receipts_enabled = Column(Boolean, default=True)
    typing_indicators_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
```


### Pydantic Schemas (DTOs)

#### Request Schemas

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class SendMessageRequest(BaseModel):
    """Request to send a new message"""
    recipient_id: Optional[str] = None
    conversation_id: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=2000)
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty or whitespace')
        return v.strip()

class CreateConversationRequest(BaseModel):
    """Request to create or get conversation"""
    recipient_id: str = Field(..., min_length=36, max_length=36)

class UpdateMessageRequest(BaseModel):
    """Request to edit message"""
    content: str = Field(..., min_length=1, max_length=2000)

class UpdateSettingsRequest(BaseModel):
    """Update message privacy settings"""
    message_filter: Optional[str] = None
    read_receipts_enabled: Optional[bool] = None
    typing_indicators_enabled: Optional[bool] = None

class BlockUserRequest(BaseModel):
    """Block a user"""
    user_id: str
    reason: Optional[str] = Field(None, max_length=500)

class ReportMessageRequest(BaseModel):
    """Report a message"""
    reason: str = Field(..., 
        regex='^(spam|harassment|inappropriate|other)$')
    details: Optional[str] = Field(None, max_length=500)
```

#### Response Schemas

```python
class UserBasicInfo(BaseModel):
    """Basic user info for participants"""
    user_id: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_verified: bool
    
    class Config:
        from_attributes = True

class AttachmentResponse(BaseModel):
    """File attachment response"""
    id: str
    file_type: str
    original_filename: str
    storage_url: str
    file_size: int
    mime_type: Optional[str]
    duration: Optional[int]
    width: Optional[int]
    height: Optional[int]
    thumbnail_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
```


class MessageResponse(BaseModel):
    """Message response"""
    id: str
    conversation_id: str
    sender_id: str
    sender: UserBasicInfo
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_edited: bool
    read_by: List[str]  # List of user IDs who read the message
    attachments: List[AttachmentResponse]
    
    class Config:
        from_attributes = True

class LastMessagePreview(BaseModel):
    """Preview of last message in conversation"""
    id: str
    content: str
    sender_id: str
    created_at: datetime
    has_attachment: bool

class ConversationResponse(BaseModel):
    """Conversation response"""
    id: str
    participants: List[UserBasicInfo]
    last_message: Optional[LastMessagePreview]
    unread_count: int
    is_message_request: bool
    request_status: Optional[str]
    last_activity_at: datetime
    is_archived: bool
    is_muted: bool
    
    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    """Paginated conversation list"""
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class MessageListResponse(BaseModel):
    """Paginated message list"""
    messages: List[MessageResponse]
    has_more: bool
    next_cursor: Optional[str]

class SettingsResponse(BaseModel):
    """User message settings"""
    message_filter: str
    read_receipts_enabled: bool
    typing_indicators_enabled: bool
    
    class Config:
        from_attributes = True

class BlockedUserResponse(BaseModel):
    """Blocked user info"""
    id: str
    blocked_user: UserBasicInfo
    blocked_at: datetime
    reason: Optional[str]
    
    class Config:
        from_attributes = True
```

## File Attachment Handling

### Attachment Workflow

1. **Upload Initiation**: Client requests upload via `POST /api/v1/messages`
2. **File Validation**: Server validates type, size, and scans for malware
3. **Storage**: File uploaded to Cloudflare R2/S3 using existing FileStorageService
4. **Thumbnail Generation**: For images, generate compressed thumbnail
5. **Metadata Extraction**: Extract duration for audio, dimensions for images
6. **Database Record**: Create `message_attachments` entry linked to message
7. **URL Generation**: Return signed URL with expiration for security

### Supported File Types and Limits

```python
ATTACHMENT_CONFIG = {
    "image": {
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "max_size_mb": 10,
        "mime_types": ["image/jpeg", "image/png", "image/gif", "image/webp"]
    },
    "audio": {
        "extensions": [".mp3", ".wav", ".m4a", ".ogg"],
        "max_size_mb": 25,
        "mime_types": ["audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg"]
    },
    "document": {
        "extensions": [".pdf", ".doc", ".docx"],
        "max_size_mb": 10,
        "mime_types": ["application/pdf", 
                       "application/msword",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    },
    "voice_note": {
        "extensions": [".mp3", ".m4a", ".ogg", ".wav"],
        "max_size_mb": 5,
        "mime_types": ["audio/mpeg", "audio/mp4", "audio/ogg", "audio/wav"]
    }
}
```


### File Storage Service Integration

The messaging system leverages the existing `FileStorageService` with new methods:

```python
class FileStorageService:
    # Existing methods...
    
    async def upload_message_attachment(
        self, file: UploadFile, message_id: str, 
        file_type: str
    ) -> Tuple[str, Dict]:
        """
        Upload message attachment
        
        Returns:
            Tuple of (storage_url, metadata_dict)
        """
        # Validate file type and size
        self._validate_attachment(file, file_type)
        
        # Generate unique filename
        filename = self.generate_unique_filename(file.filename)
        storage_path = f"messages/{message_id}/{filename}"
        
        # Upload to R2/S3
        storage_url = await self._upload_to_cloud(file, storage_path)
        
        # Extract metadata
        metadata = await self._extract_metadata(file, file_type)
        
        # Generate thumbnail for images
        if file_type == "image":
            thumbnail_url = await self._generate_thumbnail(
                file, storage_path
            )
            metadata["thumbnail_url"] = thumbnail_url
        
        return storage_url, metadata
    
    async def _generate_thumbnail(
        self, file: UploadFile, storage_path: str
    ) -> str:
        """Generate and upload thumbnail for images"""
        # Resize to 200x200
        # Upload thumbnail with _thumb suffix
        # Return thumbnail URL
        pass
    
    async def delete_message_attachment(self, storage_url: str) -> bool:
        """Delete attachment from storage"""
        # Delete main file and thumbnail
        pass
```

### Bandwidth Optimization

For African markets with limited bandwidth:

1. **Progressive Image Loading**: 
   - Send low-quality thumbnail first (< 50KB)
   - Load full resolution on user request
   
2. **Audio Compression**:
   - Convert to lower bitrate for preview (64kbps)
   - Full quality on download
   
3. **Resumable Uploads**:
   - Support chunked uploads with resume capability
   - Store upload progress in Redis

4. **CDN Integration**:
   - Serve files through Cloudflare CDN
   - Edge caching for frequently accessed files

## Real-Time Messaging Architecture

### WebSocket Connection Management

```python
from fastapi import WebSocket
from typing import Dict, List
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        # user_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # conversation_id -> set of user_ids currently viewing
        self.active_conversations: Dict[str, set] = {}
        
        # Typing indicators with auto-timeout
        self.typing_timers: Dict[str, asyncio.Task] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """Register new connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        
        # Broadcast user online status
        await self.broadcast_user_status(user_id, "online")
```

    
    async def disconnect(self, user_id: str, websocket: WebSocket):
        """Remove connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            
            # If no more connections, mark offline
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                await self.broadcast_user_status(user_id, "offline")
    
    async def send_to_user(self, user_id: str, message: Dict):
        """Send message to all user's connections"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection dead, will be cleaned up
                    pass
    
    async def broadcast_to_conversation(
        self, conversation_id: str, message: Dict, 
        exclude_user: str = None
    ):
        """Broadcast to all conversation participants"""
        # Get conversation participants from database
        participants = await self._get_conversation_participants(
            conversation_id
        )
        
        for user_id in participants:
            if user_id != exclude_user:
                await self.send_to_user(user_id, message)
    
    async def handle_typing_indicator(
        self, user_id: str, conversation_id: str, is_typing: bool
    ):
        """Handle typing indicator with auto-timeout"""
        key = f"{conversation_id}:{user_id}"
        
        # Cancel existing timer
        if key in self.typing_timers:
            self.typing_timers[key].cancel()
        
        # Broadcast typing status
        await self.broadcast_to_conversation(
            conversation_id,
            {
                "type": "typing_indicator",
                "conversation_id": conversation_id,
                "user_id": user_id,
                "is_typing": is_typing
            },
            exclude_user=user_id
        )
        
        # Set auto-timeout (3 seconds)
        if is_typing:
            self.typing_timers[key] = asyncio.create_task(
                self._typing_timeout(user_id, conversation_id, key)
            )
    
    async def _typing_timeout(
        self, user_id: str, conversation_id: str, key: str
    ):
        """Auto-stop typing indicator after 3 seconds"""
        await asyncio.sleep(3)
        
        await self.broadcast_to_conversation(
            conversation_id,
            {
                "type": "typing_indicator",
                "conversation_id": conversation_id,
                "user_id": user_id,
                "is_typing": False
            },
            exclude_user=user_id
        )
        
        del self.typing_timers[key]
```

### WebSocket Endpoint Handler

```python
from fastapi import APIRouter, WebSocket, Depends, status
from app.core.dependencies import get_current_user_ws

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/conversations")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user = Depends(get_current_user_ws)
):
    """WebSocket endpoint for real-time messaging"""
    user_id = current_user.id
    
    await manager.connect(user_id, websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            event_type = data.get("type")
            
            if event_type == "typing_start":
                await manager.handle_typing_indicator(
                    user_id, 
                    data["conversation_id"], 
                    True
                )
            
            elif event_type == "typing_stop":
                await manager.handle_typing_indicator(
                    user_id,
                    data["conversation_id"],
                    False
                )
            
            elif event_type == "join_conversation":
                # Track active conversation for read receipts
                conversation_id = data["conversation_id"]
                if conversation_id not in manager.active_conversations:
                    manager.active_conversations[conversation_id] = set()
                manager.active_conversations[conversation_id].add(user_id)
            
            elif event_type == "leave_conversation":
                conversation_id = data["conversation_id"]
                if conversation_id in manager.active_conversations:
                    manager.active_conversations[conversation_id].discard(
                        user_id
                    )
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        await manager.disconnect(user_id, websocket)
```


### Polling Fallback

For clients that can't maintain WebSocket connections:

```python
@router.get("/api/v1/conversations/{conversation_id}/poll")
async def poll_new_messages(
    conversation_id: str,
    since: datetime,
    current_user = Depends(get_current_user)
):
    """Poll for new messages since timestamp"""
    messages = await messaging_service.get_messages_since(
        conversation_id, current_user.id, since
    )
    
    typing_users = await messaging_service.get_typing_users(
        conversation_id
    )
    
    return {
        "messages": messages,
        "typing_users": typing_users
    }
```

**Polling Strategy:**
- Poll every 3 seconds when conversation is active
- Poll every 10 seconds for conversation list updates
- Use `If-Modified-Since` headers to reduce bandwidth

## Privacy and Blocking Implementation

### Message Request Logic

```python
async def should_create_message_request(
    sender_id: str, recipient_id: str
) -> bool:
    """Determine if message should be a request"""
    
    # Check if blocked
    if await privacy_service.is_blocked(sender_id, recipient_id):
        raise HTTPException(
            status_code=403,
            detail="Cannot send message to this user"
        )
    
    # Check if conversation already exists
    existing_conversation = await messaging_service.get_conversation_between(
        sender_id, recipient_id
    )
    
    if existing_conversation:
        # Already have conversation, no request needed
        return False
    
    # Get recipient's settings
    settings = await privacy_service.get_user_settings(recipient_id)
    
    # Check filter rules
    if settings.message_filter == MessageFilter.NONE:
        raise HTTPException(
            status_code=403,
            detail="User is not accepting messages"
        )
    
    if settings.message_filter == MessageFilter.VERIFIED:
        sender = await user_service.get_user(sender_id)
        if not sender.is_verified:
            return True  # Create message request
    
    if settings.message_filter == MessageFilter.FOLLOWERS:
        is_follower = await social_service.is_following(
            sender_id, recipient_id
        )
        if not is_follower:
            return True  # Create message request
    
    # MessageFilter.EVERYONE - no request needed
    return False
```

### Block Enforcement

Blocking is enforced at multiple layers:

1. **API Layer**: Check before message send
2. **Service Layer**: Validate in `can_send_message()`
3. **Database Layer**: Use database constraints where possible
4. **WebSocket Layer**: Filter events from blocked users

```python
async def enforce_block_rules(sender_id: str, recipient_id: str):
    """Enforce blocking rules"""
    
    # Check if sender is blocked by recipient
    if await privacy_service.is_blocked(recipient_id, sender_id):
        raise HTTPException(
            status_code=403,
            detail="You cannot message this user"
        )
    
    # Check if recipient is blocked by sender
    if await privacy_service.is_blocked(sender_id, recipient_id):
        raise HTTPException(
            status_code=403,
            detail="You have blocked this user"
        )
```


### Hiding Conversations on Block

When a user is blocked, existing conversations are hidden:

```python
async def block_user(blocker_id: str, blocked_id: str, reason: str = None):
    """Block user and hide conversations"""
    
    # Create block record
    block = BlockedUser(
        id=str(uuid.uuid4()),
        blocker_id=blocker_id,
        blocked_id=blocked_id,
        blocked_at=datetime.utcnow(),
        reason=reason
    )
    db.add(block)
    
    # Find all conversations between users
    conversations = await messaging_service.get_conversations_between(
        blocker_id, blocked_id
    )
    
    # Mark as left for both users (soft hide)
    for conversation in conversations:
        for participant in conversation.participants:
            if participant.user_id in [blocker_id, blocked_id]:
                participant.left_at = datetime.utcnow()
    
    db.commit()
    
    return block

async def unblock_user(blocker_id: str, blocked_id: str):
    """Unblock user and restore conversations"""
    
    # Delete block record
    block = db.query(BlockedUser).filter(
        BlockedUser.blocker_id == blocker_id,
        BlockedUser.blocked_id == blocked_id
    ).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    db.delete(block)
    
    # Restore conversations (clear left_at)
    conversations = await messaging_service.get_conversations_between(
        blocker_id, blocked_id, include_hidden=True
    )
    
    for conversation in conversations:
        for participant in conversation.participants:
            if participant.user_id == blocker_id:
                participant.left_at = None
    
    db.commit()
```

## Performance Optimizations

### 1. Database Indexing Strategy

**Critical Indexes:**
```sql
-- Conversation list query optimization
CREATE INDEX idx_conv_participants_user_active 
    ON conversation_participants(user_id, left_at) 
    WHERE left_at IS NULL;

-- Message pagination
CREATE INDEX idx_messages_conv_created 
    ON messages(conversation_id, created_at DESC) 
    WHERE deleted_at IS NULL;

-- Unread count calculation
CREATE INDEX idx_participants_unread 
    ON conversation_participants(user_id, unread_count) 
    WHERE unread_count > 0;

-- Block checking
CREATE INDEX idx_blocks_both 
    ON blocked_users(blocker_id, blocked_id);

-- Search optimization
CREATE INDEX idx_messages_content_gin 
    ON messages USING gin(to_tsvector('english', content));
```

### 2. Query Optimization

**Denormalized Data:**
- Store `last_message_preview` in conversations table to avoid joins
- Cache `unread_count` in conversation_participants
- Store sender info snapshot in messages for faster retrieval

**Efficient Conversation List Query:**
```python
async def list_conversations(user_id: str, page: int = 1, page_size: int = 20):
    """Optimized conversation list query"""
    
    # Single query with joins
    query = (
        select(Conversation, ConversationParticipant, User)
        .join(ConversationParticipant, 
              Conversation.id == ConversationParticipant.conversation_id)
        .join(User, 
              ConversationParticipant.user_id == User.id)
        .where(
            and_(
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.left_at.is_(None)
            )
        )
        .order_by(Conversation.last_activity_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    return result.fetchall()
```


### 3. Caching Strategy

**Redis Caching:**
```python
from redis import asyncio as aioredis
import json

class MessagingCache:
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.conversation_ttl = 300  # 5 minutes
        self.settings_ttl = 3600  # 1 hour
    
    async def get_conversation(self, conversation_id: str):
        """Get cached conversation"""
        key = f"conversation:{conversation_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def cache_conversation(self, conversation_id: str, data: dict):
        """Cache conversation data"""
        key = f"conversation:{conversation_id}"
        await self.redis.setex(
            key, 
            self.conversation_ttl, 
            json.dumps(data)
        )
    
    async def invalidate_conversation(self, conversation_id: str):
        """Invalidate conversation cache on update"""
        key = f"conversation:{conversation_id}"
        await self.redis.delete(key)
    
    async def cache_user_settings(self, user_id: str, settings: dict):
        """Cache privacy settings"""
        key = f"settings:{user_id}"
        await self.redis.setex(
            key,
            self.settings_ttl,
            json.dumps(settings)
        )
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get cached total unread count"""
        key = f"unread:{user_id}"
        count = await self.redis.get(key)
        return int(count) if count else 0
    
    async def increment_unread(self, user_id: str):
        """Increment unread count"""
        key = f"unread:{user_id}"
        await self.redis.incr(key)
    
    async def reset_unread(self, user_id: str):
        """Reset unread count (after recalculation)"""
        key = f"unread:{user_id}"
        await self.redis.set(key, 0)
```

**What to Cache:**
- User privacy settings (1 hour TTL)
- Conversation metadata (5 minutes TTL)
- Total unread counts (invalidate on read)
- Block lists (30 minutes TTL)
- Typing indicator state (10 seconds TTL)

**What NOT to Cache:**
- Individual messages (too volatile, storage intensive)
- Read receipts (need real-time accuracy)

### 4. Pagination Strategy

**Cursor-Based Pagination for Messages:**
```python
async def get_messages_cursor(
    conversation_id: str, 
    cursor: str = None, 
    page_size: int = 50
):
    """Cursor-based pagination for infinite scroll"""
    
    query = (
        select(Message)
        .where(
            and_(
                Message.conversation_id == conversation_id,
                Message.deleted_at.is_(None)
            )
        )
        .order_by(Message.created_at.desc())
    )
    
    # Apply cursor
    if cursor:
        cursor_time = datetime.fromisoformat(cursor)
        query = query.where(Message.created_at < cursor_time)
    
    query = query.limit(page_size + 1)
    
    messages = await db.execute(query)
    messages = messages.scalars().all()
    
    has_more = len(messages) > page_size
    if has_more:
        messages = messages[:page_size]
    
    next_cursor = messages[-1].created_at.isoformat() if has_more else None
    
    return {
        "messages": messages[::-1],  # Reverse to chronological
        "has_more": has_more,
        "next_cursor": next_cursor
    }
```

### 5. Connection Pooling

**Database Connection Pool:**
```python
# In database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=20,  # Increase for messaging load
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600  # Recycle hourly
)
```

**Redis Connection Pool:**
```python
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=50,
    decode_responses=True
)
redis_client = aioredis.Redis(connection_pool=redis_pool)
```


### 6. Bandwidth Optimization for African Markets

**Message Payload Minimization:**
```python
# Minimal message payload for real-time events
{
    "type": "new_message",
    "id": "uuid",
    "cid": "conversation_id",  # Shortened keys
    "s": "sender_id",
    "c": "content",
    "t": 1234567890,  # Unix timestamp
    "a": false  # has_attachment
}

# Full message details loaded separately on demand
```

**Image Optimization:**
```python
async def optimize_image_for_message(image_path: str) -> Tuple[str, str]:
    """
    Create optimized versions:
    - Thumbnail: 200x200, <50KB for preview
    - Full: Max 1200px width, <500KB
    """
    from PIL import Image
    import io
    
    img = Image.open(image_path)
    
    # Thumbnail
    thumb = img.copy()
    thumb.thumbnail((200, 200), Image.LANCZOS)
    thumb_buffer = io.BytesIO()
    thumb.save(thumb_buffer, format='JPEG', quality=70, optimize=True)
    thumb_url = await upload_to_storage(thumb_buffer, 'thumb')
    
    # Optimized full image
    if img.width > 1200:
        img.thumbnail((1200, 1200), Image.LANCZOS)
    
    full_buffer = io.BytesIO()
    img.save(full_buffer, format='JPEG', quality=80, optimize=True)
    full_url = await upload_to_storage(full_buffer, 'full')
    
    return thumb_url, full_url
```

**Audio Compression:**
```python
async def optimize_audio_for_message(audio_path: str) -> Tuple[str, str]:
    """
    Create two versions:
    - Preview: 64kbps MP3 for in-app playback
    - Full: Original quality for download
    """
    import subprocess
    
    # Convert to 64kbps preview
    preview_path = audio_path.replace('.', '_preview.')
    subprocess.run([
        'ffmpeg', '-i', audio_path,
        '-b:a', '64k',
        '-ar', '22050',  # Lower sample rate
        preview_path
    ])
    
    preview_url = await upload_to_storage(preview_path)
    full_url = await upload_to_storage(audio_path)
    
    return preview_url, full_url
```

## Security Considerations

### 1. Input Validation

**Message Content:**
```python
from bleach import clean
import html

def sanitize_message_content(content: str) -> str:
    """Sanitize message content"""
    # Remove HTML tags
    content = clean(content, tags=[], strip=True)
    
    # Escape HTML entities
    content = html.escape(content)
    
    # Trim whitespace
    content = content.strip()
    
    # Length validation
    if len(content) > 2000:
        raise ValueError("Message too long")
    
    if len(content) == 0:
        raise ValueError("Message cannot be empty")
    
    return content
```

**File Upload Validation:**
```python
async def validate_file_upload(file: UploadFile, file_type: str):
    """Comprehensive file validation"""
    
    # Check file extension
    ext = Path(file.filename).suffix.lower()
    allowed_exts = ATTACHMENT_CONFIG[file_type]["extensions"]
    
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {allowed_exts}"
        )
    
    # Check MIME type
    allowed_mimes = ATTACHMENT_CONFIG[file_type]["mime_types"]
    if file.content_type not in allowed_mimes:
        raise HTTPException(
            status_code=400,
            detail="Invalid MIME type"
        )
    
    # Check file size
    max_size = ATTACHMENT_CONFIG[file_type]["max_size_mb"] * 1024 * 1024
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max: {ATTACHMENT_CONFIG[file_type]['max_size_mb']}MB"
        )
    
    # Malware scan (if ClamAV available)
    if settings.MALWARE_SCAN_ENABLED:
        await scan_file_for_malware(file)
```

### 2. Authentication & Authorization

**WebSocket Authentication:**
```python
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

async def get_current_user_ws(websocket: WebSocket):
    """Authenticate WebSocket connection"""
    
    # Get token from query parameter
    token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token"
        )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        user = await user_service.get_user(user_id)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=401, detail="Invalid token")
```


**Conversation Access Control:**
```python
async def verify_conversation_access(
    conversation_id: str, 
    user_id: str
) -> bool:
    """Verify user has access to conversation"""
    
    participant = await db.execute(
        select(ConversationParticipant)
        .where(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.left_at.is_(None)
            )
        )
    )
    
    if not participant.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Access denied to conversation"
        )
    
    return True
```

### 3. Rate Limiting

**API Rate Limits:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/v1/messages")
@limiter.limit("30/minute")  # 30 messages per minute
async def send_message(request: Request, ...):
    pass

@router.post("/api/v1/messages/{message_id}/attachments")
@limiter.limit("10/minute")  # 10 file uploads per minute
async def upload_attachment(request: Request, ...):
    pass

@router.get("/api/v1/conversations")
@limiter.limit("60/minute")  # 60 list requests per minute
async def list_conversations(request: Request, ...):
    pass
```

**WebSocket Rate Limiting:**
```python
class RateLimitedWebSocketManager(ConnectionManager):
    def __init__(self):
        super().__init__()
        self.message_counts: Dict[str, List[float]] = {}
        self.typing_counts: Dict[str, List[float]] = {}
    
    async def check_rate_limit(
        self, user_id: str, 
        action: str, 
        limit: int, 
        window: int
    ) -> bool:
        """Check if user exceeded rate limit"""
        now = time.time()
        
        if action == "message":
            counts = self.message_counts
        elif action == "typing":
            counts = self.typing_counts
        else:
            return True
        
        if user_id not in counts:
            counts[user_id] = []
        
        # Remove old timestamps outside window
        counts[user_id] = [
            ts for ts in counts[user_id] 
            if now - ts < window
        ]
        
        # Check limit
        if len(counts[user_id]) >= limit:
            return False
        
        # Add current timestamp
        counts[user_id].append(now)
        return True
```

### 4. Data Encryption

**Encryption at Rest:**
- Database encryption: PostgreSQL TDE (Transparent Data Encryption)
- File storage encryption: Cloudflare R2/S3 server-side encryption (SSE)

**Encryption in Transit:**
- TLS 1.3 for all API endpoints
- WSS (WebSocket Secure) for real-time connections
- HTTPS-only file URLs with signed expiration

**Sensitive Data Handling:**
```python
# Do NOT log message content in production
logger.info(f"Message sent", extra={
    "user_id": user_id,
    "conversation_id": conversation_id,
    "message_length": len(content),
    # "content": content  # NEVER log this
})

# Redact content in error traces
def sanitize_error_message(error: Exception, context: Dict) -> Dict:
    """Remove sensitive data from error context"""
    safe_context = context.copy()
    if "content" in safe_context:
        safe_context["content"] = "[REDACTED]"
    if "attachment_url" in safe_context:
        safe_context["attachment_url"] = "[REDACTED]"
    return safe_context
```

### 5. Spam Prevention

**Automated Spam Detection (Future AI Integration):**
```python
async def check_spam_score(content: str, sender_id: str) -> float:
    """
    Calculate spam probability
    Future: Integrate with AI model
    """
    score = 0.0
    
    # Simple heuristics for now
    # Check for excessive caps
    if sum(1 for c in content if c.isupper()) / len(content) > 0.7:
        score += 0.3
    
    # Check for repeated characters
    if any(content.count(c * 5) for c in set(content)):
        score += 0.2
    
    # Check for URLs
    if "http://" in content or "https://" in content:
        score += 0.2
    
    # Check sender reputation (reported messages)
    reports = await get_user_report_count(sender_id)
    if reports > 5:
        score += 0.3
    
    return min(score, 1.0)

async def apply_spam_filters(
    content: str, 
    sender_id: str, 
    recipient_id: str
):
    """Apply spam filtering"""
    
    spam_score = await check_spam_score(content, sender_id)
    
    # Auto-flag high spam score
    if spam_score > 0.8:
        # Create automatic report
        await privacy_service.report_message(
            reporter_id="system",
            message_id=message_id,
            reason="spam",
            details=f"Auto-detected spam (score: {spam_score})"
        )
    
    return spam_score
```


## Error Handling

### Error Response Format

Consistent error responses across all endpoints:

```python
from pydantic import BaseModel
from typing import Optional

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: str
    code: str
    timestamp: datetime
    request_id: Optional[str]

# Example error response
{
    "error": "Forbidden",
    "detail": "You cannot message this user",
    "code": "BLOCKED_USER",
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
}
```

### Error Codes

```python
class MessageError(str, enum.Enum):
    """Message-specific error codes"""
    BLOCKED_USER = "BLOCKED_USER"
    USER_NOT_ACCEPTING_MESSAGES = "USER_NOT_ACCEPTING_MESSAGES"
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    MESSAGE_NOT_FOUND = "MESSAGE_NOT_FOUND"
    INVALID_MESSAGE_CONTENT = "INVALID_MESSAGE_CONTENT"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    EDIT_WINDOW_EXPIRED = "EDIT_WINDOW_EXPIRED"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SPAM_DETECTED = "SPAM_DETECTED"
```

### Exception Handlers

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "detail": str(exc),
            "code": getattr(exc, "code", "UNKNOWN"),
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request.state.request_id
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request.state.request_id
        }
    )
```

### Graceful WebSocket Error Handling

```python
async def websocket_error_handler(websocket: WebSocket, error: Exception):
    """Handle WebSocket errors gracefully"""
    
    error_message = {
        "type": "error",
        "error": str(error),
        "code": getattr(error, "code", "WS_ERROR")
    }
    
    try:
        await websocket.send_json(error_message)
    except:
        # Connection already closed
        pass
    
    # Log error
    logger.error(f"WebSocket error: {error}", exc_info=True)
    
    # Close connection with appropriate code
    if isinstance(error, HTTPException):
        if error.status_code == 401:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        elif error.status_code == 403:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        else:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    else:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
```

### Retry Logic for File Uploads

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def upload_with_retry(file: UploadFile, storage_path: str):
    """Upload file with automatic retry"""
    try:
        return await file_storage.upload_to_cloud(file, storage_path)
    except Exception as e:
        logger.warning(f"Upload attempt failed: {e}")
        raise
```

## Testing Strategy

### Unit Tests

**Test Coverage Areas:**

1. **Service Layer Tests** - Test business logic in isolation
   ```python
   # test_messaging_service.py
   async def test_send_message_creates_conversation():
       """Test message creation when conversation doesn't exist"""
       
   async def test_send_message_respects_block():
       """Test blocked users cannot send messages"""
       
   async def test_mark_conversation_read_updates_count():
       """Test unread count decreases when messages read"""
   ```

2. **Privacy Service Tests** - Test filtering and blocking logic
   ```python
   # test_privacy_service.py
   async def test_message_request_for_non_follower():
       """Test message request created for non-followers"""
       
   async def test_verified_only_filter():
       """Test verified-only filter blocks non-verified users"""
       
   async def test_block_hides_conversations():
       """Test blocking hides existing conversations"""
   ```


3. **Validation Tests** - Test input sanitization and validation
   ```python
   # test_validation.py
   def test_sanitize_message_content():
       """Test HTML stripping and escaping"""
       
   def test_message_length_validation():
       """Test 2000 character limit enforcement"""
       
   async def test_file_type_validation():
       """Test file extension and MIME type checks"""
   ```

4. **Database Model Tests** - Test ORM relationships and constraints
   ```python
   # test_models.py
   async def test_conversation_cascade_delete():
       """Test deleting conversation deletes messages"""
       
   async def test_unique_block_constraint():
       """Test cannot block same user twice"""
   ```

### Integration Tests

**API Endpoint Tests:**
```python
from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_send_message_flow(client: AsyncClient, auth_token: str):
    """Test complete message sending flow"""
    
    # Create conversation
    response = await client.post(
        "/api/v1/conversations",
        json={"recipient_id": "user123"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    conversation_id = response.json()["id"]
    
    # Send message
    response = await client.post(
        "/api/v1/messages",
        json={
            "conversation_id": conversation_id,
            "content": "Hello!"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    message = response.json()
    assert message["content"] == "Hello!"
    
    # Retrieve messages
    response = await client.get(
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()["messages"]) == 1

@pytest.mark.asyncio
async def test_file_attachment_flow(client: AsyncClient, auth_token: str):
    """Test file upload and retrieval"""
    
    # Create message
    message_response = await client.post(
        "/api/v1/messages",
        json={"recipient_id": "user123", "content": "Check this out"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    message_id = message_response.json()["id"]
    
    # Upload attachment
    with open("test_image.jpg", "rb") as f:
        response = await client.post(
            f"/api/v1/messages/{message_id}/attachments",
            files={"file": ("test.jpg", f, "image/jpeg")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    assert response.status_code == 201
    attachment = response.json()
    assert attachment["file_type"] == "image"
    assert attachment["storage_url"] is not None
```

### WebSocket Tests

```python
from fastapi.testclient import TestClient

def test_websocket_typing_indicator():
    """Test typing indicator broadcast"""
    
    client = TestClient(app)
    
    with client.websocket_connect(
        f"/ws/conversations?token={auth_token}"
    ) as websocket:
        # Send typing start
        websocket.send_json({
            "type": "typing_start",
            "conversation_id": "conv123"
        })
        
        # Should receive echo (broadcast to others)
        data = websocket.receive_json()
        assert data["type"] == "typing_indicator"
        assert data["is_typing"] is True

def test_websocket_new_message_broadcast():
    """Test message broadcast to conversation participants"""
    pass
```

### Performance Tests

```python
import asyncio
from locust import HttpUser, task, between

class MessagingUser(HttpUser):
    """Load test for messaging system"""
    wait_time = between(1, 3)
    
    @task(3)
    def send_message(self):
        """Send message (most frequent action)"""
        self.client.post(
            "/api/v1/messages",
            json={
                "recipient_id": "user123",
                "content": "Test message"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def list_conversations(self):
        """List conversations"""
        self.client.get(
            "/api/v1/conversations",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def get_messages(self):
        """Get messages from conversation"""
        self.client.get(
            f"/api/v1/conversations/{self.conversation_id}/messages",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

**Performance Benchmarks:**
- API response time: < 200ms for conversation list
- API response time: < 300ms for message list with 50 items
- WebSocket latency: < 100ms for message broadcast
- File upload: < 5s for 10MB file
- Database query time: < 50ms for conversation list query

### Security Tests

```python
async def test_blocked_user_cannot_send_message():
    """Test block enforcement"""
    # Block user
    await privacy_service.block_user(user1_id, user2_id)
    
    # Attempt to send message
    with pytest.raises(HTTPException) as exc:
        await messaging_service.send_message(
            sender_id=user2_id,
            recipient_id=user1_id,
            content="Hello"
        )
    assert exc.value.status_code == 403

async def test_unauthorized_conversation_access():
    """Test access control"""
    # Try to access conversation user is not part of
    with pytest.raises(HTTPException) as exc:
        await messaging_service.get_conversation(
            conversation_id="conv123",
            user_id="unauthorized_user"
        )
    assert exc.value.status_code == 403

async def test_xss_prevention():
    """Test XSS attack prevention"""
    malicious_content = '<script>alert("XSS")</script>'
    
    sanitized = sanitize_message_content(malicious_content)
    assert '<script>' not in sanitized
    assert '&lt;script&gt;' in sanitized
```

This comprehensive design provides a solid foundation for implementing the messaging system with performance, security, and scalability in mind, specifically optimized for the African market's bandwidth constraints and user needs.


## Correctness Properties

**Property-Based Testing Applicability Assessment:**

After analyzing the messaging system requirements, property-based testing (PBT) is **NOT the primary testing approach** for this feature. Here's why:

**Nature of the System:**
- **Infrastructure-Heavy**: WebSocket connections, database operations, file storage, external service integrations
- **State-Dependent**: Message ordering, read receipts, conversation state transitions
- **External Dependencies**: File storage (R2/S3), notification service, database transactions
- **Side-Effect Driven**: Creating notifications, updating unread counts, broadcasting events

**Testing Strategy Instead:**
1. **Integration Tests**: Test API endpoints with real database and services
2. **Unit Tests**: Test business logic in services (privacy rules, validation, filtering)
3. **WebSocket Tests**: Test real-time event broadcasting and connection management
4. **Performance Tests**: Load testing for scalability verification
5. **Security Tests**: Authentication, authorization, input validation, XSS prevention

**Example-Based Unit Test Coverage:**

While PBT is not the primary strategy, we will write comprehensive unit tests for key behaviors:

```python
# Message validation
def test_empty_message_rejected()
def test_message_over_2000_chars_rejected()
def test_html_content_sanitized()

# Privacy rules
async def test_follower_filter_blocks_non_followers()
async def test_verified_filter_blocks_unverified()
async def test_blocked_user_cannot_message()
async def test_block_hides_conversations()

# Message requests
async def test_message_request_created_for_non_follower()
async def test_accepting_request_converts_to_conversation()
async def test_declining_request_hides_conversation()

# Read receipts
async def test_marking_message_read_creates_receipt()
async def test_unread_count_decrements_on_read()
async def test_read_receipts_hidden_when_disabled()

# File attachments
async def test_valid_image_upload_succeeds()
async def test_oversized_file_rejected()
async def test_invalid_file_type_rejected()
async def test_attachment_metadata_extracted()
```

**Why No Correctness Properties:**

The messaging system does not exhibit the universal properties that benefit from randomized input testing across 100+ iterations:

- **Conversation creation** is idempotent with specific user pairs (not generalizable)
- **Message sending** depends on block status, privacy settings, and existing relationships
- **Read receipts** are state transitions, not pure functions
- **File uploads** involve external storage with error conditions
- **WebSocket broadcasting** depends on active connections

These behaviors are best verified through targeted integration and unit tests with specific scenarios rather than property-based generative testing.
