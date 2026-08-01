"""
Tip Models
Task 5.2: Tipping System
"""

from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


class TipStatus(str, enum.Enum):
    """Tip status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class WithdrawalStatus(str, enum.Enum):
    """Withdrawal request status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Tip(Base):
    """Tip/donation from one user to another"""
    __tablename__ = "tips"
    
    id = Column(String(36), primary_key=True)
    
    # Parties
    from_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    to_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Amount
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Optional context
    track_id = Column(String(36), ForeignKey("tracks.id", ondelete="SET NULL"), nullable=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    message = Column(Text)
    
    # Privacy
    is_anonymous = Column(Boolean, default=False)
    
    # Payment details
    payment_method = Column(String(50))
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_provider = Column(String(50))
    payment_transaction_id = Column(String(255))
    
    # Platform fee (2-3%)
    platform_fee = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)
    
    # Status
    status = Column(SQLEnum(TipStatus), default=TipStatus.COMPLETED)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    paid_at = Column(DateTime)
    
    # Relationships
    from_user = relationship("User", foreign_keys=[from_user_id], backref="tips_sent")
    to_user = relationship("User", foreign_keys=[to_user_id], backref="tips_received")
    track = relationship("Track", backref="tips")


class TipWithdrawal(Base):
    """Withdrawal request for tips"""
    __tablename__ = "tip_withdrawals"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Amount
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Withdrawal details
    withdrawal_method = Column(String(50), nullable=False)
    account_details = Column(Text)
    
    # Status
    status = Column(SQLEnum(WithdrawalStatus), default=WithdrawalStatus.PENDING, index=True)
    
    # Processing
    processed_by = Column(String(36))
    processed_at = Column(DateTime)
    transaction_id = Column(String(255))
    
    # Notes
    notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="withdrawals")


class UserBalance(Base):
    """User balance tracking"""
    __tablename__ = "user_balances"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Balance
    available_balance = Column(Float, default=0.0)
    pending_balance = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    total_withdrawn = Column(Float, default=0.0)
    
    # Currency
    currency = Column(String(3), default="USD")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="balance", uselist=False)
