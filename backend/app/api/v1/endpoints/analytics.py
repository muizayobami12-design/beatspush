"""
Analytics API Endpoints
Task 4.2: Unified Analytics Dashboard

Endpoints for viewing comprehensive analytics and insights
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.dependencies import get_db, get_current_user
from app.models.user import User, UserRole
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    AnalyticsDashboardResponse,
    TrackAnalyticsResponse,
    OverviewStats,
    TrackPerformance,
    PlatformStats,
    GeographicStats,
    EngagementTimeline,
    # Task 4.3: Track Performance Analytics schemas
    TrackPerformanceResponse,
    TrackComparisonResponse,
    TrackGrowthTrendsResponse,
    TrackRankingsResponse,
    # Task 4.4: Audience Analytics schemas
    AudienceDemographicsResponse,
    FanSegmentsResponse,
    AudienceGrowthResponse,
    RetentionMetricsResponse,
    AudienceInsightsResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ================== DASHBOARD ==================

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
def get_analytics_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unified analytics dashboard for the current user.
    
    **Returns:**
    - Overview stats (tracks, plays, likes, campaigns, promo links)
    - Top 5 performing tracks
    - Platform breakdown
    - Geographic distribution
    - Engagement timeline (30 days)
    - AI-generated insights
    
    **Parameters:**
    - `days`: Number of days to analyze (default: 30)
    
    **Use this for:**
    - Main analytics page
    - Performance overview
    - Quick insights
    """
    
    # Get overview stats
    overview_data = AnalyticsService.get_overview_stats(db, current_user.id, days)
    overview = OverviewStats(**overview_data)
    
    # Get top tracks
    top_tracks_data = AnalyticsService.get_top_tracks(db, current_user.id, limit=5)
    top_tracks = [TrackPerformance(**track) for track in top_tracks_data]
    
    # Get platform stats
    platform_stats_data = AnalyticsService.get_platform_stats(db, current_user.id)
    platform_stats = [PlatformStats(**stat) for stat in platform_stats_data]
    
    # Get geographic stats
    geographic_data = AnalyticsService.get_geographic_stats(db, current_user.id, limit=10)
    geographic_stats = [GeographicStats(**geo) for geo in geographic_data]
    
    # Get engagement timeline
    timeline_data = AnalyticsService.get_engagement_timeline(db, current_user.id, days)
    engagement_timeline = EngagementTimeline(**timeline_data)
    
    # Generate insights
    insights = AnalyticsService.generate_insights(db, current_user.id)
    
    return AnalyticsDashboardResponse(
        overview=overview,
        top_tracks=top_tracks,
        platform_stats=platform_stats,
        geographic_stats=geographic_stats,
        engagement_timeline=engagement_timeline,
        insights=insights
    )


# ================== TRACK ANALYTICS ==================

# NOTE: Specific routes must come before parametrized routes to avoid conflicts
@router.get("/tracks/rankings", response_model=TrackRankingsResponse)
def get_track_rankings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get rankings of all user's tracks by various metrics.
    
    **Rankings By:**
    - Plays (most played tracks)
    - Engagement (best engagement rate)
    - Revenue (highest earning tracks)
    
    **Returns:**
    - Top 10 tracks in each category
    - Track metrics and rankings
    - Total track count
    
    **Use this for:**
    - Portfolio overview
    - Identifying top performers
    - Understanding what works
    - Resource allocation decisions
    """
    try:
        rankings = AnalyticsService.get_user_track_rankings(db, current_user.id)
        return TrackRankingsResponse(**rankings)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get track rankings: {str(e)}")


@router.get("/tracks/{track_id}", response_model=TrackAnalyticsResponse)
def get_track_analytics(
    track_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed analytics for a specific track.
    
    **Returns:**
    - Track performance metrics
    - Promo link performance
    - Platform breakdown
    - Geographic distribution
    - Time series data
    - Track-specific insights
    
    **Use this for:**
    - Individual track analytics page
    - Deep dive into track performance
    - Promo link effectiveness
    """
    
    analytics_data = AnalyticsService.get_track_analytics(db, track_id, current_user.id)
    
    if not analytics_data:
        raise HTTPException(status_code=404, detail="Track not found or access denied")
    
    return TrackAnalyticsResponse(**analytics_data)


