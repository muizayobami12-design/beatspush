"""Add Live Streaming System tables

Revision ID: 007
Revises: 006
Create Date: 2026-09-01 10:00:00.000000

This migration creates all tables for the Live Streaming System:
- live_streams: Stream sessions with metadata
- stream_chat: Real-time chat messages during streams
- stream_tips: Tips/donations received during streams

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '007'
down_revision: Union[str, Sequence[str], None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create live streaming system tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # 1. Create live_streams table
    if 'live_streams' not in existing_tables:
        op.create_table(
            'live_streams',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('streamer_id', sa.String(length=36), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('category', sa.String(length=100), nullable=True),
            sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
            sa.Column('twitch_channel_id', sa.String(length=255), nullable=True, unique=True),
            sa.Column('twitch_stream_id', sa.String(length=255), nullable=True),
            sa.Column('stream_key', sa.String(length=255), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True, default='scheduled'),
            sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('duration', sa.Integer(), nullable=True),
            sa.Column('peak_viewers', sa.Integer(), default=0, nullable=True),
            sa.Column('total_views', sa.Integer(), default=0, nullable=True),
            sa.Column('total_tips', sa.Float(), default=0.0, nullable=True),
            sa.Column('messages_count', sa.Integer(), default=0, nullable=True),
            sa.Column('is_public', sa.Boolean(), default=True, nullable=True),
            sa.Column('allow_tips', sa.Boolean(), default=True, nullable=True),
            sa.Column('allow_chat', sa.Boolean(), default=True, nullable=True),
            sa.Column('moderators', sa.JSON(), nullable=True),
            sa.Column('is_recorded', sa.Boolean(), default=True, nullable=True),
            sa.Column('recording_url', sa.String(length=500), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['streamer_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_live_streams_streamer_id', 'live_streams', ['streamer_id'])
        op.create_index('ix_live_streams_status', 'live_streams', ['status'])
        op.create_index('ix_live_streams_created_at', 'live_streams', ['created_at'])
        op.create_index('ix_live_streams_twitch_channel_id', 'live_streams', ['twitch_channel_id'])
    
    # 2. Create stream_chat table
    if 'stream_chat' not in existing_tables:
        op.create_table(
            'stream_chat',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('stream_id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('message_type', sa.String(length=50), nullable=True),
            sa.Column('is_moderator', sa.Boolean(), default=False, nullable=True),
            sa.Column('is_pinned', sa.Boolean(), default=False, nullable=True),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.ForeignKeyConstraint(['stream_id'], ['live_streams.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_stream_chat_stream_id', 'stream_chat', ['stream_id'])
        op.create_index('ix_stream_chat_created_at', 'stream_chat', ['created_at'])
    
    # 3. Create stream_tips table
    if 'stream_tips' not in existing_tables:
        op.create_table(
            'stream_tips',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('stream_id', sa.String(length=36), nullable=False),
            sa.Column('tipper_id', sa.String(length=36), nullable=False),
            sa.Column('streamer_id', sa.String(length=36), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('currency', sa.String(length=10), default='NGN', nullable=True),
            sa.Column('message', sa.Text(), nullable=True),
            sa.Column('transaction_id', sa.String(length=255), nullable=True, unique=True),
            sa.Column('status', sa.String(length=50), default='completed', nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.ForeignKeyConstraint(['stream_id'], ['live_streams.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['tipper_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['streamer_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_stream_tips_stream_id', 'stream_tips', ['stream_id'])
        op.create_index('ix_stream_tips_tipper_id', 'stream_tips', ['tipper_id'])
        op.create_index('ix_stream_tips_streamer_id', 'stream_tips', ['streamer_id'])
        op.create_index('ix_stream_tips_created_at', 'stream_tips', ['created_at'])


def downgrade() -> None:
    """Drop live streaming system tables."""
    op.drop_index('ix_stream_tips_created_at', table_name='stream_tips')
    op.drop_index('ix_stream_tips_streamer_id', table_name='stream_tips')
    op.drop_index('ix_stream_tips_tipper_id', table_name='stream_tips')
    op.drop_index('ix_stream_tips_stream_id', table_name='stream_tips')
    op.drop_table('stream_tips')
    
    op.drop_index('ix_stream_chat_created_at', table_name='stream_chat')
    op.drop_index('ix_stream_chat_stream_id', table_name='stream_chat')
    op.drop_table('stream_chat')
    
    op.drop_index('ix_live_streams_twitch_channel_id', table_name='live_streams')
    op.drop_index('ix_live_streams_created_at', table_name='live_streams')
    op.drop_index('ix_live_streams_status', table_name='live_streams')
    op.drop_index('ix_live_streams_streamer_id', table_name='live_streams')
    op.drop_table('live_streams')
