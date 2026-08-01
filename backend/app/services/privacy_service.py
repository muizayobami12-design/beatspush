"""
Privacy Service - Business logic for messaging privacy and blocking
Tasks 5.1-5.4: Privacy settings, message requests, blocking, reporting
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import Optional, Dict, Tuple
from datetime import datetime
import uuid

from app.models.messaging import (
    BlockedUser, UserMessageSettings, MessageReport,
    Conversation, ConversationParticipant
)
from app.models.user import User
from app.models.social import Follow
from app.schemas.messaging import (
    SettingsResponse, BlockedUserResponse, BlockedUsersListResponse,
    ReportMessageResponse, UserBasicInfo
)


class PrivacyService:
    """Privacy and blocking service for messaging system"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # PRIVACY SETTINGS (Task 5.1)
    # ========================================================================
    
    def get_user_settings(self, user_id: str) -> UserMessageSettings:
        """
        Get user's message privacy settings (create default if not exists)
        
        Args:
            user_id: User ID
            
        Returns:
            UserMessageSettings object
        """
        settings = (
            self.db.query(UserMessageSettings)
            .filter(UserMessageSettings.user_id == user_id)
            .first()
        )
        
        if not settings:
            # Create default settings
            settings = UserMessageSettings(
                id=str(uuid.uuid4()),
                user_id=user_id,
                message_filter="everyone",
                read_receipts_enabled=True,
                typing_indicators_enabled=True
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        return settings
    
    def update_user_settings(
        self,
        user_id: str,
        settings_dict: Dict
    ) -> UserMessageSettings:
        """
        Update user's message privacy settings
        
        Args:
            user_id: User ID
            settings_dict: Dict with settings to update
            
        Returns:
            Updated UserMessageSettings object
        """
        settings = self.get_user_settings(user_id)
        
        # Update fields
        for field, value in settings_dict.items():
            if hasattr(settings, field) and value is not None:
                setattr(settings, field, value)
        
        settings.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(settings)
        
        return settings
    
    # ========================================================================
    # MESSAGE REQUESTS (Task 5.2)
    # ========================================================================
    
    def should_create_message_request(
        self,
        sender_id: str,
        recipient_id: str
    ) -> bool:
        """
        Determine if a message should create a message request
        
        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            
        Returns:
            True if message request needed, False otherwise
        """
        # Check if conversation already exists
        existing = self._find_conversation(sender_id, recipient_id)
        if existing:
            # If conversation exists and is accepted, no request needed
            if existing.request_status == "accepted":
                return False
            # If it's a pending/declined request, keep it as request
            return True
        
        # Check if users are blocking each other
        if self.is_blocked(sender_id, recipient_id) or self.is_blocked(recipient_id, sender_id):
            return False  # Will be rejected anyway
        
        # Get recipient's settings
        settings = self.get_user_settings(recipient_id)
        
        if settings.message_filter == "none":
            return True  # No one can message directly
        
        if settings.message_filter == "followers":
            # Check if sender follows recipient
            follows = (
                self.db.query(Follow)
                .filter(
                    Follow.follower_id == sender_id,
                    Follow.following_id == recipient_id
                )
                .first()
            )
            return follows is None  # Request needed if not following
        
        if settings.message_filter == "verified":
            # Check if sender is verified
            sender = self.db.query(User).filter(User.id == sender_id).first()
            return not (sender and sender.is_verified)
        
        # "everyone" filter - no request needed
        return False
    
    def accept_message_request(
        self,
        conversation_id: str,
        user_id: str
    ) -> Conversation:
        """
        Accept a message request
        
        Args:
            conversation_id: Conversation ID
            user_id: User accepting (must be recipient)
            
        Returns:
            Updated Conversation object
        """
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verify user is a participant
        participant = (
            self.db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id
            )
            .first()
        )
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a participant in this conversation"
            )
        
        # Verify it's actually a message request
        if not conversation.is_message_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This is not a message request"
            )
        
        if conversation.request_status == "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message request already accepted"
            )
        
        # Accept the request
        conversation.request_status = "accepted"
        conversation.is_message_request = False
        
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def decline_message_request(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """
        Decline a message request
        
        Args:
            conversation_id: Conversation ID
            user_id: User declining (must be recipient)
            
        Returns:
            True if declined successfully
        """
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verify user is a participant
        participant = (
            self.db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id
            )
            .first()
        )
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a participant in this conversation"
            )
        
        # Verify it's a message request
        if not conversation.is_message_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This is not a message request"
            )
        
        # Decline the request
        conversation.request_status = "declined"
        
        # Mark both participants as left
        participants = (
            self.db.query(ConversationParticipant)
            .filter(ConversationParticipant.conversation_id == conversation_id)
            .all()
        )
        
        for p in participants:
            p.left_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    # ========================================================================
    # BLOCKING (Task 5.3)
    # ========================================================================
    
    def block_user(
        self,
        blocker_id: str,
        blocked_id: str,
        reason: Optional[str] = None
    ) -> BlockedUser:
        """
        Block a user
        
        Args:
            blocker_id: User doing the blocking
            blocked_id: User being blocked
            reason: Optional reason for blocking
            
        Returns:
            BlockedUser object
        """
        if blocker_id == blocked_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot block yourself"
            )
        
        # Check if already blocked
        existing = (
            self.db.query(BlockedUser)
            .filter(
                BlockedUser.blocker_id == blocker_id,
                BlockedUser.blocked_id == blocked_id
            )
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already blocked"
            )
        
        # Create block record
        block = BlockedUser(
            id=str(uuid.uuid4()),
            blocker_id=blocker_id,
            blocked_id=blocked_id,
            reason=reason
        )
        self.db.add(block)
        
        # Hide all conversations between these users
        conversations = self._find_all_conversations(blocker_id, blocked_id)
        for conversation in conversations:
            participants = (
                self.db.query(ConversationParticipant)
                .filter(
                    ConversationParticipant.conversation_id == conversation.id,
                    ConversationParticipant.user_id.in_([blocker_id, blocked_id])
                )
                .all()
            )
            
            for participant in participants:
                participant.left_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(block)
        
        return block
    
    def unblock_user(
        self,
        blocker_id: str,
        blocked_id: str
    ) -> bool:
        """
        Unblock a user
        
        Args:
            blocker_id: User who blocked
            blocked_id: User who was blocked
            
        Returns:
            True if unblocked successfully
        """
        block = (
            self.db.query(BlockedUser)
            .filter(
                BlockedUser.blocker_id == blocker_id,
                BlockedUser.blocked_id == blocked_id
            )
            .first()
        )
        
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block record not found"
            )
        
        # Delete block record
        self.db.delete(block)
        
        # Restore conversations (clear left_at timestamps)
        conversations = self._find_all_conversations(blocker_id, blocked_id)
        for conversation in conversations:
            participants = (
                self.db.query(ConversationParticipant)
                .filter(
                    ConversationParticipant.conversation_id == conversation.id,
                    ConversationParticipant.user_id.in_([blocker_id, blocked_id])
                )
                .all()
            )
            
            for participant in participants:
                if participant.left_at:
                    participant.left_at = None
        
        self.db.commit()
        
        return True
    
    def is_blocked(
        self,
        user_id: str,
        target_id: str
    ) -> bool:
        """
        Check if user has blocked target
        
        Args:
            user_id: User ID
            target_id: Target user ID
            
        Returns:
            True if blocked, False otherwise
        """
        block = (
            self.db.query(BlockedUser)
            .filter(
                BlockedUser.blocker_id == user_id,
                BlockedUser.blocked_id == target_id
            )
            .first()
        )
        
        return block is not None
    
    def get_blocked_users(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Get list of blocked users with pagination
        
        Args:
            user_id: User ID
            page: Page number
            page_size: Items per page
            
        Returns:
            Dict with blocked users list and pagination info
        """
        # Query blocked users
        query = (
            self.db.query(BlockedUser)
            .filter(BlockedUser.blocker_id == user_id)
            .options(joinedload(BlockedUser.blocked))
            .order_by(BlockedUser.blocked_at.desc())
        )
        
        # Get total count
        total = query.count()
        
        # Paginate
        offset = (page - 1) * page_size
        blocks = query.offset(offset).limit(page_size).all()
        
        # Build response
        blocked_users = []
        for block in blocks:
            user_info = UserBasicInfo(
                user_id=block.blocked.id,
                username=block.blocked.username,
                full_name=block.blocked.full_name,
                is_verified=block.blocked.is_verified
            )
            
            blocked_user = BlockedUserResponse(
                id=block.id,
                blocker_id=block.blocker_id,
                blocked_id=block.blocked_id,
                blocked_user=user_info,
                blocked_at=block.blocked_at,
                reason=block.reason
            )
            blocked_users.append(blocked_user)
        
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "blocked_users": blocked_users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def can_send_message(
        self,
        sender_id: str,
        recipient_id: str
    ) -> Tuple[bool, str]:
        """
        Check if sender can send message to recipient
        
        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            
        Returns:
            Tuple of (can_send: bool, reason: str)
        """
        # Check if sender blocked recipient
        if self.is_blocked(sender_id, recipient_id):
            return False, "You have blocked this user"
        
        # Check if recipient blocked sender
        if self.is_blocked(recipient_id, sender_id):
            return False, "This user has blocked you"
        
        # Check recipient's privacy settings
        settings = self.get_user_settings(recipient_id)
        
        if settings.message_filter == "none":
            return False, "This user is not accepting messages"
        
        if settings.message_filter == "followers":
            # Check if sender follows recipient
            follows = (
                self.db.query(Follow)
                .filter(
                    Follow.follower_id == sender_id,
                    Follow.following_id == recipient_id
                )
                .first()
            )
            if not follows:
                return True, "Message request will be created"  # Can still send as request
        
        if settings.message_filter == "verified":
            sender = self.db.query(User).filter(User.id == sender_id).first()
            if not (sender and sender.is_verified):
                return True, "Message request will be created"  # Can still send as request
        
        return True, ""
    
    # ========================================================================
    # REPORTING (Task 5.4)
    # ========================================================================
    
    def report_message(
        self,
        reporter_id: str,
        message_id: str,
        reason: str,
        details: Optional[str] = None
    ) -> MessageReport:
        """
        Report a message for review
        
        Args:
            reporter_id: User reporting the message
            message_id: Message being reported
            reason: Report reason (spam, harassment, inappropriate, other)
            details: Optional additional details
            
        Returns:
            MessageReport object
        """
        # Verify message exists
        from app.models.messaging import Message
        message = self.db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Create report
        report = MessageReport(
            id=str(uuid.uuid4()),
            message_id=message_id,
            reporter_id=reporter_id,
            reason=reason,
            details=details,
            reviewed=False
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _find_conversation(
        self,
        user1_id: str,
        user2_id: str
    ) -> Optional[Conversation]:
        """Find conversation between two users"""
        conversation = (
            self.db.query(Conversation)
            .join(
                ConversationParticipant,
                ConversationParticipant.conversation_id == Conversation.id
            )
            .filter(ConversationParticipant.user_id.in_([user1_id, user2_id]))
            .group_by(Conversation.id)
            .having(func.count(ConversationParticipant.id) == 2)
            .first()
        )
        
        return conversation
    
    def _find_all_conversations(
        self,
        user1_id: str,
        user2_id: str
    ) -> list:
        """Find all conversations between two users"""
        conversations = (
            self.db.query(Conversation)
            .join(
                ConversationParticipant,
                ConversationParticipant.conversation_id == Conversation.id
            )
            .filter(ConversationParticipant.user_id.in_([user1_id, user2_id]))
            .group_by(Conversation.id)
            .having(func.count(ConversationParticipant.id) == 2)
            .all()
        )
        
        return conversations
