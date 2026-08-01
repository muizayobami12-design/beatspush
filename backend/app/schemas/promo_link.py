"""
Promo Link Schemas
Task 3.5: Promo Link Generator
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


# ================== REQUEST SCHEMAS ==================

class PromoLinkCreateRequest(BaseModel):
    """Create promo link request"""
    track_id: str = Field(..., description="Track ID to create link for")
    title: Optional[str] = Field(None, description="Custom title (defaults to track title)")
    description: Optional[str] = Field(None, description="Link description")
    
    # Platform URLs
    spotify_url: Optional[str] = Field(None, description="Spotify track URL")
    apple_music_url: Optional[str] = Field(None, description="Apple Music URL")
    youtube_url: Optional[str] = Field(None, description="YouTube URL")
    tidal_url: Optional[str] = Field(None, description="Tidal URL")
    soundcloud_url: Optional[str] = Field(None, description="SoundCloud URL")
    audiomack_url: Optional[str] = Field(None, description="Audiomack URL")
    boomplay_url: Optional[str] = Field(None, description="Boomplay URL")
    deezer_url: Optional[str] = Field(None, description="Deezer URL")
    
    # Branding
    background_color: Optional[str] = Field("#000000", description="Background color hex")
    text_color: Optional[str] = Field("#FFFFFF", description="Text color hex")
    custom_domain: Optional[str] = Field(None, description="Custom domain (premium)")
    
    # UTM Parameters
    utm_source: Optional[str] = Field(None, description="UTM source")
    utm_medium: Optional[str] = Field(None, description="UTM medium")
    utm_campaign: Optional[str] = Field(None, description="UTM campaign")
    
    # Expiration
    expires_at: Optional[datetime] = Field(None, description="Link expiration date")


class PromoLinkUpdateRequest(BaseModel):
    """Update promo link request"""
    title: Optional[str] = None
    description: Optional[str] = None
    
    # Platform URLs
    spotify_url: Optional[str] = None
    apple_music_url: Optional[str] = None
    youtube_url: Optional[str] = None
    tidal_url: Optional[str] = None
    soundcloud_url: Optional[str] = None
    audiomack_url: Optional[str] = None
    boomplay_url: Optional[str] = None
    deezer_url: Optional[str] = None
    
    # Branding
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    custom_domain: Optional[str] = None
    
    # UTM Parameters
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    
    # Status
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class GeoRuleCreateRequest(BaseModel):
    """Create geo-targeting rule"""
    country_codes: List[str] = Field(..., description="List of country codes (e.g., ['NG', 'GH', 'KE'])")
    platform: str = Field(..., description="Platform to redirect to (spotify, apple_music, etc.)")
    priority: int = Field(0, description="Rule priority (higher = checked first)")
    fallback_url: Optional[str] = Field(None, description="Fallback URL if platform unavailable")


class GeoRuleUpdateRequest(BaseModel):
    """Update geo-targeting rule"""
    country_codes: Optional[List[str]] = None
    platform: Optional[str] = None
    priority: Optional[int] = None
    fallback_url: Optional[str] = None
    is_active: Optional[bool] = None


# ================== RESPONSE SCHEMAS ==================

class PromoLinkResponse(BaseModel):
    """Promo link response"""
    id: str
    user_id: str
    track_id: str
    short_code: str
    title: str
    description: Optional[str]
    
    # Platform URLs
    spotify_url: Optional[str]
    apple_music_url: Optional[str]
    youtube_url: Optional[str]
    tidal_url: Optional[str]
    soundcloud_url: Optional[str]
    audiomack_url: Optional[str]
    boomplay_url: Optional[str]
    deezer_url: Optional[str]
    
    # Branding
    cover_image_url: Optional[str]
    background_color: str
    text_color: str
    custom_domain: Optional[str]
    
    # Analytics
    total_clicks: int
    unique_clicks: int
    
    # UTM Parameters
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]
    
    # Status
    is_active: bool
    expires_at: Optional[datetime]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # URLs
    short_url: str = Field(..., description="Short URL (beatpush.to/xxx)")
    full_url: str = Field(..., description="Full landing page URL")
    qr_code_url: Optional[str] = Field(None, description="QR code image URL")
    
    class Config:
        from_attributes = True


class PromoLinkDetailResponse(PromoLinkResponse):
    """Detailed promo link with track info"""
    track_title: str
    track_artist: str
    track_cover_url: Optional[str]
    
    # Platform counts
    platform_clicks: Dict[str, int] = Field(default_factory=dict, description="Clicks per platform")
    
    # Geographic breakdown
    country_clicks: Dict[str, int] = Field(default_factory=dict, description="Clicks per country")
    
    # Recent activity
    recent_clicks: List[Dict[str, Any]] = Field(default_factory=list, description="Recent 10 clicks")


class PromoLinkListResponse(BaseModel):
    """List of promo links with pagination"""
    links: List[PromoLinkResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class LinkClickResponse(BaseModel):
    """Link click analytics response"""
    id: str
    promo_link_id: str
    platform: str
    country: Optional[str]
    region: Optional[str]
    city: Optional[str]
    device_type: Optional[str]
    os: Optional[str]
    browser: Optional[str]
    referrer: Optional[str]
    is_unique_click: bool
    clicked_at: datetime
    
    class Config:
        from_attributes = True


class LinkAnalyticsResponse(BaseModel):
    """Comprehensive link analytics"""
    promo_link_id: str
    short_code: str
    
    # Overall stats
    total_clicks: int
    unique_clicks: int
    conversion_rate: float = Field(..., description="Unique clicks / total clicks")
    
    # Platform breakdown
    platform_stats: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Stats per platform {platform: {clicks, unique_clicks, percentage}}"
    )
    
    # Geographic breakdown
    country_stats: Dict[str, int] = Field(..., description="Clicks per country")
    city_stats: Dict[str, int] = Field(..., description="Top cities")
    
    # Device breakdown
    device_stats: Dict[str, int] = Field(..., description="Device types")
    os_stats: Dict[str, int] = Field(..., description="Operating systems")
    browser_stats: Dict[str, int] = Field(..., description="Browsers")
    
    # Time series (last 30 days)
    daily_clicks: List[Dict[str, Any]] = Field(..., description="Daily click counts")
    
    # Top referrers
    top_referrers: List[Dict[str, Any]] = Field(..., description="Top 10 referrers")


class GeoRuleResponse(BaseModel):
    """Geo rule response"""
    id: str
    promo_link_id: str
    country_codes: str
    platform: str
    priority: int
    fallback_url: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class QRCodeResponse(BaseModel):
    """QR code generation response"""
    promo_link_id: str
    qr_code_url: str
    qr_code_data: str = Field(..., description="Base64 encoded QR code image")


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    data: Optional[Dict[str, Any]] = None
