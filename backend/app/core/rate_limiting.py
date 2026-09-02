"""
AI Rate Limiting
Redis-based rate limiter for AI requests with tier support
"""
from datetime import datetime, timedelta
from typing import Optional
from redis import Redis
from pydantic import BaseModel
from enum import Enum


class UserTier(str, Enum):
    """User tier enum"""
    FREE = "free"
    PREMIUM = "premium"


class QuotaStatus(BaseModel):
    """Quota status response"""
    allowed: bool
    remaining: Optional[int]  # None for premium (unlimited)
    reset_at: Optional[datetime]  # None for premium
    tier: UserTier
    exceeded: bool = False


class AIRateLimiter:
    """Redis-based rate limiter for AI requests"""
    
    FREE_TIER_DAILY_LIMIT = 20
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def check_and_increment(
        self,
        user_id: int,
        user_tier: UserTier
    ) -> QuotaStatus:
        """
        Check quota and increment if allowed
        
        Args:
            user_id: User ID
            user_tier: User tier (free/premium)
            
        Returns:
            QuotaStatus with quota information
        """
        # Premium users have unlimited access
        if user_tier == UserTier.PREMIUM:
            return QuotaStatus(
                allowed=True,
                remaining=None,
                reset_at=None,
                tier=UserTier.PREMIUM
            )
        
        # Free tier: check and increment
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"ai_quota:{user_id}:{today}"
        
        try:
            # Atomic increment
            current = self.redis.incr(key)
            
            # Set expiry if this is first request of the day
            if current == 1:
                midnight = self._get_next_midnight_utc()
                ttl = int((midnight - datetime.utcnow()).total_seconds())
                self.redis.expire(key, ttl)
            
            # Check limit
            if current > self.FREE_TIER_DAILY_LIMIT:
                return QuotaStatus(
                    allowed=False,
                    remaining=0,
                    reset_at=self._get_next_midnight_utc(),
                    tier=UserTier.FREE,
                    exceeded=True
                )
            
            return QuotaStatus(
                allowed=True,
                remaining=self.FREE_TIER_DAILY_LIMIT - current,
                reset_at=self._get_next_midnight_utc(),
                tier=UserTier.FREE
            )
        except Exception as e:
            print(f"Rate limiter error: {e}")
            # Fail open - allow request if Redis is down
            return QuotaStatus(
                allowed=True,
                remaining=self.FREE_TIER_DAILY_LIMIT,
                reset_at=self._get_next_midnight_utc(),
                tier=user_tier
            )
    
    async def get_quota_info(
        self,
        user_id: int,
        user_tier: UserTier
    ) -> QuotaStatus:
        """
        Get current quota status without incrementing
        
        Args:
            user_id: User ID
            user_tier: User tier
            
        Returns:
            QuotaStatus
        """
        if user_tier == UserTier.PREMIUM:
            return QuotaStatus(
                allowed=True,
                remaining=None,
                reset_at=None,
                tier=UserTier.PREMIUM
            )
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"ai_quota:{user_id}:{today}"
        
        try:
            current = self.redis.get(key)
            current = int(current) if current else 0
            
            return QuotaStatus(
                allowed=current < self.FREE_TIER_DAILY_LIMIT,
                remaining=max(0, self.FREE_TIER_DAILY_LIMIT - current),
                reset_at=self._get_next_midnight_utc(),
                tier=UserTier.FREE
            )
        except Exception:
            return QuotaStatus(
                allowed=True,
                remaining=self.FREE_TIER_DAILY_LIMIT,
                reset_at=self._get_next_midnight_utc(),
                tier=user_tier
            )
    
    def _get_next_midnight_utc(self) -> datetime:
        """Get next midnight UTC"""
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
        return midnight
