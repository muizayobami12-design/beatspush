"""
Live Streaming Models
Stream sessions, chat messages, tips during streams
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime as dt
from enum import Enum as PyEnum
import uuid

Base = declarative_base()


class StreamStatus(str, PyEnum):
    """Live stream status"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    PAUSED = "paused"
    ENDED = "ended"
    CANCELLED = "cancelled"


class LiveStream(Base):
    """Live streaming session"""
    __tablename__ = "live_streams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    streamer_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    # Stream details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # "DJ Set", "Tutorial", "Q&A", etc.
    thumbnail_url = Column(String(500), nullable=True)
    
    # Platform integration
    twitch_channel_id = Column(String(255), nullable=True, unique=True, index=True)
    twitch_stream_id = Column(String(255), nullable=True)
    stream_key = Column(String(255), nullable=True)
    
    # Status and timing
    status = Column(Enum(StreamStatus), default=StreamStatus.SCHEDULED, index=True)
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    
    # Stats
    peak_viewers = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_tips = Column(Float, default=0.0)
    messages_count = Column(Integer, default=0)
    
    # Settings
    is_public = Column(Boolean, default=True)
    allow_tips = Column(Boolean, default=True)
    allow_chat = Column(Boolean, default=True)
    moderators = Column(JSON, nullable=True)  # List of user IDs
    
    # Recording
    is_recorded = Column(Boolean, default=True)
    recording_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=dt.utcnow, index=True)
    updated_at = Column(DateTime, default=dt.utcnow, onupdate=dt.utcnow)
    
    # Relationships
    chat_messages = relationship("StreamChat", back_populates="stream", cascade="all, delete-orphan")
    tips = relationship("StreamTip", back_populates="stream", cascade="all, delete-orphan")


class StreamChat(Base):
    """Real-time chat messages during stream"""
    __tablename__ = "stream_chat"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stream_id = Column(String(36), ForeignKey("live_streams.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    message = Column(Text, nullable=False)
    message_type = Column(String(50))  # "text", "tip", "follow", "announcement"
    
    # Metadata
    is_moderator = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=dt.utcnow, index=True)
    
    # Relationships
    stream = relationship("LiveStream", back_populates="chat_messages")


class StreamTip(Base):
    """Tip/donation during live stream"""
    __tablename__ = "stream_tips"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stream_id = Column(String(36), ForeignKey("live_streams.id"), nullable=False, index=True)
    tipper_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    streamer_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="NGN")
    message = Column(Text, nullable=True)
    
    # Payment
    transaction_id = Column(String(255), nullable=True, unique=True)
    status = Column(String(50), default="completed")  # "pending", "completed", "failed"
    
    created_at = Column(DateTime, default=dt.utcnow, index=True)
    
    # Relationships
    stream = relationship("LiveStream", back_populates="tips")
