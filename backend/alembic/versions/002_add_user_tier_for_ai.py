"""add user tier for AI

Revision ID: 002
Revises: 001
Create Date: 2026-08-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create user tier enum
    user_tier_enum = postgresql.ENUM('free', 'premium', name='usertier', create_type=False)
    user_tier_enum.create(op.get_bind(), checkfirst=True)
    
    # Add tier column to users table
    op.add_column('users', sa.Column('tier', sa.Enum('free', 'premium', name='usertier'), 
                                       server_default='free', nullable=False))


def downgrade():
    # Remove tier column
    op.drop_column('users', 'tier')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS usertier")
