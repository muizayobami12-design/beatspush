"""
Profile endpoints - Extended profile management for each user type
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Union

from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.profile import ArtistProfile, DJProfile, ProducerProfile, FanProfile
from app.core.dependencies import get_current_user
from app.services.profile_service import ProfileService
from app.utils.file_storage import FileStorageService
from app.schemas.profile import (
    ArtistProfileUpdate,
    ArtistProfileResponse,
    DJProfileUpdate,
    DJProfileResponse,
    ProducerProfileUpdate,
    ProducerProfileResponse,
    FanProfileUpdate,
    FanProfileResponse
)
from app.schemas.user import MessageResponse

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get(
    "/me",
    response_model=Union[ArtistProfileResponse, DJProfileResponse, ProducerProfileResponse, FanProfileResponse]
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's extended profile
    
    **Requires:** Authentication
    
    **Returns:** Profile data based on user role (Artist/DJ/Producer/Fan)
    """
    return ProfileService.get_profile_response(db, current_user)


@router.get(
    "/{user_id}",
    response_model=Union[ArtistProfileResponse, DJProfileResponse, ProducerProfileResponse, FanProfileResponse]
)
async def get_public_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get any user's public profile
    
    **Public endpoint** - No authentication required
    
    **Returns:** Public profile data
    """
    return ProfileService.get_public_profile(db, user_id)


@router.put("/artist", response_model=ArtistProfileResponse)
async def update_artist_profile(
    profile_data: ArtistProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update artist profile
    
    **Requires:** Authentication + Artist role
    
    **Updatable Fields:**
    - Stage name, bio, genres
    - Music platform links (Spotify, Apple Music, SoundCloud, YouTube)
    - Social media handles
    - Record label, manager info
    """
    return ProfileService.update_artist_profile(db, current_user, profile_data)


@router.put("/dj", response_model=DJProfileResponse)
async def update_dj_profile(
    profile_data: DJProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update DJ profile
    
    **Requires:** Authentication + DJ role
    
    **Updatable Fields:**
    - DJ name, bio, genres, BPM range
    - Resident venues, radio shows
    - Equipment/setup description
    - Music platform links
    - Social media handles
    """
    return ProfileService.update_dj_profile(db, current_user, profile_data)


@router.put("/producer", response_model=ProducerProfileResponse)
async def update_producer_profile(
    profile_data: ProducerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update producer profile
    
    **Requires:** Authentication + Producer role
    
    **Updatable Fields:**
    - Producer name, bio, genres
    - Production style
    - DAW (Digital Audio Workstation)
    - Equipment, collaboration preferences
    - Music platform links
    - Social media handles
    """
    return ProfileService.update_producer_profile(db, current_user, profile_data)


@router.put("/fan", response_model=FanProfileResponse)
async def update_fan_profile(
    profile_data: FanProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update fan profile
    
    **Requires:** Authentication + Fan role
    
    **Updatable Fields:**
    - Display name, bio
    - Favorite genres, location
    - Social media handles
    """
    return ProfileService.update_fan_profile(db, current_user, profile_data)



@router.post("/avatar", response_model=MessageResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload profile avatar image
    
    **Requires:** Authentication
    
    **Accepted formats:** JPG, JPEG, PNG, GIF, WEBP  
    **Max size:** 10MB  
    **Output:** Resized to 400x400px
    
    **Returns:** Success message with avatar URL
    """
    # Upload file
    storage = FileStorageService()
    avatar_url = await storage.upload_avatar(file, current_user.id)
    
    # Update profile based on user role
    profile = ProfileService.get_or_create_profile(db, current_user)
    
    # Delete old avatar if exists
    if profile.avatar_url:
        storage.delete_file(profile.avatar_url)
    
    # Update avatar URL
    profile.avatar_url = avatar_url
    db.commit()
    
    return MessageResponse(
        message="Avatar uploaded successfully",
        success=True
    )


@router.post("/cover", response_model=MessageResponse)
async def upload_cover_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload profile cover photo
    
    **Requires:** Authentication
    
    **Accepted formats:** JPG, JPEG, PNG, GIF, WEBP  
    **Max size:** 10MB  
    **Output:** Resized to 1200x400px
    
    **Returns:** Success message with cover URL
    """
    # Upload file
    storage = FileStorageService()
    cover_url = await storage.upload_cover_photo(file, current_user.id)
    
    # Update profile based on user role
    profile = ProfileService.get_or_create_profile(db, current_user)
    
    # Delete old cover if exists
    if profile.cover_photo_url:
        storage.delete_file(profile.cover_photo_url)
    
    # Update cover URL
    profile.cover_photo_url = cover_url
    db.commit()
    
    return MessageResponse(
        message="Cover photo uploaded successfully",
        success=True
    )


@router.delete("/avatar", response_model=MessageResponse)
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete profile avatar
    
    **Requires:** Authentication
    
    **Returns:** Success message
    """
    profile = ProfileService.get_or_create_profile(db, current_user)
    
    if not profile.avatar_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No avatar to delete"
        )
    
    # Delete file
    storage = FileStorageService()
    storage.delete_file(profile.avatar_url)
    
    # Update profile
    profile.avatar_url = None
    db.commit()
    
    return MessageResponse(
        message="Avatar deleted successfully",
        success=True
    )


@router.delete("/cover", response_model=MessageResponse)
async def delete_cover_photo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete profile cover photo
    
    **Requires:** Authentication
    
    **Returns:** Success message
    """
    profile = ProfileService.get_or_create_profile(db, current_user)
    
    if not profile.cover_photo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cover photo to delete"
        )
    
    # Delete file
    storage = FileStorageService()
    storage.delete_file(profile.cover_photo_url)
    
    # Update profile
    profile.cover_photo_url = None
    db.commit()
    
    return MessageResponse(
        message="Cover photo deleted successfully",
        success=True
    )
