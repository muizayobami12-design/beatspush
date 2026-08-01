"""
User model - represents users in the database
Supports: Artists, DJs, Producers, and Fans
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
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
    
    # Profile basics
    full_name = Column(String(255), nullable=True)
    username = Column(String(100), unique=True, index=True, nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    promo_links = relationship("PromoLink", back_populates="user", cascade="all, delete-orphan")
    fan_club = relationship("FanClub", back_populates="creator", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
