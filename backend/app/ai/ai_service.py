"""
AI Service - OpenAI integration for content generation
"""
from openai import OpenAI
from typing import List, Dict, Optional
from app.core.config import settings
from fastapi import HTTPException, status


class AIService:
    """AI content generation service using OpenAI"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            print(f"⚠️  OpenAI initialization failed: {e}")
            self.client = None
    
    def _check_client(self):
        """Check if OpenAI client is initialized"""
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not available. Please check API configuration."
            )
    
    def generate_social_captions(
        self,
        track_title: str,
        artist_name: str,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        platform: str = "instagram"
    ) -> List[Dict[str, str]]:
        """
        Generate social media captions for a track
        
        Args:
            track_title: Track title
            artist_name: Artist name
            genre: Music genre
            mood: Track mood
            platform: Social platform (instagram, twitter, tiktok, facebook)
            
        Returns:
            List of caption variations with tone
        """
        self._check_client()
        
        # Build prompt
        genre_text = f" in the {genre} genre" if genre else ""
        mood_text = f" with a {mood} vibe" if mood else ""
        
        prompt = f"""Generate 5 social media captions for {platform} to promote a music track.

Track: "{track_title}"
Artist: {artist_name}
{genre_text}{mood_text}

Create 5 different caption styles:
1. Hype/Energetic - Get people excited
2. Emotional/Deep - Connect emotionally
3. Professional - Industry-focused
4. Fun/Playful - Light and entertaining
5. Mysterious/Teaser - Build anticipation

Requirements:
- Keep it authentic and relatable to African music culture
- Include relevant emojis
- Make it engaging and shareable
- Length appropriate for {platform}
- Don't use hashtags (we'll generate those separately)

Format each caption with the tone label first, then the caption text."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a social media expert specializing in music promotion for African artists."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            # Parse response
            content = response.choices[0].message.content
            captions = self._parse_captions(content)
            
            return captions
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate captions: {str(e)}"
            )
    
    def _parse_captions(self, content: str) -> List[Dict[str, str]]:
        """Parse AI response into structured captions"""
        captions = []
        lines = content.strip().split('\n')
        
        current_tone = ""
        current_caption = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a tone label
            if any(tone in line.lower() for tone in ['hype', 'emotional', 'professional', 'fun', 'mysterious', 'playful', 'teaser']):
                # Save previous caption if exists
                if current_caption:
                    captions.append({
                        "tone": current_tone,
                        "caption": current_caption.strip()
                    })
                
                # Extract tone
                if ':' in line:
                    current_tone = line.split(':')[0].strip()
                    current_caption = line.split(':', 1)[1].strip() if len(line.split(':', 1)) > 1 else ""
                else:
                    current_tone = line.strip()
                    current_caption = ""
            else:
                # Continue building caption
                current_caption += " " + line
        
        # Add last caption
        if current_caption:
            captions.append({
                "tone": current_tone,
                "caption": current_caption.strip()
            })
        
        return captions
    
    def generate_hashtags(
        self,
        track_title: str,
        artist_name: str,
        genre: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Generate relevant hashtags for a track
        
        Args:
            track_title: Track title
            artist_name: Artist name
            genre: Music genre
            location: Location (e.g., "Lagos, Nigeria")
            
        Returns:
            Dictionary with categorized hashtags
        """
        self._check_client()
        
        genre_text = f"Genre: {genre}" if genre else ""
        location_text = f"Location: {location}" if location else ""
        
        prompt = f"""Generate hashtags for promoting a music track on social media.

Track: "{track_title}"
Artist: {artist_name}
{genre_text}
{location_text}

Create 4 categories of hashtags:
1. Genre Tags (5-7 tags): Related to the music genre and style
2. Trending Tags (3-5 tags): Popular music/culture hashtags
3. Location Tags (3-5 tags): City, country, regional tags
4. Campaign Tags (2-3 tags): Custom tags for this track/artist

Requirements:
- Focus on African music and culture
- Mix popular and niche tags
- Include location-specific tags
- Make them discoverable
- All lowercase, no spaces

Format as:
Genre: #tag1 #tag2 #tag3
Trending: #tag1 #tag2
Location: #tag1 #tag2
Campaign: #tag1 #tag2"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a social media hashtag expert for African music promotion."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            hashtags = self._parse_hashtags(content)
            
            return hashtags
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate hashtags: {str(e)}"
            )
    
    def _parse_hashtags(self, content: str) -> Dict[str, List[str]]:
        """Parse hashtags from AI response"""
        hashtags = {
            "genre": [],
            "trending": [],
            "location": [],
            "campaign": []
        }
        
        lines = content.strip().split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for category
            line_lower = line.lower()
            if 'genre' in line_lower and ':' in line:
                current_category = 'genre'
                line = line.split(':', 1)[1]
            elif 'trending' in line_lower and ':' in line:
                current_category = 'trending'
                line = line.split(':', 1)[1]
            elif 'location' in line_lower and ':' in line:
                current_category = 'location'
                line = line.split(':', 1)[1]
            elif 'campaign' in line_lower and ':' in line:
                current_category = 'campaign'
                line = line.split(':', 1)[1]
            
            # Extract hashtags
            if current_category:
                tags = [tag.strip() for tag in line.split() if tag.startswith('#')]
                hashtags[current_category].extend(tags)
        
        return hashtags
    
    def generate_press_release(
        self,
        track_title: str,
        artist_name: str,
        artist_bio: Optional[str] = None,
        track_description: Optional[str] = None,
        genre: Optional[str] = None,
        release_date: Optional[str] = None
    ) -> str:
        """
        Generate a press release for a track
        
        Args:
            track_title: Track title
            artist_name: Artist name
            artist_bio: Artist biography
            track_description: Track description
            genre: Music genre
            release_date: Release date
            
        Returns:
            Formatted press release
        """
        self._check_client()
        
        bio_text = f"\n\nArtist Bio: {artist_bio}" if artist_bio else ""
        desc_text = f"\n\nTrack Description: {track_description}" if track_description else ""
        genre_text = f"\nGenre: {genre}" if genre else ""
        date_text = f"\nRelease Date: {release_date}" if release_date else ""
        
        prompt = f"""Write a professional press release for a music track release.

Track: "{track_title}"
Artist: {artist_name}{genre_text}{date_text}{bio_text}{desc_text}

Create a compelling press release with:
1. Catchy headline
2. Opening paragraph (who, what, when, where, why)
3. Track details and unique selling points
4. Artist background and achievements
5. Quote from the artist (create an authentic quote)
6. Availability and streaming platforms
7. Contact information placeholder

Style:
- Professional but engaging
- Celebrate African music culture
- Highlight uniqueness
- 300-400 words
- AP style formatting

Do NOT include: [Contact:] section (we'll add that separately)"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional music publicist specializing in African artists."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate press release: {str(e)}"
            )
    
    def suggest_posting_times(
        self,
        timezone: str = "Africa/Lagos",
        target_audience: str = "Nigeria"
    ) -> List[Dict[str, str]]:
        """
        Suggest optimal posting times for social media
        
        Args:
            timezone: Timezone (e.g., "Africa/Lagos")
            target_audience: Target audience location
            
        Returns:
            List of suggested posting times with reasons
        """
        self._check_client()
        
        prompt = f"""Suggest the best times to post music content on social media.

