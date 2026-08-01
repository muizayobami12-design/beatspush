"""
Analytics Models
Task 4.2: Unified Analytics Dashboard

Models for tracking user activity and generating insights
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class UserActivity(Base):
    """Track user activity for analytics"""
    __tablename__ = "user_activity"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False, index=True)  # login, upload, campaign_create, etc.
    activity_data = Column(JSON)  # Additional data about the activity
    
    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", backref="activities")


class DailyStats(Base):
    """Aggregated daily statistics for users"""
    __tablename__ = "daily_stats"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Track stats
    total_tracks = Column(Integer, default=0)
    tracks_uploaded = Column(Integer, default=0)
    
    # Engagement stats
    total_plays = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    
    # Campaign stats
    campaigns_created = Column(Integer, default=0)
    campaigns_active = Column(Integer, default=0)
    
    # Promo link stats
    promo_links_created = Column(Integer, default=0)
    promo_link_clicks = Column(Integer, default=0)
    promo_link_unique_clicks = Column(Integer, default=0)
    
    # Revenue stats (placeholder for future)
    revenue = Column(Float, default=0.0)
    tips_received = Column(Float, default=0.0)
    
    # Calculated at end of day
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="daily_stats")
