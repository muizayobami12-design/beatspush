"""
Campaign schemas - Request/response models for Campaign Builder
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime, timezone


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class CampaignCreateRequest(BaseModel):
    """Campaign creation request"""
    track_id: str = Field(..., description="Track UUID")
    template_id: Optional[str] = Field(None, description="Template UUID (optional)")
    platforms: List[str] = Field(..., min_length=1, description="List of platform names (instagram, tiktok, twitter, facebook)")
    name: Optional[str] = Field(None, max_length=255, description="Campaign name (auto-generated if not provided)")
    
    @validator('platforms')
    def validate_platforms(cls, v):
        """Validate platform names"""
        valid_platforms = {'instagram', 'tiktok', 'twitter', 'facebook'}
        for platform in v:
            if platform.lower() not in valid_platforms:
                raise ValueError(f'Invalid platform: {platform}. Must be one of: {", ".join(valid_platforms)}')
        return [p.lower() for p in v]


class CampaignUpdateRequest(BaseModel):
    """Campaign update request"""
    name: Optional[str] = Field(None, max_length=255, description="Campaign name")
    platforms: Optional[List[str]] = Field(None, min_length=1, description="Updated platform list")
    scheduled_publish_time: Optional[datetime] = Field(None, description="Scheduled publish time")
    
    @validator('platforms')
    def validate_platforms(cls, v):
        """Validate platform names"""
        if v is None:
            return v
        valid_platforms = {'instagram', 'tiktok', 'twitter', 'facebook'}
        for platform in v:
            if platform.lower() not in valid_platforms:
                raise ValueError(f'Invalid platform: {platform}')
        return [p.lower() for p in v]


class CampaignScheduleRequest(BaseModel):
    """Schedule campaign request"""
    scheduled_publish_time: datetime = Field(..., description="Future datetime for campaign activation")
    
    @validator('scheduled_publish_time')
    def validate_future_time(cls, v):
        """Ensure scheduled time is in the future"""
        if v <= datetime.now(timezone.utc):
            raise ValueError('Scheduled time must be in the future')
        return v


class ContentGenerateRequest(BaseModel):
    """Generate content request"""
    platforms: List[str] = Field(..., min_length=1, description="Platforms to generate content for")
    
    @validator('platforms')
    def validate_platforms(cls, v):
        """Validate platform names"""
        valid_platforms = {'instagram', 'tiktok', 'twitter', 'facebook'}
        for platform in v:
            if platform.lower() not in valid_platforms:
                raise ValueError(f'Invalid platform: {platform}')
        return [p.lower() for p in v]


class ContentUpdateRequest(BaseModel):
    """Update platform content request"""
    caption: Optional[str] = Field(None, description="Updated caption text")
    hashtags: Optional[List[str]] = Field(None, description="Updated hashtags list")
    caption_tone: Optional[str] = Field(None, description="Caption tone (hype, emotional, professional, etc.)")



# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class CampaignContentResponse(BaseModel):
    """Campaign content response"""
    id: str
    campaign_id: str
    platform: str
    content_type: str
    caption: Optional[str]
    hashtags: Optional[List[str]]
    caption_tone: Optional[str]
    content_edited: bool
    posting_status: str
    engagement_count: int
    reach_count: int
    clicks_count: int
    shares_count: int
    content_generated_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CampaignResponse(BaseModel):
    """Campaign response"""
    id: str
    user_id: str
    track_id: str
    template_id: Optional[str]
    name: str
    status: str
    platforms: List[str]
    scheduled_publish_time: Optional[datetime]
    published_at: Optional[datetime]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    engagement_count: int
    reach_count: int
    clicks_count: int
    shares_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CampaignDetailResponse(CampaignResponse):
    """Detailed campaign response with content and related data"""
    track: Optional[Dict] = Field(None, description="Track basic info")
    template: Optional[Dict] = Field(None, description="Template basic info")
    content: List[CampaignContentResponse] = Field(default_factory=list, description="Platform content")


class CampaignListResponse(BaseModel):
    """Campaign list response with pagination"""
    campaigns: List[CampaignResponse]
    total: int
    limit: int
    offset: int


class CampaignTemplateResponse(BaseModel):
    """Campaign template response"""
    id: str
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    recommended_platforms: Optional[List[str]]
    usage_count: int
    is_active: bool
    
    class Config:
        from_attributes = True


class CampaignTemplateListResponse(BaseModel):
    """Template list response"""
    templates: List[CampaignTemplateResponse]


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
