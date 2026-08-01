"""
User Profile Models - Extended profile information for each user type
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class ArtistProfile(Base):
    """Extended profile for Artists"""
    __tablename__ = "artist_profiles"
    
    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    
    # Basic info
    stage_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    genres = Column(JSON, nullable=True)  # List of genres
    
    # Links
    spotify_url = Column(String(500), nullable=True)
    apple_music_url = Column(String(500), nullable=True)
    soundcloud_url = Column(String(500), nullable=True)
    youtube_url = Column(String(500), nullable=True)
    
    # Social media
    instagram_handle = Column(String(100), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    tiktok_handle = Column(String(100), nullable=True)
    facebook_url = Column(String(500), nullable=True)
    
    # Professional info
    record_label = Column(String(255), nullable=True)
    manager_name = Column(String(255), nullable=True)
    manager_email = Column(String(255), nullable=True)
    
    # Profile media
    avatar_url = Column(String(500), nullable=True)
    cover_photo_url = Column(String(500), nullable=True)
    
    # Stats (to be updated by system)
    total_tracks = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    total_followers = Column(Integer, default=0)
    
    # Relationship
    user = relationship("User", backref="artist_profile", uselist=False)


class DJProfile(Base):
    """Extended profile for DJs"""
    __tablename__ = "dj_profiles"
    
    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    
    # Basic info
    dj_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    genres = Column(JSON, nullable=True)  # List of genres
    bpm_range = Column(String(50), nullable=True)  # e.g., "120-140"
    
    # Professional info
    resident_venues = Column(JSON, nullable=True)  # List of venues
    radio_shows = Column(JSON, nullable=True)  # List of radio shows
    equipment = Column(Text, nullable=True)  # DJ equipment/setup
    
    # Links
    mixcloud_url = Column(String(500), nullable=True)
    soundcloud_url = Column(String(500), nullable=True)
    youtube_url = Column(String(500), nullable=True)
    spotify_url = Column(String(500), nullable=True)
    
    # Social media
    instagram_handle = Column(String(100), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    tiktok_handle = Column(String(100), nullable=True)
    facebook_url = Column(String(500), nullable=True)
    
    # Profile media
    avatar_url = Column(String(500), nullable=True)
    cover_photo_url = Column(String(500), nullable=True)
    
    # Stats
    total_mixes = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    total_followers = Column(Integer, default=0)
    
    # Relationship
    user = relationship("User", backref="dj_profile", uselist=False)


class ProducerProfile(Base):
    """Extended profile for Producers"""
    __tablename__ = "producer_profiles"
    
    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    
    # Basic info
    producer_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    genres = Column(JSON, nullable=True)  # List of genres
    production_style = Column(Text, nullable=True)
    
    # Technical info
    daw = Column(String(100), nullable=True)  # Digital Audio Workstation (Ableton, FL Studio, etc.)
    equipment = Column(Text, nullable=True)  # Hardware, plugins, etc.
    collaboration_preferences = Column(Text, nullable=True)
    
    # Links
    beatstars_url = Column(String(500), nullable=True)
    soundcloud_url = Column(String(500), nullable=True)
    youtube_url = Column(String(500), nullable=True)
    spotify_url = Column(String(500), nullable=True)
    
    # Social media
    instagram_handle = Column(String(100), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    tiktok_handle = Column(String(100), nullable=True)
    facebook_url = Column(String(500), nullable=True)
    
    # Profile media
    avatar_url = Column(String(500), nullable=True)
    cover_photo_url = Column(String(500), nullable=True)
    
    # Stats
    total_beats = Column(Integer, default=0)
    total_sales = Column(Integer, default=0)
    total_collaborations = Column(Integer, default=0)
    total_followers = Column(Integer, default=0)
    
    # Relationship
    user = relationship("User", backref="producer_profile", uselist=False)


class FanProfile(Base):
    """Extended profile for Fans"""
    __tablename__ = "fan_profiles"
    
    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    
    # Basic info
    display_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    favorite_genres = Column(JSON, nullable=True)  # List of genres
    location = Column(String(255), nullable=True)
    
    # Preferences
    favorite_artists = Column(JSON, nullable=True)  # List of artist IDs
    favorite_djs = Column(JSON, nullable=True)  # List of DJ IDs
    favorite_producers = Column(JSON, nullable=True)  # List of producer IDs
    
    # Social media
    instagram_handle = Column(String(100), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    tiktok_handle = Column(String(100), nullable=True)
    
    # Profile media
    avatar_url = Column(String(500), nullable=True)
    cover_photo_url = Column(String(500), nullable=True)
    
    # Stats
    total_playlists = Column(Integer, default=0)
    total_tips_given = Column(Integer, default=0)
    points_balance = Column(Integer, default=0)
    
    # Relationship
    user = relationship("User", backref="fan_profile", uselist=False)
