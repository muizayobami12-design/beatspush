"""
Profile schemas - Pydantic models for profile data validation
"""
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List


# ============================================================================
# ARTIST PROFILE SCHEMAS
# ============================================================================

class ArtistProfileUpdate(BaseModel):
    """Artist profile update request"""
    stage_name: Optional[str] = None
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    
    spotify_url: Optional[str] = None
    apple_music_url: Optional[str] = None
    soundcloud_url: Optional[str] = None
    youtube_url: Optional[str] = None
    
    instagram_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    facebook_url: Optional[str] = None
    
    record_label: Optional[str] = None
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None


class ArtistProfileResponse(BaseModel):
    """Artist profile response"""
    user_id: str
    stage_name: Optional[str]
    bio: Optional[str]
    genres: Optional[List[str]]
    
    spotify_url: Optional[str]
    apple_music_url: Optional[str]
    soundcloud_url: Optional[str]
    youtube_url: Optional[str]
    
    instagram_handle: Optional[str]
    twitter_handle: Optional[str]
    tiktok_handle: Optional[str]
    facebook_url: Optional[str]
    
    record_label: Optional[str]
    manager_name: Optional[str]
    manager_email: Optional[str]
    
    avatar_url: Optional[str]
    cover_photo_url: Optional[str]
    
    total_tracks: int
    total_plays: int
    total_followers: int
    
    class Config:
        from_attributes = True


# ============================================================================
# DJ PROFILE SCHEMAS
# ============================================================================

class DJProfileUpdate(BaseModel):
    """DJ profile update request"""
    dj_name: Optional[str] = None
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    bpm_range: Optional[str] = None
    
    resident_venues: Optional[List[str]] = None
    radio_shows: Optional[List[str]] = None
    equipment: Optional[str] = None
    
    mixcloud_url: Optional[str] = None
    soundcloud_url: Optional[str] = None
    youtube_url: Optional[str] = None
    spotify_url: Optional[str] = None
    
    instagram_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    facebook_url: Optional[str] = None


class DJProfileResponse(BaseModel):
    """DJ profile response"""
    user_id: str
    dj_name: Optional[str]
    bio: Optional[str]
    genres: Optional[List[str]]
    bpm_range: Optional[str]
    
    resident_venues: Optional[List[str]]
    radio_shows: Optional[List[str]]
    equipment: Optional[str]
    
    mixcloud_url: Optional[str]
    soundcloud_url: Optional[str]
    youtube_url: Optional[str]
    spotify_url: Optional[str]
    
    instagram_handle: Optional[str]
    twitter_handle: Optional[str]
    tiktok_handle: Optional[str]
    facebook_url: Optional[str]
    
    avatar_url: Optional[str]
    cover_photo_url: Optional[str]
    
    total_mixes: int
    total_plays: int
    total_followers: int
    
    class Config:
        from_attributes = True


# ============================================================================
# PRODUCER PROFILE SCHEMAS
# ============================================================================

class ProducerProfileUpdate(BaseModel):
    """Producer profile update request"""
    producer_name: Optional[str] = None
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    production_style: Optional[str] = None
    
    daw: Optional[str] = None
    equipment: Optional[str] = None
    collaboration_preferences: Optional[str] = None
    
    beatstars_url: Optional[str] = None
    soundcloud_url: Optional[str] = None
    youtube_url: Optional[str] = None
    spotify_url: Optional[str] = None
    
    instagram_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    facebook_url: Optional[str] = None


class ProducerProfileResponse(BaseModel):
    """Producer profile response"""
    user_id: str
    producer_name: Optional[str]
    bio: Optional[str]
    genres: Optional[List[str]]
    production_style: Optional[str]
    
    daw: Optional[str]
    equipment: Optional[str]
    collaboration_preferences: Optional[str]
    
    beatstars_url: Optional[str]
    soundcloud_url: Optional[str]
    youtube_url: Optional[str]
    spotify_url: Optional[str]
    
    instagram_handle: Optional[str]
    twitter_handle: Optional[str]
    tiktok_handle: Optional[str]
    facebook_url: Optional[str]
    
    avatar_url: Optional[str]
    cover_photo_url: Optional[str]
    
    total_beats: int
    total_sales: int
    total_collaborations: int
    total_followers: int
    
    class Config:
        from_attributes = True


# ============================================================================
# FAN PROFILE SCHEMAS
# ============================================================================

class FanProfileUpdate(BaseModel):
    """Fan profile update request"""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    favorite_genres: Optional[List[str]] = None
    location: Optional[str] = None
    
    instagram_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None


class FanProfileResponse(BaseModel):
    """Fan profile response"""
    user_id: str
    display_name: Optional[str]
    bio: Optional[str]
    favorite_genres: Optional[List[str]]
    location: Optional[str]
    
    favorite_artists: Optional[List[str]]
    favorite_djs: Optional[List[str]]
    favorite_producers: Optional[List[str]]
    
    instagram_handle: Optional[str]
    twitter_handle: Optional[str]
    tiktok_handle: Optional[str]
    
    avatar_url: Optional[str]
    cover_photo_url: Optional[str]
    
    total_playlists: int
    total_tips_given: int
    points_balance: int
    
    class Config:
        from_attributes = True
