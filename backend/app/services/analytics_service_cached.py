"""
Cached analytics service wrapper.

Wraps AnalyticsService with Redis caching for improved performance.
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, List
from decimal import Decimal

from sqlalchemy.orm import Session

from app.services.analytics_service import AnalyticsService
from app.core.cache import (
    cache_result,
    CacheKeyBuilder,
    DecimalEncoder,
    get_redis_client
)

logger = logging.getLogger(__name__)
import json


class CachedAnalyticsService(AnalyticsService):
    """
    Analytics service with Redis caching.
    
    Caches results for:
    - MRR: 1 hour TTL
    - ARPU: 4 hours TTL
    - LTV: 6 hours TTL
    - Trends: 6 hours TTL
    - Churn: 6 hours TTL
    - Retention: 12 hours TTL
    - Forecast: 12 hours TTL
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.redis_client = get_redis_client()
    
    def _get_cached(self, key: str, ttl: int):
        """Get value from cache if available."""
        if self.redis_client is None:
            return None
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"Cache hit: {key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        return None
    
    def _set_cached(self, key: str, value: any, ttl: int):
        """Store value in cache."""
        if self.redis_client is None:
            return
        
        try:
            cached_data = json.dumps(value, cls=DecimalEncoder)
            self.redis_client.setex(key, ttl, cached_data)
            logger.debug(f"Cached {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    # ==================== CACHED REVENUE METHODS ====================
    
    def get_mrr(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> Dict:
        """Get MRR with caching (1 hour TTL)."""
        
        if start_date is None:
            now = datetime.utcnow().date()
            start_date = date(now.year, now.month, 1)
        
        # Build cache key
        month_str = start_date.strftime('%Y-%m')
        cache_key = CacheKeyBuilder.mrr(fan_club_id or 0, month_str)
        
        # Try cache
        cached = self._get_cached(cache_key, 3600)
        if cached:
            return cached
        
        # Execute
        result = super().get_mrr(start_date, end_date, fan_club_id, creator_id)
        
        # Cache result
        self._set_cached(cache_key, result, 3600)
        
        return result
    
    def get_arpu(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        fan_club_id: Optional[int] = None
    ) -> Dict:
        """Get ARPU with caching (4 hours TTL)."""
        
        if start_date is None:
            start_date = datetime.utcnow().date() - __import__('datetime').timedelta(days=30)
        
        if end_date is None:
            end_date = datetime.utcnow().date()
        
        days = (end_date - start_date).days or 30
        cache_key = CacheKeyBuilder.arpu(fan_club_id or 0, days)
        
        # Try cache
        cached = self._get_cached(cache_key, 14400)
        if cached:
            return cached
        
        # Execute
        result = super().get_arpu(start_date, end_date, fan_club_id)
        
        # Cache
        self._set_cached(cache_key, result, 14400)
        
        return result
    
    def get_ltv(
        self,
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> Dict:
        """Get LTV with caching (6 hours TTL)."""
        
        cache_key = CacheKeyBuilder.ltv(fan_club_id or 0)
        
        # Try cache
        cached = self._get_cached(cache_key, 21600)
        if cached:
            return cached
        
        # Execute
        result = super().get_ltv(fan_club_id, creator_id)
        
        # Cache
        self._set_cached(cache_key, result, 21600)
        
        return result
    
    def get_revenue_trend(
        self,
        months: int = 12,
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> List[Dict]:
        """Get revenue trend with caching (6 hours TTL)."""
        
        cache_key = CacheKeyBuilder.revenue_trend(fan_club_id or 0, months)
        
        # Try cache
        cached = self._get_cached(cache_key, 21600)
        if cached:
            return cached
        
        # Execute
        result = super().get_revenue_trend(months, fan_club_id, creator_id)
        
        # Cache
        self._set_cached(cache_key, result, 21600)
        
        return result
    
    # ==================== CACHED CHURN METHODS ====================
    
    def get_churn_rate(
        self,
        month: Optional[date] = None,
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> Dict:
        """Get churn rate with caching (6 hours TTL)."""
        
        if month is None:
            month = datetime.utcnow().date()
        
        month_str = month.strftime('%Y-%m')
        cache_key = CacheKeyBuilder.churn_rate(fan_club_id or 0, month_str)
        
        # Try cache
        cached = self._get_cached(cache_key, 21600)
        if cached:
            return cached
        
        # Execute
        result = super().get_churn_rate(month, fan_club_id, creator_id)
        
        # Cache
        self._set_cached(cache_key, result, 21600)
        
        return result
    
    def get_churn_reasons(
        self,
        limit: int = 10,
        fan_club_id: Optional[int] = None
    ) -> List[Dict]:
        """Get churn reasons with caching (12 hours TTL)."""
        
        cache_key = CacheKeyBuilder.churn_reasons(fan_club_id or 0)
        
        # Try cache
        cached = self._get_cached(cache_key, 43200)
        if cached:
            return cached
        
        # Execute
        result = super().get_churn_reasons(limit, fan_club_id)
        
        # Cache
        self._set_cached(cache_key, result, 43200)
        
        return result
    
    # ==================== CACHED RETENTION METHODS ====================
    
    def get_retention_cohort(
        self,
        cohort_month: date,
        months_back: int = 12,
        fan_club_id: Optional[int] = None
    ) -> Dict:
        """Get retention cohort with caching (12 hours TTL)."""
        
        month_str = cohort_month.strftime('%Y-%m')
        cache_key = CacheKeyBuilder.retention_cohort(fan_club_id or 0, month_str)
        
        # Try cache
        cached = self._get_cached(cache_key, 43200)
        if cached:
            return cached
        
        # Execute
        result = super().get_retention_cohort(cohort_month, months_back, fan_club_id)
        
        # Cache
        self._set_cached(cache_key, result, 43200)
        
        return result
    
    def get_retention_matrix(
        self,
        months: int = 12,
        fan_club_id: Optional[int] = None
    ) -> List[Dict]:
        """Get retention matrix with caching (12 hours TTL)."""
        
        cache_key = CacheKeyBuilder.retention_matrix(fan_club_id or 0, months)
        
        # Try cache
        cached = self._get_cached(cache_key, 43200)
        if cached:
            return cached
        
        # Execute
        result = super().get_retention_matrix(months, fan_club_id)
        
        # Cache
        self._set_cached(cache_key, result, 43200)
        
        return result
    
    # ==================== CACHED FORECAST METHODS ====================
    
    def forecast_revenue(
        self,
        months_ahead: int = 6,
        method: str = 'linear',
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> List[Dict]:
        """Get revenue forecast with caching (12 hours TTL)."""
        
        cache_key = CacheKeyBuilder.forecast(fan_club_id or 0, months_ahead, method)
        
        # Try cache
        cached = self._get_cached(cache_key, 43200)
        if cached:
            return cached
        
        # Execute
        result = super().forecast_revenue(months_ahead, method, fan_club_id, creator_id)
        
        # Cache
        self._set_cached(cache_key, result, 43200)
        
        return result
    
    # ==================== CACHED METRICS METHODS ====================
    
    def get_creator_metrics(
        self,
        creator_id: int,
        days: int = 30
    ) -> Dict:
        """Get creator metrics with caching (4 hours TTL)."""
        
        cache_key = CacheKeyBuilder.creator_metrics(creator_id, days)
        
        # Try cache
        cached = self._get_cached(cache_key, 14400)
        if cached:
            return cached
        
        # Execute
        result = super().get_creator_metrics(creator_id, days)
        
        # Cache
        self._set_cached(cache_key, result, 14400)
        
        return result
    
    def get_fan_club_metrics(
        self,
        fan_club_id: int,
        days: int = 30
    ) -> Dict:
        """Get fan club metrics with caching (4 hours TTL)."""
        
        cache_key = CacheKeyBuilder.fan_club_metrics(fan_club_id, days)
        
        # Try cache
        cached = self._get_cached(cache_key, 14400)
        if cached:
            return cached
        
        # Execute
        result = super().get_fan_club_metrics(fan_club_id, days)
        
        # Cache
        self._set_cached(cache_key, result, 14400)
        
        return result
