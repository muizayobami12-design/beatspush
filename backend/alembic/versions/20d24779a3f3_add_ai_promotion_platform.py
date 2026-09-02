"""add_ai_promotion_platform

Revision ID: 20d24779a3f3
Revises: 003
Create Date: 2026-08-13

Adds AI Promotion Platform tables and columns (SQLite compatible)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20d24779a3f3'
down_revision = '003'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if table exists in database"""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    """Check if column exists in table"""
    if not table_exists(table_name):
        return False
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
    return column_name in existing_columns


def upgrade():
    """Apply migration - only create missing tables/columns"""
    
    # POST DRAFTS - Post approval workflow
    if not table_exists('post_drafts'):
        op.create_table(
            'post_drafts',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
            sa.Column('platform', sa.String(20), nullable=False),
            sa.Column('social_account_id', sa.String(36), sa.ForeignKey('social_accounts.id')),
            sa.Column('caption', sa.Text, nullable=False),
            sa.Column('media_urls', sa.Text),  # JSON array as text
            sa.Column('hashtags', sa.Text),  # JSON array as text
            sa.Column('scheduled_time', sa.DateTime(timezone=True)),
            sa.Column('status', sa.String(20)),
            sa.Column('platform_post_id', sa.String(255)),
            sa.Column('approved_at', sa.DateTime(timezone=True)),
            sa.Column('published_at', sa.DateTime(timezone=True)),
            sa.Column('rejection_reason', sa.Text),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
        )
        op.create_index('idx_post_drafts_campaign_status', 'post_drafts', ['campaign_id', 'status'])
        op.create_index('idx_post_drafts_platform_status', 'post_drafts', ['platform', 'status'])

    # PLATFORM METRICS - Performance tracking
    if not table_exists('platform_metrics'):
        op.create_table(
            'platform_metrics',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=False),
            sa.Column('beat_id', sa.String(36), sa.ForeignKey('beats.id'), nullable=False),
            sa.Column('platform', sa.String(20), nullable=False),
            sa.Column('post_id', sa.String(36), sa.ForeignKey('post_drafts.id')),
            sa.Column('metric_date', sa.Date, nullable=False),
            sa.Column('plays', sa.Integer, default=0),
            sa.Column('likes', sa.Integer, default=0),
            sa.Column('shares', sa.Integer, default=0),
            sa.Column('comments', sa.Integer, default=0),
            sa.Column('saves', sa.Integer, default=0),
            sa.Column('click_throughs', sa.Integer, default=0),
            sa.Column('revenue_ngn', sa.Numeric(10, 2), default=0),
            sa.Column('raw_data', sa.Text),  # JSON as text
            sa.Column('synced_at', sa.DateTime(timezone=True), server_default=sa.func.now())
        )
        op.create_index('idx_platform_metrics_unique', 'platform_metrics', 
                       ['campaign_id', 'platform', 'metric_date'], unique=True)
        op.create_index('idx_platform_metrics_campaign_date', 'platform_metrics', ['campaign_id', 'metric_date'])
        op.create_index('idx_platform_metrics_beat_platform', 'platform_metrics', ['beat_id', 'platform'])

    # PAYMENT PLANS - Split payments and pay-after-earnings
    if not table_exists('payment_plans'):
        op.create_table(
            'payment_plans',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
            sa.Column('plan_type', sa.String(20), nullable=False),
            sa.Column('total_amount_ngn', sa.Numeric(10, 2), nullable=False),
            sa.Column('paid_amount_ngn', sa.Numeric(10, 2), default=0),
            sa.Column('installments', sa.Text),  # JSON as text
            sa.Column('pay_after_percentage', sa.Numeric(5, 2)),
            sa.Column('minimum_payment_ngn', sa.Numeric(10, 2)),
            sa.Column('status', sa.String(20)),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
        )
        op.create_index('idx_payment_plans_campaign_status', 'payment_plans', ['campaign_id', 'status'])
        op.create_index('idx_payment_plans_type', 'payment_plans', ['plan_type'])

    # FREE TIER USAGE - Track free feature usage quotas
    if not table_exists('free_tier_usage'):
        op.create_table(
            'free_tier_usage',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('feature_type', sa.String(50), nullable=False),
            sa.Column('usage_date', sa.Date, nullable=False),
            sa.Column('usage_count', sa.Integer, default=1),
            sa.Column('quota_limit', sa.Integer),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
        )
        op.create_index('idx_free_tier_usage_unique', 'free_tier_usage',
                       ['user_id', 'feature_type', 'usage_date'], unique=True)

    # BUNDLE PURCHASES - Bulk campaign discounts
    if not table_exists('bundle_purchases'):
        op.create_table(
            'bundle_purchases',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('package_id', sa.String(36), sa.ForeignKey('promotion_packages.id'), nullable=False),
            sa.Column('quantity', sa.Integer, nullable=False),
            sa.Column('discount_percentage', sa.Numeric(5, 2), nullable=False),
            sa.Column('price_per_campaign_ngn', sa.Numeric(10, 2), nullable=False),
            sa.Column('total_paid_ngn', sa.Numeric(10, 2), nullable=False),
            sa.Column('campaigns_used', sa.Integer, default=0),
            sa.Column('campaigns_remaining', sa.Integer, nullable=False),
            sa.Column('expires_at', sa.DateTime(timezone=True)),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
        )
        op.create_index('idx_bundle_purchases_user_remaining', 'bundle_purchases', 
                       ['user_id', 'campaigns_remaining'])

    # ADD COLUMNS TO CAMPAIGNS
    if not column_exists('campaigns', 'package_id'):
        op.add_column('campaigns', sa.Column('package_id', sa.String(36)))
    if not column_exists('campaigns', 'payment_id'):
        op.add_column('campaigns', sa.Column('payment_id', sa.String(255)))
    if not column_exists('campaigns', 'paid_amount_currency'):
        op.add_column('campaigns', sa.Column('paid_amount_currency', sa.String(3)))
    if not column_exists('campaigns', 'paid_amount'):
        op.add_column('campaigns', sa.Column('paid_amount', sa.Numeric(10, 2)))
    if not column_exists('campaigns', 'paid_amount_ngn'):
        op.add_column('campaigns', sa.Column('paid_amount_ngn', sa.Numeric(10, 2)))
    if not column_exists('campaigns', 'target_countries'):
        op.add_column('campaigns', sa.Column('target_countries', sa.Text))
    if not column_exists('campaigns', 'target_platforms'):
        op.add_column('campaigns', sa.Column('target_platforms', sa.Text))
    if not column_exists('campaigns', 'budget_spent_ngn'):
        op.add_column('campaigns', sa.Column('budget_spent_ngn', sa.Numeric(10, 2), default=0))
    if not column_exists('campaigns', 'earnings_ngn'):
        op.add_column('campaigns', sa.Column('earnings_ngn', sa.Numeric(10, 2), default=0))
    if not column_exists('campaigns', 'total_reach'):
        op.add_column('campaigns', sa.Column('total_reach', sa.Integer, default=0))
    if not column_exists('campaigns', 'total_plays'):
        op.add_column('campaigns', sa.Column('total_plays', sa.Integer, default=0))
    if not column_exists('campaigns', 'total_likes'):
        op.add_column('campaigns', sa.Column('total_likes', sa.Integer, default=0))
    if not column_exists('campaigns', 'total_shares'):
        op.add_column('campaigns', sa.Column('total_shares', sa.Integer, default=0))
    if not column_exists('campaigns', 'total_comments'):
        op.add_column('campaigns', sa.Column('total_comments', sa.Integer, default=0))
    if not column_exists('campaigns', 'started_at'):
        op.add_column('campaigns', sa.Column('started_at', sa.DateTime(timezone=True)))
    if not column_exists('campaigns', 'ends_at'):
        op.add_column('campaigns', sa.Column('ends_at', sa.DateTime(timezone=True)))

    # ADD COLUMNS TO BEATS
    if not column_exists('beats', 'price_tiktok'):
        op.add_column('beats', sa.Column('price_tiktok', sa.Integer))
    if not column_exists('beats', 'price_instagram'):
        op.add_column('beats', sa.Column('price_instagram', sa.Integer))
    if not column_exists('beats', 'price_facebook'):
        op.add_column('beats', sa.Column('price_facebook', sa.Integer))
    if not column_exists('beats', 'price_spotify'):
        op.add_column('beats', sa.Column('price_spotify', sa.Integer))
    if not column_exists('beats', 'price_apple_music'):
        op.add_column('beats', sa.Column('price_apple_music', sa.Integer))
    if not column_exists('beats', 'copyright_status'):
        op.add_column('beats', sa.Column('copyright_status', sa.String(20), default='pending'))
    if not column_exists('beats', 'copyright_scan_id'):
        op.add_column('beats', sa.Column('copyright_scan_id', sa.String(36)))

    # ADD COLUMNS TO USERS
    if not column_exists('users', 'ai_conversation_enabled'):
        op.add_column('users', sa.Column('ai_conversation_enabled', sa.Boolean, default=True))
    if not column_exists('users', 'default_target_countries'):
        op.add_column('users', sa.Column('default_target_countries', sa.Text, default='["NG"]'))