Timezone: {timezone}
Target Audience: {target_audience}

Provide 5 optimal posting times for maximum engagement with:
1. Day of week
2. Time (in 24-hour format)
3. Platform (Instagram, Twitter, TikTok, or Facebook)
4. Reason why this time is optimal

Consider:
- African social media usage patterns
- Peak engagement times
- Work schedules and leisure time
- Weekend vs weekday behavior

Format each suggestion clearly."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a social media timing expert for African markets."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            times = self._parse_posting_times(content)
            
            return times
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate posting times: {str(e)}"
            )
    
    def _parse_posting_times(self, content: str) -> List[Dict[str, str]]:
        """Parse posting times from AI response"""
        times = []
        lines = content.strip().split('\n')
        
        current_time = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Simple parsing - look for time-related content
            if any(day in line for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
                if current_time:
                    times.append(current_time)
                current_time = {"suggestion": line}
            elif current_time:
                current_time["suggestion"] += f" {line}"
        
        if current_time:
            times.append(current_time)
        
        return times
    
    def generate_bio(
        self,
        artist_name: str,
        genre: Optional[str] = None,
        achievements: Optional[List[str]] = None,
        style: str = "professional"
    ) -> Dict[str, str]:
        """
        Generate artist bio in different styles
        
        Args:
            artist_name: Artist name
            genre: Music genre
            achievements: List of achievements
            style: Bio style (professional, casual, short, detailed)
            
        Returns:
            Dictionary with different bio versions
        """
        self._check_client()
        
        genre_text = f"Genre: {genre}" if genre else ""
        achievements_text = ""
        if achievements:
            achievements_text = "Achievements:\n- " + "\n- ".join(achievements)
        
        prompt = f"""Generate an artist biography for:

Artist: {artist_name}
{genre_text}
{achievements_text}

Create 3 versions:
1. Short Bio (50-75 words): For social media profiles
2. Medium Bio (150-200 words): For press kits and websites
3. Detailed Bio (300-400 words): For full press releases

Style: {style}

Requirements:
- Authentic and engaging
- Celebrate African music culture
- Professional yet personable
- Include genre and style
- Mention key achievements
- Make it shareable

Label each version clearly."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional music bio writer specializing in African artists."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            bios = self._parse_bios(content)
            
            return bios
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate bio: {str(e)}"
            )
    
    def _parse_bios(self, content: str) -> Dict[str, str]:
        """Parse bios from AI response"""
        bios = {
            "short": "",
            "medium": "",
            "detailed": ""
        }
        
        lines = content.strip().split('\n')
        current_type = None
        current_bio = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Check for bio type
            if 'short' in line_lower and ('bio' in line_lower or ':' in line):
                if current_type and current_bio:
                    bios[current_type] = ' '.join(current_bio)
                current_type = 'short'
                current_bio = []
                if ':' in line:
                    text = line.split(':', 1)[1].strip()
                    if text:
                        current_bio.append(text)
            elif 'medium' in line_lower and ('bio' in line_lower or ':' in line):
                if current_type and current_bio:
                    bios[current_type] = ' '.join(current_bio)
                current_type = 'medium'
                current_bio = []
                if ':' in line:
                    text = line.split(':', 1)[1].strip()
                    if text:
                        current_bio.append(text)
            elif 'detailed' in line_lower and ('bio' in line_lower or ':' in line):
                if current_type and current_bio:
                    bios[current_type] = ' '.join(current_bio)
                current_type = 'detailed'
                current_bio = []
                if ':' in line:
                    text = line.split(':', 1)[1].strip()
                    if text:
                        current_bio.append(text)
            elif current_type:
                current_bio.append(line)
        
        # Save last bio
        if current_type and current_bio:
            bios[current_type] = ' '.join(current_bio)
        
        return bios
