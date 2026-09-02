"""
Unit tests for messaging notification helpers

Tests for:
- create_message_notification: Creates notifications for new messages
- create_message_request_notification: Creates notifications for message requests
- should_create_notification: Checks notification preferences
- is_user_active_in_conversation: Checks if user is actively viewing
- get_notification_batching_key: Generates batching keys
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

from app.services.messaging_notification_helpers import (
    create_message_notification,
    create_message_request_notification,
    should_create_notification,
    is_user_active_in_conversation,
    get_notification_batching_key,
    should_batch_notification
)


# ============================================================================
# Test: get_notification_batching_key
# ============================================================================

def test_get_notification_batching_key():
    """Test batching key generation"""
    conversation_id = "conv-123"
    recipient_id = "user-456"
    
    result = get_notification_batching_key(conversation_id, recipient_id)
    
    assert result == "msg_batch_conv-123_user-456"


def test_get_notification_batching_key_different_ids():
    """Test batching key is different for different IDs"""
    key1 = get_notification_batching_key("conv-1", "user-1")
    key2 = get_notification_batching_key("conv-2", "user-1")
    key3 = get_notification_batching_key("conv-1", "user-2")
    
    assert key1 != key2
    assert key1 != key3
    assert key2 != key3


# ============================================================================
# Test: should_create_notification
# ============================================================================

@patch('app.services.messaging_notification_helpers.NotificationService')
def test_should_create_notification_enabled(mock_service_class):
    """Test returns True when notifications enabled"""
    mock_db = Mock()
    mock_service = Mock()
    mock_service_class.return_value = mock_service
    mock_prefs = Mock()
    mock_prefs.newmessage = True
    mock_service.get_or_create_preferences.return_value = mock_prefs
    
    result = should_create_notification("user-123", mock_db)
    
    assert result is True


@patch('app.services.messaging_notification_helpers.NotificationService')
def test_should_create_notification_disabled(mock_service_class):
    """Test returns False when notifications disabled"""
    mock_db = Mock()
    mock_service = Mock()
    mock_service_class.return_value = mock_service
    mock_prefs = Mock()
    mock_prefs.newmessage = False
    mock_service.get_or_create_preferences.return_value = mock_prefs
    
    result = should_create_notification("user-123", mock_db)
    
    assert result is False


@patch('app.services.messaging_notification_helpers.NotificationService')
def test_should_create_notification_exception_defaults_true(mock_service_class):
    """Test defaults to True on exception"""
    mock_db = Mock()
    mock_service_class.side_effect = Exception("DB error")
    
    result = should_create_notification("user-123", mock_db)
    
    assert result is True


# ============================================================================
# Test: is_user_active_in_conversation
# ============================================================================

@patch('app.services.messaging_notification_helpers.connection_manager')
def test_is_user_active_in_conversation_true(mock_manager):
    """Test returns True when user is viewing"""
    mock_db = Mock()
    mock_manager.is_user_viewing_conversation.return_value = True
    
    result = is_user_active_in_conversation("conv-123", "user-456", mock_db)
    
    assert result is True
    mock_manager.is_user_viewing_conversation.assert_called_once_with(
        user_id="user-456",
        conversation_id="conv-123"
    )


@patch('app.services.messaging_notification_helpers.connection_manager')
def test_is_user_active_in_conversation_false(mock_manager):
    """Test returns False when user is not viewing"""
    mock_db = Mock()
    mock_manager.is_user_viewing_conversation.return_value = False
    
    result = is_user_active_in_conversation("conv-123", "user-456", mock_db)
    
    assert result is False


@patch('app.services.messaging_notification_helpers.connection_manager')
def test_is_user_active_in_conversation_exception_defaults_false(mock_manager):
    """Test defaults to False on exception (safe to send notification)"""
    mock_db = Mock()
    mock_manager.is_user_viewing_conversation.side_effect = Exception("Connection error")
    
    result = is_user_active_in_conversation("conv-123", "user-456", mock_db)
    
    assert result is False


# ============================================================================
# Test: should_batch_notification
# ============================================================================

def test_should_batch_notification_returns_false():
    """Test batching returns False for now (placeholder)"""
    mock_db = Mock()
    
    result = should_batch_notification("user-123", "conv-456", mock_db)
    
    # Currently always returns False (no batching implemented yet)
    assert result is False


# ============================================================================
# Test: create_message_notification
# ============================================================================

@patch('app.services.messaging_notification_helpers.is_user_active_in_conversation')
@patch('app.services.messaging_notification_helpers.should_create_notification')
@patch('app.services.messaging_notification_helpers.NotificationService')
def test_create_message_notification_success(mock_service_class, mock_should_create, mock_is_active):
    """Test successfully creates message notification"""
    mock_db = Mock()
    mock_message = Mock()
    mock_message.id = "msg-123"
    mock_message.content = "Hello there! This is a longer message to test preview"
    mock_message.conversation_id = "conv-456"
    mock_message.sender_id = "user-789"
    
    mock_user = Mock()
    mock_user.id = "user-789"
    mock_user.username = "john_doe"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    mock_service = Mock()
    mock_service_class.return_value = mock_service
    mock_notification = Mock()
    mock_service.create_notification.return_value = mock_notification
    
    mock_should_create.return_value = True
    mock_is_active.return_value = False
    
    recipient_id = "user-recipient"
    result = create_message_notification(mock_message, recipient_id, mock_db)
    
    assert result is True
    mock_should_create.assert_called_once_with(recipient_id, mock_db)
    mock_is_active.assert_called_once_with("conv-456", recipient_id, mock_db)
    mock_service.create_notification.assert_called_once()
    
    # Verify notification details
    call_kwargs = mock_service.create_notification.call_args[1]
    assert call_kwargs['user_id'] == recipient_id
    assert call_kwargs['notification_type'] == "new_message"
    assert "john_doe" in call_kwargs['title']
    assert call_kwargs['message'] == "Hello there! This is a longer message to test prev..."


@patch('app.services.messaging_notification_helpers.is_user_active_in_conversation')
@patch('app.services.messaging_notification_helpers.should_create_notification')
def test_create_message_notification_skipped_preferences_disabled(mock_should_create, mock_is_active):
    """Test skips notification when preferences disabled"""
    mock_db = Mock()
    mock_message = Mock()
    
    mock_should_create.return_value = False
    
    result = create_message_notification(mock_message, "user-123", mock_db)
    
    assert result is False
    mock_is_active.assert_not_called()


@patch('app.services.messaging_notification_helpers.is_user_active_in_conversation')
@patch('app.services.messaging_notification_helpers.should_create_notification')
def test_create_message_notification_skipped_user_active(mock_should_create, mock_is_active):
    """Test skips notification when user actively viewing"""
    mock_db = Mock()
    mock_message = Mock()
    
    mock_should_create.return_value = True
    mock_is_active.return_value = True
    
    result = create_message_notification(mock_message, "user-123", mock_db)
    
    assert result is False


@patch('app.services.messaging_notification_helpers.is_user_active_in_conversation')
@patch('app.services.messaging_notification_helpers.should_create_notification')
@patch('app.services.messaging_notification_helpers.NotificationService')
def test_create_message_notification_sender_not_found(mock_service_class, mock_should_create, mock_is_active):
    """Test handles missing sender gracefully"""
    mock_db = Mock()
    mock_message = Mock()
    mock_message.sender_id = "user-nonexistent"
    
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    mock_should_create.return_value = True
    mock_is_active.return_value = False
    
    result = create_message_notification(mock_message, "user-123", mock_db)
    
    assert result is False


@patch('app.services.messaging_notification_helpers.is_user_active_in_conversation')
@patch('app.services.messaging_notification_helpers.should_create_notification')
@patch('app.services.messaging_notification_helpers.NotificationService')
def test_create_message_notification_preview_truncated(mock_service_class, mock_should_create, mock_is_active):
    """Test message preview is truncated to 50 chars"""
    mock_db = Mock()
    mock_message = Mock()
    mock_message.id = "msg-123"
    mock_message.content = "This is a really long message that should be truncated because it is more than fifty characters long"
    mock_message.conversation_id = "conv-456"
    mock_message.sender_id = "user-789"
    
    mock_user = Mock()
    mock_user.username = "alice"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    mock_service = Mock()
    mock_service_class.return_value = mock_service
    mock_service.create_notification.return_value = Mock()
    
    mock_should_create.return_value = True
    mock_is_active.return_value = False
    
    create_message_notification(mock_message, "user-recipient", mock_db)
    
    # Check the preview was truncated
    call_kwargs = mock_service.create_notification.call_args[1]
    preview = call_kwargs['message']
    assert len(preview) == 53  # 50 chars + "..."
    assert preview.endswith("...")


# ============================================================================
# Test: create_message_request_notification
# ============================================================================

@patch('app.services.messaging_notification_helpers.is_user_active_in_conversation')
@patch('app.services.messaging_notification_helpers.should_create_notification')
@patch('app.services.messaging_notification_helpers.NotificationService')
def test_create_message_request_notification_success(mock_service_class, mock_should_create, mock_is_active):
    """Test successfully creates message request notification"""
    mock_db = Mock()
    mock_conversation = Mock()
    mock_conversation.id = "conv-123"
    mock_conversation.last_message_preview = "Hey, I'd like to collaborate!"
    
    # Mock ConversationParticipant query
    mock_participant1 = Mock()
    mock_participant1.user_id = "user-sender"
    mock_participant2 = Mock()
    mock_participant2.user_id = "user-recipient"
    
    mock_db.query.return_value.filter.return_value.all.return_value = [
        mock_participant1,
        mock_participant2
    ]
    
    # Mock sender user
    mock_sender = Mock()
    mock_sender.id = "user-sender"
    mock_sender.username = "collaborator"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_sender
    
    mock_service = Mock()
    mock_service_class.return_value = mock_service
    mock_notification = Mock()
    mock_service.create_notification.return_value = mock_notification
    
    mock_should_create.return_value = True
    mock_is_active.return_value = False
    
    result = create_message_request_notification(mock_conversation, "user-recipient", mock_db)
    
    assert result is True
    mock_service.create_notification.assert_called_once()
    
    # Verify notification details
    call_kwargs = mock_service.create_notification.call_args[1]
    assert call_kwargs['user_id'] == "user-recipient"
    assert call_kwargs['notification_type'] == "message_request"
    assert "collaborator" in call_kwargs['title']


@patch('app.services.messaging_notification_helpers.is_user_active_in_conversation')
@patch('app.services.messaging_notification_helpers.should_create_notification')
def test_create_message_request_notification_skipped_preferences(mock_should_create, mock_is_active):
    """Test skips when preferences disabled"""
    mock_db = Mock()
    mock_conversation = Mock()
    
    mock_should_create.return_value = False
    
    result = create_message_request_notification(mock_conversation, "user-123", mock_db)
    
    assert result is False


@patch('app.services.messaging_notification_helpers.is_user_active_in_conversation')
@patch('app.services.messaging_notification_helpers.should_create_notification')
def test_create_message_request_notification_skipped_active(mock_should_create, mock_is_active):
    """Test skips when user actively viewing"""
    mock_db = Mock()
    mock_conversation = Mock()
    
    mock_should_create.return_value = True
    mock_is_active.return_value = True
    
    result = create_message_request_notification(mock_conversation, "user-123", mock_db)
    
    assert result is False
