"""add_social_feed_system

Revision ID: a2d4fc4303db
Revises: 20d24779a3f3
Create Date: 2026-08-15 09:40:21.899542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2d4fc4303db'
down_revision: Union[str, Sequence[str], None] = '20d24779a3f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add Social Feed System tables."""
    
    # Check if posts table exists and add missing columns
    # The posts table might already exist but be missing columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'posts' in inspector.get_table_names():
        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns('posts')]
        
        # Add post_type column if it doesn't exist (model uses 'post_type' as the actual column name)
        if 'post_type' not in existing_columns:
            op.add_column('posts', sa.Column('post_type', sa.String(50), nullable=True))
        
        # Handle media columns - migrate from media_url to media_urls
        if 'media_url' in existing_columns and 'media_urls' not in existing_columns:
            op.add_column('posts', sa.Column('media_urls', sa.JSON(), nullable=True))
            # Copy single media_url to media_urls as JSON array
            op.execute("UPDATE posts SET media_urls = json_array(media_url) WHERE media_url IS NOT NULL")
        elif 'media_urls' not in existing_columns:
            op.add_column('posts', sa.Column('media_urls', sa.JSON(), nullable=True))
        
        # Add other missing columns
        if 'track_id' not in existing_columns:
            op.add_column('posts', sa.Column('track_id', sa.String(36), nullable=True))
        if 'poll_options' not in existing_columns:
            op.add_column('posts', sa.Column('poll_options', sa.JSON(), nullable=True))
        if 'poll_ends_at' not in existing_columns:
            op.add_column('posts', sa.Column('poll_ends_at', sa.String(100), nullable=True))
        
        # Handle event columns - migrate from event_date to event_data
        if 'event_date' in existing_columns and 'event_data' not in existing_columns:
            op.add_column('posts', sa.Column('event_data', sa.JSON(), nullable=True))
            # Migrate event_date to event_data JSON
            op.execute("UPDATE posts SET event_data = json_object('date', event_date) WHERE event_date IS NOT NULL")
        elif 'event_data' not in existing_columns:
            op.add_column('posts', sa.Column('event_data', sa.JSON(), nullable=True))
        
        if 'visibility' not in existing_columns:
            op.add_column('posts', sa.Column('visibility', sa.String(50), nullable=True))
        if 'is_pinned' not in existing_columns:
            op.add_column('posts', sa.Column('is_pinned', sa.Boolean(), default=False))
        if 'is_deleted' not in existing_columns:
            op.add_column('posts', sa.Column('is_deleted', sa.Boolean(), default=False))
        if 'like_count' not in existing_columns:
            op.add_column('posts', sa.Column('like_count', sa.Integer(), default=0))
        if 'comment_count' not in existing_columns:
            op.add_column('posts', sa.Column('comment_count', sa.Integer(), default=0))
        if 'share_count' not in existing_columns:
            op.add_column('posts', sa.Column('share_count', sa.Integer(), default=0))
        if 'view_count' not in existing_columns:
            op.add_column('posts', sa.Column('view_count', sa.Integer(), default=0))
        if 'edited_at' not in existing_columns:
            op.add_column('posts', sa.Column('edited_at', sa.String(100), nullable=True))
    else:
        # Create posts table from scratch
        op.create_table(
            'posts',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('post_type', sa.String(50), nullable=False),  # Column name is post_type, not type
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('media_urls', sa.JSON(), nullable=True),
            sa.Column('track_id', sa.String(36), sa.ForeignKey('tracks.id', ondelete='SET NULL'), nullable=True),
            sa.Column('poll_options', sa.JSON(), nullable=True),
            sa.Column('poll_ends_at', sa.String(100), nullable=True),
            sa.Column('event_data', sa.JSON(), nullable=True),
            sa.Column('visibility', sa.String(50), default='public'),
            sa.Column('is_pinned', sa.Boolean(), default=False),
            sa.Column('is_deleted', sa.Boolean(), default=False),
            sa.Column('like_count', sa.Integer(), default=0),
            sa.Column('comment_count', sa.Integer(), default=0),
            sa.Column('share_count', sa.Integer(), default=0),
            sa.Column('view_count', sa.Integer(), default=0),
            sa.Column('created_at', sa.String(100), nullable=False),
            sa.Column('updated_at', sa.String(100), nullable=False),
            sa.Column('edited_at', sa.String(100), nullable=True),
        )
    
    # Create indexes for posts table
    try:
        op.create_index('idx_posts_user_created', 'posts', ['user_id', 'created_at'])
    except:
        pass  # Index might already exist
    try:
        op.create_index('idx_posts_type_created', 'posts', ['post_type', 'created_at'])  # Column name is post_type
    except:
        pass
    try:
        op.create_index('idx_posts_visibility', 'posts', ['visibility', 'is_deleted'])
    except:
        pass
    
    # Create post_likes table
    if 'post_likes' not in inspector.get_table_names():
        op.create_table(
            'post_likes',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('post_id', sa.String(36), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.String(100), nullable=False),
        )
        op.create_index('idx_post_likes_post', 'post_likes', ['post_id', 'created_at'])
    
    # Create post_comments table
    if 'post_comments' not in inspector.get_table_names():
        op.create_table(
            'post_comments',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('post_id', sa.String(36), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('parent_comment_id', sa.String(36), sa.ForeignKey('post_comments.id', ondelete='CASCADE'), nullable=True),
            sa.Column('like_count', sa.Integer(), default=0),
            sa.Column('is_deleted', sa.Boolean(), default=False),
            sa.Column('is_edited', sa.Boolean(), default=False),
            sa.Column('created_at', sa.String(100), nullable=False),
            sa.Column('updated_at', sa.String(100), nullable=False),
        )
        op.create_index('idx_post_comments_post', 'post_comments', ['post_id', 'created_at'])
        op.create_index('idx_post_comments_user', 'post_comments', ['user_id', 'created_at'])
    
    # Create post_comment_likes table
    if 'post_comment_likes' not in inspector.get_table_names():
        op.create_table(
            'post_comment_likes',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('comment_id', sa.String(36), sa.ForeignKey('post_comments.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.String(100), nullable=False),
        )
    
    # Create post_shares table
    if 'post_shares' not in inspector.get_table_names():
        op.create_table(
            'post_shares',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('post_id', sa.String(36), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('share_type', sa.String(50), default='repost'),
            sa.Column('comment', sa.Text(), nullable=True),
            sa.Column('created_at', sa.String(100), nullable=False),
        )
        op.create_index('idx_post_shares_user', 'post_shares', ['user_id', 'created_at'])
        op.create_index('idx_post_shares_post', 'post_shares', ['post_id', 'created_at'])
    
    # Create follows table
    if 'follows' not in inspector.get_table_names():
        op.create_table(
            'follows',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('follower_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('following_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.String(100), nullable=False),
        )
    
    # Create post_saves table
    if 'post_saves' not in inspector.get_table_names():
        op.create_table(
            'post_saves',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('post_id', sa.String(36), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('collection_name', sa.String(100), nullable=True),
            sa.Column('created_at', sa.String(100), nullable=False),
        )
        op.create_index('idx_post_saves_user', 'post_saves', ['user_id', 'created_at'])
    
    # Create poll_votes table
    if 'poll_votes' not in inspector.get_table_names():
        op.create_table(
            'poll_votes',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('post_id', sa.String(36), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('option_id', sa.String(36), nullable=False),
            sa.Column('created_at', sa.String(100), nullable=False),
        )
    
    # Create post_reports table
    if 'post_reports' not in inspector.get_table_names():
        op.create_table(
            'post_reports',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('post_id', sa.String(36), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('reporter_user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('reason', sa.String(50), nullable=False),
            sa.Column('details', sa.Text(), nullable=True),
            sa.Column('status', sa.String(50), default='pending'),
            sa.Column('created_at', sa.String(100), nullable=False),
            sa.Column('reviewed_at', sa.String(100), nullable=True),
            sa.Column('reviewed_by', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        )
    
    # Create additional social tables
    if 'user_verifications' not in inspector.get_table_names():
        op.create_table(
            'user_verifications',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('status', sa.String(50), default='pending'),
            sa.Column('reason', sa.Text(), nullable=True),
            sa.Column('social_links', sa.Text(), nullable=True),
            sa.Column('submitted_at', sa.String(100), nullable=False),
            sa.Column('reviewed_at', sa.String(100), nullable=True),
            sa.Column('reviewed_by', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('rejection_reason', sa.Text(), nullable=True),
        )
    
    if 'notifications' not in inspector.get_table_names():
        op.create_table(
            'notifications',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('type', sa.String(50), nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('data', sa.Text(), nullable=True),
            sa.Column('is_read', sa.Boolean(), default=False),
            sa.Column('created_at', sa.String(100), nullable=False),
            sa.Column('read_at', sa.String(100), nullable=True),
        )
    
    if 'follow_suggestions' not in inspector.get_table_names():
        op.create_table(
            'follow_suggestions',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('suggested_user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('reason', sa.String(255), nullable=True),
            sa.Column('suggestion_type', sa.String(50), nullable=True),
            sa.Column('score', sa.Integer(), default=0),
            sa.Column('is_dismissed', sa.Boolean(), default=False),
            sa.Column('created_at', sa.String(100), nullable=False),
            sa.Column('dismissed_at', sa.String(100), nullable=True),
        )
    
    if 'trending_creators' not in inspector.get_table_names():
        op.create_table(
            'trending_creators',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('trending_score', sa.Integer(), default=0),
            sa.Column('follower_growth_rate', sa.Integer(), default=0),
            sa.Column('engagement_rate', sa.Integer(), default=0),
            sa.Column('period_start', sa.String(100), nullable=False),
            sa.Column('period_end', sa.String(100), nullable=False),
            sa.Column('genre', sa.String(100), nullable=True),
            sa.Column('location', sa.String(100), nullable=True),
            sa.Column('calculated_at', sa.String(100), nullable=False),
        )
    
    if 'notification_preferences' not in inspector.get_table_names():
        op.create_table(
            'notification_preferences',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
            sa.Column('new_follower', sa.Boolean(), default=True),
            sa.Column('mutual_follow', sa.Boolean(), default=True),
            sa.Column('verification_granted', sa.Boolean(), default=True),
            sa.Column('follow_suggestion', sa.Boolean(), default=True),
            sa.Column('follower_milestone', sa.Boolean(), default=True),
            sa.Column('post_like', sa.Boolean(), default=True),
            sa.Column('post_comment', sa.Boolean(), default=True),
            sa.Column('post_share', sa.Boolean(), default=True),
            sa.Column('created_at', sa.String(100), nullable=False),
            sa.Column('updated_at', sa.String(100), nullable=False),
        )


def downgrade() -> None:
    """Downgrade schema - Remove Social Feed System tables."""
    
    # Drop tables in reverse order (respecting foreign keys)
    try:
        op.drop_table('notification_preferences')
    except:
        pass
    try:
        op.drop_table('trending_creators')
    except:
        pass
    try:
        op.drop_table('follow_suggestions')
    except:
        pass
    try:
        op.drop_table('notifications')
    except:
        pass
    try:
        op.drop_table('user_verifications')
    except:
        pass
    try:
        op.drop_table('post_reports')
    except:
        pass
    try:
        op.drop_table('poll_votes')
    except:
        pass
    try:
        op.drop_table('post_saves')
    except:
        pass
    try:
        op.drop_table('follows')
    except:
        pass
    try:
        op.drop_table('post_shares')
    except:
        pass
    try:
        op.drop_table('post_comment_likes')
    except:
        pass
    try:
        op.drop_table('post_comments')
    except:
        pass
    try:
        op.drop_table('post_likes')
    except:
        pass
    
    # SQLite doesn't support dropping columns directly, and posts table has complex indexes
    # Instead of trying to drop columns, we'll just drop and recreate the posts table
    # if it exists in the state this migration created it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'posts' in inspector.get_table_names():
        # Drop indexes first
        try:
            op.drop_index('idx_posts_visibility')
        except:
            pass
        try:
            op.drop_index('idx_posts_type_created')
        except:
            pass
        try:
            op.drop_index('idx_posts_user_created')
        except:
            pass
        
        # For a complete rollback, we would need to know the original posts table structure
        # Since this is complex and SQLite doesn't support ALTER COLUMN well,
        # we'll leave the posts table as-is for safety (preserving any existing data)
        # In production, you would handle this more carefully based on your needs
