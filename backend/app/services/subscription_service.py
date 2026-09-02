"""
Subscription Service - Business logic for subscription management
Tasks 6.1-6.10: Core subscription operations and lifecycle management
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid
from decimal import Decimal

from app.models.fan_club import (
    Subscription, MembershipTier, FanClub, SubscriptionStatus,
    SubscriptionPayment, PaymentStatus
)
from app.models.user import User
from app.schemas.fan_club import (
    SubscriptionCreate, SubscriptionResponse, SubscriberListResponse
)


class SubscriptionService:
    """Core subscription service for fan club memberships"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # SUBSCRIPTION MANAGEMENT
    # ========================================================================
    
    def create_subscription(
        self,
        subscriber_id: str,
        tier_id: str,
        data: SubscriptionCreate
    ) -> Subscription:
        """
        Create a new subscription to a membership tier.
        
        Business Rules (BR-6.1):
        - Subscriber cannot have existing active subscription to same fan club
        - Tier must be active (is_active = True)
        - Subscription payment will be processed by payment provider
        - Initial subscription period set based on billing_cycle
        - No duplicate active subscriptions per fan club
        
        Args:
            subscriber_id: User subscribing to tier
            tier_id: MembershipTier to subscribe to
            data: Subscription creation data (billing_cycle, trial_days)
            
        Returns:
            Created Subscription object
            
        Raises:
            HTTPException 404: Tier or fan club not found
            HTTPException 400: Active subscription already exists
            HTTPException 403: Tier is not active
        """
        # 1. Validate tier exists and is active
        tier = (
            self.db.query(MembershipTier)
            .options(joinedload(MembershipTier.fan_club))
            .filter(MembershipTier.id == tier_id)
            .first()
        )
        
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership tier not found"
            )
        
        if not tier.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This tier is not currently available for new subscriptions"
            )
        
        # 2. Check for existing active subscription to same fan club
        existing = (
            self.db.query(Subscription)
            .filter(
                and_(
                    Subscription.fan_club_id == tier.fan_club_id,
                    Subscription.subscriber_id == subscriber_id,
                    Subscription.status.in_([
                        SubscriptionStatus.ACTIVE.value,
                        SubscriptionStatus.TRIALING.value
                    ])
                )
            )
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an active subscription to this creator's fan club. Cancel it first or upgrade your tier."
            )
        
        # 3. Validate subscriber exists
        subscriber = self.db.query(User).filter(User.id == subscriber_id).first()
        if not subscriber:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscriber not found"
            )
        
        # 4. Calculate subscription period
        now = datetime.utcnow()
        
        if data.billing_cycle == "monthly":
            period_end = now + timedelta(days=30)
            price_paid = tier.price_monthly
        else:  # yearly
            period_end = now + timedelta(days=365)
            price_paid = tier.price_yearly
        
        # 5. Create subscription
        subscription = Subscription(
            id=str(uuid.uuid4()),
            fan_club_id=tier.fan_club_id,
            tier_id=tier_id,
            subscriber_id=subscriber_id,
            status=SubscriptionStatus.ACTIVE.value,
            billing_cycle=data.billing_cycle,
            price_paid=price_paid,
            currency="USD",
            current_period_start=now,
            current_period_end=period_end,
            next_billing_date=period_end,
            started_at=now,
            auto_renew=data.auto_renew if hasattr(data, 'auto_renew') else True,
            payment_provider=data.payment_provider or "stripe",
            failed_payment_count=0
        )
        
        # 6. Add trial if specified
        if hasattr(data, 'trial_days') and data.trial_days:
            subscription.status = SubscriptionStatus.TRIALING.value
            subscription.trial_ends_at = now + timedelta(days=data.trial_days)
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """
        Retrieve a subscription with all tier details.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            Subscription object with tier details, or None if not found
        """
        return (
            self.db.query(Subscription)
            .options(
                joinedload(Subscription.tier),
                joinedload(Subscription.fan_club),
                joinedload(Subscription.subscriber),
                joinedload(Subscription.payments)
            )
            .filter(Subscription.id == subscription_id)
            .first()
        )
    
    def list_user_subscriptions(
        self,
        subscriber_id: str,
        status_filter: Optional[str] = None
    ) -> List[Subscription]:
        """
        Get all active subscriptions for a user.
        
        Business Rules (BR-6.3):
        - Only returns active, paused, or trialing subscriptions
        - Include tier and fan club details
        - Ordered by created_at descending
        
        Args:
            subscriber_id: User ID
            status_filter: Optional status filter (active, paused, trialing)
            
        Returns:
            List of Subscription objects
        """
        query = (
            self.db.query(Subscription)
            .options(
                joinedload(Subscription.tier),
                joinedload(Subscription.fan_club),
                joinedload(Subscription.payments)
            )
            .filter(Subscription.subscriber_id == subscriber_id)
        )
        
        # Filter by status
        if status_filter:
            query = query.filter(Subscription.status == status_filter)
        else:
            # Default: show active, paused, trialing (not cancelled/past_due)
            query = query.filter(
                Subscription.status.in_([
                    SubscriptionStatus.ACTIVE.value,
                    SubscriptionStatus.PAUSED.value,
                    SubscriptionStatus.TRIALING.value
                ])
            )
        
        return query.order_by(Subscription.created_at.desc()).all()
    
    def cancel_subscription(
        self,
        subscription_id: str,
        reason: Optional[str] = None
    ) -> Subscription:
        """
        Cancel a subscription with end-of-period access.
        
        Business Rules (BR-6.4):
        - Subscription remains ACTIVE until current_period_end
        - Set cancelled_at and ended_at timestamps
        - User retains access until period end
        - Cannot cancel already cancelled subscriptions
        
        Args:
            subscription_id: Subscription to cancel
            reason: Optional cancellation reason for analytics
            
        Returns:
            Updated Subscription object
            
        Raises:
            HTTPException 404: Subscription not found
            HTTPException 400: Subscription already cancelled
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        if subscription.status == SubscriptionStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already cancelled"
            )
        
        # Set cancellation timestamps
        now = datetime.utcnow()
        subscription.cancelled_at = now
        subscription.auto_renew = False
        
        # User has access until end of current period
        subscription.status = SubscriptionStatus.ACTIVE.value
        subscription.ended_at = subscription.current_period_end
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def pause_subscription(
        self,
        subscription_id: str,
        duration_days: int = 30
    ) -> Subscription:
        """
        Pause a subscription (up to 3 months).
        
        Business Rules (BR-6.5):
        - Can only pause for 7-90 days (3 months max)
        - Set status to PAUSED
        - Track pause period with paused_at and paused_until
        - Billing is frozen during pause
        - Cannot pause already paused subscriptions
        
        Args:
            subscription_id: Subscription to pause
            duration_days: Days to pause (7-90)
            
        Returns:
            Updated Subscription object
            
        Raises:
            HTTPException 404: Subscription not found
            HTTPException 400: Invalid pause duration or subscription already paused
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Validate pause duration (7-90 days)
        if duration_days < 7 or duration_days > 90:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pause duration must be between 7 and 90 days (max 3 months)"
            )
        
        if subscription.status == SubscriptionStatus.PAUSED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already paused"
            )
        
        if subscription.status == SubscriptionStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot pause a cancelled subscription"
            )
        
        # Set pause period
        now = datetime.utcnow()
        subscription.status = SubscriptionStatus.PAUSED.value
        subscription.paused_at = now
        subscription.paused_until = now + timedelta(days=duration_days)
        subscription.auto_renew = False
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def resume_subscription(self, subscription_id: str) -> Subscription:
        """
        Resume a paused subscription.
        
        Business Rules (BR-6.6):
        - Can only resume paused subscriptions
        - Reset auto_renew to True
        - Clear pause timestamps
        - Return to ACTIVE status immediately
        
        Args:
            subscription_id: Subscription to resume
            
        Returns:
            Updated Subscription object
            
        Raises:
            HTTPException 404: Subscription not found
            HTTPException 400: Subscription is not paused
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        if subscription.status != SubscriptionStatus.PAUSED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only paused subscriptions can be resumed"
            )
        
        # Resume subscription
        subscription.status = SubscriptionStatus.ACTIVE.value
        subscription.auto_renew = True
        subscription.paused_at = None
        subscription.paused_until = None
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def upgrade_tier(
        self,
        subscription_id: str,
        new_tier_id: str
    ) -> Subscription:
        """
        Upgrade to a higher tier with immediate proration.
        
        Business Rules (BR-6.7):
        - New tier must have higher tier_level than current
        - Proration: charge difference for remaining period
        - Effective immediately
        - Update tier_id and price_paid
        - Calculate proration credit/charge
        
        Args:
            subscription_id: Current subscription
            new_tier_id: New (higher) tier
            
        Returns:
            Updated Subscription object
            
        Raises:
            HTTPException 404: Subscription or tier not found
            HTTPException 400: Invalid tier level or same tier
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        new_tier = (
            self.db.query(MembershipTier)
            .filter(MembershipTier.id == new_tier_id)
            .first()
        )
        
        if not new_tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New tier not found"
            )
        
        # Validate tier upgrade (must be higher level)
        if new_tier.tier_level <= subscription.tier.tier_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New tier must be higher than current tier"
            )
        
        if subscription.status == SubscriptionStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot upgrade a cancelled subscription"
            )
        
        # Calculate proration
        now = datetime.utcnow()
        days_remaining = (subscription.current_period_end - now).days
        total_days = (subscription.current_period_end - subscription.current_period_start).days
        
        if subscription.billing_cycle == "monthly":
            current_daily_rate = subscription.price_paid / Decimal(30)
            new_daily_rate = new_tier.price_monthly / Decimal(30)
        else:  # yearly
            current_daily_rate = subscription.price_paid / Decimal(365)
            new_daily_rate = new_tier.price_yearly / Decimal(365)
        
        proration_credit = current_daily_rate * Decimal(days_remaining)
        proration_charge = new_daily_rate * Decimal(days_remaining)
        proration_amount = proration_charge - proration_credit
        
        # Update subscription
        old_price = subscription.price_paid
        subscription.tier_id = new_tier_id
        
        if subscription.billing_cycle == "monthly":
            subscription.price_paid = new_tier.price_monthly
        else:
            subscription.price_paid = new_tier.price_yearly
        
        subscription.updated_at = now
        
        # TODO: Charge proration_amount via payment provider
        # For now, just track the change
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def downgrade_tier(
        self,
        subscription_id: str,
        new_tier_id: str
    ) -> Subscription:
        """
        Downgrade to a lower tier (effective next billing cycle).
        
        Business Rules (BR-6.8):
        - New tier must have lower tier_level than current
        - Change takes effect at next_billing_date (not immediate)
        - No proration charge (credit applied)
        - Store pending downgrade info
        
        Args:
            subscription_id: Current subscription
            new_tier_id: New (lower) tier
            
        Returns:
            Updated Subscription object
            
        Raises:
            HTTPException 404: Subscription or tier not found
            HTTPException 400: Invalid tier level or same tier
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        new_tier = (
            self.db.query(MembershipTier)
            .filter(MembershipTier.id == new_tier_id)
            .first()
        )
        
        if not new_tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New tier not found"
            )
        
        # Validate tier downgrade (must be lower level)
        if new_tier.tier_level >= subscription.tier.tier_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New tier must be lower than current tier"
            )
        
        if subscription.status == SubscriptionStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot downgrade a cancelled subscription"
            )
        
        # TODO: Store pending_tier_id to apply at next renewal
        # For now, just track the change effective next billing cycle
        subscription.updated_at = datetime.utcnow()
        
        # Downgrade effective at next_billing_date
        # Store this as a pending change
        # (Actual implementation would use a pending_downgrade field)
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return subscription
    
    def check_subscription_status(
        self,
        fan_club_id: str,
        subscriber_id: str
    ) -> bool:
        """
        Check if user has active subscription to fan club.
        
        Business Rules (BR-6.9):
        - Returns True if ACTIVE or TRIALING status
        - Returns False for PAUSED, CANCELLED, PAST_DUE
        - Considers trial_ends_at for trialing subscriptions
        
        Args:
            fan_club_id: Fan club to check
            subscriber_id: User to check
            
        Returns:
            True if user has active/trialing subscription, False otherwise
        """
        now = datetime.utcnow()
        
        subscription = (
            self.db.query(Subscription)
            .filter(
                and_(
                    Subscription.fan_club_id == fan_club_id,
                    Subscription.subscriber_id == subscriber_id,
                    Subscription.status.in_([
                        SubscriptionStatus.ACTIVE.value,
                        SubscriptionStatus.TRIALING.value
                    ])
                )
            )
            .first()
        )
        
        if not subscription:
            return False
        
        # Check if trialing and trial has expired
        if subscription.status == SubscriptionStatus.TRIALING.value:
            if subscription.trial_ends_at and subscription.trial_ends_at < now:
                return False
        
        # Check if in active period
        if subscription.status == SubscriptionStatus.ACTIVE.value:
            if subscription.current_period_end < now and not subscription.cancelled_at:
                # Period ended but not yet auto-renewed
                return False
        
        return True
    
    def validate_subscription_state_transitions(
        self,
        subscription_id: str,
        target_status: str
    ) -> bool:
        """
        Validate allowed state transitions for subscriptions.
        
        Business Rules (BR-6.10):
        
        Valid transitions:
        - TRIALING → ACTIVE (when trial ends or converts)
        - TRIALING → CANCELLED (cancel before trial ends)
        - ACTIVE → PAUSED
        - ACTIVE → CANCELLED
        - PAUSED → ACTIVE (resume)
        - PAUSED → CANCELLED
        - ACTIVE → PAST_DUE (failed payment)
        - PAST_DUE → ACTIVE (payment recovered)
        - PAST_DUE → CANCELLED
        
        Invalid transitions:
        - CANCELLED → anything
        - Same status to same status
        
        Args:
            subscription_id: Subscription to validate
            target_status: Desired target status
            
        Returns:
            True if transition is valid, False otherwise
            
        Raises:
            HTTPException 400: Invalid state transition
        """
        subscription = self.get_subscription(subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        current = subscription.status
        
        # Cannot transition from cancelled
        if current == SubscriptionStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status of a cancelled subscription"
            )
        
        # Cannot transition to same status
        if current == target_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already in this status"
            )
        
        # Define valid transitions
        valid_transitions = {
            SubscriptionStatus.TRIALING.value: [
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.CANCELLED.value
            ],
            SubscriptionStatus.ACTIVE.value: [
                SubscriptionStatus.PAUSED.value,
                SubscriptionStatus.CANCELLED.value,
                SubscriptionStatus.PAST_DUE.value
            ],
            SubscriptionStatus.PAUSED.value: [
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.CANCELLED.value
            ],
            SubscriptionStatus.PAST_DUE.value: [
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.CANCELLED.value
            ]
        }
        
        if current not in valid_transitions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown subscription status: {current}"
            )
        
        if target_status not in valid_transitions[current]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {current} to {target_status}"
            )
        
        return True
