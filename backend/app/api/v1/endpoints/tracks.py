"""
Track endpoints - Music track upload and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.models.track import TrackStatus
from app.core.dependencies import get_current_user, get_optional_user
from app.services.track_service import TrackService
from app.schemas.track import (
    TrackUploadMetadata,
    TrackUpdate,
    TrackResponse,
    TrackListItem,
    TrackUploadResponse
)
from app.schemas.user import MessageResponse

router = APIRouter(prefix="/tracks", tags=["Tracks"])


@router.post("/upload", response_model=TrackUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_track(
    audio_file: UploadFile = File(..., description="Audio file (MP3, WAV, FLAC, M4A, OGG)"),
    title: str = Form(..., description="Track title"),
    artist_name: Optional[str] = Form(None, description="Artist name (auto-filled if not provided)"),
    album: Optional[str] = Form(None, description="Album name"),
    genre: Optional[str] = Form(None, description="Genre"),
    sub_genre: Optional[str] = Form(None, description="Sub-genre"),
    description: Optional[str] = Form(None, description="Track description"),
    is_explicit: bool = Form(False, description="Explicit content flag"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new music track
    
    **Requires:** Authentication
    
    **Accepted formats:** MP3, WAV, FLAC, M4A, OGG  
    **Max size:** 200MB
    
    **Features:**
    - Automatic metadata extraction
    - Duration, bitrate, sample rate detection
    - ID3 tag reading
    - File validation
    
    **Returns:** Track ID, audio URL, and extracted metadata
    """
    # Create metadata object
    metadata = TrackUploadMetadata(
        title=title,
        artist_name=artist_name,
        album=album,
        genre=genre,
        sub_genre=sub_genre,
        description=description,
        is_explicit=is_explicit
    )
    
    # Upload track
    return await TrackService.upload_track(db, current_user, audio_file, metadata)


@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Get track details
    
    **Public endpoint** for public tracks  
    **Authentication required** for private tracks
    
    **Returns:** Complete track information
    """
    return TrackService.get_track(db, track_id, current_user)


@router.put("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: str,
    update_data: TrackUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update track information
    
    **Requires:** Authentication + Track ownership
    
    **Updatable fields:**
    - Title, artist name, album
    - Genre, sub-genre, mood tags, language
    - BPM, key
    - Description, lyrics, release date
    - ISRC, copyright, license
    - Featured artists, producers
    - Status (draft/published/scheduled/archived)
    - Visibility (public/private/unlisted)
    - Flags (explicit, downloadable, comments)
    
    **Returns:** Updated track information
    """
    return TrackService.update_track(db, track_id, current_user, update_data)


@router.delete("/{track_id}", response_model=MessageResponse)
async def delete_track(
    track_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a track
    
    **Requires:** Authentication + Track ownership
    
    **Warning:** This action cannot be undone!  
    Deletes audio file, cover art, and all track data.
    
    **Returns:** Success message
    """
    return TrackService.delete_track(db, track_id, current_user)


@router.get("/", response_model=List[TrackListItem])
async def get_my_tracks(
    status: Optional[TrackStatus] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's tracks
    
    **Requires:** Authentication
    
    **Query Parameters:**
    - `status`: Filter by status (draft, published, scheduled, archived)
    - `limit`: Max results (default: 50)
    - `offset`: Results offset (default: 0)
    
    **Returns:** List of user's tracks
    """
    return TrackService.get_user_tracks(db, current_user.id, status, limit, offset)


@router.get("/user/{user_id}", response_model=List[TrackListItem])
async def get_user_tracks(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get tracks by user ID
    
    **Public endpoint** - Only returns published tracks
    
    **Query Parameters:**
    - `limit`: Max results (default: 50)
    - `offset`: Results offset (default: 0)
    
    **Returns:** List of user's published tracks
    """
    return TrackService.get_user_tracks(
        db,
        user_id,
        status=TrackStatus.PUBLISHED,
        limit=limit,
        offset=offset
    )


@router.post("/{track_id}/cover", response_model=MessageResponse)
async def upload_track_cover_art(
    track_id: str,
    cover_file: UploadFile = File(..., description="Cover art image (JPG, PNG, etc.)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload cover art for a track
    
    **Requires:** Authentication + Track ownership
    
    **Accepted formats:** JPG, JPEG, PNG, GIF, WEBP  
    **Max size:** 10MB  
    **Output:** Resized to 800x800px
    
    **Returns:** Success message with cover URL
    """
    return await TrackService.upload_cover_art(db, track_id, current_user, cover_file)
