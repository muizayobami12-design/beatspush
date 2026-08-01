"""
File Attachment Service - Handle message file attachments
Tasks 6.1-6.3: File validation, upload, and deletion for messaging
"""
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io
import uuid
from sqlalchemy.orm import Session

from app.utils.file_storage import FileStorageService
from app.models.messaging import MessageAttachment, Message
from app.schemas.messaging import AttachmentResponse


# Task 6.1: File validation configuration
ATTACHMENT_CONFIG = {
    "image": {
        "extensions": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
        "max_size_mb": 10,
        "mime_types": {"image/jpeg", "image/png", "image/gif", "image/webp"}
    },
    "audio": {
        "extensions": {".mp3", ".wav", ".m4a", ".ogg", ".flac"},
        "max_size_mb": 25,
        "mime_types": {"audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg", "audio/flac"}
    },
    "document": {
        "extensions": {".pdf", ".doc", ".docx", ".txt"},
        "max_size_mb": 10,
        "mime_types": {
            "application/pdf", 
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain"
        }
    },
    "voice_note": {
        "extensions": {".mp3", ".wav", ".m4a", ".ogg", ".webm"},
        "max_size_mb": 5,
        "mime_types": {"audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg", "audio/webm"}
    }
}


class FileAttachmentService:
    """Service for handling message file attachments"""
    
    # Attachment storage paths
    ATTACHMENTS_DIR = FileStorageService.UPLOAD_DIR / "messages"
    
    def __init__(self, db: Session):
        self.db = db
        self.storage = FileStorageService()
        
        # Create attachments directory
        self.ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # FILE VALIDATION (Task 6.1)
    # ========================================================================
    
    def validate_file_upload(
        self,
        file: UploadFile,
        file_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate file upload against type-specific rules
        
        Args:
            file: Uploaded file
            file_type: Type (image, audio, document, voice_note)
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        # Check if file type is supported
        if file_type not in ATTACHMENT_CONFIG:
            return False, f"Unsupported file type: {file_type}"
        
        config = ATTACHMENT_CONFIG[file_type]
        
        # Check file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in config["extensions"]:
            allowed = ", ".join(config["extensions"])
            return False, f"Invalid file extension for {file_type}. Allowed: {allowed}"
        
        # Check MIME type
        if file.content_type and file.content_type not in config["mime_types"]:
            return False, f"Invalid MIME type: {file.content_type}"
        
        # Check file size (if available)
        if hasattr(file, 'size') and file.size:
            max_size_bytes = config["max_size_mb"] * 1024 * 1024
            if file.size > max_size_bytes:
                return False, f"File too large. Max size: {config['max_size_mb']}MB"
        
        return True, None
    
    # ========================================================================
    # FILE UPLOAD (Task 6.2)
    # ========================================================================
    
    async def upload_message_attachment(
        self,
        file: UploadFile,
        message_id: str,
        file_type: str
    ) -> MessageAttachment:
        """
        Upload file attachment for a message
        
        Args:
            file: Uploaded file
            message_id: Message ID
            file_type: Type (image, audio, document, voice_note)
            
        Returns:
            MessageAttachment object
            
        Raises:
            HTTPException: If validation or upload fails
        """
        # Validate message exists
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Validate file
        is_valid, error_msg = self.validate_file_upload(file, file_type)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate size again with actual content
        config = ATTACHMENT_CONFIG[file_type]
        max_size_bytes = config["max_size_mb"] * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {config['max_size_mb']}MB"
            )
        
        try:
            # Generate unique filename and storage path
            ext = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{ext}"
            message_dir = self.ATTACHMENTS_DIR / message_id
            message_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = message_dir / unique_filename
            storage_url = f"/uploads/messages/{message_id}/{unique_filename}"
            
            # Extract metadata based on file type
            width = None
            height = None
            duration = None
            thumbnail_url = None
            
            if file_type == "image":
                # Process image and create thumbnail
                width, height, thumbnail_url = await self._process_image(
                    content, message_id, unique_filename, filepath
                )
            elif file_type in ["audio", "voice_note"]:
                # Extract audio duration
                duration = self._extract_audio_duration(content, ext)
                # Save audio file
                with open(filepath, 'wb') as f:
                    f.write(content)
            else:
                # Save document as-is
                with open(filepath, 'wb') as f:
                    f.write(content)
            
            # Create attachment record
            attachment = MessageAttachment(
                id=str(uuid.uuid4()),
                message_id=message_id,
                file_type=file_type,
                original_filename=file.filename,
                storage_url=storage_url,
                file_size=file_size,
                mime_type=file.content_type,
                duration=duration,
                width=width,
                height=height,
                thumbnail_url=thumbnail_url
            )
            
            self.db.add(attachment)
            self.db.commit()
            self.db.refresh(attachment)
            
            return attachment
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload attachment: {str(e)}"
            )
    
    async def _process_image(
        self,
        content: bytes,
        message_id: str,
        unique_filename: str,
        filepath: Path
    ) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Process image: extract dimensions and create thumbnail
        
        Args:
            content: Image content bytes
            message_id: Message ID
            unique_filename: Unique filename
            filepath: Full file path
            
        Returns:
            Tuple of (width, height, thumbnail_url)
        """
        try:
            image = Image.open(io.BytesIO(content))
            
            # Get original dimensions
            width, height = image.size
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if 'A' in image.mode:
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            
            # Save full image (optimized)
            image.save(filepath, quality=85, optimize=True)
            
            # Create thumbnail (200x200, maintain aspect ratio)
            thumbnail = image.copy()
            thumbnail.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Generate thumbnail filename
            thumbnail_filename = f"thumb_{unique_filename}"
            thumbnail_path = filepath.parent / thumbnail_filename
            thumbnail.save(thumbnail_path, quality=75, optimize=True)
            
            thumbnail_url = f"/uploads/messages/{message_id}/{thumbnail_filename}"
            
            return width, height, thumbnail_url
            
        except Exception:
            # If image processing fails, save as-is
            with open(filepath, 'wb') as f:
                f.write(content)
            return None, None, None
    
    def _extract_audio_duration(
        self,
        content: bytes,
        ext: str
    ) -> Optional[int]:
        """
        Extract audio duration in seconds
        
        Args:
            content: Audio content bytes
            ext: File extension
            
        Returns:
            Duration in seconds or None
        """
        try:
            from mutagen import File as MutagenFile
            import tempfile
            
            # Save to temp file for mutagen to read
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            try:
                audio = MutagenFile(temp_path)
                if audio and hasattr(audio.info, 'length'):
                    duration = int(audio.info.length)
                    return duration
            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)
            
        except (ImportError, Exception):
            pass
        
        return None
    
    # ========================================================================
    # FILE DELETION (Task 6.3)
    # ========================================================================
    
    def delete_message_attachment(
        self,
        attachment_id: str
    ) -> bool:
        """
        Delete attachment from storage and database
        
        Args:
            attachment_id: Attachment ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            HTTPException: If attachment not found
        """
        attachment = (
            self.db.query(MessageAttachment)
            .filter(MessageAttachment.id == attachment_id)
            .first()
        )
        
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        try:
            # Delete main file
            if attachment.storage_url:
                self._delete_file_from_path(attachment.storage_url)
            
            # Delete thumbnail if exists
            if attachment.thumbnail_url:
                self._delete_file_from_path(attachment.thumbnail_url)
            
            # Delete from database
            self.db.delete(attachment)
            self.db.commit()
            
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete attachment: {str(e)}"
            )
    
    def _delete_file_from_path(self, file_url: str) -> bool:
        """
        Delete file from storage using URL
        
        Args:
            file_url: File URL path
            
        Returns:
            True if deleted
        """
        try:
            if file_url.startswith("/uploads/"):
                filepath = Path(file_url[1:])  # Remove leading slash
                if filepath.exists():
                    filepath.unlink()
                    return True
        except Exception:
            pass
        return False
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def get_attachment(
        self,
        attachment_id: str
    ) -> MessageAttachment:
        """
        Get attachment by ID
        
        Args:
            attachment_id: Attachment ID
            
        Returns:
            MessageAttachment object
            
        Raises:
            HTTPException: If not found
        """
        attachment = (
            self.db.query(MessageAttachment)
            .filter(MessageAttachment.id == attachment_id)
            .first()
        )
        
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        return attachment
    
    def build_attachment_response(
        self,
        attachment: MessageAttachment
    ) -> AttachmentResponse:
        """
        Build attachment response schema
        
        Args:
            attachment: MessageAttachment object
            
        Returns:
            AttachmentResponse schema
        """
        return AttachmentResponse(
            id=attachment.id,
            file_type=attachment.file_type,
            original_filename=attachment.original_filename,
            storage_url=attachment.storage_url,
            file_size=attachment.file_size,
            mime_type=attachment.mime_type,
            duration=attachment.duration,
            width=attachment.width,
            height=attachment.height,
            thumbnail_url=attachment.thumbnail_url,
            created_at=attachment.created_at
        )
