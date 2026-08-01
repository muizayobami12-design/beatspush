"""
WebSocket Endpoint for Real-Time Messaging
Wave 12: WebSocket connection handling, authentication, and event routing
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.db.database import get_db
from app.models.user import User
from app.services.websocket_manager import connection_manager
from app.services.messaging_service import MessagingService
from app.core.security import decode_token

router = APIRouter(tags=["WebSocket"])


# ============================================================================
# WEBSOCKET AUTHENTICATION (Task 12.1)
# ============================================================================

async def get_current_user_ws(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT access token"),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Authenticate WebSocket connection via JWT token
    
    Args:
        websocket: WebSocket connection
        token: JWT token from query parameter
        db: Database session
        
    Returns:
        Authenticated User object or None
        
    Note:
        Closes connection with 1008 policy violation if auth fails
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        return None
    
    try:
        # Decode and validate token
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return None
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return None
        
        if not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User account deactivated")
            return None
        
        return user
        
    except Exception as e:
        print(f"❌ WebSocket authentication failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return None


# ============================================================================
# WEBSOCKET ENDPOINT (Task 12.2)
# ============================================================================

@router.websocket("/ws/conversations")
async def websocket_conversations_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT access token"),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time messaging
    
    **Authentication:**
    - Pass JWT token as query parameter: ?token=your_jwt_token
    - Connection rejected if token invalid or missing
    
    **Client → Server Events:**
    ```json
    {
        "type": "typing_start",
        "conversation_id": "uuid"
    }
    
    {
        "type": "typing_stop",
        "conversation_id": "uuid"
    }
    
    {
        "type": "join_conversation",
        "conversation_id": "uuid"
    }
    
    {
        "type": "leave_conversation",
        "conversation_id": "uuid"
    }
    ```
    
    **Server → Client Events:**
    ```json
    {
        "type": "new_message",
        "conversation_id": "uuid",
        "message": { ... }
    }
    
    {
        "type": "typing_indicator",
        "conversation_id": "uuid",
        "user_id": "uuid",
        "is_typing": true/false
    }
    
    {
        "type": "message_read",
        "message_id": "uuid",
        "read_by": "uuid",
        "read_at": "timestamp"
    }
    
    {
        "type": "user_online",
        "user_id": "uuid"
    }
    
    {
        "type": "user_offline",
        "user_id": "uuid"
    }
    
    {
        "type": "message_edited",
        "conversation_id": "uuid",
        "message": { ... }
    }
    
    {
        "type": "message_deleted",
        "conversation_id": "uuid",
        "message_id": "uuid"
    }
    ```
    
    **Features:**
    - Real-time message delivery
    - Typing indicators with auto-timeout
    - Read receipts
    - Online/offline status
    - Multi-device support
    """
    # Authenticate user
    user = await get_current_user_ws(websocket, token, db)
    
    if not user:
        # Connection already closed by auth function
        return
    
    # Register connection
    await connection_manager.connect(user.id, websocket)
    
    # Initialize messaging service
    messaging_service = MessagingService(db)
    
    try:
        # Main event loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                event = json.loads(data)
                event_type = event.get("type")
                
                # Route event to appropriate handler
                if event_type == "typing_start":
                    await handle_typing_start(
                        user_id=user.id,
                        conversation_id=event.get("conversation_id"),
                        db=db
                    )
                
                elif event_type == "typing_stop":
                    await handle_typing_stop(
                        user_id=user.id,
                        conversation_id=event.get("conversation_id"),
                        db=db
                    )
                
                elif event_type == "join_conversation":
                    await handle_join_conversation(
                        user_id=user.id,
                        conversation_id=event.get("conversation_id")
                    )
                
                elif event_type == "leave_conversation":
                    await handle_leave_conversation(
                        user_id=user.id,
                        conversation_id=event.get("conversation_id")
                    )
                
                else:
                    # Unknown event type
                    print(f"⚠️ Unknown WebSocket event type: {event_type}")
            
            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON received from user {user.id}")
            except Exception as e:
                print(f"❌ Error handling WebSocket event: {e}")
    
    except WebSocketDisconnect:
        # Client disconnected
        print(f"🔌 WebSocket client disconnected: user={user.id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        # Clean up connection
        await connection_manager.disconnect(user.id, websocket)


# ============================================================================
# EVENT HANDLERS (Task 12.2)
# ============================================================================

async def handle_typing_start(user_id: str, conversation_id: str, db: Session):
    """
    Handle typing start event
    
    Args:
        user_id: User who started typing
        conversation_id: Conversation ID
        db: Database session
    """
    if not conversation_id:
        return
    
    # Get conversation participants
    from app.models.messaging import ConversationParticipant
    participants = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.left_at.is_(None)
        )
        .all()
    )
    
    participant_ids = [p.user_id for p in participants]
    
    # Broadcast typing indicator
    await connection_manager.handle_typing_indicator(
        user_id=user_id,
        conversation_id=conversation_id,
        participant_ids=participant_ids,
        is_typing=True
    )


async def handle_typing_stop(user_id: str, conversation_id: str, db: Session):
    """
    Handle typing stop event
    
    Args:
        user_id: User who stopped typing
        conversation_id: Conversation ID
        db: Database session
    """
    if not conversation_id:
        return
    
    # Get conversation participants
    from app.models.messaging import ConversationParticipant
    participants = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.left_at.is_(None)
        )
        .all()
    )
    
    participant_ids = [p.user_id for p in participants]
    
    # Broadcast typing stopped
    await connection_manager.handle_typing_indicator(
        user_id=user_id,
        conversation_id=conversation_id,
        participant_ids=participant_ids,
        is_typing=False
    )


async def handle_join_conversation(user_id: str, conversation_id: str):
    """
    Handle user joining a conversation
    
    Args:
        user_id: User ID
        conversation_id: Conversation ID
    """
    if not conversation_id:
        return
    
    await connection_manager.join_conversation(user_id, conversation_id)


async def handle_leave_conversation(user_id: str, conversation_id: str):
    """
    Handle user leaving a conversation
    
    Args:
        user_id: User ID
        conversation_id: Conversation ID
    """
    if not conversation_id:
        return
    
    await connection_manager.leave_conversation(user_id, conversation_id)


# ============================================================================
# RATE LIMITING (Task 12.3)
# ============================================================================

class RateLimitedWebSocketManager:
    """
    WebSocket manager with rate limiting
    
    Limits:
    - 60 messages per minute
    - 20 typing indicators per minute
    
    Note: This is a placeholder for future implementation
    Rate limiting would be implemented by tracking timestamps
    per user and action type, disconnecting abusive users.
    """
    pass


# ============================================================================
# MONITORING ENDPOINT
# ============================================================================

@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics
    
    **Returns:**
    - Total users online
    - Total connections (multi-device)
    - Active conversations being viewed
    - Active typing indicators
    
    **Use Cases:**
    - Monitoring and debugging
    - Dashboard metrics
    - Performance tracking
    """
    stats = connection_manager.get_connection_stats()
    
    return {
        "status": "operational",
        "stats": stats
    }
