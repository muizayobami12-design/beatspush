"""
Free AI Tools endpoints for the AI Promotion Platform

Provides:
- Beat audio analysis (quality, metadata, genre classification)
- Copyright scanning (fingerprinting, similarity detection)
- Caption generation (marketing copy for social media)
"""

import os
import tempfile
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.beat_analyzer_service import BeatAnalyzerService, AudioQualityLevel
from app.services.copyright_scanner_service import CopyrightScannerService
from app.services.caption_generator_service import (
    CaptionGeneratorService,
    CaptionOptions,
)
from app.ai.ai_service import AIService
from pydantic import BaseModel


router = APIRouter(prefix="/api/v1/free-tools", tags=["free-tools"])

# Initialize services
beat_analyzer = BeatAnalyzerService()
copyright_scanner = CopyrightScannerService()
ai_service = AIService()
caption_generator = CaptionGeneratorService(ai_service)


# Response schemas
class AudioQualityResponse(BaseModel):
    """Audio quality analysis response"""
    success: bool
    quality_level: str
    loudness_db: float
    dynamic_range_db: float
    signal_to_noise_ratio: float
    peak_level_db: float
    clipping_detected: bool
    confidence: float
    recommendations: list[str]


class BeatMetadataResponse(BaseModel):
    """Beat metadata extraction response"""
    success: bool
    bpm: float
    key: str
    time_signature: str
    duration_seconds: float
    energy: float
    danceability: float
    genres: list[str]
    mood: str
    instruments: list[str]


class GenreClassificationResponse(BaseModel):
    """Genre classification response"""
    success: bool
    primary_genre: str
    secondary_genres: list[str]
    confidence: float
    energy_level: str
    mood: str


class CopyrightScanResponse(BaseModel):
    """Copyright scan response"""
    success: bool
    risk_level: str
    is_original: bool
    confidence: float
    matches: list[dict]
    recommendations: list[str]


class BeatComparisonResponse(BaseModel):
    """Beat comparison response"""
    success: bool
    similarity_score: float
    risk_assessment: str


class CaptionGenerationResponse(BaseModel):
    """Caption generation response"""
    success: bool
    content: str
    platform: str
    tone: str
    hashtags: list[str]
    character_count: int
    word_count: int
    confidence: float


class MultipleCaptionsResponse(BaseModel):
    """Multiple captions response"""
    success: bool
    captions: dict[str, dict]


class PromotionalCopyResponse(BaseModel):
    """Promotional copy response"""
    success: bool
    copy: str


class BeatDescriptionResponse(BaseModel):
    """Beat description response"""
    success: bool
    description: str


# Beat Analysis Endpoints


