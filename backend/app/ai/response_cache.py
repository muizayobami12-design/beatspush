"""
Response Cache
Redis-based caching for AI responses
"""
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime
from redis import Redis
from .providers.base import AIRequestType, AIResponse


class ResponseCache:
    """Redis-based response caching for AI generation"""
    
    TTL_DAYS = 7
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = self.TTL_DAYS * 24 * 60 * 60  # Convert to seconds
    
    def build_key(
        self,
        request_type: AIRequestType,
        params: Dict[str, Any]
    ) -> str:
        """
        Build cache key from request type and parameters
        
        Args:
            request_type: Type of AI request
            params: Request parameters
            
        Returns:
            Cache key string
        """
        # Normalize params (remove user-specific data, lowercase strings)
        normalized = self._normalize_params(params)
        
        # Create hash from normalized params
        param_str = json.dumps(normalized, sort_keys=True)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        
        return f"ai_cache:{request_type.value}:{param_hash}"
    
    async def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response dict or None
        """
        try:
            data = self.redis.get(cache_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        cache_key: str,
        response: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """
        Cache response
        
        Args:
            cache_key: Cache key
            response: Response to cache
            ttl: Time to live in seconds (optional)
        """
        try:
            ttl = ttl or self.ttl
            self.redis.setex(
                cache_key,
                ttl,
                json.dumps(response)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def _normalize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize parameters for consistent caching
        
        Args:
            params: Raw parameters
            
        Returns:
            Normalized parameters
        """
        # Fields to exclude from caching (user-specific)
        exclude_fields = {'user_id', 'request_id', 'timestamp', 'session_id'}
        
        normalized = {}
        for key, value in params.items():
            if key in exclude_fields or value is None:
                continue
            
            # Lowercase strings for consistency
            if isinstance(value, str):
                normalized[key] = value.lower().strip()
            elif isinstance(value, list):
                # Sort lists and lowercase string elements
                normalized[key] = sorted([
                    v.lower() if isinstance(v, str) else v
                    for v in value
                ])
            else:
                normalized[key] = value
        
        return normalized
    
    async def get_hit_rate(self) -> float:
        """
        Calculate cache hit rate
        
        Returns:
            Hit rate as percentage (0-100)
        """
        try:
            hits = int(self.redis.get('ai_cache:hits') or 0)
            misses = int(self.redis.get('ai_cache:misses') or 0)
            total = hits + misses
            
            if total == 0:
                return 0.0
            
            return (hits / total) * 100
        except Exception:
            return 0.0
    
    async def record_hit(self):
        """Record a cache hit"""
        try:
            self.redis.incr('ai_cache:hits')
        except Exception:
            pass
    
    async def record_miss(self):
        """Record a cache miss"""
        try:
            self.redis.incr('ai_cache:misses')
        except Exception:
            pass
