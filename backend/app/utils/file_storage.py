"""
File Storage Service - Handle file uploads (local and cloud)
Supports: Local storage (development), Cloudflare R2 (production)
"""
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io

from app.core.config import settings


class FileStorageService:
    """File storage service for handling uploads"""
    
    # Allowed file extensions
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
    ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    
    # File size limits (in bytes)
    MAX_IMAGE_SIZE = settings.MAX_IMAGE_FILE_SIZE_MB * 1024 * 1024
    MAX_AUDIO_SIZE = settings.MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024
    MAX_VIDEO_SIZE = settings.MAX_VIDEO_FILE_SIZE_MB * 1024 * 1024
    
    # Local storage paths
    UPLOAD_DIR = Path("uploads")
    AVATARS_DIR = UPLOAD_DIR / "avatars"
    COVERS_DIR = UPLOAD_DIR / "covers"
    AUDIO_DIR = UPLOAD_DIR / "audio"
    VIDEO_DIR = UPLOAD_DIR / "video"
    
    def __init__(self):
        """Initialize file storage service"""
        # Create upload directories if they don't exist
        self.AVATARS_DIR.mkdir(parents=True, exist_ok=True)
        self.COVERS_DIR.mkdir(parents=True, exist_ok=True)
        self.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        self.VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
        """Check if file extension is allowed"""
        ext = Path(filename).suffix.lower()
        return ext in allowed_extensions
    
    @staticmethod
    def validate_file_size(file_size: int, max_size: int) -> bool:
        """Check if file size is within limit"""
        return file_size <= max_size
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generate unique filename to prevent conflicts"""
        ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{ext}"
    
    async def upload_avatar(self, file: UploadFile, user_id: str) -> str:
        """
        Upload user avatar image
        
        Args:
            file: Uploaded file
            user_id: User ID
            
        Returns:
            File URL/path
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate extension
        if not self.validate_file_extension(file.filename, self.ALLOWED_IMAGE_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(self.ALLOWED_IMAGE_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        if not self.validate_file_size(file_size, self.MAX_IMAGE_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MAX_IMAGE_FILE_SIZE_MB}MB"
            )
        
        # Process image (resize, optimize)
        try:
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
                image = background
            
            # Resize to 400x400 (avatar size)
            image.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Generate filename
            filename = f"{user_id}_avatar{Path(file.filename).suffix.lower()}"
            filepath = self.AVATARS_DIR / filename
            
            # Save optimized image
            image.save(filepath, quality=85, optimize=True)
            
            # Return URL (relative path for now)
            return f"/uploads/avatars/{filename}"
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process image: {str(e)}"
            )
    
    async def upload_cover_photo(self, file: UploadFile, user_id: str) -> str:
        """
        Upload profile cover photo
        
        Args:
            file: Uploaded file
            user_id: User ID
            
        Returns:
            File URL/path
        """
        # Validate extension
        if not self.validate_file_extension(file.filename, self.ALLOWED_IMAGE_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(self.ALLOWED_IMAGE_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        if not self.validate_file_size(file_size, self.MAX_IMAGE_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MAX_IMAGE_FILE_SIZE_MB}MB"
            )
        
        # Process image
        try:
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
                image = background
            
            # Resize to 1200x400 (cover photo size)
            # Maintain aspect ratio, crop to fit
            target_ratio = 1200 / 400
            img_ratio = image.width / image.height
            
            if img_ratio > target_ratio:
                # Image is wider, crop width
                new_width = int(image.height * target_ratio)
                left = (image.width - new_width) // 2
                image = image.crop((left, 0, left + new_width, image.height))
            else:
                # Image is taller, crop height
                new_height = int(image.width / target_ratio)
                top = (image.height - new_height) // 2
                image = image.crop((0, top, image.width, top + new_height))
            
            # Resize to target dimensions
            image = image.resize((1200, 400), Image.Resampling.LANCZOS)
            
            # Generate filename
            filename = f"{user_id}_cover{Path(file.filename).suffix.lower()}"
            filepath = self.COVERS_DIR / filename
            
            # Save optimized image
            image.save(filepath, quality=85, optimize=True)
            
            # Return URL
            return f"/uploads/covers/{filename}"
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process image: {str(e)}"
            )
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            file_url: File URL/path
            
        Returns:
            True if deleted successfully
        """
        try:
            # Convert URL to file path
            if file_url.startswith("/uploads/"):
                filepath = Path(file_url[1:])  # Remove leading slash
                if filepath.exists():
                    filepath.unlink()
                    return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_file_info(file: UploadFile) -> dict:
        """
        Get file information
        
        Args:
            file: Uploaded file
            
        Returns:
            File information dict
        """
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, 'size') else None,
        }


    async def upload_audio(self, file: UploadFile, user_id: str, track_id: str) -> Tuple[str, dict]:
        """
        Upload audio file
        
        Args:
            file: Uploaded file
            user_id: User ID
            track_id: Track ID
            
        Returns:
            Tuple of (file_url, metadata_dict)
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate extension
        if not self.validate_file_extension(file.filename, self.ALLOWED_AUDIO_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(self.ALLOWED_AUDIO_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        if not self.validate_file_size(file_size, self.MAX_AUDIO_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MAX_AUDIO_FILE_SIZE_MB}MB"
            )
        
        try:
            # Generate filename
            ext = Path(file.filename).suffix.lower()
            filename = f"{track_id}{ext}"
            filepath = self.AUDIO_DIR / filename
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(content)
            
            # Extract metadata using mutagen
            metadata = self._extract_audio_metadata(filepath)
            
            # Return URL
            return f"/uploads/audio/{filename}", metadata
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process audio file: {str(e)}"
            )
    
    @staticmethod
    def _extract_audio_metadata(filepath: Path) -> dict:
        """
        Extract metadata from audio file
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Dictionary with audio metadata
        """
        try:
            from mutagen import File as MutagenFile
            
            audio = MutagenFile(str(filepath))
            
            if audio is None:
                return {}
            
            metadata = {
                "duration": int(audio.info.length) if hasattr(audio.info, 'length') else None,
                "bitrate": int(audio.info.bitrate / 1000) if hasattr(audio.info, 'bitrate') else None,
                "sample_rate": audio.info.sample_rate if hasattr(audio.info, 'sample_rate') else None,
            }
            
            # Try to extract ID3 tags
            if hasattr(audio, 'tags') and audio.tags:
                tags = audio.tags
                
                # Try different tag formats (ID3, Vorbis, etc.)
                title = tags.get('TIT2') or tags.get('title') or tags.get('TITLE')
                artist = tags.get('TPE1') or tags.get('artist') or tags.get('ARTIST')
                album = tags.get('TALB') or tags.get('album') or tags.get('ALBUM')
                genre = tags.get('TCON') or tags.get('genre') or tags.get('GENRE')
                
                if title:
                    metadata['title'] = str(title[0]) if isinstance(title, list) else str(title)
                if artist:
                    metadata['artist'] = str(artist[0]) if isinstance(artist, list) else str(artist)
                if album:
                    metadata['album'] = str(album[0]) if isinstance(album, list) else str(album)
                if genre:
                    metadata['genre'] = str(genre[0]) if isinstance(genre, list) else str(genre)
            
            return metadata
            
        except ImportError:
            # Mutagen not installed, return basic info
            return {}
        except Exception:
            # Failed to extract metadata
            return {}
    
    async def upload_track_cover_art(self, file: UploadFile, track_id: str) -> str:
        """
        Upload cover art for a track
        
        Args:
            file: Uploaded image file
            track_id: Track ID
            
        Returns:
            File URL/path
        """
        # Validate extension
        if not self.validate_file_extension(file.filename, self.ALLOWED_IMAGE_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(self.ALLOWED_IMAGE_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        if not self.validate_file_size(file_size, self.MAX_IMAGE_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MAX_IMAGE_FILE_SIZE_MB}MB"
            )
        
        # Process image
        try:
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
                image = background
            
            # Resize to 800x800 (album cover size)
            image.thumbnail((800, 800), Image.Resampling.LANCZOS)
            
            # Generate filename
            filename = f"{track_id}_cover{Path(file.filename).suffix.lower()}"
            filepath = self.COVERS_DIR / filename
            
            # Save optimized image
            image.save(filepath, quality=90, optimize=True)
            
            # Return URL
            return f"/uploads/covers/{filename}"
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process image: {str(e)}"
            )
