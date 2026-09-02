"""
Test suite for conversation API endpoints (Tasks 8.2, 8.3, 8.4)
Tests POST /conversations, GET /conversations/{id}, and DELETE /conversations/{id}
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.db.database import get_db, Base
from app.core.security import create_access_token
from app.models.user import User
from app.models.messaging import Conversation, ConversationParticipant, BlockedUser, UserMessageSettings
from app.models.social import Follow
import uuid

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_conversations.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_users(db):
    """Create test users"""
    from app.models.user import UserRole
    
    user1 = User(
        id=str(uuid.uuid4()),
        username="testuser1",
        email="test1@example.com",
        hashed_password="hashedpass",
        full_name="Test User 1",
        role=UserRole.ARTIST,
        is_verified=False
    )
    user2 = User(
        id=str(uuid.uuid4()),
        username="testuser2",
        email="test2@example.com",
        hashed_password="hashedpass",
        full_name="Test User 2",
        role=UserRole.DJ,
        is_verified=True
    )
    user3 = User(
        id=str(uuid.uuid4()),
        username="testuser3",
        email="test3@example.com",
        hashed_password="hashedpass",
        full_name="Test User 3",
        role=UserRole.PRODUCER,
        is_verified=False
    )
    
    db.add(user1)
    db.add(user2)
    db.add(user3)
    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    db.refresh(user3)
    
    return {"user1": user1, "user2": user2, "user3": user3}

@pytest.fixture
def auth_headers(test_users):
    """Create authentication headers for test users"""
    user1_token = create_access_token(data={"sub": test_users["user1"].id})
    user2_token = create_access_token(data={"sub": test_users["user2"].id})
    user3_token = create_access_token(data={"sub": test_users["user3"].id})
    
    return {
        "user1": {"Authorization": f"Bearer {user1_token}"},
        "user2": {"Authorization": f"Bearer {user2_token}"},
        "user3": {"Authorization": f"Bearer {user3_token}"}
    }


# ============================================================================
# Task 8.2: POST /api/v1/conversations Tests
# ============================================================================

def test_create_new_conversation_success(db, test_users, auth_headers):
    """Test creating a new conversation between two users"""
    response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "id" in data
    assert "participants" in data
    assert "is_message_request" in data
    assert "request_status" in data
    assert "last_activity_at" in data
    assert "created_at" in data
    
    # Verify participants
    assert len(data["participants"]) == 1  # Only shows other participant
    assert data["participants"][0]["user_id"] == test_users["user2"].id
    
    # Verify conversation created in database
    conversation = db.query(Conversation).filter_by(id=data["id"]).first()
    assert conversation is not None
    
    # Verify both users are participants
    participants = db.query(ConversationParticipant).filter_by(
        conversation_id=conversation.id
    ).all()
    assert len(participants) == 2
    participant_ids = {p.user_id for p in participants}
    assert test_users["user1"].id in participant_ids
    assert test_users["user2"].id in participant_ids


def test_get_existing_conversation(db, test_users, auth_headers):
    """Test that calling POST with existing conversation returns the existing one"""
    # Create first conversation
    response1 = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    assert response1.status_code == 201
    conversation_id_1 = response1.json()["id"]
    
    # Try to create again - should return existing
    response2 = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    assert response2.status_code == 201
    conversation_id_2 = response2.json()["id"]
    
    # Should be the same conversation
    assert conversation_id_1 == conversation_id_2


def test_create_conversation_with_message_request(db, test_users, auth_headers):
    """Test that message request is created when recipient has followers-only filter"""
    # Set user2 to followers-only
    settings = UserMessageSettings(
        id=str(uuid.uuid4()),
        user_id=test_users["user2"].id,
        message_filter="followers",
        read_receipts_enabled=True,
        typing_indicators_enabled=True
    )
    db.add(settings)
    db.commit()
    
    # User1 (non-follower) creates conversation with user2
    response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Should be a message request
    assert data["is_message_request"] is True
    assert data["request_status"] == "pending"


def test_create_conversation_no_message_request_for_follower(db, test_users, auth_headers):
    """Test that no message request is created when sender follows recipient"""
    # Set user2 to followers-only
    settings = UserMessageSettings(
        id=str(uuid.uuid4()),
        user_id=test_users["user2"].id,
        message_filter="followers",
        read_receipts_enabled=True,
        typing_indicators_enabled=True
    )
    db.add(settings)
    
    # User1 follows user2
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=test_users["user1"].id,
        following_id=test_users["user2"].id
    )
    db.add(follow)
    db.commit()
    
    # User1 creates conversation with user2
    response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Should NOT be a message request
    assert data["is_message_request"] is False
    assert data["request_status"] == "accepted"


def test_create_conversation_blocked_user(db, test_users, auth_headers):
    """Test that conversation creation fails when users have blocked each other"""
    # User2 blocks user1
    block = BlockedUser(
        id=str(uuid.uuid4()),
        blocker_id=test_users["user2"].id,
        blocked_id=test_users["user1"].id,
        reason="Testing"
    )
    db.add(block)
    db.commit()
    
    # User1 tries to create conversation
    response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 403
    assert "blocked" in response.json()["detail"].lower()


def test_create_conversation_with_self_fails(db, test_users, auth_headers):
    """Test that user cannot create conversation with themselves"""
    response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user1"].id},
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 400
    assert "yourself" in response.json()["detail"].lower()


def test_create_conversation_nonexistent_recipient(db, test_users, auth_headers):
    """Test that conversation creation fails with non-existent recipient"""
    fake_id = str(uuid.uuid4())
    response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": fake_id},
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_conversation_requires_auth(db, test_users):
    """Test that creating conversation requires authentication"""
    response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id}
    )
    
    assert response.status_code == 401


# ============================================================================
# Task 8.3: GET /api/v1/conversations/{conversation_id} Tests
# ============================================================================

def test_get_conversation_success(db, test_users, auth_headers):
    """Test retrieving a conversation by ID"""
    # Create conversation first
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # Get the conversation
    response = client.get(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert data["id"] == conversation_id
    assert "participants" in data
    assert "last_message" in data
    assert "unread_count" in data
    assert "is_message_request" in data
    assert "last_activity_at" in data
    
    # Verify participant info
    assert len(data["participants"]) == 1
    assert data["participants"][0]["user_id"] == test_users["user2"].id
    assert data["participants"][0]["username"] == "testuser2"


def test_get_conversation_both_participants_can_access(db, test_users, auth_headers):
    """Test that both participants can access the conversation"""
    # Create conversation
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # User1 can access
    response1 = client.get(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user1"]
    )
    assert response1.status_code == 200
    
    # User2 can also access
    response2 = client.get(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user2"]
    )
    assert response2.status_code == 200


def test_get_conversation_non_participant_denied(db, test_users, auth_headers):
    """Test that non-participants cannot access a conversation"""
    # Create conversation between user1 and user2
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # User3 (non-participant) tries to access
    response = client.get(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user3"]
    )
    
    assert response.status_code == 403
    assert "access denied" in response.json()["detail"].lower()


def test_get_conversation_not_found(db, test_users, auth_headers):
    """Test retrieving non-existent conversation returns 404"""
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/messaging/conversations/{fake_id}",
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_conversation_requires_auth(db, test_users, auth_headers):
    """Test that getting conversation requires authentication"""
    # Create conversation
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # Try without auth
    response = client.get(f"/api/v1/messaging/conversations/{conversation_id}")
    assert response.status_code == 401


# ============================================================================
# Task 8.4: DELETE /api/v1/conversations/{conversation_id} Tests
# ============================================================================

def test_delete_conversation_success(db, test_users, auth_headers):
    """Test soft deleting (leaving) a conversation"""
    # Create conversation
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # User1 leaves conversation
    response = client.delete(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 200
    assert "success" in response.json()["message"].lower()
    
    # Verify left_at is set in database
    participant = db.query(ConversationParticipant).filter_by(
        conversation_id=conversation_id,
        user_id=test_users["user1"].id
    ).first()
    
    assert participant is not None
    assert participant.left_at is not None


def test_delete_conversation_hides_from_list(db, test_users, auth_headers):
    """Test that leaving a conversation hides it from user's conversation list"""
    # Create conversation
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # Verify it appears in user1's list
    list_response = client.get(
        "/api/v1/messaging/conversations",
        headers=auth_headers["user1"]
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["conversations"]) == 1
    
    # User1 leaves
    client.delete(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user1"]
    )
    
    # Verify it no longer appears in list
    list_response2 = client.get(
        "/api/v1/messaging/conversations",
        headers=auth_headers["user1"]
    )
    assert list_response2.status_code == 200
    assert len(list_response2.json()["conversations"]) == 0


