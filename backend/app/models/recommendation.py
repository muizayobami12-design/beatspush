"""
Recommendation Engine Models
Task 1.1: Create new database models for recommendation engine

Models for storing user preferences, similarity caches, trending data,
and recommendation logs for the BeatPush recommendation system.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import uuid


class UserPreferenceProfile(Base):
    """
    Aggregated user preference profile for faster recommendations.
    Stores weighted preferences based on user behavior history.
    
    Requirements: 8.2 (Cache Management)
    """
    __tablename__ = "user_preference_profiles"
    
    # Primary key
    user_id = Column(String(36), primary_key=True, index=True)
    
    # Aggregated preferences (JSON fields)
    genre_weights = Column(JSON, nullable=True)  # {"Afrobeats": 0.35, "Hip-Hop": 0.25, ...}
    bpm_range = Column(JSON, nullable=True)  # {"min": 80, "max": 140, "preferred": 120}
    key_preferences = Column(JSON, nullable=True)  # ["C", "G", "D"]
    mood_preferences = Column(JSON, nullable=True)  # {"Energetic": 0.4, "Chill": 0.3, ...}
    
    # Interaction counts for cold start detection
    total_plays = Column(Integer, default=0, nullable=False)
    total_favorites = Column(Integer, default=0, nullable=False)
    total_purchases = Column(Integer, default=0, nullable=False)
    interaction_count = Column(Integer, default=0, nullable=False)
    
    # Regional preference (ISO 3166-1 alpha-2 country codes)
    region = Column(String(2), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('length(region) = 2 OR region IS NULL', name='check_region_iso_code'),
        CheckConstraint('total_plays >= 0', name='check_total_plays_non_negative'),
        CheckConstraint('total_favorites >= 0', name='check_total_favorites_non_negative'),
        CheckConstraint('total_purchases >= 0', name='check_total_purchases_non_negative'),
        CheckConstraint('interaction_count >= 0', name='check_interaction_count_non_negative'),
    )


class BeatSimilarityCache(Base):
    """
    Pre-computed similarity scores for popular beats.
    Caches content-based and collaborative filtering results.
    
    Requirements: 8.2 (Cache Management), 8.4 (Cache warming)
    """
    __tablename__ = "beat_similarity_cache"
    
    # Composite primary key: source_beat_id + algorithm
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_beat_id = Column(String(36), nullable=False, index=True)
    
    # Similar beat IDs with scores: [{"beat_id": "...", "score": 0.85}, ...]
    similar_beat_ids = Column(JSON, nullable=False)
    
    # Algorithm used for similarity calculation
    algorithm = Column(String(20), nullable=False)  # "content", "collaborative", "hybrid"
    
    # Cache metadata
    hit_count = Column(Integer, default=0, nullable=False)  # Track cache usage
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Constraints
    __table_args__ = (
        Index('idx_beat_similarity_source_algo', 'source_beat_id', 'algorithm'),
        CheckConstraint("algorithm IN ('content', 'collaborative', 'hybrid')", name='check_algorithm_type'),
        CheckConstraint('hit_count >= 0', name='check_hit_count_non_negative'),
        CheckConstraint('expires_at > created_at', name='check_expires_after_created'),
    )


class TrendingBeatCache(Base):
    """
    Cached trending beats by genre and region.
    Refreshed every 15 minutes via background job.
    
    Requirements: 8.2 (Cache Management), 8.4 (Cache warming)
    """
    __tablename__ = "trending_beat_cache"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Filtering dimensions
    genre = Column(String(100), nullable=True, index=True)  # NULL = all genres
    region = Column(String(2), nullable=True, index=True)  # NULL = global, or ISO country code
    
    # Beat IDs with trending scores: [{"beat_id": "...", "score": 0.92, "rank": 1}, ...]
    beat_ids = Column(JSON, nullable=False)
    
    # Calculation window
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    
    # Cache metadata
    hit_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Constraints
    __table_args__ = (
        Index('idx_trending_genre_region', 'genre', 'region'),
        CheckConstraint('length(region) = 2 OR region IS NULL', name='check_trending_region_iso_code'),
        CheckConstraint('hit_count >= 0', name='check_trending_hit_count_non_negative'),
        CheckConstraint('window_end > window_start', name='check_window_end_after_start'),
        CheckConstraint('expires_at > created_at', name='check_trending_expires_after_created'),
    )


class RecommendationLog(Base):
    """
    Logging and analytics for recommendations.
    Tracks performance metrics and user engagement with recommendations.
    
    Requirements: 14.1 (Log requests), 14.2 (Track click-through rate)
    """
    __tablename__ = "recommendation_logs"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User context
    user_id = Column(String(36), nullable=True, index=True)  # NULL for anonymous users
    session_id = Column(String(36), nullable=True)  # For anonymous user tracking
    
    # Recommendation context
    recommendation_type = Column(String(50), nullable=False, index=True)
    # Types: "personalized_beats", "similar_beats", "trending", "discover_feed", 
    #        "also_bought", "artist_suggestions", "anonymous"
    
    # Request details (JSON for flexibility)
    request_params = Column(JSON, nullable=True)  # {"genre": "Afrobeats", "limit": 20, ...}
    
    # Performance metrics
    response_time_ms = Column(Integer, nullable=False)
    cache_hit = Column(Boolean, nullable=False, default=False)
    algorithm_used = Column(String(50), nullable=True)  # "cf", "cb", "hybrid", "trending"
    
    # Returned recommendations
    beat_ids = Column(JSON, nullable=False)  # List of beat IDs returned
    recommendation_count = Column(Integer, nullable=False)
    
    # Engagement tracking (updated post-recommendation)
    clicked_beat_ids = Column(JSON, nullable=True, default=list)
    purchased_beat_ids = Column(JSON, nullable=True, default=list)
    click_through_rate = Column(Float, nullable=True)  # 0.0 to 1.0
    conversion_rate = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_engagement_at = Column(DateTime, nullable=True)  # Last click/purchase time
    
    # Constraints
    __table_args__ = (
        Index('idx_recommendation_user_type', 'user_id', 'recommendation_type'),
        Index('idx_recommendation_created', 'created_at'),
        CheckConstraint('response_time_ms >= 0', name='check_response_time_non_negative'),
        CheckConstraint('recommendation_count >= 0', name='check_recommendation_count_non_negative'),
        CheckConstraint(
            'click_through_rate IS NULL OR (click_through_rate >= 0.0 AND click_through_rate <= 1.0)',
            name='check_ctr_range'
        ),
        CheckConstraint(
            'conversion_rate IS NULL OR (conversion_rate >= 0.0 AND conversion_rate <= 1.0)',
            name='check_conversion_rate_range'
        ),
        CheckConstraint(
            "recommendation_type IN ('personalized_beats', 'similar_beats', 'trending', "
            "'discover_feed', 'also_bought', 'artist_suggestions', 'anonymous')",
            name='check_recommendation_type'
        ),
    )
