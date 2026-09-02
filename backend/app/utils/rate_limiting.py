"""
Rate limiting utilities for messaging API endpoints
Task 15.3: Add rate limiting to API endpoints

Uses in-memory token bucket algorithm as a fallback when Redis is unavailable.
Limits:
- POST /messages: 30 requests per minute
- File uploads: 10 requests per minute
- GET /conversations: 60 requests per minute
"""
import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Tuple
from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    """
    Simple sliding window rate limiter using in-memory storage.
    Thread-safe using a Lock.
    Falls back gracefully when Redis is not available.
    """
    
    def __init__(self):
        # {key: [(timestamp, count), ...]}
        self._windows: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
    
    def is_allowed(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if request is allowed under the rate limit.
        
        Args:
            key: Unique key for this limit (e.g., "user_id:action")
            limit: Maximum requests allowed in the window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = time.time()
        window_start = now - window_seconds
        
        with self._lock:
            # Clean old entries
            self._windows[key] = [
                ts for ts in self._windows[key] 
                if ts > window_start
            ]
            
            current_count = len(self._windows[key])
            
            if current_count >= limit:
                return False, 0
            
            # Add current request
            self._windows[key].append(now)
            return True, limit - current_count - 1
    
    def cleanup(self):
        """Remove all expired entries to free memory."""
        now = time.time()
        with self._lock:
            keys_to_delete = []
            for key, timestamps in self._windows.items():
                # Keep keys that have entries in the last hour
                recent = [ts for ts in timestamps if ts > now - 3600]
                if not recent:
                    keys_to_delete.append(key)
                else:
                    self._windows[key] = recent
            for key in keys_to_delete:
                del self._windows[key]


# Global rate limiter instance
_limiter = InMemoryRateLimiter()


def check_rate_limit(
    user_id: str,
    action: str,
    limit: int,
    window_seconds: int = 60
) -> None:
    """
    Check rate limit and raise 429 if exceeded.
    
    Args:
        user_id: User making the request
        action: Action identifier (e.g., "send_message", "upload_file")
        limit: Maximum requests per window
        window_seconds: Time window in seconds (default 60)
        
    Raises:
        HTTPException 429: If rate limit exceeded
    """
    key = f"{user_id}:{action}"
    allowed, remaining = _limiter.is_allowed(key, limit, window_seconds)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {limit} {action} requests per {window_seconds} seconds.",
            headers={"Retry-After": str(window_seconds)}
        )


# Convenience functions for specific endpoints
def check_message_send_limit(user_id: str) -> None:
    """30 messages per minute."""
    check_rate_limit(user_id, "send_message", limit=30, window_seconds=60)


def check_file_upload_limit(user_id: str) -> None:
    """10 uploads per minute."""
    check_rate_limit(user_id, "upload_file", limit=10, window_seconds=60)


def check_conversation_list_limit(user_id: str) -> None:
    """60 list requests per minute."""
    check_rate_limit(user_id, "list_conversations", limit=60, window_seconds=60)
