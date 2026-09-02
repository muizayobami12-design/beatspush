"""
Unit tests for Tier Service
Tests membership tier CRUD operations
Tasks 5.1-5.6: Tier management with pricing, validation, and access control
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.tier_service import TierService
from app.models.fan_club import FanClub, MembershipTier, Subscription
from app.models.user import User, UserRole
from app.schemas.fan_club import TierCreate, TierUpdate


class TestTierService:
    """Test suite for TierService"""
    
    # ========================================================================
    # TASK 5.1: create_tier() - Validate pricing, tier level uniqueness
    # ========================================================================
    
    def test_create_tier_success(self, db: Session, fan_club: FanClub):
        """Task 5.1: Test successful tier creation with valid data"""
        service = TierService(db)
        
        tier_data = TierCreate(
            name="Bronze",
            description="Entry level tier",
            tier_level=1,
            price_monthly=Decimal("4.99"),
            benefits=["Access to exclusive posts", "Early track releases"]
        )
        
        tier = service.create_tier(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id,
            data=tier_data
        )
        
        assert tier is not None
        assert tier.name == "Bronze"
        assert tier.tier_level == 1
        assert tier.price_monthly == Decimal("4.99")
        # Verify 10% discount on yearly price (monthly * 12 * 0.9)
        expected_yearly = Decimal("4.99") * 12 * Decimal("0.9")
        assert tier.price_yearly == expected_yearly.quantize(Decimal("0.01"))
        assert len(tier.benefits) == 2
        assert tier.is_active is True
        assert tier.subscriber_count == 0
    
    def test_create_tier_minimum_price(self, db: Session, fan_club: FanClub):
        """Task 5.1: Test tier creation with minimum allowed price ($2.99)"""
        service = TierService(db)
        
        tier_data = TierCreate(
            name="Budget Tier",
            tier_level=1,
            price_monthly=Decimal("2.99"),
            benefits=["Basic access"]
        )
        
        tier = service.create_tier(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id,
            data=tier_data
        )
        
        assert tier.price_monthly == Decimal("2.99")
        # Yearly should be monthly * 12 * 0.9
        expected_yearly = Decimal("2.99") * 12 * Decimal("0.9")
        assert tier.price_yearly == expected_yearly.quantize(Decimal("0.01"))
    
    def test_create_tier_maximum_price(self, db: Session, fan_club: FanClub):
        """Task 5.1: Test tier creation with maximum allowed price ($99.99)"""
        service = TierService(db)
        
        tier_data = TierCreate(
            name="Premium Tier",
            tier_level=1,
            price_monthly=Decimal("99.99"),
            benefits=["All premium features"]
        )
        
        tier = service.create_tier(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id,
            data=tier_data
        )
        
        assert tier.price_monthly == Decimal("99.99")
    
    def test_create_tier_yearly_discount_calculation(self, db: Session, fan_club: FanClub):
        """Task 5.6: Test yearly price calculation (10% discount = 2 months free)"""
        service = TierService(db)
        
        tier_data = TierCreate(
            name="Standard",
            tier_level=1,
            price_monthly=Decimal("10.00"),
            benefits=["Standard access"]
        )
        
        tier = service.create_tier(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id,
            data=tier_data
        )
        
        # 10.00 * 12 * 0.9 = 108.00 (effectively paying for 10 months)
        assert tier.price_yearly == Decimal("108.00")
    
    def test_create_tier_duplicate_level(self, db: Session, fan_club: FanClub):
        """Task 5.1: Test creating tier with duplicate tier level fails"""
        service = TierService(db)
        
        # Create first tier
        tier_data1 = TierCreate(
            name="Bronze",
            tier_level=1,
            price_monthly=Decimal("4.99"),
            benefits=[]
        )
        service.create_tier(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id,
            data=tier_data1
        )
        
        # Try to create another tier with same level
        tier_data2 = TierCreate(
            name="Different Name",
            tier_level=1,  # Same level
            price_monthly=Decimal("9.99"),
            benefits=[]
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_tier(
                fan_club_id=fan_club.id,
                creator_id=fan_club.creator_id,
                data=tier_data2
            )
        assert exc.value.status_code == 400
        assert "level 1 already exists" in str(exc.value.detail).lower()
    
    def test_create_tier_duplicate_name(self, db: Session, fan_club: FanClub):
        """Task 5.1: Test creating tier with duplicate name fails"""
        service = TierService(db)
        
        # Create first tier
        tier_data1 = TierCreate(
            name="Bronze",
            tier_level=1,
            price_monthly=Decimal("4.99"),
            benefits=[]
        )
        service.create_tier(
            fan_club_id=fan_club.id,
            creator_id=fan_club.creator_id,
            data=tier_data1
        )
        
        # Try to create another tier with same name
        tier_data2 = TierCreate(
            name="Bronze",  # Same name
            tier_level=2,
            price_monthly=Decimal("9.99"),
            benefits=[]
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_tier(
                fan_club_id=fan_club.id,
                creator_id=fan_club.creator_id,
                data=tier_data2
            )
        assert exc.value.status_code == 400
        assert "name 'bronze' already exists" in str(exc.value.detail).lower()
    
    def test_create_tier_maximum_limit(self, db: Session, fan_club: FanClub):
        """Task 5.1: Test creating more than 3 tiers fails"""
        service = TierService(db)
        
        # Create 3 tiers
        for i in range(1, 4):
            tier_data = TierCreate(
                name=f"Tier {i}",
                tier_level=i,
                price_monthly=Decimal("9.99"),
                benefits=[]
            )
            service.create_tier(
                fan_club_id=fan_club.id,
                creator_id=fan_club.creator_id,
                data=tier_data
            )
        
        # Try to create 4th tier
        tier_data4 = TierCreate(
            name="Fourth Tier",
            tier_level=1,  # Reusing level to bypass level check
            price_monthly=Decimal("9.99"),
            benefits=[]
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_tier(
                fan_club_id=fan_club.id,
                creator_id=fan_club.creator_id,
                data=tier_data4
            )
        assert exc.value.status_code == 400
        assert "maximum 3 tiers" in str(exc.value.detail).lower()
    
    def test_create_tier_unauthorized(self, db: Session, fan_club: FanClub, other_creator: User):
        """Task 5.1: Test creating tier without ownership fails"""
        service = TierService(db)
        
        tier_data = TierCreate(
            name="Unauthorized Tier",
            tier_level=1,
            price_monthly=Decimal("9.99"),
            benefits=[]
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_tier(
                fan_club_id=fan_club.id,
                creator_id=other_creator.id,  # Different creator
                data=tier_data
            )
        assert exc.value.status_code == 403
        assert "permission" in str(exc.value.detail).lower()
    
    def test_create_tier_fan_club_not_found(self, db: Session, eligible_creator: User):
        """Task 5.1: Test creating tier for non-existent fan club"""
        service = TierService(db)
        
        tier_data = TierCreate(
            name="Test Tier",
            tier_level=1,
            price_monthly=Decimal("9.99"),
            benefits=[]
        )
        
        with pytest.raises(HTTPException) as exc:
            service.create_tier(
                fan_club_id="non-existent-id",
                creator_id=eligible_creator.id,
                data=tier_data
            )
        assert exc.value.status_code == 404
        assert "not found" in str(exc.value.detail).lower()
    
    # ========================================================================
    # TASK 5.2: update_tier() - Allow edits with subscriber notice
    # ========================================================================
    
    def test_update_tier_name(self, db: Session, tier: MembershipTier):
        """Task 5.2: Test updating tier name"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        
        update_data = TierUpdate(name="Updated Bronze")
        
        updated = service.update_tier(
            tier_id=tier.id,
            creator_id=fan_club.creator_id,
            data=update_data
        )
        
        assert updated.name == "Updated Bronze"
    
    def test_update_tier_description(self, db: Session, tier: MembershipTier):
        """Task 5.2: Test updating tier description"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        
        update_data = TierUpdate(description="Updated description")
        
        updated = service.update_tier(
            tier_id=tier.id,
            creator_id=fan_club.creator_id,
            data=update_data
        )
        
        assert updated.description == "Updated description"
    
    def test_update_tier_price(self, db: Session, tier: MembershipTier):
        """Task 5.2: Test updating tier price recalculates yearly price"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        
        update_data = TierUpdate(price_monthly=Decimal("14.99"))
        
        updated = service.update_tier(
            tier_id=tier.id,
            creator_id=fan_club.creator_id,
            data=update_data
        )
        
        assert updated.price_monthly == Decimal("14.99")
        # Verify yearly price recalculation
        expected_yearly = Decimal("14.99") * 12 * Decimal("0.9")
        assert updated.price_yearly == expected_yearly.quantize(Decimal("0.01"))
    
    def test_update_tier_benefits(self, db: Session, tier: MembershipTier):
        """Task 5.2: Test updating tier benefits"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        
        new_benefits = ["New benefit 1", "New benefit 2", "New benefit 3"]
        update_data = TierUpdate(benefits=new_benefits)
        
        updated = service.update_tier(
            tier_id=tier.id,
            creator_id=fan_club.creator_id,
            data=update_data
        )
        
        assert updated.benefits == new_benefits
    
    def test_update_tier_partial(self, db: Session, tier: MembershipTier):
        """Task 5.2: Test partial tier update"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        
        original_name = tier.name
        original_price = tier.price_monthly
        
        update_data = TierUpdate(description="Only description updated")
        
        updated = service.update_tier(
            tier_id=tier.id,
            creator_id=fan_club.creator_id,
            data=update_data
        )
        
        assert updated.name == original_name  # Unchanged
        assert updated.price_monthly == original_price  # Unchanged
        assert updated.description == "Only description updated"
    
    def test_update_tier_duplicate_name_check(self, db: Session, fan_club_with_multiple_tiers: FanClub):
        """Task 5.2: Test updating tier name to duplicate fails"""
        service = TierService(db)
        
        tiers = fan_club_with_multiple_tiers.tiers
        tier_to_update = tiers[0]
        existing_name = tiers[1].name
        
        update_data = TierUpdate(name=existing_name)
        
        with pytest.raises(HTTPException) as exc:
            service.update_tier(
                tier_id=tier_to_update.id,
                creator_id=fan_club_with_multiple_tiers.creator_id,
                data=update_data
            )
        assert exc.value.status_code == 400
        assert "already exists" in str(exc.value.detail).lower()
    
    def test_update_tier_unauthorized(self, db: Session, tier: MembershipTier, other_creator: User):
        """Task 5.2: Test updating tier without ownership fails"""
        service = TierService(db)
        
        update_data = TierUpdate(name="Hacked Name")
        
        with pytest.raises(HTTPException) as exc:
            service.update_tier(
                tier_id=tier.id,
                creator_id=other_creator.id,  # Different creator
                data=update_data
            )
        assert exc.value.status_code == 403
        assert "permission" in str(exc.value.detail).lower()
    
    def test_update_tier_not_found(self, db: Session, eligible_creator: User):
        """Task 5.2: Test updating non-existent tier"""
        service = TierService(db)
        
        update_data = TierUpdate(name="New Name")
        
        with pytest.raises(HTTPException) as exc:
            service.update_tier(
                tier_id="non-existent-id",
                creator_id=eligible_creator.id,
                data=update_data
            )
        assert exc.value.status_code == 404
        assert "not found" in str(exc.value.detail).lower()
    
    # ========================================================================
    # TASK 5.3: delete_tier() - Check no active subscribers
    # ========================================================================
    
    def test_delete_tier_success(self, db: Session, tier: MembershipTier):
        """Task 5.3: Test successful tier deletion with no subscribers"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        
        result = service.delete_tier(
            tier_id=tier.id,
            creator_id=fan_club.creator_id
        )
        
        assert result is True
        
        # Verify tier is deleted
        deleted_tier = db.query(MembershipTier).filter(MembershipTier.id == tier.id).first()
        assert deleted_tier is None
    
    def test_delete_tier_with_active_subscribers(self, db: Session, tier_with_active_subscription: MembershipTier):
        """Task 5.3: Test deleting tier with active subscribers fails"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier_with_active_subscription.fan_club_id).first()
        
        with pytest.raises(HTTPException) as exc:
            service.delete_tier(
                tier_id=tier_with_active_subscription.id,
                creator_id=fan_club.creator_id
            )
        assert exc.value.status_code == 400
        assert "active subscriptions" in str(exc.value.detail).lower()
        assert "pause the tier instead" in str(exc.value.detail).lower()
    
    def test_delete_tier_with_paused_subscribers(self, db: Session, tier_with_paused_subscription: MembershipTier):
        """Task 5.3: Test deleting tier with paused subscribers fails"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier_with_paused_subscription.fan_club_id).first()
        
        with pytest.raises(HTTPException) as exc:
            service.delete_tier(
                tier_id=tier_with_paused_subscription.id,
                creator_id=fan_club.creator_id
            )
        assert exc.value.status_code == 400
        assert "active subscriptions" in str(exc.value.detail).lower()
    
    def test_delete_tier_unauthorized(self, db: Session, tier: MembershipTier, other_creator: User):
        """Task 5.3: Test deleting tier without ownership fails"""
        service = TierService(db)
        
        with pytest.raises(HTTPException) as exc:
            service.delete_tier(
                tier_id=tier.id,
                creator_id=other_creator.id  # Different creator
            )
        assert exc.value.status_code == 403
        assert "permission" in str(exc.value.detail).lower()
    
    def test_delete_tier_not_found(self, db: Session, eligible_creator: User):
        """Task 5.3: Test deleting non-existent tier"""
        service = TierService(db)
        
        with pytest.raises(HTTPException) as exc:
            service.delete_tier(
                tier_id="non-existent-id",
                creator_id=eligible_creator.id
            )
        assert exc.value.status_code == 404
        assert "not found" in str(exc.value.detail).lower()
    
    # ========================================================================
    # TASK 5.4: list_tiers() - Get all tiers for fan club
    # ========================================================================
    
    def test_list_tiers_empty(self, db: Session, fan_club: FanClub):
        """Task 5.4: Test listing tiers for fan club with no tiers"""
        service = TierService(db)
        
        tiers = service.list_tiers(fan_club_id=fan_club.id)
        
        assert tiers == []
    
    def test_list_tiers_ordered_by_level(self, db: Session, fan_club_with_multiple_tiers: FanClub):
        """Task 5.4: Test listing tiers returns them ordered by tier level"""
        service = TierService(db)
        
        tiers = service.list_tiers(fan_club_id=fan_club_with_multiple_tiers.id)
        
        assert len(tiers) == 3
        assert tiers[0].tier_level == 1
        assert tiers[1].tier_level == 2
        assert tiers[2].tier_level == 3
    
    def test_list_tiers_only_active(self, db: Session, fan_club_with_inactive_tier: FanClub):
        """Task 5.4: Test listing tiers excludes inactive by default"""
        service = TierService(db)
        
        tiers = service.list_tiers(fan_club_id=fan_club_with_inactive_tier.id)
        
        # Should only return active tiers
        assert all(tier.is_active for tier in tiers)
        # Should not include the inactive tier
        assert len(tiers) < len(fan_club_with_inactive_tier.tiers)
    
    def test_list_tiers_include_inactive(self, db: Session, fan_club_with_inactive_tier: FanClub):
        """Task 5.4: Test listing tiers with include_inactive flag"""
        service = TierService(db)
        
        tiers = service.list_tiers(
            fan_club_id=fan_club_with_inactive_tier.id,
            include_inactive=True
        )
        
        # Should include all tiers
        assert len(tiers) == len(fan_club_with_inactive_tier.tiers)
        # Should have at least one inactive tier
        assert any(not tier.is_active for tier in tiers)
    
    # ========================================================================
    # TASK 5.5: pause_tier() - Prevent new subscriptions
    # ========================================================================
    
    def test_pause_tier_success(self, db: Session, tier: MembershipTier):
        """Task 5.5: Test successfully pausing a tier"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        
        paused = service.pause_tier(
            tier_id=tier.id,
            creator_id=fan_club.creator_id
        )
        
        assert paused.is_active is False
    
    def test_pause_tier_with_subscribers(self, db: Session, tier_with_active_subscription: MembershipTier):
        """Task 5.5: Test pausing tier with active subscribers succeeds"""
        service = TierService(db)
        fan_club = db.query(FanClub).filter(FanClub.id == tier_with_active_subscription.fan_club_id).first()
        
        # Pausing should succeed even with active subscribers
        paused = service.pause_tier(
            tier_id=tier_with_active_subscription.id,
            creator_id=fan_club.creator_id
        )
        
        assert paused.is_active is False
        
        # Verify subscription still exists and is active
        subscription = db.query(Subscription).filter(
            Subscription.tier_id == tier_with_active_subscription.id
        ).first()
        assert subscription is not None
        assert subscription.status == "active"
    
    def test_pause_tier_unauthorized(self, db: Session, tier: MembershipTier, other_creator: User):
        """Task 5.5: Test pausing tier without ownership fails"""
        service = TierService(db)
        
        with pytest.raises(HTTPException) as exc:
            service.pause_tier(
                tier_id=tier.id,
                creator_id=other_creator.id  # Different creator
            )
        assert exc.value.status_code == 403
        assert "permission" in str(exc.value.detail).lower()
    
    def test_pause_tier_not_found(self, db: Session, eligible_creator: User):
        """Task 5.5: Test pausing non-existent tier"""
        service = TierService(db)
        
        with pytest.raises(HTTPException) as exc:
            service.pause_tier(
                tier_id="non-existent-id",
                creator_id=eligible_creator.id
            )
        assert exc.value.status_code == 404
        assert "not found" in str(exc.value.detail).lower()
    
    # ========================================================================
    # TASK 5.6: Calculate yearly price (10% discount from monthly)
    # ========================================================================
    
    def test_calculate_price_monthly(self, db: Session):
        """Task 5.6: Test calculating monthly price"""
        service = TierService(db)
        
        price = service.calculate_price(
            monthly_price=Decimal("9.99"),
            billing_cycle="monthly"
        )
        
        assert price == Decimal("9.99")
    
    def test_calculate_price_yearly(self, db: Session):
        """Task 5.6: Test calculating yearly price with 10% discount"""
        service = TierService(db)
        
        price = service.calculate_price(
            monthly_price=Decimal("10.00"),
            billing_cycle="yearly"
        )
        
        # 10.00 * 12 * 0.9 = 108.00 (10% discount = 2 months free)
        assert price == Decimal("108.00")
    
    def test_calculate_price_yearly_various_amounts(self, db: Session):
        """Task 5.6: Test yearly price calculation with various amounts"""
        service = TierService(db)
        
        test_cases = [
            (Decimal("2.99"), Decimal("2.99") * 12 * Decimal("0.9")),   # 2.99 * 12 * 0.9
            (Decimal("4.99"), Decimal("4.99") * 12 * Decimal("0.9")),   # 4.99 * 12 * 0.9
            (Decimal("19.99"), Decimal("19.99") * 12 * Decimal("0.9")), # 19.99 * 12 * 0.9
            (Decimal("99.99"), Decimal("99.99") * 12 * Decimal("0.9")), # 99.99 * 12 * 0.9
        ]
        
        for monthly_price, expected_yearly in test_cases:
            yearly_price = service.calculate_price(
                monthly_price=monthly_price,
                billing_cycle="yearly"
            )
            assert yearly_price == expected_yearly
    
    def test_calculate_price_invalid_cycle(self, db: Session):
        """Task 5.6: Test invalid billing cycle raises error"""
        service = TierService(db)
        
        with pytest.raises(ValueError) as exc:
            service.calculate_price(
                monthly_price=Decimal("9.99"),
                billing_cycle="invalid"
            )
        assert "invalid billing cycle" in str(exc.value).lower()
    
    # ========================================================================
    # ADDITIONAL INTEGRATION TESTS
    # ========================================================================
    
    def test_get_tier_success(self, db: Session, tier: MembershipTier):
        """Test retrieving tier by ID"""
        service = TierService(db)
        
        retrieved = service.get_tier(tier_id=tier.id)
        
        assert retrieved is not None
        assert retrieved.id == tier.id
        assert retrieved.name == tier.name
    
    def test_get_tier_not_found(self, db: Session):
        """Test retrieving non-existent tier"""
        service = TierService(db)
        
        with pytest.raises(HTTPException) as exc:
            service.get_tier(tier_id="non-existent-id")
        assert exc.value.status_code == 404


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

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
    """Create a fully eligible creator"""
    import uuid
    from app.models.social import Follow
    from app.models.track import Track, TrackStatus
    
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
def other_creator(db: Session) -> User:
    """Create another creator for unauthorized access tests"""
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email="other@test.com",
        username="othercreator",
        hashed_password="hashed",
        role=UserRole.ARTIST,
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
def tier(db: Session, fan_club: FanClub) -> MembershipTier:
    """Create a test tier"""
    import uuid
    
    tier = MembershipTier(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        name="Bronze",
        description="Entry tier",
        tier_level=1,
        price_monthly=Decimal("4.99"),
        price_yearly=Decimal("53.89"),
        benefits=["Benefit 1", "Benefit 2"],
        is_active=True,
        subscriber_count=0
    )
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier


