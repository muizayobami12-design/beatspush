"""
Base AI Provider Interface
Abstract base class for all AI providers
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class AIRequestType(str, Enum):
    """Types of AI generation requests"""
    TITLE = "title"
    DESCRIPTION = "description"
    CAPTION = "caption"
    HASHTAGS = "hashtags"
    PRESS_RELEASE = "press_release"
    CAMPAIGN_SUGGESTIONS = "campaign_suggestions"
    GENRE_TAGS = "genre_tags"
    AUDIENCE_INSIGHTS = "audience_insights"


class AIResponse(BaseModel):
    """AI generation response"""
    content: Dict[str, Any]
    provider: str
    model: str
    from_cache: bool = False


class ProviderException(Exception):
    """Base exception for provider errors"""
    pass


class ProviderBusyException(ProviderException):
    """Provider is temporarily busy (503)"""
    pass


class ProviderUnavailableException(ProviderException):
    """Provider is unavailable"""
    pass


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self):
        self.name: str = "base"
        self.priority: int = 999
    
    @abstractmethod
    async def generate(
        self,
        request_type: AIRequestType,
        params: Dict[str, Any]
    ) -> AIResponse:
        """
        Generate AI content
        
        Args:
            request_type: Type of content to generate
            params: Request parameters
            
        Returns:
            AIResponse with generated content
            
        Raises:
            ProviderException: If generation fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def get_model_for_type(self, request_type: AIRequestType) -> str:
        """
        Get optimal model for request type
        
        Args:
            request_type: Type of content to generate
            
        Returns:
            Model identifier string
        """
        pass
    
    def _get_max_length(self, request_type: AIRequestType) -> int:
        """Get maximum generation length for request type"""
        length_map = {
            AIRequestType.TITLE: 50,
            AIRequestType.DESCRIPTION: 400,
            AIRequestType.CAPTION: 300,
            AIRequestType.HASHTAGS: 150,
            AIRequestType.PRESS_RELEASE: 600,
            AIRequestType.CAMPAIGN_SUGGESTIONS: 500,
            AIRequestType.GENRE_TAGS: 100,
            AIRequestType.AUDIENCE_INSIGHTS: 500,
        }
        return length_map.get(request_type, 300)
