"""
Messaging System API Endpoints
Wave 8-11: REST API for conversations, messages, privacy, and settings
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.messaging import (
    # Conversation schemas
    CreateConversationRequest, ConversationResponse, ConversationListResponse,
    # Message schemas
    SendMessageRequest, UpdateMessageRequest, MessageResponse, MessageListResponse,
    # Privacy schemas
    UpdateSettingsRequest, SettingsResponse, BlockUserRequest, 
    BlockedUsersListResponse, ReportMessageRequest, ReportMessageResponse,
    # Response schemas
    SuccessResponse, UnreadCountResponse
)
from app.services.messaging_service import MessagingService
from app.services.privacy_service import PrivacyService
from app.services.file_attachment_service import FileAttachmentService
from app.services.websocket_manager import connection_manager

router = APIRouter(prefix="/messaging", tags=["Messaging"])

# ============================================================================
# WAVE 8: CONVERSATION ENDPOINTS
# ============================================================================

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    unread_only: bool = Query(False, description="Show only unread conversations"),
    search: Optional[str] = Query(None, description="Search by participant name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List user's conversations with pagination and filtering
    
    **Features:**
    - Paginated list ordered by last activity
    - Filter by unread status
    - Search by participant names
    - Shows unread count per conversation
    - Displays last message preview
    
    **Returns:**
    - List of conversations with metadata
    - Pagination info (total, pages, etc.)
    """
    messaging_service = MessagingService(db)
    
    result = messaging_service.list_conversations(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        unread_only=unread_only,
        search=search
    )
    
    return ConversationListResponse(**result)


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_or_get_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new conversation or get existing one
    
    **Behavior:**
    - If conversation exists, returns existing conversation
    - If no conversation exists, creates new one
    - May create message request based on recipient's privacy settings
    
    **Privacy Rules:**
    - Checks if users have blocked each other
    - Respects recipient's message filter settings
    - Creates message request for non-followers if required
    
    **Returns:**
    - Conversation object with `is_message_request` flag
    """
    messaging_service = MessagingService(db)
    
    conversation = messaging_service.get_or_create_conversation(
        user_id=current_user.id,
        recipient_id=request.recipient_id
    )
    
    # Build response
    conv_response = messaging_service._build_conversation_response(
        conversation,
        current_user.id
    )
    
    return conv_response


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation details by ID
    
    **Access Control:**
    - Only participants can view conversation
    - Returns 403 if user is not a participant
    
    **Returns:**
    - Full conversation details
    - Participant information
    - Last message preview
    - Unread count for current user
    """
    messaging_service = MessagingService(db)
    
    conversation = messaging_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    conv_response = messaging_service._build_conversation_response(
        conversation,
        current_user.id
    )
    
    return conv_response


