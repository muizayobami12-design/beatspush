"""
Campaign models - Campaign Builder feature (Task 3.2)
"""
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class CampaignStatus(str, enum.Enum):
    """Campaign status lifecycle"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Platform(str, enum.Enum):
    """Supported social media platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class ContentType(str, enum.Enum):
    """Content type per platform"""
    INSTAGRAM_FEED = "instagram_feed"
    INSTAGRAM_STORY = "instagram_story"
    INSTAGRAM_REEL = "instagram_reel"
    TIKTOK_VIDEO = "tiktok_video"
    TWITTER_TWEET = "twitter_tweet"
    TWITTER_THREAD = "twitter_thread"
    FACEBOOK_POST = "facebook_post"
    FACEBOOK_STORY = "facebook_story"


class Campaign(Base):
    """Campaign model - promotional campaigns for tracks"""
    __tablename__ = "campaigns"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    track_id = Column(String(36), ForeignKey("tracks.id"), nullable=False, index=True)
    template_id = Column(String(36), ForeignKey("campaign_templates.id"), nullable=True)
    
    # Campaign details
    name = Column(String(255), nullable=False)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False, index=True)
    
    # Platform selections (JSON array of platform names)
    platforms = Column(JSON, nullable=False)  # ["instagram", "tiktok", "twitter", "facebook"]
    
    # Scheduling
    scheduled_publish_time = Column(DateTime(timezone=True), nullable=True, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Performance metrics (placeholders for Task 3.3)
    engagement_count = Column(Integer, default=0)
    reach_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="campaigns")
    track = relationship("Track", backref="campaigns")
    template = relationship("CampaignTemplate", backref="campaigns")
    content = relationship("CampaignContent", back_populates="campaign", cascade="all, delete-orphan")
    activity_logs = relationship("CampaignActivityLog", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Campaign {self.name} ({self.status})>"


class CampaignContent(Base):
    """Platform-specific campaign content"""
    __tablename__ = "campaign_content"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Foreign key
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Platform info
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    
    # Content data
    caption = Column(Text, nullable=True)  # Main text content
    hashtags = Column(JSON, nullable=True)  # Array of hashtags
    
    # Platform-specific fields (JSON for flexibility)
    platform_specific_data = Column(JSON, nullable=True)  # e.g., {"video_idea": "...", "thread_parts": [...]}
    
    # AI generation tracking
    ai_generated_caption = Column(Text, nullable=True)  # Original AI-generated caption
    caption_tone = Column(String(50), nullable=True)  # Tone used (e.g., "hype", "emotional")
    content_edited = Column(Boolean, default=False)  # Has user edited content?
    
    # Posting status (for Task 3.3 integration)
    posting_status = Column(String(50), default="pending")  # pending, posted, failed
    posted_at = Column(DateTime(timezone=True), nullable=True)
    post_url = Column(String(500), nullable=True)  # URL of posted content
    
    # Performance metrics per platform (placeholders)
    engagement_count = Column(Integer, default=0)
    reach_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Timestamps
    content_generated_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    campaign = relationship("Campaign", back_populates="content")
    
    def __repr__(self):
        return f"<CampaignContent {self.platform} for campaign {self.campaign_id}>"


class CampaignTemplate(Base):
    """Campaign template definitions"""
    __tablename__ = "campaign_templates"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Template info
    name = Column(String(100), nullable=False, unique=True)  # "New Release", "Pre-Release Teaser", etc.
    slug = Column(String(100), nullable=False, unique=True, index=True)  # "new-release", "pre-release-teaser"
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)  # Icon name for UI
    
    # AI prompt modifications (JSON)
    prompt_strategy = Column(JSON, nullable=False)  # Strategy for AI generation
    # Example: {
    #   "tone_emphasis": "excitement",
    #   "keywords": ["new", "available now", "streaming"],
    #   "call_to_action": "Listen now"
    # }
    
    # Recommended platforms
    recommended_platforms = Column(JSON, nullable=True)  # ["instagram", "tiktok"]
    
    # Usage stats
    usage_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<CampaignTemplate {self.name}>"



class CampaignActivityLog(Base):
    """Campaign activity audit log"""
    __tablename__ = "campaign_activity_log"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Foreign keys
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Activity details
    action = Column(String(100), nullable=False)  # "created", "status_changed", "edited", "deleted", etc.
    details = Column(JSON, nullable=True)  # Action-specific details
    # Example: {"old_status": "draft", "new_status": "scheduled"}
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="activity_logs")
    user = relationship("User")
    
    def __repr__(self):
        return f"<CampaignActivityLog {self.action} on campaign {self.campaign_id}>"
