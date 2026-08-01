"""
Beat Models
Task 5.4: Beat Marketplace
"""

from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class LicenseType(str, enum.Enum):
    """License type for beat purchases"""
    LEASE = "lease"
    EXCLUSIVE = "exclusive"


class BeatStatus(str, enum.Enum):
    """Beat status"""
    DRAFT = "draft"
    ACTIVE = "active"
    SOLD_EXCLUSIVE = "sold_exclusive"
    ARCHIVED = "archived"


class PurchaseStatus(str, enum.Enum):
    """Purchase status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Beat(Base):
    """Beat/Instrumental for sale"""
    __tablename__ = "beats"
    
    id = Column(String(36), primary_key=True)
    
    # Producer
    producer_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Beat details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Audio files
    tagged_audio_url = Column(String(500), nullable=False)  # With producer tag/voiceover
    untagged_audio_url = Column(String(500))  # Clean version (for purchases)
    waveform_url = Column(String(500))
    cover_art_url = Column(String(500))
    
    # Technical details
    bpm = Column(Integer)
    musical_key = Column(String(10))
    genre = Column(String(100))
    mood = Column(String(100))
    duration = Column(Integer)  # in seconds
    
    # Pricing (in USD)
    lease_price = Column(Float)
    exclusive_price = Column(Float)
    
    # License terms
    lease_terms = Column(Text)
    exclusive_terms = Column(Text)
    
    # Availability
    is_available = Column(Boolean, default=True)
    is_exclusive_sold = Column(Boolean, default=False)
    
    # Statistics
    play_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Platform
    platform_commission_rate = Column(Float, default=0.15)  # 15%
    
    # Metadata
    tags = Column(Text)  # Comma-separated
    
    # Status
    status = Column(String(20), default="active", index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    # Relationships
    producer = relationship("User", backref="beats")


class BeatPurchase(Base):
    """Beat purchase transaction"""
    __tablename__ = "beat_purchases"
    
    id = Column(String(36), primary_key=True)
    
    # Parties
    beat_id = Column(String(36), ForeignKey("beats.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    producer_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Purchase details
    license_type = Column(String(20), nullable=False)  # lease or exclusive
    purchase_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Platform fee
    platform_commission_rate = Column(Float, nullable=False)
    platform_commission = Column(Float, nullable=False)
    producer_payout = Column(Float, nullable=False)
    
    # Payment
    payment_status = Column(String(20), default="pending")
    payment_transaction_id = Column(String(255))
    
    # License
    license_certificate_url = Column(String(500))
    license_key = Column(String(100))
    
    # Download
    download_url = Column(String(500))
    download_count = Column(Integer, default=0)
    download_limit = Column(Integer, default=10)
    
    # Status
    status = Column(String(20), default="completed")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)
    
    # Relationships
    beat = relationship("Beat", backref="purchases")
    buyer = relationship("User", foreign_keys=[buyer_user_id], backref="beat_purchases")
    producer = relationship("User", foreign_keys=[producer_user_id], backref="beat_sales")


class BeatFavorite(Base):
    """User's favorite beats"""
    __tablename__ = "beat_favorites"
    
    id = Column(String(36), primary_key=True)
    beat_id = Column(String(36), ForeignKey("beats.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    beat = relationship("Beat", backref="favorites")
    user = relationship("User", backref="favorite_beats")


class BeatPlay(Base):
    """Beat play tracking"""
    __tablename__ = "beat_plays"
    
    id = Column(String(36), primary_key=True)
    beat_id = Column(String(36), ForeignKey("beats.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    
    # Play details
    duration_played = Column(Integer)  # seconds
    completed = Column(Boolean, default=False)
    
    # Context
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    beat = relationship("Beat", backref="plays")
    user = relationship("User", backref="beat_plays")
