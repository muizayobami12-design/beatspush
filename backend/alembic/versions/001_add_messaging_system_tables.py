"""Add messaging system tables

Revision ID: 001
Revises: 
Create Date: 2026-01-08 00:00:00.000000

This migration creates all tables for the messaging system:
- conversations: Main conversation threads
- conversation_participants: User participation in conversations
- messages: Individual messages within conversations
- message_read_receipts: Read status tracking
- message_attachments: File attachments for messages
- blocked_users: User blocking for privacy
- message_reports: Message reporting for moderation
- user_message_settings: User privacy settings

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create messaging system tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Create conversations table (only if it doesn't exist)
    if 'conversations' not in existing_tables:
        op.create_table(
            'conversations',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('last_message_preview', sa.Text(), nullable=True),
            sa.Column('is_message_request', sa.Boolean(), default=False, nullable=True),
            sa.Column('request_status', sa.String(length=20), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_conversations_id', 'conversations', ['id'], unique=False)
        op.create_index('idx_conversations_last_activity', 'conversations', ['last_activity_at'], unique=False)
        op.create_index('idx_conversations_request', 'conversations', ['is_message_request', 'request_status'], unique=False)
    
    # Create conversation_participants table (only if it doesn't exist)
    if 'conversation_participants' not in existing_tables:
        op.create_table(
            'conversation_participants',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('conversation_id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('unread_count', sa.Integer(), default=0, nullable=True),
            sa.Column('last_read_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('is_archived', sa.Boolean(), default=False, nullable=True),
            sa.Column('is_muted', sa.Boolean(), default=False, nullable=True),
            sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('conversation_id', 'user_id', name='uq_conversation_user')
        )
        op.create_index('ix_conversation_participants_id', 'conversation_participants', ['id'], unique=False)
        op.create_index('idx_participant_user', 'conversation_participants', ['user_id'], unique=False)
        op.create_index('idx_participant_conversation', 'conversation_participants', ['conversation_id'], unique=False)
        op.create_index('idx_participant_unread', 'conversation_participants', ['user_id', 'unread_count'], unique=False)
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('sender_id', sa.String(length=36), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_edited', sa.Boolean(), default=False, nullable=True),
        sa.Column('language_code', sa.String(length=10), nullable=True),
        sa.Column('spam_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('ai_processed', sa.Boolean(), default=False, nullable=True),
        sa.Column('smart_reply_suggestions', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=True),
        sa.CheckConstraint('length(content) <= 2000', name='ck_message_content_length'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_id', 'messages', ['id'], unique=False)
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'], unique=False)
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'], unique=False)
    op.create_index('ix_messages_created_at', 'messages', ['created_at'], unique=False)
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'], unique=False)
    
    # Create message_read_receipts table
    op.create_table(
        'message_read_receipts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('message_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id', 'user_id', name='uq_message_user_receipt')
    )
    op.create_index('ix_message_read_receipts_id', 'message_read_receipts', ['id'], unique=False)
    op.create_index('idx_receipts_message', 'message_read_receipts', ['message_id'], unique=False)
    op.create_index('idx_receipts_user', 'message_read_receipts', ['user_id'], unique=False)
    
    # Create message_attachments table
    op.create_table(
        'message_attachments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('message_id', sa.String(length=36), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('storage_url', sa.Text(), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.CheckConstraint('file_size > 0', name='ck_attachment_file_size'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_message_attachments_id', 'message_attachments', ['id'], unique=False)
    op.create_index('ix_message_attachments_message_id', 'message_attachments', ['message_id'], unique=False)
    op.create_index('idx_attachments_type', 'message_attachments', ['file_type'], unique=False)
    
    # Create blocked_users table (only if it doesn't exist)
    if 'blocked_users' not in existing_tables:
        op.create_table(
            'blocked_users',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('blocker_id', sa.String(length=36), nullable=False),
            sa.Column('blocked_id', sa.String(length=36), nullable=False),
            sa.Column('blocked_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('reason', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['blocker_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['blocked_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('blocker_id', 'blocked_id', name='uq_blocker_blocked')
        )
        op.create_index('ix_blocked_users_id', 'blocked_users', ['id'], unique=False)
        op.create_index('idx_blocks_blocker', 'blocked_users', ['blocker_id'], unique=False)
        op.create_index('idx_blocks_blocked', 'blocked_users', ['blocked_id'], unique=False)
    
    # Create message_reports table
    op.create_table(
        'message_reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('message_id', sa.String(length=36), nullable=False),
        sa.Column('reporter_id', sa.String(length=36), nullable=False),
        sa.Column('reason', sa.String(length=50), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('reviewed', sa.Boolean(), default=False, nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', sa.String(length=36), nullable=True),
        sa.Column('action_taken', sa.String(length=100), nullable=True),
        sa.CheckConstraint('length(details) <= 500', name='ck_report_details_length'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_message_reports_id', 'message_reports', ['id'], unique=False)
    op.create_index('ix_message_reports_message_id', 'message_reports', ['message_id'], unique=False)
    op.create_index('idx_reports_status', 'message_reports', ['reviewed', 'created_at'], unique=False)
    
    # Create user_message_settings table (only if it doesn't exist)
    if 'user_message_settings' not in existing_tables:
        op.create_table(
            'user_message_settings',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('message_filter', sa.String(length=20), default='everyone', nullable=True),
            sa.Column('read_receipts_enabled', sa.Boolean(), default=True, nullable=True),
            sa.Column('typing_indicators_enabled', sa.Boolean(), default=True, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', name='uq_user_message_settings')
        )
        op.create_index('ix_user_message_settings_id', 'user_message_settings', ['id'], unique=False)
        op.create_index('idx_settings_user', 'user_message_settings', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop messaging system tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Drop tables in reverse order (respect foreign keys)
    if 'user_message_settings' in existing_tables:
        op.drop_index('idx_settings_user', table_name='user_message_settings')
        op.drop_index('ix_user_message_settings_id', table_name='user_message_settings')
        op.drop_table('user_message_settings')
    
    if 'message_reports' in existing_tables:
        op.drop_index('idx_reports_status', table_name='message_reports')
        op.drop_index('ix_message_reports_message_id', table_name='message_reports')
        op.drop_index('ix_message_reports_id', table_name='message_reports')
        op.drop_table('message_reports')
    
    if 'blocked_users' in existing_tables:
        op.drop_index('idx_blocks_blocked', table_name='blocked_users')
        op.drop_index('idx_blocks_blocker', table_name='blocked_users')
        op.drop_index('ix_blocked_users_id', table_name='blocked_users')
        op.drop_table('blocked_users')
    
    if 'message_attachments' in existing_tables:
        op.drop_index('idx_attachments_type', table_name='message_attachments')
        op.drop_index('ix_message_attachments_message_id', table_name='message_attachments')
        op.drop_index('ix_message_attachments_id', table_name='message_attachments')
        op.drop_table('message_attachments')
    
    if 'message_read_receipts' in existing_tables:
        op.drop_index('idx_receipts_user', table_name='message_read_receipts')
        op.drop_index('idx_receipts_message', table_name='message_read_receipts')
        op.drop_index('ix_message_read_receipts_id', table_name='message_read_receipts')
        op.drop_table('message_read_receipts')
    
    if 'messages' in existing_tables:
        op.drop_index('idx_messages_conversation_created', table_name='messages')
        op.drop_index('ix_messages_created_at', table_name='messages')
        op.drop_index('ix_messages_sender_id', table_name='messages')
        op.drop_index('ix_messages_conversation_id', table_name='messages')
        op.drop_index('ix_messages_id', table_name='messages')
        op.drop_table('messages')
    
    if 'conversation_participants' in existing_tables:
        op.drop_index('idx_participant_unread', table_name='conversation_participants')
        op.drop_index('idx_participant_conversation', table_name='conversation_participants')
        op.drop_index('idx_participant_user', table_name='conversation_participants')
        op.drop_index('ix_conversation_participants_id', table_name='conversation_participants')
        op.drop_table('conversation_participants')
    
    if 'conversations' in existing_tables:
        op.drop_index('idx_conversations_request', table_name='conversations')
        op.drop_index('idx_conversations_last_activity', table_name='conversations')
        op.drop_index('ix_conversations_id', table_name='conversations')
        op.drop_table('conversations')


def _is_sqlite() -> bool:
    """Check if we're using SQLite."""
    from alembic import context
    return context.get_bind().dialect.name == 'sqlite'
