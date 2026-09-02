"""
Redis Caching Layer for Messaging System
Task 14.1: Implement Redis caching layer

Caches frequently accessed data to reduce database load:
- Conversation metadata (5 min TTL)
- User message settings (1 hour TTL)
- Unread counts (invalidated on read)
- Recent messages (2 min TTL)
"""
import json
import logging
from typing import Optional, Dict, Any
from datetime import timedelta

logger = logging.getLogger(__name__)

# TTL constants
CONVERSATION_TTL = 300       # 5 minutes
SETTINGS_TTL = 3600          # 1 hour
UNREAD_COUNT_TTL = 60        # 1 minute
RECENT_MESSAGES_TTL = 120    # 2 minutes


class MessagingCache:
    """
    Redis caching service for messaging system.
    Falls back gracefully if Redis is unavailable.
    """
    
    def __init__(self, redis_client=None):
        """
        Initialize with optional Redis client.
        If no client provided, operates in no-cache mode.
        
        Args:
            redis_client: Redis client instance (redis.Redis or aioredis)
        """
        self._redis = redis_client
        self._available = redis_client is not None
    
    def _is_available(self) -> bool:
        """Check if Redis is available."""
        if not self._available or self._redis is None:
            return False
        try:
            self._redis.ping()
            return True
        except Exception:
            self._available = False
            return False
    
    def _get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._is_available():
            return None
        try:
            value = self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis GET failed for key {key}: {e}")
            return None
    
    def _set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL."""
        if not self._is_available():
            return False
        try:
            serialized = json.dumps(value, default=str)
            self._redis.setex(key, timedelta(seconds=ttl), serialized)
            return True
        except Exception as e:
            logger.warning(f"Redis SET failed for key {key}: {e}")
            return False
    
    def _delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._is_available():
            return False
        try:
            self._redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE failed for key {key}: {e}")
            return False
    
    def _increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache."""
        if not self._is_available():
            return None
        try:
            return self._redis.incrby(key, amount)
        except Exception as e:
            logger.warning(f"Redis INCR failed for key {key}: {e}")
            return None
    
    # =========================================================================
    # Conversation caching
    # =========================================================================
    
    def cache_conversation(self, conversation_id: str, data: Dict) -> bool:
        """
        Cache conversation metadata.
        
        Args:
            conversation_id: Conversation UUID
            data: Serializable conversation dict
            
        Returns:
            True if cached successfully
        """
        key = f"conv:{conversation_id}"
        return self._set(key, data, CONVERSATION_TTL)
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Get cached conversation metadata.
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            Cached conversation dict or None if not cached
        """
        key = f"conv:{conversation_id}"
        return self._get(key)
    
    def invalidate_conversation(self, conversation_id: str) -> bool:
        """
        Remove conversation from cache (call after updates).
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            True if invalidated
        """
        key = f"conv:{conversation_id}"
        return self._delete(key)
    
    # =========================================================================
    # User settings caching
    # =========================================================================
    
    def cache_user_settings(self, user_id: str, settings: Dict) -> bool:
        """
        Cache user message settings.
        
        Args:
            user_id: User UUID
            settings: Settings dict (message_filter, read_receipts_enabled, etc.)
            
        Returns:
            True if cached
        """
        key = f"msg_settings:{user_id}"
        return self._set(key, settings, SETTINGS_TTL)
    
    def get_user_settings(self, user_id: str) -> Optional[Dict]:
        """
        Get cached user settings.
        
        Args:
            user_id: User UUID
            
        Returns:
            Settings dict or None
        """
        key = f"msg_settings:{user_id}"
        return self._get(key)
    
    def invalidate_user_settings(self, user_id: str) -> bool:
        """
        Remove user settings from cache.
        
        Args:
            user_id: User UUID
        """
        key = f"msg_settings:{user_id}"
        return self._delete(key)
    
    # =========================================================================
    # Unread count caching
    # =========================================================================
    
    def get_unread_count(self, user_id: str, conversation_id: Optional[str] = None) -> Optional[int]:
        """
        Get cached unread message count.
        
        Args:
            user_id: User UUID
            conversation_id: Optional specific conversation UUID
            
        Returns:
            Unread count or None if not cached
        """
        if conversation_id:
            key = f"unread:{user_id}:{conversation_id}"
        else:
            key = f"unread_total:{user_id}"
        
        value = self._get(key)
        return int(value) if value is not None else None
    
    def set_unread_count(self, user_id: str, count: int, conversation_id: Optional[str] = None) -> bool:
        """
        Cache unread count.
        
        Args:
            user_id: User UUID
            count: Unread message count
            conversation_id: Optional specific conversation UUID
        """
        if conversation_id:
            key = f"unread:{user_id}:{conversation_id}"
        else:
            key = f"unread_total:{user_id}"
        
        return self._set(key, count, UNREAD_COUNT_TTL)
    
    def increment_unread(self, user_id: str, conversation_id: str, amount: int = 1) -> Optional[int]:
        """
        Increment unread count for a user in a conversation.
        Also invalidates the total count.
        
        Args:
            user_id: User UUID
            conversation_id: Conversation UUID
            amount: Amount to increment (default 1)
            
        Returns:
            New unread count or None
        """
        key = f"unread:{user_id}:{conversation_id}"
        
        # Invalidate total count since it changed
        self._delete(f"unread_total:{user_id}")
        
        if not self._is_available():
            return None
        
        try:
            # Set with TTL if doesn't exist, otherwise just increment
            if not self._redis.exists(key):
                self._redis.setex(key, timedelta(seconds=UNREAD_COUNT_TTL), amount)
                return amount
            else:
                return self._redis.incrby(key, amount)
        except Exception as e:
            logger.warning(f"Redis increment failed: {e}")
            return None
    
    def reset_unread(self, user_id: str, conversation_id: str) -> bool:
        """
        Reset unread count to 0 when messages are read.
        
        Args:
            user_id: User UUID
            conversation_id: Conversation UUID
        """
        key = f"unread:{user_id}:{conversation_id}"
        total_key = f"unread_total:{user_id}"
        
        self._delete(key)
        self._delete(total_key)  # Invalidate total too
        return True
    
    # =========================================================================
    # Recent messages caching
    # =========================================================================
    
    def cache_recent_messages(self, conversation_id: str, messages: list) -> bool:
        """
        Cache recent messages for a conversation.
        
        Args:
            conversation_id: Conversation UUID
            messages: List of serializable message dicts
        """
        key = f"msgs:{conversation_id}:recent"
        return self._set(key, messages, RECENT_MESSAGES_TTL)
    
    def get_recent_messages(self, conversation_id: str) -> Optional[list]:
        """
        Get cached recent messages.
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            List of messages or None
        """
        key = f"msgs:{conversation_id}:recent"
        return self._get(key)
    
    def invalidate_messages(self, conversation_id: str) -> bool:
        """
        Invalidate cached messages when new message is sent.
        
        Args:
            conversation_id: Conversation UUID
        """
        key = f"msgs:{conversation_id}:recent"
        return self._delete(key)


def get_messaging_cache() -> MessagingCache:
    """
    Factory function to get MessagingCache instance.
    Tries to connect to Redis, falls back to no-cache mode.
    
    Returns:
        MessagingCache instance
    """
    try:
        import redis
        import os
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
        client.ping()  # Test connection
        logger.info("✅ Redis cache connected")
        return MessagingCache(redis_client=client)
    except Exception as e:
        logger.warning(f"⚠️ Redis not available, running without cache: {e}")
        return MessagingCache(redis_client=None)


# Singleton instance
_cache_instance: Optional[MessagingCache] = None


def get_cache() -> MessagingCache:
    """Get or create the singleton cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = get_messaging_cache()
    return _cache_instance