@router.delete("/conversations/{conversation_id}", response_model=SuccessResponse)
async def leave_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Leave a conversation (soft delete)
    
    **Behavior:**
    - Sets `left_at` timestamp for current user
    - Conversation hidden from user's list
    - Does not delete messages or conversation
    - Other participants unaffected
    
    **Returns:**
    - Success confirmation
    """
    messaging_service = MessagingService(db)
    
    # Verify access and get conversation
    conversation = messaging_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    # Get participant record
    from app.models.messaging import ConversationParticipant
    from datetime import datetime
    
    participant = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.id
        )
        .first()
    )
    
    if participant:
        participant.left_at = datetime.utcnow()
        db.commit()
    
    return SuccessResponse(message="Successfully left conversation")


# ============================================================================
# WAVE 9: MESSAGE ENDPOINTS
# ============================================================================

@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    conversation_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get messages in a conversation
    
    **Features:**
    - Cursor-based pagination for infinite scroll
    - Returns messages ordered oldest to newest
    - Includes sender info and attachments
    - Shows read receipts
    
    **Pagination:**
    - Use `cursor` for infinite scroll (more efficient)
    - Or use `page` for traditional pagination
    - `has_more` indicates if more messages available
    - `next_cursor` for loading older messages
    
    **Returns:**
    - List of messages with full details
    - Pagination metadata
    """
    messaging_service = MessagingService(db)
    
    result = messaging_service.get_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        cursor=cursor
    )
    
    return MessageListResponse(**result)


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a new message
    
    **Required:**
    - Either `conversation_id` OR `recipient_id` (not both)
    - `content` (1-2000 characters, trimmed)
    
    **Privacy Checks:**
    - Validates users haven't blocked each other
    - Respects recipient's message filter settings
    - Creates message request if needed
    
    **Side Effects:**
    - Updates conversation `last_activity_at`
    - Updates `last_message_preview`
    - Increments unread count for recipients
    - Triggers WebSocket broadcast (if recipient online)
    - Creates notification (if recipient offline/inactive)
    
    **Returns:**
    - Created message with full details
    """
    messaging_service = MessagingService(db)
    
    message = messaging_service.send_message(
        sender_id=current_user.id,
        content=request.content,
        recipient_id=request.recipient_id,
        conversation_id=request.conversation_id
    )
    
    # Build response
    message_response = messaging_service._build_message_response(message)
    
    # Get conversation participants
    from app.models.messaging import ConversationParticipant
    participants = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == message.conversation_id,
            ConversationParticipant.left_at.is_(None)
        )
        .all()
    )
    participant_ids = [p.user_id for p in participants]
    
    # Broadcast via WebSocket to conversation participants (non-blocking)
    try:
        await connection_manager.broadcast_new_message(
            conversation_id=message.conversation_id,
            participant_ids=participant_ids,
            message_response=message_response
        )
    except Exception as e:
        # Log error but don't block message sending
        print(f"⚠️ WebSocket broadcast failed: {e}")
    
    # Create notification for offline/inactive recipients
    try:
        from app.services.notification_service import NotificationService
        notification_service = NotificationService(db)
        
        for participant_id in participant_ids:
            # Skip sender
            if participant_id == current_user.id:
                continue
            
            # Check if recipient is online and viewing the conversation
            is_viewing = connection_manager.is_user_viewing_conversation(
                participant_id,
                message.conversation_id
            )
            
            # Only send notification if recipient is not actively viewing
            if not is_viewing:
                # Create message preview (first 50 chars)
                preview = message.content[:50]
                if len(message.content) > 50:
                    preview += "..."
                
                notification_service.create_notification(
                    user_id=participant_id,
                    notification_type="new_message",
                    title=f"New message from @{current_user.username}",
                    message=preview,
                    data={
                        "sender_id": current_user.id,
                        "sender_username": current_user.username,
                        "conversation_id": message.conversation_id,
                        "message_id": message.id
                    }
                )
    except Exception as e:
        # Log error but don't block message sending
        print(f"⚠️ Notification creation failed: {e}")
    
    return message_response


@router.put("/messages/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: str,
    request: UpdateMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit a message
    
    **Restrictions:**
    - Only sender can edit
    - Must edit within 15 minutes of creation
    - Cannot edit deleted messages
    
    **Behavior:**
    - Sets `is_edited` flag to true
    - Updates `updated_at` timestamp
    - Broadcasts edit via WebSocket
    
    **Returns:**
    - Updated message with `is_edited=true`
    """
    messaging_service = MessagingService(db)
    
    message = messaging_service.edit_message(
        message_id=message_id,
        user_id=current_user.id,
        new_content=request.content
    )
    
    message_response = messaging_service._build_message_response(message)
    
    # Broadcast edit via WebSocket
    from app.models.messaging import ConversationParticipant
    participants = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == message.conversation_id,
            ConversationParticipant.left_at.is_(None)
        )
        .all()
    )
    participant_ids = [p.user_id for p in participants]
    
    # Broadcast edit via WebSocket (non-blocking)
    try:
        await connection_manager.broadcast_message_edit(
            conversation_id=message.conversation_id,
            participant_ids=participant_ids,
            message_response=message_response
        )
    except Exception as e:
        print(f"⚠️ WebSocket broadcast failed: {e}")
    
    return message_response


@router.delete("/messages/{message_id}", response_model=SuccessResponse)
async def delete_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a message (soft delete)
    
    **Restrictions:**
    - Only sender can delete
    - Cannot delete already deleted messages
    
    **Behavior:**
    - Sets `deleted_at` timestamp
    - Replaces content with "[Message deleted]"
    - Message still visible but content hidden
    - Broadcasts deletion via WebSocket
    
    **Returns:**
    - Success confirmation
    """
    messaging_service = MessagingService(db)
    
    # Get message before deletion for WebSocket broadcast
    from app.models.messaging import Message
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    conversation_id = message.conversation_id
    
    messaging_service.delete_message(
        message_id=message_id,
        user_id=current_user.id
    )
    
    # Broadcast deletion via WebSocket
    from app.models.messaging import ConversationParticipant
    participants = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.left_at.is_(None)
        )
        .all()
    )
    participant_ids = [p.user_id for p in participants]
    
    # Broadcast deletion via WebSocket (non-blocking)
    try:
        await connection_manager.broadcast_message_delete(
            conversation_id=conversation_id,
            participant_ids=participant_ids,
            message_id=message_id,
            sender_id=current_user.id
        )
    except Exception as e:
        print(f"⚠️ WebSocket broadcast failed: {e}")
    
    return SuccessResponse(message="Message deleted successfully")


@router.post("/messages/{message_id}/read", response_model=SuccessResponse)
async def mark_message_read(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a message as read
    
    **Behavior:**
    - Creates read receipt with timestamp
    - Updates conversation unread count
    - Broadcasts read receipt via WebSocket (if sender has receipts enabled)
    
    **Privacy:**
    - Read receipt only visible to sender if recipient has receipts enabled
    - Timestamp always recorded internally regardless of settings
    
    **Returns:**
    - Success confirmation
    """
    messaging_service = MessagingService(db)
    
    # Get message for sender info
    from app.models.messaging import Message
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    messaging_service.mark_message_read(
        message_id=message_id,
        user_id=current_user.id
    )
    
    # Broadcast read receipt via WebSocket (non-blocking)
    try:
        from datetime import datetime
        await connection_manager.broadcast_read_receipt(
            message_id=message_id,
            sender_id=message.sender_id,
            reader_id=current_user.id,
            read_at=datetime.utcnow()
        )
    except Exception as e:
        print(f"⚠️ WebSocket broadcast failed: {e}")
    
    return SuccessResponse(message="Message marked as read")


