"""Add recommendation engine tables and indexes

Revision ID: 004
Revises: 003
Create Date: 2026-01-14 00:00:00.000000

This migration creates all tables and indexes for the recommendation engine:
- user_preference_profiles: Aggregated user preference profiles
- beat_similarity_cache: Pre-computed beat similarity scores
- trending_beat_cache: Cached trending beats by genre/region
- recommendation_logs: Analytics and logging for recommendations

Also adds performance indexes on existing tables:
- beat_plays: composite indexes for CF queries and time-window queries
- beat_favorites: composite indexes for CF queries
- beat_purchases: composite indexes for CF queries and trending calculations

Requirements: 8.2, 8.4, 11.3, 14.1, 14.2
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, Sequence[str], None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create recommendation engine tables and add indexes."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # ========================================
    # Create new recommendation engine tables
    # ========================================
    
    # Create user_preference_profiles table
    if 'user_preference_profiles' not in existing_tables:
        op.create_table(
            'user_preference_profiles',
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('genre_weights', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=True),
            sa.Column('bpm_range', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=True),
            sa.Column('key_preferences', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=True),
            sa.Column('mood_preferences', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=True),
            sa.Column('total_plays', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('total_favorites', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('total_purchases', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('interaction_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('region', sa.String(length=2), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('user_id'),
            sa.CheckConstraint('length(region) = 2 OR region IS NULL', name='check_region_iso_code'),
            sa.CheckConstraint('total_plays >= 0', name='check_total_plays_non_negative'),
            sa.CheckConstraint('total_favorites >= 0', name='check_total_favorites_non_negative'),
            sa.CheckConstraint('total_purchases >= 0', name='check_total_purchases_non_negative'),
            sa.CheckConstraint('interaction_count >= 0', name='check_interaction_count_non_negative')
        )
        op.create_index('ix_user_preference_profiles_user_id', 'user_preference_profiles', ['user_id'])
        op.create_index('ix_user_preference_profiles_region', 'user_preference_profiles', ['region'])
        op.create_index('ix_user_preference_profiles_updated_at', 'user_preference_profiles', ['updated_at'])
    
    # Create beat_similarity_cache table
    if 'beat_similarity_cache' not in existing_tables:
        op.create_table(
            'beat_similarity_cache',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('source_beat_id', sa.String(length=36), nullable=False),
            sa.Column('similar_beat_ids', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=False),
            sa.Column('algorithm', sa.String(length=20), nullable=False),
            sa.Column('hit_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.CheckConstraint("algorithm IN ('content', 'collaborative', 'hybrid')", name='check_algorithm_type'),
            sa.CheckConstraint('hit_count >= 0', name='check_hit_count_non_negative'),
            sa.CheckConstraint('expires_at > created_at', name='check_expires_after_created')
        )
        op.create_index('ix_beat_similarity_cache_source_beat_id', 'beat_similarity_cache', ['source_beat_id'])
        op.create_index('ix_beat_similarity_cache_created_at', 'beat_similarity_cache', ['created_at'])
        op.create_index('ix_beat_similarity_cache_expires_at', 'beat_similarity_cache', ['expires_at'])
        op.create_index('idx_beat_similarity_source_algo', 'beat_similarity_cache', ['source_beat_id', 'algorithm'])
    
    # Create trending_beat_cache table
    if 'trending_beat_cache' not in existing_tables:
        op.create_table(
            'trending_beat_cache',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('genre', sa.String(length=100), nullable=True),
            sa.Column('region', sa.String(length=2), nullable=True),
            sa.Column('beat_ids', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=False),
            sa.Column('window_start', sa.DateTime(), nullable=False),
            sa.Column('window_end', sa.DateTime(), nullable=False),
            sa.Column('hit_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.CheckConstraint('length(region) = 2 OR region IS NULL', name='check_trending_region_iso_code'),
            sa.CheckConstraint('hit_count >= 0', name='check_trending_hit_count_non_negative'),
            sa.CheckConstraint('window_end > window_start', name='check_window_end_after_start'),
            sa.CheckConstraint('expires_at > created_at', name='check_trending_expires_after_created')
        )
        op.create_index('ix_trending_beat_cache_genre', 'trending_beat_cache', ['genre'])
        op.create_index('ix_trending_beat_cache_region', 'trending_beat_cache', ['region'])
        op.create_index('ix_trending_beat_cache_created_at', 'trending_beat_cache', ['created_at'])
        op.create_index('ix_trending_beat_cache_expires_at', 'trending_beat_cache', ['expires_at'])
        op.create_index('idx_trending_genre_region', 'trending_beat_cache', ['genre', 'region'])
    
    # Create recommendation_logs table
    if 'recommendation_logs' not in existing_tables:
        op.create_table(
            'recommendation_logs',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=True),
            sa.Column('session_id', sa.String(length=36), nullable=True),
            sa.Column('recommendation_type', sa.String(length=50), nullable=False),
            sa.Column('request_params', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=True),
            sa.Column('response_time_ms', sa.Integer(), nullable=False),
            sa.Column('cache_hit', sa.Boolean(), nullable=False, server_default='0'),
            sa.Column('algorithm_used', sa.String(length=50), nullable=True),
            sa.Column('beat_ids', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=False),
            sa.Column('recommendation_count', sa.Integer(), nullable=False),
            sa.Column('clicked_beat_ids', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=True),
            sa.Column('purchased_beat_ids', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=True),
            sa.Column('click_through_rate', sa.Float(), nullable=True),
            sa.Column('conversion_rate', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('last_engagement_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.CheckConstraint('response_time_ms >= 0', name='check_response_time_non_negative'),
            sa.CheckConstraint('recommendation_count >= 0', name='check_recommendation_count_non_negative'),
            sa.CheckConstraint(
                'click_through_rate IS NULL OR (click_through_rate >= 0.0 AND click_through_rate <= 1.0)',
                name='check_ctr_range'
            ),
            sa.CheckConstraint(
                'conversion_rate IS NULL OR (conversion_rate >= 0.0 AND conversion_rate <= 1.0)',
                name='check_conversion_rate_range'
            ),
            sa.CheckConstraint(
                "recommendation_type IN ('personalized_beats', 'similar_beats', 'trending', "
                "'discover_feed', 'also_bought', 'artist_suggestions', 'anonymous')",
                name='check_recommendation_type'
            )
        )
        op.create_index('ix_recommendation_logs_user_id', 'recommendation_logs', ['user_id'])
        op.create_index('ix_recommendation_logs_recommendation_type', 'recommendation_logs', ['recommendation_type'])
        op.create_index('ix_recommendation_logs_created_at', 'recommendation_logs', ['created_at'])
        op.create_index('idx_recommendation_user_type', 'recommendation_logs', ['user_id', 'recommendation_type'])
    
    # ========================================
    # Add indexes on existing behavior tables
    # ========================================
    
    # Get existing indexes to avoid duplicates
    existing_indexes = set()
    if 'beat_plays' in existing_tables:
        for index in inspector.get_indexes('beat_plays'):
            existing_indexes.add(index['name'])
    if 'beat_favorites' in existing_tables:
        for index in inspector.get_indexes('beat_favorites'):
            existing_indexes.add(index['name'])
    if 'beat_purchases' in existing_tables:
        for index in inspector.get_indexes('beat_purchases'):
            existing_indexes.add(index['name'])
    
    # Beat plays indexes for collaborative filtering and trending
    if 'beat_plays' in existing_tables:
        # Composite index for collaborative filtering (user-beat interactions)
        if 'idx_beat_plays_beat_user' not in existing_indexes:
            op.create_index('idx_beat_plays_beat_user', 'beat_plays', ['beat_id', 'user_id'])
        
        # Composite index for user's recent plays (with time filtering)
        if 'idx_beat_plays_user_created' not in existing_indexes:
            op.create_index('idx_beat_plays_user_created', 'beat_plays', ['user_id', 'created_at'])
        
        # Composite index for trending calculations (time-window queries)
        if 'idx_beat_plays_beat_created' not in existing_indexes:
            op.create_index('idx_beat_plays_beat_created', 'beat_plays', ['beat_id', 'created_at'])
        
        # Index for completed plays (quality metrics)
        if 'idx_beat_plays_completed' not in existing_indexes:
            op.create_index('idx_beat_plays_completed', 'beat_plays', ['completed', 'beat_id'])
    
    # Beat favorites indexes for collaborative filtering
    if 'beat_favorites' in existing_tables:
        # Composite index for collaborative filtering (user-beat interactions)
        if 'idx_beat_favorites_beat_user' not in existing_indexes:
            op.create_index('idx_beat_favorites_beat_user', 'beat_favorites', ['beat_id', 'user_id'])
        
        # Composite index for user's favorites with time ordering
        if 'idx_beat_favorites_user_created' not in existing_indexes:
            op.create_index('idx_beat_favorites_user_created', 'beat_favorites', ['user_id', 'created_at'])
        
        # Composite index for trending calculations (time-window queries)
        if 'idx_beat_favorites_beat_created' not in existing_indexes:
            op.create_index('idx_beat_favorites_beat_created', 'beat_favorites', ['beat_id', 'created_at'])
    
    # Beat purchases indexes for collaborative filtering and trending
    if 'beat_purchases' in existing_tables:
        # Composite index for "also-bought" recommendations
        if 'idx_beat_purchases_beat_buyer' not in existing_indexes:
            op.create_index('idx_beat_purchases_beat_buyer', 'beat_purchases', ['beat_id', 'buyer_user_id'])
        
        # Composite index for buyer's purchase history with time ordering
        if 'idx_beat_purchases_buyer_created' not in existing_indexes:
            op.create_index('idx_beat_purchases_buyer_created', 'beat_purchases', ['buyer_user_id', 'created_at'])
        
        # Composite index for trending calculations (time-window queries)
        if 'idx_beat_purchases_beat_created' not in existing_indexes:
            op.create_index('idx_beat_purchases_beat_created', 'beat_purchases', ['beat_id', 'created_at'])
        
        # Index for purchase status filtering (completed purchases only)
        if 'idx_beat_purchases_status' not in existing_indexes:
            op.create_index('idx_beat_purchases_status', 'beat_purchases', ['status', 'beat_id'])


def downgrade() -> None:
    """Drop recommendation engine tables and indexes."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # ========================================
    # Drop indexes from existing behavior tables
    # ========================================
    
    # Get existing indexes
    existing_indexes = set()
    if 'beat_plays' in existing_tables:
        for index in inspector.get_indexes('beat_plays'):
            existing_indexes.add(index['name'])
    if 'beat_favorites' in existing_tables:
        for index in inspector.get_indexes('beat_favorites'):
            existing_indexes.add(index['name'])
    if 'beat_purchases' in existing_tables:
        for index in inspector.get_indexes('beat_purchases'):
            existing_indexes.add(index['name'])
    
    # Drop beat_purchases indexes
    if 'beat_purchases' in existing_tables:
        if 'idx_beat_purchases_status' in existing_indexes:
            op.drop_index('idx_beat_purchases_status', table_name='beat_purchases')
        if 'idx_beat_purchases_beat_created' in existing_indexes:
            op.drop_index('idx_beat_purchases_beat_created', table_name='beat_purchases')
        if 'idx_beat_purchases_buyer_created' in existing_indexes:
            op.drop_index('idx_beat_purchases_buyer_created', table_name='beat_purchases')
        if 'idx_beat_purchases_beat_buyer' in existing_indexes:
            op.drop_index('idx_beat_purchases_beat_buyer', table_name='beat_purchases')
    
    # Drop beat_favorites indexes
    if 'beat_favorites' in existing_tables:
        if 'idx_beat_favorites_beat_created' in existing_indexes:
            op.drop_index('idx_beat_favorites_beat_created', table_name='beat_favorites')
        if 'idx_beat_favorites_user_created' in existing_indexes:
            op.drop_index('idx_beat_favorites_user_created', table_name='beat_favorites')
        if 'idx_beat_favorites_beat_user' in existing_indexes:
            op.drop_index('idx_beat_favorites_beat_user', table_name='beat_favorites')
    
    # Drop beat_plays indexes
    if 'beat_plays' in existing_tables:
        if 'idx_beat_plays_completed' in existing_indexes:
            op.drop_index('idx_beat_plays_completed', table_name='beat_plays')
        if 'idx_beat_plays_beat_created' in existing_indexes:
            op.drop_index('idx_beat_plays_beat_created', table_name='beat_plays')
        if 'idx_beat_plays_user_created' in existing_indexes:
            op.drop_index('idx_beat_plays_user_created', table_name='beat_plays')
        if 'idx_beat_plays_beat_user' in existing_indexes:
            op.drop_index('idx_beat_plays_beat_user', table_name='beat_plays')
    
    # ========================================
    # Drop recommendation engine tables
    # ========================================
    
    # Drop tables in reverse order (respect foreign keys)
    if 'recommendation_logs' in existing_tables:
        op.drop_index('idx_recommendation_user_type', table_name='recommendation_logs')
        op.drop_index('ix_recommendation_logs_created_at', table_name='recommendation_logs')
        op.drop_index('ix_recommendation_logs_recommendation_type', table_name='recommendation_logs')
        op.drop_index('ix_recommendation_logs_user_id', table_name='recommendation_logs')
        op.drop_table('recommendation_logs')
    
    if 'trending_beat_cache' in existing_tables:
        op.drop_index('idx_trending_genre_region', table_name='trending_beat_cache')
        op.drop_index('ix_trending_beat_cache_expires_at', table_name='trending_beat_cache')
        op.drop_index('ix_trending_beat_cache_created_at', table_name='trending_beat_cache')
        op.drop_index('ix_trending_beat_cache_region', table_name='trending_beat_cache')
        op.drop_index('ix_trending_beat_cache_genre', table_name='trending_beat_cache')
        op.drop_table('trending_beat_cache')
    
    if 'beat_similarity_cache' in existing_tables:
        op.drop_index('idx_beat_similarity_source_algo', table_name='beat_similarity_cache')
        op.drop_index('ix_beat_similarity_cache_expires_at', table_name='beat_similarity_cache')
        op.drop_index('ix_beat_similarity_cache_created_at', table_name='beat_similarity_cache')
        op.drop_index('ix_beat_similarity_cache_source_beat_id', table_name='beat_similarity_cache')
        op.drop_table('beat_similarity_cache')
    
    if 'user_preference_profiles' in existing_tables:
        op.drop_index('ix_user_preference_profiles_updated_at', table_name='user_preference_profiles')
        op.drop_index('ix_user_preference_profiles_region', table_name='user_preference_profiles')
        op.drop_index('ix_user_preference_profiles_user_id', table_name='user_preference_profiles')
        op.drop_table('user_preference_profiles')


def _is_sqlite() -> bool:
    """Check if we're using SQLite."""
    from alembic import context
    return context.get_bind().dialect.name == 'sqlite'
