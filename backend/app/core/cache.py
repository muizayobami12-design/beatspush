"""
Caching utilities for analytics and other operations.

Supports:
- Redis-based caching
- TTL configuration
- Cache invalidation
- Key namespacing
"""

import logging
import json
from functools import wraps
from datetime import datetime, timedelta
from typing import Optional, Any, Callable
from decimal import Decimal

logger = logging.getLogger(__name__)

# Redis client (lazy loaded)
_redis_client = None


def get_redis_client():
    """Get or initialize Redis client."""
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        import redis
        from app.core.config import settings
        
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Test connection
        _redis_client.ping()
        logger.info("✓ Redis connection established")
        return _redis_client
    
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Caching disabled.")
        return None


class CacheKeyBuilder:
    """Build cache keys with namespacing."""
    
    PREFIX = "beatspush:analytics"
    
    @staticmethod
    def mrr(fan_club_id: int, month: str) -> str:
        """Cache key for MRR."""
        return f"{CacheKeyBuilder.PREFIX}:mrr:{fan_club_id}:{month}"
    
    @staticmethod
    def arpu(fan_club_id: int, days: int) -> str:
        """Cache key for ARPU."""
        return f"{CacheKeyBuilder.PREFIX}:arpu:{fan_club_id}:{days}"
    
    @staticmethod
    def ltv(fan_club_id: int) -> str:
        """Cache key for LTV."""
        return f"{CacheKeyBuilder.PREFIX}:ltv:{fan_club_id}"
    
    @staticmethod
    def revenue_trend(fan_club_id: int, months: int) -> str:
        """Cache key for revenue trend."""
        return f"{CacheKeyBuilder.PREFIX}:trend:{fan_club_id}:{months}"
    
    @staticmethod
    def churn_rate(fan_club_id: int, month: str) -> str:
        """Cache key for churn rate."""
        return f"{CacheKeyBuilder.PREFIX}:churn:{fan_club_id}:{month}"
    
    @staticmethod
    def churn_reasons(fan_club_id: int) -> str:
        """Cache key for churn reasons."""
        return f"{CacheKeyBuilder.PREFIX}:churn_reasons:{fan_club_id}"
    
    @staticmethod
    def retention_cohort(fan_club_id: int, month: str) -> str:
        """Cache key for retention cohort."""
        return f"{CacheKeyBuilder.PREFIX}:retention_cohort:{fan_club_id}:{month}"
    
    @staticmethod
    def retention_matrix(fan_club_id: int, months: int) -> str:
        """Cache key for retention matrix."""
        return f"{CacheKeyBuilder.PREFIX}:retention_matrix:{fan_club_id}:{months}"
    
    @staticmethod
    def forecast(fan_club_id: int, months: int, method: str) -> str:
        """Cache key for forecast."""
        return f"{CacheKeyBuilder.PREFIX}:forecast:{fan_club_id}:{months}:{method}"
    
    @staticmethod
    def creator_metrics(creator_id: int, days: int) -> str:
        """Cache key for creator metrics."""
        return f"{CacheKeyBuilder.PREFIX}:creator:{creator_id}:{days}"
    
    @staticmethod
    def fan_club_metrics(fan_club_id: int, days: int) -> str:
        """Cache key for fan club metrics."""
        return f"{CacheKeyBuilder.PREFIX}:fc_metrics:{fan_club_id}:{days}"
    
    @staticmethod
    def dashboard_summary(fan_club_id: int) -> str:
        """Cache key for dashboard summary."""
        return f"{CacheKeyBuilder.PREFIX}:dashboard:{fan_club_id}"


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""
    
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def cache_result(
    ttl: int = 3600,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results in Redis.
    
    Args:
        ttl: Time to live in seconds (default: 1 hour)
        key_builder: Function to build cache key from function args
    
    Usage:
        @cache_result(ttl=3600, key_builder=lambda args: f"key:{args[0]}")
        def get_data(id):
            return expensive_operation()
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            redis_client = get_redis_client()
            
            # If Redis unavailable, run function normally
            if redis_client is None:
                return func(*args, **kwargs)
            
            try:
                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    # Default: use function name and all args
                    cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # Try to get from cache
                cached = redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached)
                
                # Execute function
                logger.debug(f"Cache miss: {cache_key}, executing...")
                result = func(*args, **kwargs)
                
                # Store in cache
                try:
                    cached_data = json.dumps(result, cls=DecimalEncoder)
                    redis_client.setex(cache_key, ttl, cached_data)
                    logger.debug(f"Cached: {cache_key} (TTL: {ttl}s)")
                except Exception as e:
                    logger.warning(f"Failed to cache {cache_key}: {e}")
                
                return result
            
            except Exception as e:
                logger.error(f"Cache error in {func.__name__}: {e}")
                # Fall back to function execution
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


