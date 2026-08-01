"""
Messaging System Schemas - Pydantic models for request/response validation
Tasks 3.1, 3.2, 3.3: Request/Response DTOs for messaging system
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class MessageFilterEnum(str, Enum):
    """Message filter options for privacy settings"""
    EVERYONE = "everyone"
    FOLLOWERS = "followers"
    VERIFIED = "verified"
    NONE = "none"


class RequestStatusEnum(str, Enum):
    """Message request status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class ReportReasonEnum(str, Enum):
    """Message report reasons"""
    SPAM = "spam"
    HARASSMENT = "harassment"
    INAPPROPRIATE = "inappropriate"
    OTHER = "other"


class FileTypeEnum(str, Enum):
    """Attachment file types"""
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"
    VOICE_NOTE = "voice_note"


# ============================================================================
# SHARED/NESTED SCHEMAS
# ============================================================================

class UserBasicInfo(BaseModel):
    """Basic user info for participants"""
    user_id: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str] = None
    is_verified: bool = False
    
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
    duration: Optional[int] = None  # for audio/voice notes (seconds)
    width: Optional[int] = None  # for images
    height: Optional[int] = None  # for images
    thumbnail_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LastMessagePreview(BaseModel):
    """Preview of last message in conversation"""
    id: str
    content: str
    sender_id: str
    created_at: datetime
    has_attachment: bool = False
    
    class Config:
        from_attributes = True


# ============================================================================
# MESSAGE REQUEST SCHEMAS (Task 3.1)
# ============================================================================

class SendMessageRequest(BaseModel):
    """Request to send a new message"""
    recipient_id: Optional[str] = Field(None, min_length=36, max_length=36)
    conversation_id: Optional[str] = Field(None, min_length=36, max_length=36)
    content: str = Field(..., min_length=1, max_length=2000)
    
    @validator('content')
    def validate_content(cls, v):
        """Ensure message content is not empty or whitespace"""
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty or whitespace')
        return v.strip()
    
    @validator('conversation_id', always=True)
    def validate_ids(cls, v, values):
        """Ensure either recipient_id or conversation_id is provided"""
        recipient_id = values.get('recipient_id')
        if not v and not recipient_id:
            raise ValueError('Either recipient_id or conversation_id must be provided')
        return v


class UpdateMessageRequest(BaseModel):
    """Request to edit message content"""
    content: str = Field(..., min_length=1, max_length=2000)
    
    @validator('content')
    def validate_content(cls, v):
        """Ensure message content is not empty or whitespace"""
        if not v or not v.strip():
            raise ValueError('Message content cannot be empty or whitespace')
        return v.strip()


class MessageResponse(BaseModel):
    """Message response"""
    id: str
    conversation_id: str
    sender_id: str
    sender: UserBasicInfo
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_edited: bool = False
    read_by: List[str] = []  # List of user IDs who read the message
    attachments: List[AttachmentResponse] = []
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Paginated list of messages"""
    messages: List[MessageResponse]
    has_more: bool
    next_cursor: Optional[str] = None
    total: Optional[int] = None


# ============================================================================
# CONVERSATION REQUEST SCHEMAS (Task 3.2)
# ============================================================================

class CreateConversationRequest(BaseModel):
    """Request to create or get conversation"""
    recipient_id: str = Field(..., min_length=36, max_length=36)
    
    @validator('recipient_id')
    def validate_recipient_id(cls, v):
        """Ensure recipient_id is a valid UUID format"""
        if not v or len(v) != 36:
            raise ValueError('recipient_id must be a valid UUID (36 characters)')
        return v


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: str
    participants: List[UserBasicInfo]
    last_message: Optional[LastMessagePreview] = None
    unread_count: int = 0
    is_message_request: bool = False
    request_status: Optional[str] = None
    last_activity_at: datetime
    is_archived: bool = False
    is_muted: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Paginated list of conversations"""
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# PRIVACY AND SETTINGS SCHEMAS (Task 3.3)
# ============================================================================

class UpdateSettingsRequest(BaseModel):
    """Update message privacy settings"""
    message_filter: Optional[MessageFilterEnum] = None
    read_receipts_enabled: Optional[bool] = None
    typing_indicators_enabled: Optional[bool] = None


class SettingsResponse(BaseModel):
    """User message settings response"""
    id: str
    user_id: str
    message_filter: str
    read_receipts_enabled: bool
    typing_indicators_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BlockUserRequest(BaseModel):
    """Block a user"""
    user_id: str = Field(..., min_length=36, max_length=36)
    reason: Optional[str] = Field(None, max_length=500)
    
    @validator('reason')
    def validate_reason(cls, v):
        """Trim whitespace from reason"""
        if v:
            return v.strip()
        return v


class BlockedUserResponse(BaseModel):
    """Blocked user response"""
    id: str
    blocker_id: str
    blocked_id: str
    blocked_user: UserBasicInfo
    blocked_at: datetime
    reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class BlockedUsersListResponse(BaseModel):
    """Paginated list of blocked users"""
    blocked_users: List[BlockedUserResponse]
    total: int
    page: int
    page_size: int


class ReportMessageRequest(BaseModel):
    """Report a message"""
    reason: ReportReasonEnum
    details: Optional[str] = Field(None, max_length=500)
    
    @validator('details')
    def validate_details(cls, v):
        """Trim whitespace from details"""
        if v:
            return v.strip()
        return v


class ReportMessageResponse(BaseModel):
    """Message report response"""
    id: str
    message_id: str
    reporter_id: str
    reason: str
    details: Optional[str] = None
    created_at: datetime
    reviewed: bool = False
    
    class Config:
        from_attributes = True


# ============================================================================
# WEBSOCKET EVENT SCHEMAS
# ============================================================================

class TypingIndicatorEvent(BaseModel):
    """Typing indicator WebSocket event"""
    type: str = "typing_indicator"
    conversation_id: str
    user_id: str
    is_typing: bool


class NewMessageEvent(BaseModel):
    """New message WebSocket event"""
    type: str = "new_message"
    conversation_id: str
    message: MessageResponse


class MessageReadEvent(BaseModel):
    """Message read WebSocket event"""
    type: str = "message_read"
    message_id: str
    read_by: str
    read_at: datetime


class UserStatusEvent(BaseModel):
    """User online/offline status event"""
    type: str  # "user_online" or "user_offline"
    user_id: str


# ============================================================================
# SEARCH AND FILTER SCHEMAS
# ============================================================================

class SearchMessagesRequest(BaseModel):
    """Search messages request"""
    query: str = Field(..., min_length=1, max_length=200)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class SearchConversationsRequest(BaseModel):
    """Search conversations request"""
    query: str = Field(..., min_length=1, max_length=200)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


# ============================================================================
# GENERIC RESPONSE SCHEMAS
# ============================================================================

class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    success: bool = True


class UnreadCountResponse(BaseModel):
    """Unread message count response"""
    conversation_id: Optional[str] = None
    unread_count: int
    total_unread: Optional[int] = None  # Total across all conversations
