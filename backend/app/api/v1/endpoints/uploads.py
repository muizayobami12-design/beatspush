"""
File Upload API Endpoints
Handles audio, image, and file uploads to Cloudflare R2
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.r2_storage_service import get_r2_storage_service
from app.services.rate_limiter import RateLimiter, get_rate_limit_config
from app.core.config import settings
from redis import Redis

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize rate limiter
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
rate_limiter = RateLimiter(redis_client)


@router.post("/audio", response_model=dict)
async def upload_audio_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    track_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload audio file (MP3, WAV, FLAC, etc.)
    
    - **file**: Audio file to upload
    - **title**: Optional track title
    - **track_id**: Optional track ID
    
    Returns:
    - **file_id**: Unique file identifier
    - **public_url**: CDN URL for accessing the file
    - **metadata**: Audio metadata (duration, bitrate, etc.)
    """
    try:
        # Rate limiting (10 uploads per hour)
        limit_config = get_rate_limit_config("upload")
        allowed = await rate_limiter.is_allowed(
            identifier=str(current_user.id),
            action="upload",
            max_requests=limit_config["max_requests"],
            window_seconds=limit_config["window_seconds"]
        )
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Upload limit exceeded. Please try again later."
            )
        
        # Upload to R2
        storage_service = get_r2_storage_service()
        public_url, metadata = await storage_service.upload_audio(
            file=file,
            user_id=str(current_user.id),
            track_id=track_id
        )
        
        logger.info(f"User {current_user.id} uploaded audio: {public_url}")
        
        return {
            "success": True,
            "file_id": metadata.get("track_id"),
            "public_url": public_url,
            "metadata": {
                "duration": metadata.get("duration"),
                "bitrate": metadata.get("bitrate"),
                "sample_rate": metadata.get("sample_rate"),
                "file_size": metadata.get("file_size"),
                "original_filename": metadata.get("original_filename"),
                "title": title or metadata.get("title")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/image", response_model=dict)
async def upload_image_file(
    file: UploadFile = File(...),
    image_type: str = Form("general"),  # avatar, cover, beat_cover, general
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload image file (JPEG, PNG, WebP, etc.)
    
    - **file**: Image file to upload
    - **image_type**: Type of image (avatar, cover, beat_cover, general)
    
    Returns:
    - **public_url**: CDN URL for accessing the image
    - **dimensions**: Image dimensions (width x height)
    """
    try:
        # Rate limiting
        limit_config = get_rate_limit_config("upload")
        allowed = await rate_limiter.is_allowed(
            identifier=str(current_user.id),
            action="upload",
            max_requests=limit_config["max_requests"],
            window_seconds=limit_config["window_seconds"]
        )
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Upload limit exceeded. Please try again later."
            )
        
        # Upload to R2
        storage_service = get_r2_storage_service()
        
        # Choose upload method based on type
        if image_type == "avatar":
            public_url = await storage_service.upload_avatar(file, str(current_user.id))
            dimensions = "400x400"
        elif image_type == "cover":
            public_url = await storage_service.upload_cover_photo(file, str(current_user.id))
            dimensions = "1200x400"
        elif image_type == "beat_cover":
            public_url = await storage_service.upload_beat_cover(file, str(current_user.id))
            dimensions = "800x800"
        else:
            public_url = await storage_service.upload_image(file, str(current_user.id), image_type)
            dimensions = "auto"
        
        logger.info(f"User {current_user.id} uploaded image ({image_type}): {public_url}")
        
        return {
            "success": True,
            "public_url": public_url,
            "image_type": image_type,
            "dimensions": dimensions,
            "format": "webp"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.delete("/{file_url:path}")
async def delete_file(
    file_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file from storage
    
    - **file_url**: URL or path of file to delete
    
    Returns:
    - **success**: Whether deletion was successful
    """
    try:
        storage_service = get_r2_storage_service()
        
        # Only allow users to delete their own files
        # Extract user_id from URL and verify ownership
        if str(current_user.id) not in file_url:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own files"
            )
        
        success = await storage_service.delete_file(file_url)
        
        if success:
            logger.info(f"User {current_user.id} deleted file: {file_url}")
            return {"success": True, "message": "File deleted successfully"}
        else:
            return {"success": False, "message": "File not found or already deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(e)}"
        )


@router.get("/stats")
async def get_upload_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get upload statistics for current user
    
    Returns:
    - **uploads_today**: Number of uploads today
    - **remaining**: Remaining uploads allowed
    - **storage_used**: Storage space used (if available)
    """
    try:
        # Get rate limit info
        limit_config = get_rate_limit_config("upload")
        remaining = await rate_limiter.get_remaining(
            identifier=str(current_user.id),
            action="upload",
            max_requests=limit_config["max_requests"],
            window_seconds=limit_config["window_seconds"]
        )
        
        return {
            "uploads_remaining": remaining,
            "max_uploads_per_hour": limit_config["max_requests"],
            "window_seconds": limit_config["window_seconds"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get upload stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve upload statistics"
        )


@router.get("/health")
async def storage_health_check():
    """
    Check if storage service is healthy
    
    Returns:
    - **status**: Service status
    - **storage_type**: "r2" or "local"
    """
    try:
        storage_service = get_r2_storage_service()
        
        return {
            "status": "healthy",
            "storage_type": "r2" if storage_service.use_r2 else "local",
            "r2_configured": storage_service.use_r2
        }
        
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e)
        }
