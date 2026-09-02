"""
Pytest configuration and fixtures for fan club system tests.

Provides:
- Database fixtures (in-memory SQLite)
- User fixtures
- Fan club fixtures
- Mock payment providers
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models.user import User
from app.models.fan_club import (
    FanClub,
    MembershipTier,
    Subscription,
    SubscriptionPayment,
    ExclusiveContent
)
from app.core.security import hash_password


# ==================== DATABASE FIXTURES ====================

@pytest.fixture(scope="session")
def db_engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Session:
    """Create a new database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    # Rollback to keep tests isolated
    session.close()
    transaction.rollback()
    connection.close()


# ==================== USER FIXTURES ====================

@pytest.fixture
def creator_user(db_session: Session) -> User:
    """Create a test creator user."""
    from app.models.user import UserRole
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email="creator@test.com",
        username="testcreator",
        full_name="Test Creator",
        hashed_password=hash_password("password123"),
        is_active=True,
        is_verified=True,
        email_verified=True,
        role=UserRole.ARTIST
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def subscriber_user(db_session: Session) -> User:
    """Create a test subscriber user."""
    from app.models.user import UserRole
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email="subscriber@test.com",
        username="testsubscriber",
        full_name="Test Subscriber",
        hashed_password=hash_password("password123"),
        is_active=True,
        is_verified=True,
        email_verified=True,
        role=UserRole.FAN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def another_subscriber(db_session: Session) -> User:
    """Create another test subscriber."""
    from app.models.user import UserRole
    import uuid
    
    user = User(
        id=str(uuid.uuid4()),
        email="subscriber2@test.com",
        username="testsubscriber2",
        full_name="Test Subscriber 2",
        hashed_password=hash_password("password123"),
        is_active=True,
        is_verified=True,
        email_verified=True,
        role=UserRole.FAN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ==================== FAN CLUB FIXTURES ====================

@pytest.fixture
def fan_club(db_session: Session, creator_user: User) -> FanClub:
    """Create a test fan club."""
    import uuid
    
    fan_club = FanClub(
        id=str(uuid.uuid4()),
        creator_id=creator_user.id,
        name="Test Fan Club",
        description="A test fan club for unit tests",
        welcome_message="Welcome to the test fan club!",
        is_active=True
    )
    db_session.add(fan_club)
    db_session.commit()
    db_session.refresh(fan_club)
    return fan_club


@pytest.fixture
def membership_tiers(db_session: Session, fan_club: FanClub) -> dict:
    """Create test membership tiers."""
    import uuid
    
    tiers = {}
    
    basic = MembershipTier(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        name="Basic",
        description="Basic tier with standard content",
        tier_level=1,
        price_monthly=Decimal("4.99"),
        price_yearly=Decimal("49.99"),
        benefits=["Access to basic content", "Monthly update"],
        is_active=True
    )
    db_session.add(basic)
    
    premium = MembershipTier(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        name="Premium",
        description="Premium tier with exclusive content",
        tier_level=2,
        price_monthly=Decimal("9.99"),
        price_yearly=Decimal("99.99"),
        benefits=["Access to exclusive content", "Early releases", "Monthly live chat"],
        is_active=True
    )
    db_session.add(premium)
    
    vip = MembershipTier(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        name="VIP",
        description="VIP tier with premium perks",
        tier_level=3,
        price_monthly=Decimal("19.99"),
        price_yearly=Decimal("199.99"),
        benefits=["All premium benefits", "1-on-1 messaging", "VIP merchandise"],
        is_active=True
    )
    db_session.add(vip)
    
    db_session.commit()
    
    db_session.refresh(basic)
    db_session.refresh(premium)
    db_session.refresh(vip)
    
    tiers['basic'] = basic
    tiers['premium'] = premium
    tiers['vip'] = vip
    
    return tiers


# ==================== SUBSCRIPTION FIXTURES ====================

@pytest.fixture
def active_subscription(
    db_session: Session,
    subscriber_user: User,
    fan_club: FanClub,
    membership_tiers: dict
) -> Subscription:
    """Create an active subscription."""
    import uuid
    from datetime import datetime
    
    now = datetime.utcnow()
    
    subscription = Subscription(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        tier_id=membership_tiers['premium'].id,
        subscriber_id=subscriber_user.id,
        status="active",
        billing_cycle="monthly",
        price_paid=Decimal("9.99"),
        currency="USD",
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        next_billing_date=now + timedelta(days=30),
        started_at=now,
        auto_renew=True,
        payment_provider="stripe",
        payment_provider_customer_id="cus_test123",
        payment_provider_subscription_id="sub_test123"
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription


@pytest.fixture
def cancelled_subscription(
    db_session: Session,
    another_subscriber: User,
    fan_club: FanClub,
    membership_tiers: dict
) -> Subscription:
    """Create a cancelled subscription."""
    import uuid
    from datetime import datetime
    
    now = datetime.utcnow()
    
    subscription = Subscription(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        tier_id=membership_tiers['basic'].id,
        subscriber_id=another_subscriber.id,
        status="cancelled",
        billing_cycle="monthly",
        price_paid=Decimal("4.99"),
        currency="USD",
        current_period_start=now - timedelta(days=60),
        current_period_end=now - timedelta(days=30),
        started_at=now - timedelta(days=90),
        cancelled_at=now - timedelta(days=30),
        auto_renew=False,
        payment_provider="stripe"
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription


@pytest.fixture
def trial_subscription(
    db_session: Session,
    subscriber_user: User,
    fan_club: FanClub,
    membership_tiers: dict
) -> Subscription:
    """Create a trial subscription."""
    import uuid
    from datetime import datetime
    
    now = datetime.utcnow()
    
    subscription = Subscription(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        tier_id=membership_tiers['basic'].id,
        subscriber_id=subscriber_user.id,
        status="trialing",
        billing_cycle="monthly",
        price_paid=Decimal("0.00"),
        currency="USD",
        current_period_start=now,
        current_period_end=now + timedelta(days=7),
        next_billing_date=now + timedelta(days=7),
        trial_ends_at=now + timedelta(days=7),
        started_at=now,
        auto_renew=True,
        payment_provider="stripe"
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription


# ==================== PAYMENT FIXTURES ====================

@pytest.fixture
def successful_payment(
    db_session: Session,
    active_subscription: Subscription
) -> SubscriptionPayment:
    """Create a successful payment."""
    import uuid
    from datetime import datetime
    
    payment = SubscriptionPayment(
        id=str(uuid.uuid4()),
        subscription_id=active_subscription.id,
        amount=active_subscription.price_paid,
        currency="USD",
        status="succeeded",
        payment_method="card",
        payment_provider="stripe",
        payment_provider_payment_id="pi_test123",
        payment_provider_invoice_id="in_test123",
        platform_fee=Decimal("1.00"),
        creator_payout=Decimal("8.99"),
        payment_processing_fee=Decimal("0.30"),
        paid_at=datetime.utcnow()
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    return payment


@pytest.fixture
def failed_payment(
    db_session: Session,
    active_subscription: Subscription
) -> SubscriptionPayment:
    """Create a failed payment."""
    import uuid
    
    payment = SubscriptionPayment(
        id=str(uuid.uuid4()),
        subscription_id=active_subscription.id,
        amount=active_subscription.price_paid,
        currency="USD",
        status="failed",
        payment_method="card",
        payment_provider="stripe",
        payment_provider_payment_id="pi_fail123",
        failure_code="card_declined",
        failure_message="Your card was declined",
        retry_attempt=1
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    return payment


# ==================== CONTENT FIXTURES ====================

@pytest.fixture
def exclusive_content(
    db_session: Session,
    fan_club: FanClub
) -> ExclusiveContent:
    """Create exclusive content."""
    import uuid
    
    content = ExclusiveContent(
        id=str(uuid.uuid4()),
        fan_club_id=fan_club.id,
        content_type="post",
        content_id=str(uuid.uuid4()),
        minimum_tier_level=2,
        teaser_text="This is an exclusive post for premium members",
        view_count=0,
        engagement_count=0
    )
    db_session.add(content)
    db_session.commit()
    db_session.refresh(content)
    return content


# ==================== MOCK PROVIDERS ====================

class MockStripeProvider:
    """Mock Stripe payment provider for testing."""
    
    @staticmethod
    def charge_subscription(amount: Decimal, customer_id: str) -> tuple:
        """Mock charging a subscription."""
        # Return (success, payment_data)
        return (True, {
            'id': 'ch_test123',
            'amount': int(amount * 100),
            'currency': 'usd',
            'status': 'succeeded'
        })
    
    @staticmethod
    def refund_payment(charge_id: str, amount: Decimal = None) -> tuple:
        """Mock refunding a payment."""
        return (True, {'id': 'ref_test123', 'status': 'succeeded'})
    
    @staticmethod
    def create_customer(email: str, name: str) -> str:
        """Mock creating a customer."""
        return 'cus_test123'


class MockPaystackProvider:
    """Mock Paystack payment provider for testing."""
    
    @staticmethod
    def charge_authorization(amount: Decimal, authorization_code: str) -> tuple:
        """Mock charging an authorization."""
        return (True, {
            'reference': f'ref_{datetime.utcnow().timestamp()}',
            'amount': int(amount * 100),
            'status': 'success'
        })
    
    @staticmethod
    def refund_payment(reference: str, amount: Decimal = None) -> tuple:
        """Mock refunding a payment."""
        return (True, {'status': 'success'})


@pytest.fixture
def mock_stripe_provider():
    """Provide mock Stripe provider."""
    return MockStripeProvider


@pytest.fixture
def mock_paystack_provider():
    """Provide mock Paystack provider."""
    return MockPaystackProvider


# ==================== TOKEN FIXTURES ====================

@pytest.fixture
def creator_token(creator_user: User):
    """Generate test token for creator."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": creator_user.id})


@pytest.fixture
def subscriber_token(subscriber_user: User):
    """Generate test token for subscriber."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": subscriber_user.id})
