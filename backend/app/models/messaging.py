"""
Messaging System Models
Task 1.1: Create Alembic migration for messaging tables

Models for conversations, messages, attachments, blocks, reports, and privacy settings.
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, ForeignKey, 
    DateTime, BigInteger, Numeric, CheckConstraint, Index,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
import enum
from app.db.database import Base


class MessageFilter(str, enum.Enum):
    """Message filter types for privacy settings"""
    EVERYONE = "everyone"
    FOLLOWERS = "followers"
    VERIFIED = "verified"
    NONE = "none"


class RequestStatus(str, enum.Enum):
    """Message request status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class ReportReason(str, enum.Enum):
    """Message report reasons"""
    SPAM = "spam"
    HARASSMENT = "harassment"
    INAPPROPRIATE = "inappropriate"
    OTHER = "other"


class Conversation(Base):
    """Conversation model"""
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
    
    __table_args__ = (
        Index('idx_conversations_last_activity', 'last_activity_at'),
        Index('idx_conversations_request', 'is_message_request', 'request_status'),
    )


class ConversationParticipant(Base):
    """Conversation participants (many-to-many)"""
    __tablename__ = "conversation_participants"
    
    id = Column(String(36), primary_key=True, index=True)
    conversation_id = Column(String(36), 
                            ForeignKey("conversations.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                    nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))
    unread_count = Column(Integer, default=0)
    last_read_at = Column(DateTime(timezone=True))
    is_archived = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('conversation_id', 'user_id', 
                        name='uq_conversation_user'),
        Index('idx_participant_user', 'user_id'),
        Index('idx_participant_conversation', 'conversation_id'),
        Index('idx_participant_unread', 'user_id', 'unread_count'),
    )


class Message(Base):
    """Message model"""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, index=True)
    conversation_id = Column(String(36), 
                            ForeignKey("conversations.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"),
                      index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), 
                       server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    is_edited = Column(Boolean, default=False)
    
    # AI feature fields (future use)
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
    reports = relationship("MessageReport", back_populates="message",
                          cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('length(content) <= 2000', 
                       name='ck_message_content_length'),
        Index('idx_messages_conversation_created', 'conversation_id', 'created_at'),
        Index('idx_messages_sender', 'sender_id'),
        Index('idx_messages_created', 'created_at'),
    )


class MessageReadReceipt(Base):
    """Message read receipts"""
    __tablename__ = "message_read_receipts"
    
    id = Column(String(36), primary_key=True, index=True)
    message_id = Column(String(36), 
                       ForeignKey("messages.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                    nullable=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    message = relationship("Message", back_populates="read_receipts")
    user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('message_id', 'user_id', 
                        name='uq_message_user_receipt'),
        Index('idx_receipts_message', 'message_id'),
        Index('idx_receipts_user', 'user_id'),
    )


class MessageAttachment(Base):
    """Message attachments"""
    __tablename__ = "message_attachments"
    
    id = Column(String(36), primary_key=True, index=True)
    message_id = Column(String(36), 
                       ForeignKey("messages.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    file_type = Column(String(50), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    storage_url = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100))
    duration = Column(Integer)  # for audio/voice notes (seconds)
    width = Column(Integer)  # for images
    height = Column(Integer)  # for images
    thumbnail_url = Column(Text)  # for images/videos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    message = relationship("Message", back_populates="attachments")
    
    __table_args__ = (
        CheckConstraint('file_size > 0', name='ck_attachment_file_size'),
        Index('idx_attachments_message', 'message_id'),
        Index('idx_attachments_type', 'file_type'),
    )


class BlockedUser(Base):
    """Blocked users"""
    __tablename__ = "blocked_users"
    
    id = Column(String(36), primary_key=True, index=True)
    blocker_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    blocked_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    blocked_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text)
    
    # Relationships
    blocker = relationship("User", foreign_keys=[blocker_id])
    blocked = relationship("User", foreign_keys=[blocked_id])
    
    __table_args__ = (
        UniqueConstraint('blocker_id', 'blocked_id', 
                        name='uq_blocker_blocked'),
        Index('idx_blocks_blocker', 'blocker_id'),
        Index('idx_blocks_blocked', 'blocked_id'),
    )


class MessageReport(Base):
    """Message reports"""
    __tablename__ = "message_reports"
    
    id = Column(String(36), primary_key=True, index=True)
    message_id = Column(String(36), 
                       ForeignKey("messages.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    reporter_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False)
    reason = Column(String(50), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed = Column(Boolean, default=False, index=True)
    reviewed_at = Column(DateTime(timezone=True))
    reviewed_by = Column(String(36), ForeignKey("users.id"))
    action_taken = Column(String(100))
    
    # Relationships
    message = relationship("Message", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reporter_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    __table_args__ = (
        CheckConstraint('length(details) <= 500', 
                       name='ck_report_details_length'),
        Index('idx_reports_message', 'message_id'),
        Index('idx_reports_status', 'reviewed', 'created_at'),
    )


class UserMessageSettings(Base):
    """User message privacy settings"""
    __tablename__ = "user_message_settings"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                    unique=True, nullable=False, index=True)
    message_filter = Column(String(20), default='everyone')
    read_receipts_enabled = Column(Boolean, default=True)
    typing_indicators_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_settings_user', 'user_id'),
    )
