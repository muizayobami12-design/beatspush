"""
Beat Schemas
Task 5.4: Beat Marketplace
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ================== REQUEST SCHEMAS ==================

class BeatCreateRequest(BaseModel):
    """Create beat listing"""
    title: str = Field(..., max_length=255, description="Beat title")
    description: Optional[str] = Field(None, description="Beat description")
    
    # Audio (URLs after upload)
    tagged_audio_url: str = Field(..., description="URL to tagged/preview audio")
    untagged_audio_url: Optional[str] = Field(None, description="URL to clean audio (for purchases)")
    cover_art_url: Optional[str] = Field(None, description="Cover art URL")
    
    # Technical
    bpm: Optional[int] = Field(None, ge=60, le=200, description="Beats per minute")
    musical_key: Optional[str] = Field(None, description="Musical key (e.g., C minor)")
    genre: Optional[str] = Field(None, description="Genre")
    mood: Optional[str] = Field(None, description="Mood/vibe")
    duration: Optional[int] = Field(None, description="Duration in seconds")
    
    # Pricing
    lease_price: Optional[float] = Field(None, ge=1.0, description="Lease price")
    exclusive_price: Optional[float] = Field(None, ge=100.0, description="Exclusive price")
    
    # License terms
    lease_terms: Optional[str] = Field(None, description="Lease license terms")
    exclusive_terms: Optional[str] = Field(None, description="Exclusive license terms")
    
    # Metadata
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class BeatUpdateRequest(BaseModel):
    """Update beat listing"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    cover_art_url: Optional[str] = None
    bpm: Optional[int] = Field(None, ge=60, le=200)
    musical_key: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    lease_price: Optional[float] = Field(None, ge=1.0)
    exclusive_price: Optional[float] = Field(None, ge=100.0)
    lease_terms: Optional[str] = None
    exclusive_terms: Optional[str] = None
    tags: Optional[str] = None
    is_available: Optional[bool] = None


class BeatPurchaseRequest(BaseModel):
    """Purchase beat"""
    license_type: str = Field(..., description="lease or exclusive")
    payment_method: str = Field("card", description="Payment method (simulated)")


class BeatPlayRequest(BaseModel):
    """Track beat play"""
    duration_played: Optional[int] = Field(None, description="Seconds played")
    completed: bool = Field(False, description="Whether play completed")


# ================== RESPONSE SCHEMAS ==================

class BeatResponse(BaseModel):
    """Beat response"""
    id: str
    producer_user_id: str
    producer_name: Optional[str] = None
    
    # Details
    title: str
    description: Optional[str]
    
    # Audio
    tagged_audio_url: str
    untagged_audio_url: Optional[str]  # Only visible to purchasers
    waveform_url: Optional[str]
    cover_art_url: Optional[str]
    
    # Technical
    bpm: Optional[int]
    musical_key: Optional[str]
    genre: Optional[str]
    mood: Optional[str]
    duration: Optional[int]
    
    # Pricing
    lease_price: Optional[float]
    exclusive_price: Optional[float]
    
    # License
    lease_terms: Optional[str]
    exclusive_terms: Optional[str]
    
    # Availability
    is_available: bool
    is_exclusive_sold: bool
    
    # Statistics
    play_count: int
    favorite_count: int
    purchase_count: int
    total_revenue: float
    
    # Platform
    platform_commission_rate: float
    
    # Metadata
    tags: Optional[str]
    
    # Status
    status: str
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    
    # User interaction
    is_favorited: bool = False
    is_purchased: bool = False
    
    class Config:
        from_attributes = True


class BeatListResponse(BaseModel):
    """List of beats"""
    beats: List[BeatResponse]
    total: int
    page: int
    page_size: int


class BeatPurchaseResponse(BaseModel):
    """Purchase response"""
    id: str
    beat_id: str
    beat_title: Optional[str] = None
    buyer_user_id: str
    producer_user_id: str
    producer_name: Optional[str] = None
    
    # Purchase
    license_type: str
    purchase_price: float
    currency: str
    
    # Fees
    platform_commission_rate: float
    platform_commission: float
    producer_payout: float
    
    # Payment
    payment_status: str
    
    # License
    license_certificate_url: Optional[str]
    license_key: Optional[str]
    
    # Download
    download_url: Optional[str]
    download_count: int
    download_limit: int
    
    # Status
    status: str
    
    # Timestamps
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BeatPurchaseListResponse(BaseModel):
    """List of purchases"""
    purchases: List[BeatPurchaseResponse]
    total: int
    page: int
    page_size: int


class BeatStatsResponse(BaseModel):
    """Beat statistics"""
    # As producer
    total_beats: int
    active_beats: int
    total_sales: int
    total_revenue: float
    lease_sales: int
    exclusive_sales: int
    
    # Popular beats
    top_beats: List[BeatResponse]
    
    # Recent activity
    recent_purchases: List[BeatPurchaseResponse]


class ProducerEarningsResponse(BaseModel):
    """Producer earnings dashboard"""
    total_earned: float
    pending_earnings: float
    withdrawn_earnings: float
    total_sales: int
    average_sale_price: float
    
    # Breakdown
    lease_revenue: float
    exclusive_revenue: float
    
    # Top selling beats
    top_sellers: List[dict]


class BeatAnalyticsResponse(BaseModel):
    """Beat analytics"""
    beat_id: str
    beat_title: str
    
    # Engagement
    total_plays: int
    unique_listeners: int
    total_favorites: int
    
    # Sales
    total_purchases: int
    lease_count: int
    exclusive_count: int
    total_revenue: float
    
    # Time series data
    plays_last_30_days: List[dict]
    revenue_last_30_days: List[dict]


class LicenseCertificateResponse(BaseModel):
    """License certificate"""
    purchase_id: str
    license_key: str
    license_type: str
    beat_title: str
    producer_name: str
    buyer_name: str
    certificate_text: str
    certificate_url: Optional[str]
    generated_at: datetime


class MessageResponse(BaseModel):
    """Generic message"""
    message: str
    data: Optional[dict] = None
