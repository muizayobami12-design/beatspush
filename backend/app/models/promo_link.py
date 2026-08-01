"""
Promo Link Models
Task 3.5: Promo Link Generator
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class PromoLink(Base):
    """Smart link for music promotion - one link redirects to all platforms"""
    __tablename__ = "promo_links"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    track_id = Column(String(36), ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Platform links
    spotify_url = Column(String(500))
    apple_music_url = Column(String(500))
    youtube_url = Column(String(500))
    tidal_url = Column(String(500))
    soundcloud_url = Column(String(500))
    audiomack_url = Column(String(500))
    boomplay_url = Column(String(500))
    deezer_url = Column(String(500))
    
    # Branding
    cover_image_url = Column(String(500))
    background_color = Column(String(7), default="#000000")
    text_color = Column(String(7), default="#FFFFFF")
    custom_domain = Column(String(255))
    
    # Analytics
    total_clicks = Column(Integer, default=0)
    unique_clicks = Column(Integer, default=0)
    
    # UTM Parameters
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="promo_links")
    track = relationship("Track", back_populates="promo_links")
    clicks = relationship("LinkClick", back_populates="promo_link", cascade="all, delete-orphan")
    geo_rules = relationship("GeoRule", back_populates="promo_link", cascade="all, delete-orphan")


class LinkClick(Base):
    """Track every click on a promo link"""
    __tablename__ = "link_clicks"
    
    id = Column(String(36), primary_key=True)
    promo_link_id = Column(String(36), ForeignKey("promo_links.id", ondelete="CASCADE"), nullable=False)
    
    # Platform clicked
    platform = Column(String(50), nullable=False, index=True)
    
    # Visitor info
    ip_address = Column(String(45))
    user_agent = Column(Text)
    referrer = Column(String(500))
    
    # Location
    country = Column(String(100), index=True)
    region = Column(String(100))
    city = Column(String(100))
    
    # Device info
    device_type = Column(String(50))
    os = Column(String(100))
    browser = Column(String(100))
    
    # UTM Parameters
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    utm_term = Column(String(100))
    utm_content = Column(String(100))
    
    # Session tracking
    session_id = Column(String(100), index=True)
    is_unique_click = Column(Boolean, default=True)
    
    # Timestamp
    clicked_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    promo_link = relationship("PromoLink", back_populates="clicks")


class GeoRule(Base):
    """Geo-targeted redirect rules for promo links"""
    __tablename__ = "geo_rules"
    
    id = Column(String(36), primary_key=True)
    promo_link_id = Column(String(36), ForeignKey("promo_links.id", ondelete="CASCADE"), nullable=False)
    
    # Geographic targeting (comma-separated country codes)
    country_codes = Column(Text)
    
    # Platform priority for this region
    platform = Column(String(50), nullable=False)
    priority = Column(Integer, default=0)
    
    # Fallback URL
    fallback_url = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    promo_link = relationship("PromoLink", back_populates="geo_rules")
