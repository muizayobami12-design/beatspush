"""
Integration tests for Fan Club API Endpoints
Tests full API request/response cycles
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from main import app
from app.models.user import User
from app.models.fan_club import FanClub, MembershipTier


client = TestClient(app)


class TestFanClubEndpoints:
    """Test suite for fan club API endpoints"""
    
    def test_create_fan_club_success(self, auth_token: str):
        """Test POST /api/v1/fan-clubs"""
        response = client.post(
            "/api/v1/fan-clubs",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "API Test Club",
                "description": "Created via API",
                "welcome_message": "Welcome!"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Test Club"
        assert data["is_active"] is True
    
    def test_create_fan_club_unauthorized(self):
        """Test creating fan club without auth fails"""
        response = client.post(
            "/api/v1/fan-clubs",
            json={"name": "Test Club"}
        )
        
        assert response.status_code == 401
    
    def test_get_my_fan_club(self, auth_token: str, fan_club: FanClub):
        """Test GET /api/v1/fan-clubs/me"""
        response = client.get(
            "/api/v1/fan-clubs/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == fan_club.id
        assert "tiers" in data
    
    def test_update_fan_club(self, auth_token: str, fan_club: FanClub):
        """Test PUT /api/v1/fan-clubs/me"""
        response = client.put(
            "/api/v1/fan-clubs/me",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"description": "Updated via API"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated via API"
    
    def test_get_fan_club_stats(self, auth_token: str, fan_club: FanClub):
        """Test GET /api/v1/fan-clubs/me/stats"""
        response = client.get(
            "/api/v1/fan-clubs/me/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_members" in data
        assert "monthly_revenue" in data
    
    def test_get_analytics(self, auth_token: str, fan_club: FanClub):
        """Test GET /api/v1/fan-clubs/me/analytics"""
        response = client.get(
            "/api/v1/fan-clubs/me/analytics",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mrr" in data
        assert "churn" in data
        assert "ltv" in data
        assert "retention_cohorts" in data
        assert "revenue_forecast" in data
        assert "engagement" in data


class TestTierEndpoints:
    """Test suite for tier management endpoints"""
    
    def test_create_tier_success(self, auth_token: str, fan_club: FanClub):
        """Test POST /api/v1/fan-clubs/me/tiers"""
        response = client.post(
            "/api/v1/fan-clubs/me/tiers",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "API Tier",
                "description": "Created via API",
                "tier_level": 1,
                "monthly_price": 9.99,
                "benefits": ["Benefit 1", "Benefit 2"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Tier"
        assert data["tier_level"] == 1
        assert data["monthly_price"] == 9.99
        # Yearly should be auto-calculated with 10% discount
        assert data["yearly_price"] == 9.99 * 10  # 10 months
    
    def test_create_tier_invalid_level(self, auth_token: str, fan_club: FanClub):
        """Test creating tier with invalid level fails"""
        response = client.post(
            "/api/v1/fan-clubs/me/tiers",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Invalid Tier",
                "tier_level": 5,  # Invalid: must be 1-3
                "monthly_price": 9.99
            }
        )
        
        assert response.status_code == 400
    
    def test_list_tiers(self, auth_token: str, fan_club: FanClub, tier: MembershipTier):
        """Test GET /api/v1/fan-clubs/{id}/tiers"""
        response = client.get(
            f"/api/v1/fan-clubs/{fan_club.id}/tiers",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["id"] == tier.id
    
    def test_update_tier(self, auth_token: str, tier: MembershipTier):
        """Test PUT /api/v1/fan-clubs/me/tiers/{id}"""
        response = client.put(
            f"/api/v1/fan-clubs/me/tiers/{tier.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"description": "Updated tier description"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated tier description"
    
    def test_delete_tier(self, auth_token: str, tier: MembershipTier):
        """Test DELETE /api/v1/fan-clubs/me/tiers/{id}"""
        response = client.delete(
            f"/api/v1/fan-clubs/me/tiers/{tier.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestSubscriptionEndpoints:
    """Test suite for subscription endpoints"""
    
    def test_create_subscription(self, fan_auth_token: str, tier: MembershipTier):
        """Test POST /api/v1/fan-clubs/subscriptions"""
        response = client.post(
            "/api/v1/fan-clubs/subscriptions",
            headers={"Authorization": f"Bearer {fan_auth_token}"},
            json={
                "tier_id": tier.id,
                "billing_cycle": "monthly",
                "payment_method": {
                    "provider": "stripe",
                    "token": "tok_visa"
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["tier_id"] == tier.id
        assert data["status"] == "active"
        assert data["billing_cycle"] == "monthly"
    
    def test_list_my_subscriptions(self, fan_auth_token: str):
        """Test GET /api/v1/fan-clubs/subscriptions/me"""
        response = client.get(
            "/api/v1/fan-clubs/subscriptions/me",
            headers={"Authorization": f"Bearer {fan_auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "subscriptions" in data
        assert "total" in data
    
    def test_cancel_subscription(
        self, 
        fan_auth_token: str, 
        subscription_id: str
    ):
        """Test DELETE /api/v1/fan-clubs/subscriptions/{id}"""
        response = client.delete(
            f"/api/v1/fan-clubs/subscriptions/{subscription_id}",
            headers={"Authorization": f"Bearer {fan_auth_token}"},
            params={"immediate": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["active", "cancelled"]
    
    def test_pause_subscription(
        self, 
        fan_auth_token: str, 
        subscription_id: str
    ):
        """Test POST /api/v1/fan-clubs/subscriptions/{id}/pause"""
        from datetime import datetime, timedelta
        pause_until = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        response = client.post(
            f"/api/v1/fan-clubs/subscriptions/{subscription_id}/pause",
            headers={"Authorization": f"Bearer {fan_auth_token}"},
            json={"pause_until": pause_until}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paused"


class TestWebhookEndpoints:
    """Test suite for webhook endpoints"""
    
    def test_stripe_webhook_test_mode(self):
        """Test POST /api/v1/webhooks/stripe in test mode"""
        response = client.post(
            "/api/v1/webhooks/stripe",
            json={
                "type": "invoice.paid",
                "data": {
                    "object": {
                        "id": "in_test",
                        "subscription": "sub_test",
                        "amount_paid": 999,
                        "currency": "usd"
                    }
                }
            }
        )
        
        # Should return 200 even in test mode
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_paystack_webhook_test_mode(self):
        """Test POST /api/v1/webhooks/paystack in test mode"""
        response = client.post(
            "/api/v1/webhooks/paystack",
            json={
                "event": "charge.success",
                "data": {
                    "reference": "test_ref",
                    "amount": 99900,
                    "currency": "NGN",
                    "metadata": {
                        "subscription_id": "sub_test"
                    }
                }
            }
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"


# Pytest Fixtures

@pytest.fixture
def db():
    """Database session"""
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
        id="api-creator-test",
        email="api@creator.com",
        username="apicreator",
        account_type="creator",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def fan_user(db: Session) -> User:
    """Create test fan"""
    user = User(
        id="api-fan-test",
        email="api@fan.com",
        username="apifan",
        account_type="fan"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(creator_user: User) -> str:
    """Generate auth token for creator"""
    from app.core.security import create_access_token
    return create_access_token({"sub": creator_user.id})


@pytest.fixture
def fan_auth_token(fan_user: User) -> str:
    """Generate auth token for fan"""
    from app.core.security import create_access_token
    return create_access_token({"sub": fan_user.id})


@pytest.fixture
def fan_club(db: Session, creator_user: User) -> FanClub:
    """Create test fan club"""
    club = FanClub(
        id="api-club-test",
        creator_id=creator_user.id,
        name="API Test Club",
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
        id="api-tier-test",
        fan_club_id=fan_club.id,
        name="API Tier",
        tier_level=2,
        price_monthly=Decimal("9.99"),
        price_yearly=Decimal("99.99"),
        is_active=True
    )
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier


@pytest.fixture
def subscription_id(
    db: Session, 
    fan_club: FanClub, 
    tier: MembershipTier,
    fan_user: User
) -> str:
    """Create test subscription and return ID"""
    from app.models.fan_club import Subscription
    from datetime import datetime, timedelta
    
    sub = Subscription(
        id="api-sub-test",
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
    return sub.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
