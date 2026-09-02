"""
Track model - represents music tracks uploaded by users
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class TrackStatus(str, enum.Enum):
    """Track status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class TrackVisibility(str, enum.Enum):
    """Track visibility"""
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class Track(Base):
    """Track model - music tracks"""
    __tablename__ = "tracks"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Owner
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False)
    artist_name = Column(String(255), nullable=False)
    album = Column(String(255), nullable=True)
    
    # Genre & classification
    genre = Column(String(100), nullable=True)
    sub_genre = Column(String(100), nullable=True)
    mood_tags = Column(JSON, nullable=True)  # ["energetic", "happy", "chill"]
    language = Column(String(50), nullable=True)
    
    # Technical details
    duration = Column(Integer, nullable=True)  # Duration in seconds
    bpm = Column(Integer, nullable=True)  # Beats per minute
    key = Column(String(10), nullable=True)  # Musical key (e.g., "C Major", "Am")
    bitrate = Column(Integer, nullable=True)  # Audio bitrate
    sample_rate = Column(Integer, nullable=True)  # Sample rate (e.g., 44100)
    
    # Files
    audio_url = Column(String(500), nullable=True)  # Main audio file
    cover_art_url = Column(String(500), nullable=True)  # Cover artwork
    waveform_url = Column(String(500), nullable=True)  # Waveform image
    
    # Metadata
    description = Column(Text, nullable=True)
    lyrics = Column(Text, nullable=True)
    release_date = Column(DateTime(timezone=True), nullable=True)
    
    # Licensing & copyright
    isrc = Column(String(50), nullable=True)  # International Standard Recording Code
    copyright_info = Column(String(500), nullable=True)
    license_type = Column(String(100), nullable=True)  # "all_rights_reserved", "creative_commons", etc.
    
    # Collaboration
    featuring_artists = Column(JSON, nullable=True)  # List of featured artist IDs
    producers = Column(JSON, nullable=True)  # List of producer IDs
    
    # Status & visibility
    status = Column(SQLEnum(TrackStatus), default=TrackStatus.DRAFT, nullable=False)
    visibility = Column(SQLEnum(TrackVisibility), default=TrackVisibility.PUBLIC, nullable=False)
    
    # Flags
    is_explicit = Column(Boolean, default=False)
    is_downloadable = Column(Boolean, default=False)
    allow_comments = Column(Boolean, default=True)
    
    # AI Analysis (populated by AI service)
    ai_detected_genre = Column(String(100), nullable=True)
    ai_detected_mood = Column(JSON, nullable=True)
    ai_detected_bpm = Column(Integer, nullable=True)
    ai_detected_key = Column(String(10), nullable=True)
    ai_content_warning = Column(String(255), nullable=True)
    
    # Stats
    play_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="tracks")
    promo_links = relationship("PromoLink", back_populates="track", cascade="all, delete-orphan", lazy="select")
    posts = relationship("Post", back_populates="track")
    
    def __repr__(self):
        return f"<Track {self.title} by {self.artist_name}>"
