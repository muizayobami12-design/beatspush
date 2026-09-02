"""
AI Publishing Assistant Endpoints
ChatGPT-like interface for music publishing
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import json
import os
import uuid

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.ai_publishing_assistant import ai_assistant
from app.services.r2_storage_service import get_r2_storage_service


router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])


class ChatMessage(BaseModel):
    message: str
    context: dict = {}


class AnalyzeAudioRequest(BaseModel):
    file_path: str
    genre: Optional[str] = None


@router.post("/chat")
async def chat_with_ai(
    data: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI assistant (streaming responses)
    Like ChatGPT for music publishing
    """
    
    async def generate_response():
        """Stream AI responses"""
        try:
            async for chunk in ai_assistant.chat_response(
                user_message=data.message,
                context=data.context,
                db=db
            ):
                # Send as Server-Sent Events
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            
            # Send done signal
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream"
    )


@router.post("/analyze-audio")
async def analyze_audio(
    file: UploadFile = File(...),
    genre: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze audio file
    Returns BPM, key, mood, quality, etc.
    """
    
    # Save uploaded file temporarily
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    temp_path = os.path.join(temp_dir, f"{file_id}{file_extension}")
    
    try:
        # Save file
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Analyze audio
        analysis = await ai_assistant.analyze_audio(temp_path)
        
        # Detect genre if not provided
        if not genre:
            # Improved genre detection based on filename keywords
            filename_lower = file.filename.lower()
            
            genre_keywords = {
                "Afrobeat": ["afro", "naija", "amapiano", "gqom"],
                "Trap": ["trap", "808"],
                "Drill": ["drill", "uk drill"],
                "Dancehall": ["dancehall", "reggae", "caribbean"],
                "Hip Hop": ["hiphop", "hip-hop", "rap", "boom bap"],
                "R&B": ["r&b", "rnb", "soul"],
                "Electronic": ["electronic", "edm", "house", "techno", "synth"],
                "Lo-Fi": ["lofi", "lo-fi", "chill", "study"],
            }
            
            genre = "Hip Hop"  # Default fallback
            for detected_genre, keywords in genre_keywords.items():
                if any(kw in filename_lower for kw in keywords):
                    genre = detected_genre
                    break
        
        # Generate publishing draft
        title = await ai_assistant.generate_title(
            genre=genre,
            mood=analysis.get("mood", "Energetic")
        )
        
        description = await ai_assistant.generate_description(
            title=title,
            genre=genre,
            mood=analysis.get("mood", "Energetic"),
            bpm=analysis.get("bpm", 128),
            key=analysis.get("key", "C Minor")
        )
        
        tags = await ai_assistant.generate_tags(
            genre=genre,
            mood=analysis.get("mood", "Energetic"),
            bpm=analysis.get("bpm", 128)
        )
        
        price = await ai_assistant.suggest_price(
            genre=genre,
            quality=analysis.get("quality", "Good"),
            duration=analysis.get("duration", 180),
            bpm=analysis.get("bpm", 128)
        )
        
        social_captions = await ai_assistant.generate_social_captions(
            title=title,
            genre=genre,
            price=price
        )
        
        best_time = await ai_assistant.get_best_posting_time()
        
        return {
            "success": True,
            "file_id": file_id,
            "temp_path": temp_path,
            "filename": file.filename,
            "analysis": analysis,
            "detected_genre": genre,
            "draft": {
                "title": title,
                "description": description,
                "tags": tags,
                "price": price,
                "genre": genre,
                "social_captions": social_captions,
                "best_posting_time": best_time.isoformat(),
                "audio_file": temp_path
            }
        }
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze audio: {str(e)}"
        )


@router.post("/publish-draft")
async def publish_draft(
    draft: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publish beat from AI-generated draft
    One-click publishing!
    """
    
    try:
        # Import beat model
        from app.models.beat import Beat
        from datetime import datetime
        
        # Upload audio to storage
        audio_path = draft.get("audio_file")
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(
                status_code=400,
                detail="Audio file not found"
            )
        
        # Read file
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        # Upload to R2 (or local storage)
        filename = os.path.basename(audio_path)
        r2_storage = get_r2_storage_service()
        
        # Read file and create UploadFile-like object
        with open(audio_path, "rb") as f:
            file_content = f.read()
        
        # Create fake UploadFile for compatibility
        class FakeUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self._content = content
            
            async def read(self):
                return self._content
        
        fake_file = FakeUploadFile(filename, file_content)
        audio_url, metadata = await r2_storage.upload_audio(
            file=fake_file,
            user_id=str(current_user.id)
        )
        
        # Create beat record
        beat = Beat(
            id=str(uuid.uuid4()),
            producer_id=current_user.id,
            title=draft.get("title", "Untitled"),
            description=draft.get("description", ""),
            genre=draft.get("genre", "Hip Hop"),
            bpm=draft.get("bpm", 128),
            key=draft.get("key", ""),
            price=draft.get("price", 5000),
            audio_url=audio_url,
            tags=draft.get("tags", []),
            is_published=True,
            created_at=datetime.utcnow()
        )
        
        db.add(beat)
        db.commit()
        db.refresh(beat)
        
        # Clean up temp file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {
            "success": True,
            "message": "Beat published successfully! 🎉",
            "beat_id": beat.id,
            "beat_url": f"/beats/{beat.id}",
            "title": beat.title,
            "price": beat.price,
            "social_captions": draft.get("social_captions", {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish: {str(e)}"
        )


@router.get("/greeting")
async def get_greeting(
    current_user: User = Depends(get_current_user)
):
    """Get AI assistant greeting message"""
    return {
        "message": f"Hi {current_user.full_name}! 👋 I'm your AI publishing assistant. "
                  f"Upload a beat and I'll help you publish it in seconds! Just drag and "
                  f"drop your audio file to get started. 🎵",
        "tips": [
            "I can analyze your beat's BPM, key, and mood",
            "I'll generate title, description, and tags automatically",
            "I'll suggest the best price based on market analysis",
            "I'll create social media captions ready to post",
            "One click and your beat is published!"
        ]
    }
