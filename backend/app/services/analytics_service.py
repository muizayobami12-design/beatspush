"""
Fan club analytics service.

Provides metrics:
- MRR (Monthly Recurring Revenue)
- ARPU (Average Revenue Per User)
- Churn rate & analysis
- Retention cohorts
- Revenue forecasting
- Engagement metrics
"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from collections import defaultdict
import statistics

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models.fan_club import (
    Subscription,
    SubscriptionPayment,
    FanClub,
    MembershipTier,
    ExclusiveContent
)
from app.models.user import User
from app.models.social import Post

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Comprehensive analytics for fan club system.
    
    Metrics:
    - Revenue: MRR, ARPU, LTV
    - Churn: Monthly rate, reasons, trends
    - Retention: Cohorts, repeat rate
    - Engagement: Activity, content consumption
    - Forecasting: Trends, predictions
    """
    
    def __init__(self, db: Session):
        """Initialize analytics service with database session."""
        self.db = db
    
    # ==================== REVENUE METRICS ====================
    
    def get_mrr(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> Dict:
        """
        Calculate Monthly Recurring Revenue (MRR).
        
        MRR = Sum of all active subscription amounts in a month
        
        Args:
            start_date: Month start (default: current month)
            end_date: Month end
            fan_club_id: Filter by specific fan club
            creator_id: Filter by creator
        
        Returns:
            {
                'mrr': Decimal,
                'active_subscriptions': int,
                'month': str,
                'currency': str,
                'breakdown': {
                    'tier_name': amount,
                    ...
                }
            }
        """
        if start_date is None:
            now = datetime.utcnow().date()
            start_date = date(now.year, now.month, 1)
        
        if end_date is None:
            if start_date.month == 12:
                end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
        
        query = self.db.query(Subscription).filter(
            Subscription.status == "active",
            Subscription.next_billing_date >= start_date,
            Subscription.next_billing_date <= end_date
        )
        
        if fan_club_id:
            query = query.filter(Subscription.fan_club_id == fan_club_id)
        
        if creator_id:
            query = query.join(FanClub).filter(FanClub.creator_id == creator_id)
        
        subscriptions = query.all()
        
        # Calculate MRR by summing all active subscription amounts
        total_mrr = sum(sub.tier.price for sub in subscriptions)
        
        # Breakdown by tier
        tier_breakdown = defaultdict(Decimal)
        for sub in subscriptions:
            tier_breakdown[sub.tier.name] += sub.tier.price
        
        return {
            'mrr': total_mrr,
            'active_subscriptions': len(subscriptions),
            'month': start_date.strftime('%Y-%m'),
            'currency': 'USD',  # Default, should be configurable
            'breakdown': dict(tier_breakdown)
        }
    
    def get_arpu(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        fan_club_id: Optional[int] = None
    ) -> Dict:
        """
        Calculate Average Revenue Per User (ARPU).
        
        ARPU = Total Revenue / Active Subscribers
        
        Args:
            start_date: Period start
            end_date: Period end
            fan_club_id: Filter by fan club
        
        Returns:
            {
                'arpu': Decimal,
                'total_revenue': Decimal,
                'active_users': int,
                'period': str
            }
        """
        if start_date is None:
            start_date = datetime.utcnow().date() - timedelta(days=30)
        
        if end_date is None:
            end_date = datetime.utcnow().date()
        
        query = self.db.query(Subscription).filter(
            Subscription.status == "active",
            Subscription.started_at >= datetime.combine(start_date, datetime.min.time()),
            Subscription.started_at <= datetime.combine(end_date, datetime.max.time())
        )
        
        if fan_club_id:
            query = query.filter(Subscription.fan_club_id == fan_club_id)
        
        subscriptions = query.all()
        
        if not subscriptions:
            return {
                'arpu': Decimal(0),
                'total_revenue': Decimal(0),
                'active_users': 0,
                'period': f"{start_date} to {end_date}"
            }
        
        total_revenue = sum(sub.tier.price for sub in subscriptions)
        unique_users = len(set(sub.subscriber_id for sub in subscriptions))
        arpu = total_revenue / unique_users if unique_users > 0 else Decimal(0)
        
        return {
            'arpu': arpu,
            'total_revenue': total_revenue,
            'active_users': unique_users,
            'period': f"{start_date} to {end_date}"
        }
    
    def get_ltv(
        self,
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> Dict:
        """
        Calculate Lifetime Value (LTV) per subscriber.
        
        LTV = ARPU × Average Customer Lifespan (in months)
        
        Args:
            fan_club_id: Filter by fan club
            creator_id: Filter by creator
        
        Returns:
            {
                'ltv': Decimal,
                'avg_arpu': Decimal,
                'avg_lifetime_months': float,
                'sample_size': int
            }
        """
        query = self.db.query(Subscription).filter(
            Subscription.status.in_(["active", "cancelled"])
        )
        
        if fan_club_id:
            query = query.filter(Subscription.fan_club_id == fan_club_id)
        
        if creator_id:
            query = query.join(FanClub).filter(FanClub.creator_id == creator_id)
        
        subscriptions = query.all()
        
        if not subscriptions:
            return {
                'ltv': Decimal(0),
                'avg_arpu': Decimal(0),
                'avg_lifetime_months': 0,
                'sample_size': 0
            }
        
        # Calculate average revenue per subscription
        avg_arpu = sum(sub.tier.price for sub in subscriptions) / len(subscriptions)
        
        # Calculate average subscription length in months
        lifetimes = []
        for sub in subscriptions:
            if sub.cancelled_at:
                lifetime = (sub.cancelled_at - sub.started_at).days / 30
            else:
                lifetime = (datetime.utcnow() - sub.started_at).days / 30
            lifetimes.append(lifetime)
        
        avg_lifetime = statistics.mean(lifetimes) if lifetimes else 0
        ltv = avg_arpu * avg_lifetime
        
        return {
            'ltv': ltv,
            'avg_arpu': avg_arpu,
            'avg_lifetime_months': avg_lifetime,
            'sample_size': len(subscriptions)
        }
    
    def get_revenue_trend(
        self,
        months: int = 12,
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get monthly revenue trend for N months.
        
        Args:
            months: Number of months to retrieve
            fan_club_id: Filter by fan club
            creator_id: Filter by creator
        
        Returns:
            [
                {
                    'month': '2026-01',
                    'mrr': Decimal,
                    'subscriptions': int,
                    'new_subs': int,
                    'cancelled_subs': int
                },
                ...
            ]
        """
        trend = []
        now = datetime.utcnow().date()
        
        for i in range(months - 1, -1, -1):
            # Calculate month boundaries
            current_month = now - timedelta(days=30 * i)
            month_start = date(current_month.year, current_month.month, 1)
            
            if current_month.month == 12:
                month_end = date(current_month.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(current_month.year, current_month.month + 1, 1) - timedelta(days=1)
            
            # Get MRR
            mrr_data = self.get_mrr(month_start, month_end, fan_club_id, creator_id)
            
            # Get new subscriptions in month
            new_subs = self.db.query(func.count(Subscription.id)).filter(
                Subscription.started_at >= datetime.combine(month_start, datetime.min.time()),
                Subscription.started_at <= datetime.combine(month_end, datetime.max.time()),
                Subscription.status.in_(["active", "cancelled"])
            )
            
            if fan_club_id:
                new_subs = new_subs.filter(Subscription.fan_club_id == fan_club_id)
            
            if creator_id:
                new_subs = new_subs.join(FanClub).filter(FanClub.creator_id == creator_id)
            
            new_subs_count = new_subs.scalar()
            
            # Get cancelled subscriptions in month
            cancelled_subs = self.db.query(func.count(Subscription.id)).filter(
                Subscription.cancelled_at >= datetime.combine(month_start, datetime.min.time()),
                Subscription.cancelled_at <= datetime.combine(month_end, datetime.max.time())
            )
            
            if fan_club_id:
                cancelled_subs = cancelled_subs.filter(Subscription.fan_club_id == fan_club_id)
            
            if creator_id:
                cancelled_subs = cancelled_subs.join(FanClub).filter(FanClub.creator_id == creator_id)
            
            cancelled_subs_count = cancelled_subs.scalar()
            
            trend.append({
                'month': month_start.strftime('%Y-%m'),
                'mrr': mrr_data['mrr'],
                'subscriptions': mrr_data['active_subscriptions'],
                'new_subs': new_subs_count or 0,
                'cancelled_subs': cancelled_subs_count or 0
            })
        
        return trend
    
    # ==================== CHURN METRICS ====================
    
    def get_churn_rate(
        self,
        month: Optional[date] = None,
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> Dict:
        """
        Calculate monthly churn rate.
        
        Churn Rate = Cancelled Subscriptions / Beginning Subscribers × 100
        
        Args:
            month: Month to calculate (default: last month)
            fan_club_id: Filter by fan club
            creator_id: Filter by creator
        
        Returns:
            {
                'churn_rate': float (percentage),
                'churned_subscribers': int,
                'beginning_subscribers': int,
                'ending_subscribers': int,
                'month': str
            }
        """
        if month is None:
            month = datetime.utcnow().date()
            if month.day > 1:
                month = date(month.year, month.month - 1, 1)
        
        month_start = date(month.year, month.month, 1)
        if month.month == 12:
            month_end = date(month.year + 1, 1, 1) - timedelta(days=1)
            next_month_start = date(month.year + 1, 1, 1)
        else:
            month_end = date(month.year, month.month + 1, 1) - timedelta(days=1)
            next_month_start = date(month.year, month.month + 1, 1)
        
        # Get beginning subscribers (active at start of month)
        beginning_query = self.db.query(func.count(Subscription.id)).filter(
            Subscription.started_at <= datetime.combine(month_start, datetime.min.time()),
            or_(
                Subscription.cancelled_at >= datetime.combine(month_start, datetime.max.time()),
                Subscription.cancelled_at == None
            ),
            Subscription.status != "cancelled"
        )
        
        if fan_club_id:
            beginning_query = beginning_query.filter(Subscription.fan_club_id == fan_club_id)
        if creator_id:
            beginning_query = beginning_query.join(FanClub).filter(FanClub.creator_id == creator_id)
        
        beginning_subs = beginning_query.scalar() or 0
        
        # Get churned subscriptions (cancelled in month)
        churned_query = self.db.query(func.count(Subscription.id)).filter(
            Subscription.cancelled_at >= datetime.combine(month_start, datetime.min.time()),
            Subscription.cancelled_at <= datetime.combine(month_end, datetime.max.time())
        )
        
        if fan_club_id:
            churned_query = churned_query.filter(Subscription.fan_club_id == fan_club_id)
        if creator_id:
            churned_query = churned_query.join(FanClub).filter(FanClub.creator_id == creator_id)
        
        churned = churned_query.scalar() or 0
        
        # Get ending subscribers
        ending_query = self.db.query(func.count(Subscription.id)).filter(
            Subscription.started_at <= datetime.combine(month_end, datetime.min.time()),
            or_(
                Subscription.cancelled_at >= datetime.combine(next_month_start, datetime.max.time()),
                Subscription.cancelled_at == None
            ),
            Subscription.status != "cancelled"
        )
        
        if fan_club_id:
            ending_query = ending_query.filter(Subscription.fan_club_id == fan_club_id)
        if creator_id:
            ending_query = ending_query.join(FanClub).filter(FanClub.creator_id == creator_id)
        
        ending_subs = ending_query.scalar() or 0
        
        # Calculate churn rate
        churn_rate = 0
        if beginning_subs > 0:
            churn_rate = (churned / beginning_subs) * 100
        
        return {
            'churn_rate': round(churn_rate, 2),
            'churned_subscribers': churned,
            'beginning_subscribers': beginning_subs,
            'ending_subscribers': ending_subs,
            'month': month_start.strftime('%Y-%m')
        }
    
    def get_churn_reasons(
        self,
        limit: int = 10,
        fan_club_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get most common churn reasons.
        
        Returns:
            [
                {
                    'reason': 'Low engagement',
                    'count': 5,
                    'percentage': 10.5
                },
                ...
            ]
        """
        query = self.db.query(
            Subscription.cancellation_reason,
            func.count(Subscription.id).label('count')
        ).filter(
            Subscription.cancellation_reason != None,
            Subscription.cancelled_at != None
        )
        
        if fan_club_id:
            query = query.filter(Subscription.fan_club_id == fan_club_id)
        
        results = query.group_by(Subscription.cancellation_reason).order_by(
            func.count(Subscription.id).desc()
        ).limit(limit).all()
        
        total = sum(r[1] for r in results)
        
        return [
            {
                'reason': reason or 'Unknown',
                'count': count,
                'percentage': round((count / total * 100) if total > 0 else 0, 2)
            }
            for reason, count in results
        ]
    
    # ==================== RETENTION METRICS ====================
    
    def get_retention_cohort(
        self,
        cohort_month: date,
        months_back: int = 12,
        fan_club_id: Optional[int] = None
    ) -> Dict:
        """
        Calculate retention cohort for subscribers started in a month.
        
        Shows what % of subscribers from cohort_month are still active
        after N months.
        
        Args:
            cohort_month: Month subscribers started
            months_back: Number of months to track back
            fan_club_id: Filter by fan club
        
        Returns:
            {
                'cohort_month': '2025-01',
                'cohort_size': 50,
                'retention': [
                    {'month': 0, 'retained': 50, 'percentage': 100},
                    {'month': 1, 'retained': 45, 'percentage': 90},
                    ...
                ]
            }
        """
        cohort_start = date(cohort_month.year, cohort_month.month, 1)
        if cohort_month.month == 12:
            cohort_end = date(cohort_month.year + 1, 1, 1) - timedelta(days=1)
        else:
            cohort_end = date(cohort_month.year, cohort_month.month + 1, 1) - timedelta(days=1)
        
        # Get cohort size
        cohort_query = self.db.query(Subscription).filter(
            Subscription.started_at >= datetime.combine(cohort_start, datetime.min.time()),
            Subscription.started_at <= datetime.combine(cohort_end, datetime.max.time())
        )
        
        if fan_club_id:
            cohort_query = cohort_query.filter(Subscription.fan_club_id == fan_club_id)
        
        cohort_subs = cohort_query.all()
        cohort_size = len(cohort_subs)
        
        if cohort_size == 0:
            return {
                'cohort_month': cohort_start.strftime('%Y-%m'),
                'cohort_size': 0,
                'retention': []
            }
        
        # Track retention over months
        retention = []
        for month_offset in range(months_back):
            check_date = cohort_start + timedelta(days=30 * month_offset)
            
            retained = 0
            for sub in cohort_subs:
                if sub.cancelled_at is None or sub.cancelled_at > check_date:
                    retained += 1
            
            retention.append({
                'month': month_offset,
                'retained': retained,
                'percentage': round((retained / cohort_size * 100), 2)
            })
        
        return {
            'cohort_month': cohort_start.strftime('%Y-%m'),
            'cohort_size': cohort_size,
            'retention': retention
        }
    
    def get_retention_matrix(
        self,
        months: int = 12,
        fan_club_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get retention matrix for last N months.
        
        Returns:
            [
                {
                    'cohort_month': '2025-01',
                    'cohort_size': 50,
                    'retention_percentages': [100, 90, 85, 82, ...]
                },
                ...
            ]
        """
        cohorts = []
        now = datetime.utcnow().date()
        
        for i in range(months):
            cohort_month = now - timedelta(days=30 * i)
            cohort_data = self.get_retention_cohort(cohort_month, 12, fan_club_id)
            
            if cohort_data['cohort_size'] > 0:
                cohorts.append({
                    'cohort_month': cohort_data['cohort_month'],
                    'cohort_size': cohort_data['cohort_size'],
                    'retention_percentages': [r['percentage'] for r in cohort_data['retention']]
                })
        
        return cohorts
    
    # ==================== FORECASTING ====================
    
    def forecast_revenue(
        self,
        months_ahead: int = 6,
        method: str = 'linear',
        fan_club_id: Optional[int] = None,
        creator_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Forecast future revenue.
        
        Methods:
        - 'linear': Linear regression on historical data
        - 'seasonal': Seasonal adjustment
        
        Args:
            months_ahead: Number of months to forecast
            method: Forecasting method
            fan_club_id: Filter by fan club
            creator_id: Filter by creator
        
        Returns:
            [
                {
                    'month': '2026-09',
                    'forecast_mrr': Decimal,
                    'confidence_interval': (low, high),
                    'method': 'linear'
                },
                ...
            ]
        """
        # Get historical data (last 12 months)
        trend = self.get_revenue_trend(12, fan_club_id, creator_id)
        
        if len(trend) < 3:
            # Not enough data for forecast
            return []
        
        mrr_values = [Decimal(t['mrr']) for t in trend]
        
        if method == 'linear':
            return self._forecast_linear(mrr_values, months_ahead)
        elif method == 'seasonal':
            return self._forecast_seasonal(mrr_values, months_ahead, trend)
        else:
            return []
    
    def _forecast_linear(
        self,
        historical_values: List[Decimal],
        months_ahead: int
    ) -> List[Dict]:
        """Linear regression forecast."""
        if len(historical_values) < 2:
            return []
        
        # Calculate trend using simple linear regression
        n = len(historical_values)
        x_values = list(range(n))
        y_values = [float(v) for v in historical_values]
        
        # Calculate slope and intercept
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # Generate forecast
        forecast = []
        now = datetime.utcnow().date()
        
        for i in range(1, months_ahead + 1):
            predicted_value = slope * (n + i) + intercept
            predicted_value = max(0, predicted_value)  # No negative revenue
            
            # Calculate confidence interval (±20%)
            ci_low = predicted_value * 0.8
            ci_high = predicted_value * 1.2
            
            forecast_month = now + timedelta(days=30 * i)
            
            forecast.append({
                'month': forecast_month.strftime('%Y-%m'),
                'forecast_mrr': Decimal(str(round(predicted_value, 2))),
                'confidence_interval': (
                    Decimal(str(round(ci_low, 2))),
                    Decimal(str(round(ci_high, 2)))
                ),
                'method': 'linear'
            })
        
        return forecast
    
    def _forecast_seasonal(
        self,
        historical_values: List[Decimal],
        months_ahead: int,
        trend_data: List[Dict]
    ) -> List[Dict]:
        """Seasonal forecast with trend adjustment."""
        # For now, use linear as base
        # In production, implement full seasonal decomposition
        return self._forecast_linear(historical_values, months_ahead)
    
    # ==================== ENGAGEMENT METRICS ====================
    
    def get_subscriber_activity(
        self,
        subscriber_id: int,
        days: int = 30
    ) -> Dict:
        """
        Get subscriber activity metrics.
        
        Returns:
            {
                'subscriber_id': 1,
                'content_views': 45,
                'posts_liked': 10,
                'messages_sent': 3,
                'last_activity': '2026-08-31',
                'engagement_score': 85
            }
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Count content views (TODO: implement content view tracking)
        content_views = 0
        
        # Count posts liked (TODO: implement post engagement)
        posts_liked = 0
        
        # Count messages sent (TODO: implement message tracking)
        messages_sent = 0
        
        # Get last activity
        last_activity = None
        
        # Calculate engagement score (0-100)
        engagement_score = min(100, (content_views * 2 + posts_liked + messages_sent) // 2)
        
        return {
            'subscriber_id': subscriber_id,
            'content_views': content_views,
            'posts_liked': posts_liked,
            'messages_sent': messages_sent,
            'last_activity': last_activity,
            'engagement_score': engagement_score,
            'period_days': days
        }
    
    def get_creator_metrics(
        self,
        creator_id: int,
        days: int = 30
    ) -> Dict:
        """
        Get creator fan club metrics.
        
        Returns:
            {
                'creator_id': 1,
                'fan_clubs': 2,
                'total_subscribers': 150,
                'total_mrr': Decimal('1500.00'),
                'average_tier_price': Decimal('10.00'),
                'top_tier': 'Premium',
                'churn_rate': 2.5
            }
        """
        fan_clubs = self.db.query(FanClub).filter(
            FanClub.creator_id == creator_id
        ).all()
        
        total_subscribers = 0
        total_mrr = Decimal(0)
        
        for fan_club in fan_clubs:
            active_subs = self.db.query(func.count(Subscription.id)).filter(
                Subscription.fan_club_id == fan_club.id,
                Subscription.status == "active"
            ).scalar() or 0
            
            total_subscribers += active_subs
            
            # Calculate fan club MRR
            fc_mrr = self.db.query(func.sum(MembershipTier.price)).join(
                Subscription
            ).filter(
                Subscription.fan_club_id == fan_club.id,
                Subscription.status == "active"
            ).scalar() or Decimal(0)
            
            total_mrr += fc_mrr
        
        # Get average tier price
        avg_tier_price = Decimal(0)
        if total_subscribers > 0:
            avg_tier_price = total_mrr / total_subscribers
        
        # Get top tier
        top_tier = self.db.query(MembershipTier).join(
            Subscription
        ).filter(
            FanClub.creator_id == creator_id
        ).group_by(MembershipTier.id).order_by(
            func.count(Subscription.id).desc()
        ).first()
        
        top_tier_name = top_tier.name if top_tier else "N/A"
        
        # Get churn rate (last month)
        month_start = (datetime.utcnow().date()).replace(day=1)
        churn_data = self.get_churn_rate(month_start, None, creator_id)
        
        return {
            'creator_id': creator_id,
            'fan_clubs': len(fan_clubs),
            'total_subscribers': total_subscribers,
            'total_mrr': total_mrr,
            'average_tier_price': avg_tier_price,
            'top_tier': top_tier_name,
            'churn_rate': churn_data['churn_rate'],
            'period_days': days
        }
    
    def get_fan_club_metrics(
        self,
        fan_club_id: int,
        days: int = 30
    ) -> Dict:
        """
        Get fan club metrics.
        
        Returns:
            {
                'fan_club_id': 1,
                'name': 'The Weeknd Premium',
                'total_subscribers': 500,
                'active_subscribers': 450,
                'cancelled_subscribers': 50,
                'mrr': Decimal('5000.00'),
                'growth_rate': 15.2,
                'engagement_rate': 65.5
            }
        """
        fan_club = self.db.query(FanClub).filter(
            FanClub.id == fan_club_id
        ).first()
        
        if not fan_club:
            return {}
        
        # Total and active subscriptions
        total_subs = self.db.query(func.count(Subscription.id)).filter(
            Subscription.fan_club_id == fan_club_id
        ).scalar() or 0
        
        active_subs = self.db.query(func.count(Subscription.id)).filter(
            Subscription.fan_club_id == fan_club_id,
            Subscription.status == "active"
        ).scalar() or 0
        
        cancelled_subs = self.db.query(func.count(Subscription.id)).filter(
            Subscription.fan_club_id == fan_club_id,
            Subscription.status == "cancelled"
        ).scalar() or 0
        
        # Get MRR
        mrr_data = self.get_mrr(fan_club_id=fan_club_id)
        
        # Calculate growth rate
        cutoff = datetime.utcnow() - timedelta(days=days)
        new_subs = self.db.query(func.count(Subscription.id)).filter(
            Subscription.fan_club_id == fan_club_id,
            Subscription.started_at >= cutoff
        ).scalar() or 0
        
        growth_rate = 0
        if active_subs > 0:
            growth_rate = (new_subs / active_subs) * 100
        
        # Calculate engagement (placeholder)
        engagement_rate = 0
        
        return {
            'fan_club_id': fan_club_id,
            'name': fan_club.name,
            'total_subscribers': total_subs,
            'active_subscribers': active_subs,
            'cancelled_subscribers': cancelled_subs,
            'mrr': mrr_data['mrr'],
            'growth_rate': round(growth_rate, 2),
            'engagement_rate': round(engagement_rate, 2),
            'period_days': days
        }
