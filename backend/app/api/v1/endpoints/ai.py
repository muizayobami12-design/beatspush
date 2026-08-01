"""
AI endpoints - AI-powered content generation for music promotion
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.ai.ai_service import AIService
from app.schemas.ai import (
    GenerateCaptionRequest,
    GenerateCaptionResponse,
    Caption,
    GenerateHashtagsRequest,
    HashtagsResponse,
    GeneratePressReleaseRequest,
    PressReleaseResponse,
    SuggestPostingTimesRequest,
    PostingTimesResponse,
    PostingTimeSuggestion,
    GenerateBioRequest,
    BioResponse
)

router = APIRouter(prefix="/ai", tags=["AI Content Generation"])


@router.post("/generate-captions", response_model=GenerateCaptionResponse)
async def generate_captions(
    request: GenerateCaptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate social media captions for a track
    
    **Requires:** Authentication
    
    **Generates 5 caption variations:**
    1. **Hype/Energetic** - Get people excited
    2. **Emotional/Deep** - Connect emotionally  
    3. **Professional** - Industry-focused
    4. **Fun/Playful** - Light and entertaining
    5. **Mysterious/Teaser** - Build anticipation
    
    **Features:**
    - Platform-specific formatting
    - Emoji suggestions
    - Authentic to African music culture
    - Ready to copy-paste
    
    **Supported platforms:** Instagram, Twitter, TikTok, Facebook
    
    **Example:**
    ```json
    {
      "track_title": "Essence",
      "artist_name": "Wizkid",
      "genre": "Afrobeats",
      "mood": "romantic",
      "platform": "instagram"
    }
    ```
    """
    ai_service = AIService()
    
    captions = ai_service.generate_social_captions(
        track_title=request.track_title,
        artist_name=request.artist_name,
        genre=request.genre,
        mood=request.mood,
        platform=request.platform
    )
    
    return GenerateCaptionResponse(
        captions=[Caption(**c) for c in captions],
        track_title=request.track_title,
        artist_name=request.artist_name,
        platform=request.platform
    )


@router.post("/generate-hashtags", response_model=HashtagsResponse)
async def generate_hashtags(
    request: GenerateHashtagsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate relevant hashtags for music promotion
    
    **Requires:** Authentication
    
    **Generates 4 categories:**
    1. **Genre Tags** - Music genre and style
    2. **Trending Tags** - Popular culture hashtags
    3. **Location Tags** - City, country, regional
    4. **Campaign Tags** - Custom for this track
    
    **Features:**
    - Mix of popular and niche tags
    - Location-specific tags
    - Discoverable and relevant
    - Optimized for reach
    
    **Example:**
    ```json
    {
      "track_title": "Essence",
      "artist_name": "Wizkid",
      "genre": "Afrobeats",
      "location": "Lagos, Nigeria"
    }
    ```
    """
    ai_service = AIService()
    
    hashtags = ai_service.generate_hashtags(
        track_title=request.track_title,
        artist_name=request.artist_name,
        genre=request.genre,
        location=request.location
    )
    
    return HashtagsResponse(**hashtags)


@router.post("/generate-press-release", response_model=PressReleaseResponse)
async def generate_press_release(
    request: GeneratePressReleaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a professional press release for a track
    
    **Requires:** Authentication
    
    **Includes:**
    - Catchy headline
    - Opening paragraph (5 Ws)
    - Track details and highlights
    - Artist background
    - Authentic artist quote
    - Availability info
    - Professional formatting
    
    **Length:** 300-400 words  
    **Style:** AP format
    
    **Perfect for:**
    - Music blogs
    - Online magazines
    - Press kits
    - Email pitches
    
    **Example:**
    ```json
    {
      "track_title": "Essence",
      "artist_name": "Wizkid",
      "artist_bio": "Grammy-winning Nigerian artist...",
      "track_description": "A beautiful blend of Afrobeats and R&B...",
      "genre": "Afrobeats",
      "release_date": "2023-12-01"
    }
    ```
    """
    ai_service = AIService()
    
    press_release = ai_service.generate_press_release(
        track_title=request.track_title,
        artist_name=request.artist_name,
        artist_bio=request.artist_bio,
        track_description=request.track_description,
        genre=request.genre,
        release_date=request.release_date
    )
    
    word_count = len(press_release.split())
    
    return PressReleaseResponse(
        press_release=press_release,
        word_count=word_count
    )


@router.post("/suggest-posting-times", response_model=PostingTimesResponse)
async def suggest_posting_times(
    request: SuggestPostingTimesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get optimal posting times for social media
    
    **Requires:** Authentication
    
    **Provides 5 suggestions with:**
    - Day of week
    - Best time to post
    - Target platform
    - Reason for timing
    
    **Considers:**
    - African social media patterns
    - Peak engagement hours
    - Work/leisure schedules
    - Weekend vs weekday behavior
    
    **Example:**
    ```json
    {
      "timezone": "Africa/Lagos",
      "target_audience": "Nigeria"
    }
    ```
    
    **Supported timezones:**
    - Africa/Lagos (Nigeria)
    - Africa/Accra (Ghana)
    - Africa/Nairobi (Kenya)
    - Africa/Johannesburg (South Africa)
    """
    ai_service = AIService()
    
    times = ai_service.suggest_posting_times(
        timezone=request.timezone,
        target_audience=request.target_audience
    )
    
    return PostingTimesResponse(
        suggestions=[PostingTimeSuggestion(**t) for t in times],
        timezone=request.timezone,
        target_audience=request.target_audience
    )


@router.post("/generate-bio", response_model=BioResponse)
async def generate_bio(
    request: GenerateBioRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate artist biography in multiple lengths
    
    **Requires:** Authentication
    
    **Generates 3 versions:**
    1. **Short** (50-75 words) - Social media profiles
    2. **Medium** (150-200 words) - Press kits, websites
    3. **Detailed** (300-400 words) - Full press releases
    
    **Features:**
    - Professional yet personable
    - Celebrates African music culture
    - Includes genre and achievements
    - Shareable and engaging
    
    **Styles:** Professional, Casual
    
    **Example:**
    ```json
    {
      "artist_name": "Wizkid",
      "genre": "Afrobeats",
      "achievements": [
        "Grammy Award winner",
        "Multiple platinum certifications",
        "Global collaboration with Drake"
      ],
      "style": "professional"
    }
    ```
    """
    ai_service = AIService()
    
    bios = ai_service.generate_bio(
        artist_name=request.artist_name,
        genre=request.genre,
        achievements=request.achievements,
        style=request.style
    )
    
    return BioResponse(**bios)
