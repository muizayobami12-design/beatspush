"""
Performance Optimization & Caching Layer
Redis integration, query optimization, CDN configuration
"""

import os
import json
import redis
from typing import Any, Optional, List, Dict
from datetime import timedelta
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

class CacheService:
    """Redis caching service for performance optimization"""
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour
    
    # ============ CACHE OPERATIONS ============
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def delete_pattern(self, pattern: str):
        """Delete keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache delete pattern error: {str(e)}")
            return False
    
    def increment(self, key: str, amount: int = 1):
        """Increment counter"""
        try:
            self.redis_client.incrby(key, amount)
            return True
        except Exception as e:
            logger.error(f"Cache increment error: {str(e)}")
            return False
    
    def get_counter(self, key: str) -> int:
        """Get counter value"""
        try:
            value = self.redis_client.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Cache counter error: {str(e)}")
            return 0
    
    def flush_all(self):
        """Flush all cache (use carefully)"""
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Cache flush error: {str(e)}")
            return False
    
    # ============ LIST OPERATIONS ============
    
    def list_push(self, key: str, values: List[Any]):
        """Push values to list"""
        try:
            for value in values:
                self.redis_client.rpush(key, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.error(f"List push error: {str(e)}")
            return False
    
    def list_get(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get list values"""
        try:
            values = self.redis_client.lrange(key, start, end)
            return [json.loads(v) for v in values]
        except Exception as e:
            logger.error(f"List get error: {str(e)}")
            return []
    
    def list_length(self, key: str) -> int:
        """Get list length"""
        try:
            return self.redis_client.llen(key)
        except Exception as e:
            logger.error(f"List length error: {str(e)}")
            return 0


class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is allowed within rate limit"""
        try:
            current = self.redis.incr(key)
            if current == 1:
                self.redis.expire(key, window)
            return current <= limit
        except Exception as e:
            logger.error(f"Rate limit error: {str(e)}")
            return True  # Allow on error
    
    def get_remaining(self, key: str, limit: int) -> int:
        """Get remaining requests in window"""
        try:
            current = int(self.redis.get(key) or 0)
            return max(0, limit - current)
        except Exception as e:
            logger.error(f"Get remaining error: {str(e)}")
            return limit


# ============ CACHING DECORATOR ============

def cache(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = cache_service.get(cache_key)
            if cached:
                logger.info(f"Cache hit: {cache_key}")
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_service.set(cache_key, result, ttl)
            return result
        
        return async_wrapper
    return decorator


# ============ QUERY OPTIMIZATION ============

class QueryOptimizer:
    """Database query optimization strategies"""
    
    @staticmethod
    def add_indexes():
        """Common database indexes to add"""
        indexes = [
            # User indexes
            ("users", ["email"]),
            ("users", ["username"]),
            ("users", ["user_type"]),
            
            # Content indexes
            ("beats", ["producer_id", "created_at"]),
            ("tracks", ["artist_id", "created_at"]),
            ("mixes", ["dj_id", "created_at"]),
            
            # Transaction indexes
            ("tips", ["receiver_id", "created_at"]),
            ("tips", ["sender_id", "created_at"]),
            ("beat_sales", ["producer_id", "created_at"]),
            
            # Engagement indexes
            ("follows", ["follower_id"]),
            ("follows", ["following_id"]),
            ("likes", ["user_id", "content_type"]),
            
            # Search optimization
            ("beats", ["genre", "created_at"]),
            ("tracks", ["genre", "created_at"]),
            
            # Analytics
            ("plays", ["content_id", "created_at"]),
            ("downloads", ["content_id", "created_at"]),
        ]
        return indexes
    
    @staticmethod
    def optimize_queries():
        """Query optimization recommendations"""
        return {
            "use_pagination": "Always paginate large result sets",
            "select_fields": "Only select needed fields, not *",
            "use_indexes": "Query on indexed columns",
            "eager_load": "Use eager loading for relationships",
            "cache_common": "Cache frequently accessed data",
            "batch_operations": "Batch insert/update operations",
            "avoid_n_plus_1": "Prevent N+1 query problem",
        }


# ============ CDN CONFIGURATION ============

class CDNService:
    """CDN configuration for static assets"""
    
    def __init__(self):
        self.cdn_url = os.getenv("CDN_URL", "https://cdn.beatpush.com")
        self.cloudfront_url = os.getenv("CLOUDFRONT_URL")
    
    def get_asset_url(self, path: str) -> str:
        """Get CDN URL for asset"""
        if self.cloudfront_url:
            return f"{self.cloudfront_url}/{path}"
        return f"{self.cdn_url}/{path}"
    
    def get_image_url(self, image_path: str, size: str = "medium") -> str:
        """Get optimized image URL"""
        # Sizes: thumbnail (100x100), small (300x300), medium (600x600), large (1200x1200)
        return f"{self.get_asset_url(image_path)}?size={size}&quality=80&format=webp"
    
    def get_audio_url(self, audio_path: str) -> str:
        """Get CDN URL for audio streaming"""
        return self.get_asset_url(audio_path)
    
    def get_video_url(self, video_path: str, quality: str = "1080p") -> str:
        """Get CDN URL for video streaming"""
        return f"{self.get_asset_url(video_path)}?quality={quality}"


# ============ PERFORMANCE MONITORING ============

class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def track_request(self, endpoint: str, response_time: float):
        """Track endpoint response time"""
        try:
            key = f"perf:{endpoint}:times"
            self.redis.rpush(key, response_time)
            self.redis.expire(key, 86400)  # Keep for 24 hours
        except Exception as e:
            logger.error(f"Performance tracking error: {str(e)}")
    
    def get_average_response_time(self, endpoint: str) -> float:
        """Get average response time for endpoint"""
        try:
            key = f"perf:{endpoint}:times"
            times = self.redis.lrange(key, 0, -1)
            if times:
                return sum(float(t) for t in times) / len(times)
            return 0.0
        except Exception as e:
            logger.error(f"Get average response time error: {str(e)}")
            return 0.0
    
    def track_db_query(self, query_type: str, duration: float):
        """Track database query performance"""
        try:
            key = f"db:query:{query_type}"
            self.redis.rpush(key, duration)
            self.redis.expire(key, 86400)
        except Exception as e:
            logger.error(f"DB query tracking error: {str(e)}")
    
    def get_slow_queries(self, threshold_ms: float = 100) -> List[Dict]:
        """Get queries exceeding threshold"""
        slow_queries = []
        try:
            keys = self.redis.keys("db:query:*")
            for key in keys:
                times = self.redis.lrange(key, 0, -1)
                slow = [float(t) for t in times if float(t) > threshold_ms]
                if slow:
                    slow_queries.append({
                        "query": key,
                        "slow_count": len(slow),
                        "avg_time_ms": sum(slow) / len(slow)
                    })
        except Exception as e:
            logger.error(f"Get slow queries error: {str(e)}")
        return slow_queries


# Global instances
cache_service = CacheService()
cdn_service = CDNService()

# Create instances when needed
def get_rate_limiter() -> RateLimiter:
    return RateLimiter(cache_service.redis_client)

def get_performance_monitor() -> PerformanceMonitor:
    return PerformanceMonitor(cache_service.redis_client)
