"""
Track schemas - Pydantic models for track data validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.track import TrackStatus, TrackVisibility


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class TrackUploadMetadata(BaseModel):
    """Metadata provided during track upload"""
    title: str = Field(..., min_length=1, max_length=255)
    artist_name: Optional[str] = None  # Auto-filled from user profile
    album: Optional[str] = Field(None, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    sub_genre: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_explicit: bool = False


class TrackUpdate(BaseModel):
    """Track update request"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    artist_name: Optional[str] = Field(None, max_length=255)
    album: Optional[str] = Field(None, max_length=255)
    
    genre: Optional[str] = Field(None, max_length=100)
    sub_genre: Optional[str] = Field(None, max_length=100)
    mood_tags: Optional[List[str]] = None
    language: Optional[str] = Field(None, max_length=50)
    
    bpm: Optional[int] = Field(None, ge=20, le=300)
    key: Optional[str] = Field(None, max_length=10)
    
    description: Optional[str] = None
    lyrics: Optional[str] = None
    release_date: Optional[datetime] = None
    
    isrc: Optional[str] = Field(None, max_length=50)
    copyright_info: Optional[str] = Field(None, max_length=500)
    license_type: Optional[str] = Field(None, max_length=100)
    
    featuring_artists: Optional[List[str]] = None
    producers: Optional[List[str]] = None
    
    status: Optional[TrackStatus] = None
    visibility: Optional[TrackVisibility] = None
    
    is_explicit: Optional[bool] = None
    is_downloadable: Optional[bool] = None
    allow_comments: Optional[bool] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class TrackResponse(BaseModel):
    """Track response"""
    id: str
    user_id: str
    
    # Basic info
    title: str
    artist_name: str
    album: Optional[str]
    
    # Genre & classification
    genre: Optional[str]
    sub_genre: Optional[str]
    mood_tags: Optional[List[str]]
    language: Optional[str]
    
    # Technical details
    duration: Optional[int]
    bpm: Optional[int]
    key: Optional[str]
    bitrate: Optional[int]
    sample_rate: Optional[int]
    
    # Files
    audio_url: Optional[str]
    cover_art_url: Optional[str]
    waveform_url: Optional[str]
    
    # Metadata
    description: Optional[str]
    lyrics: Optional[str]
    release_date: Optional[datetime]
    
    # Licensing
    isrc: Optional[str]
    copyright_info: Optional[str]
    license_type: Optional[str]
    
    # Collaboration
    featuring_artists: Optional[List[str]]
    producers: Optional[List[str]]
    
    # Status
    status: TrackStatus
    visibility: TrackVisibility
    
    # Flags
    is_explicit: bool
    is_downloadable: bool
    allow_comments: bool
    
    # AI Analysis
    ai_detected_genre: Optional[str]
    ai_detected_mood: Optional[List[str]]
    ai_detected_bpm: Optional[int]
    ai_detected_key: Optional[str]
    ai_content_warning: Optional[str]
    
    # Stats
    play_count: int
    like_count: int
    comment_count: int
    download_count: int
    share_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TrackListItem(BaseModel):
    """Track list item (simplified for lists)"""
    id: str
    title: str
    artist_name: str
    genre: Optional[str]
    duration: Optional[int]
    cover_art_url: Optional[str]
    status: TrackStatus
    play_count: int
    like_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TrackUploadResponse(BaseModel):
    """Response after track upload"""
    track_id: str
    message: str
    audio_url: str
    duration: Optional[int]
    bitrate: Optional[int]
    sample_rate: Optional[int]
