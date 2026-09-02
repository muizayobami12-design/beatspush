"""Add ML Analytics System tables

Revision ID: 008
Revises: 007
Create Date: 2026-09-01 10:00:00.000000

This migration creates all tables for the ML Analytics System:
- revenue_predictions: Revenue forecasting data
- audience_predictions: Audience growth predictions
- trend_forecasts: Beat trend analysis
- anomaly_detections: Unusual pattern detection
- health_scores: User health metrics
- insights_reports: Comprehensive AI reports

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '008'
down_revision: Union[str, Sequence[str], None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ML analytics system tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # 1. Create revenue_predictions table
    if 'revenue_predictions' not in existing_tables:
        op.create_table(
            'revenue_predictions',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('current_revenue', sa.Float(), default=0.0, nullable=True),
            sa.Column('predicted_revenue', sa.Float(), default=0.0, nullable=True),
            sa.Column('trend_percentage', sa.Float(), default=0.0, nullable=True),
            sa.Column('confidence', sa.Float(), default=0.0, nullable=True),
            sa.Column('days_ahead', sa.Integer(), default=30, nullable=True),
            sa.Column('predictions', sa.JSON(), nullable=True),
            sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_revenue_predictions_user_id', 'revenue_predictions', ['user_id'])
        op.create_index('ix_revenue_predictions_generated_at', 'revenue_predictions', ['generated_at'])
    
    # 2. Create audience_predictions table
    if 'audience_predictions' not in existing_tables:
        op.create_table(
            'audience_predictions',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('current_followers', sa.Integer(), default=0, nullable=True),
            sa.Column('predicted_followers', sa.Integer(), default=0, nullable=True),
            sa.Column('projected_growth', sa.Integer(), default=0, nullable=True),
            sa.Column('growth_rate_per_day', sa.Float(), default=0.0, nullable=True),
            sa.Column('confidence', sa.Float(), default=0.0, nullable=True),
            sa.Column('days_ahead', sa.Integer(), default=30, nullable=True),
            sa.Column('predictions', sa.JSON(), nullable=True),
            sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_audience_predictions_user_id', 'audience_predictions', ['user_id'])
        op.create_index('ix_audience_predictions_generated_at', 'audience_predictions', ['generated_at'])
    
    # 3. Create trend_forecasts table
    if 'trend_forecasts' not in existing_tables:
        op.create_table(
            'trend_forecasts',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('beat_id', sa.String(length=36), nullable=False),
            sa.Column('trend', sa.String(length=50), nullable=True),
            sa.Column('trend_score', sa.Float(), default=0.0, nullable=True),
            sa.Column('confidence', sa.Float(), default=0.0, nullable=True),
            sa.Column('days_ahead', sa.Integer(), default=14, nullable=True),
            sa.Column('play_trend', sa.Float(), default=0.0, nullable=True),
            sa.Column('engagement_trend', sa.Float(), default=0.0, nullable=True),
            sa.Column('current_plays_daily', sa.Float(), default=0.0, nullable=True),
            sa.Column('current_saves_daily', sa.Float(), default=0.0, nullable=True),
            sa.Column('recommendation', sa.Text(), nullable=True),
            sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.ForeignKeyConstraint(['beat_id'], ['beats.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_trend_forecasts_beat_id', 'trend_forecasts', ['beat_id'])
        op.create_index('ix_trend_forecasts_generated_at', 'trend_forecasts', ['generated_at'])
    
    # 4. Create anomaly_detections table
    if 'anomaly_detections' not in existing_tables:
        op.create_table(
            'anomaly_detections',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('metric', sa.String(length=50), nullable=False),
            sa.Column('anomaly_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('anomaly_value', sa.Float(), nullable=True),
            sa.Column('anomaly_score', sa.Float(), default=0.0, nullable=True),
            sa.Column('severity', sa.String(length=50), nullable=True),
            sa.Column('expected_value', sa.Float(), nullable=True),
            sa.Column('deviation', sa.Float(), nullable=True),
            sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_anomaly_detections_user_id', 'anomaly_detections', ['user_id'])
        op.create_index('ix_anomaly_detections_detected_at', 'anomaly_detections', ['detected_at'])
    
    # 5. Create health_scores table
    if 'health_scores' not in existing_tables:
        op.create_table(
            'health_scores',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False, unique=True),
            sa.Column('overall_score', sa.Integer(), default=0, nullable=True),
            sa.Column('rating', sa.String(length=50), nullable=True),
            sa.Column('revenue_health', sa.Integer(), default=0, nullable=True),
            sa.Column('audience_health', sa.Integer(), default=0, nullable=True),
            sa.Column('stability', sa.Integer(), default=0, nullable=True),
            sa.Column('previous_score', sa.Integer(), default=0, nullable=True),
            sa.Column('score_change', sa.Integer(), default=0, nullable=True),
            sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_health_scores_user_id', 'health_scores', ['user_id'])
        op.create_index('ix_health_scores_calculated_at', 'health_scores', ['calculated_at'])
    
    # 6. Create insights_reports table
    if 'insights_reports' not in existing_tables:
        op.create_table(
            'insights_reports',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('report_data', sa.JSON(), nullable=True),
            sa.Column('revenue_prediction_id', sa.String(length=36), nullable=True),
            sa.Column('audience_prediction_id', sa.String(length=36), nullable=True),
            sa.Column('health_score_id', sa.String(length=36), nullable=True),
            sa.Column('anomalies_count', sa.Integer(), default=0, nullable=True),
            sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['revenue_prediction_id'], ['revenue_predictions.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['audience_prediction_id'], ['audience_predictions.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['health_score_id'], ['health_scores.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_insights_reports_user_id', 'insights_reports', ['user_id'])
        op.create_index('ix_insights_reports_generated_at', 'insights_reports', ['generated_at'])


def downgrade() -> None:
    """Drop ML analytics system tables."""
    op.drop_index('ix_insights_reports_generated_at', table_name='insights_reports')
    op.drop_index('ix_insights_reports_user_id', table_name='insights_reports')
    op.drop_table('insights_reports')
    
    op.drop_index('ix_health_scores_calculated_at', table_name='health_scores')
    op.drop_index('ix_health_scores_user_id', table_name='health_scores')
    op.drop_table('health_scores')
    
    op.drop_index('ix_anomaly_detections_detected_at', table_name='anomaly_detections')
    op.drop_index('ix_anomaly_detections_user_id', table_name='anomaly_detections')
    op.drop_table('anomaly_detections')
    
    op.drop_index('ix_trend_forecasts_generated_at', table_name='trend_forecasts')
    op.drop_index('ix_trend_forecasts_beat_id', table_name='trend_forecasts')
    op.drop_table('trend_forecasts')
    
    op.drop_index('ix_audience_predictions_generated_at', table_name='audience_predictions')
    op.drop_index('ix_audience_predictions_user_id', table_name='audience_predictions')
    op.drop_table('audience_predictions')
    
    op.drop_index('ix_revenue_predictions_generated_at', table_name='revenue_predictions')
    op.drop_index('ix_revenue_predictions_user_id', table_name='revenue_predictions')
    op.drop_table('revenue_predictions')
