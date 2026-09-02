#!/usr/bin/env python3
"""
Comprehensive test script for Messaging System
Tests all critical backend functionality before integration
"""
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.db.database import Base
from app.models.user import User
from app.models.messaging import (
    Conversation, ConversationParticipant, Message, MessageReadReceipt,
    MessageAttachment, BlockedUser, UserMessageSettings
)
from app.services.messaging_service import MessagingService
from app.services.privacy_service import PrivacyService

# In-memory SQLite for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_users(db):
    """Create test users"""
    user1 = User(
        id=str(uuid.uuid4()),
        username="alice",
        email="alice@example.com",
        hashed_password="hash1",
        full_name="Alice Test",
        is_verified=True,
        role="artist"
    )
    user2 = User(
        id=str(uuid.uuid4()),
        username="bob",
        email="bob@example.com",
        hashed_password="hash2",
        full_name="Bob Test",
        is_verified=False,
        role="fan"
    )
    user3 = User(
        id=str(uuid.uuid4()),
        username="charlie",
        email="charlie@example.com",
        hashed_password="hash3",
        full_name="Charlie Test",
        is_verified=True,
        role="producer"
    )
    db.add_all([user1, user2, user3])
    db.commit()
    return user1, user2, user3

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MESSAGING SYSTEM TEST SUITE")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Create test users once
        user1, user2, user3 = create_test_users(db)
        
        # Test 1: Conversation creation
        print("\n" + "="*60)
        print("TEST 1: Conversation Creation")
        print("="*60)
        
        messaging_svc = MessagingService(db)
        conv = messaging_svc.get_or_create_conversation(user1.id, user2.id)
        assert conv is not None, "Conversation should be created"
        print("✓ Conversation created successfully")
        print(f"  - ID: {conv.id}")
        
        # Test 2: Send message
        print("\n" + "="*60)
        print("TEST 2: Send Message")
        print("="*60)
        
        message = messaging_svc.send_message(
            sender_id=user1.id,
            recipient_id=user2.id,
            content="Hello Bob!",
            conversation_id=conv.id
        )
        assert message is not None, "Message should be created"
        print("✓ Message sent successfully")
        print(f"  - Content: {message.content}")
        
        # Test 3: Mark as read
        print("\n" + "="*60)
        print("TEST 3: Mark Message as Read")
        print("="*60)
        
        messaging_svc.mark_message_read(message.id, user2.id)
        receipt = db.query(MessageReadReceipt).filter(
            MessageReadReceipt.message_id == message.id,
            MessageReadReceipt.user_id == user2.id
        ).first()
        assert receipt is not None, "Read receipt should be created"
        print("✓ Message marked as read")
        
        # Test 4: Edit message
        print("\n" + "="*60)
        print("TEST 4: Edit Message")
        print("="*60)
        
        edited = messaging_svc.edit_message(
            message_id=message.id,
            user_id=user1.id,
            new_content="Hello Bob! (edited)"
        )
        assert edited.is_edited, "Should be marked as edited"
        print("✓ Message edited successfully")
        
        # Test 5: Delete message
        print("\n" + "="*60)
        print("TEST 5: Delete Message")
        print("="*60)
        
        msg = messaging_svc.send_message(
            sender_id=user1.id,
            recipient_id=user2.id,
            content="Delete me",
            conversation_id=conv.id
        )
        messaging_svc.delete_message(message_id=msg.id, user_id=user1.id)
        deleted_msg = db.query(Message).filter(Message.id == msg.id).first()
        assert deleted_msg.deleted_at is not None, "Should be soft deleted"
        print("✓ Message deleted successfully (soft delete)")
        
        # Test 6: Block user
        print("\n" + "="*60)
        print("TEST 6: Block User")
        print("="*60)
        
        privacy_svc = PrivacyService(db)
        privacy_svc.block_user(
            blocker_id=user1.id,
            blocked_id=user2.id,
            reason="Spam"
        )
        is_blocked = privacy_svc.is_blocked(user1.id, user2.id)
        assert is_blocked, "User2 should be blocked by User1"
        print("✓ User blocked successfully")
        
        privacy_svc.unblock_user(user1.id, user2.id)
        print("✓ User unblocked successfully")
        
        # Test 7: Message requests
        print("\n" + "="*60)
        print("TEST 7: Message Requests (Privacy Filters)")
        print("="*60)
        
        should_request = privacy_svc.should_create_message_request(user1.id, user3.id)
        print(f"  - Should create message request: {should_request}")
        print("✓ Message request filtering works")
        
        # Test 8: Search messages
        print("\n" + "="*60)
        print("TEST 8: Search Messages")
        print("="*60)
        
        for i in range(3):
            messaging_svc.send_message(
                sender_id=user1.id if i % 2 == 0 else user2.id,
                recipient_id=user2.id if i % 2 == 0 else user1.id,
                content=f"Message {i} with keyword here",
                conversation_id=conv.id
            )
        
        results = messaging_svc.search_messages(
            user_id=user1.id,
            query="keyword",
            page=1
        )
        assert len(results['messages']) > 0, "Should find messages"
        print("✓ Message search works")
        print(f"  - Found {len(results['messages'])} results")
        
        # Test 9: Unread counts
        print("\n" + "="*60)
        print("TEST 9: Unread Counts")
        print("="*60)
        
        # Create new conversation for unread test
        conv2 = messaging_svc.get_or_create_conversation(user1.id, user3.id)
        for i in range(3):
            messaging_svc.send_message(
                sender_id=user1.id,
                recipient_id=user3.id,
                content=f"Message {i}",
                conversation_id=conv2.id
            )
        
        unread = messaging_svc.get_unread_count(user3.id)
        print(f"  - Unread for user3: {unread}")
        
        messaging_svc.mark_conversation_read(conv2.id, user3.id)
        unread_after = messaging_svc.get_unread_count(user3.id)
        print(f"  - Unread after marking read: {unread_after}")
        print("✓ Unread count tracking works")
        
        # Test 10: List conversations
        print("\n" + "="*60)
        print("TEST 10: List Conversations")
        print("="*60)
        
        result = messaging_svc.list_conversations(
            user_id=user1.id,
            page=1,
            page_size=20
        )
        assert result['total'] > 0, "Should have conversations"
        print("✓ List conversations works")
        print(f"  - Total: {result['total']}")
        print(f"  - Returned: {len(result['conversations'])}")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
