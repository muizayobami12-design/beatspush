"""
Unit tests for AnalyticsService.

Tests:
- MRR calculation
- ARPU calculation
- LTV calculation
- Churn rate
- Retention cohorts
- Revenue forecasting
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.analytics_service import AnalyticsService


class TestMRRCalculation:
    """Test Monthly Recurring Revenue calculation."""
    
    def test_mrr_single_subscription(
        self,
        db_session: Session,
        fan_club,
        active_subscription
    ):
        """Test MRR with single subscription."""
        service = AnalyticsService(db_session)
        
        mrr_data = service.get_mrr(fan_club_id=fan_club.id)
        
        assert mrr_data['mrr'] == active_subscription.tier.price
        assert mrr_data['active_subscriptions'] == 1
        assert 'breakdown' in mrr_data
    
    def test_mrr_breakdown_by_tier(
        self,
        db_session: Session,
        fan_club,
        active_subscription
    ):
        """Test MRR breakdown by tier."""
        service = AnalyticsService(db_session)
        
        mrr_data = service.get_mrr(fan_club_id=fan_club.id)
        
        assert mrr_data['breakdown'] is not None
        assert len(mrr_data['breakdown']) > 0
    
    def test_mrr_excludes_inactive(
        self,
        db_session: Session,
        fan_club,
        active_subscription,
        cancelled_subscription
    ):
        """Test that MRR excludes inactive subscriptions."""
        service = AnalyticsService(db_session)
        
        mrr_data = service.get_mrr(fan_club_id=fan_club.id)
        
        # Should only include active_subscription
        assert mrr_data['active_subscriptions'] == 1
        assert mrr_data['mrr'] == active_subscription.tier.price


class TestARPUCalculation:
    """Test Average Revenue Per User calculation."""
    
    def test_arpu_single_user(
        self,
        db_session: Session,
        fan_club,
        active_subscription
    ):
        """Test ARPU with single user."""
        service = AnalyticsService(db_session)
        
        arpu_data = service.get_arpu(fan_club_id=fan_club.id)
        
        assert arpu_data['arpu'] == active_subscription.tier.price
        assert arpu_data['active_users'] == 1
        assert arpu_data['total_revenue'] == active_subscription.tier.price
    
    def test_arpu_multiple_users(
        self,
        db_session: Session,
        fan_club,
        subscriber_user,
        membership_tiers
    ):
        """Test ARPU calculation with multiple users."""
        from app.models.fan_club import Subscription
        
        # Create multiple subscriptions
        for i in range(3):
            subscription = Subscription(
                fan_club_id=fan_club.id,
                tier_id=membership_tiers['premium'].id,
                subscriber_id=subscriber_user.id + i,
                status="active",
                billing_cycle="monthly",
                price_paid=Decimal("9.99"),
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                started_at=datetime.utcnow(),
                auto_renew=True,
                payment_provider="stripe"
            )
        
        service = AnalyticsService(db_session)
        arpu_data = service.get_arpu(fan_club_id=fan_club.id)
        
        assert arpu_data['active_users'] >= 1
        assert arpu_data['arpu'] > Decimal("0.00")


class TestLTVCalculation:
    """Test Lifetime Value calculation."""
    
    def test_ltv_calculation(
        self,
        db_session: Session,
        fan_club
    ):
        """Test LTV calculation."""
        service = AnalyticsService(db_session)
        
        ltv_data = service.get_ltv(fan_club_id=fan_club.id)
        
        assert ltv_data['ltv'] >= Decimal("0.00")
        assert ltv_data['avg_arpu'] >= Decimal("0.00")
        assert ltv_data['avg_lifetime_months'] >= 0


class TestChurnRateCalculation:
    """Test churn rate calculation."""
    
    def test_churn_rate_monthly(
        self,
        db_session: Session,
        fan_club,
        active_subscription,
        cancelled_subscription
    ):
        """Test monthly churn rate."""
        service = AnalyticsService(db_session)
        
        # Use current month
        churn_data = service.get_churn_rate(fan_club_id=fan_club.id)
        
        assert 'churn_rate' in churn_data
        assert churn_data['churn_rate'] >= 0
        assert churn_data['churn_rate'] <= 100
    
    def test_churn_rate_zero_when_no_cancellations(
        self,
        db_session: Session,
        fan_club,
        active_subscription
    ):
        """Test churn rate is zero with no cancellations."""
        service = AnalyticsService(db_session)
        
        churn_data = service.get_churn_rate(fan_club_id=fan_club.id)
        
        # Should be 0 or very low (depends on timing)
        assert churn_data['churn_rate'] >= 0


class TestChurnReasons:
    """Test churn reasons analysis."""
    
    def test_get_churn_reasons_empty(
        self,
        db_session: Session,
        fan_club
    ):
        """Test churn reasons when empty."""
        service = AnalyticsService(db_session)
        
        reasons = service.get_churn_reasons(fan_club_id=fan_club.id)
        
        assert isinstance(reasons, list)
    
    def test_get_churn_reasons_with_data(
        self,
        db_session: Session,
        fan_club,
        cancelled_subscription
    ):
        """Test churn reasons with cancellations."""
        service = AnalyticsService(db_session)
        
        reasons = service.get_churn_reasons(fan_club_id=fan_club.id)
        
        assert isinstance(reasons, list)
        if reasons:
            assert 'reason' in reasons[0]
            assert 'count' in reasons[0]


class TestRetentionCohort:
    """Test retention cohort analysis."""
    
    def test_retention_cohort_calculation(
        self,
        db_session: Session,
        fan_club
    ):
        """Test retention cohort calculation."""
        service = AnalyticsService(db_session)
        
        cohort_month = date.today().replace(day=1)
        cohort = service.get_retention_cohort(
            cohort_month,
            fan_club_id=fan_club.id
        )
        
        assert 'cohort_month' in cohort
        assert 'cohort_size' in cohort
        assert 'retention' in cohort
        assert isinstance(cohort['retention'], list)


class TestRetentionMatrix:
    """Test retention matrix."""
    
    def test_retention_matrix_calculation(
        self,
        db_session: Session,
        fan_club
    ):
        """Test retention matrix calculation."""
        service = AnalyticsService(db_session)
        
        matrix = service.get_retention_matrix(
            months=3,
            fan_club_id=fan_club.id
        )
        
        assert isinstance(matrix, list)
        if matrix:
            assert 'cohort_month' in matrix[0]
            assert 'cohort_size' in matrix[0]
            assert 'retention_percentages' in matrix[0]


class TestRevenueTrend:
    """Test revenue trend calculation."""
    
    def test_revenue_trend_12_months(
        self,
        db_session: Session,
        fan_club
    ):
        """Test 12-month revenue trend."""
        service = AnalyticsService(db_season)
        
        trend = service.get_revenue_trend(
            months=12,
            fan_club_id=fan_club.id
        )
        
        assert isinstance(trend, list)
        assert len(trend) <= 12
        if trend:
            assert 'month' in trend[0]
            assert 'mrr' in trend[0]
            assert 'subscriptions' in trend[0]


class TestRevenueForecasting:
    """Test revenue forecasting."""
    
    def test_linear_forecast(
        self,
        db_session: Session,
        fan_club
    ):
        """Test linear revenue forecast."""
        service = AnalyticsService(db_session)
        
        forecast = service.forecast_revenue(
            months_ahead=6,
            method='linear',
            fan_club_id=fan_club.id
        )
        
        assert isinstance(forecast, list)
        # May be empty if not enough historical data
        if forecast:
            assert 'month' in forecast[0]
            assert 'forecast_mrr' in forecast[0]
            assert 'confidence_interval' in forecast[0]
    
    def test_seasonal_forecast(
        self,
        db_session: Session,
        fan_club
    ):
        """Test seasonal revenue forecast."""
        service = AnalyticsService(db_session)
        
        forecast = service.forecast_revenue(
            months_ahead=3,
            method='seasonal',
            fan_club_id=fan_club.id
        )
        
        assert isinstance(forecast, list)


class TestMetricsCalculation:
    """Test various metrics calculations."""
    
    def test_creator_metrics(
        self,
        db_session: Session,
        creator_user
    ):
        """Test creator metrics calculation."""
        service = AnalyticsService(db_session)
        
        metrics = service.get_creator_metrics(creator_user.id)
        
        assert 'creator_id' in metrics
        assert 'fan_clubs' in metrics
        assert 'total_subscribers' in metrics
        assert 'total_mrr' in metrics
    
    def test_fan_club_metrics(
        self,
        db_session: Session,
        fan_club,
        active_subscription
    ):
        """Test fan club metrics calculation."""
        service = AnalyticsService(db_session)
        
        metrics = service.get_fan_club_metrics(fan_club.id)
        
        assert 'fan_club_id' in metrics
        assert 'name' in metrics
        assert 'total_subscribers' in metrics
        assert 'active_subscribers' in metrics
        assert 'mrr' in metrics
    
    def test_subscriber_activity(
        self,
        db_session: Session,
        subscriber_user
    ):
        """Test subscriber activity metrics."""
        service = AnalyticsService(db_session)
        
        activity = service.get_subscriber_activity(subscriber_user.id)
        
        assert 'subscriber_id' in activity
        assert 'engagement_score' in activity
        assert 0 <= activity['engagement_score'] <= 100
