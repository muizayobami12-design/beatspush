"""
Fan Club System Schemas - Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class SubscriptionStatusEnum(str, Enum):
    """Subscription status options"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class PaymentStatusEnum(str, Enum):
    """Payment status options"""
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PENDING = "pending"
    REFUNDED = "refunded"


class BillingCycleEnum(str, Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class PaymentProviderEnum(str, Enum):
    """Payment provider options"""
    STRIPE = "stripe"
    PAYSTACK = "paystack"


class ContentTypeEnum(str, Enum):
    """Exclusive content types"""
    POST = "post"
    TRACK = "track"
    VIDEO = "video"
    IMAGE = "image"
    EVENT = "event"


# ============================================================================
# FAN CLUB SCHEMAS
# ============================================================================

class FanClubCreate(BaseModel):
    """Request to create a fan club"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    welcome_message: Optional[str] = Field(None, max_length=1000)
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Fan club name cannot be empty')
        return v.strip()


class FanClubUpdate(BaseModel):
    """Request to update fan club"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    welcome_message: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


class FanClubResponse(BaseModel):
    """Fan club response"""
    id: str
    creator_id: str
    name: str
    description: Optional[str]
    welcome_message: Optional[str]
    is_active: bool
    total_members: int
    monthly_revenue: Decimal
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# MEMBERSHIP TIER SCHEMAS
# ============================================================================

class TierCreate(BaseModel):
    """Request to create membership tier"""
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    tier_level: int = Field(..., ge=1, le=3)
    price_monthly: Decimal = Field(..., ge=2.99, le=99.99, decimal_places=2)
    benefits: List[str] = Field(default_factory=list)
    
    @validator('price_monthly')
    def validate_price(cls, v):
        if v < Decimal('2.99'):
            raise ValueError('Monthly price must be at least $2.99')
        if v > Decimal('99.99'):
            raise ValueError('Monthly price cannot exceed $99.99')
        return v
    
    @validator('benefits')
    def validate_benefits(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 benefits allowed')
        return [b.strip() for b in v if b.strip()]
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Tier name cannot be empty')
        return v.strip()


class TierUpdate(BaseModel):
    """Request to update membership tier"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    price_monthly: Optional[Decimal] = Field(None, ge=2.99, le=99.99)
    benefits: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TierResponse(BaseModel):
    """Membership tier response"""
    id: str
    fan_club_id: str
    name: str
    description: Optional[str]
    tier_level: int
    price_monthly: Decimal
    price_yearly: Decimal
    benefits: List[str]
    is_active: bool
    subscriber_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# SUBSCRIPTION SCHEMAS
# ============================================================================

class SubscriptionCreate(BaseModel):
    """Request to create subscription"""
    tier_id: str = Field(..., min_length=36, max_length=36)
    billing_cycle: BillingCycleEnum
    payment_method_token: str  # Stripe/Paystack payment method token
    payment_provider: PaymentProviderEnum = PaymentProviderEnum.STRIPE
    
    @validator('tier_id')
    def validate_tier_id(cls, v):
        if len(v) != 36:
            raise ValueError('Invalid tier ID format')
        return v


class SubscriptionUpdate(BaseModel):
    """Request to update subscription"""
    new_tier_id: Optional[str] = Field(None, min_length=36, max_length=36)
    auto_renew: Optional[bool] = None


class SubscriptionResponse(BaseModel):
    """Subscription response"""
    id: str
    fan_club_id: str
    tier_id: str
    subscriber_id: str
    status: str
    billing_cycle: str
    price_paid: Decimal
    currency: str
    current_period_start: datetime
    current_period_end: datetime
    started_at: datetime
    cancelled_at: Optional[datetime]
    paused_at: Optional[datetime]
    paused_until: Optional[datetime]
    trial_ends_at: Optional[datetime]
    auto_renew: bool
    payment_provider: str
    created_at: datetime
    
    # Relationships (optional nested data)
    tier: Optional[TierResponse] = None
    
    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Paginated list of subscriptions"""
    subscriptions: List[SubscriptionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# PAYMENT SCHEMAS
# ============================================================================

class PaymentMethodRequest(BaseModel):
    """Payment method information"""
    payment_provider: PaymentProviderEnum
    payment_method_token: str  # Token from Stripe/Paystack
    save_for_future: bool = True


class PaymentResponse(BaseModel):
    """Payment transaction response"""
    id: str
    subscription_id: str
    amount: Decimal
    currency: str
    status: str
    payment_method: Optional[str]
    payment_provider: str
    failure_code: Optional[str]
    failure_message: Optional[str]
    retry_attempt: int
    platform_fee: Optional[Decimal]
    creator_payout: Optional[Decimal]
    paid_at: Optional[datetime]
    refunded_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# EXCLUSIVE CONTENT SCHEMAS
# ============================================================================

class ExclusiveContentCreate(BaseModel):
    """Request to mark content as exclusive"""
    content_type: ContentTypeEnum
    content_id: str = Field(..., min_length=36, max_length=36)
    minimum_tier_level: int = Field(..., ge=1, le=3)
    teaser_text: Optional[str] = Field(None, max_length=500)
    preview_url: Optional[str] = Field(None, max_length=500)
    
    @validator('content_id')
    def validate_content_id(cls, v):
        if len(v) != 36:
            raise ValueError('Invalid content ID format')
        return v


class ExclusiveContentResponse(BaseModel):
    """Exclusive content response"""
    id: str
    fan_club_id: str
    content_type: str
    content_id: str
    minimum_tier_level: int
    teaser_text: Optional[str]
    preview_url: Optional[str]
    view_count: int
    engagement_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContentAccessResponse(BaseModel):
    """Content access check response"""
    has_access: bool
    reason: Optional[str]  # Why access denied (if applicable)
    required_tier_level: Optional[int]
    current_tier_level: Optional[int]
    unlock_url: Optional[str]  # Link to subscribe page


# ============================================================================
# SUBSCRIBER MANAGEMENT SCHEMAS
# ============================================================================

class SubscriberInfo(BaseModel):
    """Basic subscriber information"""
    subscriber_id: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    tier_name: str
    tier_level: int
    subscription_status: str
    subscribed_since: datetime
    
    class Config:
        from_attributes = True


class SubscriberListResponse(BaseModel):
    """Paginated list of subscribers"""
    subscribers: List[SubscriberInfo]
    total: int
    page: int
    page_size: int
    total_pages: int


class BroadcastRequest(BaseModel):
    """Request to send announcement to members"""
    title: str = Field(..., min_length=3, max_length=100)
    message: str = Field(..., min_length=10, max_length=2000)
    tier_levels: Optional[List[int]] = Field(None, description="Send to specific tiers (1, 2, 3)")
    send_email: bool = True
    send_push: bool = True
    
    @validator('tier_levels')
    def validate_tier_levels(cls, v):
        if v:
            for level in v:
                if level < 1 or level > 3:
                    raise ValueError('Tier level must be between 1 and 3')
        return v


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class SubscriptionAnalytics(BaseModel):
    """Subscription analytics data"""
    total_subscribers: int
    subscribers_by_tier: Dict[str, int]  # tier_name -> count
    monthly_recurring_revenue: Decimal
    revenue_by_tier: Dict[str, Decimal]  # tier_name -> revenue
    churn_rate: float  # Percentage
    retention_rate: float  # Percentage
    average_subscription_duration_days: float
    total_revenue_ytd: Decimal
    new_subscribers_this_month: int
    cancelled_this_month: int
    revenue_growth_percentage: float


class EngagementMetrics(BaseModel):
    """Engagement metrics for exclusive content"""
    total_exclusive_posts: int
    total_views: int
    total_engagement: int  # likes + comments
    average_views_per_post: float
    top_performing_content: List[Dict[str, Any]]


class RevenueForecas(BaseModel):
    """Revenue forecast for next periods"""
    next_month_forecast: Decimal
    next_quarter_forecast: Decimal
    confidence_level: str  # low, medium, high


# ============================================================================
# GENERIC RESPONSE SCHEMAS
# ============================================================================

class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    details: Optional[str]
    success: bool = False
