"""
Fan Club System Models
Task 7.5: Membership tiers, subscriptions, and exclusive content

Models for fan clubs, membership tiers, subscriptions, payments, and content gating.
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, ForeignKey, 
    DateTime, Numeric, CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
import enum
from app.db.database import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status types"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class PaymentStatus(str, enum.Enum):
    """Payment transaction status"""
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PENDING = "pending"
    REFUNDED = "refunded"


class BillingCycle(str, enum.Enum):
    """Subscription billing cycle"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class PaymentProvider(str, enum.Enum):
    """Payment service providers"""
    STRIPE = "stripe"
    PAYSTACK = "paystack"


class FanClub(Base):
    """Fan Club model - Creator's membership community"""
    __tablename__ = "fan_clubs"
    
    id = Column(String(36), primary_key=True, index=True)
    creator_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                       unique=True, nullable=False, index=True)
    
    # Basic info
    name = Column(String(100), nullable=False)
    description = Column(Text)
    welcome_message = Column(Text)  # Auto-sent to new members
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Cached metrics (updated via triggers/background jobs)
    total_members = Column(Integer, default=0)
    monthly_revenue = Column(Numeric(10, 2), default=0.00)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="fan_club")
    tiers = relationship("MembershipTier", back_populates="fan_club",
                        cascade="all, delete-orphan", order_by="MembershipTier.tier_level")
    subscriptions = relationship("Subscription", back_populates="fan_club",
                                cascade="all, delete-orphan")
    exclusive_content = relationship("ExclusiveContent", back_populates="fan_club",
                                    cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_fanclub_creator', 'creator_id'),
        Index('idx_fanclub_active', 'is_active'),
    )


