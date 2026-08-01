"""
Analytics Schemas
Task 4.2: Unified Analytics Dashboard
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


# ================== RESPONSE SCHEMAS ==================

class OverviewStats(BaseModel):
    """Overview statistics card"""
    total_tracks: int = Field(..., description="Total tracks uploaded")
    total_plays: int = Field(..., description="Total plays across all tracks")
    total_likes: int = Field(..., description="Total likes")
    total_shares: int = Field(..., description="Total shares")
    
    # Promo links
    total_promo_links: int = Field(..., description="Total promo links created")
    promo_link_clicks: int = Field(..., description="Total clicks on promo links")
    promo_link_unique_clicks: int = Field(..., description="Unique clicks")
    
    # Campaigns
    total_campaigns: int = Field(..., description="Total campaigns created")
    active_campaigns: int = Field(..., description="Currently active campaigns")
    
    # Engagement
    engagement_rate: float = Field(..., description="Overall engagement rate")
    
    # Growth (vs previous period)
    plays_growth: float = Field(..., description="Growth % in plays")
    likes_growth: float = Field(..., description="Growth % in likes")
    clicks_growth: float = Field(..., description="Growth % in promo link clicks")


class TrackPerformance(BaseModel):
    """Individual track performance"""
    track_id: str
    track_title: str
    track_artist: str
    cover_url: Optional[str]
    
    plays: int
    likes: int
    shares: int
    downloads: int
    
    # Promo links for this track
    promo_links_count: int
    promo_link_clicks: int
    
    # Calculated
    engagement_rate: float
    performance_score: float = Field(..., description="0-100 score based on all metrics")


class PlatformStats(BaseModel):
    """Platform-specific statistics"""
    platform: str
    clicks: int
    unique_clicks: int
    percentage: float


class GeographicStats(BaseModel):
    """Geographic distribution"""
    country: str
    country_code: str
    clicks: int
    percentage: float


class TimeSeriesData(BaseModel):
    """Time series data point"""
    date: str
    value: int


class EngagementTimeline(BaseModel):
    """Engagement over time"""
    plays: List[TimeSeriesData]
    likes: List[TimeSeriesData]
    shares: List[TimeSeriesData]
    promo_clicks: List[TimeSeriesData]


class AnalyticsDashboardResponse(BaseModel):
    """Complete analytics dashboard data"""
    
    # Overview cards
    overview: OverviewStats
    
    # Top performing tracks
    top_tracks: List[TrackPerformance] = Field(..., description="Top 5 tracks by performance")
    
    # Platform breakdown
    platform_stats: List[PlatformStats] = Field(..., description="Performance by platform")
    
    # Geographic distribution
    geographic_stats: List[GeographicStats] = Field(..., description="Top 10 countries")
    
    # Engagement timeline
    engagement_timeline: EngagementTimeline = Field(..., description="Last 30 days")
    
    # Quick insights
    insights: List[str] = Field(..., description="AI-generated insights")


class TrackAnalyticsResponse(BaseModel):
    """Detailed analytics for a single track"""
    track_id: str
    track_title: str
    track_artist: str
    cover_url: Optional[str]
    
    # Overall stats
    total_plays: int
    total_likes: int
    total_shares: int
    total_downloads: int
    
    # Promo link performance
    promo_links: List[Dict[str, Any]] = Field(..., description="All promo links for this track")
    total_promo_clicks: int
    
    # Platform breakdown
    platform_clicks: Dict[str, int]
    
    # Geographic breakdown
    country_breakdown: Dict[str, int]
    city_breakdown: Dict[str, int]
    
    # Time series
    plays_over_time: List[TimeSeriesData]
    clicks_over_time: List[TimeSeriesData]
    
    # Engagement metrics
    engagement_rate: float
    click_through_rate: float
    
    # Insights
    insights: List[str]


class CampaignAnalyticsResponse(BaseModel):
    """Campaign performance analytics"""
    campaign_id: str
    campaign_name: str
    status: str
    
    # Platform content stats
    platforms: List[str]
    content_generated: int
    
    # Performance (when Task 3.3 is done, this will have real data)
    estimated_reach: int = Field(0, description="Placeholder for future")
    estimated_impressions: int = Field(0, description="Placeholder for future")
    estimated_engagement: int = Field(0, description="Placeholder for future")
    
    # Timing
    created_at: datetime
    scheduled_at: Optional[datetime]


class UserActivityResponse(BaseModel):
    """User activity log item"""
    id: str
    activity_type: str
    activity_data: Optional[Dict[str, Any]]
    created_at: datetime


class UserActivityListResponse(BaseModel):
    """List of user activities"""
    activities: List[UserActivityResponse]
    total: int
    page: int
    page_size: int


class ExportRequest(BaseModel):
    """Export analytics request"""
    format: str = Field(..., description="pdf or csv")
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    include_tracks: bool = True
    include_campaigns: bool = True
    include_promo_links: bool = True


class ComparisonPeriod(BaseModel):
    """Date range for comparison"""
    start_date: date
    end_date: date
    label: str = Field(..., description="e.g., 'This Week', 'Last Month'")



# ================== TRACK PERFORMANCE ANALYTICS (Task 4.3) ==================

class PlatformBreakdown(BaseModel):
    """Platform breakdown"""
    platform: str
    plays: int
    percentage: float


class GeoDistribution(BaseModel):
    """Geographic distribution"""
    country: str
    clicks: int
    percentage: float


class EngagementTimelinePoint(BaseModel):
    """Timeline data point"""
    date: str
    plays: int
    likes: int
    shares: int


class PlaylistAdds(BaseModel):
    """Playlist statistics"""
    total: int
    algorithmic: int
    editorial: int
    user_created: int


class DemographicGroup(BaseModel):
    """Demographic group"""
    range: Optional[str] = None
    gender: Optional[str] = None
    percentage: float
    count: int


class Demographics(BaseModel):
    """Demographics data"""
    age_groups: List[DemographicGroup]
    gender: List[DemographicGroup]


class TrackPerformanceResponse(BaseModel):
    """Track performance analytics"""
    track_id: str
    track_title: str
    total_plays: int
    total_likes: int
    total_shares: int
    total_downloads: int
    performance_score: float
    tips_revenue: float
    promo_clicks: int
    platform_breakdown: List[PlatformBreakdown]
    geo_distribution: List[GeoDistribution]
    engagement_timeline: List[EngagementTimelinePoint]
    playlist_adds: PlaylistAdds
    demographics: Demographics


class TrackComparisonItem(BaseModel):
    """Track comparison item"""
    track_id: str
    track_title: str
    plays: int
    likes: int
    shares: int
    downloads: int
    performance_score: float
    revenue: float
    engagement_rate: float
    rank: int


class TrackComparisonResponse(BaseModel):
    """Track comparison"""
    tracks: List[TrackComparisonItem]
    best_performer: Optional[TrackComparisonItem]
    total_plays: int
    total_revenue: float


class WeeklyDataPoint(BaseModel):
    """Weekly growth data"""
    week_start: str
    week_number: int
    plays: int
    likes: int
    shares: int
    new_listeners: int


class TrackGrowthTrendsResponse(BaseModel):
    """Track growth trends"""
    track_id: str
    track_title: str
    period_days: int
    weekly_data: List[WeeklyDataPoint]
    growth_rate_percentage: float
    trend: str
    peak_week: Optional[WeeklyDataPoint]


class TrackRankingItem(BaseModel):
    """Track ranking item"""
    track_id: str
    track_title: str
    plays: int
    likes: int
    shares: int
    performance_score: float
    engagement_rate: float
    revenue: float
    rank: int


class TrackRankingsResponse(BaseModel):
    """Track rankings"""
    by_plays: List[TrackRankingItem]
    by_engagement: List[TrackRankingItem]
    by_revenue: List[TrackRankingItem]
    total_tracks: int



# ================== AUDIENCE ANALYTICS (Task 4.4) ==================

class AgeDistribution(BaseModel):
    """Age distribution data"""
    age_range: str
    count: int
    percentage: float


class GenderBreakdown(BaseModel):
    """Gender breakdown data"""
    gender: str
    count: int
    percentage: float


class GeographicLocation(BaseModel):
    """Geographic location data"""
    country: str
    country_code: str
    listeners: int
    percentage: float


class DeviceUsage(BaseModel):
    """Device usage data"""
    device: str
    count: int
    percentage: float


class PlatformPreference(BaseModel):
    """Platform preference data"""
    platform: str
    listeners: int
    percentage: float


class AudienceDemographicsResponse(BaseModel):
    """Audience demographics dashboard"""
    total_listeners: int
    age_distribution: List[AgeDistribution]
    gender_breakdown: List[GenderBreakdown]
    geographic_distribution: List[GeographicLocation]
    device_usage: List[DeviceUsage]
    platform_preferences: List[PlatformPreference]


class FanSegment(BaseModel):
    """Fan segment data"""
    count: int
    percentage: float
    description: str
    avg_plays_per_track: int
    engagement_score: float


class FanSegmentsResponse(BaseModel):
    """Fan segmentation data"""
    super_fans: FanSegment
    new_listeners: FanSegment
    casual_listeners: FanSegment
    at_risk: FanSegment
    total_fans: int
    insights: List[str]


class GrowthDataPoint(BaseModel):
    """Weekly growth data point"""
    week_start: str
    week_end: str
    week_number: int
    audience_size: int
    new_listeners: int
    churned_listeners: int
    net_growth: int


class AudienceGrowthResponse(BaseModel):
    """Audience growth over time"""
    current_audience_size: int
    growth_data: List[GrowthDataPoint]
    growth_rate_percentage: float
    net_new_listeners: int
    average_daily_growth: float
    trend: str


class CohortRetention(BaseModel):
    """Cohort retention data"""
    period: str
    retention_rate: float
    listeners_remaining: int


class RetentionBySource(BaseModel):
    """Retention by acquisition source"""
    source: str
    initial_listeners: int
    retained: int
    retention_rate: float


class RetentionMetricsResponse(BaseModel):
    """Listener retention metrics"""
    overall_retention_rate: float
    cohort_retention: List[CohortRetention]
    retention_by_source: List[RetentionBySource]
    average_session_duration: float
    repeat_listener_rate: float
    insights: List[str]


class ContentStrategy(BaseModel):
    """Recommended content strategy"""
    posting_frequency: str
    best_platforms: List[str]
    content_types: List[str]
    optimal_timing: str


class GrowthStrategy(BaseModel):
    """Recommended growth strategy"""
    focus_areas: List[str]
    target_demographics: List[AgeDistribution]
    geographic_targets: List[str]


class AudienceInsightsResponse(BaseModel):
    """AI-powered audience insights"""
    insights: List[str]
    recommendations: List[str]
    content_strategy: ContentStrategy
    growth_strategy: GrowthStrategy
