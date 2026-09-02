"""add security features

Revision ID: 003
Revises: 002
Create Date: 2026-08-12

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add security fields to users table
    op.add_column('users', sa.Column('device_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('device_info', sa.String(1000), nullable=True))
    op.add_column('users', sa.Column('last_login_ip', sa.String(45), nullable=True))
    op.add_column('users', sa.Column('last_login_country', sa.String(2), nullable=True))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer, default=0))
    
    # Create indexes for security fields
    op.create_index('ix_users_device_id', 'users', ['device_id'])
    
    # Create security_events table
    op.create_table(
        'security_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('device_id', sa.String(255), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('country', sa.String(2), nullable=True),
        sa.Column('risk_score', sa.Float, nullable=True),
        sa.Column('flags', sa.Text, nullable=True),
        sa.Column('decision', sa.String(20), nullable=True),
        sa.Column('metadata', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Create indexes for security_events
    op.create_index('ix_security_events_id', 'security_events', ['id'])
    op.create_index('ix_security_events_event_type', 'security_events', ['event_type'])
    op.create_index('ix_security_events_user_id', 'security_events', ['user_id'])


def downgrade():
    # Drop security_events table
    op.drop_index('ix_security_events_user_id')
    op.drop_index('ix_security_events_event_type')
    op.drop_index('ix_security_events_id')
    op.drop_table('security_events')
    
    # Remove security fields from users
    op.drop_index('ix_users_device_id')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'last_login_country')
    op.drop_column('users', 'last_login_ip')
    op.drop_column('users', 'device_info')
    op.drop_column('users', 'device_id')
