"""
Unit tests for Subscription Service
Tests subscription lifecycle, upgrades, downgrades, cancellations
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.subscription_service import SubscriptionService
from app.models.fan_club import FanClub, MembershipTier, Subscription
from app.models.user import User
from app.schemas.fan_club import SubscriptionCreate


class TestSubscriptionService:
    """Test suite for SubscriptionService"""
    
    def test_create_subscription_success(
        self, 
        db: Session, 
        tier: MembershipTier,
        fan_user: User
    ):
        """Test successful subscription creation"""
        service = SubscriptionService(db)
        
        subscription_data = SubscriptionCreate(
            tier_id=tier.id,
            billing_cycle="monthly",
            payment_method={
                "provider": "stripe",
                "token": "tok_visa"
            }
        )
        
        subscription = service.create_subscription(
            user_id=fan_user.id,
            subscription_data=subscription_data
        )
        
        assert subscription is not None
        assert subscription.tier_id == tier.id
        assert subscription.subscriber_id == fan_user.id
        assert subscription.status == "active"
        assert subscription.billing_cycle == "monthly"
        assert subscription.auto_renew is True
    
    def test_create_subscription_yearly(
        self, 
        db: Session, 
        tier: MembershipTier,
        fan_user: User
    ):
        """Test yearly subscription has correct pricing"""
        service = SubscriptionService(db)
        
        subscription_data = SubscriptionCreate(
            tier_id=tier.id,
            billing_cycle="yearly",
            payment_method={
                "provider": "stripe",
                "token": "tok_visa"
            }
        )
        
        subscription = service.create_subscription(
            user_id=fan_user.id,
            subscription_data=subscription_data
        )
        
        # Yearly price should be discounted
        assert subscription.billing_cycle == "yearly"
        assert subscription.price_paid == tier.price_yearly
        # Verify 10% discount (2 months free)
        expected_yearly = tier.price_monthly * 10  # 10 months instead of 12
        assert abs(subscription.price_paid - expected_yearly) < Decimal("0.01")
    
    def test_create_subscription_duplicate_active(
        self, 
        db: Session, 
        active_subscription: Subscription,
        tier: MembershipTier
    ):
        """Test creating duplicate subscription to same tier fails"""
        service = SubscriptionService(db)
        
        subscription_data = SubscriptionCreate(
            tier_id=tier.id,
            billing_cycle="monthly",
            payment_method={"provider": "stripe", "token": "tok_visa"}
        )
        
        with pytest.raises(Exception) as exc:
            service.create_subscription(
                user_id=active_subscription.subscriber_id,
                subscription_data=subscription_data
            )
        assert "already subscribed" in str(exc.value).lower()
    
    def test_cancel_subscription_immediate(
        self, 
        db: Session, 
        active_subscription: Subscription
    ):
        """Test immediate subscription cancellation"""
        service = SubscriptionService(db)
        
        cancelled = service.cancel_subscription(
            subscription_id=active_subscription.id,
            immediate=True
        )
        
        assert cancelled.status == "cancelled"
        assert cancelled.cancelled_at is not None
        assert cancelled.ended_at is not None
    
    def test_cancel_subscription_end_of_period(
        self, 
        db: Session, 
        active_subscription: Subscription
    ):
        """Test end-of-period cancellation"""
        service = SubscriptionService(db)
        
        cancelled = service.cancel_subscription(
            subscription_id=active_subscription.id,
            immediate=False
        )
        
        assert cancelled.status == "active"  # Still active until period end
        assert cancelled.cancelled_at is not None
        assert cancelled.auto_renew is False  # But renewal disabled
        assert cancelled.ended_at is None  # Not ended yet
    
    def test_pause_subscription_success(
        self, 
        db: Session, 
        active_subscription: Subscription
    ):
        """Test subscription pause"""
        service = SubscriptionService(db)
        
        pause_until = datetime.utcnow() + timedelta(days=30)
        paused = service.pause_subscription(
            subscription_id=active_subscription.id,
            pause_until=pause_until
        )
        
        assert paused.status == "paused"
        assert paused.paused_at is not None
        assert paused.paused_until == pause_until
    
    def test_pause_subscription_exceeds_limit(
        self, 
        db: Session, 
        active_subscription: Subscription
    ):
        """Test pausing for more than 90 days fails"""
        service = SubscriptionService(db)
        
        pause_until = datetime.utcnow() + timedelta(days=100)
        
        with pytest.raises(Exception) as exc:
            service.pause_subscription(
                subscription_id=active_subscription.id,
                pause_until=pause_until
            )
        assert "90 days" in str(exc.value).lower()
    
    def test_resume_subscription_success(
        self, 
        db: Session, 
        paused_subscription: Subscription
    ):
        """Test resuming paused subscription"""
        service = SubscriptionService(db)
        
        resumed = service.resume_subscription(
            subscription_id=paused_subscription.id
        )
        
        assert resumed.status == "active"
        assert resumed.paused_at is None
        assert resumed.paused_until is None
    
    def test_upgrade_tier_immediate(
        self, 
        db: Session, 
        active_subscription: Subscription,
        higher_tier: MembershipTier
    ):
        """Test immediate tier upgrade"""
        service = SubscriptionService(db)
        
        upgraded = service.upgrade_tier(
            subscription_id=active_subscription.id,
            new_tier_id=higher_tier.id
        )
        
        assert upgraded.tier_id == higher_tier.id
        assert upgraded.price_paid == higher_tier.price_monthly
        # Upgrade should be immediate
        assert upgraded.status == "active"
    
    def test_downgrade_tier_next_cycle(
        self, 
        db: Session, 
        active_subscription: Subscription,
        lower_tier: MembershipTier
    ):
        """Test tier downgrade scheduled for next cycle"""
        service = SubscriptionService(db)
        
        downgraded = service.downgrade_tier(
            subscription_id=active_subscription.id,
            new_tier_id=lower_tier.id
        )
        
        # Downgrade should be scheduled, not immediate
        assert downgraded.tier_id == active_subscription.tier_id  # Still old tier
        # Should have metadata about pending downgrade
        # (Implementation detail - adjust based on actual implementation)
    
    def test_check_subscription_status_active(
        self, 
        db: Session, 
        active_subscription: Subscription,
        fan_user: User
    ):
        """Test checking active subscription status"""
        service = SubscriptionService(db)
        
        is_subscribed = service.check_subscription_status(
            user_id=fan_user.id,
            fan_club_id=active_subscription.fan_club_id
        )
        
        assert is_subscribed is True
    
    def test_check_subscription_status_inactive(
        self, 
        db: Session, 
        fan_user: User,
        fan_club: FanClub
    ):
        """Test checking subscription status with no subscription"""
        service = SubscriptionService(db)
        
        is_subscribed = service.check_subscription_status(
            user_id=fan_user.id,
            fan_club_id=fan_club.id
        )
        
        assert is_subscribed is False
    
    def test_list_user_subscriptions(
        self, 
        db: Session, 
        fan_user: User,
        active_subscription: Subscription
    ):
        """Test listing user's subscriptions"""
        service = SubscriptionService(db)
        
        subscriptions = service.list_user_subscriptions(
            user_id=fan_user.id
        )
        
        assert len(subscriptions) > 0
        assert any(sub.id == active_subscription.id for sub in subscriptions)


