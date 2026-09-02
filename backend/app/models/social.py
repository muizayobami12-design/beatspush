"""
Social Feed Models
Task 7.1: Social Feed

Models for posts, comments, likes, follows, etc.
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, DateTime, Enum, Index, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.database import Base


# ==========================================
# Enums for Post Model
# ==========================================

class PostType(str, enum.Enum):
    """Post types enum - FR-1.1"""
    TEXT = "text"
    TRACK_SHARE = "track_share"
    MEDIA = "media"
    POLL = "poll"
    EVENT = "event"
    MILESTONE = "milestone"


class PostVisibility(str, enum.Enum):
    """Post visibility enum - FR-7.2"""
    PUBLIC = "public"          # Everyone can see
    FOLLOWERS = "followers"    # Only followers
    PRIVATE = "private"        # Only mentioned users


class ShareType(str, enum.Enum):
    """Share types enum - FR-3.3"""
    REPOST = "repost"      # Share to own feed
    DM = "dm"              # Share via direct message
    EXTERNAL = "external"  # Share to external platform


class ReportReason(str, enum.Enum):
    """Report reason enum - FR-3.5, FR-7.1"""
    SPAM = "spam"
    HARASSMENT = "harassment"
    EXPLICIT_CONTENT = "explicit_content"
    COPYRIGHT = "copyright"
    MISINFORMATION = "misinformation"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    """Report status enum - FR-7.1"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    ACTIONED = "actioned"
    DISMISSED = "dismissed"


class Post(Base):
    """Post model for social feed
    
    Implements FR-1.1, FR-4.1, FR-7.2
    """
    __tablename__ = "posts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(PostType), name='post_type', nullable=False, default=PostType.TEXT)  # Map to post_type column
    content = Column(Text, nullable=True)  # Text content, markdown supported
    
    # Media & attachments
    media_urls = Column(JSON, nullable=True)  # List of media URLs
    track_id = Column(String(36), ForeignKey("tracks.id", ondelete="SET NULL"), nullable=True)
    
    # Poll data (for poll posts)
    poll_options = Column(JSON, nullable=True)  # [{"id": "1", "text": "Option 1"}]
    poll_ends_at = Column(String(100), nullable=True)  # ISO timestamp
    
    # Event data (for event posts)
    event_data = Column(JSON, nullable=True)  # {title, date, location, link}
    
    # Visibility & status
    visibility = Column(Enum(PostVisibility), default=PostVisibility.PUBLIC)
    is_pinned = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Engagement counters (denormalized for performance)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(String(100), nullable=False, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String(100), nullable=False, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    edited_at = Column(String(100), nullable=True)  # ISO timestamp (if edited)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    track = relationship("Track", back_populates="posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")
    shares = relationship("PostShare", back_populates="post", cascade="all, delete-orphan")
    saves = relationship("PostSave", back_populates="post", cascade="all, delete-orphan")
    reports = relationship("PostReport", back_populates="post", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_posts_user_created', 'user_id', 'created_at'),
        Index('idx_posts_type_created', 'post_type', 'created_at'),
        Index('idx_posts_visibility', 'visibility', 'is_deleted'),
    )


class PostLike(Base):
    """Post like model
    
    Implements FR-3.1: Like/Unlike functionality
    User can like a post only once (enforced by unique constraint)
    """
    __tablename__ = "post_likes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(String(100), nullable=False, default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    user = relationship("User", back_populates="post_likes")
    post = relationship("Post", back_populates="likes")
    
    # Unique constraint: user can like a post only once
    # Index for efficient querying by post
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),
        Index('idx_post_likes_post', 'post_id', 'created_at'),
    )


class PostComment(Base):
    """Post comment model with threading support (1 level deep) - FR-3.2"""
    __tablename__ = "post_comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    # Threading (1 level deep)
    parent_comment_id = Column(String(36), ForeignKey("post_comments.id", ondelete="CASCADE"), nullable=True)
    
    # Engagement
    like_count = Column(Integer, default=0)
    
    # Status
    is_deleted = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(String(100), nullable=False, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String(100), nullable=False, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    user = relationship("User", back_populates="post_comments")
    post = relationship("Post", back_populates="comments")
    parent_comment = relationship("PostComment", remote_side=[id], backref="replies")
    comment_likes = relationship("PostCommentLike", back_populates="comment", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_post_comments_post', 'post_id', 'created_at'),
        Index('idx_post_comments_user', 'user_id', 'created_at'),
    )


class PostCommentLike(Base):
    """Post comment like model - FR-3.2"""
    __tablename__ = "post_comment_likes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    comment_id = Column(String(36), ForeignKey("post_comments.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    user = relationship("User")
    comment = relationship("PostComment", back_populates="comment_likes")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'comment_id', name='uq_user_comment_like'),
    )


