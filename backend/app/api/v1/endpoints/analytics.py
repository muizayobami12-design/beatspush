"""
Analytics endpoints for fan club system.

Provides:
- MRR, ARPU, LTV calculations
- Revenue trends and forecasts
- Churn analysis and retention cohorts
- Engagement metrics
"""

import logging
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.cache import CacheManager
from app.models.user import User
from app.models.fan_club import FanClub
from app.services.analytics_service_cached import CachedAnalyticsService
from app.schemas.fan_club import (
    MRRResponse,
    ARPUResponse,
    LTVResponse,
    RevenueTrendResponse,
    ChurnRateResponse,
    ChurnReasonsResponse,
    RetentionCohortResponse,
    RetentionMatrixResponse,
    ForecastResponse,
    CreatorMetricsResponse,
    FanClubMetricsResponse,
    SubscriberActivityResponse
)

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)


# ==================== PERMISSION HELPERS ====================

def verify_fan_club_access(
    fan_club_id: int,
    user: User,
    db: Session
):
    """Verify user has access to fan club analytics."""
    fan_club = db.query(FanClub).filter(FanClub.id == fan_club_id).first()
    
    if not fan_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fan club not found"
        )
    
    # Only creator can access their fan club analytics
    if fan_club.creator_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return fan_club


# ==================== REVENUE ENDPOINTS ====================

