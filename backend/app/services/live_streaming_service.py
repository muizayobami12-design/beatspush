"""
Live Streaming Service
Twitch integration, real-time WebSocket chat, tips during streams, stream management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
import json
import uuid
from enum import Enum as PyEnum
import asyncio
import aiohttp

Base = declarative_base()


class StreamStatus(PyEnum):
    """Live stream status"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    PAUSED = "paused"
    ENDED = "ended"
    CANCELLED = "cancelled"


class LiveStream(Base):
    """Live streaming session"""
    __tablename__ = "live_streams"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    streamer_id = Column(String, ForeignKey("user.id"), nullable=False)
    
    # Stream details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # "DJ Set", "Production Tutorial", "Q&A", etc.
    thumbnail_url = Column(String(500))
    
    # Platform integration
    twitch_channel_id = Column(String(255), unique=True, index=True)
    twitch_stream_id = Column(String(255))
    stream_key = Column(String(255))  # Private key for streaming software
    
    # Status and timing
    status = Column(Enum(StreamStatus), default=StreamStatus.SCHEDULED)
    scheduled_at = Column(DateTime)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    duration = Column(Integer)  # seconds
    
    # Stats
    peak_viewers = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_tips = Column(Float, default=0.0)
    messages_count = Column(Integer, default=0)
    
    # Settings
    is_public = Column(Boolean, default=True)
    allow_tips = Column(Boolean, default=True)
    allow_chat = Column(Boolean, default=True)
    moderators = Column(JSON)  # List of user IDs with mod permissions
    
    # Recording
    is_recorded = Column(Boolean, default=True)
    recording_url = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StreamChat(Base):
    """Real-time chat messages during stream"""
    __tablename__ = "stream_chat"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stream_id = Column(String, ForeignKey("live_streams.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    
    message = Column(Text, nullable=False)
    message_type = Column(String(50))  # "text", "tip", "follow", "announcement"
    
    # Metadata
    is_moderator = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class StreamTip(Base):
    """Tip/donation during live stream"""
    __tablename__ = "stream_tips"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stream_id = Column(String, ForeignKey("live_streams.id"), nullable=False, index=True)
    tipper_id = Column(String, ForeignKey("user.id"), nullable=False)
    streamer_id = Column(String, ForeignKey("user.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="NGN")
    message = Column(Text)
    
    # Payment
    transaction_id = Column(String(255), unique=True)
    status = Column(String(50), default="completed")  # "pending", "completed", "failed"
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ============ LIVE STREAMING SERVICE ============

class LiveStreamingService:
    """Manage live streams and real-time interactions"""

    def __init__(self, twitch_client_id: str = None, twitch_oauth_token: str = None):
        self.twitch_client_id = twitch_client_id
        self.twitch_oauth_token = twitch_oauth_token
        
        # WebSocket connections tracking
        self.active_connections: Dict[str, Set[str]] = {}  # stream_id -> set of user_ids
        self.stream_viewers: Dict[str, int] = {}  # stream_id -> viewer count

    # ============ STREAM MANAGEMENT ============

    async def create_stream(
        self,
        streamer_id: str,
        title: str,
        description: str,
        scheduled_at: Optional[datetime],
        category: str,
        db: Session,
    ) -> Dict:
        """Create new scheduled stream"""

        stream = LiveStream(
            streamer_id=streamer_id,
            title=title,
            description=description,
            category=category,
            scheduled_at=scheduled_at or datetime.utcnow() + timedelta(hours=1),
            status=StreamStatus.SCHEDULED,
            stream_key=str(uuid.uuid4()),  # Generate private stream key
        )

        db.add(stream)
        db.commit()

        return {
            "stream_id": stream.id,
            "title": title,
            "status": "scheduled",
            "scheduled_at": stream.scheduled_at.isoformat(),
            "stream_key": stream.stream_key,  # Share with streaming software
        }

    async def start_stream(
        self,
        stream_id: str,
        db: Session,
    ) -> Dict:
        """Start live stream"""

        stream = db.query(LiveStream).filter_by(id=stream_id).first()
        if not stream:
            return {"error": "Stream not found"}

        if stream.status != StreamStatus.SCHEDULED:
            return {"error": f"Cannot start stream in {stream.status.value} status"}

        stream.status = StreamStatus.LIVE
        stream.started_at = datetime.utcnow()

        # Create Twitch stream entry (if using Twitch)
        if self.twitch_client_id:
            twitch_result = await self._create_twitch_stream(stream, db)
            if "error" not in twitch_result:
                stream.twitch_stream_id = twitch_result.get("stream_id")
                stream.twitch_channel_id = twitch_result.get("channel_id")

        db.commit()

        # Initialize viewer tracking
        self.active_connections[stream_id] = set()
        self.stream_viewers[stream_id] = 0

        return {
            "stream_id": stream.id,
            "status": "live",
            "started_at": stream.started_at.isoformat(),
            "watch_url": f"https://beatpush.com/stream/{stream_id}",
        }

    async def end_stream(
        self,
        stream_id: str,
        db: Session,
    ) -> Dict:
        """End live stream"""

        stream = db.query(LiveStream).filter_by(id=stream_id).first()
        if not stream:
            return {"error": "Stream not found"}

        stream.status = StreamStatus.ENDED
        stream.ended_at = datetime.utcnow()

        if stream.started_at:
            stream.duration = int((stream.ended_at - stream.started_at).total_seconds())

        # Update total views
        stream.total_views = self.stream_viewers.get(stream_id, 0)

        db.commit()

        # Cleanup
        if stream_id in self.active_connections:
            del self.active_connections[stream_id]
        if stream_id in self.stream_viewers:
            del self.stream_viewers[stream_id]

        return {
            "stream_id": stream.id,
            "status": "ended",
            "duration": stream.duration,
            "total_views": stream.total_views,
            "total_tips": float(stream.total_tips),
        }

    # ============ REAL-TIME CHAT ============

    async def send_chat_message(
        self,
        stream_id: str,
        user_id: str,
        message: str,
        is_moderator: bool = False,
        db: Session = None,
    ) -> Dict:
        """Send chat message to stream"""

        stream = db.query(LiveStream).filter_by(id=stream_id).first()
        if not stream or stream.status != StreamStatus.LIVE:
            return {"error": "Stream not found or not live"}

        if not stream.allow_chat:
            return {"error": "Chat disabled for this stream"}

        # Moderation - check for spam/abuse
        if not is_moderator:
            message = self._moderate_message(message)

        chat = StreamChat(
            stream_id=stream_id,
            user_id=user_id,
            message=message,
            message_type="text",
            is_moderator=is_moderator,
        )

        stream.messages_count += 1
        db.add(chat)
        db.commit()

        return {
            "message_id": chat.id,
            "user_id": user_id,
            "message": message,
            "timestamp": chat.created_at.isoformat(),
            "is_moderator": is_moderator,
        }

    async def get_chat_history(
        self,
        stream_id: str,
        limit: int = 50,
        db: Session = None,
    ) -> List[Dict]:
        """Get recent chat messages"""

        messages = db.query(StreamChat).filter(
            StreamChat.stream_id == stream_id,
            StreamChat.deleted_at.is_(None),
        ).order_by(
            StreamChat.created_at.desc()
        ).limit(limit).all()

        return [
            {
                "message_id": m.id,
                "user_id": m.user_id,
                "message": m.message,
                "is_moderator": m.is_moderator,
                "created_at": m.created_at.isoformat(),
            }
            for m in reversed(messages)
        ]

    async def delete_chat_message(
        self,
        message_id: str,
        moderator_id: str,
        db: Session = None,
    ) -> Dict:
        """Delete inappropriate chat message"""

        message = db.query(StreamChat).filter_by(id=message_id).first()
        if not message:
            return {"error": "Message not found"}

        message.deleted_at = datetime.utcnow()
        db.commit()

        return {"status": "deleted", "message_id": message_id}

    # ============ TIPPING ============

    async def send_tip(
        self,
        stream_id: str,
        tipper_id: str,
        amount: float,
        message: Optional[str],
        db: Session = None,
    ) -> Dict:
        """Send tip during live stream"""

        stream = db.query(LiveStream).filter_by(id=stream_id).first()
        if not stream:
            return {"error": "Stream not found"}

        if not stream.allow_tips:
            return {"error": "Tips disabled for this stream"}

        # Create tip record
        tip = StreamTip(
            stream_id=stream_id,
            tipper_id=tipper_id,
            streamer_id=stream.streamer_id,
            amount=amount,
            message=message,
        )

        # Update stream stats
        stream.total_tips += amount

        db.add(tip)
        db.commit()

        # Send tip notification to chat
        tip_message = f"🎁 {tipper_id} tipped ₦{amount:,.0f}"
        if message:
            tip_message += f": {message}"

        tip_chat = StreamChat(
            stream_id=stream_id,
            user_id=tipper_id,
            message=tip_message,
            message_type="tip",
        )
        db.add(tip_chat)
        db.commit()

        return {
            "tip_id": tip.id,
            "amount": amount,
            "status": "processed",
            "created_at": tip.created_at.isoformat(),
        }

    async def get_stream_tips(
        self,
        stream_id: str,
        limit: int = 20,
        db: Session = None,
    ) -> List[Dict]:
        """Get tip history for stream"""

        tips = db.query(StreamTip).filter_by(stream_id=stream_id).order_by(
            StreamTip.created_at.desc()
        ).limit(limit).all()

        return [
            {
                "tipper_id": t.tipper_id,
                "amount": float(t.amount),
                "message": t.message,
                "created_at": t.created_at.isoformat(),
            }
            for t in reversed(tips)
        ]

    # ============ VIEWER TRACKING ============

    async def on_viewer_join(
        self,
        stream_id: str,
        user_id: str,
    ):
        """Track viewer joining stream"""
        if stream_id not in self.active_connections:
            self.active_connections[stream_id] = set()

        self.active_connections[stream_id].add(user_id)
        self.stream_viewers[stream_id] = len(self.active_connections[stream_id])

    async def on_viewer_leave(
        self,
        stream_id: str,
        user_id: str,
    ):
        """Track viewer leaving stream"""
        if stream_id in self.active_connections:
            self.active_connections[stream_id].discard(user_id)
            self.stream_viewers[stream_id] = len(self.active_connections[stream_id])

    def get_viewer_count(self, stream_id: str) -> int:
        """Get current viewer count"""
        return self.stream_viewers.get(stream_id, 0)

    # ============ STREAM STATS ============

    async def get_stream_stats(
        self,
        stream_id: str,
        db: Session = None,
    ) -> Dict:
        """Get detailed stream statistics"""

        stream = db.query(LiveStream).filter_by(id=stream_id).first()
        if not stream:
            return {"error": "Stream not found"}

        current_viewers = self.get_viewer_count(stream_id)
        total_messages = db.query(StreamChat).filter_by(stream_id=stream_id).count()
        total_tips = db.query(StreamTip).filter_by(stream_id=stream_id).count()

        return {
            "stream_id": stream.id,
            "title": stream.title,
            "status": stream.status.value,
            "streamer_id": stream.streamer_id,
            "current_viewers": current_viewers,
            "peak_viewers": stream.peak_viewers,
            "total_views": stream.total_views,
            "total_messages": total_messages,
            "total_tips": float(stream.total_tips),
            "total_tip_count": total_tips,
            "duration": stream.duration,
            "started_at": stream.started_at.isoformat() if stream.started_at else None,
            "ended_at": stream.ended_at.isoformat() if stream.ended_at else None,
        }

    # ============ UTILITY METHODS ============

    def _moderate_message(self, message: str) -> str:
        """Basic message moderation (filter spam/profanity)"""
        # Implement profanity filter, spam detection, etc.
        return message[:500]  # Limit message length

    async def _create_twitch_stream(self, stream: LiveStream, db: Session) -> Dict:
        """Create stream entry on Twitch (if integrated)"""
        if not self.twitch_client_id or not self.twitch_oauth_token:
            return {}

        headers = {
            "Client-ID": self.twitch_client_id,
            "Authorization": f"Bearer {self.twitch_oauth_token}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                # This would call Twitch API to create a stream
                # For now, return mock response
                return {
                    "stream_id": str(uuid.uuid4()),
                    "channel_id": str(uuid.uuid4()),
                }
        except Exception as e:
            print(f"Twitch integration error: {e}")
            return {}

    # ============ SCHEDULE MANAGEMENT ============

    async def get_upcoming_streams(
        self,
        limit: int = 10,
        db: Session = None,
    ) -> List[Dict]:
        """Get upcoming scheduled streams"""

        streams = db.query(LiveStream).filter(
            LiveStream.status == StreamStatus.SCHEDULED,
            LiveStream.scheduled_at > datetime.utcnow(),
        ).order_by(
            LiveStream.scheduled_at
        ).limit(limit).all()

        return [
            {
                "stream_id": s.id,
                "title": s.title,
                "streamer_id": s.streamer_id,
                "category": s.category,
                "scheduled_at": s.scheduled_at.isoformat(),
            }
            for s in streams
        ]
