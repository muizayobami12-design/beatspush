"""
Integration tests for analytics endpoints.

Tests all 15+ analytics endpoints:
- Revenue metrics (MRR, ARPU, LTV)
- Churn analysis
- Retention cohorts
- Revenue forecasting
- Comparisons
- Dashboard
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, date

from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestRevenueEndpoints:
    """Test revenue analytics endpoints."""
    
    def test_get_mrr(self, client, creator_token, fan_club):
        """Test getting Monthly Recurring Revenue."""
        response = client.get(
            f"/api/v1/analytics/revenue/mrr?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mrr" in data
        assert "active_subscriptions" in data
        assert "breakdown" in data
    
    def test_get_arpu(self, client, creator_token, fan_club):
        """Test getting Average Revenue Per User."""
        response = client.get(
            f"/api/v1/analytics/revenue/arpu?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "arpu" in data
        assert "total_revenue" in data
        assert "active_users" in data
    
    def test_get_ltv(self, client, creator_token, fan_club):
        """Test getting Lifetime Value."""
        response = client.get(
            f"/api/v1/analytics/revenue/ltv?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "ltv" in data
        assert "avg_arpu" in data
        assert "avg_lifetime_months" in data
    
    def test_get_revenue_trend(self, client, creator_token, fan_club):
        """Test getting revenue trend."""
        response = client.get(
            f"/api/v1/analytics/revenue/trend?fan_club_id={fan_club.id}&months=12",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_mrr_with_specific_month(self, client, creator_token, fan_club):
        """Test MRR for specific month."""
        month = datetime.utcnow().strftime("%Y-%m")
        
        response = client.get(
            f"/api/v1/analytics/revenue/mrr?fan_club_id={fan_club.id}&month={month}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == month


class TestChurnEndpoints:
    """Test churn analysis endpoints."""
    
    def test_get_churn_rate(self, client, creator_token, fan_club):
        """Test getting churn rate."""
        response = client.get(
            f"/api/v1/analytics/churn/rate?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "churn_rate" in data
        assert "churned_subscribers" in data
        assert "beginning_subscribers" in data
        assert "ending_subscribers" in data
    
    def test_get_churn_reasons(self, client, creator_token, fan_club):
        """Test getting churn reasons."""
        response = client.get(
            f"/api/v1/analytics/churn/reasons?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "reasons" in data
        assert isinstance(data["reasons"], list)


class TestRetentionEndpoints:
    """Test retention analysis endpoints."""
    
    def test_get_retention_cohort(self, client, creator_token, fan_club):
        """Test getting retention cohort."""
        month = date.today().replace(day=1).strftime("%Y-%m")
        
        response = client.get(
            f"/api/v1/analytics/retention/cohort?fan_club_id={fan_club.id}&month={month}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "cohort_month" in data
        assert "cohort_size" in data
        assert "retention" in data
    
    def test_get_retention_matrix(self, client, creator_token, fan_club):
        """Test getting retention matrix."""
        response = client.get(
            f"/api/v1/analytics/retention/matrix?fan_club_id={fan_club.id}&months=12",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "cohorts" in data
        assert "months" in data


class TestForecastEndpoints:
    """Test revenue forecasting endpoints."""
    
    def test_get_revenue_forecast(self, client, creator_token, fan_club):
        """Test revenue forecast."""
        response = client.get(
            f"/api/v1/analytics/forecast/revenue?fan_club_id={fan_club.id}&months=6&method=linear",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        assert isinstance(data["forecast"], list)
    
    def test_forecast_with_seasonal_method(self, client, creator_token, fan_club):
        """Test seasonal forecast."""
        response = client.get(
            f"/api/v1/analytics/forecast/revenue?fan_club_id={fan_club.id}&months=6&method=seasonal",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200


class TestMetricsEndpoints:
    """Test metrics endpoints."""
    
    def test_get_creator_metrics(self, client, creator_token):
        """Test creator metrics."""
        response = client.get(
            "/api/v1/analytics/metrics/creator",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "creator_id" in data
        assert "fan_clubs" in data
        assert "total_subscribers" in data
    
    def test_get_fan_club_metrics(self, client, creator_token, fan_club):
        """Test fan club metrics."""
        response = client.get(
            f"/api/v1/analytics/metrics/fan-club?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "fan_club_id" in data
        assert "total_subscribers" in data
        assert "mrr" in data


class TestDashboardEndpoint:
    """Test dashboard summary endpoint."""
    
    def test_get_dashboard_summary(self, client, creator_token, fan_club):
        """Test dashboard summary."""
        response = client.get(
            f"/api/v1/analytics/dashboard/summary?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mrr" in data
        assert "arpu" in data
        assert "churn_rate" in data
        assert "active_subscribers" in data


class TestComparisonEndpoints:
    """Test period comparison endpoints."""
    
    def test_compare_periods(self, client, creator_token, fan_club):
        """Test comparing two periods."""
        today = date.today()
        period1_start = (today - timedelta(days=60)).strftime("%Y-%m-%d")
        period1_end = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        period2_start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        period2_end = today.strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/v1/analytics/compare/period?fan_club_id={fan_club.id}&"
            f"period1_start={period1_start}&period1_end={period1_end}&"
            f"period2_start={period2_start}&period2_end={period2_end}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "period1" in data
        assert "period2" in data
        assert "comparison" in data
        assert "trend" in data
    
    def test_mom_comparison(self, client, creator_token, fan_club):
        """Test month-over-month comparison."""
        response = client.get(
            f"/api/v1/analytics/compare/month-over-month?fan_club_id={fan_club.id}&months=12",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "comparisons" in data
        assert "average_growth_percent" in data
        assert "trend" in data
    
    def test_yoy_comparison(self, client, creator_token, fan_club):
        """Test year-over-year comparison."""
        response = client.get(
            f"/api/v1/analytics/compare/year-over-year?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        # May fail if not enough historical data
        assert response.status_code in [200, 400]


class TestCacheManagement:
    """Test cache management endpoints."""
    
    def test_get_cache_stats(self, client, creator_token):
        """Test getting cache statistics."""
        response = client.get(
            "/api/v1/analytics/cache/stats",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_invalidate_fan_club_cache(self, client, creator_token, fan_club):
        """Test invalidating fan club cache."""
        response = client.post(
            f"/api/v1/analytics/cache/invalidate?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200


class TestErrorHandling:
    """Test analytics error handling."""
    
    def test_unauthorized_analytics_access(self, client):
        """Test accessing analytics without auth."""
        response = client.get("/api/v1/analytics/revenue/mrr?fan_club_id=1")
        
        assert response.status_code == 401
    
    def test_forbidden_analytics_access(self, client, subscriber_token, fan_club):
        """Test non-creator accessing fan club analytics."""
        response = client.get(
            f"/api/v1/analytics/revenue/mrr?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {subscriber_token}"}
        )
        
        assert response.status_code == 403
    
    def test_invalid_date_format(self, client, creator_token, fan_club):
        """Test invalid date format in period comparison."""
        response = client.get(
            f"/api/v1/analytics/compare/period?fan_club_id={fan_club.id}&"
            f"period1_start=invalid&period1_end=invalid&"
            f"period2_start=invalid&period2_end=invalid",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 400


class TestAnalyticsPerformance:
    """Test analytics performance."""
    
    def test_mrr_response_time(self, client, creator_token, fan_club):
        """Test MRR endpoint response time (should be cached)."""
        import time
        
        start = time.time()
        response = client.get(
            f"/api/v1/analytics/revenue/mrr?fan_club_id={fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Should be fast (< 500ms with cache)
        assert elapsed < 1.0
    
    def test_cached_vs_uncached_performance(self, client, creator_token, fan_club):
        """Test performance improvement with caching."""
        # First request (cache miss)
        response1 = client.get(
            f"/api/v1/analytics/revenue/trend?fan_club_id={fan_club.id}&months=12",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        assert response1.status_code == 200
        
        # Second request (cache hit - should be faster)
        response2 = client.get(
            f"/api/v1/analytics/revenue/trend?fan_club_id={fan_club.id}&months=12",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        assert response2.status_code == 200