# ================== OVERVIEW ONLY ==================

@router.get("/overview", response_model=OverviewStats)
def get_overview_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overview statistics only (lightweight endpoint).
    
    **Returns:** Overview cards data only
    
    **Use this for:**
    - Dashboard summary cards
    - Quick stats refresh
    - Mobile apps (lighter payload)
    """
    
    overview_data = AnalyticsService.get_overview_stats(db, current_user.id, days)
    return OverviewStats(**overview_data)


# ================== TOP TRACKS ==================

@router.get("/top-tracks")
def get_top_tracks(
    limit: int = Query(10, ge=1, le=50, description="Number of tracks to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get top performing tracks.
    
    **Parameters:**
    - `limit`: Number of tracks (1-50, default: 10)
    
    **Returns:** List of top tracks by performance score
    """
    
    tracks_data = AnalyticsService.get_top_tracks(db, current_user.id, limit)
    return [TrackPerformance(**track) for track in tracks_data]


# ================== PLATFORM STATS ==================

@router.get("/platforms")
def get_platform_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get platform performance breakdown.
    
    **Returns:** Click distribution across platforms (Spotify, Apple Music, etc.)
    
    **Use this for:**
    - Platform comparison charts
    - Understanding audience platform preferences
    """
    
    stats_data = AnalyticsService.get_platform_stats(db, current_user.id)
    return [PlatformStats(**stat) for stat in stats_data]


# ================== GEOGRAPHIC STATS ==================

@router.get("/geographic")
def get_geographic_stats(
    limit: int = Query(10, ge=1, le=50, description="Number of countries to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get geographic distribution.
    
    **Parameters:**
    - `limit`: Number of countries (1-50, default: 10)
    
    **Returns:** Top countries by click count
    
    **Use this for:**
    - Geographic heatmaps
    - Understanding audience location
    - Targeting campaigns
    """
    
    geo_data = AnalyticsService.get_geographic_stats(db, current_user.id, limit)
    return [GeographicStats(**geo) for geo in geo_data]


# ================== ENGAGEMENT TIMELINE ==================

