"""
Analytics Service for Fan Club System.

Provides subscription analytics:
- MRR (Monthly Recurring Revenue)
- Churn rate
- Retention cohorts
- LTV (Lifetime Value)
- Revenue forecasting
- Engagement metrics
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract

from app.models.fan_club import (
    FanClub, MembershipTier, Subscription,
    SubscriptionPayment, ExclusiveContent
)
from app.models.user import User

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating fan club analytics and insights."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_mrr(self, fan_club_id: str) -> Dict:
        """
        Calculate Monthly Recurring Revenue (MRR) for a fan club.
        
        Args:
            fan_club_id: Fan club ID
        
        Returns:
            Dict with MRR breakdown by tier and totals
        """
        # Get all active subscriptions
        active_subs = self.db.query(Subscription).filter(
            and_(
                Subscription.fan_club_id == fan_club_id,
                Subscription.status == "active"
            )
        ).all()
        
        mrr_by_tier = {}
        total_mrr = Decimal("0")
        
        for sub in active_subs:
            # Convert yearly to monthly for MRR calculation
            if sub.billing_cycle == "monthly":
                monthly_value = sub.price_paid
            else:  # yearly
                monthly_value = sub.price_paid / 12
            
            tier_name = sub.tier.name
            if tier_name not in mrr_by_tier:
                mrr_by_tier[tier_name] = {
                    "mrr": Decimal("0"),
                    "subscriber_count": 0
                }
            
            mrr_by_tier[tier_name]["mrr"] += monthly_value
            mrr_by_tier[tier_name]["subscriber_count"] += 1
            total_mrr += monthly_value
        
        # Calculate creator payout (90% of MRR)
        creator_mrr = total_mrr * Decimal("0.90")
        platform_fee = total_mrr * Decimal("0.10")
        
        return {
            "total_mrr": float(total_mrr),
            "creator_mrr": float(creator_mrr),
            "platform_fee": float(platform_fee),
            "by_tier": {
                tier: {
                    "mrr": float(data["mrr"]),
                    "subscriber_count": data["subscriber_count"]
                }
                for tier, data in mrr_by_tier.items()
            },
            "total_active_subscribers": len(active_subs),
            "currency": "USD"
        }
    
    def calculate_churn_rate(
        self, 
        fan_club_id: str, 
        period_months: int = 1
    ) -> Dict:
        """
        Calculate churn rate for a given period.
        
        Churn rate = (Canceled subscriptions) / (Total subscriptions at start) * 100
        
        Args:
            fan_club_id: Fan club ID
            period_months: Number of months to analyze (default: 1)
        
        Returns:
            Dict with churn metrics
        """
        period_start = datetime.utcnow() - timedelta(days=30 * period_months)
        period_end = datetime.utcnow()
        
        # Subscriptions at start of period
        start_count = self.db.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.fan_club_id == fan_club_id,
                Subscription.started_at < period_start,
                Subscription.status.in_(["active", "cancelled", "past_due"])
            )
        ).scalar() or 0
        
        # Subscriptions canceled during period
        canceled_count = self.db.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.fan_club_id == fan_club_id,
                Subscription.cancelled_at.between(period_start, period_end)
            )
        ).scalar() or 0
        
        # New subscriptions during period
        new_count = self.db.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.fan_club_id == fan_club_id,
                Subscription.started_at.between(period_start, period_end)
            )
        ).scalar() or 0
        
        # Current active subscriptions
        current_active = self.db.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.fan_club_id == fan_club_id,
                Subscription.status == "active"
            )
        ).scalar() or 0
        
        # Calculate churn rate
        churn_rate = (canceled_count / start_count * 100) if start_count > 0 else 0
        
        # Calculate net growth
        net_growth = new_count - canceled_count
        growth_rate = (net_growth / start_count * 100) if start_count > 0 else 0
        
        return {
            "period_months": period_months,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "subscribers_at_start": start_count,
            "new_subscribers": new_count,
            "canceled_subscribers": canceled_count,
            "current_active_subscribers": current_active,
            "churn_rate_percent": round(churn_rate, 2),
            "net_growth": net_growth,
            "growth_rate_percent": round(growth_rate, 2)
        }
    
    def calculate_retention_cohorts(self, fan_club_id: str) -> List[Dict]:
        """
        Calculate retention cohorts by signup month.
        
        Shows how many subscribers from each month are still active.
        
        Args:
            fan_club_id: Fan club ID
        
        Returns:
            List of cohort data
        """
        # Get all subscriptions grouped by signup month
        cohorts = self.db.query(
            extract('year', Subscription.started_at).label('year'),
            extract('month', Subscription.started_at).label('month'),
            func.count(Subscription.id).label('initial_count'),
            func.sum(
                func.case(
                    (Subscription.status == 'active', 1),
                    else_=0
                )
            ).label('still_active')
        ).filter(
            Subscription.fan_club_id == fan_club_id
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        cohort_data = []
        for cohort in cohorts:
            retention_rate = (cohort.still_active / cohort.initial_count * 100) if cohort.initial_count > 0 else 0
            cohort_data.append({
                "cohort_month": f"{int(cohort.year)}-{int(cohort.month):02d}",
                "initial_subscribers": cohort.initial_count,
                "still_active": cohort.still_active,
                "retention_rate_percent": round(retention_rate, 2),
                "months_since_start": (
                    datetime.utcnow().year - int(cohort.year)
                ) * 12 + (datetime.utcnow().month - int(cohort.month))
            })
        
        return cohort_data
    
    def calculate_ltv(self, fan_club_id: str) -> Dict:
        """
        Calculate average Lifetime Value (LTV) per subscriber.
        
        LTV = Average revenue per subscriber * Average subscription lifetime
        
        Args:
            fan_club_id: Fan club ID
        
        Returns:
            Dict with LTV metrics
        """
        # Get all completed payments
        total_revenue = self.db.query(
            func.sum(SubscriptionPayment.amount)
        ).join(Subscription).filter(
            and_(
                Subscription.fan_club_id == fan_club_id,
                SubscriptionPayment.status == "completed"
            )
        ).scalar() or Decimal("0")
        
        # Get all unique subscribers (past and present)
        total_subscribers = self.db.query(
            func.count(func.distinct(Subscription.subscriber_id))
        ).filter(
            Subscription.fan_club_id == fan_club_id
        ).scalar() or 0
        
        # Calculate average revenue per subscriber
        avg_revenue_per_subscriber = (
            float(total_revenue / total_subscribers)
            if total_subscribers > 0 else 0
        )
        
        # Calculate average subscription length (in months)
        avg_subscription_months = self.db.query(
            func.avg(
                func.extract('epoch', 
                    func.coalesce(Subscription.cancelled_at, func.now()) - 
                    Subscription.started_at
                ) / 2592000  # Convert seconds to months (30 days)
            )
        ).filter(
            Subscription.fan_club_id == fan_club_id
        ).scalar() or 0
        
        # LTV = avg revenue per sub * avg subscription length factor
        ltv = avg_revenue_per_subscriber
        
        # Get current MRR for projections
        mrr_data = self.calculate_mrr(fan_club_id)
        avg_monthly_revenue = (
            mrr_data["total_mrr"] / mrr_data["total_active_subscribers"]
            if mrr_data["total_active_subscribers"] > 0 else 0
        )
        
        # Projected LTV (assuming average 12 month retention)
        projected_ltv = avg_monthly_revenue * 12
        
        return {
            "total_revenue": float(total_revenue),
            "total_subscribers": total_subscribers,
            "avg_revenue_per_subscriber": round(avg_revenue_per_subscriber, 2),
            "avg_subscription_months": round(avg_subscription_months, 2),
            "historical_ltv": round(ltv, 2),
            "projected_ltv_12_months": round(projected_ltv, 2),
            "currency": "USD"
        }
    
    def forecast_revenue(
        self, 
        fan_club_id: str, 
        months: int = 3
    ) -> List[Dict]:
        """
        Forecast revenue for the next N months.
        
        Uses current MRR + growth trend to project future revenue.
        
        Args:
            fan_club_id: Fan club ID
            months: Number of months to forecast
        
        Returns:
            List of monthly revenue forecasts
        """
        # Get current MRR
        current_mrr_data = self.calculate_mrr(fan_club_id)
        current_mrr = Decimal(str(current_mrr_data["total_mrr"]))
        
        # Calculate growth rate from last 3 months
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        
        new_subs_last_3m = self.db.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.fan_club_id == fan_club_id,
                Subscription.started_at >= three_months_ago
            )
        ).scalar() or 0
        
        canceled_subs_last_3m = self.db.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.fan_club_id == fan_club_id,
                Subscription.cancelled_at >= three_months_ago
            )
        ).scalar() or 0
        
        total_subs = current_mrr_data["total_active_subscribers"]
        
        # Calculate monthly growth rate
        net_growth = new_subs_last_3m - canceled_subs_last_3m
        monthly_growth_rate = (net_growth / 3 / total_subs) if total_subs > 0 else 0.05  # Default 5%
        
        # Generate forecast
        forecasts = []
        projected_mrr = current_mrr
        
        for month_offset in range(1, months + 1):
            forecast_date = datetime.utcnow() + timedelta(days=30 * month_offset)
            
            # Apply growth rate
            projected_mrr = projected_mrr * (1 + Decimal(str(monthly_growth_rate)))
            
            # Creator payout (90%)
            creator_revenue = projected_mrr * Decimal("0.90")
            
            forecasts.append({
                "month": forecast_date.strftime("%Y-%m"),
                "projected_mrr": round(float(projected_mrr), 2),
                "creator_revenue": round(float(creator_revenue), 2),
                "growth_rate_applied": round(monthly_growth_rate * 100, 2),
                "confidence": "medium" if month_offset <= 3 else "low"
            })
        
        return forecasts
    
    def get_engagement_metrics(self, fan_club_id: str) -> Dict:
        """
        Calculate engagement metrics for exclusive content.
        
        Args:
            fan_club_id: Fan club ID
        
        Returns:
            Dict with engagement data
        """
        # Count exclusive content items
        exclusive_content_count = self.db.query(
            func.count(ExclusiveContent.id)
        ).filter(
            ExclusiveContent.fan_club_id == fan_club_id
        ).scalar() or 0
        
        # Get total views
        total_views = self.db.query(
            func.sum(ExclusiveContent.view_count)
        ).filter(
            ExclusiveContent.fan_club_id == fan_club_id
        ).scalar() or 0
        
        # Get active subscribers
        active_subs = self.db.query(func.count(Subscription.id)).filter(
            and_(
                Subscription.fan_club_id == fan_club_id,
                Subscription.status == "active"
            )
        ).scalar() or 0
        
        # Calculate engagement rate
        avg_views_per_content = (
            total_views / exclusive_content_count
            if exclusive_content_count > 0 else 0
        )
        
        engagement_rate = (
            (avg_views_per_content / active_subs * 100)
            if active_subs > 0 else 0
        )
        
        return {
            "exclusive_content_count": exclusive_content_count,
            "total_views": total_views,
            "active_subscribers": active_subs,
            "avg_views_per_content": round(avg_views_per_content, 2),
            "engagement_rate_percent": round(engagement_rate, 2),
            "views_per_subscriber": round(total_views / active_subs, 2) if active_subs > 0 else 0
        }
    
    def get_comprehensive_analytics(self, fan_club_id: str) -> Dict:
        """
        Get all analytics in one call.
        
        Args:
            fan_club_id: Fan club ID
        
        Returns:
            Dict with all analytics data
        """
        return {
            "mrr": self.calculate_mrr(fan_club_id),
            "churn": self.calculate_churn_rate(fan_club_id, period_months=1),
            "ltv": self.calculate_ltv(fan_club_id),
            "retention_cohorts": self.calculate_retention_cohorts(fan_club_id),
            "revenue_forecast": self.forecast_revenue(fan_club_id, months=3),
            "engagement": self.get_engagement_metrics(fan_club_id),
            "generated_at": datetime.utcnow().isoformat()
        }
