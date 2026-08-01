"""
Booking Models
Task 5.3: Booking System
"""

from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class BookingStatus(str, enum.Enum):
    """Booking status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventType(str, enum.Enum):
    """Event type"""
    CLUB = "club"
    FESTIVAL = "festival"
    PRIVATE_EVENT = "private_event"
    RADIO_SHOW = "radio_show"
    CORPORATE = "corporate"
    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    CONCERT = "concert"
    OTHER = "other"


class PaymentStatus(str, enum.Enum):
    """Payment status for bookings"""
    PENDING = "pending"
    HELD = "held"  # Escrow
    RELEASED = "released"
    REFUNDED = "refunded"


class Booking(Base):
    """Booking between client and artist"""
    __tablename__ = "bookings"
    
    id = Column(String(36), primary_key=True)
    
    # Parties
    client_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    artist_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Event details
    event_name = Column(String(255), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_date = Column(DateTime, nullable=False, index=True)
    event_duration = Column(Integer)  # Duration in minutes
    location = Column(String(500), nullable=False)
    venue_name = Column(String(255))
    
    # Financial
    budget = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    deposit_amount = Column(Float, default=0.0)
    platform_commission_rate = Column(Float, default=0.125)  # 12.5%
    platform_commission = Column(Float, default=0.0)
    artist_payout = Column(Float, default=0.0)
    
    # Details
    description = Column(Text)
    special_requirements = Column(Text)
    
    # Status
    status = Column(String(20), default="pending", index=True)
    
    # Contract & Payment
    contract_url = Column(String(500))
    contract_signed = Column(Boolean, default=False)
    contract_signed_at = Column(DateTime)
    invoice_url = Column(String(500))
    payment_status = Column(String(20), default="pending")
    payment_held = Column(Boolean, default=False)
    
    # Completion
    completed_at = Column(DateTime)
    rating = Column(Integer)  # 1-5 stars
    review = Column(Text)
    
    # Cancellation
    cancelled_by = Column(String(36))
    cancellation_reason = Column(Text)
    cancellation_fee = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = Column(DateTime)
    declined_at = Column(DateTime)
    
    # Relationships
    client = relationship("User", foreign_keys=[client_user_id], backref="bookings_as_client")
    artist = relationship("User", foreign_keys=[artist_user_id], backref="bookings_as_artist")


class BookingAvailability(Base):
    """Artist availability for bookings"""
    __tablename__ = "booking_availability"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Availability
    date = Column(DateTime, nullable=False, index=True)
    is_available = Column(Boolean, default=True)
    
    # Pricing
    base_rate = Column(Float)
    currency = Column(String(3), default="USD")
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="availability_slots")


class BookingMessage(Base):
    """Messages between client and artist for a booking"""
    __tablename__ = "booking_messages"
    
    id = Column(String(36), primary_key=True)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message
    sender_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    
    # Attachments
    attachment_url = Column(String(500))
    
    # Read status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    booking = relationship("Booking", backref="messages")
    sender = relationship("User", backref="booking_messages_sent")