class PostShare(Base):
    """Post share model - FR-3.3"""
    __tablename__ = "post_shares"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    share_type = Column(Enum(ShareType), default=ShareType.REPOST)
    comment = Column(Text, nullable=True)  # Optional comment when sharing
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    post = relationship("Post", back_populates="shares")
    user = relationship("User", back_populates="post_shares")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_post_shares_user', 'user_id', 'created_at'),
        Index('idx_post_shares_post', 'post_id', 'created_at'),
    )


class Follow(Base):
    """Follow relationship model"""
    __tablename__ = "follows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    follower_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], backref="following_relations")
    following = relationship("User", foreign_keys=[following_id], backref="follower_relations")


class PostSave(Base):
    """Post save/bookmark model - FR-3.4"""
    __tablename__ = "post_saves"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    collection_name = Column(String(100), nullable=True)  # Optional collection
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    user = relationship("User", back_populates="post_saves")
    post = relationship("Post", back_populates="saves")
    
    # Unique constraint and indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_user_post_save'),
        Index('idx_post_saves_user', 'user_id', 'created_at'),
    )


class PollVote(Base):
    """Poll vote model - FR-1.4"""
    __tablename__ = "poll_votes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    option_id = Column(String(36), nullable=False)  # References poll_options JSON
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    user = relationship("User")
    post = relationship("Post")
    
    # Unique constraint: one vote per user per poll
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_user_poll_vote'),
    )


class PostReport(Base):
    """Post report model for content moderation - FR-3.5, FR-7.1"""
    __tablename__ = "post_reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    reporter_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Enum(ReportReason), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    reviewed_at = Column(String(100), nullable=True)
    reviewed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    post = relationship("Post", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reporter_user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


# ==========================================
# Task 7.3: Enhanced Follow System Models
# ==========================================

class UserVerification(Base):
    """User verification request model"""
    __tablename__ = "user_verifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    reason = Column(Text, nullable=True)
    social_links = Column(Text, nullable=True)  # JSON string
    
    # Review info
    submitted_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    reviewed_at = Column(String(100), nullable=True)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="verification_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class Notification(Base):
    """Notification model"""
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # new_follower, mutual_follow, verified, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text, nullable=True)  # JSON string with additional data
    
    # Status
    is_read = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    read_at = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", backref="notifications")


class FollowSuggestion(Base):
    """Follow suggestion model"""
    __tablename__ = "follow_suggestions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    suggested_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Suggestion metadata
    reason = Column(String(255), nullable=True)
    suggestion_type = Column(String(50), nullable=True)  # similar, trending, nearby, mutual
    score = Column(Integer, default=0)  # Relevance score (0-100)
    
    # Status
    is_dismissed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    dismissed_at = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="follow_suggestions")
    suggested_user = relationship("User", foreign_keys=[suggested_user_id])


class TrendingCreator(Base):
    """Trending creator cache model"""
    __tablename__ = "trending_creators"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Metrics
    trending_score = Column(Integer, default=0)
    follower_growth_rate = Column(Integer, default=0)  # Percentage
    engagement_rate = Column(Integer, default=0)  # Percentage
    
    # Period
    period_start = Column(String(100), nullable=False)
    period_end = Column(String(100), nullable=False)
    
    # Filters
    genre = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Metadata
    calculated_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    user = relationship("User", backref="trending_periods")


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Preference flags
    new_follower = Column(Boolean, default=True)
    mutual_follow = Column(Boolean, default=True)
    verification_granted = Column(Boolean, default=True)
    follow_suggestion = Column(Boolean, default=True)
    follower_milestone = Column(Boolean, default=True)
    post_like = Column(Boolean, default=True)
    post_comment = Column(Boolean, default=True)
    post_share = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String(100), default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    user = relationship("User", backref="notification_preferences", uselist=False)