@router.post("/conversations/{conversation_id}/mark-read", response_model=SuccessResponse)
async def mark_conversation_read(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all messages in conversation as read
    
    **Behavior:**
    - Marks all unread messages as read
    - Resets unread count to 0
    - Updates `last_read_at` timestamp
    - Broadcasts read receipts via WebSocket
    
    **Returns:**
    - Success message with count of messages marked
    """
    messaging_service = MessagingService(db)
    
    count = messaging_service.mark_conversation_read(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    return SuccessResponse(message=f"Marked {count} messages as read")


@router.post("/messages/{message_id}/attachments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    message_id: str,
    file: UploadFile = File(...),
    file_type: str = Query(..., description="File type: image, audio, document, voice_note"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload file attachment to a message
    
    **File Types & Limits:**
    - `image`: jpg, png, gif, webp (max 10MB)
    - `audio`: mp3, wav, m4a, ogg (max 25MB)
    - `document`: pdf, doc, docx (max 10MB)
    - `voice_note`: mp3, wav, m4a, ogg, webm (max 5MB)
    
    **Processing:**
    - Images: Generates 200x200 thumbnail, extracts dimensions
    - Audio: Extracts duration in seconds
    - Documents: Stored as-is with metadata
    
    **Returns:**
    - Attachment metadata (URL, size, dimensions, duration, etc.)
    """
    # Verify message exists and user owns it
    from app.models.messaging import Message
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add attachments to your own messages"
        )
    
    # Upload attachment
    attachment_service = FileAttachmentService(db)
    attachment = await attachment_service.upload_message_attachment(
        file=file,
        message_id=message_id,
        file_type=file_type
    )
    
    return {
        "message": "Attachment uploaded successfully",
        "attachment": attachment_service.build_attachment_response(attachment).dict()
    }


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    conversation_id: Optional[str] = Query(None, description="Specific conversation ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unread message count
    
    **Options:**
    - Without `conversation_id`: Returns total across all conversations
    - With `conversation_id`: Returns count for specific conversation
    
    **Returns:**
    - Unread count (and total if applicable)
    """
    messaging_service = MessagingService(db)
    
    result = messaging_service.get_unread_count(
        user_id=current_user.id,
        conversation_id=conversation_id
    )
    
    return result


# ============================================================================
# WAVE 10: MESSAGE REQUEST ENDPOINTS
# ============================================================================

@router.get("/message-requests", response_model=ConversationListResponse)
async def list_message_requests(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List pending message requests
    
    **Returns:**
    - Conversations where `is_message_request=true`
    - Only shows `request_status='pending'`
    - Ordered by most recent
    """
    from app.models.messaging import Conversation, ConversationParticipant
    
    # Query message requests
    query = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.user_id == current_user.id,
            ConversationParticipant.left_at.is_(None)
        )
        .join(Conversation)
        .filter(
            Conversation.is_message_request == True,
            Conversation.request_status == "pending"
        )
        .order_by(Conversation.last_activity_at.desc())
    )
    
    total = query.count()
    offset = (page - 1) * page_size
    participants = query.offset(offset).limit(page_size).all()
    
    # Build conversation responses
    messaging_service = MessagingService(db)
    conversations = []
    for participant in participants:
        conv_response = messaging_service._build_conversation_response(
            participant.conversation,
            current_user.id
        )
        conversations.append(conv_response)
    
    total_pages = (total + page_size - 1) // page_size
    
    return ConversationListResponse(
        conversations=conversations,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/message-requests/{conversation_id}/accept", response_model=ConversationResponse)
async def accept_message_request(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accept a message request
    
    **Behavior:**
    - Updates `request_status` to 'accepted'
    - Sets `is_message_request` to false
    - Converts to normal conversation
    - Allows continued messaging
    
    **Returns:**
    - Updated conversation object
    """
    privacy_service = PrivacyService(db)
    
    conversation = privacy_service.accept_message_request(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    # TODO: Notify sender via notification service
    
    messaging_service = MessagingService(db)
    conv_response = messaging_service._build_conversation_response(
        conversation,
        current_user.id
    )
    
    return conv_response


@router.post("/message-requests/{conversation_id}/decline", response_model=SuccessResponse)
async def decline_message_request(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Decline a message request
    
    **Behavior:**
    - Updates `request_status` to 'declined'
    - Hides conversation from both users
    - Sets `left_at` for both participants
    - Prevents further messages without new request
    
    **Returns:**
    - Success confirmation
    """
    privacy_service = PrivacyService(db)
    
    privacy_service.decline_message_request(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    return SuccessResponse(message="Message request declined")


# ============================================================================
# WAVE 11: PRIVACY & SETTINGS ENDPOINTS
# ============================================================================

@router.get("/settings", response_model=SettingsResponse)
async def get_messaging_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's message privacy settings
    
    **Settings:**
    - `message_filter`: everyone, followers, verified, none
    - `read_receipts_enabled`: Show read receipts to senders
    - `typing_indicators_enabled`: Show typing indicators
    
    **Returns:**
    - Current settings (creates defaults if not set)
    """
    privacy_service = PrivacyService(db)
    
    settings = privacy_service.get_user_settings(current_user.id)
    
    return SettingsResponse.from_orm(settings)


@router.put("/settings", response_model=SettingsResponse)
async def update_messaging_settings(
    request: UpdateSettingsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update message privacy settings
    
    **Updatable Fields:**
    - `message_filter`: Controls who can message you
      - `everyone`: Anyone can send messages
      - `followers`: Only followers can send messages
      - `verified`: Only verified users can send messages
      - `none`: No one can send messages (message requests disabled)
    - `read_receipts_enabled`: Toggle read receipt visibility
    - `typing_indicators_enabled`: Toggle typing indicator broadcasting
    
    **Returns:**
    - Updated settings
    """
    privacy_service = PrivacyService(db)
    
    settings_dict = request.dict(exclude_unset=True)
    settings = privacy_service.update_user_settings(
        user_id=current_user.id,
        settings_dict=settings_dict
    )
    
    return SettingsResponse.from_orm(settings)


@router.post("/block", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def block_user(
    request: BlockUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Block a user
    
    **Effects:**
    - Prevents blocked user from sending messages
    - Hides all existing conversations between users
    - Both users lose access to conversations
    
    **Returns:**
    - Success confirmation
    """
    privacy_service = PrivacyService(db)
    
    privacy_service.block_user(
        blocker_id=current_user.id,
        blocked_id=request.user_id,
        reason=request.reason
    )
    
    return SuccessResponse(message="User blocked successfully")


@router.delete("/block/{user_id}", response_model=SuccessResponse)
async def unblock_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unblock a user
    
    **Effects:**
    - Removes block record
    - Restores access to existing conversations
    - Clears `left_at` timestamps
    - Allows new messages
    
    **Returns:**
    - Success confirmation
    """
    privacy_service = PrivacyService(db)
    
    privacy_service.unblock_user(
        blocker_id=current_user.id,
        blocked_id=user_id
    )
    
    return SuccessResponse(message="User unblocked successfully")


@router.get("/blocked-users", response_model=BlockedUsersListResponse)
async def get_blocked_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List blocked users
    
    **Returns:**
    - Paginated list of blocked users
    - Includes user info and block reason
    - Ordered by most recently blocked
    """
    privacy_service = PrivacyService(db)
    
    result = privacy_service.get_blocked_users(
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    
    return BlockedUsersListResponse(**result)


@router.post("/messages/{message_id}/report", response_model=ReportMessageResponse, status_code=status.HTTP_201_CREATED)
async def report_message(
    message_id: str,
    request: ReportMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Report a message for admin review
    
    **Report Reasons:**
    - `spam`: Unsolicited messages
    - `harassment`: Abusive or threatening content
    - `inappropriate`: Offensive or explicit content
    - `other`: Other violations
    
    **Behavior:**
    - Creates report record
    - Does NOT notify reported user
    - Queued for admin review
    
    **Returns:**
    - Report confirmation with ID
    """
    privacy_service = PrivacyService(db)
    
    report = privacy_service.report_message(
        reporter_id=current_user.id,
        message_id=message_id,
        reason=request.reason.value,
        details=request.details
    )
    
    return ReportMessageResponse.from_orm(report)
