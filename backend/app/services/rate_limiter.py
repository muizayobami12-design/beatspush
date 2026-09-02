"""
Rate Limiting Service
Redis-based rate limiting for API endpoints
"""

import time
from typing import Optional
from redis import Redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis-based rate limiter for preventing abuse"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        # Test connection to ensure Redis is available
        try:
            self.redis.ping()
            logger.info("Rate limiter initialized with Redis connection")
        except Exception as e:
            logger.warning(f"Rate limiter Redis connection failed: {e}")
    
    async def check_rate_limit(
        self,
        identifier: str,
        action: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if identifier has exceeded rate limit
        
        Args:
            identifier: IP address or user ID
            action: Action being rate limited (e.g., "login", "upload")
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            (allowed: bool, remaining: int)
        """
        key = f"rate_limit:{action}:{identifier}"
        current_time = int(time.time())
        window_start = current_time - window_seconds
        
        try:
            # Remove old entries outside the window
            self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count requests in current window
            request_count = self.redis.zcard(key)
            
            if request_count >= max_requests:
                remaining = 0
                return False, remaining
            
            # Add current request with unique member (timestamp + microsecond counter)
            import random
            unique_member = f"{current_time}.{random.randint(1000, 9999)}"
            self.redis.zadd(key, {unique_member: current_time})
            self.redis.expire(key, window_seconds)
            
            remaining = max_requests - request_count - 1
            return True, remaining
            
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            # On error, allow the request (fail open)
            return True, max_requests
    
    async def is_allowed(
        self,
        identifier: str,
        action: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Simple check if action is allowed
        
        Returns:
            True if within limit, False if exceeded
        """
        allowed, _ = await self.check_rate_limit(
            identifier, action, max_requests, window_seconds
        )
        return allowed
    
    async def get_remaining(
        self,
        identifier: str,
        action: str,
        max_requests: int,
        window_seconds: int
    ) -> int:
        """
        Get remaining requests in current window
        
        Returns:
            Number of requests remaining
        """
        _, remaining = await self.check_rate_limit(
            identifier, action, max_requests, window_seconds
        )
        return remaining
    
    def clear_rate_limit(self, identifier: str, action: str):
        """
        Clear rate limit for identifier (e.g., after successful login)
        """
        key = f"rate_limit:{action}:{identifier}"
        self.redis.delete(key)


# Rate limit configurations
RATE_LIMITS = {
    "login": {
        "max_requests": 5,
        "window_seconds": 900  # 15 minutes
    },
    "register": {
        "max_requests": 3,
        "window_seconds": 3600  # 1 hour
    },
    "password_reset": {
        "max_requests": 3,
        "window_seconds": 3600  # 1 hour
    },
    "upload": {
        "max_requests": 10,
        "window_seconds": 3600  # 1 hour
    },
    "api_call": {
        "max_requests": 100,
        "window_seconds": 60  # 1 minute
    },
    "ai_generation": {
        "max_requests": 20,
        "window_seconds": 3600  # 1 hour (free tier)
    }
}


def get_rate_limit_config(action: str) -> dict:
    """Get rate limit configuration for action"""
    return RATE_LIMITS.get(action, {
        "max_requests": 60,
        "window_seconds": 60
    })