@pytest.fixture
def fan_club_with_multiple_tiers(db: Session, fan_club: FanClub) -> FanClub:
    """Create a fan club with 3 tiers"""
    import uuid
    
    tiers_data = [
        {"name": "Bronze", "level": 1, "price": Decimal("4.99")},
        {"name": "Silver", "level": 2, "price": Decimal("9.99")},
        {"name": "Gold", "level": 3, "price": Decimal("19.99")},
    ]
    
    for tier_data in tiers_data:
        yearly_price = tier_data["price"] * 12 * Decimal("0.9")
        tier = MembershipTier(
            id=str(uuid.uuid4()),
            fan_club_id=fan_club.id,
            name=tier_data["name"],
            tier_level=tier_data["level"],
            price_monthly=tier_data["price"],
            price_yearly=yearly_price.quantize(Decimal("0.01")),
            is_active=True,
            benefits=[f"Benefit {tier_data['level']}"]
        )
        db.add(tier)
    
    db.commit()
    db.refresh(fan_club)
    return fan_club


@pytest.fixture
def fan_club_with_inactive_tier(db: Session, fan_club: FanClub) -> FanClub:
    """Create a fan club with active and inactive tiers"""
    import uuid
    
    # Active tier
    active_tier = MembershipTier(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        name="Active Tier",
        tier_level=1,
        price_monthly=Decimal("9.99"),
        price_yearly=Decimal("107.89"),
        is_active=True,
        benefits=["Active benefit"]
    )
    db.add(active_tier)
    
    # Inactive tier
    inactive_tier = MembershipTier(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        name="Inactive Tier",
        tier_level=2,
        price_monthly=Decimal("19.99"),
        price_yearly=Decimal("215.89"),
        is_active=False,
        benefits=["Inactive benefit"]
    )
    db.add(inactive_tier)
    
    db.commit()
    db.refresh(fan_club)
    return fan_club


@pytest.fixture
def tier_with_active_subscription(db: Session, tier: MembershipTier) -> MembershipTier:
    """Create a tier with an active subscription"""
    import uuid
    
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
        fan_club_id=tier.fan_club_id,
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
    db.commit()
    db.refresh(tier)
    return tier


@pytest.fixture
def tier_with_paused_subscription(db: Session, tier: MembershipTier) -> MembershipTier:
    """Create a tier with a paused subscription"""
    import uuid
    
    # Create subscriber
    subscriber = User(
        id=str(uuid.uuid4()),
        email="paused@test.com",
        username="pausedsubscriber",
        hashed_password="hashed",
        role=UserRole.FAN,
        is_active=True
    )
    db.add(subscriber)
    db.flush()
    
    # Create paused subscription
    subscription = Subscription(
        id=str(uuid.uuid4()),
        fan_club_id=tier.fan_club_id,
        tier_id=tier.id,
        subscriber_id=subscriber.id,
        status="paused",
        billing_cycle="monthly",
        price_paid=Decimal("9.99"),
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow(),
        payment_provider="stripe",
        auto_renew=True
    )
    db.add(subscription)
    db.commit()
    db.refresh(tier)
    return tier


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