class MembershipTier(Base):
    """Membership Tier model - Subscription levels with pricing and benefits"""
    __tablename__ = "membership_tiers"
    
    id = Column(String(36), primary_key=True, index=True)
    fan_club_id = Column(String(36), ForeignKey("fan_clubs.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    
    # Tier details
    name = Column(String(50), nullable=False)  # e.g., "Bronze", "Silver", "Gold"
    description = Column(Text)
    tier_level = Column(Integer, nullable=False)  # 1=Bronze, 2=Silver, 3=Gold
    
    # Pricing (in USD)
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_yearly = Column(Numeric(10, 2), nullable=False)
    
    # Benefits (JSON array of strings)
    benefits = Column(JSON, default=list)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Cached metrics
    subscriber_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fan_club = relationship("FanClub", back_populates="tiers")
    subscriptions = relationship("Subscription", back_populates="tier",
                                cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('fan_club_id', 'name', name='uq_fanclub_tier_name'),
        UniqueConstraint('fan_club_id', 'tier_level', name='uq_fanclub_tier_level'),
        CheckConstraint('price_monthly >= 2.99', name='ck_tier_min_monthly_price'),
        CheckConstraint('price_monthly <= 99.99', name='ck_tier_max_monthly_price'),
        CheckConstraint('tier_level BETWEEN 1 AND 3', name='ck_tier_level_range'),
        Index('idx_tier_fanclub', 'fan_club_id'),
        Index('idx_tier_level', 'tier_level'),
    )


class Subscription(Base):
    """Subscription model - Fan's membership to a creator's tier"""
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True, index=True)
    fan_club_id = Column(String(36), ForeignKey("fan_clubs.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    tier_id = Column(String(36), ForeignKey("membership_tiers.id", ondelete="CASCADE"),
                    nullable=False, index=True)
    subscriber_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    
    # Subscription details
    status = Column(String(20), nullable=False, default="active", index=True)
    billing_cycle = Column(String(10), nullable=False)  # monthly, yearly
    price_paid = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Period tracking
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    next_billing_date = Column(DateTime(timezone=True), index=True)
    
    # Lifecycle dates
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    cancelled_at = Column(DateTime(timezone=True))
    paused_at = Column(DateTime(timezone=True))
    paused_until = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    
    # Trial support
    trial_ends_at = Column(DateTime(timezone=True))
    trial_end_date = Column(DateTime(timezone=True))  # Alias for trial_ends_at
    
    # Settings
    auto_renew = Column(Boolean, default=True)
    
    # Payment tracking
    failed_payment_count = Column(Integer, default=0)
    
    # Payment provider integration
    payment_provider = Column(String(20), nullable=False)  # stripe, paystack
    payment_provider_subscription_id = Column(String(100), unique=True)
    payment_provider_customer_id = Column(String(100))
    
    # Provider-specific IDs (for webhook processing)
    stripe_subscription_id = Column(String(100), unique=True, index=True)
    paystack_subscription_code = Column(String(100), unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fan_club = relationship("FanClub", back_populates="subscriptions")
    tier = relationship("MembershipTier", back_populates="subscriptions")
    subscriber = relationship("User")
    payments = relationship("SubscriptionPayment", back_populates="subscription",
                           cascade="all, delete-orphan", order_by="SubscriptionPayment.created_at.desc()")
    
    __table_args__ = (
        UniqueConstraint('fan_club_id', 'subscriber_id', name='uq_fanclub_subscriber'),
        Index('idx_subscription_fanclub', 'fan_club_id'),
        Index('idx_subscription_subscriber', 'subscriber_id'),
        Index('idx_subscription_status', 'status'),
        Index('idx_subscription_period_end', 'current_period_end'),
        Index('idx_subscription_provider', 'payment_provider_subscription_id'),
    )


class SubscriptionPayment(Base):
    """Subscription Payment model - Transaction records for subscriptions"""
    __tablename__ = "subscription_payments"
    
    id = Column(String(36), primary_key=True, index=True)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    
    # Payment amount
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Status
    status = Column(String(20), nullable=False, index=True)
    payment_method = Column(String(50))  # card, wallet, bank_transfer
    
    # Payment provider details
    payment_provider = Column(String(20), nullable=False)
    payment_provider_payment_id = Column(String(100), unique=True)
    payment_provider_charge_id = Column(String(100))
    payment_provider_invoice_id = Column(String(100))
    
    # Failure tracking
    failure_code = Column(String(50))
    failure_message = Column(Text)
    retry_attempt = Column(Integer, default=0)
    next_retry_at = Column(DateTime(timezone=True))
    
    # Revenue split (calculated at payment time)
    platform_fee = Column(Numeric(10, 2))  # 10% of amount
    creator_payout = Column(Numeric(10, 2))  # 90% of amount
    payment_processing_fee = Column(Numeric(10, 2))  # Stripe/Paystack fee
    
    # Timestamps
    paid_at = Column(DateTime(timezone=True))
    refunded_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="payments")
    
    __table_args__ = (
        Index('idx_payment_subscription', 'subscription_id'),
        Index('idx_payment_status', 'status'),
        Index('idx_payment_date', 'paid_at'),
        Index('idx_payment_provider_id', 'payment_provider_payment_id'),
        CheckConstraint('amount > 0', name='ck_payment_positive_amount'),
    )


class ExclusiveContent(Base):
    """Exclusive Content model - Marks content as tier-gated"""
    __tablename__ = "exclusive_content"
    
    id = Column(String(36), primary_key=True, index=True)
    fan_club_id = Column(String(36), ForeignKey("fan_clubs.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    
    # Content reference
    content_type = Column(String(20), nullable=False, index=True)  # post, track, video, image, event
    content_id = Column(String(36), nullable=False, index=True)
    
    # Access control
    minimum_tier_level = Column(Integer, nullable=False)  # 1, 2, or 3
    
    # Metadata
    teaser_text = Column(Text)  # First 20% shown to non-subscribers
    preview_url = Column(String(500))  # Thumbnail/preview for locked content
    
    # Stats
    view_count = Column(Integer, default=0)
    engagement_count = Column(Integer, default=0)  # likes + comments
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    fan_club = relationship("FanClub", back_populates="exclusive_content")
    
    __table_args__ = (
        UniqueConstraint('content_type', 'content_id', name='uq_content_exclusivity'),
        CheckConstraint('minimum_tier_level BETWEEN 1 AND 3', name='ck_exclusive_tier_range'),
        Index('idx_exclusive_fanclub', 'fan_club_id'),
        Index('idx_exclusive_content', 'content_type', 'content_id'),
    )


class CreatorPayout(Base):
    """Creator Payout model - Monthly payouts to creators"""
    __tablename__ = "creator_payouts"
    
    id = Column(String(36), primary_key=True, index=True)
    creator_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    fan_club_id = Column(String(36), ForeignKey("fan_clubs.id", ondelete="CASCADE"),
                        nullable=False)
    
    # Payout details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, index=True)  # pending, processing, completed, failed
    
    # Payment method
    payout_method = Column(String(50))  # bank_transfer, paypal
    payout_destination = Column(String(200))  # Bank account or PayPal email (encrypted)
    
    # Provider details
    payment_provider = Column(String(20))
    payment_provider_payout_id = Column(String(100), unique=True)
    
    # Failure tracking
    failure_reason = Column(Text)
    
    # Timestamps
    scheduled_at = Column(DateTime(timezone=True))
    processed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User")
    fan_club = relationship("FanClub")
    
    __table_args__ = (
        Index('idx_payout_creator', 'creator_id'),
        Index('idx_payout_status', 'status'),
        Index('idx_payout_scheduled', 'scheduled_at'),
        CheckConstraint('amount >= 50.00', name='ck_payout_minimum'),
    )
