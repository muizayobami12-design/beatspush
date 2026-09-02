"""
Access control and authorization utilities for messaging system
Task 15.2: Implement access control and authorization
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional


def verify_conversation_access(
    conversation_id: str,
    user_id: str,
    db: Session
) -> None:
    """
    Verify that a user has access to a conversation.
    Raises 403 if user is not a participant.
    
    Args:
        conversation_id: Conversation UUID
        user_id: User UUID to check
        db: Database session
        
    Raises:
        HTTPException 404: If conversation not found
        HTTPException 403: If user is not a participant
    """
    from app.models.messaging import Conversation, ConversationParticipant
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    participant = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id,
        ConversationParticipant.user_id == user_id,
        ConversationParticipant.left_at.is_(None)
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this conversation"
        )


def verify_message_sender(
    message_id: str,
    user_id: str,
    db: Session
):
    """
    Verify that a user is the sender of a message.
    Raises 403 if user is not the sender.
    
    Args:
        message_id: Message UUID
        user_id: User UUID to check
        db: Database session
        
    Returns:
        Message object if authorized
        
    Raises:
        HTTPException 404: If message not found
        HTTPException 403: If user is not the sender
    """
    from app.models.messaging import Message
    
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if message.sender_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own messages"
        )
    
    return message


def check_block_status(
    user_id: str,
    target_id: str,
    db: Session
) -> bool:
    """
    Check if either user has blocked the other.
    
    Args:
        user_id: First user UUID
        target_id: Second user UUID
        db: Database session
        
    Returns:
        True if a block exists in either direction
    """
    from app.models.messaging import BlockedUser
    
    block = db.query(BlockedUser).filter(
        ((BlockedUser.blocker_id == user_id) & (BlockedUser.blocked_id == target_id)) |
        ((BlockedUser.blocker_id == target_id) & (BlockedUser.blocked_id == user_id))
    ).first()
    
    return block is not None


def verify_not_blocked(
    user_id: str,
    target_id: str,
    db: Session
) -> None:
    """
    Verify that neither user has blocked the other.
    Raises 403 if a block exists.
    
    Args:
        user_id: First user UUID
        target_id: Second user UUID
        db: Database session
        
    Raises:
        HTTPException 403: If block exists
    """
    if check_block_status(user_id, target_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot send messages to this user"
        )


def verify_not_self(user_id: str, target_id: str, action: str = "perform this action on yourself") -> None:
    """
    Verify that user is not targeting themselves.
    
    Args:
        user_id: Current user UUID
        target_id: Target user UUID
        action: Description of the action for error message
        
    Raises:
        HTTPException 400: If user is targeting themselves
    """
    if user_id == target_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You cannot {action}"
        )
