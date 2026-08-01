"""
Track Service - Business logic for music track management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.track import Track, TrackStatus, TrackVisibility
from app.models.user import User
from app.schemas.track import (
    TrackUploadMetadata,
    TrackUpdate,
    TrackResponse,
    TrackListItem,
    TrackUploadResponse
)
from app.utils.file_storage import FileStorageService


class TrackService:
    """Track management service"""
    
    @staticmethod
    async def upload_track(
        db: Session,
        user: User,
        audio_file: UploadFile,
        metadata: TrackUploadMetadata
    ) -> TrackUploadResponse:
        """
        Upload a new track
        
        Args:
            db: Database session
            user: Current user
            audio_file: Audio file to upload
            metadata: Track metadata
            
        Returns:
            TrackUploadResponse with track info
        """
        # Generate track ID
        track_id = str(uuid.uuid4())
        
        # Upload audio file
        storage = FileStorageService()
        audio_url, audio_metadata = await storage.upload_audio(audio_file, user.id, track_id)
        
        # Get artist name from user profile or metadata
        artist_name = metadata.artist_name
        if not artist_name:
            # Try to get from profile
            if hasattr(user, 'artist_profile') and user.artist_profile:
                artist_name = user.artist_profile.stage_name or user.full_name
            elif hasattr(user, 'dj_profile') and user.dj_profile:
                artist_name = user.dj_profile.dj_name or user.full_name
            elif hasattr(user, 'producer_profile') and user.producer_profile:
                artist_name = user.producer_profile.producer_name or user.full_name
            else:
                artist_name = user.full_name or user.username or user.email
        
        # Create track
        track = Track(
            id=track_id,
            user_id=user.id,
            title=metadata.title,
            artist_name=artist_name,
            album=metadata.album,
            genre=metadata.genre or audio_metadata.get('genre'),
            sub_genre=metadata.sub_genre,
            description=metadata.description,
            is_explicit=metadata.is_explicit,
            audio_url=audio_url,
            duration=audio_metadata.get('duration'),
            bitrate=audio_metadata.get('bitrate'),
            sample_rate=audio_metadata.get('sample_rate'),
            status=TrackStatus.DRAFT,
            visibility=TrackVisibility.PRIVATE,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        db.add(track)
        db.commit()
        db.refresh(track)
        
        # TODO: Queue AI analysis task
        # analyze_track_with_ai.delay(track_id)
        
        return TrackUploadResponse(
            track_id=track.id,
            message="Track uploaded successfully",
            audio_url=track.audio_url,
            duration=track.duration,
            bitrate=track.bitrate,
            sample_rate=track.sample_rate
        )
    
    @staticmethod
    def get_track(db: Session, track_id: str, user: Optional[User] = None) -> TrackResponse:
        """
        Get a track by ID
        
        Args:
            db: Database session
            track_id: Track ID
            user: Optional current user (for permission check)
            
        Returns:
            TrackResponse
            
        Raises:
            HTTPException: If track not found or access denied
        """
        track = db.query(Track).filter(Track.id == track_id).first()
        
        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Track not found"
            )
        
        # Check access permission
        if track.visibility == TrackVisibility.PRIVATE:
            if not user or user.id != track.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to private track"
                )
        
        return TrackResponse.from_orm(track)
    
    @staticmethod
    def update_track(
        db: Session,
        track_id: str,
        user: User,
        update_data: TrackUpdate
    ) -> TrackResponse:
        """
        Update a track
        
        Args:
            db: Database session
            track_id: Track ID
            user: Current user
            update_data: Update data
            
        Returns:
            Updated TrackResponse
            
        Raises:
            HTTPException: If track not found or access denied
        """
        track = db.query(Track).filter(Track.id == track_id).first()
        
        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Track not found"
            )
        
        # Check ownership
        if track.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't own this track"
            )
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(track, field, value)
        
        # Update timestamp
        track.updated_at = datetime.utcnow()
        
        # If publishing, set published_at
        if update_data.status == TrackStatus.PUBLISHED and not track.published_at:
            track.published_at = datetime.utcnow()
        
        db.commit()
        db.refresh(track)
        
        return TrackResponse.from_orm(track)
    
    @staticmethod
    def delete_track(db: Session, track_id: str, user: User) -> dict:
        """
        Delete a track
        
        Args:
            db: Database session
            track_id: Track ID
            user: Current user
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If track not found or access denied
        """
        track = db.query(Track).filter(Track.id == track_id).first()
        
        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Track not found"
            )
        
        # Check ownership
        if track.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't own this track"
            )
        
        # Delete files
        storage = FileStorageService()
        if track.audio_url:
            storage.delete_file(track.audio_url)
        if track.cover_art_url:
            storage.delete_file(track.cover_art_url)
        
        # Delete from database
        db.delete(track)
        db.commit()
        
        return {"message": "Track deleted successfully", "success": True}
    
    @staticmethod
    def get_user_tracks(
        db: Session,
        user_id: str,
        status: Optional[TrackStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TrackListItem]:
        """
        Get tracks by user
        
        Args:
            db: Database session
            user_id: User ID
            status: Optional status filter
            limit: Max results
            offset: Results offset
            
        Returns:
            List of TrackListItem
        """
        query = db.query(Track).filter(Track.user_id == user_id)
        
        if status:
            query = query.filter(Track.status == status)
        
        query = query.order_by(Track.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        tracks = query.all()
        
        return [TrackListItem.from_orm(track) for track in tracks]
    
    @staticmethod
    async def upload_cover_art(
        db: Session,
        track_id: str,
        user: User,
        cover_file: UploadFile
    ) -> dict:
        """
        Upload cover art for a track
        
        Args:
            db: Database session
            track_id: Track ID
            user: Current user
            cover_file: Cover art image
            
        Returns:
            Success message with URL
        """
        track = db.query(Track).filter(Track.id == track_id).first()
        
        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Track not found"
            )
        
        # Check ownership
        if track.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't own this track"
            )
        
        # Upload cover art
        storage = FileStorageService()
        cover_url = await storage.upload_track_cover_art(cover_file, track_id)
        
        # Delete old cover if exists
        if track.cover_art_url:
            storage.delete_file(track.cover_art_url)
        
        # Update track
        track.cover_art_url = cover_url
        db.commit()
        
        return {
            "message": "Cover art uploaded successfully",
            "success": True,
            "cover_url": cover_url
        }
