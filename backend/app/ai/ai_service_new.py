"""
AI Service - Unified AI service with provider abstraction
Supports free Hugging Face API and fallback providers
"""
import time
from typing import Dict, Any, Optional
from redis import Redis
from sqlalchemy.orm import Session

from .providers import AIProvider, AIRequestType, AIResponse, HuggingFaceProvider
from .providers.base import ProviderException, ProviderBusyException
from .response_cache import ResponseCache
from app.core.config import settings


class AIService:
    """
    Unified AI service with provider abstraction and caching
    """
    
    def __init__(self, redis: Redis, db: Optional[Session] = None):
        """
        Initialize AI service
        
        Args:
            redis: Redis client for caching
            db: Database session (optional, for analytics)
        """
        self.redis = redis
        self.db = db
        self.cache = ResponseCache(redis)
        
        # Initialize providers in priority order
        self.providers = [
            HuggingFaceProvider(api_url=settings.HUGGINGFACE_API_URL)
        ]
        # Sort by priority
        self.providers.sort(key=lambda p: p.priority)
    
    async def generate(
        self,
        request_type: AIRequestType,
        params: Dict[str, Any],
        user_id: Optional[int] = None,
        bypass_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Generate AI content with caching and fallback
        
        Args:
            request_type: Type of content to generate
            params: Generation parameters
            user_id: User ID (for analytics)
            bypass_cache: Skip cache lookup
            
        Returns:
            Generated content dict with metadata
        """
        start_time = time.time()
        
        # Check cache first (unless bypassed)
        if not bypass_cache:
            cache_key = self.cache.build_key(request_type, params)
            cached = await self.cache.get(cache_key)
            
            if cached:
                await self.cache.record_hit()
                response_time_ms = int((time.time() - start_time) * 1000)
                
                return {
                    "success": True,
                    "content": cached.get("content", {}),
                    "metadata": {
                        "provider": cached.get("provider", "cache"),
                        "model": cached.get("model", "cached"),
                        "response_time_ms": response_time_ms,
                        "cached": True
                    }
                }
        
        # Cache miss - generate with providers
        await self.cache.record_miss()
        
        # Try each provider in priority order
        last_error = None
        for provider in self.providers:
            if not provider.is_available():
                continue
            
            retries = 0
            max_retries = settings.AI_MAX_RETRIES
            
            while retries <= max_retries:
                try:
                    # Generate content
                    result = await provider.generate(request_type, params)
                    
                    # Cache the result
                    cache_data = {
                        "content": result.content,
                        "provider": result.provider,
                        "model": result.model
                    }
                    
                    if not bypass_cache:
                        cache_key = self.cache.build_key(request_type, params)
                        await self.cache.set(cache_key, cache_data)
                    
                    # Calculate response time
                    response_time_ms = int((time.time() - start_time) * 1000)
                    
                    # Log analytics (if db available)
                    if self.db and user_id:
                        await self._log_request(
                            user_id=user_id,
                            request_type=request_type,
                            provider=result.provider,
                            response_time_ms=response_time_ms,
                            success=True
                        )
                    
                    return {
                        "success": True,
                        "content": result.content,
                        "metadata": {
                            "provider": result.provider,
                            "model": result.model,
                            "response_time_ms": response_time_ms,
                            "cached": False
                        }
                    }
                
                except ProviderBusyException as e:
                    # Provider is busy (503), retry with exponential backoff
                    retries += 1
                    if retries <= max_retries:
                        wait_time = 2 ** (retries - 1)  # 1s, 2s, 4s
                        print(f"Provider busy, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        last_error = e
                        break
                
                except ProviderException as e:
                    # Provider failed, try next provider
                    last_error = e
                    print(f"Provider {provider.name} failed: {e}")
                    break
        
        # All providers failed
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if self.db and user_id:
            await self._log_request(
                user_id=user_id,
                request_type=request_type,
                provider="none",
                response_time_ms=response_time_ms,
                success=False,
                error_message=str(last_error)
            )
        
        raise Exception(f"AI service unavailable: {last_error}")
    
    async def _log_request(
        self,
        user_id: int,
        request_type: AIRequestType,
        provider: str,
        response_time_ms: int,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log AI request for analytics"""
        # TODO: Implement database logging
        pass
    
    async def close(self):
        """Close all provider sessions"""
        for provider in self.providers:
            if hasattr(provider, 'close'):
                await provider.close()
