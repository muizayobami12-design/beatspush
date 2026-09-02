"""Add Fan Club System tables

Revision ID: 005
Revises: 004
Create Date: 2026-08-15 10:00:00.000000

This migration creates all tables for the Fan Club & Membership System:
- fan_clubs: Creator's membership community configuration
- membership_tiers: Subscription levels with pricing and benefits
- subscriptions: Fan subscriptions to creator tiers
- subscription_payments: Payment transaction records
- exclusive_content: Tier-gated content tracking
- creator_payouts: Monthly payout records

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, Sequence[str], None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create fan club system tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # 1. Create fan_clubs table (Task 1.1)
    if 'fan_clubs' not in existing_tables:
        op.create_table(
            'fan_clubs',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('creator_id', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('welcome_message', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
            sa.Column('total_members', sa.Integer(), default=0, nullable=True),
            sa.Column('monthly_revenue', sa.Numeric(precision=10, scale=2), default=0.00, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('creator_id', name='uq_fanclub_creator')
        )
        op.create_index('ix_fan_clubs_id', 'fan_clubs', ['id'], unique=False)
        op.create_index('idx_fanclub_creator', 'fan_clubs', ['creator_id'], unique=False)
        op.create_index('idx_fanclub_active', 'fan_clubs', ['is_active'], unique=False)
    
    # 2. Create membership_tiers table (Task 1.2)
    if 'membership_tiers' not in existing_tables:
        op.create_table(
            'membership_tiers',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('fan_club_id', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('tier_level', sa.Integer(), nullable=False),
            sa.Column('price_monthly', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('price_yearly', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('benefits', sa.JSON() if not _is_sqlite() else sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
            sa.Column('subscriber_count', sa.Integer(), default=0, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.CheckConstraint('price_monthly >= 2.99', name='ck_tier_min_monthly_price'),
            sa.CheckConstraint('price_monthly <= 99.99', name='ck_tier_max_monthly_price'),
            sa.CheckConstraint('tier_level BETWEEN 1 AND 3', name='ck_tier_level_range'),
            sa.ForeignKeyConstraint(['fan_club_id'], ['fan_clubs.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('fan_club_id', 'name', name='uq_fanclub_tier_name'),
            sa.UniqueConstraint('fan_club_id', 'tier_level', name='uq_fanclub_tier_level')
        )
        op.create_index('ix_membership_tiers_id', 'membership_tiers', ['id'], unique=False)
        op.create_index('idx_tier_fanclub', 'membership_tiers', ['fan_club_id'], unique=False)
        op.create_index('idx_tier_level', 'membership_tiers', ['tier_level'], unique=False)
        op.create_index('ix_membership_tiers_is_active', 'membership_tiers', ['is_active'], unique=False)
    
    # 3. Create subscriptions table (Task 1.3)
    if 'subscriptions' not in existing_tables:
        op.create_table(
            'subscriptions',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('fan_club_id', sa.String(length=36), nullable=False),
            sa.Column('tier_id', sa.String(length=36), nullable=False),
            sa.Column('subscriber_id', sa.String(length=36), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False, default='active'),
            sa.Column('billing_cycle', sa.String(length=10), nullable=False),
            sa.Column('price_paid', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('currency', sa.String(length=3), default='USD', nullable=True),
            sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
            sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
            sa.Column('next_billing_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('paused_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('paused_until', sa.DateTime(timezone=True), nullable=True),
            sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('trial_end_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('auto_renew', sa.Boolean(), default=True, nullable=True),
            sa.Column('failed_payment_count', sa.Integer(), default=0, nullable=True),
            sa.Column('payment_provider', sa.String(length=20), nullable=False),
            sa.Column('payment_provider_subscription_id', sa.String(length=100), nullable=True),
            sa.Column('payment_provider_customer_id', sa.String(length=100), nullable=True),
            sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True),
            sa.Column('paystack_subscription_code', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['fan_club_id'], ['fan_clubs.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['tier_id'], ['membership_tiers.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['subscriber_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('fan_club_id', 'subscriber_id', name='uq_fanclub_subscriber'),
            sa.UniqueConstraint('payment_provider_subscription_id', name='uq_provider_subscription_id'),
            sa.UniqueConstraint('stripe_subscription_id', name='uq_stripe_subscription_id'),
            sa.UniqueConstraint('paystack_subscription_code', name='uq_paystack_subscription_code')
        )
        op.create_index('ix_subscriptions_id', 'subscriptions', ['id'], unique=False)
        op.create_index('idx_subscription_fanclub', 'subscriptions', ['fan_club_id'], unique=False)
        op.create_index('idx_subscription_subscriber', 'subscriptions', ['subscriber_id'], unique=False)
        op.create_index('idx_subscription_status', 'subscriptions', ['status'], unique=False)
        op.create_index('idx_subscription_period_end', 'subscriptions', ['current_period_end'], unique=False)
        op.create_index('idx_subscription_provider', 'subscriptions', ['payment_provider_subscription_id'], unique=False)
        op.create_index('ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'], unique=False)
        op.create_index('ix_subscriptions_paystack_subscription_code', 'subscriptions', ['paystack_subscription_code'], unique=False)
    
    # 4. Create subscription_payments table (Task 1.4)
    if 'subscription_payments' not in existing_tables:
        op.create_table(
            'subscription_payments',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('subscription_id', sa.String(length=36), nullable=False),
            sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('currency', sa.String(length=3), default='USD', nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('payment_method', sa.String(length=50), nullable=True),
            sa.Column('payment_provider', sa.String(length=20), nullable=False),
            sa.Column('payment_provider_payment_id', sa.String(length=100), nullable=True),
            sa.Column('payment_provider_charge_id', sa.String(length=100), nullable=True),
            sa.Column('payment_provider_invoice_id', sa.String(length=100), nullable=True),
            sa.Column('failure_code', sa.String(length=50), nullable=True),
            sa.Column('failure_message', sa.Text(), nullable=True),
            sa.Column('retry_attempt', sa.Integer(), default=0, nullable=True),
            sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('platform_fee', sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column('creator_payout', sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column('payment_processing_fee', sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.CheckConstraint('amount > 0', name='ck_payment_positive_amount'),
            sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('payment_provider_payment_id', name='uq_provider_payment_id')
        )
        op.create_index('ix_subscription_payments_id', 'subscription_payments', ['id'], unique=False)
        op.create_index('idx_payment_subscription', 'subscription_payments', ['subscription_id'], unique=False)
        op.create_index('idx_payment_status', 'subscription_payments', ['status'], unique=False)
        op.create_index('idx_payment_date', 'subscription_payments', ['paid_at'], unique=False)
        op.create_index('idx_payment_provider_id', 'subscription_payments', ['payment_provider_payment_id'], unique=False)
    
    # 5. Create exclusive_content table (Task 1.5)
    if 'exclusive_content' not in existing_tables:
        op.create_table(
            'exclusive_content',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('fan_club_id', sa.String(length=36), nullable=False),
            sa.Column('content_type', sa.String(length=20), nullable=False),
            sa.Column('content_id', sa.String(length=36), nullable=False),
            sa.Column('minimum_tier_level', sa.Integer(), nullable=False),
            sa.Column('teaser_text', sa.Text(), nullable=True),
            sa.Column('preview_url', sa.String(length=500), nullable=True),
            sa.Column('view_count', sa.Integer(), default=0, nullable=True),
            sa.Column('engagement_count', sa.Integer(), default=0, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.CheckConstraint('minimum_tier_level BETWEEN 1 AND 3', name='ck_exclusive_tier_range'),
            sa.ForeignKeyConstraint(['fan_club_id'], ['fan_clubs.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('content_type', 'content_id', name='uq_content_exclusivity')
        )
        op.create_index('ix_exclusive_content_id', 'exclusive_content', ['id'], unique=False)
        op.create_index('idx_exclusive_fanclub', 'exclusive_content', ['fan_club_id'], unique=False)
        op.create_index('idx_exclusive_content', 'exclusive_content', ['content_type', 'content_id'], unique=False)
        op.create_index('ix_exclusive_content_content_type', 'exclusive_content', ['content_type'], unique=False)
    
    # 6. Create creator_payouts table
    if 'creator_payouts' not in existing_tables:
        op.create_table(
            'creator_payouts',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('creator_id', sa.String(length=36), nullable=False),
            sa.Column('fan_club_id', sa.String(length=36), nullable=False),
            sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('currency', sa.String(length=3), default='USD', nullable=True),
            sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
            sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('payout_method', sa.String(length=50), nullable=True),
            sa.Column('payout_destination', sa.String(length=200), nullable=True),
            sa.Column('payment_provider', sa.String(length=20), nullable=True),
            sa.Column('payment_provider_payout_id', sa.String(length=100), nullable=True),
            sa.Column('failure_reason', sa.Text(), nullable=True),
            sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.CheckConstraint('amount >= 50.00', name='ck_payout_minimum'),
            sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['fan_club_id'], ['fan_clubs.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('payment_provider_payout_id', name='uq_provider_payout_id')
        )
        op.create_index('ix_creator_payouts_id', 'creator_payouts', ['id'], unique=False)
        op.create_index('idx_payout_creator', 'creator_payouts', ['creator_id'], unique=False)
        op.create_index('idx_payout_status', 'creator_payouts', ['status'], unique=False)
        op.create_index('idx_payout_scheduled', 'creator_payouts', ['scheduled_at'], unique=False)


def downgrade() -> None:
    """Drop fan club system tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Drop tables in reverse order (respect foreign keys)
    if 'creator_payouts' in existing_tables:
        op.drop_index('idx_payout_scheduled', table_name='creator_payouts')
        op.drop_index('idx_payout_status', table_name='creator_payouts')
        op.drop_index('idx_payout_creator', table_name='creator_payouts')
        op.drop_index('ix_creator_payouts_id', table_name='creator_payouts')
        op.drop_table('creator_payouts')
    
    if 'exclusive_content' in existing_tables:
        op.drop_index('ix_exclusive_content_content_type', table_name='exclusive_content')
        op.drop_index('idx_exclusive_content', table_name='exclusive_content')
        op.drop_index('idx_exclusive_fanclub', table_name='exclusive_content')
        op.drop_index('ix_exclusive_content_id', table_name='exclusive_content')
        op.drop_table('exclusive_content')
    
    if 'subscription_payments' in existing_tables:
        op.drop_index('idx_payment_provider_id', table_name='subscription_payments')
        op.drop_index('idx_payment_date', table_name='subscription_payments')
        op.drop_index('idx_payment_status', table_name='subscription_payments')
        op.drop_index('idx_payment_subscription', table_name='subscription_payments')
        op.drop_index('ix_subscription_payments_id', table_name='subscription_payments')
        op.drop_table('subscription_payments')
    
    if 'subscriptions' in existing_tables:
        op.drop_index('ix_subscriptions_paystack_subscription_code', table_name='subscriptions')
        op.drop_index('ix_subscriptions_stripe_subscription_id', table_name='subscriptions')
        op.drop_index('idx_subscription_provider', table_name='subscriptions')
        op.drop_index('idx_subscription_period_end', table_name='subscriptions')
        op.drop_index('idx_subscription_status', table_name='subscriptions')
        op.drop_index('idx_subscription_subscriber', table_name='subscriptions')
        op.drop_index('idx_subscription_fanclub', table_name='subscriptions')
        op.drop_index('ix_subscriptions_id', table_name='subscriptions')
        op.drop_table('subscriptions')
    
    if 'membership_tiers' in existing_tables:
        op.drop_index('ix_membership_tiers_is_active', table_name='membership_tiers')
        op.drop_index('idx_tier_level', table_name='membership_tiers')
        op.drop_index('idx_tier_fanclub', table_name='membership_tiers')
        op.drop_index('ix_membership_tiers_id', table_name='membership_tiers')
        op.drop_table('membership_tiers')
    
    if 'fan_clubs' in existing_tables:
        op.drop_index('idx_fanclub_active', table_name='fan_clubs')
        op.drop_index('idx_fanclub_creator', table_name='fan_clubs')
        op.drop_index('ix_fan_clubs_id', table_name='fan_clubs')
        op.drop_table('fan_clubs')


def _is_sqlite() -> bool:
    """Check if we're using SQLite."""
    from alembic import context
    return context.get_bind().dialect.name == 'sqlite'
