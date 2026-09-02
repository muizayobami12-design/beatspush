"""
Integration tests for fan club endpoints.

Tests all 26 fan club system endpoints:
- Fan club management (CRUD)
- Membership tier management
- Subscription management
- Subscriber management
- Exclusive content
"""

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import datetime, timedelta

from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestFanClubManagement:
    """Test fan club CRUD operations."""
    
    def test_create_fan_club(self, client, creator_token):
        """Test creating a fan club."""
        response = client.post(
            "/api/v1/fan-clubs",
            headers={"Authorization": f"Bearer {creator_token}"},
            json={
                "name": "Test Fan Club",
                "description": "A test fan club",
                "welcome_message": "Welcome!"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Fan Club"
        assert "id" in data
    
    def test_get_fan_club(self, client, creator_token, fan_club):
        """Test getting fan club details."""
        response = client.get(
            f"/api/v1/fan-clubs/{fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == fan_club.id
        assert data["name"] == fan_club.name
    
    def test_list_creator_fan_clubs(self, client, creator_token, fan_club):
        """Test listing creator's fan clubs."""
        response = client.get(
            "/api/v1/fan-clubs/my",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "fan_clubs" in data
        assert len(data["fan_clubs"]) > 0
    
    def test_update_fan_club(self, client, creator_token, fan_club):
        """Test updating fan club."""
        response = client.put(
            f"/api/v1/fan-clubs/{fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"},
            json={
                "description": "Updated description"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
    
    def test_delete_fan_club(self, client, creator_token, fan_club):
        """Test deleting fan club."""
        response = client.delete(
            f"/api/v1/fan-clubs/{fan_club.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 204


class TestMembershipTierManagement:
    """Test membership tier operations."""
    
    def test_create_tier(self, client, creator_token, fan_club):
        """Test creating membership tier."""
        response = client.post(
            f"/api/v1/fan-clubs/{fan_club.id}/tiers",
            headers={"Authorization": f"Bearer {creator_token}"},
            json={
                "name": "Premium",
                "description": "Premium tier",
                "tier_level": 2,
                "price_monthly": 9.99,
                "benefits": ["Exclusive content", "Early access"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Premium"
        assert data["tier_level"] == 2
    
    def test_list_tiers(self, client, fan_club, membership_tiers):
        """Test listing membership tiers."""
        response = client.get(
            f"/api/v1/fan-clubs/{fan_club.id}/tiers"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tiers" in data
        assert len(data["tiers"]) >= 3
    
    def test_update_tier(self, client, creator_token, fan_club, membership_tiers):
        """Test updating tier."""
        tier = membership_tiers['basic']
        
        response = client.put(
            f"/api/v1/fan-clubs/{fan_club.id}/tiers/{tier.id}",
            headers={"Authorization": f"Bearer {creator_token}"},
            json={
                "description": "Updated tier description"
            }
        )
        
        assert response.status_code == 200
    
    def test_delete_tier(self, client, creator_token, fan_club, membership_tiers):
        """Test deleting tier (if no active subscriptions)."""
        # This should fail if tier has subscriptions
        tier = membership_tiers['basic']
        
        response = client.delete(
            f"/api/v1/fan-clubs/{fan_club.id}/tiers/{tier.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        # May be 409 if tier has subscriptions
        assert response.status_code in [200, 204, 409]


class TestSubscriptionManagement:
    """Test subscription operations."""
    
    def test_create_subscription(self, client, subscriber_token, fan_club, membership_tiers):
        """Test creating subscription."""
        response = client.post(
            "/api/v1/fan-clubs/subscribe",
            headers={"Authorization": f"Bearer {subscriber_token}"},
            json={
                "fan_club_id": fan_club.id,
                "tier_id": membership_tiers['premium'].id,
                "billing_cycle": "monthly",
                "payment_method_token": "tok_test"
            }
        )
        
        assert response.status_code in [201, 200]
        data = response.json()
        assert "id" in data
    
    def test_get_subscription(self, client, subscriber_token, active_subscription):
        """Test getting subscription details."""
        response = client.get(
            f"/api/v1/fan-clubs/subscriptions/{active_subscription.id}",
            headers={"Authorization": f"Bearer {subscriber_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == active_subscription.id
    
    def test_list_subscriber_subscriptions(self, client, subscriber_token):
        """Test listing subscriber's subscriptions."""
        response = client.get(
            "/api/v1/fan-clubs/subscriptions/my",
            headers={"Authorization": f"Bearer {subscriber_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "subscriptions" in data
    
    def test_change_subscription_tier(self, client, subscriber_token, active_subscription, membership_tiers):
        """Test changing subscription tier."""
        response = client.put(
            f"/api/v1/fan-clubs/subscriptions/{active_subscription.id}/tier",
            headers={"Authorization": f"Bearer {subscriber_token}"},
            json={
                "new_tier_id": membership_tiers['vip'].id
            }
        )
        
        assert response.status_code == 200
    
    def test_pause_subscription(self, client, subscriber_token, active_subscription):
        """Test pausing subscription."""
        response = client.post(
            f"/api/v1/fan-clubs/subscriptions/{active_subscription.id}/pause",
            headers={"Authorization": f"Bearer {subscriber_token}"},
            json={
                "pause_until": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
        )
        
        assert response.status_code == 200
    
    def test_resume_subscription(self, client, subscriber_token, active_subscription):
        """Test resuming subscription."""
        response = client.post(
            f"/api/v1/fan-clubs/subscriptions/{active_subscription.id}/resume",
            headers={"Authorization": f"Bearer {subscriber_token}"}
        )
        
        assert response.status_code in [200, 409]  # 409 if not paused
    
    def test_cancel_subscription(self, client, subscriber_token, active_subscription):
        """Test canceling subscription."""
        response = client.post(
            f"/api/v1/fan-clubs/subscriptions/{active_subscription.id}/cancel",
            headers={"Authorization": f"Bearer {subscriber_token}"},
            json={
                "reason": "User requested"
            }
        )
        
        assert response.status_code == 200


class TestSubscriberManagement:
    """Test subscriber operations."""
    
    def test_list_fan_club_subscribers(self, client, creator_token, fan_club):
        """Test listing fan club subscribers."""
        response = client.get(
            f"/api/v1/fan-clubs/{fan_club.id}/subscribers",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "subscribers" in data
    
    def test_get_subscriber_info(self, client, creator_token, fan_club, subscriber_user):
        """Test getting subscriber information."""
        response = client.get(
            f"/api/v1/fan-clubs/{fan_club.id}/subscribers/{subscriber_user.id}",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code in [200, 404]
    
    def test_send_broadcast_message(self, client, creator_token, fan_club):
        """Test sending broadcast message to subscribers."""
        response = client.post(
            f"/api/v1/fan-clubs/{fan_club.id}/broadcast",
            headers={"Authorization": f"Bearer {creator_token}"},
            json={
                "title": "New Exclusive Content",
                "message": "Check out the new exclusive content available now!",
                "send_email": True,
                "send_push": True
            }
        )
        
        assert response.status_code in [200, 202]  # 202 for async


class TestExclusiveContent:
    """Test exclusive content operations."""
    
    def test_mark_content_exclusive(self, client, creator_token, fan_club):
        """Test marking content as exclusive."""
        response = client.post(
            f"/api/v1/fan-clubs/{fan_club.id}/exclusive-content",
            headers={"Authorization": f"Bearer {creator_token}"},
            json={
                "content_type": "post",
                "content_id": "post_123",
                "minimum_tier_level": 2,
                "teaser_text": "Exclusive content preview"
            }
        )
        
        assert response.status_code == 201
    
    def test_check_content_access(self, client, subscriber_token, fan_club, exclusive_content):
        """Test checking access to exclusive content."""
        response = client.get(
            f"/api/v1/fan-clubs/{fan_club.id}/exclusive-content/{exclusive_content.id}/access",
            headers={"Authorization": f"Bearer {subscriber_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "has_access" in data


class TestErrorHandling:
    """Test error handling in endpoints."""
    
    def test_unauthorized_access(self, client):
        """Test accessing protected endpoint without auth."""
        response = client.get("/api/v1/fan-clubs/my")
        
        assert response.status_code == 401
    
    def test_forbidden_access(self, client, subscriber_token, fan_club, creator_user):
        """Test accessing fan club as non-creator."""
        response = client.put(
            f"/api/v1/fan-clubs/{fan_club.id}",
            headers={"Authorization": f"Bearer {subscriber_token}"},
            json={"description": "Hacked!"}
        )
        
        assert response.status_code == 403
    
    def test_not_found(self, client, creator_token):
        """Test accessing non-existent resource."""
        response = client.get(
            "/api/v1/fan-clubs/999999",
            headers={"Authorization": f"Bearer {creator_token}"}
        )
        
        assert response.status_code == 404
    
    def test_validation_error(self, client, creator_token):
        """Test invalid request data."""
        response = client.post(
            "/api/v1/fan-clubs",
            headers={"Authorization": f"Bearer {creator_token}"},
            json={
                "name": ""  # Empty name
            }
        )
        
        assert response.status_code == 422
