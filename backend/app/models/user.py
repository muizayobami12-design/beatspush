"""
User model - represents users in the database
Supports: Artists, DJs, Producers, and Fans
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class UserRole(str, enum.Enum):
    """User role types"""
    ARTIST = "artist"
    DJ = "dj"
    PRODUCER = "producer"
    FAN = "fan"
    ADMIN = "admin"


class UserTier(str, enum.Enum):
    """User subscription tier for AI features"""
    FREE = "FREE"
    PREMIUM = "PREMIUM"


class User(Base):
    """User model"""
    __tablename__ = "users"

    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User type
    role = Column(SQLEnum(UserRole), nullable=False)
    tier = Column(SQLEnum(UserTier), default=UserTier.FREE, nullable=True)  # AI subscription tier (nullable for now)
    
    # Profile basics
    full_name = Column(String(255), nullable=True)
    username = Column(String(100), unique=True, index=True, nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Security - Device Tracking
    device_id = Column(String(255), nullable=True, index=True)  # FingerprintJS visitor ID
    device_info = Column(String(1000), nullable=True)  # JSON string of device metadata
    
    # Security - Login Tracking
    last_login_ip = Column(String(45), nullable=True)  # IPv4 or IPv6
    last_login_country = Column(String(2), nullable=True)  # ISO country code
    failed_login_attempts = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    promo_links = relationship("PromoLink", back_populates="user", cascade="all, delete-orphan")
    fan_club = relationship("FanClub", back_populates="creator", uselist=False, cascade="all, delete-orphan")
    
    # Social feed relationships
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    post_likes = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
    post_comments = relationship("PostComment", back_populates="user", cascade="all, delete-orphan")
    post_shares = relationship("PostShare", back_populates="user", cascade="all, delete-orphan")
    post_saves = relationship("PostSave", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
