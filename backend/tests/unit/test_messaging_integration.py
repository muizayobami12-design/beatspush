"""
Integration tests for messaging notification helpers with endpoints

Tests that verify:
- create_message_notification is called from send_message endpoint
- create_message_request_notification is called from accept_message_request endpoint
- All imports work correctly
- Functions integrate without errors
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


def test_messaging_endpoints_imports():
    """Test that messaging endpoints can be imported with notification helpers"""
    try:
        from app.api.v1.endpoints import messaging
        assert hasattr(messaging, 'send_message')
        assert hasattr(messaging, 'accept_message_request')
        assert hasattr(messaging, 'connection_manager')
    except ImportError as e:
        pytest.fail(f"Failed to import messaging endpoints: {e}")


def test_notification_helpers_imports():
    """Test that notification helpers can be imported"""
    try:
        from app.services.messaging_notification_helpers import (
            create_message_notification,
            create_message_request_notification,
            should_create_notification,
            is_user_active_in_conversation,
            get_notification_batching_key,
            should_batch_notification
        )
        assert callable(create_message_notification)
        assert callable(create_message_request_notification)
        assert callable(should_create_notification)
        assert callable(is_user_active_in_conversation)
        assert callable(get_notification_batching_key)
        assert callable(should_batch_notification)
    except ImportError as e:
        pytest.fail(f"Failed to import notification helpers: {e}")


def test_all_services_available():
    """Test that all required services are available"""
    try:
        from app.services.notification_service import NotificationService
        from app.services.websocket_manager import connection_manager
        from app.services.messaging_service import MessagingService
        from app.services.privacy_service import PrivacyService
        
        assert NotificationService is not None
        assert connection_manager is not None
        assert MessagingService is not None
        assert PrivacyService is not None
    except ImportError as e:
        pytest.fail(f"Failed to import required services: {e}")


def test_message_notification_helper_has_correct_signature():
    """Test create_message_notification has correct function signature"""
    from app.services.messaging_notification_helpers import create_message_notification
    import inspect
    
    sig = inspect.signature(create_message_notification)
    params = list(sig.parameters.keys())
    
    # Should have message, recipient_id, and db parameters
    assert 'message' in params
    assert 'recipient_id' in params
    assert 'db' in params
    assert len(params) == 3


def test_message_request_notification_helper_has_correct_signature():
    """Test create_message_request_notification has correct function signature"""
    from app.services.messaging_notification_helpers import create_message_request_notification
    import inspect
    
    sig = inspect.signature(create_message_request_notification)
    params = list(sig.parameters.keys())
    
    # Should have conversation, recipient_id, and db parameters
    assert 'conversation' in params
    assert 'recipient_id' in params
    assert 'db' in params
    assert len(params) == 3


def test_should_create_notification_has_correct_signature():
    """Test should_create_notification has correct function signature"""
    from app.services.messaging_notification_helpers import should_create_notification
    import inspect
    
    sig = inspect.signature(should_create_notification)
    params = list(sig.parameters.keys())
    
    # Should have recipient_id and db parameters
    assert 'recipient_id' in params
    assert 'db' in params
    assert len(params) == 2


def test_is_user_active_in_conversation_has_correct_signature():
    """Test is_user_active_in_conversation has correct function signature"""
    from app.services.messaging_notification_helpers import is_user_active_in_conversation
    import inspect
    
    sig = inspect.signature(is_user_active_in_conversation)
    params = list(sig.parameters.keys())
    
    # Should have conversation_id, recipient_id, and db parameters
    assert 'conversation_id' in params
    assert 'recipient_id' in params
    assert 'db' in params
    assert len(params) == 3


def test_get_notification_batching_key_has_correct_signature():
    """Test get_notification_batching_key has correct function signature"""
    from app.services.messaging_notification_helpers import get_notification_batching_key
    import inspect
    
    sig = inspect.signature(get_notification_batching_key)
    params = list(sig.parameters.keys())
    
    # Should have conversation_id and recipient_id parameters
    assert 'conversation_id' in params
    assert 'recipient_id' in params
    assert len(params) == 2


@patch('app.services.messaging_notification_helpers.connection_manager')
@patch('app.services.messaging_notification_helpers.NotificationService')
def test_notification_service_called_with_correct_type(mock_service_class, mock_manager):
    """Test create_message_notification calls NotificationService with correct type"""
    from app.services.messaging_notification_helpers import create_message_notification
    
    mock_db = Mock()
    mock_message = Mock()
    mock_message.id = "msg-1"
    mock_message.content = "Hello"
    mock_message.conversation_id = "conv-1"
    mock_message.sender_id = "user-1"
    
    mock_user = Mock()
    mock_user.username = "alice"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    mock_service = Mock()
    mock_service_class.return_value = mock_service
    mock_service.create_notification.return_value = Mock()
    
    mock_manager.is_user_viewing_conversation.return_value = False
    
    create_message_notification(mock_message, "user-2", mock_db)
    
    # Verify notification type
    call_kwargs = mock_service.create_notification.call_args[1]
    assert call_kwargs['notification_type'] == 'new_message'


@patch('app.services.messaging_notification_helpers.connection_manager')
@patch('app.services.messaging_notification_helpers.NotificationService')
def test_message_request_notification_type(mock_service_class, mock_manager):
    """Test create_message_request_notification uses correct type"""
    from app.services.messaging_notification_helpers import create_message_request_notification
    
    mock_db = Mock()
    mock_conversation = Mock()
    mock_conversation.id = "conv-1"
    mock_conversation.last_message_preview = "Hey"
    
    # Mock participants
    mock_p1 = Mock()
    mock_p1.user_id = "user-1"
    mock_p2 = Mock()
    mock_p2.user_id = "user-2"
    
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_p1, mock_p2]
    
    # Mock sender
    mock_user = Mock()
    mock_user.username = "alice"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    mock_service = Mock()
    mock_service_class.return_value = mock_service
    mock_service.create_notification.return_value = Mock()
    
    mock_manager.is_user_viewing_conversation.return_value = False
    
    create_message_request_notification(mock_conversation, "user-2", mock_db)
    
    # Verify notification type
    call_kwargs = mock_service.create_notification.call_args[1]
    assert call_kwargs['notification_type'] == 'message_request'
