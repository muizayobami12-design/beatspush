"""
Messaging Notification Helpers

Helper functions for triggering notifications when messages are sent.
Integrates with BeatsPush's existing NotificationService and WebSocket ConnectionManager.

Requirements covered:
- 10.1: New message notification triggered
- 10.2: Message preview in notification
- 10.3: Notification includes sender info
- 10.4: Notification preferences respected
- 10.5: Skip if user viewing conversation
- 10.6: Message request notifications
- 10.7: Notification batching logic
- 10.8: No notification for own messages
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.models.messaging import Message, Conversation
from app.models.user import User
from app.services.notification_service import NotificationService
from app.services.websocket_manager import connection_manager


# ============================================================================
# HELPER: Check User Notification Preferences
# ============================================================================

def should_create_notification(recipient_id: str, db: Session) -> bool:
    """
    Check if user has message notifications enabled.
    
    Queries user's notification preferences via NotificationService.
    Returns False only if user explicitly disabled message notifications.
    
    Args:
        recipient_id: ID of notification recipient
        db: Database session
    
    Returns:
        bool: True if notification should be created, False if user disabled them
    """
    try:
        notification_service = NotificationService(db)
        prefs = notification_service.get_or_create_preferences(recipient_id)
        
        # Check if new_message notifications are enabled
        # Default to True if not found (backward compatibility)
        is_enabled = getattr(prefs, 'newmessage', True)
        
        return is_enabled
    except Exception as e:
        # Log error but default to creating notification
        print(f"⚠️ Error checking notification preferences: {e}")
        return True


# ============================================================================
# HELPER: Check if User is Actively Viewing Conversation
# ============================================================================

def is_user_active_in_conversation(conversation_id: str, recipient_id: str, db: Session) -> bool:
    """
    Check if user is currently viewing this conversation.
    
    Queries ConnectionManager.active_conversations to see if user has
    active WebSocket connection to this specific conversation.
    
    Args:
        conversation_id: ID of conversation to check
        recipient_id: ID of user to check
        db: Database session (not used but included for consistency)
    
    Returns:
        bool: True if user has active WebSocket in conversation, False otherwise
    """
    try:
        return connection_manager.is_user_viewing_conversation(
            user_id=recipient_id,
            conversation_id=conversation_id
        )
    except Exception as e:
        # Log error but default to False (safe to send notification)
        print(f"⚠️ Error checking active conversations: {e}")
        return False


# ============================================================================
# HELPER: Generate Notification Batching Key
# ============================================================================

def get_notification_batching_key(conversation_id: str, recipient_id: str) -> str:
    """
    Generate key for Redis batching logic.
    
    Used to group multiple messages from same conversation into single
    batched notification to prevent spam.
    
    Args:
        conversation_id: ID of conversation
        recipient_id: ID of recipient
    
    Returns:
        str: Batching key in format "msg_batch_{conversation_id}_{recipient_id}"
    """
    return f"msg_batch_{conversation_id}_{recipient_id}"


# ============================================================================
# MAIN: Create New Message Notification
# ============================================================================

def create_message_notification(message: Message, recipient_id: str, db: Session) -> bool:
    """
    Create notification for new message.
    
    Called from POST /messages endpoint after message is sent.
    
    Checks:
    - User's notification preferences enabled
    - User not actively viewing the conversation
    - Message not from user themselves (handled by caller)
    
    Args:
        message: Message object (from database)
        recipient_id: ID of notification recipient
        db: Database session
    
    Returns:
        bool: True if notification created, False if skipped
    
    Requirements:
    - 10.1: New message notification triggered
    - 10.2: Message preview in notification (first 50 chars)
    - 10.3: Notification includes sender info
    - 10.4: Notification preferences respected
    - 10.5: Skip if user viewing conversation
    """
    
    # Requirement 10.4: Check notification preferences
    if not should_create_notification(recipient_id, db):
        print(f"ℹ️ Notifications disabled for user {recipient_id}")
        return False
    
    # Requirement 10.5: Skip if user actively viewing conversation
    if is_user_active_in_conversation(message.conversation_id, recipient_id, db):
        print(f"ℹ️ User {recipient_id} actively viewing conversation {message.conversation_id}")
        return False
    
    try:
        # Get sender information
        sender = db.query(User).filter(User.id == message.sender_id).first()
        if not sender:
            print(f"⚠️ Sender {message.sender_id} not found")
            return False
        
        # Requirement 10.2: Create message preview (first 50 chars)
        preview = message.content[:50]
        if len(message.content) > 50:
            preview += "..."
        
        # Requirement 10.3: Include sender info
        notification_service = NotificationService(db)
        notification = notification_service.create_notification(
            user_id=recipient_id,
            notification_type="new_message",
            title=f"{sender.username} sent you a message",
            message=preview,
            data={
                "sender_id": message.sender_id,
                "sender_username": sender.username,
                "conversation_id": message.conversation_id,
                "message_id": message.id,
                "message_preview": preview
            }
        )
        
        if notification:
            print(f"✓ Message notification created for user {recipient_id}")
            return True
        else:
            print(f"ℹ️ Notification creation returned None (preferences disabled?)")
            return False
            
    except Exception as e:
        print(f"⚠️ Error creating message notification: {e}")
        return False


# ============================================================================
# MAIN: Create Message Request Notification
# ============================================================================

def create_message_request_notification(
    conversation: Conversation,
    recipient_id: str,
    db: Session
) -> bool:
    """
    Create notification for new message request.
    
    Called when new message request is created (non-follower sending first message).
    
    Checks:
    - User's notification preferences enabled
    - User not actively viewing the conversation
    
    Args:
        conversation: Conversation object (message request)
        recipient_id: ID of notification recipient (receiver of request)
        db: Database session
    
    Returns:
        bool: True if notification created, False if skipped
    
    Requirements:
    - 10.6: Message request notifications
    - 10.3: Notification includes sender info
    - 10.4: Notification preferences respected
    """
    
    # Check notification preferences
    if not should_create_notification(recipient_id, db):
        print(f"ℹ️ Notifications disabled for user {recipient_id}")
        return False
    
    # Skip if user actively viewing conversation
    if is_user_active_in_conversation(conversation.id, recipient_id, db):
        print(f"ℹ️ User {recipient_id} actively viewing conversation {conversation.id}")
        return False
    
    try:
        # Get the sender (other participant in the message request)
        from app.models.messaging import ConversationParticipant
        
        participants = (
            db.query(ConversationParticipant)
            .filter(ConversationParticipant.conversation_id == conversation.id)
            .all()
        )
        
        sender_id = None
        for participant in participants:
            if participant.user_id != recipient_id:
                sender_id = participant.user_id
                break
        
        if not sender_id:
            print(f"⚠️ Could not find sender for message request {conversation.id}")
            return False
        
        # Get sender information
        sender = db.query(User).filter(User.id == sender_id).first()
        if not sender:
            print(f"⚠️ Sender {sender_id} not found")
            return False
        
        # Get first message preview from conversation
        preview = ""
        if conversation.last_message_preview:
            preview = conversation.last_message_preview[:50]
            if len(conversation.last_message_preview) > 50:
                preview += "..."
        
        # Create notification
        notification_service = NotificationService(db)
        notification = notification_service.create_notification(
            user_id=recipient_id,
            notification_type="message_request",
            title=f"{sender.username} sent you a message request",
            message=preview,
            data={
                "sender_id": sender_id,
                "sender_username": sender.username,
                "conversation_id": conversation.id,
                "message_preview": preview
            }
        )
        
        if notification:
            print(f"✓ Message request notification created for user {recipient_id}")
            return True
        else:
            print(f"ℹ️ Notification creation returned None (preferences disabled?)")
            return False
            
    except Exception as e:
        print(f"⚠️ Error creating message request notification: {e}")
        return False


# ============================================================================
# HELPER: Batch Notifications (Future Implementation)
# ============================================================================

def should_batch_notification(
    recipient_id: str,
    conversation_id: str,
    db: Session,
    batch_window_minutes: int = 5
) -> bool:
    """
    Check if notification should be batched.
    
    Used for future implementation of notification batching:
    if multiple unread messages in same conversation within batch_window,
    send single batched notification instead of multiple.
    
    Currently a placeholder - actual batching logic requires Redis.
    
    Args:
        recipient_id: ID of recipient
        conversation_id: ID of conversation
        db: Database session
        batch_window_minutes: Time window for batching (default 5 minutes)
    
    Returns:
        bool: True if should batch, False if should send now
    
    Requirement:
    - 10.7: Notification batching logic (structure for it)
    """
    # TODO: Implement Redis-based batching logic
    # For now, always send immediately (no batching)
    return False