# Pytest Fixtures

@pytest.fixture
def db():
    """Database session fixture"""
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def creator_user(db: Session) -> User:
    """Create test creator"""
    user = User(
        id="creator-sub-test",
        email="creator@sub-test.com",
        username="subcreator",
        account_type="creator",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def fan_user(db: Session) -> User:
    """Create test fan user"""
    user = User(
        id="fan-sub-test",
        email="fan@sub-test.com",
        username="subfan",
        account_type="fan"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def fan_club(db: Session, creator_user: User) -> FanClub:
    """Create test fan club"""
    club = FanClub(
        id="club-sub-test",
        creator_id=creator_user.id,
        name="Sub Test Club",
        is_active=True,
        total_members=0,
        monthly_revenue=Decimal("0")
    )
    db.add(club)
    db.commit()
    db.refresh(club)
    return club


@pytest.fixture
def tier(db: Session, fan_club: FanClub) -> MembershipTier:
    """Create test tier"""
    tier = MembershipTier(
        id="tier-sub-test",
        fan_club_id=fan_club.id,
        name="Test Tier",
        tier_level=2,
        price_monthly=Decimal("9.99"),
        price_yearly=Decimal("99.99"),
        benefits=["Benefit 1", "Benefit 2"],
        is_active=True
    )
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier


@pytest.fixture
def higher_tier(db: Session, fan_club: FanClub) -> MembershipTier:
    """Create higher tier for upgrade tests"""
    tier = MembershipTier(
        id="tier-high-test",
        fan_club_id=fan_club.id,
        name="Premium Tier",
        tier_level=3,
        price_monthly=Decimal("19.99"),
        price_yearly=Decimal("199.99"),
        is_active=True
    )
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier


@pytest.fixture
def lower_tier(db: Session, fan_club: FanClub) -> MembershipTier:
    """Create lower tier for downgrade tests"""
    tier = MembershipTier(
        id="tier-low-test",
        fan_club_id=fan_club.id,
        name="Basic Tier",
        tier_level=1,
        price_monthly=Decimal("4.99"),
        price_yearly=Decimal("49.99"),
        is_active=True
    )
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier


@pytest.fixture
def active_subscription(
    db: Session, 
    fan_club: FanClub, 
    tier: MembershipTier,
    fan_user: User
) -> Subscription:
    """Create active subscription"""
    sub = Subscription(
        id="sub-active-test",
        fan_club_id=fan_club.id,
        tier_id=tier.id,
        subscriber_id=fan_user.id,
        status="active",
        billing_cycle="monthly",
        price_paid=Decimal("9.99"),
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        payment_provider="stripe",
        auto_renew=True
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@pytest.fixture
def paused_subscription(
    db: Session, 
    fan_club: FanClub, 
    tier: MembershipTier,
    fan_user: User
) -> Subscription:
    """Create paused subscription"""
    sub = Subscription(
        id="sub-paused-test",
        fan_club_id=fan_club.id,
        tier_id=tier.id,
        subscriber_id=fan_user.id,
        status="paused",
        billing_cycle="monthly",
        price_paid=Decimal("9.99"),
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        paused_at=datetime.utcnow(),
        paused_until=datetime.utcnow() + timedelta(days=30),
        payment_provider="stripe",
        auto_renew=True
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
