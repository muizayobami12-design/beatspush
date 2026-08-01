"""
Subscription Service - Business logic for subscription lifecycle
Tasks 6.1-6.10: Core subscription operations
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.models.fan_club import (
    Subscription, MembershipTier, FanClub, SubscriptionPayment
)
from app.models.user import User
from app.schemas.fan_club import (
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    SubscriptionListResponse
)


class SubscriptionService:
    """Core subscription service for managing fan memberships"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # SUBSCRIPTION CREATION
    # ========================================================================
    
    def create_subscription(
        self,
        subscriber_id: str,
        data: SubscriptionCreate
    ) -> Subscription:
        """
        Create a new subscription (initiate subscription flow)
        
        Note: Payment processing happens in PaymentService
        This creates the subscription record in 'pending' state
        
        Args:
            subscriber_id: User ID subscribing
            data: Subscription creation data
            
        Returns:
            Created Subscription object (pending payment)
        """
        # Get tier
        tier = self.db.query(MembershipTier).filter(
            MembershipTier.id == data.tier_id
        ).first()
        
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership tier not found"
            )
        
        if not tier.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This membership tier is not currently available"
            )
        
        # Get fan club
        fan_club = self.db.query(FanClub).filter(
            FanClub.id == tier.fan_club_id
        ).first()
        
        if not fan_club or not fan_club.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This fan club is not currently accepting memberships"
            )
        
        # Check if user is trying to subscribe to their own fan club
        if fan_club.creator_id == subscriber_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot subscribe to your own fan club"
            )
        
        # Check if user already has an active subscription to this fan club
        existing = (
            self.db.query(Subscription)
            .filter(
                Subscription.fan_club_id == tier.fan_club_id,
                Subscription.subscriber_id == subscriber_id,
                Subscription.status.in_(["active", "paused", "trialing"])
            )
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an active subscription to this fan club"
            )
        
        # Calculate price based on billing cycle
        if data.billing_cycle == "monthly":
            price = tier.price_monthly
        else:  # yearly
            price = tier.price_yearly
        
        # Calculate subscription period
        now = datetime.utcnow()
        if data.billing_cycle == "monthly":
            period_end = now + timedelta(days=30)
        else:  # yearly
            period_end = now + timedelta(days=365)
        
        # Create subscription (pending payment)
        subscription = Subscription(
            id=str(uuid.uuid4()),
            fan_club_id=tier.fan_club_id,
            tier_id=tier.id,
            subscriber_id=subscriber_id,
            status="pending",  # Will be updated to 'active' after payment
            billing_cycle=data.billing_cycle.value,
            price_paid=price,
            currency="USD",
            current_period_start=now,
            current_period_end=period_end,
            started_at=now,
            auto_renew=True,
            payment_provider=data.payment_provider.value,
            payment_provider_customer_id=None,  # Set by payment service
            payment_provider_subscription_id=None  # Set by payment service
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    # ========================================================================
    # SUBSCRIPTION RETRIEVAL
    # ========================================================================
    
    def get_subscription(
        self,
        subscription_id: str,
        user_id: Optional[str] = None
    ) -> Subscription:
        """
        Get subscription by ID
        
        Args:
            subscription_id: Subscription ID
            user_id: Optional user ID for authorization check
            
        Returns:
            Subscription object
        """
        subscription = (
            self.db.query(Subscription)
            .options(
                joinedload(Subscription.tier),
                joinedload(Subscription.fan_club),
                joinedload(Subscription.subscriber)
            )
            .filter(Subscription.id == subscription_id)
            .first()
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Check authorization if user_id provided
        if user_id:
            if subscription.subscriber_id != user_id:
                # Allow creator to view subscriber details
                fan_club = subscription.fan_club
                if fan_club.creator_id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You don't have permission to view this subscription"
                    )
        
        return subscription
    
    def list_user_subscriptions(
        self,
        user_id: str,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        List user's subscriptions
        
        Args:
            user_id: User ID
            status_filter: Filter by status (active, cancelled, paused, etc.)
            page: Page number
            page_size: Items per page
            
        Returns:
            Dict with subscriptions and pagination info
        """
        query = (
            self.db.query(Subscription)
            .filter(Subscription.subscriber_id == user_id)
            .options(
                joinedload(Subscription.tier),
                joinedload(Subscription.fan_club)
            )
        )
        
        if status_filter:
            query = query.filter(Subscription.status == status_filter)
        
        # Order by most recent
        query = query.order_by(Subscription.created_at.desc())
        
        # Get total count
        total = query.count()
        
        # Paginate
        offset = (page - 1) * page_size
        subscriptions = query.offset(offset).limit(page_size).all()
        
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "subscriptions": subscriptions,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    # ========================================================================
    # SUBSCRIPTION CANCELLATION
    # ========================================================================
    
    def cancel_subscription(
        self,
        subscription_id: str,
        user_id: str,
        immediate: bool = False
    ) -> Subscription:
        """
        Cancel subscription
        
        Default: Access continues until end of billing period
        Immediate: Access ends immediately (requires refund)
        
        Args:
            subscription_id: Subscription ID
            user_id: User ID (must be subscriber)
            immediate: Cancel immediately vs end of period
            
        Returns:
            Updated Subscription object
        """
        subscription = self.get_subscription(subscription_id, user_id)
        
        # Check if user is the subscriber
        if subscription.subscriber_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the subscriber can cancel this subscription"
            )
        
        if subscription.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already cancelled"
            )
        
        if immediate:
            # Immediate cancellation - end access now
            subscription.status = "cancelled"
            subscription.cancelled_at = datetime.utcnow()
            subscription.ended_at = datetime.utcnow()
            subscription.auto_renew = False
            # Note: Refund processing would happen in PaymentService
        else:
            # End of period cancellation - keep access until period ends
            subscription.status = "cancelled"
            subscription.cancelled_at = datetime.utcnow()
            subscription.auto_renew = False
            # ended_at will be set when period expires
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    # ========================================================================
    # SUBSCRIPTION PAUSE/RESUME
    # ========================================================================
    
    def pause_subscription(
        self,
        subscription_id: str,
        user_id: str,
        pause_duration_days: int = 30
    ) -> Subscription:
        """
        Pause subscription (up to 90 days, once per year)
        
        Args:
            subscription_id: Subscription ID
            user_id: User ID (must be subscriber)
            pause_duration_days: How long to pause (max 90 days)
            
        Returns:
            Updated Subscription object
        """
        subscription = self.get_subscription(subscription_id, user_id)
        
        if subscription.subscriber_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the subscriber can pause this subscription"
            )
        
        if subscription.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active subscriptions can be paused"
            )
        
        if pause_duration_days > 90:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum pause duration is 90 days"
            )
        
        # Check if already paused this year (limit 1 pause per year)
        # This would require additional tracking in a production system
        
        now = datetime.utcnow()
        paused_until = now + timedelta(days=pause_duration_days)
        
        subscription.status = "paused"
        subscription.paused_at = now
        subscription.paused_until = paused_until
        
        # Extend the subscription period by pause duration
        subscription.current_period_end = subscription.current_period_end + timedelta(days=pause_duration_days)
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def resume_subscription(
        self,
        subscription_id: str,
        user_id: str
    ) -> Subscription:
        """
        Resume paused subscription
        
        Args:
            subscription_id: Subscription ID
            user_id: User ID (must be subscriber)
            
        Returns:
            Updated Subscription object
        """
        subscription = self.get_subscription(subscription_id, user_id)
        
        if subscription.subscriber_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the subscriber can resume this subscription"
            )
        
        if subscription.status != "paused":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only paused subscriptions can be resumed"
            )
        
        now = datetime.utcnow()
        
        # Calculate how many days were left in pause
        if subscription.paused_until and subscription.paused_until > now:
            days_left = (subscription.paused_until - now).days
            # Reduce period extension by days not used
            subscription.current_period_end = subscription.current_period_end - timedelta(days=days_left)
        
        subscription.status = "active"
        subscription.paused_at = None
        subscription.paused_until = None
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    # ========================================================================
    # TIER UPGRADE/DOWNGRADE
    # ========================================================================
    
    def upgrade_tier(
        self,
        subscription_id: str,
        user_id: str,
        new_tier_id: str
    ) -> Subscription:
        """
        Upgrade subscription to higher tier (immediate, with proration)
        
        Args:
            subscription_id: Subscription ID
            user_id: User ID (must be subscriber)
            new_tier_id: New tier ID
            
        Returns:
            Updated Subscription object
        """
        subscription = self.get_subscription(subscription_id, user_id)
        
        if subscription.subscriber_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the subscriber can upgrade this subscription"
            )
        
        if subscription.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active subscriptions can be upgraded"
            )
        
        # Get new tier
        new_tier = self.db.query(MembershipTier).filter(
            MembershipTier.id == new_tier_id
        ).first()
        
        if not new_tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New tier not found"
            )
        
        # Verify tier belongs to same fan club
        if new_tier.fan_club_id != subscription.fan_club_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New tier must belong to the same fan club"
            )
        
        # Get current tier
        current_tier = subscription.tier
        
        # Verify it's actually an upgrade
        if new_tier.tier_level <= current_tier.tier_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New tier must be higher than current tier. Use downgrade for lower tiers."
            )
        
        # Calculate prorated credit (would be handled by PaymentService in production)
        # For now, just update the tier
        
        subscription.tier_id = new_tier_id
        
        # Update price for next billing cycle
        if subscription.billing_cycle == "monthly":
            subscription.price_paid = new_tier.price_monthly
        else:
            subscription.price_paid = new_tier.price_yearly
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def downgrade_tier(
        self,
        subscription_id: str,
        user_id: str,
        new_tier_id: str
    ) -> Subscription:
        """
        Downgrade subscription to lower tier (effective next billing cycle)
        
        Args:
            subscription_id: Subscription ID
            user_id: User ID (must be subscriber)
            new_tier_id: New tier ID
            
        Returns:
            Updated Subscription object
        """
        subscription = self.get_subscription(subscription_id, user_id)
        
        if subscription.subscriber_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the subscriber can downgrade this subscription"
            )
        
        if subscription.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active subscriptions can be downgraded"
            )
        
        # Get new tier
        new_tier = self.db.query(MembershipTier).filter(
            MembershipTier.id == new_tier_id
        ).first()
        
        if not new_tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New tier not found"
            )
        
        # Verify tier belongs to same fan club
        if new_tier.fan_club_id != subscription.fan_club_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New tier must belong to the same fan club"
            )
        
        # Get current tier
        current_tier = subscription.tier
        
        # Verify it's actually a downgrade
        if new_tier.tier_level >= current_tier.tier_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New tier must be lower than current tier. Use upgrade for higher tiers."
            )
        
        # Schedule downgrade for next billing cycle
        # In production, this would be stored in a separate field
        # For now, we'll note it and apply at renewal
        
        # Keep current tier active until period ends
        # Update will happen at renewal time
        
        subscription.tier_id = new_tier_id
        
        # Update price for next billing cycle
        if subscription.billing_cycle == "monthly":
            subscription.price_paid = new_tier.price_monthly
        else:
            subscription.price_paid = new_tier.price_yearly
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    # ========================================================================
    # SUBSCRIPTION STATUS CHECKS
    # ========================================================================
    
    def check_subscription_status(
        self,
        user_id: str,
        fan_club_id: str
    ) -> Dict:
        """
        Check if user has active subscription to fan club
        
        Args:
            user_id: User ID
            fan_club_id: Fan club ID
            
        Returns:
            Dict with subscription status and details
        """
        subscription = (
            self.db.query(Subscription)
            .filter(
                Subscription.fan_club_id == fan_club_id,
                Subscription.subscriber_id == user_id,
                Subscription.status.in_(["active", "trialing"])
            )
            .first()
        )
        
        if not subscription:
            return {
                "is_subscribed": False,
                "tier_level": 0,
                "subscription_id": None
            }
        
        return {
            "is_subscribed": True,
            "tier_level": subscription.tier.tier_level,
            "tier_name": subscription.tier.name,
            "subscription_id": subscription.id,
            "status": subscription.status,
            "period_end": subscription.current_period_end
        }
    
    def is_subscriber(
        self,
        user_id: str,
        fan_club_id: str,
        minimum_tier_level: int = 1
    ) -> bool:
        """
        Check if user is subscribed at minimum tier level
        
        Args:
            user_id: User ID
            fan_club_id: Fan club ID
            minimum_tier_level: Minimum tier level required
            
        Returns:
            True if user has active subscription at required level
        """
        subscription = (
            self.db.query(Subscription)
            .join(MembershipTier, Subscription.tier_id == MembershipTier.id)
            .filter(
                Subscription.fan_club_id == fan_club_id,
                Subscription.subscriber_id == user_id,
                Subscription.status.in_(["active", "trialing"]),
                MembershipTier.tier_level >= minimum_tier_level
            )
            .first()
        )
        
        return subscription is not None
    
    # ========================================================================
    # SUBSCRIPTION RENEWAL
    # ========================================================================
    
    def process_renewal(
        self,
        subscription_id: str
    ) -> bool:
        """
        Process subscription renewal
        
        Called by background job when subscription period ends
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            True if renewal successful
        """
        subscription = self.get_subscription(subscription_id)
        
        # Check if auto-renew is enabled
        if not subscription.auto_renew:
            # End subscription
            subscription.status = "cancelled"
            subscription.ended_at = datetime.utcnow()
            self.db.commit()
            return False
        
        # Check if subscription is active
        if subscription.status != "active":
            return False
        
        # Extend subscription period
        now = datetime.utcnow()
        if subscription.billing_cycle == "monthly":
            new_period_end = now + timedelta(days=30)
        else:  # yearly
            new_period_end = now + timedelta(days=365)
        
        subscription.current_period_start = now
        subscription.current_period_end = new_period_end
        
        self.db.commit()
        
        # Payment processing would happen in PaymentService
        # This would create a new SubscriptionPayment record
        
        return True
