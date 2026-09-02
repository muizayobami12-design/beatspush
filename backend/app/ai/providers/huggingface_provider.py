"""
Hugging Face Provider
Primary free AI provider using Hugging Face Inference API
"""
import httpx
import json
from typing import Dict, Any
from .base import (
    AIProvider,
    AIRequestType,
    AIResponse,
    ProviderException,
    ProviderBusyException,
    ProviderUnavailableException
)


class HuggingFaceProvider(AIProvider):
    """Primary provider using Hugging Face Inference API (free)"""
    
    # Model mapping for different request types
    MODELS = {
        AIRequestType.TITLE: "google/flan-t5-large",
        AIRequestType.DESCRIPTION: "google/flan-t5-large",
        AIRequestType.CAPTION: "facebook/bart-large-cnn",
        AIRequestType.HASHTAGS: "google/flan-t5-base",
        AIRequestType.PRESS_RELEASE: "google/flan-t5-large",
        AIRequestType.CAMPAIGN_SUGGESTIONS: "google/flan-t5-large",
        AIRequestType.GENRE_TAGS: "google/flan-t5-base",
        AIRequestType.AUDIENCE_INSIGHTS: "google/flan-t5-large"
    }
    
    def __init__(self, api_url: str = "https://api-inference.huggingface.co"):
        super().__init__()
        self.api_url = api_url
        self.name = "huggingface"
        self.priority = 1
    
    def is_available(self) -> bool:
        """Hugging Face API is always available (free tier)"""
        return True
    
    def get_model_for_type(self, request_type: AIRequestType) -> str:
        """Get optimal model for request type"""
        return self.MODELS.get(request_type, "google/flan-t5-base")
    
    async def generate(
        self,
        request_type: AIRequestType,
        params: Dict[str, Any]
    ) -> AIResponse:
        """Generate using Hugging Face API"""
        
        model = self.get_model_for_type(request_type)
        prompt = self._build_prompt(request_type, params)
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": self._get_max_length(request_type),
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.api_url}/models/{model}",
                    headers=headers,
                    json=payload
                )
                if response.status_code == 200:
                    data = response.json()
                    content = self._parse_response(request_type, data, params)
                    
                    return AIResponse(
                        content=content,
                        provider=self.name,
                        model=model,
                        from_cache=False
                    )
                elif response.status_code == 503:
                    # Model is loading, retry later
                    raise ProviderBusyException(f"Model {model} is loading")
                elif response.status_code == 429:
                    raise ProviderBusyException("Rate limit exceeded")
                else:
                    error_text = response.text
                    raise ProviderException(
                        f"Hugging Face API error {response.status_code}: {error_text}"
                    )
                    
        except httpx.HTTPError as e:
            raise ProviderUnavailableException(f"Network error: {str(e)}")
        except Exception as e:
            if isinstance(e, (ProviderException, ProviderBusyException)):
                raise
            raise ProviderException(f"Unexpected error: {str(e)}")
    
    def _build_prompt(
        self,
        request_type: AIRequestType,
        params: Dict[str, Any]
    ) -> str:
        """Build prompt for specific request type"""
        
        if request_type == AIRequestType.TITLE:
            return self._build_title_prompt(params)
        elif request_type == AIRequestType.DESCRIPTION:
            return self._build_description_prompt(params)
        elif request_type == AIRequestType.CAPTION:
            return self._build_caption_prompt(params)
        elif request_type == AIRequestType.HASHTAGS:
            return self._build_hashtags_prompt(params)
        elif request_type == AIRequestType.PRESS_RELEASE:
            return self._build_press_release_prompt(params)
        elif request_type == AIRequestType.CAMPAIGN_SUGGESTIONS:
            return self._build_campaign_prompt(params)
        elif request_type == AIRequestType.GENRE_TAGS:
            return self._build_genre_tags_prompt(params)
        elif request_type == AIRequestType.AUDIENCE_INSIGHTS:
            return self._build_audience_insights_prompt(params)
        else:
            raise ValueError(f"Unknown request type: {request_type}")

    
    def _build_title_prompt(self, params: Dict[str, Any]) -> str:
        """Build prompt for beat title generation"""
        genre = params.get('genre', 'music')
        mood = params.get('mood', '')
        bpm = params.get('bpm', '')
        instruments = params.get('instruments', [])
        
        mood_text = f"with {mood} mood" if mood else ""
        bpm_text = f"at {bpm} BPM" if bpm else ""
        inst_text = f"using {', '.join(instruments)}" if instruments else ""
        
        prompt = f"""Generate 5 creative, catchy titles for a {genre} beat {mood_text} {bpm_text} {inst_text}.

Requirements:
- Each title should be 2-5 words
- Make them memorable and commercial
- Appeal to African music culture
- Avoid generic names

Generate exactly 5 titles, separated by newlines:
1."""
        return prompt.strip()
    
    def _build_description_prompt(self, params: Dict[str, Any]) -> str:
        """Build prompt for beat description"""
        title = params.get('title', 'Untitled')
        genre = params.get('genre', 'music')
        mood = params.get('mood', '')
        
        prompt = f"""Write a compelling description for a {genre} beat titled "{title}" with {mood} mood.

Include:
- What makes this beat unique
- Best use cases (recording, live performance, etc.)
- Mood and energy level
- Production quality highlights

Write 150-200 words that will help sell this beat."""
        return prompt.strip()
    
    def _build_caption_prompt(self, params: Dict[str, Any]) -> str:
        """Build prompt for social media captions"""
        track_title = params.get('track_title', 'New Track')
        artist_name = params.get('artist_name', 'Artist')
        genre = params.get('genre', '')
        platform = params.get('platform', 'instagram')
        
        genre_text = f"({genre})" if genre else ""
        
        prompt = f"""Generate 5 social media captions for {platform} promoting:
Track: "{track_title}" by {artist_name} {genre_text}

Create 5 variations with different tones:
1. Hype/Energetic
2. Emotional
3. Professional
4. Fun/Playful
5. Mysterious

Each caption should be platform-appropriate, include emojis, and be authentic to African music culture.

Format each as:
[Tone]: [Caption text]"""
        return prompt.strip()

    
    def _build_hashtags_prompt(self, params: Dict[str, Any]) -> str:
        """Build prompt for hashtag generation"""
        track_title = params.get('track_title', 'Track')
        artist_name = params.get('artist_name', 'Artist')
        genre = params.get('genre', '')
        location = params.get('location', '')
        
        prompt = f"""Generate hashtags for: "{track_title}" by {artist_name}
Genre: {genre}
Location: {location}

Create 4 categories:
1. Genre Tags (5-7): #afrobeats #amapiano etc
2. Trending Tags (3-5): #newmusic #viral etc
3. Location Tags (3-5): #lagos #nigeria etc
4. Campaign Tags (2-3): Custom for this track

Format:
Genre: #tag1 #tag2
Trending: #tag1 #tag2
Location: #tag1 #tag2
Campaign: #tag1 #tag2"""
        return prompt.strip()
    
    def _build_press_release_prompt(self, params: Dict[str, Any]) -> str:
        """Build prompt for press release"""
        title = params.get('track_title', 'Untitled')
        artist = params.get('artist_name', 'Artist')
        genre = params.get('genre', '')
        
        prompt = f"""Write a professional press release (300-400 words) for:
Track: "{title}"
Artist: {artist}
Genre: {genre}

Include:
1. Catchy headline
2. Opening paragraph
3. Track details
4. Artist quote
5. Availability info

Style: Professional, AP format, celebrate African music."""
        return prompt.strip()
    
    def _build_campaign_prompt(self, params: Dict[str, Any]) -> str:
        """Build prompt for campaign optimization"""
        metrics = params.get('campaign_metrics', {})
        
        prompt = f"""Analyze this campaign and provide 3-5 optimization suggestions:

Metrics: {json.dumps(metrics)}

Provide:
- Specific actionable improvements
- Budget allocation tips
- A/B testing ideas
- Best posting times

Keep suggestions practical and data-driven."""
        return prompt.strip()
    
    def _build_genre_tags_prompt(self, params: Dict[str, Any]) -> str:
        """Build prompt for genre tagging"""
        title = params.get('title', '')
        description = params.get('description', '')
        bpm = params.get('bpm', '')
        
        prompt = f"""Suggest genres and moods for this beat:
Title: {title}
Description: {description}
BPM: {bpm}

Provide:
1. 3-5 primary genres with confidence (e.g., "Afrobeats (95%)")
2. 5-10 mood tags (e.g., energetic, chill, dark)

Be specific and avoid contradictions."""
        return prompt.strip()
    
    def _build_audience_insights_prompt(self, params: Dict[str, Any]) -> str:
        """Build prompt for audience insights"""
        genre = params.get('genre', 'music')
        
        prompt = f"""Provide audience insights for {genre} music:

Include:
1. Demographics (age, gender, locations)
2. Best social platforms
3. Content themes that resonate
4. Growth strategies

Focus on African music markets."""
        return prompt.strip()

    
    def _parse_response(
        self,
        request_type: AIRequestType,
        data: Any,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse Hugging Face API response"""
        
        # Extract generated text from response
        if isinstance(data, list) and len(data) > 0:
            generated_text = data[0].get('generated_text', '')
        elif isinstance(data, dict):
            generated_text = data.get('generated_text', '')
        else:
            generated_text = str(data)
        
        # Parse based on request type
        if request_type == AIRequestType.TITLE:
            return self._parse_titles(generated_text)
        elif request_type == AIRequestType.DESCRIPTION:
            return {"description": generated_text.strip()}
        elif request_type == AIRequestType.CAPTION:
            return self._parse_captions(generated_text)
        elif request_type == AIRequestType.HASHTAGS:
            return self._parse_hashtags(generated_text)
        elif request_type == AIRequestType.PRESS_RELEASE:
            return {"press_release": generated_text.strip()}
        elif request_type == AIRequestType.CAMPAIGN_SUGGESTIONS:
            return self._parse_suggestions(generated_text)
        elif request_type == AIRequestType.GENRE_TAGS:
            return self._parse_genre_tags(generated_text)
        elif request_type == AIRequestType.AUDIENCE_INSIGHTS:
            return {"insights": generated_text.strip()}
        else:
            return {"content": generated_text.strip()}
    
    def _parse_titles(self, text: str) -> Dict[str, Any]:
        """Parse title list from response"""
        titles = []
        for line in text.split('\n'):
            line = line.strip()
            # Remove numbering
            line = line.lstrip('0123456789.)-')  .strip()
            if line and len(line) >= 10 and len(line) <= 60:
                titles.append(line)
            if len(titles) >= 5:
                break
        
        # If we didn't get 5 titles, pad with variations
        while len(titles) < 5:
            titles.append(f"Beat #{len(titles) + 1}")
        
        return {"titles": titles[:5]}
    
    def _parse_captions(self, text: str) -> Dict[str, Any]:
        """Parse captions with tones"""
        captions = []
        lines = text.split('\n')
        
        current_tone = ""
        current_caption = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains tone indicator
            if ':' in line and any(t in line.lower() for t in ['hype', 'emotional', 'professional', 'fun', 'mysterious']):
                if current_caption:
                    captions.append({
                        "tone": current_tone,
                        "caption": current_caption.strip()
                    })
                parts = line.split(':', 1)
                current_tone = parts[0].strip()
                current_caption = parts[1].strip() if len(parts) > 1 else ""
            else:
                current_caption += " " + line
        
        if current_caption:
            captions.append({
                "tone": current_tone,
                "caption": current_caption.strip()
            })
        
        # Ensure we have 5 captions
        tones = ["Hype", "Emotional", "Professional", "Fun", "Mysterious"]
        while len(captions) < 5:
            captions.append({
                "tone": tones[len(captions)],
                "caption": "Check out this amazing track! 🎵"
            })
        
        return {"captions": captions[:5]}
    
    def _parse_hashtags(self, text: str) -> Dict[str, Any]:
        """Parse categorized hashtags"""
        hashtags = {
            "genre": [],
            "trending": [],
            "location": [],
            "campaign": []
        }
        
        current_category = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            if 'genre' in line_lower:
                current_category = 'genre'
            elif 'trending' in line_lower:
                current_category = 'trending'
            elif 'location' in line_lower:
                current_category = 'location'
            elif 'campaign' in line_lower:
                current_category = 'campaign'
            
            if current_category:
                # Extract hashtags from line
                tags = [word for word in line.split() if word.startswith('#')]
                hashtags[current_category].extend(tags)
        
        return hashtags
    
    def _parse_suggestions(self, text: str) -> Dict[str, Any]:
        """Parse campaign suggestions"""
        suggestions = []
        for line in text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                suggestion = line.lstrip('0123456789.)-').strip()
                if suggestion:
                    suggestions.append(suggestion)
        
        return {"suggestions": suggestions}
    
    def _parse_genre_tags(self, text: str) -> Dict[str, Any]:
        """Parse genre and mood tags"""
        genres = []
        moods = []
        
        for line in text.split('\n'):
            line = line.strip()
            if 'genre' in line.lower() or '%' in line:
                # Extract genre with confidence
                genres.append(line)
            elif 'mood' in line.lower() or any(m in line.lower() for m in ['energetic', 'chill', 'dark', 'uplifting']):
                moods.append(line)
        
        return {
            "genres": genres[:5],
            "moods": moods[:10]
        }
    
    async def close(self):
        """Clean up provider resources"""
        pass