@router.get(
    "/revenue/mrr",
    response_model=MRRResponse,
    summary="Get Monthly Recurring Revenue"
)
async def get_mrr(
    fan_club_id: int = Query(...),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate Monthly Recurring Revenue (MRR) for a fan club.
    
    MRR = Sum of all active subscription amounts in a month
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - month: Target month (optional, defaults to current month)
    
    **Returns:**
    - mrr: Total MRR amount
    - active_subscriptions: Number of active subscriptions
    - breakdown: Revenue by tier
    
    **Caching:** 1 hour TTL (automatically cached)
    """
    # Verify access
    verify_fan_club_access(fan_club_id, current_user, db)
    
    # Parse month if provided
    start_date = None
    if month:
        try:
            start_date = datetime.strptime(month, '%Y-%m').date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month format, use YYYY-MM"
            )
    
    analytics = CachedCachedAnalyticsService(db)
    mrr_data = analytics.get_mrr(start_date, fan_club_id=fan_club_id)
    
    return MRRResponse(**mrr_data)


@router.get(
    "/revenue/arpu",
    response_model=ARPUResponse,
    summary="Get Average Revenue Per User"
)
async def get_arpu(
    fan_club_id: int = Query(...),
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate Average Revenue Per User (ARPU).
    
    ARPU = Total Revenue / Active Subscribers
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - days: Period in days (default: 30)
    
    **Returns:**
    - arpu: Average revenue per user
    - total_revenue: Total revenue in period
    - active_users: Number of active users
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    start_date = date.fromordinal(date.today().toordinal() - days)
    
    analytics = CachedCachedAnalyticsService(db)
    arpu_data = analytics.get_arpu(start_date, fan_club_id=fan_club_id)
    
    return ARPUResponse(**arpu_data)


@router.get(
    "/revenue/ltv",
    response_model=LTVResponse,
    summary="Get Lifetime Value"
)
async def get_ltv(
    fan_club_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate Lifetime Value (LTV) per subscriber.
    
    LTV = ARPU × Average Customer Lifespan
    
    **Parameters:**
    - fan_club_id: Fan club ID
    
    **Returns:**
    - ltv: Lifetime value per subscriber
    - avg_arpu: Average revenue per user
    - avg_lifetime_months: Average subscription duration
    - sample_size: Number of subscriptions analyzed
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    analytics = CachedAnalyticsService(db)
    ltv_data = analytics.get_ltv(fan_club_id=fan_club_id)
    
    return LTVResponse(**ltv_data)


@router.get(
    "/revenue/trend",
    response_model=RevenueTrendResponse,
    summary="Get Revenue Trend"
)
async def get_revenue_trend(
    fan_club_id: int = Query(...),
    months: int = Query(12, ge=3, le=36),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly revenue trend for N months.
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - months: Number of months (default: 12)
    
    **Returns:**
    - data: List of monthly revenue data
    - currency: Currency code
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    analytics = CachedAnalyticsService(db)
    trend = analytics.get_revenue_trend(months, fan_club_id=fan_club_id)
    
    return RevenueTrendResponse(data=trend)


# ==================== CHURN ENDPOINTS ====================

@router.get(
    "/churn/rate",
    response_model=ChurnRateResponse,
    summary="Get Monthly Churn Rate"
)
async def get_churn_rate(
    fan_club_id: int = Query(...),
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate monthly churn rate.
    
    Churn Rate = Cancelled / Beginning Subscribers × 100%
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - month: Target month (optional, defaults to last month)
    
    **Returns:**
    - churn_rate: Percentage of churned subscribers
    - churned_subscribers: Number of cancellations
    - beginning_subscribers: Subscribers at month start
    - ending_subscribers: Subscribers at month end
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    target_month = None
    if month:
        try:
            target_month = datetime.strptime(month, '%Y-%m').date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month format, use YYYY-MM"
            )
    
    analytics = CachedAnalyticsService(db)
    churn_data = analytics.get_churn_rate(target_month, fan_club_id=fan_club_id)
    
    return ChurnRateResponse(**churn_data)


@router.get(
    "/churn/reasons",
    response_model=ChurnReasonsResponse,
    summary="Get Churn Reasons"
)
async def get_churn_reasons(
    fan_club_id: int = Query(...),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get most common churn reasons.
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - limit: Max reasons to return (default: 10)
    
    **Returns:**
    - reasons: List of cancellation reasons with counts
    - total_churned: Total number of churned subscribers
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    analytics = CachedAnalyticsService(db)
    reasons = analytics.get_churn_reasons(limit, fan_club_id)
    
    total_churned = sum(r['count'] for r in reasons)
    
    return ChurnReasonsResponse(reasons=reasons, total_churned=total_churned)


# ==================== RETENTION ENDPOINTS ====================

@router.get(
    "/retention/cohort",
    response_model=RetentionCohortResponse,
    summary="Get Retention Cohort"
)
async def get_retention_cohort(
    fan_club_id: int = Query(...),
    month: str = Query(..., description="Cohort month in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate retention cohort for subscribers started in a month.
    
    Shows what % of subscribers from a month are still active after N months.
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - month: Cohort month in YYYY-MM format
    
    **Returns:**
    - cohort_month: Month of cohort
    - cohort_size: Number of subscribers in cohort
    - retention: Monthly retention data (0-12 months)
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    try:
        cohort_date = datetime.strptime(month, '%Y-%m').date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid month format, use YYYY-MM"
        )
    
    analytics = CachedAnalyticsService(db)
    cohort = analytics.get_retention_cohort(cohort_date, fan_club_id=fan_club_id)
    
    return RetentionCohortResponse(**cohort)


@router.get(
    "/retention/matrix",
    response_model=RetentionMatrixResponse,
    summary="Get Retention Matrix"
)
async def get_retention_matrix(
    fan_club_id: int = Query(...),
    months: int = Query(12, ge=3, le=36),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get retention matrix for last N months.
    
    Shows retention cohorts for each month's new subscribers.
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - months: Number of months (default: 12)
    
    **Returns:**
    - cohorts: List of cohorts with retention percentages
    - months: Number of months requested
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    analytics = CachedAnalyticsService(db)
    matrix = analytics.get_retention_matrix(months, fan_club_id)
    
    return RetentionMatrixResponse(cohorts=matrix, months=months)


# ==================== FORECASTING ENDPOINTS ====================

@router.get(
    "/forecast/revenue",
    response_model=ForecastResponse,
    summary="Forecast Revenue"
)
async def forecast_revenue(
    fan_club_id: int = Query(...),
    months: int = Query(6, ge=1, le=12),
    method: str = Query("linear", regex="^(linear|seasonal)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Forecast future revenue based on historical data.
    
    **Methods:**
    - linear: Linear regression on historical trend
    - seasonal: Seasonal adjustment (advanced)
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - months: Months to forecast (default: 6)
    - method: Forecasting method (default: linear)
    
    **Returns:**
    - forecast: List of monthly forecasts
    - currency: Currency code
    - historical_months: Months of historical data used
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    analytics = CachedAnalyticsService(db)
    forecast = analytics.forecast_revenue(months, method, fan_club_id=fan_club_id)
    
    return ForecastResponse(forecast=forecast)


# ==================== METRICS ENDPOINTS ====================

@router.get(
    "/metrics/creator",
    response_model=CreatorMetricsResponse,
    summary="Get Creator Metrics"
)
async def get_creator_metrics(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get creator fan club metrics.
    
    **Parameters:**
    - days: Period in days (default: 30)
    
    **Returns:**
    - creator_id: Creator ID
    - fan_clubs: Number of fan clubs
    - total_subscribers: Total across all fan clubs
    - total_mrr: Total MRR
    - average_tier_price: Average subscription price
    - top_tier: Most popular tier
    - churn_rate: Current churn rate
    """
    analytics = CachedAnalyticsService(db)
    metrics = analytics.get_creator_metrics(current_user.id, days)
    
    return CreatorMetricsResponse(**metrics)


@router.get(
    "/metrics/fan-club",
    response_model=FanClubMetricsResponse,
    summary="Get Fan Club Metrics"
)
async def get_fan_club_metrics(
    fan_club_id: int = Query(...),
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific fan club metrics.
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - days: Period in days (default: 30)
    
    **Returns:**
    - fan_club_id: Fan club ID
    - name: Fan club name
    - total_subscribers: Total subscribers
    - active_subscribers: Active subscriptions
    - cancelled_subscribers: Cancelled subscriptions
    - mrr: Monthly recurring revenue
    - growth_rate: Growth percentage
    - engagement_rate: Engagement percentage
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    analytics = CachedAnalyticsService(db)
    metrics = analytics.get_fan_club_metrics(fan_club_id, days)
    
    return FanClubMetricsResponse(**metrics)


@router.get(
    "/metrics/subscriber/{subscriber_id}",
    response_model=SubscriberActivityResponse,
    summary="Get Subscriber Activity"
)
async def get_subscriber_activity(
    subscriber_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get subscriber activity metrics.
    
    **Parameters:**
    - subscriber_id: Subscriber user ID
    - days: Period in days (default: 30)
    
    **Returns:**
    - subscriber_id: Subscriber ID
    - content_views: Number of content views
    - posts_liked: Number of posts liked
    - messages_sent: Messages sent
    - last_activity: Last activity timestamp
    - engagement_score: 0-100 engagement score
    """
    # TODO: Verify current user can access this subscriber
    
    analytics = CachedAnalyticsService(db)
    activity = analytics.get_subscriber_activity(subscriber_id, days)
    
    return SubscriberActivityResponse(**activity)


# ==================== DASHBOARD ENDPOINTS ====================

@router.get(
    "/dashboard/summary",
    summary="Get Dashboard Summary"
)
async def get_dashboard_summary(
    fan_club_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard summary for fan club.
    
    **Returns:**
    - mrr: Current MRR
    - arpu: Average revenue per user
    - churn_rate: Current churn rate
    - retention_rate: 30-day retention
    - forecast: Next month forecast
    - top_tier: Most popular tier
    - new_subscribers: New this month
    - trending: Growth trend (up/down/stable)
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    analytics = CachedAnalyticsService(db)
    
    # Get all metrics
    mrr = analytics.get_mrr(fan_club_id=fan_club_id)
    arpu = analytics.get_arpu(fan_club_id=fan_club_id)
    churn = analytics.get_churn_rate(fan_club_id=fan_club_id)
    forecast = analytics.forecast_revenue(1, fan_club_id=fan_club_id)
    metrics = analytics.get_fan_club_metrics(fan_club_id)
    
    # Determine trend
    trend_data = analytics.get_revenue_trend(3, fan_club_id=fan_club_id)
    trend = "stable"
    if len(trend_data) >= 2:
        if trend_data[-1]['mrr'] > trend_data[-2]['mrr']:
            trend = "up"
        elif trend_data[-1]['mrr'] < trend_data[-2]['mrr']:
            trend = "down"
    
    return {
        'mrr': mrr['mrr'],
        'arpu': arpu['arpu'],
        'churn_rate': churn['churn_rate'],
        'retention_rate': 100 - churn['churn_rate'],  # Inverse
        'forecast_next_month': forecast[0]['forecast_mrr'] if forecast else None,
        'top_tier': metrics.get('top_tier', 'N/A'),
        'new_subscribers': metrics.get('growth_rate', 0),
        'trending': trend,
        'active_subscribers': mrr['active_subscriptions'],
        'monthly_growth_percent': metrics.get('growth_rate', 0)
    }


@router.get(
    "/export/csv",
    summary="Export Analytics to CSV"
)
async def export_analytics_csv(
    fan_club_id: int = Query(...),
    report_type: str = Query("revenue", regex="^(revenue|churn|retention)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export analytics data as CSV.
    
    **Report Types:**
    - revenue: MRR and revenue trend
    - churn: Churn analysis and reasons
    - retention: Retention cohorts
    
    **Returns:**
    - CSV file download
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    # TODO: Implement CSV export
    return {"message": "CSV export coming soon"}


# ==================== CACHE MANAGEMENT ====================

@router.get(
    "/cache/stats",
    summary="Get Cache Statistics"
)
async def get_cache_stats(
    current_user: User = Depends(get_current_user),
):
    """
    Get cache statistics (admin only).
    
    **Returns:**
    - status: 'connected', 'unavailable', or 'error'
    - cached_analytics: Number of cached analytics
    - memory_used_mb: Memory used by cache
    - connected_clients: Number of connected clients
    """
    stats = CacheManager.get_cache_stats()
    return stats


@router.post(
    "/cache/invalidate",
    summary="Invalidate Cache"
)
async def invalidate_cache(
    fan_club_id: Optional[int] = Query(None),
    clear_all: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invalidate analytics cache (admin only).
    
    **Parameters:**
    - fan_club_id: Invalidate specific fan club cache
    - clear_all: Clear all analytics cache
    
    **Returns:**
    - message: Invalidation status
    """
    if fan_club_id:
        # Verify access
        verify_fan_club_access(fan_club_id, current_user, db)
        CacheManager.invalidate_fan_club(fan_club_id)
        return {"message": f"Invalidated cache for fan club {fan_club_id}"}
    
    elif clear_all:
        # TODO: Add admin check
        CacheManager.invalidate_all()
        return {"message": "Cleared all analytics cache"}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specify fan_club_id or set clear_all=true"
        )


# ==================== TIME-BASED COMPARISON ====================

@router.get(
    "/compare/period",
    summary="Compare Two Periods"
)
async def compare_periods(
    fan_club_id: int = Query(...),
    period1_start: str = Query(..., description="Period 1 start (YYYY-MM-DD)"),
    period1_end: str = Query(..., description="Period 1 end (YYYY-MM-DD)"),
    period2_start: str = Query(..., description="Period 2 start (YYYY-MM-DD)"),
    period2_end: str = Query(..., description="Period 2 end (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare metrics between two time periods.
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - period1_start: Start date (YYYY-MM-DD)
    - period1_end: End date (YYYY-MM-DD)
    - period2_start: Start date (YYYY-MM-DD)
    - period2_end: End date (YYYY-MM-DD)
    
    **Returns:**
    - period1: Metrics for first period
    - period2: Metrics for second period
    - comparison: Change in metrics (amount and %)
    - trend: 'up', 'down', or 'stable'
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    # Parse dates
    try:
        p1_start = datetime.strptime(period1_start, '%Y-%m-%d').date()
        p1_end = datetime.strptime(period1_end, '%Y-%m-%d').date()
        p2_start = datetime.strptime(period2_start, '%Y-%m-%d').date()
        p2_end = datetime.strptime(period2_end, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format, use YYYY-MM-DD"
        )
    
    analytics = CachedAnalyticsService(db)
    
    # Get metrics for both periods
    arpu1 = analytics.get_arpu(p1_start, p1_end, fan_club_id)
    arpu2 = analytics.get_arpu(p2_start, p2_end, fan_club_id)
    
    # Calculate change
    change_amount = arpu2['arpu'] - arpu1['arpu']
    change_percent = 0
    if arpu1['arpu'] > 0:
        change_percent = (change_amount / arpu1['arpu']) * 100
    
    trend = "stable"
    if change_percent > 5:
        trend = "up"
    elif change_percent < -5:
        trend = "down"
    
    return {
        'period1': {
            'start': period1_start,
            'end': period1_end,
            'arpu': arpu1['arpu'],
            'total_revenue': arpu1['total_revenue'],
            'active_users': arpu1['active_users']
        },
        'period2': {
            'start': period2_start,
            'end': period2_end,
            'arpu': arpu2['arpu'],
            'total_revenue': arpu2['total_revenue'],
            'active_users': arpu2['active_users']
        },
        'comparison': {
            'arpu_change': change_amount,
            'arpu_percent_change': round(change_percent, 2),
            'revenue_change': arpu2['total_revenue'] - arpu1['total_revenue'],
            'user_change': arpu2['active_users'] - arpu1['active_users']
        },
        'trend': trend
    }


@router.get(
    "/compare/month-over-month",
    summary="Month-Over-Month Comparison"
)
async def mom_comparison(
    fan_club_id: int = Query(...),
    months: int = Query(12, ge=3, le=24),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get month-over-month comparison for last N months.
    
    **Parameters:**
    - fan_club_id: Fan club ID
    - months: Number of months to compare (default: 12)
    
    **Returns:**
    - comparisons: List of month-to-month comparisons
    - average_growth: Average MoM growth %
    - trend: Overall trend
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    analytics = CachedAnalyticsService(db)
    trend = analytics.get_revenue_trend(months, fan_club_id=fan_club_id)
    
    comparisons = []
    growths = []
    
    for i in range(1, len(trend)):
        current = trend[i]
        previous = trend[i - 1]
        
        mrr_change = current['mrr'] - previous['mrr']
        mrr_percent = 0
        if previous['mrr'] > 0:
            mrr_percent = (mrr_change / previous['mrr']) * 100
        
        sub_change = current['subscriptions'] - previous['subscriptions']
        
        comparisons.append({
            'month': current['month'],
            'mrr_current': current['mrr'],
            'mrr_previous': previous['mrr'],
            'mrr_change': mrr_change,
            'mrr_percent_change': round(mrr_percent, 2),
            'subscriptions_change': sub_change,
            'trend': 'up' if mrr_change > 0 else 'down' if mrr_change < 0 else 'stable'
        })
        
        growths.append(mrr_percent)
    
    avg_growth = sum(growths) / len(growths) if growths else 0
    
    overall_trend = "stable"
    if avg_growth > 5:
        overall_trend = "up"
    elif avg_growth < -5:
        overall_trend = "down"
    
    return {
        'comparisons': comparisons,
        'average_growth_percent': round(avg_growth, 2),
        'trend': overall_trend,
        'months_analyzed': len(comparisons)
    }


@router.get(
    "/compare/year-over-year",
    summary="Year-Over-Year Comparison"
)
async def yoy_comparison(
    fan_club_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get year-over-year comparison.
    
    Compares current year metrics with previous year.
    
    **Parameters:**
    - fan_club_id: Fan club ID
    
    **Returns:**
    - current_year: Current year metrics (12 months)
    - previous_year: Previous year metrics (12 months)
    - comparison: YoY change
    - growth_percent: YoY growth %
    """
    verify_fan_club_access(fan_club_id, current_user, db)
    
    analytics = CachedAnalyticsService(db)
    
    # Get 24 months of data
    trend_24 = analytics.get_revenue_trend(24, fan_club_id=fan_club_id)
    
    if len(trend_24) < 24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough historical data for YoY comparison (need 24 months)"
        )
    
    current_year = trend_24[12:]  # Last 12 months
    previous_year = trend_24[:12]  # First 12 months
    
    current_mrr_total = sum(m['mrr'] for m in current_year)
    previous_mrr_total = sum(m['mrr'] for m in previous_year)
    
    mrr_change = current_mrr_total - previous_mrr_total
    growth_percent = 0
    if previous_mrr_total > 0:
        growth_percent = (mrr_change / previous_mrr_total) * 100
    
    return {
        'current_year': current_year,
        'previous_year': previous_year,
        'comparison': {
            'total_mrr_change': mrr_change,
            'total_mrr_percent_change': round(growth_percent, 2),
            'avg_mrr_current': sum(m['mrr'] for m in current_year) / 12,
            'avg_mrr_previous': sum(m['mrr'] for m in previous_year) / 12
        },
        'trend': 'up' if growth_percent > 0 else 'down' if growth_percent < 0 else 'stable'
    }