class CacheManager:
    """Manage cache operations."""
    
    @staticmethod
    def invalidate(pattern: str):
        """
        Invalidate cache keys matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "beatspush:analytics:mrr:*")
        """
        redis_client = get_redis_client()
        
        if redis_client is None:
            return
        
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys matching {pattern}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
    
    @staticmethod
    def invalidate_fan_club(fan_club_id: int):
        """Invalidate all analytics cache for a fan club."""
        pattern = f"{CacheKeyBuilder.PREFIX}:*:{fan_club_id}:*"
        CacheManager.invalidate(pattern)
        
        # Also invalidate related patterns
        CacheManager.invalidate(f"{CacheKeyBuilder.PREFIX}:dashboard:{fan_club_id}")
    
    @staticmethod
    def invalidate_creator(creator_id: int):
        """Invalidate all analytics cache for a creator."""
        pattern = f"{CacheKeyBuilder.PREFIX}:creator:{creator_id}:*"
        CacheManager.invalidate(pattern)
    
    @staticmethod
    def invalidate_all():
        """Invalidate all analytics cache."""
        CacheManager.invalidate(f"{CacheKeyBuilder.PREFIX}:*")
    
    @staticmethod
    def get_cache_stats() -> dict:
        """Get cache statistics."""
        redis_client = get_redis_client()
        
        if redis_client is None:
            return {'status': 'unavailable'}
        
        try:
            info = redis_client.info()
            keys = redis_client.keys(f"{CacheKeyBuilder.PREFIX}:*")
            
            return {
                'status': 'connected',
                'cached_analytics': len(keys),
                'memory_used_mb': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands': info.get('total_commands_processed', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def clear_expired():
        """Clear expired cache entries (Redis handles this automatically)."""
        redis_client = get_redis_client()
        
        if redis_client is None:
            return
        
        try:
            # Redis automatically cleans up expired keys
            # This is just for logging purposes
            logger.info("Redis expiry check triggered")
        except Exception as e:
            logger.error(f"Error checking expired cache: {e}")


def cache_warmup_analytics(fan_club_id: int, db_session):
    """
    Pre-populate cache with commonly accessed analytics.
    
    Called when fan club is accessed to improve response times.
    """
    redis_client = get_redis_client()
    
    if redis_client is None:
        return
    
    try:
        from app.services.analytics_service import AnalyticsService
        
        analytics = AnalyticsService(db_session)
        
        # Warm up MRR
        mrr_data = analytics.get_mrr(fan_club_id=fan_club_id)
        cache_key = CacheKeyBuilder.mrr(fan_club_id, mrr_data['month'])
        redis_client.setex(
            cache_key,
            3600,
            json.dumps(mrr_data, cls=DecimalEncoder)
        )
        
        # Warm up trend
        trend_data = analytics.get_revenue_trend(12, fan_club_id=fan_club_id)
        cache_key = CacheKeyBuilder.revenue_trend(fan_club_id, 12)
        redis_client.setex(
            cache_key,
            3600,
            json.dumps(trend_data, cls=DecimalEncoder)
        )
        
        logger.debug(f"Warmed up cache for fan_club {fan_club_id}")
    
    except Exception as e:
        logger.warning(f"Failed to warm up cache: {e}")


def invalidate_on_subscription_change(fan_club_id: int):
    """
    Invalidate relevant cache when subscription changes occur.
    
    Called when:
    - New subscription created
    - Subscription cancelled
    - Subscription tier changed
    """
    CacheManager.invalidate_fan_club(fan_club_id)
    logger.info(f"Invalidated analytics cache for fan_club {fan_club_id}")


def invalidate_on_payment(fan_club_id: int):
    """
    Invalidate revenue-related cache when payment occurs.
    
    Called when:
    - Payment processed
    - Payment refunded
    - Payment failed then succeeded
    """
    # Invalidate MRR, ARPU, LTV, trends, forecast
    CacheManager.invalidate(f"{CacheKeyBuilder.PREFIX}:mrr:{fan_club_id}:*")
    CacheManager.invalidate(f"{CacheKeyBuilder.PREFIX}:arpu:{fan_club_id}:*")
    CacheManager.invalidate(f"{CacheKeyBuilder.PREFIX}:ltv:{fan_club_id}")
    CacheManager.invalidate(f"{CacheKeyBuilder.PREFIX}:trend:{fan_club_id}:*")
    CacheManager.invalidate(f"{CacheKeyBuilder.PREFIX}:forecast:{fan_club_id}:*")
    CacheManager.invalidate(f"{CacheKeyBuilder.PREFIX}:dashboard:{fan_club_id}")
    
    logger.info(f"Invalidated revenue cache for fan_club {fan_club_id}")
