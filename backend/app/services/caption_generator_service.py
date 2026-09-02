"""
Caption Generator Service for AI Promotion Platform

Generates marketing captions and descriptions for beats.
Uses existing AIService with platform-specific templates.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json
from app.ai.ai_service import AIService


@dataclass
class CaptionOptions:
    """Options for caption generation"""
    tone: str  # professional, casual, hype, poetic
    length: str  # short (1-2 lines), medium (3-4 lines), long (5+ lines)
    platform: str  # twitter, instagram, tiktok, facebook, youtube
    include_hashtags: bool = True
    include_emojis: bool = True
    target_audience: str = "producers"  # producers, djs, fans, all


@dataclass
class GeneratedCaption:
    """Generated caption result"""
    content: str
    platform: str
    tone: str
    length: str
    hashtags: List[str]
    character_count: int
    word_count: int
    confidence: float


class CaptionGeneratorService:
    """Service for generating marketing captions for beats"""
    
    # Platform-specific constraints
    PLATFORM_LIMITS = {
        "twitter": 280,
        "instagram": 2200,
        "tiktok": 150,
        "facebook": 63206,
        "youtube": 5000,
    }
    
    # Tone templates
    TONE_TEMPLATES = {
        "professional": {
            "opening": "Introducing",
            "style": "polished, credible, industry-standard",
            "closing": "Available now on BeatPush",
        },
        "casual": {
            "opening": "Check out",
            "style": "relaxed, conversational, friendly",
            "closing": "Grab it today!",
        },
        "hype": {
            "opening": "🔥 DROP ALERT",
            "style": "energetic, exciting, trending",
            "closing": "Get it NOW",
        },
        "poetic": {
            "opening": "Experience",
            "style": "artistic, evocative, inspirational",
            "closing": "Feel the beat",
        },
    }
    
    # Relevant hashtags by genre
    GENRE_HASHTAGS = {
        "Afrobeat": ["#Afrobeat", "#AfricanMusic", "#AfroWave", "#BeatMaker", "#ProducerLife"],
        "Trap": ["#TrapMusic", "#TrapBeats", "#DrillandTrap", "#BeatForSale", "#TrapProducer"],
        "Drill": ["#Drill", "#DrillMusic", "#DrillBeats", "#UK", "#Rap"],
        "Dancehall": ["#Dancehall", "#Reggae", "#Caribbean", "#DanceMusic", "#BeatPush"],
        "Hip Hop": ["#HipHop", "#Rap", "#BeatMaker", "#HipHopBeats", "#WildOutBeats"],
        "R&B": ["#RnB", "#RandB", "#SoulMusic", "#Smooth", "#BeatMarket"],
        "Electronic": ["#Electronic", "#EDM", "#Synth", "#Producer", "#ElectronicMusic"],
        "Lo-Fi": ["#LoFi", "#LoFiBeats", "#Chill", "#Relaxing", "#StudyMusic"],
        "Amapiano": ["#Amapiano", "#SouthAfrican", "#Piano", "#BeatMaker", "#AfricanSound"],
        "House": ["#House", "#HouseMusic", "#Dance", "#EDM", "#DanceFloor"],
        "Techno": ["#Techno", "#TechnoMusic", "#Electronica", "#Underground", "#Dance"],
    }

    def __init__(self, ai_service: AIService):
        """
        Initialize caption generator service
        
        Args:
            ai_service: Instance of AIService for LLM-based generation
        """
        self.ai_service = ai_service

    def generate_caption(
        self,
        beat_title: str,
        beat_genre: str,
        beat_mood: str,
        bpm: float,
        options: CaptionOptions,
    ) -> GeneratedCaption:
        """
        Generate a marketing caption for a beat
        
        Args:
            beat_title: Title of the beat
            beat_genre: Genre of the beat
            beat_mood: Mood of the beat (e.g., 'energetic', 'chill')
            bpm: BPM of the beat
            options: Caption generation options
            
        Returns:
            GeneratedCaption with content and metadata
        """
        try:
            # Build prompt for AI service
            prompt = self._build_generation_prompt(
                beat_title, beat_genre, beat_mood, bpm, options
            )
            
            # Generate caption using AI service
            caption_content = self.ai_service.generate(prompt)
            
            # Clean and validate caption
            caption_content = caption_content.strip()
            
            # Extract hashtags if present
            hashtags = self._extract_hashtags(caption_content) if options.include_hashtags else []
            
            # Add platform-specific hashtags
            if options.include_hashtags and not hashtags:
                hashtags = self._get_hashtags_for_genre(beat_genre, options.platform)
            
            # Count words and characters
            word_count = len(caption_content.split())
            char_count = len(caption_content)
            
            # Validate against platform limit
            if char_count > self.PLATFORM_LIMITS.get(options.platform, 5000):
                # Truncate if necessary
                caption_content = self._truncate_caption(caption_content, options.platform)
                char_count = len(caption_content)
            
            # Calculate confidence
            confidence = self._calculate_confidence(caption_content, options)
            
            return GeneratedCaption(
                content=caption_content,
                platform=options.platform,
                tone=options.tone,
                length=options.length,
                hashtags=hashtags,
                character_count=char_count,
                word_count=word_count,
                confidence=confidence,
            )
        
        except Exception as e:
            raise ValueError(f"Failed to generate caption: {str(e)}")

    def generate_multiple_captions(
        self,
        beat_title: str,
        beat_genre: str,
        beat_mood: str,
        bpm: float,
        platforms: List[str],
        tone: str = "casual",
    ) -> Dict[str, GeneratedCaption]:
        """
        Generate captions for multiple platforms
        
        Args:
            beat_title: Title of the beat
            beat_genre: Genre
            beat_mood: Mood
            bpm: BPM
            platforms: List of platforms (twitter, instagram, etc.)
            tone: Tone for all captions
            
        Returns:
            Dictionary mapping platform names to GeneratedCaption objects
        """
        captions = {}
        
        for platform in platforms:
            # Adapt length based on platform
            if platform == "twitter":
                length = "short"
            elif platform in ["tiktok"]:
                length = "short"
            elif platform in ["instagram", "facebook"]:
                length = "long"
            else:
                length = "medium"
            
            options = CaptionOptions(
                tone=tone,
                length=length,
                platform=platform,
                include_hashtags=True,
                include_emojis=platform in ["instagram", "tiktok", "twitter"],
                target_audience="all",
            )
            
            captions[platform] = self.generate_caption(
                beat_title, beat_genre, beat_mood, bpm, options
            )
        
        return captions

    def generate_promotional_copy(
        self,
        beat_title: str,
        beat_genre: str,
        producer_name: str,
        key: str,
        bpm: float,
        length: Optional[str] = None,
    ) -> str:
        """
        Generate promotional copy for beat listing page
        
        Args:
            beat_title: Title of the beat
            beat_genre: Genre
            producer_name: Name of producer
            key: Musical key
            bpm: BPM
            length: Optional beat length in seconds
            
        Returns:
            Promotional copy as string
        """
        try:
            length_str = f"{length} seconds" if length else "high-quality instrumental"
            
            prompt = f"""Generate engaging promotional copy for a beat listing (max 100 words):

