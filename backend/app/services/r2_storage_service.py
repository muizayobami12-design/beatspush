"""
Cloudflare R2 Storage Service
S3-compatible object storage for audio, images, and files
"""
import boto3
import uuid
import io
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class R2StorageService:
    """
    Cloudflare R2 Storage Service
    Uses S3-compatible API for file uploads
    """
    
    # Allowed file extensions
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
    ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    
    # File size limits (in bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB
    MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
    
    def __init__(self):
        """Initialize R2 storage service"""
        self.use_r2 = self._should_use_r2()
        
        if self.use_r2:
            try:
                # Initialize S3 client for R2
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
                    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                    config=Config(
                        signature_version='s3v4',
                        retries={'max_attempts': 3, 'mode': 'adaptive'}
                    )
                )
                
                # Test connection
                self._test_connection()
                
                logger.info("R2 Storage initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize R2: {e}")
                logger.warning("Falling back to local storage")
                self.use_r2 = False
        else:
            logger.info("Using local storage (R2 not configured)")
    
    def _should_use_r2(self) -> bool:
        """Check if R2 is configured and should be used"""
        return all([
            hasattr(settings, 'R2_ACCOUNT_ID') and settings.R2_ACCOUNT_ID,
            hasattr(settings, 'R2_ACCESS_KEY_ID') and settings.R2_ACCESS_KEY_ID,
            hasattr(settings, 'R2_SECRET_ACCESS_KEY') and settings.R2_SECRET_ACCESS_KEY,
            hasattr(settings, 'R2_BUCKET_AUDIO') and settings.R2_BUCKET_AUDIO,
        ])
    
    def _test_connection(self):
        """Test R2 connection by listing buckets"""
        try:
            self.s3_client.list_buckets()
        except Exception as e:
            raise Exception(f"R2 connection test failed: {e}")
    
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
    def generate_unique_filename(original_filename: str, user_id: str, prefix: str = "") -> str:
        """Generate unique filename for R2"""
        ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        
        if prefix:
            return f"{prefix}/{user_id}/{unique_id}{ext}"
        return f"{user_id}/{unique_id}{ext}"
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename"""
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'
    
    async def upload_to_r2(
        self,
        file_content: bytes,
        key: str,
        bucket: str,
        content_type: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Upload file to R2
        
        Args:
            file_content: File content as bytes
            key: Object key (path) in bucket
            bucket: Bucket name
            content_type: MIME type
            metadata: Optional metadata dict
            
        Returns:
            Public URL of uploaded file
        """
        try:
            # Prepare upload parameters
            upload_params = {
                'Bucket': bucket,
                'Key': key,
                'Body': file_content,
                'ContentType': content_type,
                'CacheControl': 'public, max-age=31536000, immutable',
            }
            
            # Add metadata if provided
            if metadata:
                upload_params['Metadata'] = {
                    k: str(v) for k, v in metadata.items()
                }
            
            # Upload to R2
            self.s3_client.put_object(**upload_params)
            
            # Generate public URL
            public_url = f"{settings.R2_PUBLIC_URL}/{key}"
            
            logger.info(f"Uploaded file to R2: {key}")
            return public_url
            
        except ClientError as e:
            logger.error(f"R2 upload failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def delete_from_r2(self, key: str, bucket: str) -> bool:
        """
        Delete file from R2
        
        Args:
            key: Object key
            bucket: Bucket name
            
        Returns:
            True if deleted successfully
        """
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"Deleted file from R2: {key}")
            return True
        except ClientError as e:
            logger.error(f"R2 delete failed: {e}")
            return False
    
    async def upload_audio(
        self,
        file: UploadFile,
        user_id: str,
        track_id: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """
        Upload audio file to R2
        
        Args:
            file: Uploaded audio file
            user_id: User ID
            track_id: Optional track ID
            
        Returns:
            Tuple of (public_url, metadata_dict)
        """
        # Validate extension
        if not self.validate_file_extension(file.filename, self.ALLOWED_AUDIO_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid audio type. Allowed: {', '.join(self.ALLOWED_AUDIO_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        if not self.validate_file_size(file_size, self.MAX_AUDIO_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {self.MAX_AUDIO_SIZE / (1024*1024)}MB"
            )
        
        # Generate key
        track_id = track_id or str(uuid.uuid4())
        key = self.generate_unique_filename(file.filename, user_id, prefix="audio")
        
        # Extract audio metadata
        metadata = self._extract_audio_metadata(io.BytesIO(content))
        metadata.update({
            'user_id': user_id,
            'track_id': track_id,
            'uploaded_at': datetime.utcnow().isoformat(),
            'file_size': str(file_size),
            'original_filename': file.filename
        })
        
        # Upload to R2
        if self.use_r2:
            bucket = settings.R2_BUCKET_AUDIO
            content_type = self._get_content_type(file.filename)
            public_url = await self.upload_to_r2(content, key, bucket, content_type, metadata)
        else:
            # Fallback to local storage
            from app.utils.file_storage import FileStorageService
            storage = FileStorageService()
            public_url, _ = await storage.upload_audio(file, user_id, track_id)
        
        return public_url, metadata
    
    async def upload_image(
        self,
        file: UploadFile,
        user_id: str,
        image_type: str = "general",
        resize: Optional[Tuple[int, int]] = None
    ) -> str:
        """
        Upload image file to R2
        
        Args:
            file: Uploaded image file
            user_id: User ID
            image_type: Type of image (avatar, cover, beat_cover, etc.)
            resize: Optional (width, height) tuple to resize
            
        Returns:
            Public URL of uploaded image
        """
        # Validate extension
        if not self.validate_file_extension(file.filename, self.ALLOWED_IMAGE_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed: {', '.join(self.ALLOWED_IMAGE_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size
        if not self.validate_file_size(file_size, self.MAX_IMAGE_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {self.MAX_IMAGE_SIZE / (1024*1024)}MB"
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
            
            # Resize if specified
            if resize:
                if image_type == "cover":
                    # For cover photos, crop to fit
                    target_ratio = resize[0] / resize[1]
                    img_ratio = image.width / image.height
                    
                    if img_ratio > target_ratio:
                        new_width = int(image.height * target_ratio)
                        left = (image.width - new_width) // 2
                        image = image.crop((left, 0, left + new_width, image.height))
                    else:
                        new_height = int(image.width / target_ratio)
                        top = (image.height - new_height) // 2
                        image = image.crop((0, top, image.width, top + new_height))
                    
                    image = image.resize(resize, Image.Resampling.LANCZOS)
                else:
                    # For other images, maintain aspect ratio
                    image.thumbnail(resize, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='WEBP', quality=85, optimize=True)
            processed_content = output.getvalue()
            
            # Generate key
            key = self.generate_unique_filename(file.filename, user_id, prefix="images")
            # Force .webp extension
            key = key.rsplit('.', 1)[0] + '.webp'
            
            # Metadata
            metadata = {
                'user_id': user_id,
                'image_type': image_type,
                'uploaded_at': datetime.utcnow().isoformat(),
                'original_filename': file.filename,
                'dimensions': f"{image.width}x{image.height}"
            }
            
            # Upload to R2
            if self.use_r2:
                bucket = settings.R2_BUCKET_IMAGES
                public_url = await self.upload_to_r2(
                    processed_content, key, bucket, 'image/webp', metadata
                )
            else:
                # Fallback to local storage
                from app.utils.file_storage import FileStorageService
                storage = FileStorageService()
                if image_type == "avatar":
                    public_url = await storage.upload_avatar(file, user_id)
                elif image_type == "cover":
                    public_url = await storage.upload_cover_photo(file, user_id)
                else:
                    public_url = await storage.upload_track_cover_art(file, user_id)
            
            return public_url
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process image: {str(e)}"
            )
    
    async def upload_avatar(self, file: UploadFile, user_id: str) -> str:
        """Upload user avatar (400x400)"""
        return await self.upload_image(file, user_id, "avatar", resize=(400, 400))
    
    async def upload_cover_photo(self, file: UploadFile, user_id: str) -> str:
        """Upload profile cover photo (1200x400)"""
        return await self.upload_image(file, user_id, "cover", resize=(1200, 400))
    
    async def upload_beat_cover(self, file: UploadFile, user_id: str) -> str:
        """Upload beat cover art (800x800)"""
        return await self.upload_image(file, user_id, "beat_cover", resize=(800, 800))
    
    @staticmethod
    def _extract_audio_metadata(file_stream: io.BytesIO) -> Dict:
        """
        Extract metadata from audio file
        
        Args:
            file_stream: Audio file stream
            
        Returns:
            Dictionary with audio metadata
        """
        try:
            from mutagen import File as MutagenFile
            
            audio = MutagenFile(file_stream)
            
            if audio is None:
                return {}
            
            metadata = {}
            
            # Duration and bitrate
            if hasattr(audio, 'info'):
                if hasattr(audio.info, 'length'):
                    metadata['duration'] = int(audio.info.length)
                if hasattr(audio.info, 'bitrate'):
                    metadata['bitrate'] = int(audio.info.bitrate / 1000)
                if hasattr(audio.info, 'sample_rate'):
                    metadata['sample_rate'] = audio.info.sample_rate
            
            # Tags
            if hasattr(audio, 'tags') and audio.tags:
                tags = audio.tags
                
                # Try different tag formats
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
            
        except Exception as e:
            logger.warning(f"Failed to extract audio metadata: {e}")
            return {}
    
    def get_public_url(self, key: str, bucket_type: str = "audio") -> str:
        """
        Get public URL for a file
        
        Args:
            key: Object key
            bucket_type: "audio" or "images"
            
        Returns:
            Public URL
        """
        if self.use_r2:
            return f"{settings.R2_PUBLIC_URL}/{key}"
        else:
            # Local storage URL
            return f"/uploads/{bucket_type}/{key}"
    
    async def delete_file(self, url: str) -> bool:
        """
        Delete file from R2 or local storage
        
        Args:
            url: File URL
            
        Returns:
            True if deleted successfully
        """
        if self.use_r2 and url.startswith(settings.R2_PUBLIC_URL):
            # Extract key from URL
            key = url.replace(f"{settings.R2_PUBLIC_URL}/", "")
            
            # Determine bucket
            if key.startswith("audio/"):
                bucket = settings.R2_BUCKET_AUDIO
            elif key.startswith("images/"):
                bucket = settings.R2_BUCKET_IMAGES
            else:
                logger.warning(f"Unknown bucket for key: {key}")
                return False
            
            return await self.delete_from_r2(key, bucket)
        else:
            # Local storage
            from app.utils.file_storage import FileStorageService
            storage = FileStorageService()
            return storage.delete_file(url)


# Singleton instance
_r2_storage_service = None

def get_r2_storage_service() -> R2StorageService:
    """Get R2 storage service singleton"""
    global _r2_storage_service
    if _r2_storage_service is None:
        _r2_storage_service = R2StorageService()
    return _r2_storage_service
