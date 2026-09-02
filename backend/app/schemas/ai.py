"""
AI service schemas - Request/response models for AI endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class GenerateCaptionRequest(BaseModel):
    """Request to generate social media captions"""
    track_title: str = Field(..., description="Track title")
    artist_name: str = Field(..., description="Artist name")
    genre: Optional[str] = Field(None, description="Music genre")
    mood: Optional[str] = Field(None, description="Track mood/vibe")
    platform: str = Field("instagram", description="Social platform (instagram, twitter, tiktok, facebook)")


class GenerateHashtagsRequest(BaseModel):
    """Request to generate hashtags"""
    track_title: str = Field(..., description="Track title")
    artist_name: str = Field(..., description="Artist name")
    genre: Optional[str] = Field(None, description="Music genre")
    location: Optional[str] = Field(None, description="Location (e.g., 'Lagos, Nigeria')")


class GeneratePressReleaseRequest(BaseModel):
    """Request to generate press release"""
    track_title: str = Field(..., description="Track title")
    artist_name: str = Field(..., description="Artist name")
    artist_bio: Optional[str] = Field(None, description="Artist biography")
    track_description: Optional[str] = Field(None, description="Track description")
    genre: Optional[str] = Field(None, description="Music genre")
    release_date: Optional[str] = Field(None, description="Release date")


class SuggestPostingTimesRequest(BaseModel):
    """Request for posting time suggestions"""
    timezone: str = Field("Africa/Lagos", description="Timezone")
    target_audience: str = Field("Nigeria", description="Target audience location")


class GenerateBioRequest(BaseModel):
    """Request to generate artist bio"""
    artist_name: str = Field(..., description="Artist name")
    genre: Optional[str] = Field(None, description="Music genre")
    achievements: Optional[List[str]] = Field(None, description="List of achievements")
    style: str = Field("professional", description="Bio style (professional, casual)")


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class Caption(BaseModel):
    """Social media caption"""
    tone: str = Field(..., description="Caption tone/style")
    caption: str = Field(..., description="Caption text")


class GenerateCaptionResponse(BaseModel):
    """Response with generated captions"""
    captions: List[Caption] = Field(..., description="List of caption variations")
    track_title: str
    artist_name: str
    platform: str


class HashtagsResponse(BaseModel):
    """Response with generated hashtags"""
    genre: List[str] = Field(..., description="Genre-related hashtags")
    trending: List[str] = Field(..., description="Trending hashtags")
    location: List[str] = Field(..., description="Location hashtags")
    campaign: List[str] = Field(..., description="Campaign hashtags")


class PressReleaseResponse(BaseModel):
    """Response with press release"""
    press_release: str = Field(..., description="Full press release text")
    word_count: int = Field(..., description="Word count")


class PostingTimeSuggestion(BaseModel):
    """Posting time suggestion"""
    suggestion: str = Field(..., description="Full suggestion text")


class PostingTimesResponse(BaseModel):
    """Response with posting time suggestions"""
    suggestions: List[PostingTimeSuggestion] = Field(..., description="List of time suggestions")
    timezone: str
    target_audience: str


class BioResponse(BaseModel):
    """Response with generated bios"""
    short: str = Field(..., description="Short bio (50-75 words)")
    medium: str = Field(..., description="Medium bio (150-200 words)")
    detailed: str = Field(..., description="Detailed bio (300-400 words)")



# ============================================================================
# UNIFIED AI GENERATION SCHEMAS
# ============================================================================

class AIGenerateRequest(BaseModel):
    """Unified AI generation request"""
    request_type: str = Field(..., description="Type of content (title, description, caption, hashtags, etc.)")
    params: Dict = Field(..., description="Generation parameters")
    bypass_cache: bool = Field(False, description="Skip cache lookup")


class ResponseMetadata(BaseModel):
    """Response metadata"""
    provider: str = Field(..., description="AI provider used")
    model: str = Field(..., description="Model used")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    cached: bool = Field(..., description="Whether response was cached")


class QuotaInfo(BaseModel):
    """User quota information"""
    tier: str = Field(..., description="User tier (free/premium)")
    remaining: Optional[int] = Field(None, description="Remaining requests (None for premium)")
    reset_at: Optional[str] = Field(None, description="Quota reset time (None for premium)")


class AIGenerateResponse(BaseModel):
    """Unified AI generation response"""
    success: bool = Field(..., description="Whether generation succeeded")
    content: Dict = Field(..., description="Generated content")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    quota: Optional[QuotaInfo] = Field(None, description="Quota information")