Beat Title: {beat_title}
Genre: {beat_genre}
Producer: {producer_name}
Key: {key}
BPM: {bpm}
Duration: {length_str}

Write in a professional but exciting tone. Include:
1. Brief description of the beat
2. Key technical specs
3. Call to action (e.g., "License now" or "Available for purchase")

Keep it concise and persuasive for producers and DJs."""

            copy = self.ai_service.generate(prompt)
            return copy.strip()
        
        except Exception as e:
            raise ValueError(f"Failed to generate promotional copy: {str(e)}")

    def generate_beat_description(
        self,
        beat_title: str,
        beat_genre: str,
        beat_mood: str,
        bpm: float,
        key: str,
        instruments: List[str],
    ) -> str:
        """
        Generate detailed beat description
        
        Args:
            beat_title: Title
            beat_genre: Genre
            beat_mood: Mood
            bpm: BPM
            key: Key
            instruments: List of instruments
            
        Returns:
            Detailed description
        """
        try:
            instruments_str = ", ".join(instruments) if instruments else "various instruments"
            
            prompt = f"""Generate a detailed and engaging beat description (150-200 words):

Beat: {beat_title}
Genre: {beat_genre}
Mood: {beat_mood}
BPM: {bpm}
Key: {key}
Instruments: {instruments_str}

