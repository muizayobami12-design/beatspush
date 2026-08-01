"""
Unit tests for Fan Club Service
Tests fan club creation, management, and statistics
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.fan_club_service import FanClubService
from app.models.fan_club import FanClub
from app.models.user import User
from app.schemas.fan_club import FanClubCreate, FanClubUpdate


class TestFanClubService:
    """Test suite for FanClubService"""
    
    def test_create_fan_club_success(self, db: Session, creator_user: User):
        """Test successful fan club creation"""
        service = FanClubService(db)
        
        fan_club_data = FanClubCreate(
            name="Test Fan Club",
            description="A test fan club",
            welcome_message="Welcome to my club!"
        )
        
        fan_club = service.create_fan_club(
            creator_id=creator_user.id,
            fan_club_data=fan_club_data
        )
        
        assert fan_club is not None
        assert fan_club.name == "Test Fan Club"
        assert fan_club.creator_id == creator_user.id
        assert fan_club.is_active is True
        assert fan_club.total_members == 0
        assert fan_club.monthly_revenue == Decimal("0")
    
    def test_create_fan_club_duplicate(self, db: Session, creator_user: User):
        """Test creating duplicate fan club fails"""
        service = FanClubService(db)
        
        fan_club_data = FanClubCreate(
            name="Test Fan Club",
            description="A test fan club"
        )
        
        # Create first fan club
        service.create_fan_club(
            creator_id=creator_user.id,
            fan_club_data=fan_club_data
        )
        
        # Attempt duplicate should raise error
        with pytest.raises(Exception) as exc:
            service.create_fan_club(
                creator_id=creator_user.id,
                fan_club_data=fan_club_data
            )
        assert "already has a fan club" in str(exc.value).lower()
    
    def test_get_fan_club_by_creator(self, db: Session, fan_club: FanClub):
        """Test retrieving fan club by creator ID"""
        service = FanClubService(db)
        
        retrieved = service.get_fan_club(creator_id=fan_club.creator_id)
        
        assert retrieved is not None
        assert retrieved.id == fan_club.id
        assert retrieved.creator_id == fan_club.creator_id
    
    def test_get_fan_club_not_found(self, db: Session):
        """Test getting non-existent fan club"""
        service = FanClubService(db)
        
        with pytest.raises(Exception) as exc:
            service.get_fan_club(creator_id="non-existent-id")
        assert "not found" in str(exc.value).lower()
    
    def test_update_fan_club_success(self, db: Session, fan_club: FanClub):
        """Test successful fan club update"""
        service = FanClubService(db)
        
        update_data = FanClubUpdate(
            name="Updated Name",
            description="Updated description",
            welcome_message="Updated welcome!"
        )
        
        updated = service.update_fan_club(
            fan_club_id=fan_club.id,
            update_data=update_data
        )
        
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        assert updated.welcome_message == "Updated welcome!"
    
    def test_update_fan_club_partial(self, db: Session, fan_club: FanClub):
        """Test partial fan club update"""
        service = FanClubService(db)
        
        original_name = fan_club.name
        update_data = FanClubUpdate(description="Only description updated")
        
        updated = service.update_fan_club(
            fan_club_id=fan_club.id,
            update_data=update_data
        )
        
        assert updated.name == original_name  # Unchanged
        assert updated.description == "Only description updated"
    
    def test_deactivate_fan_club_no_subscribers(self, db: Session, fan_club: FanClub):
        """Test deactivating fan club with no active subscribers"""
        service = FanClubService(db)
        
        result = service.deactivate_fan_club(fan_club_id=fan_club.id)
        
        assert result is True
        
        # Verify deactivation
        deactivated = service.get_fan_club(fan_club_id=fan_club.id)
        assert deactivated.is_active is False
    
    def test_deactivate_fan_club_with_subscribers(
        self, 
        db: Session, 
        fan_club_with_subscribers: FanClub
    ):
        """Test deactivating fan club with active subscribers fails"""
        service = FanClubService(db)
        
        with pytest.raises(Exception) as exc:
            service.deactivate_fan_club(fan_club_id=fan_club_with_subscribers.id)
        assert "active subscribers" in str(exc.value).lower()
    
    def test_get_fan_club_stats(
        self, 
        db: Session, 
        fan_club_with_subscribers: FanClub
    ):
        """Test retrieving fan club statistics"""
        service = FanClubService(db)
        
        stats = service.get_fan_club_stats(fan_club_id=fan_club_with_subscribers.id)
        
        assert "total_members" in stats
        assert "monthly_revenue" in stats
        assert "revenue_by_tier" in stats
        assert stats["total_members"] > 0
        assert stats["monthly_revenue"] >= 0


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
    """Create a test creator user"""
    user = User(
        id="creator-test-id",
        email="creator@test.com",
        username="testcreator",
        account_type="creator",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def fan_club(db: Session, creator_user: User) -> FanClub:
    """Create a test fan club"""
    fan_club = FanClub(
        id="fanclub-test-id",
        creator_id=creator_user.id,
        name="Test Fan Club",
        description="A test fan club",
        welcome_message="Welcome!",
        is_active=True,
        total_members=0,
        monthly_revenue=Decimal("0")
    )
    db.add(fan_club)
    db.commit()
    db.refresh(fan_club)
    return fan_club


@pytest.fixture
def fan_club_with_subscribers(db: Session, fan_club: FanClub) -> FanClub:
    """Create a fan club with active subscribers"""
    from app.models.fan_club import MembershipTier, Subscription
    
    # Create tier
    tier = MembershipTier(
        id="tier-test-id",
        fan_club_id=fan_club.id,
        name="Test Tier",
        tier_level=1,
        price_monthly=Decimal("9.99"),
        price_yearly=Decimal("99.99"),
        is_active=True
    )
    db.add(tier)
    
    # Create subscriber
    subscriber = User(
        id="subscriber-test-id",
        email="subscriber@test.com",
        username="testsubscriber",
        account_type="fan"
    )
    db.add(subscriber)
    
    # Create subscription
    subscription = Subscription(
        id="subscription-test-id",
        fan_club_id=fan_club.id,
        tier_id=tier.id,
        subscriber_id=subscriber.id,
        status="active",
        billing_cycle="monthly",
        price_paid=Decimal("9.99"),
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow(),
        payment_provider="stripe",
        auto_renew=True
    )
    db.add(subscription)
    
    # Update fan club stats
    fan_club.total_members = 1
    fan_club.monthly_revenue = Decimal("9.99")
    
    db.commit()
    db.refresh(fan_club)
    return fan_club


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