def downgrade():
    """Rollback migration"""
    # Drop added columns
    op.drop_column('users', 'default_target_countries')
    op.drop_column('users', 'ai_conversation_enabled')
    
    op.drop_column('beats', 'copyright_scan_id')
    op.drop_column('beats', 'copyright_status')
    op.drop_column('beats', 'price_apple_music')
    op.drop_column('beats', 'price_spotify')
    op.drop_column('beats', 'price_facebook')
    op.drop_column('beats', 'price_instagram')
    op.drop_column('beats', 'price_tiktok')
    
    op.drop_column('campaigns', 'ends_at')
    op.drop_column('campaigns', 'started_at')
    op.drop_column('campaigns', 'total_comments')
    op.drop_column('campaigns', 'total_shares')
    op.drop_column('campaigns', 'total_likes')
    op.drop_column('campaigns', 'total_plays')
    op.drop_column('campaigns', 'total_reach')
    op.drop_column('campaigns', 'earnings_ngn')
    op.drop_column('campaigns', 'budget_spent_ngn')
    op.drop_column('campaigns', 'target_platforms')
    op.drop_column('campaigns', 'target_countries')
    op.drop_column('campaigns', 'paid_amount_ngn')
    op.drop_column('campaigns', 'paid_amount')
    op.drop_column('campaigns', 'paid_amount_currency')
    op.drop_column('campaigns', 'payment_id')
    op.drop_column('campaigns', 'package_id')
    
    # Drop new tables
    op.drop_table('bundle_purchases')
    op.drop_table('free_tier_usage')
    op.drop_table('payment_plans')
    op.drop_table('platform_metrics')
    op.drop_table('post_drafts')
