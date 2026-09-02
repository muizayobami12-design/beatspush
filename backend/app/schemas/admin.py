"""
Pydantic schemas for Admin Dashboard
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AdminRole(str, Enum):
    MODERATOR = "moderator"
    ANALYST = "analyst"
    MANAGER = "manager"
    SUPER_ADMIN = "super_admin"


class ReportType(str, Enum):
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    COPYRIGHT_VIOLATION = "copyright_violation"
    SPAM = "spam"
    HARASSMENT = "harassment"
    SCAM = "scam"
    HATE_SPEECH = "hate_speech"
    ADULT_CONTENT = "adult_content"
    MISINFORMATION = "misinformation"
    OTHER = "other"


class ContentType(str, Enum):
    BEAT = "beat"
    TRACK = "track"
    POST = "post"
    COMMENT = "comment"
    USER_PROFILE = "user_profile"
    MESSAGE = "message"


class ModerationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REMOVED = "removed"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


# Admin User Schemas
class AdminUserCreate(BaseModel):
    """Schema for creating admin users"""
    user_id: str
    role: AdminRole = AdminRole.MODERATOR
    can_review_content: bool = True
    can_suspend_users: bool = False
    can_manage_payments: bool = False
    can_manage_admins: bool = False
    can_view_analytics: bool = True

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "role": "moderator",
                "can_review_content": True,
                "can_suspend_users": False
            }
        }


class AdminUserUpdate(BaseModel):
    """Schema for updating admin users"""
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None
    can_review_content: Optional[bool] = None
    can_suspend_users: Optional[bool] = None
    can_manage_payments: Optional[bool] = None
    can_manage_admins: Optional[bool] = None
    can_view_analytics: Optional[bool] = None


class AdminUserResponse(BaseModel):
    """Admin user response"""
    id: str
    user_id: str
    role: AdminRole
    is_active: bool
    appointed_at: datetime
    last_active_at: Optional[datetime]

    class Config:
        from_attributes = True


# Content Report Schemas
class ContentReportCreate(BaseModel):
    """Schema for creating content reports"""
    report_type: ReportType
    content_type: ContentType
    content_id: str
    content_owner_id: str
    description: Optional[str] = Field(None, max_length=2000)
    evidence_urls: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "report_type": "copyright_violation",
                "content_type": "beat",
                "content_id": "beat123",
                "description": "This beat is clearly a copy of artist X's work"
            }
        }


class ContentReportReview(BaseModel):
    """Schema for reviewing reports"""
    status: ModerationStatus
    action_taken: Optional[str] = Field(None, max_length=100)
    action_notes: Optional[str] = Field(None, max_length=1000)

    class Config:
        schema_extra = {
            "example": {
                "status": "approved",
                "action_taken": "removed",
                "action_notes": "Content verified as copyright violation"
            }
        }


class ContentReportResponse(BaseModel):
    """Content report response"""
    id: str
    reporter_id: str
    report_type: ReportType
    content_type: ContentType
    content_id: str
    content_owner_id: str
    status: ModerationStatus
    description: Optional[str]
    reported_at: datetime
    reviewed_at: Optional[datetime]
    action_taken: Optional[str]

    class Config:
        from_attributes = True


# User Moderation Schemas
class UserModerationUpdate(BaseModel):
    """Schema for moderating users"""
    status: ModerationStatus
    is_suspended: Optional[bool] = None
    is_banned: Optional[bool] = None
    can_upload: Optional[bool] = None
    can_post: Optional[bool] = None
    can_message: Optional[bool] = None
    reason: Optional[str] = Field(None, max_length=1000)
    suspended_until: Optional[datetime] = None
    warning_count: Optional[int] = Field(None, ge=0)

    class Config:
        schema_extra = {
            "example": {
                "status": "suspended",
                "is_suspended": True,
                "reason": "Multiple copyright violations",
                "suspended_until": "2024-02-01T00:00:00"
            }
        }


class UserModerationResponse(BaseModel):
    """User moderation info response"""
    user_id: str
    status: ModerationStatus
    is_suspended: bool
    is_banned: bool
    warning_count: int
    can_upload: bool
    can_post: bool
    can_message: bool
    reason: Optional[str]
    suspended_until: Optional[datetime]
    last_warning_at: Optional[datetime]

    class Config:
        from_attributes = True


# Dashboard & Analytics Schemas
class ReportStats(BaseModel):
    """Statistics on reports"""
    total_reports: int
    pending: int
    under_review: int
    approved: int
    rejected: int
    
    by_type: dict  # {report_type: count}
    by_content_type: dict  # {content_type: count}

    class Config:
        schema_extra = {
            "example": {
                "total_reports": 150,
                "pending": 20,
                "under_review": 10,
                "approved": 85,
                "rejected": 35,
                "by_type": {"copyright_violation": 50, "spam": 30},
                "by_content_type": {"beat": 60, "post": 40}
            }
        }


class UserStats(BaseModel):
    """Statistics on user moderation"""
    total_users: int
    active_users: int
    suspended_users: int
    banned_users: int
    warned_users: int
    
    avg_warning_count: float
    new_warnings_today: int

    class Config:
        schema_extra = {
            "example": {
                "total_users": 5000,
                "active_users": 4800,
                "suspended_users": 150,
                "banned_users": 50,
                "warned_users": 200
            }
        }


class PlatformMetricsResponse(BaseModel):
    """Platform metrics response"""
    metric_date: datetime
    metric_type: str
    
    # User Metrics
    active_users: int
    new_signups: int
    user_churn: int
    
    # Content Metrics
    new_beats: int
    new_tracks: int
    new_posts: int
    total_plays: int
    
    # Engagement
    total_purchases: int
    total_favorites: int
    total_shares: int
    
    # Revenue
    revenue_streams: float
    revenue_sales: float
    revenue_tips: float
    revenue_subscriptions: float
    total_revenue: float
    
    # Moderation
    reports_submitted: int
    reports_reviewed: int
    content_removed: int
    users_suspended: int

    class Config:
        from_attributes = True


class AdminDashboard(BaseModel):
    """Complete admin dashboard response"""
    # Quick Stats
    total_users: int
    new_signups_today: int
    suspended_count: int
    banned_count: int
    
    # Reports
    pending_reports: int
    reports_today: int
    report_stats: ReportStats
    
    # Recent Activity
    recent_reports: List[ContentReportResponse]
    recent_moderation_actions: List[dict]
    
    # Revenue & Metrics
    daily_revenue: float
    monthly_revenue: float
    platform_metrics: Optional[PlatformMetricsResponse]

    class Config:
        schema_extra = {
            "example": {
                "total_users": 5000,
                "new_signups_today": 12,
                "suspended_count": 150,
                "banned_count": 50,
                "pending_reports": 25,
                "daily_revenue": 5000.0
            }
        }


class ModerationQueue(BaseModel):
    """Moderation queue with priority sorting"""
    urgent_reports: List[ContentReportResponse]  # New + flagged
    routine_reports: List[ContentReportResponse]  # Standard review
    completed_today: int
    
    average_review_time: float  # minutes

    class Config:
        schema_extra = {
            "example": {
                "urgent_reports": [],
                "routine_reports": [],
                "completed_today": 15,
                "average_review_time": 12.5
            }
        }


class PaymentTrackingResponse(BaseModel):
    """Payment tracking and reconciliation"""
    total_revenue: float
    creator_payouts: float
    platform_fees: float
    pending_payouts: float
    
    by_source: dict  # {source: amount} - sales, tips, subscriptions, streaming
    by_currency: dict  # {currency: amount}
    
    payment_method_breakdown: dict
    failed_transactions: int
    pending_transactions: int

    class Config:
        schema_extra = {
            "example": {
                "total_revenue": 50000.0,
                "creator_payouts": 45000.0,
                "platform_fees": 5000.0,
                "by_source": {"sales": 30000, "tips": 15000, "subscriptions": 5000}
            }
        }


class AuditLogResponse(BaseModel):
    """Audit log entry response"""
    id: str
    admin_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
