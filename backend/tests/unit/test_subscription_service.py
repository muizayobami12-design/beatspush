"""
Unit tests for SubscriptionService.

Tests:
- Subscription creation
- Subscription status transitions
- Subscription updates
- Trial management
- Cancellation
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.subscription_service import SubscriptionService
from app.models.fan_club import Subscription, MembershipTier


class TestSubscriptionCreation:
    """Test subscription creation."""
    
    def test_create_subscription_success(
        self,
        db_session: Session,
        subscriber_user,
        fan_club,
        membership_tiers
    ):
        """Test successful subscription creation."""
        service = SubscriptionService(db_session)
        
        subscription = service.create_subscription(
            fan_club_id=fan_club.id,
            tier_id=membership_tiers['premium'].id,
            subscriber_id=subscriber_user.id,
            billing_cycle="monthly",
            payment_provider="stripe",
            payment_provider_customer_id="cus_test123",
            payment_provider_subscription_id="sub_test123"
        )
        
        assert subscription is not None
        assert subscription.fan_club_id == fan_club.id
        assert subscription.subscriber_id == subscriber_user.id
        assert subscription.status == "active"
        assert subscription.billing_cycle == "monthly"
        assert subscription.auto_renew is True
    
    def test_create_subscription_with_trial(
        self,
        db_session: Session,
        subscriber_user,
        fan_club,
        membership_tiers
    ):
        """Test subscription creation with trial."""
        service = SubscriptionService(db_session)
        trial_days = 7
        
        subscription = service.create_subscription(
            fan_club_id=fan_club.id,
            tier_id=membership_tiers['basic'].id,
            subscriber_id=subscriber_user.id,
            billing_cycle="monthly",
            payment_provider="stripe",
            trial_days=trial_days
        )
        
        assert subscription.status == "trialing"
        assert subscription.trial_ends_at is not None
        assert subscription.price_paid == Decimal("0.00")
    
    def test_duplicate_subscription_prevented(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test that duplicate active subscriptions are prevented."""
        service = SubscriptionService(db_session)
        
        # Try to create duplicate
        with pytest.raises(Exception):  # Should raise error
            service.create_subscription(
                fan_club_id=active_subscription.fan_club_id,
                tier_id=active_subscription.tier_id,
                subscriber_id=active_subscription.subscriber_id,
                billing_cycle="monthly",
                payment_provider="stripe"
            )


