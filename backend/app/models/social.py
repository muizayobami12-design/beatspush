"""
Social Feed Models
Task 7.1: Social Feed

Models for posts, comments, likes, follows, etc.
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base


class Post(Base):
    """Post model for social feed"""
    __tablename__ = "posts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    post_type = Column(String(20), nullable=False)  # status, track_share, event, milestone, poll
    content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    track_id = Column(String(36), ForeignKey("tracks.id"), nullable=True)
    event_date = Column(String(100), nullable=True)  # ISO format
    poll_options = Column(Text, nullable=True)  # JSON string
    poll_ends_at = Column(String(100), nullable=True)  # ISO format
    
    # Engagement counts
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Visibility
    visibility = Column(String(20), default="public")  # public, followers, private
    is_pinned = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String(100), default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    user = relationship("User", backref="posts")
    track = relationship("Track", backref="shared_posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")
    shares = relationship("PostShare", back_populates="post", cascade="all, delete-orphan")
    bookmarks = relationship("PostBookmark", back_populates="post", cascade="all, delete-orphan")


class PostLike(Base):
    """Post like model"""
    __tablename__ = "post_likes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    post = relationship("Post", back_populates="likes")
    user = relationship("User", backref="post_likes")


class PostComment(Base):
    """Post comment model"""
    __tablename__ = "post_comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    parent_comment_id = Column(String(36), ForeignKey("post_comments.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    
    # Engagement
    like_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String(100), default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    is_edited = Column(Boolean, default=False)
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    user = relationship("User", backref="comments")
    parent = relationship("PostComment", remote_side=[id], backref="replies")
    likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")


class CommentLike(Base):
    """Comment like model"""
    __tablename__ = "comment_likes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    comment_id = Column(String(36), ForeignKey("post_comments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    comment = relationship("PostComment", back_populates="likes")
    user = relationship("User", backref="comment_likes")


class PostShare(Base):
    """Post share model"""
    __tablename__ = "post_shares"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    share_type = Column(String(20), nullable=False)  # repost, quote, external
    quote_text = Column(Text, nullable=True)
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    post = relationship("Post", back_populates="shares")
    user = relationship("User", backref="shares")


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


class PostBookmark(Base):
    """Post bookmark model"""
    __tablename__ = "post_bookmarks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    post = relationship("Post", back_populates="bookmarks")
    user = relationship("User", backref="bookmarks")


class PollVote(Base):
    """Poll vote model"""
    __tablename__ = "poll_votes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    option_index = Column(Integer, nullable=False)
    created_at = Column(String(100), default=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    post = relationship("Post", backref="votes")
    user = relationship("User", backref="poll_votes")


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
