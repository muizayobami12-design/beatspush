"""
Admin Dashboard & Moderation Models

Manages admin users, moderation queue, reports, and platform analytics.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid

from app.db.database import Base


class ModerationStatus(str, PyEnum):
    """Status of moderation action"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REMOVED = "removed"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class ReportType(str, PyEnum):
    """Type of content report"""
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    COPYRIGHT_VIOLATION = "copyright_violation"
    SPAM = "spam"
    HARASSMENT = "harassment"
    SCAM = "scam"
    HATE_SPEECH = "hate_speech"
    ADULT_CONTENT = "adult_content"
    MISINFORMATION = "misinformation"
    OTHER = "other"


class ContentType(str, PyEnum):
    """Type of content being moderated"""
    BEAT = "beat"
    TRACK = "track"
    POST = "post"
    COMMENT = "comment"
    USER_PROFILE = "user_profile"
    MESSAGE = "message"


class AdminRole(str, PyEnum):
    """Admin privilege levels"""
    MODERATOR = "moderator"  # Can review content and users
    ANALYST = "analyst"      # Can view analytics only
    MANAGER = "manager"      # Can manage other admins
    SUPER_ADMIN = "super_admin"  # Full access


class AdminUser(Base):
    """
    Model for admin/moderator users

    Admin users have special permissions to moderate content,
    manage users, view analytics, and manage the platform.
    """
    __tablename__ = "admin_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # User Reference
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Admin Details
    role = Column(Enum(AdminRole), default=AdminRole.MODERATOR, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Permissions
    can_review_content = Column(Boolean, default=True)
    can_suspend_users = Column(Boolean, default=False)
    can_manage_payments = Column(Boolean, default=False)
    can_manage_admins = Column(Boolean, default=False)
    can_view_analytics = Column(Boolean, default=True)
    can_access_all_reports = Column(Boolean, default=False)
    
    # Audit
    appointed_by = Column(String(36), ForeignKey("admin_users.id"), nullable=True)
    appointed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="admin_profile")
    appointed_admin = relationship("AdminUser", remote_side=[id], foreign_keys=[appointed_by])

    def __repr__(self):
        return f"<AdminUser(id={self.id}, role={self.role}, user_id={self.user_id})>"


class ContentReport(Base):
    """
    Model for user reports of inappropriate content

    Users can report beats, tracks, posts, comments, etc. for violation
    of community guidelines. Admins review and take action.
    """
    __tablename__ = "content_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Report Details
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    report_type = Column(Enum(ReportType), nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    
    # What's being reported
    content_id = Column(String(36), nullable=False)  # ID of beat, post, comment, etc.
    content_owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Report Content
    description = Column(Text, nullable=True)
    evidence_urls = Column(Text, nullable=True)  # Comma-separated URLs if applicable
    
    # Status & Action
    status = Column(Enum(ModerationStatus), default=ModerationStatus.PENDING, nullable=False, index=True)
    reviewed_by = Column(String(36), ForeignKey("admin_users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Action Taken
    action_taken = Column(String(100), nullable=True)  # removed, suspended, warning, closed
    action_notes = Column(Text, nullable=True)
    
    # Metadata
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], backref="reports_made")
    content_owner = relationship("User", foreign_keys=[content_owner_id], backref="reports_against")
    reviewer = relationship("AdminUser", backref="reviewed_reports")

    def __repr__(self):
        return f"<ContentReport(id={self.id}, type={self.report_type}, status={self.status})>"


class UserModeration(Base):
    """
    Model for user account moderation/restrictions

    Tracks warnings, suspensions, bans, and other account actions.
    """
    __tablename__ = "user_moderation"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # User Being Moderated
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Status
    status = Column(Enum(ModerationStatus), default=ModerationStatus.APPROVED, nullable=False)
    
    # Restrictions
    is_suspended = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    can_upload = Column(Boolean, default=True)
    can_post = Column(Boolean, default=True)
    can_message = Column(Boolean, default=True)
    
    # Reason & Dates
    reason = Column(Text, nullable=True)
    suspended_at = Column(DateTime, nullable=True)
    suspended_until = Column(DateTime, nullable=True)
    
    # Warning System
    warning_count = Column(Integer, default=0)
    last_warning_at = Column(DateTime, nullable=True)
    
    # Action History
    action_by = Column(String(36), ForeignKey("admin_users.id"), nullable=True)
    action_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", backref="moderation_record")
    moderator = relationship("AdminUser", backref="moderation_actions")

    def __repr__(self):
        return f"<UserModeration(id={self.id}, user_id={self.user_id}, status={self.status})>"


class AuditLog(Base):
    """
    Model for audit logging of all admin actions

    Tracks all admin/moderator actions for compliance and accountability.
    """
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Who Did It
    admin_id = Column(String(36), ForeignKey("admin_users.id"), nullable=False, index=True)
    
    # What Happened
    action = Column(String(100), nullable=False)  # reviewed_report, suspended_user, updated_content, etc.
    resource_type = Column(String(50), nullable=False)  # report, user, beat, post, etc.
    resource_id = Column(String(36), nullable=False, index=True)
    
    # Details
    details = Column(Text, nullable=True)  # JSON of what changed
    ip_address = Column(String(45), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    admin = relationship("AdminUser", backref="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource={self.resource_type})>"


class PlatformMetrics(Base):
    """
    Model for daily/hourly platform metrics and analytics

    Tracks key metrics like active users, uploads, revenue, etc.
    """
    __tablename__ = "platform_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Time Period
    metric_date = Column(DateTime, nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # daily, hourly, weekly
    
    # User Metrics
    active_users = Column(Integer, default=0)
    new_signups = Column(Integer, default=0)
    user_churn = Column(Integer, default=0)
    
    # Content Metrics
    new_beats = Column(Integer, default=0)
    new_tracks = Column(Integer, default=0)
    new_posts = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    
    # Engagement
    total_purchases = Column(Integer, default=0)
    total_favorites = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    
    # Revenue
    revenue_streams = Column(Float, default=0.0)  # From streaming
    revenue_sales = Column(Float, default=0.0)    # From beat sales
    revenue_tips = Column(Float, default=0.0)     # From tips
    revenue_subscriptions = Column(Float, default=0.0)  # From fan clubs
    platform_fee = Column(Float, default=0.0)
    creator_payout = Column(Float, default=0.0)
    
    # Moderation
    reports_submitted = Column(Integer, default=0)
    reports_reviewed = Column(Integer, default=0)
    content_removed = Column(Integer, default=0)
    users_suspended = Column(Integer, default=0)
    
    # System Health
    server_uptime_percent = Column(Float, default=100.0)
    avg_response_time_ms = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PlatformMetrics(id={self.id}, date={self.metric_date}, type={self.metric_type})>"