class TestSubscriptionStatusTransitions:
    """Test subscription status transitions."""
    
    def test_transition_to_past_due(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test transition to past_due."""
        service = SubscriptionService(db_session)
        
        result = service.update_subscription_status(
            active_subscription.id,
            "past_due"
        )
        
        assert result.status == "past_due"
    
    def test_transition_to_paused(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test pausing subscription."""
        service = SubscriptionService(db_session)
        
        result = service.pause_subscription(
            active_subscription.id,
            pause_until=datetime.utcnow() + timedelta(days=30)
        )
        
        assert result.status == "paused"
        assert result.paused_at is not None
        assert result.paused_until is not None
    
    def test_resume_paused_subscription(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test resuming paused subscription."""
        service = SubscriptionService(db_session)
        
        # Pause first
        service.pause_subscription(
            active_subscription.id,
            pause_until=datetime.utcnow() + timedelta(days=30)
        )
        
        # Resume
        result = service.resume_subscription(active_subscription.id)
        
        assert result.status == "active"
        assert result.paused_at is not None
        assert result.paused_until is None
    
    def test_cancel_subscription(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test subscription cancellation."""
        service = SubscriptionService(db_session)
        
        result = service.cancel_subscription(
            active_subscription.id,
            reason="User requested"
        )
        
        assert result.status == "cancelled"
        assert result.cancelled_at is not None
        assert result.cancellation_reason == "User requested"


class TestSubscriptionTierChange:
    """Test tier changes."""
    
    def test_upgrade_subscription_tier(
        self,
        db_session: Session,
        active_subscription,
        membership_tiers
    ):
        """Test upgrading subscription tier."""
        service = SubscriptionService(db_session)
        
        # Currently on Premium, upgrade to VIP
        result = service.change_tier(
            active_subscription.id,
            membership_tiers['vip'].id,
            proration=True
        )
        
        assert result.tier_id == membership_tiers['vip'].id
    
    def test_downgrade_subscription_tier(
        self,
        db_session: Session,
        active_subscription,
        membership_tiers
    ):
        """Test downgrading subscription tier."""
        service = SubscriptionService(db_session)
        
        # Currently on Premium, downgrade to Basic
        result = service.change_tier(
            active_subscription.id,
            membership_tiers['basic'].id,
            proration=True
        )
        
        assert result.tier_id == membership_tiers['basic'].id


class TestTrialManagement:
    """Test trial subscription management."""
    
    def test_convert_trial_to_paid(
        self,
        db_session: Session,
        trial_subscription,
        subscriber_user,
        fan_club,
        membership_tiers,
        mock_stripe_provider
    ):
        """Test converting trial to paid subscription."""
        service = SubscriptionService(db_session)
        
        result = service.convert_trial_to_paid(
            trial_subscription.id,
            payment_provider_customer_id="cus_converted123"
        )
        
        assert result.status == "active"
        assert result.trial_ends_at is None
    
    def test_expire_trial_subscription(
        self,
        db_session: Session,
        trial_subscription
    ):
        """Test expiring trial subscription."""
        service = SubscriptionService(db_session)
        
        result = service.cancel_subscription(
            trial_subscription.id,
            reason="Trial expired"
        )
        
        assert result.status == "cancelled"


class TestSubscriptionQueries:
    """Test subscription queries."""
    
    def test_get_active_subscriptions(
        self,
        db_session: Session,
        fan_club,
        active_subscription
    ):
        """Test retrieving active subscriptions."""
        service = SubscriptionService(db_session)
        
        active_subs = service.get_active_subscriptions(fan_club.id)
        
        assert len(active_subs) == 1
        assert active_subs[0].id == active_subscription.id
    
    def test_get_subscriber_subscriptions(
        self,
        db_session: Session,
        subscriber_user,
        active_subscription,
        trial_subscription
    ):
        """Test retrieving all subscriptions for a subscriber."""
        service = SubscriptionService(db_session)
        
        subs = service.get_subscriber_subscriptions(subscriber_user.id)
        
        assert len(subs) >= 1
        assert any(s.id == active_subscription.id for s in subs)
    
    def test_get_subscription_by_id(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test retrieving subscription by ID."""
        service = SubscriptionService(db_session)
        
        result = service.get_subscription(active_subscription.id)
        
        assert result is not None
        assert result.id == active_subscription.id


class TestAutoRenewal:
    """Test auto-renewal functionality."""
    
    def test_enable_auto_renewal(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test enabling auto-renewal."""
        service = SubscriptionService(db_session)
        
        active_subscription.auto_renew = False
        db_session.commit()
        
        result = service.update_subscription(
            active_subscription.id,
            auto_renew=True
        )
        
        assert result.auto_renew is True
    
    def test_disable_auto_renewal(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test disabling auto-renewal."""
        service = SubscriptionService(db_session)
        
        result = service.update_subscription(
            active_subscription.id,
            auto_renew=False
        )
        
        assert result.auto_renew is False


class TestBillingDateCalculation:
    """Test billing date calculations."""
    
    def test_calculate_next_billing_date_monthly(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test next billing date for monthly cycle."""
        service = SubscriptionService(db_session)
        
        next_date = service.calculate_next_billing_date(
            active_subscription.current_period_end,
            "monthly"
        )
        
        assert next_date > active_subscription.current_period_end
        assert (next_date - active_subscription.current_period_end).days >= 28
        assert (next_date - active_subscription.current_period_end).days <= 31
    
    def test_calculate_next_billing_date_yearly(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test next billing date for yearly cycle."""
        service = SubscriptionService(db_session)
        
        next_date = service.calculate_next_billing_date(
            active_subscription.current_period_end,
            "yearly"
        )
        
        assert next_date > active_subscription.current_period_end
        assert (next_date - active_subscription.current_period_end).days >= 365