def test_delete_conversation_other_participant_unaffected(db, test_users, auth_headers):
    """Test that leaving a conversation doesn't affect other participant"""
    # Create conversation
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # User1 leaves
    client.delete(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user1"]
    )
    
    # User2 can still access the conversation
    response = client.get(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user2"]
    )
    assert response.status_code == 200
    
    # User2 still sees it in their list
    list_response = client.get(
        "/api/v1/messaging/conversations",
        headers=auth_headers["user2"]
    )
    assert list_response.status_code == 200
    assert len(list_response.json()["conversations"]) == 1


def test_delete_conversation_not_participant(db, test_users, auth_headers):
    """Test that non-participants cannot leave a conversation"""
    # Create conversation between user1 and user2
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # User3 tries to leave
    response = client.delete(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user3"]
    )
    
    assert response.status_code == 403


def test_delete_conversation_not_found(db, test_users, auth_headers):
    """Test deleting non-existent conversation returns 404"""
    fake_id = str(uuid.uuid4())
    response = client.delete(
        f"/api/v1/messaging/conversations/{fake_id}",
        headers=auth_headers["user1"]
    )
    
    assert response.status_code == 404


def test_delete_conversation_requires_auth(db, test_users, auth_headers):
    """Test that deleting conversation requires authentication"""
    # Create conversation
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # Try without auth
    response = client.delete(f"/api/v1/messaging/conversations/{conversation_id}")
    assert response.status_code == 401


def test_delete_conversation_twice_is_idempotent(db, test_users, auth_headers):
    """Test that leaving a conversation twice doesn't cause errors"""
    # Create conversation
    create_response = client.post(
        "/api/v1/messaging/conversations",
        json={"recipient_id": test_users["user2"].id},
        headers=auth_headers["user1"]
    )
    conversation_id = create_response.json()["id"]
    
    # Leave first time
    response1 = client.delete(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user1"]
    )
    assert response1.status_code == 200
    
    # Leave second time - should fail since user already left
    response2 = client.delete(
        f"/api/v1/messaging/conversations/{conversation_id}",
        headers=auth_headers["user1"]
    )
    # Should return 403 since user is no longer a participant
    assert response2.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
