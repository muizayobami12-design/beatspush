"""
Messaging Service - Business logic for messaging system
Tasks 4.1-4.6: Core messaging operations
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import uuid

from app.models.messaging import (
    Conversation, ConversationParticipant, Message, MessageReadReceipt,
    MessageAttachment, BlockedUser, MessageReport, UserMessageSettings
)
from app.models.user import User
from app.models.social import Follow
from app.schemas.messaging import (
    MessageResponse, MessageListResponse, ConversationResponse,
    ConversationListResponse, UserBasicInfo, LastMessagePreview,
    AttachmentResponse, UnreadCountResponse
)


class MessagingService:
    """Core messaging service for conversations and messages"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # CONVERSATION MANAGEMENT (Task 4.1)
    # ========================================================================
    
    def get_or_create_conversation(
        self,
        user_id: str,
        recipient_id: str
    ) -> Conversation:
        """
        Get existing conversation or create new one between two users
        
        Args:
            user_id: Current user ID
            recipient_id: Other user ID
            
        Returns:
            Conversation object
        """
        if user_id == recipient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create conversation with yourself"
            )
        
        # Check if recipient exists
        recipient = self.db.query(User).filter(User.id == recipient_id).first()
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )
        
        # Check if either user has blocked the other
        if self._is_blocked(user_id, recipient_id) or self._is_blocked(recipient_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create conversation with blocked user"
            )
        
        # Find existing conversation between these users
        existing = (
            self.db.query(Conversation)
            .join(ConversationParticipant, ConversationParticipant.conversation_id == Conversation.id)
            .filter(ConversationParticipant.user_id.in_([user_id, recipient_id]))
            .group_by(Conversation.id)
            .having(func.count(ConversationParticipant.id) == 2)
            .first()
        )
        
        if existing:
            # Check if both users are still participants (not left)
            participants = (
                self.db.query(ConversationParticipant)
                .filter(
                    ConversationParticipant.conversation_id == existing.id,
                    ConversationParticipant.user_id.in_([user_id, recipient_id])
                )
                .all()
            )
            
            # Rejoin if user had left
            for participant in participants:
                if participant.left_at is not None:
                    participant.left_at = None
                    self.db.commit()
            
            return existing
        
        # Check if message request is needed
        is_request = self._should_create_message_request(user_id, recipient_id)
        
        # Create new conversation
        conversation = Conversation(
            id=str(uuid.uuid4()),
            is_message_request=is_request,
            request_status="pending" if is_request else "accepted"
        )
        self.db.add(conversation)
        self.db.flush()
        
        # Add participants
        for uid in [user_id, recipient_id]:
            participant = ConversationParticipant(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                user_id=uid
            )
            self.db.add(participant)
        
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def list_conversations(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
        search: Optional[str] = None
    ) -> Dict:
        """
        List user's conversations with pagination and filtering
        
        Args:
            user_id: Current user ID
            page: Page number (1-indexed)
            page_size: Items per page
            unread_only: Filter to only unread conversations
            search: Search query for participant names
            
        Returns:
            Dict with conversations list and pagination info
        """
        # Base query: get user's conversation participants
        query = (
            self.db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.left_at.is_(None)
            )
            .join(Conversation)
            .options(joinedload(ConversationParticipant.conversation))
        )
        
        # Filter by unread
        if unread_only:
            query = query.filter(ConversationParticipant.unread_count > 0)
        
        # Search by participant names
        if search:
            # Join to get other participants' user info
            query = query.join(
                ConversationParticipant,
                and_(
                    ConversationParticipant.conversation_id == Conversation.id,
                    ConversationParticipant.user_id != user_id
                )
            ).join(User, User.id == ConversationParticipant.user_id)
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )
        
        # Order by last activity
        query = query.order_by(desc(Conversation.last_activity_at))
        
        # Get total count
        total = query.count()
        
        # Paginate
        offset = (page - 1) * page_size
        participants = query.offset(offset).limit(page_size).all()
        
        # Build conversation responses
        conversations = []
        for participant in participants:
            conv_response = self._build_conversation_response(
                participant.conversation,
                user_id
            )
            conversations.append(conv_response)
        
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "conversations": conversations,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def get_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> Conversation:
        """
        Get conversation by ID with access control
        
        Args:
            conversation_id: Conversation ID
            user_id: Current user ID
            
        Returns:
            Conversation object
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
        
        # Check if user is a participant
        participant = (
            self.db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.left_at.is_(None)
            )
            .first()
        )
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )
        
        return conversation
    
    def search_conversations(
        self,
        user_id: str,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Search conversations by participant names
        
        Args:
            user_id: Current user ID
            query: Search query
            page: Page number
            page_size: Items per page
            
        Returns:
            Dict with search results and pagination
        """
        return self.list_conversations(
            user_id=user_id,
            page=page,
            page_size=page_size,
            search=query
        )
    
    # ========================================================================
    # MESSAGE OPERATIONS (Task 4.2)
    # ========================================================================
    
    def send_message(
        self,
        sender_id: str,
        content: str,
        recipient_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Message:
        """
        Send a new message
        
        Args:
            sender_id: Sender user ID
            content: Message content
            recipient_id: Recipient ID (for new conversations)
            conversation_id: Existing conversation ID
            
        Returns:
            Message object
        """
        # Sanitize message content (Task 15.1)
        from app.utils.sanitization import sanitize_message_content
        try:
            content = sanitize_message_content(content)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Get or create conversation
        if conversation_id:
            conversation = self.get_conversation(conversation_id, sender_id)
        elif recipient_id:
            # Check privacy settings first
            can_send, reason = self._can_send_message(sender_id, recipient_id)
            if not can_send:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=reason
                )
            conversation = self.get_or_create_conversation(sender_id, recipient_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either recipient_id or conversation_id must be provided"
            )
        
        # Create message
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            sender_id=sender_id,
            content=content.strip()
        )
        self.db.add(message)
        
        # Update conversation metadata
        conversation.last_activity_at = datetime.utcnow()
        conversation.last_message_preview = content[:100] + ("..." if len(content) > 100 else "")
        
        # Increment unread count for other participants
        participants = (
            self.db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == conversation.id,
                ConversationParticipant.user_id != sender_id
            )
            .all()
        )
        
        for participant in participants:
            participant.unread_count += 1
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_messages(
        self,
        conversation_id: str,
        user_id: str,
        page: int = 1,
        page_size: int = 50,
        cursor: Optional[str] = None
    ) -> Dict:
        """
        Get messages in a conversation with pagination
        
        Args:
            conversation_id: Conversation ID
            user_id: Current user ID
            page: Page number
            page_size: Items per page
            cursor: Cursor for cursor-based pagination (message ID)
            
        Returns:
            Dict with messages and pagination info
        """
        # Verify access
        self.get_conversation(conversation_id, user_id)
        
        # Base query
        query = (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.deleted_at.is_(None)
            )
            .options(
                joinedload(Message.sender),
                joinedload(Message.attachments),
                joinedload(Message.read_receipts)
            )
        )
        
        # Cursor-based pagination
        if cursor:
            cursor_message = self.db.query(Message).filter(Message.id == cursor).first()
            if cursor_message:
                query = query.filter(Message.created_at < cursor_message.created_at)
        
        # Order by created_at DESC for recent-first
        query = query.order_by(desc(Message.created_at))
        
        # Fetch messages
        messages = query.limit(page_size + 1).all()
        
        # Check if there are more messages
        has_more = len(messages) > page_size
        if has_more:
            messages = messages[:page_size]
        
        # Get next cursor
        next_cursor = messages[-1].id if has_more and messages else None
        
        # Build response
        message_responses = []
        for msg in reversed(messages):  # Reverse to show oldest first
            msg_response = self._build_message_response(msg)
            message_responses.append(msg_response)
        
        return {
            "messages": message_responses,
            "has_more": has_more,
            "next_cursor": next_cursor
        }
    
    def get_messages_since(
        self,
        conversation_id: str,
        user_id: str,
        since_timestamp: str,
        page_size: int = 50
    ) -> Dict:
        """
        Get messages since a given ISO timestamp (polling fallback)
        
        Args:
            conversation_id: Conversation ID
            user_id: Current user ID
            since_timestamp: ISO 8601 timestamp string
            page_size: Max messages to return
            
        Returns:
            Dict with messages and pagination info
        """
        from datetime import datetime
        
        # Verify access
        self.get_conversation(conversation_id, user_id)
        
        # Parse timestamp
        try:
            since_dt = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            since_dt = datetime.utcnow()
        
        # Query messages since timestamp
        messages = (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.deleted_at.is_(None),
                Message.created_at > since_dt
            )
            .options(
                joinedload(Message.sender),
                joinedload(Message.attachments),
                joinedload(Message.read_receipts)
            )
            .order_by(Message.created_at.asc())
            .limit(page_size + 1)
            .all()
        )
        
        has_more = len(messages) > page_size
        if has_more:
            messages = messages[:page_size]
        
        next_cursor = messages[-1].id if has_more and messages else None
        
        message_responses = [self._build_message_response(msg) for msg in messages]
        
        return {
            "messages": message_responses,
            "has_more": has_more,
            "next_cursor": next_cursor
        }

    def search_messages(
        self,
        user_id: str,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Search messages by content
        
        Args:
            user_id: Current user ID
            query: Search query
            page: Page number
            page_size: Items per page
            
        Returns:
            Dict with search results
        """
        # Get user's conversation IDs
        conversation_ids = (
            self.db.query(ConversationParticipant.conversation_id)
            .filter(
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.left_at.is_(None)
            )
            .all()
        )
        conversation_ids = [cid[0] for cid in conversation_ids]
        
        # Search messages
        messages_query = (
            self.db.query(Message)
            .filter(
                Message.conversation_id.in_(conversation_ids),
                Message.content.ilike(f"%{query}%"),
                Message.deleted_at.is_(None)
            )
            .options(
                joinedload(Message.sender),
                joinedload(Message.attachments)
            )
            .order_by(desc(Message.created_at))
        )
        
        # Get total
        total = messages_query.count()
        
        # Paginate
        offset = (page - 1) * page_size
        messages = messages_query.offset(offset).limit(page_size).all()
        
        # Build responses
        message_responses = [
            self._build_message_response(msg) for msg in messages
        ]
        
        return {
            "messages": message_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": total > (page * page_size)
        }
    
    # ========================================================================
    # READ RECEIPTS (Task 4.3)
    # ========================================================================
    
    def mark_message_read(
        self,
        message_id: str,
        user_id: str
    ) -> bool:
        """
        Mark a single message as read
        
        Args:
            message_id: Message ID
            user_id: User ID
            
        Returns:
            True if marked successfully
        """
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Verify user is participant
        self.get_conversation(message.conversation_id, user_id)
        
        # Check if already read
        existing = (
            self.db.query(MessageReadReceipt)
            .filter(
                MessageReadReceipt.message_id == message_id,
                MessageReadReceipt.user_id == user_id
            )
            .first()
        )
        
        if not existing:
            receipt = MessageReadReceipt(
                id=str(uuid.uuid4()),
                message_id=message_id,
                user_id=user_id
            )
            self.db.add(receipt)
            self.db.commit()
        
        return True
    
    def mark_conversation_read(
        self,
        conversation_id: str,
        user_id: str
    ) -> int:
        """
        Mark all messages in conversation as read
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            
        Returns:
            Number of messages marked as read
        """
        # Verify access
        self.get_conversation(conversation_id, user_id)
        
        # Get all unread messages in conversation
        unread_messages = (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.sender_id != user_id,  # Don't mark own messages
                Message.deleted_at.is_(None)
            )
            .outerjoin(
                MessageReadReceipt,
                and_(
                    MessageReadReceipt.message_id == Message.id,
                    MessageReadReceipt.user_id == user_id
                )
            )
            .filter(MessageReadReceipt.id.is_(None))  # No receipt exists
            .all()
        )
        
        # Create read receipts
        count = 0
        for message in unread_messages:
            receipt = MessageReadReceipt(
                id=str(uuid.uuid4()),
                message_id=message.id,
                user_id=user_id
            )
            self.db.add(receipt)
            count += 1
        
        # Update participant unread count
        participant = (
            self.db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id
            )
            .first()
        )
        
        if participant:
            participant.unread_count = 0
            participant.last_read_at = datetime.utcnow()
        
        self.db.commit()
        
        return count
    
    def get_unread_count(
        self,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> UnreadCountResponse:
        """
        Get unread message count
        
        Args:
            user_id: User ID
            conversation_id: Optional conversation ID (for specific conversation)
            
        Returns:
            UnreadCountResponse with counts
        """
        if conversation_id:
            participant = (
                self.db.query(ConversationParticipant)
                .filter(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == user_id
                )
                .first()
            )
            
            if not participant:
                return UnreadCountResponse(
                    conversation_id=conversation_id,
                    unread_count=0
                )
            
            return UnreadCountResponse(
                conversation_id=conversation_id,
                unread_count=participant.unread_count or 0
            )
        else:
            # Get total unread across all conversations
            total = (
                self.db.query(func.sum(ConversationParticipant.unread_count))
                .filter(
                    ConversationParticipant.user_id == user_id,
                    ConversationParticipant.left_at.is_(None)
                )
                .scalar()
            ) or 0
            
            return UnreadCountResponse(
                unread_count=0,
                total_unread=total
            )
    
    # ========================================================================
    # MESSAGE EDITING AND DELETION (Task 4.4)
    # ========================================================================
    
    def edit_message(
        self,
        message_id: str,
        user_id: str,
        new_content: str
    ) -> Message:
        """
        Edit a message (within 15 minute window)
        
        Args:
            message_id: Message ID
            user_id: User ID (must be sender)
            new_content: New message content
            
        Returns:
            Updated Message object
        """
        message = self.db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Check if user is the sender
        if message.sender_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the sender can edit messages"
            )
        
        # Check if message is already deleted
        if message.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit deleted message"
            )
        
        # Check 15-minute time window
        time_since_creation = datetime.utcnow() - message.created_at
        if time_since_creation > timedelta(minutes=15):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Messages can only be edited within 15 minutes of creation"
            )
        
        # Update message
        message.content = new_content.strip()
        message.is_edited = True
        message.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def delete_message(
        self,
        message_id: str,
        user_id: str
    ) -> bool:
        """
        Soft delete a message
        
        Args:
            message_id: Message ID
            user_id: User ID (must be sender)
            
        Returns:
            True if deleted successfully
        """
        message = self.db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Check if user is the sender
        if message.sender_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the sender can delete messages"
            )
        
        # Check if already deleted
        if message.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message is already deleted"
            )
        
        # Soft delete
        message.deleted_at = datetime.utcnow()
        message.content = "[Message deleted]"
        
        self.db.commit()
        
        return True
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _is_blocked(self, user_id: str, target_id: str) -> bool:
        """Check if user has blocked target"""
        block = (
            self.db.query(BlockedUser)
            .filter(
                BlockedUser.blocker_id == user_id,
                BlockedUser.blocked_id == target_id
            )
            .first()
        )
        return block is not None
    
    def _should_create_message_request(
        self,
        sender_id: str,
        recipient_id: str
    ) -> bool:
        """Determine if message should be a request"""
        # Get recipient's privacy settings
        settings = (
            self.db.query(UserMessageSettings)
            .filter(UserMessageSettings.user_id == recipient_id)
            .first()
        )
        
        if not settings:
            # Default: everyone can message
            return False
        
        if settings.message_filter == "none":
            return True  # Message request required
        
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
            return follows is None
        
        if settings.message_filter == "verified":
            # Check if sender is verified
            sender = self.db.query(User).filter(User.id == sender_id).first()
            return not (sender and sender.is_verified)
        
        return False  # "everyone" - no request needed
    
    def _can_send_message(
        self,
        sender_id: str,
        recipient_id: str
    ) -> Tuple[bool, str]:
        """Check if sender can message recipient"""
        # Check blocking
        if self._is_blocked(sender_id, recipient_id):
            return False, "You have blocked this user"
        
        if self._is_blocked(recipient_id, sender_id):
            return False, "This user has blocked you"
        
        return True, ""
    
    def _build_conversation_response(
        self,
        conversation: Conversation,
        user_id: str
    ) -> ConversationResponse:
        """Build conversation response with participant info"""
        # Get all participants except current user
        participants = (
            self.db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == conversation.id,
                ConversationParticipant.left_at.is_(None)
            )
            .options(joinedload(ConversationParticipant.user))
            .all()
        )
        
        # Get current user's participant record
        current_participant = next(
            (p for p in participants if p.user_id == user_id),
            None
        )
        
        # Build participant info list
        participant_infos = []
        for p in participants:
            if p.user_id != user_id:
                user_info = UserBasicInfo(
                    user_id=p.user.id,
                    username=p.user.username,
                    full_name=p.user.full_name,
                    is_verified=p.user.is_verified
                )
                participant_infos.append(user_info)
        
        # Get last message
        last_msg = None
        if conversation.last_message_preview:
            last_message_obj = (
                self.db.query(Message)
                .filter(
                    Message.conversation_id == conversation.id,
                    Message.deleted_at.is_(None)
                )
                .order_by(desc(Message.created_at))
                .first()
            )
            
            if last_message_obj:
                has_attachment = len(last_message_obj.attachments) > 0
                last_msg = LastMessagePreview(
                    id=last_message_obj.id,
                    content=last_message_obj.content,
                    sender_id=last_message_obj.sender_id,
                    created_at=last_message_obj.created_at,
                    has_attachment=has_attachment
                )
        
        return ConversationResponse(
            id=conversation.id,
            participants=participant_infos,
            last_message=last_msg,
            unread_count=current_participant.unread_count if current_participant else 0,
            is_message_request=conversation.is_message_request,
            request_status=conversation.request_status,
            last_activity_at=conversation.last_activity_at,
            is_archived=current_participant.is_archived if current_participant else False,
            is_muted=current_participant.is_muted if current_participant else False,
            created_at=conversation.created_at
        )
    
    def _build_message_response(self, message: Message) -> MessageResponse:
        """Build message response with all related data"""
        # Get sender info
        sender = message.sender
        sender_info = UserBasicInfo(
            user_id=sender.id,
            username=sender.username,
            full_name=sender.full_name,
            is_verified=sender.is_verified
        )
        
        # Get read_by list
        read_by = [receipt.user_id for receipt in message.read_receipts]
        
        # Get attachments
        attachments = [
            AttachmentResponse(
                id=att.id,
                file_type=att.file_type,
                original_filename=att.original_filename,
                storage_url=att.storage_url,
                file_size=att.file_size,
                mime_type=att.mime_type,
                duration=att.duration,
                width=att.width,
                height=att.height,
                thumbnail_url=att.thumbnail_url,
                created_at=att.created_at
            )
            for att in message.attachments
        ]
        
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            sender=sender_info,
            content=message.content,
            created_at=message.created_at,
            updated_at=message.updated_at,
            is_edited=message.is_edited,
            read_by=read_by,
            attachments=attachments
        )
