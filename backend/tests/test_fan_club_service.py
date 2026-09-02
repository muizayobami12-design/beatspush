"""
Unit tests for Fan Club Service
Tests fan club creation, management, and statistics
Task 4.1: Test creator eligibility validation
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.fan_club_service import FanClubService
from app.models.fan_club import FanClub
from app.models.user import User, UserRole
from app.models.social import Follow, Post
from app.models.track import Track, TrackStatus
from app.schemas.fan_club import FanClubCreate, FanClubUpdate


class TestFanClubService:
    """Test suite for FanClubService"""
    
    def test_create_fan_club_success(self, db: Session, eligible_creator: User):
        """Test successful fan club creation with eligible creator"""
        service = FanClubService(db)
        
        fan_club_data = FanClubCreate(
            name="Test Fan Club",
            description="A test fan club",
            welcome_message="Welcome to my club!"
        )
        
        fan_club = service.create_fan_club(
            creator_id=eligible_creator.id,
            data=fan_club_data
        )
        
        assert fan_club is not None
        assert fan_club.name == "Test Fan Club"
        assert fan_club.creator_id == eligible_creator.id
        assert fan_club.is_active is True
        assert fan_club.total_members == 0
        assert fan_club.monthly_revenue == Decimal("0.00")
    
    def test_create_fan_club_duplicate(self, db: Session, eligible_creator: User):
        """Test creating duplicate fan club fails"""
        service = FanClubService(db)
        
        fan_club_data = FanClubCreate(
            name="Test Fan Club",
            description="A test fan club"
        )
        
        # Create first fan club
        service.create_fan_club(
            creator_id=eligible_creator.id,
            data=fan_club_data
        )
        
        # Attempt duplicate should raise error
        with pytest.raises(HTTPException) as exc:
            fan_club_data2 = FanClubCreate(
                name="Another Fan Club",
                description="A different fan club"
            )
            service.create_fan_club(
                creator_id=eligible_creator.id,
                data=fan_club_data2
            )
        assert exc.value.status_code == 400
        assert "already have a fan club" in str(exc.value.detail).lower()
    
    def test_create_fan_club_creator_not_found(self, db: Session):
        """Test creating fan club for non-existent creator"""
        service = FanClubService(db)
        
        fan_club_data = FanClubCreate(
            name="Test Fan Club",
            description="A test fan club"
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_fan_club(
                creator_id="non-existent-id",
                data=fan_club_data
            )
        assert exc.value.status_code == 404
        assert "not found" in str(exc.value.detail).lower()
    
    def test_create_fan_club_not_verified(self, db: Session, unverified_creator: User):
        """Test creating fan club without verified account fails"""
        service = FanClubService(db)
        
        fan_club_data = FanClubCreate(
            name="Test Fan Club",
            description="A test fan club"
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_fan_club(
                creator_id=unverified_creator.id,
                data=fan_club_data
            )
        assert exc.value.status_code == 403
        assert "verified account" in str(exc.value.detail).lower()
    
    def test_create_fan_club_insufficient_followers(
        self, 
        db: Session, 
        creator_with_few_followers: User
    ):
        """Test creating fan club with less than 100 followers fails"""
        service = FanClubService(db)
        
        fan_club_data = FanClubCreate(
            name="Test Fan Club",
            description="A test fan club"
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_fan_club(
                creator_id=creator_with_few_followers.id,
                data=fan_club_data
            )
        assert exc.value.status_code == 403
        assert "100 followers" in str(exc.value.detail).lower()
    
    def test_create_fan_club_insufficient_content(
        self, 
        db: Session, 
        creator_with_few_content: User
    ):
        """Test creating fan club with less than 10 published tracks/posts fails"""
        service = FanClubService(db)
        
        fan_club_data = FanClubCreate(
            name="Test Fan Club",
            description="A test fan club"
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_fan_club(
                creator_id=creator_with_few_content.id,
                data=fan_club_data
            )
        assert exc.value.status_code == 403
        assert "10 published" in str(exc.value.detail).lower()
    
    def test_create_fan_club_wrong_role(self, db: Session, fan_user: User):
        """Test creating fan club with non-creator role fails"""
        service = FanClubService(db)
        
        fan_club_data = FanClubCreate(
            name="Test Fan Club",
            description="A test fan club"
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_fan_club(
                creator_id=fan_user.id,
                data=fan_club_data
            )
        assert exc.value.status_code == 403
        assert "only artists" in str(exc.value.detail).lower()
    
    def test_get_fan_club_by_id(self, db: Session, fan_club_with_tiers: FanClub):
        """Task 4.2: Test retrieving fan club by ID with eager-loaded tiers"""
        service = FanClubService(db)
        
        retrieved = service.get_fan_club(fan_club_id=fan_club_with_tiers.id)
        
        assert retrieved is not None
        assert retrieved.id == fan_club_with_tiers.id
        assert retrieved.creator_id == fan_club_with_tiers.creator_id
        # Verify tiers are eager-loaded
        assert hasattr(retrieved, 'tiers')
        assert len(retrieved.tiers) > 0
        assert retrieved.tiers[0].fan_club_id == fan_club_with_tiers.id
    
    def test_get_fan_club_not_found(self, db: Session):
        """Task 4.2: Test getting non-existent fan club"""
        service = FanClubService(db)
        
        with pytest.raises(HTTPException) as exc:
            service.get_fan_club(fan_club_id="non-existent-id")
        assert exc.value.status_code == 404
        assert "not found" in str(exc.value.detail).lower()
    
    def test_update_fan_club_success(self, db: Session, fan_club: FanClub):
        """Task 4.3: Test successful fan club update"""
        service = FanClubService(db)
        
        update_data = FanClubUpdate(
            name="Updated Name",
            description="Updated description",
            welcome_message="Updated welcome!"
        )
        
        updated = service.update_fan_club(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id,
            data=update_data
        )
        
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        assert updated.welcome_message == "Updated welcome!"
    
    def test_update_fan_club_partial(self, db: Session, fan_club: FanClub):
        """Task 4.3: Test partial fan club update using exclude_unset"""
        service = FanClubService(db)
        
        original_name = fan_club.name
        original_welcome = fan_club.welcome_message
        update_data = FanClubUpdate(description="Only description updated")
        
        updated = service.update_fan_club(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id,
            data=update_data
        )
        
        assert updated.name == original_name  # Unchanged
        assert updated.welcome_message == original_welcome  # Unchanged
        assert updated.description == "Only description updated"
    
    def test_update_fan_club_unauthorized(self, db: Session, fan_club: FanClub, fan_user: User):
        """Task 4.3: Test update fails when user is not owner"""
        service = FanClubService(db)
        
        update_data = FanClubUpdate(name="Hacker Name")
        
        with pytest.raises(HTTPException) as exc:
            service.update_fan_club(
                fan_club_id=fan_club.id,
                creator_id=fan_user.id,  # Different user
                data=update_data
            )
        assert exc.value.status_code == 403
        assert "permission" in str(exc.value.detail).lower()
    
    def test_deactivate_fan_club_no_subscribers(self, db: Session, fan_club: FanClub):
        """Task 4.4: Test deactivating fan club with no active subscribers"""
        service = FanClubService(db)
        
        service.deactivate_fan_club(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id
        )
        
        # Verify deactivation
        deactivated = service.get_fan_club(fan_club_id=fan_club.id)
        assert deactivated.is_active is False
    
    def test_deactivate_fan_club_with_subscribers(
        self, 
        db: Session, 
        fan_club_with_subscribers: FanClub
    ):
        """Task 4.4: Test deactivating fan club with active subscribers fails"""
        service = FanClubService(db)
        
        with pytest.raises(HTTPException) as exc:
            service.deactivate_fan_club(
                fan_club_id=fan_club_with_subscribers.id,
                creator_id=fan_club_with_subscribers.creator_id
            )
        assert exc.value.status_code == 400
        assert "active subscriptions" in str(exc.value.detail).lower()
        assert "cancel all subscriptions first" in str(exc.value.detail).lower()
    
    def test_deactivate_fan_club_unauthorized(
        self, 
        db: Session, 
        fan_club: FanClub,
        fan_user: User
    ):
        """Task 4.4: Test deactivation fails when user is not owner"""
        service = FanClubService(db)
        
        with pytest.raises(HTTPException) as exc:
            service.deactivate_fan_club(
                fan_club_id=fan_club.id,
                creator_id=fan_user.id  # Different user
            )
        assert exc.value.status_code == 403
        assert "permission" in str(exc.value.detail).lower()
    
    def test_get_fan_club_stats(
        self, 
        db: Session, 
        fan_club_with_subscribers: FanClub
    ):
        """Task 4.5: Test retrieving fan club statistics"""
        service = FanClubService(db)
        
        stats = service.get_fan_club_stats(
            fan_club_id=fan_club_with_subscribers.id,
            creator_id=fan_club_with_subscribers.creator_id
        )
        
        # Verify structure
        assert "total_members" in stats
        assert "active_subscriptions" in stats
        assert "mrr" in stats
        assert "tier_breakdown" in stats
        
        # Verify values
        assert stats["total_members"] > 0
        assert stats["active_subscriptions"] > 0
        assert stats["mrr"] >= 0
        assert isinstance(stats["tier_breakdown"], list)
        
        # Verify tier breakdown structure
        if len(stats["tier_breakdown"]) > 0:
            tier_info = stats["tier_breakdown"][0]
            assert "tier_id" in tier_info
            assert "tier_name" in tier_info
            assert "tier_level" in tier_info
            assert "subscriber_count" in tier_info
    
    def test_get_fan_club_stats_empty(self, db: Session, fan_club: FanClub):
        """Task 4.5: Test stats for fan club with no subscribers"""
        service = FanClubService(db)
        
        stats = service.get_fan_club_stats(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id
        )
        
        assert stats["total_members"] == 0
        assert stats["active_subscriptions"] == 0
        assert stats["mrr"] == Decimal("0.00")
        assert stats["tier_breakdown"] == []
    
    def test_get_fan_club_stats_unauthorized(
        self, 
        db: Session, 
        fan_club: FanClub,
        fan_user: User
    ):
        """Task 4.5: Test stats fails when user is not owner"""
        service = FanClubService(db)
        
        with pytest.raises(HTTPException) as exc:
            service.get_fan_club_stats(
                fan_club_id=fan_club.id,
                creator_id=fan_user.id  # Different user
            )
        assert exc.value.status_code == 403
        assert "permission" in str(exc.value.detail).lower()
    
    def test_get_fan_club_stats_mrr_calculation(
        self,
        db: Session,
        fan_club_with_mixed_subscriptions: FanClub
    ):
        """Task 4.5: Test MRR calculation with mixed billing cycles"""
        service = FanClubService(db)
        
        stats = service.get_fan_club_stats(
            fan_club_id=fan_club_with_mixed_subscriptions.id,
            creator_id=fan_club_with_mixed_subscriptions.creator_id
        )
        
        # Should include monthly subs + yearly subs / 12
        assert stats["mrr"] > 0
        # Should have multiple tier types
        assert len(stats["tier_breakdown"]) > 0


# Pytest Fixtures

@pytest.fixture(scope="function", autouse=True)
def db():
    """Database session fixture with clean slate for each test"""
    from app.db.database import SessionLocal, engine, Base
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables fresh
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        # Clean up after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def eligible_creator(db: Session) -> User:
    """Create a fully eligible creator with 100+ followers and 10+ tracks"""
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email="creator@test.com",
        username="testcreator",
        hashed_password="hashed",
        role=UserRole.ARTIST,
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Add 100 followers
    for i in range(100):
        follower = User(
            id=str(uuid.uuid4()),
            email=f"follower{i}@test.com",
            username=f"follower{i}",
            hashed_password="hashed",
            role=UserRole.FAN,
            is_active=True
        )
        db.add(follower)
        db.flush()
        
        follow = Follow(
            id=str(uuid.uuid4()),
            follower_id=follower.id,
            following_id=user.id,
            created_at=datetime.utcnow().isoformat()
        )
        db.add(follow)
    
    # Add 10 published tracks
    for i in range(10):
        track = Track(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title=f"Test Track {i}",
            artist_name="Test Artist",
            status=TrackStatus.PUBLISHED
        )
        db.add(track)
    
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def unverified_creator(db: Session) -> User:
    """Create an unverified creator"""
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email="unverified@test.com",
        username="unverified",
        hashed_password="hashed",
        role=UserRole.ARTIST,
        is_verified=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def creator_with_few_followers(db: Session) -> User:
    """Create a creator with less than 100 followers"""
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email="fewfollowers@test.com",
        username="fewfollowers",
        hashed_password="hashed",
        role=UserRole.ARTIST,
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Add only 50 followers
    for i in range(50):
        follower = User(
            id=str(uuid.uuid4()),
            email=f"follower_few{i}@test.com",
            username=f"follower_few{i}",
            hashed_password="hashed",
            role=UserRole.FAN,
            is_active=True
        )
        db.add(follower)
        db.flush()
        
        follow = Follow(
            id=str(uuid.uuid4()),
            follower_id=follower.id,
            following_id=user.id,
            created_at=datetime.utcnow().isoformat()
        )
        db.add(follow)
    
    # Add 10 tracks to meet that requirement
    for i in range(10):
        track = Track(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title=f"Test Track {i}",
            artist_name="Test Artist",
            status=TrackStatus.PUBLISHED
        )
        db.add(track)
    
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def creator_with_few_content(db: Session) -> User:
    """Create a creator with less than 10 published tracks/posts"""
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email="fewcontent@test.com",
        username="fewcontent",
        hashed_password="hashed",
        role=UserRole.ARTIST,
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Add 100 followers to meet that requirement
    for i in range(100):
        follower = User(
            id=str(uuid.uuid4()),
            email=f"follower_content{i}@test.com",
            username=f"follower_content{i}",
            hashed_password="hashed",
            role=UserRole.FAN,
            is_active=True
        )
        db.add(follower)
        db.flush()
        
        follow = Follow(
            id=str(uuid.uuid4()),
            follower_id=follower.id,
            following_id=user.id,
            created_at=datetime.utcnow().isoformat()
        )
        db.add(follow)
    
    # Add only 5 tracks (less than 10)
    for i in range(5):
        track = Track(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title=f"Test Track {i}",
            artist_name="Test Artist",
            status=TrackStatus.PUBLISHED
        )
        db.add(track)
    
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def fan_user(db: Session) -> User:
    """Create a fan user (wrong role)"""
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email="fan@test.com",
        username="fanuser",
        hashed_password="hashed",
        role=UserRole.FAN,
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def fan_club(db: Session, eligible_creator: User) -> FanClub:
    """Create a test fan club"""
    import uuid
    
    fan_club = FanClub(
        id=str(uuid.uuid4()),
        creator_id=eligible_creator.id,
        name="Test Fan Club",
        description="A test fan club",
        welcome_message="Welcome!",
        is_active=True,
        total_members=0,
        monthly_revenue=Decimal("0.00")
    )
    db.add(fan_club)
    db.commit()
    db.refresh(fan_club)
    return fan_club


@pytest.fixture
def fan_club_with_subscribers(db: Session, fan_club: FanClub) -> FanClub:
    """Create a fan club with active subscribers"""
    import uuid
    from app.models.fan_club import MembershipTier, Subscription
    
    # Create tier
    tier = MembershipTier(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        name="Test Tier",
        tier_level=1,
        price_monthly=Decimal("9.99"),
        price_yearly=Decimal("89.99"),
        is_active=True,
        benefits=["Benefit 1", "Benefit 2"]
    )
    db.add(tier)
    db.flush()
    
    # Create subscriber
    subscriber = User(
        id=str(uuid.uuid4()),
        email="subscriber@test.com",
        username="testsubscriber",
        hashed_password="hashed",
        role=UserRole.FAN,
        is_active=True
    )
    db.add(subscriber)
    db.flush()
    
    # Create subscription
    subscription = Subscription(
        id=str(uuid.uuid4()),
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


@pytest.fixture
def fan_club_with_tiers(db: Session, fan_club: FanClub) -> FanClub:
    """Create a fan club with multiple tiers"""
    import uuid
    from app.models.fan_club import MembershipTier
    
    # Create 3 tiers
    tiers_data = [
        {"name": "Bronze", "level": 1, "price": Decimal("4.99")},
        {"name": "Silver", "level": 2, "price": Decimal("9.99")},
        {"name": "Gold", "level": 3, "price": Decimal("19.99")},
    ]
    
    for tier_data in tiers_data:
        tier = MembershipTier(
            id=str(uuid.uuid4()),
            fan_club_id=fan_club.id,
            name=tier_data["name"],
            tier_level=tier_data["level"],
            price_monthly=tier_data["price"],
            price_yearly=tier_data["price"] * 10,  # 10x monthly
            is_active=True,
            benefits=[f"Benefit {tier_data['level']}.1", f"Benefit {tier_data['level']}.2"]
        )
        db.add(tier)
    
    db.commit()
    db.refresh(fan_club)
    return fan_club


@pytest.fixture
def fan_club_with_mixed_subscriptions(db: Session, fan_club_with_tiers: FanClub) -> FanClub:
    """Create a fan club with mixed billing cycle subscriptions"""
    import uuid
    from app.models.fan_club import Subscription
    
    tiers = fan_club_with_tiers.tiers
    
    # Create monthly subscription
    subscriber1 = User(
        id=str(uuid.uuid4()),
        email="monthly@test.com",
        username="monthly_sub",
        hashed_password="hashed",
        role=UserRole.FAN,
        is_active=True
    )
    db.add(subscriber1)
    db.flush()
    
    subscription1 = Subscription(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club_with_tiers.id,
        tier_id=tiers[0].id,
        subscriber_id=subscriber1.id,
        status="active",
        billing_cycle="monthly",
        price_paid=Decimal("4.99"),
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow(),
        payment_provider="stripe",
        auto_renew=True
    )
    db.add(subscription1)
    
    # Create yearly subscription
    subscriber2 = User(
        id=str(uuid.uuid4()),
        email="yearly@test.com",
        username="yearly_sub",
        hashed_password="hashed",
        role=UserRole.FAN,
        is_active=True
    )
    db.add(subscriber2)
    db.flush()
    
    subscription2 = Subscription(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club_with_tiers.id,
        tier_id=tiers[1].id,
        subscriber_id=subscriber2.id,
        status="active",
        billing_cycle="yearly",
        price_paid=Decimal("99.90"),  # 10 months equivalent
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow(),
        payment_provider="stripe",
        auto_renew=True
    )
    db.add(subscription2)
    
    db.commit()
    db.refresh(fan_club_with_tiers)
    return fan_club_with_tiers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