@router.post("/analyze-beat", response_model=AudioQualityResponse)
async def analyze_beat_quality(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze audio quality of uploaded beat
    
    Checks:
    - Loudness (LUFS target: -14dB)
    - Dynamic range
    - Signal-to-noise ratio
    - Clipping detection
    - Peak levels
    
    Returns quality assessment with recommendations
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Analyze quality
            quality_metrics = beat_analyzer.analyze_audio_quality(temp_path)
            
            return AudioQualityResponse(
                success=True,
                quality_level=quality_metrics.quality_level.value,
                loudness_db=quality_metrics.loudness_db,
                dynamic_range_db=quality_metrics.dynamic_range_db,
                signal_to_noise_ratio=quality_metrics.signal_to_noise_ratio,
                peak_level_db=quality_metrics.peak_level_db,
                clipping_detected=quality_metrics.clipping_detected,
                confidence=quality_metrics.confidence,
                recommendations=quality_metrics.recommendations,
            )
        finally:
            os.unlink(temp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-metadata", response_model=BeatMetadataResponse)
async def extract_beat_metadata(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Extract metadata from beat audio
    
    Extracts:
    - BPM (tempo)
    - Musical key
    - Time signature
    - Duration
    - Energy level
    - Danceability
    - Genres
    - Mood
    - Instruments
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Extract metadata
            metadata = beat_analyzer.extract_metadata(temp_path)
            
            return BeatMetadataResponse(
                success=True,
                bpm=metadata.bpm,
                key=metadata.key,
                time_signature=metadata.time_signature,
                duration_seconds=metadata.duration_seconds,
                energy=metadata.energy,
                danceability=metadata.danceability,
                genres=metadata.genres,
                mood=metadata.mood,
                instruments=metadata.instruments,
            )
        finally:
            os.unlink(temp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-genre", response_model=GenreClassificationResponse)
async def classify_beat_genre(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Classify the genre of a beat
    
    Uses audio fingerprinting and spectral analysis to determine:
    - Primary genre
    - Secondary genres
    - Confidence score
    - Energy level
    - Mood
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            import librosa
            
            # Load audio and classify
            y, sr = librosa.load(temp_path, sr=22050, mono=True)
            
            # Estimate BPM first
            bpm, _ = librosa.beat.tempo(y=y, sr=sr)
            
            # Classify genre
            genre_info = beat_analyzer.classify_genre(y, sr, float(bpm))
            
            return GenreClassificationResponse(
                success=True,
                primary_genre=genre_info.primary_genre,
                secondary_genres=genre_info.secondary_genres,
                confidence=genre_info.confidence,
                energy_level=genre_info.energy_level,
                mood=genre_info.mood,
            )
        finally:
            os.unlink(temp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Copyright Scanning Endpoints


@router.post("/scan-copyright", response_model=CopyrightScanResponse)
async def scan_beat_copyright(
    file: UploadFile = File(...),
    beat_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """
    Scan a beat for copyright issues
    
    Checks for:
    - Similar content in database
    - Known samples
    - Copyright patterns
    - Risk assessment
    
    Returns risk level (clear, low, medium, high, blocked)
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Scan copyright
            scan_result = copyright_scanner.scan_beat_copyright(
                temp_path, beat_id or "new_beat"
            )
            
            return CopyrightScanResponse(
                success=True,
                risk_level=scan_result.risk_level.value,
                is_original=scan_result.is_original,
                confidence=scan_result.confidence,
                matches=[
                    {
                        "beat_id": m.beat_id,
                        "beat_title": m.beat_title,
                        "similarity_score": m.similarity_score,
                        "risk_level": m.risk_level.value,
                        "reason": m.reason,
                    }
                    for m in scan_result.matches
                ],
                recommendations=scan_result.recommendations,
            )
        finally:
            os.unlink(temp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-beats", response_model=BeatComparisonResponse)
async def compare_two_beats(
    file1: UploadFile = File(..., description="First beat audio"),
    file2: UploadFile = File(..., description="Second beat audio"),
    current_user: User = Depends(get_current_user),
):
    """
    Compare two beats for similarity
    
    Uses audio fingerprinting to calculate similarity score.
    Useful for checking if a beat is too similar to existing content.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp1:
            content1 = await file1.read()
            temp1.write(content1)
            path1 = temp1.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp2:
            content2 = await file2.read()
            temp2.write(content2)
            path2 = temp2.name
        
        try:
            # Compare beats
            similarity = copyright_scanner.compare_beats(path1, path2)
            
            # Determine risk assessment
            if similarity > 0.85:
                risk = "High - Beats are very similar"
            elif similarity > 0.65:
                risk = "Medium - Notable similarities detected"
            elif similarity > 0.45:
                risk = "Low - Minor similarities"
            else:
                risk = "Clear - Beats are distinct"
            
            return BeatComparisonResponse(
                success=True,
                similarity_score=similarity,
                risk_assessment=risk,
            )
        finally:
            os.unlink(path1)
            os.unlink(path2)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Caption Generation Endpoints


@router.post("/generate-caption", response_model=CaptionGenerationResponse)
async def generate_marketing_caption(
    beat_title: str = Query(...),
    beat_genre: str = Query(...),
    beat_mood: str = Query(...),
    bpm: float = Query(...),
    tone: str = Query("casual", regex="^(professional|casual|hype|poetic)$"),
    length: str = Query("medium", regex="^(short|medium|long)$"),
    platform: str = Query("instagram", regex="^(twitter|instagram|tiktok|facebook|youtube)$"),
    include_hashtags: bool = Query(True),
    include_emojis: bool = Query(True),
    current_user: User = Depends(get_current_user),
):
    """
    Generate AI marketing caption for a beat
    
    Parameters:
    - beat_title: Name of the beat
    - beat_genre: Genre (Afrobeat, Trap, etc.)
    - beat_mood: Mood (energetic, chill, etc.)
    - bpm: Tempo in beats per minute
    - tone: Caption tone (professional, casual, hype, poetic)
    - length: Caption length (short, medium, long)
    - platform: Target platform (twitter, instagram, etc.)
    - include_hashtags: Whether to include hashtags
    - include_emojis: Whether to include emojis
    """
    try:
        options = CaptionOptions(
            tone=tone,
            length=length,
            platform=platform,
            include_hashtags=include_hashtags,
            include_emojis=include_emojis,
            target_audience="all",
        )
        
        caption = caption_generator.generate_caption(
            beat_title, beat_genre, beat_mood, bpm, options
        )
        
        return CaptionGenerationResponse(
            success=True,
            content=caption.content,
            platform=caption.platform,
            tone=caption.tone,
            hashtags=caption.hashtags,
            character_count=caption.character_count,
            word_count=caption.word_count,
            confidence=caption.confidence,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-captions-batch", response_model=MultipleCaptionsResponse)
async def generate_captions_for_platforms(
    beat_title: str = Query(...),
    beat_genre: str = Query(...),
    beat_mood: str = Query(...),
    bpm: float = Query(...),
    platforms: str = Query("instagram,twitter,tiktok", description="Comma-separated platforms"),
    tone: str = Query("casual"),
    current_user: User = Depends(get_current_user),
):
    """
    Generate captions for multiple platforms at once
    
    Automatically adapts caption length and style for each platform.
    """
    try:
        platform_list = [p.strip() for p in platforms.split(",")]
        
        captions_dict = caption_generator.generate_multiple_captions(
            beat_title, beat_genre, beat_mood, bpm, platform_list, tone
        )
        
        return MultipleCaptionsResponse(
            success=True,
            captions={
                platform: {
                    "content": caption.content,
                    "hashtags": caption.hashtags,
                    "character_count": caption.character_count,
                    "word_count": caption.word_count,
                    "confidence": caption.confidence,
                }
                for platform, caption in captions_dict.items()
            },
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-promo-copy", response_model=PromotionalCopyResponse)
async def generate_promotional_copy(
    beat_title: str = Query(...),
    beat_genre: str = Query(...),
    producer_name: str = Query(...),
    key: str = Query(...),
    bpm: float = Query(...),
    duration_seconds: Optional[float] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """
    Generate promotional copy for beat listing page
    
    Creates engaging description for marketplace listing.
    Includes technical specs and call-to-action.
    """
    try:
        copy = caption_generator.generate_promotional_copy(
            beat_title, beat_genre, producer_name, key, bpm, duration_seconds
        )
        
        return PromotionalCopyResponse(success=True, copy=copy)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-beat-description", response_model=BeatDescriptionResponse)
async def generate_beat_description(
    beat_title: str = Query(...),
    beat_genre: str = Query(...),
    beat_mood: str = Query(...),
    bpm: float = Query(...),
    key: str = Query(...),
    instruments: str = Query(..., description="Comma-separated list of instruments"),
    current_user: User = Depends(get_current_user),
):
    """
    Generate detailed beat description
    
    Creates comprehensive description including:
    - Vibe and energy description
    - Technical details
    - Use cases
    - Production quality highlights
    - License information
    """
    try:
        instrument_list = [i.strip() for i in instruments.split(",")]
        
        description = caption_generator.generate_beat_description(
            beat_title, beat_genre, beat_mood, bpm, key, instrument_list
        )
        
        return BeatDescriptionResponse(success=True, description=description)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