Write from a producer/DJ perspective. Include:
1. Overall vibe and energy
2. Technical details (tempo, key, sound design)
3. Use cases (songs, videos, podcasts)
4. Production quality highlights
5. License information teaser

Make it compelling and informative."""

            description = self.ai_service.generate(prompt)
            return description.strip()
        
        except Exception as e:
            raise ValueError(f"Failed to generate description: {str(e)}")

    # Helper methods
    
    def _build_generation_prompt(
        self,
        beat_title: str,
        beat_genre: str,
        beat_mood: str,
        bpm: float,
        options: CaptionOptions,
    ) -> str:
        """Build AI prompt for caption generation"""
        
        tone_info = self.TONE_TEMPLATES.get(options.tone, {})
        platform_limit = self.PLATFORM_LIMITS.get(options.platform, 280)
        
        length_instruction = {
            "short": "1-2 lines, punchy and concise",
            "medium": "3-4 lines, balanced detail",
            "long": "5+ lines, detailed and comprehensive",
        }.get(options.length, "3-4 lines")
        
        prompt = f"""Generate a marketing caption for a beat on {options.platform}:

Beat Details:
- Title: {beat_title}
- Genre: {beat_genre}
- Mood: {beat_mood}
- BPM: {bpm}

Requirements:
- Tone: {options.tone} ({tone_info.get('style', 'engaging')})
- Length: {length_instruction}
- Character limit: {platform_limit} characters
- Include hashtags: {options.include_hashtags}
- Include emojis: {options.include_emojis}
- Target audience: {options.target_audience}

Style guidelines:
- Opening: "{tone_info.get('opening', 'Check out')}"
- Closing: "{tone_info.get('closing', 'Available now')}"
- Keep it engaging and shareable
- Highlight the beat's unique qualities

Generate only the caption text, nothing else."""

        return prompt

    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from generated content"""
        words = content.split()
        hashtags = [word for word in words if word.startswith('#')]
        return hashtags

    def _get_hashtags_for_genre(self, genre: str, platform: str) -> List[str]:
        """Get relevant hashtags for a genre"""
        hashtags = self.GENRE_HASHTAGS.get(genre, [])
        
        # Limit hashtags based on platform
        platform_hashtag_limits = {
            "twitter": 2,
            "instagram": 30,
            "tiktok": 5,
            "facebook": 10,
            "youtube": 15,
        }
        
        limit = platform_hashtag_limits.get(platform, 5)
        return hashtags[:limit]

    def _truncate_caption(self, content: str, platform: str) -> str:
        """Truncate caption to platform limit"""
        limit = self.PLATFORM_LIMITS.get(platform, 280)
        
        if len(content) <= limit:
            return content
        
        # Try to cut at word boundary
        truncated = content[:limit]
        last_space = truncated.rfind(" ")
        
        if last_space > limit * 0.8:  # If space is within 80% of limit
            truncated = truncated[:last_space]
        
        # Add ellipsis if truncated
        if len(truncated) < len(content):
            truncated = truncated.rstrip(".!?") + "..."
        
        return truncated

    def _calculate_confidence(self, caption: str, options: CaptionOptions) -> float:
        """Calculate confidence score for generated caption"""
        confidence = 0.8  # Base confidence
        
        # Increase if has hashtags
        if "#" in caption:
            confidence += 0.05
        
        # Increase if appropriate length
        word_count = len(caption.split())
        if options.length == "short" and word_count < 20:
            confidence += 0.05
        elif options.length == "medium" and 20 <= word_count < 50:
            confidence += 0.05
        elif options.length == "long" and word_count >= 50:
            confidence += 0.05
        
        # Ensure emojis if requested
        if options.include_emojis and any(ord(char) > 127 for char in caption):
            confidence += 0.05
        
        return min(confidence, 0.99)