@router.get("/timeline", response_model=EngagementTimeline)
def get_engagement_timeline(
    days: int = Query(30, ge=7, le=365, description="Number of days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get engagement timeline for charts.
    
    **Parameters:**
    - `days`: Number of days (7-365, default: 30)
    
    **Returns:** Time series data for plays, likes, shares, clicks
    
    **Use this for:**
    - Line charts
    - Trend analysis
    - Performance over time
    """
    
    timeline_data = AnalyticsService.get_engagement_timeline(db, current_user.id, days)
    return EngagementTimeline(**timeline_data)


# ================== INSIGHTS ==================

@router.get("/insights")
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-generated insights and recommendations.
    
    **Returns:** List of actionable insights based on user data
    
    **Use this for:**
    - Dashboard notifications
    - Tips and suggestions
    - Performance highlights
    """
    
    insights = AnalyticsService.generate_insights(db, current_user.id)
    return {"insights": insights}



# ================== TRACK PERFORMANCE ANALYTICS (Task 4.3) ==================

@router.get("/track/{track_id}/performance", response_model=TrackPerformanceResponse)
def get_track_performance(
    track_id: str,
    days: int = Query(30, ge=7, le=365, description="Number of days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed performance analytics for a specific track.
    
    **Authorization:** Must be the track owner
    
    **Metrics:**
    - Total plays, likes, shares, downloads
    - Performance score (weighted metric)
    - Tips revenue
    - Promo link clicks
    
    **Breakdown:**
    - Platform breakdown (Spotify, Apple Music, YouTube, etc.)
    - Geographic distribution (top countries)
    - Engagement timeline (daily data)
    - Playlist adds (algorithmic, editorial, user)
    - Listener demographics (age, gender)
    
    **Use this for:**
    - Individual track analysis
    - Understanding audience
    - Identifying best platforms
    - Geographic targeting
    
    **Returns:** Comprehensive track performance data
    """
    try:
        performance = AnalyticsService.get_track_performance(db, track_id, current_user.id, days)
        return TrackPerformanceResponse(**performance)
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get track performance: {str(e)}")


@router.post("/tracks/compare", response_model=TrackComparisonResponse)
def compare_tracks(
    track_ids: List[str] = Body(..., description="List of track IDs to compare (max 5)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare performance of multiple tracks.
    
    **Authorization:** Must own all tracks
    
    **Limit:** Max 5 tracks at once
    
    **Comparison Metrics:**
    - Plays, likes, shares, downloads
    - Performance score
    - Revenue
    - Engagement rate
    - Rankings
    
    **Returns:**
    - Side-by-side comparison
    - Best performer
    - Total aggregates
    
    **Use this for:**
    - A/B testing content styles
    - Identifying successful patterns
    - Portfolio analysis
    """
    try:
        comparison = AnalyticsService.compare_tracks(db, current_user.id, track_ids)
        return TrackComparisonResponse(**comparison)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare tracks: {str(e)}")


@router.get("/track/{track_id}/growth", response_model=TrackGrowthTrendsResponse)
def get_track_growth_trends(
    track_id: str,
    days: int = Query(90, ge=30, le=365, description="Number of days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get growth trends for a track over time.
    
    **Authorization:** Must be the track owner
    
    **Period:** 30-365 days (default: 90 days)
    
    **Metrics:**
    - Weekly breakdown (plays, likes, shares, new listeners)
    - Growth rate percentage
    - Trend direction (growing/stable/declining)
    - Peak week identification
    
    **Use this for:**
    - Tracking momentum
    - Identifying viral moments
    - Understanding lifecycle
    - Planning promotion timing
    
    **Returns:** Weekly growth data and trends
    """
    try:
        trends = AnalyticsService.get_track_growth_trends(db, track_id, current_user.id, days)
        return TrackGrowthTrendsResponse(**trends)
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get growth trends: {str(e)}")




# ================== AUDIENCE ANALYTICS (Task 4.4) ==================

@router.get("/audience/demographics", response_model=AudienceDemographicsResponse)
def get_audience_demographics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive audience demographics.
    
    **Authorization:** Requires authentication
    
    **Returns:**
    - Total listener count
    - Age distribution (6 age groups)
    - Gender breakdown
    - Geographic distribution (top 15 countries)
    - Device usage (mobile, desktop, tablet)
    - Platform preferences (Spotify, Apple Music, etc.)
    
    **Data Sources:**
    - Promo link clicks (geographic data)
    - Platform analytics (simulated, ready for real API integration)
    - Listener tracking from plays
    
    **Use this for:**
    - Understanding your audience composition
    - Targeting campaigns effectively
    - Making content decisions
    - Planning tours and events
    """
    try:
        demographics = AnalyticsService.get_audience_demographics(db, current_user.id)
        return AudienceDemographicsResponse(**demographics)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audience demographics: {str(e)}")


@router.get("/audience/segments", response_model=FanSegmentsResponse)
def get_fan_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get fan segmentation based on engagement levels.
    
    **Authorization:** Requires authentication
    
    **Fan Segments:**
    - **Super Fans:** Top 5% most engaged listeners
      - Listen 10+ times per track
      - High engagement score (95)
      - Likely to share and promote
    
    - **New Listeners:** Discovered in last 30 days
      - 25% of audience
      - Average 2 plays per track
      - Conversion opportunity
    
    - **Casual Listeners:** Occasional listeners
      - 60% of audience
      - Moderate engagement
      - Growth potential
    
    - **At-Risk:** Previously active, now declining
      - 10% of audience
      - Need re-engagement
      - Risk of churn
    
    **Returns:**
    - Counts and percentages for each segment
    - Engagement scores
    - Average plays per track
    - Actionable insights
    
    **Use this for:**
    - Targeted re-engagement campaigns
    - Reward programs for super fans
    - Converting casual to engaged listeners
    - Preventing churn
    """
    try:
        segments = AnalyticsService.get_fan_segments(db, current_user.id)
        return FanSegmentsResponse(**segments)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get fan segments: {str(e)}")


@router.get("/audience/growth", response_model=AudienceGrowthResponse)
def get_audience_growth(
    days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Track audience growth over time.
    
    **Authorization:** Requires authentication
    
    **Query Parameters:**
    - `days`: Analysis period (30-365 days, default: 90)
    
    **Returns:**
    - Current audience size
    - Weekly growth data points
    - Growth rate percentage
    - Net new listeners
    - Average daily growth
    - Trend classification (growing, stable, declining)
    
    **Each Week Shows:**
    - Audience size at week end
    - New listeners acquired
    - Churned listeners (stopped listening)
    - Net growth (new - churned)
    
    **Growth Rate Calculation:**
    - Compares recent 4 weeks to previous 4 weeks
    - Positive = growing audience
    - Negative = declining audience
    
    **Use this for:**
    - Monitoring growth trajectory
    - Evaluating campaign effectiveness
    - Setting growth targets
    - Identifying growth inflection points
    """
    try:
        growth = AnalyticsService.get_audience_growth(db, current_user.id, days)
        return AudienceGrowthResponse(**growth)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audience growth: {str(e)}")


@router.get("/audience/retention", response_model=RetentionMetricsResponse)
def get_retention_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get listener retention metrics.
    
    **Authorization:** Requires authentication
    
    **Metrics Returned:**
    
    1. **Overall Retention Rate:**
       - Percentage of listeners who return within 30 days
       - Industry benchmark: 25-30%
    
    2. **Cohort Retention:**
       - Retention at Day 1, 7, 14, 30, 60, 90
       - Shows how many listeners stick around over time
       - Helps identify drop-off points
    
    3. **Retention by Source:**
       - How well listeners from each source stick around
       - Sources: Promo Links, Social Media, Playlists, Search, Direct
       - Identifies best acquisition channels
    
    4. **Average Session Duration:**
       - How long listeners typically engage
       - Measured in minutes
       - Indicates content stickiness
    
    5. **Repeat Listener Rate:**
       - Percentage who come back for more
       - Higher = more engaged audience
    
    **Use this for:**
    - Identifying churn points
    - Optimizing acquisition channels
    - Improving content strategy
    - Increasing listener lifetime value
    """
    try:
        retention = AnalyticsService.get_retention_metrics(db, current_user.id)
        return RetentionMetricsResponse(**retention)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get retention metrics: {str(e)}")


@router.get("/audience/insights", response_model=AudienceInsightsResponse)
def get_audience_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered audience insights and recommendations.
    
    **Authorization:** Requires authentication
    
    **What You Get:**
    
    1. **Insights:**
       - Key findings about your audience
       - Demographic patterns
       - Geographic strengths
       - Engagement trends
       - Growth patterns
    
    2. **Recommendations:**
       - Actionable steps to grow
       - Platform-specific advice
       - Content suggestions
       - Timing recommendations
       - Collaboration opportunities
       - Tour/event locations
    
    3. **Content Strategy:**
       - Optimal posting frequency
       - Best platforms for your audience
       - Recommended content types
       - Timing for maximum engagement
    
    4. **Growth Strategy:**
       - Focus areas for growth
       - Target demographics to reach
       - Geographic markets to prioritize
    
    **AI Analysis Includes:**
    - Audience size and composition
    - Fan segment distribution
    - Growth trajectory
    - Retention patterns
    - Platform performance
    - Geographic reach
    
    **Use this for:**
    - Strategic planning
    - Campaign optimization
    - Resource allocation
    - Content calendar planning
    - Partnership decisions
    """
    try:
        insights = AnalyticsService.generate_audience_insights(db, current_user.id)
        return AudienceInsightsResponse(**insights)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate audience insights: {str(e)}")
