"""
WebSocket Connection Manager - Real-time messaging infrastructure
Tasks 7.1-7.3: Connection management, typing indicators, message broadcasting
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import asyncio
import json
from datetime import datetime

from app.models.messaging import Message, Conversation
from app.schemas.messaging import (
    MessageResponse, TypingIndicatorEvent, 
    NewMessageEvent, MessageReadEvent, UserStatusEvent
)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time messaging
    
    Task 7.1: Connection management
    Task 7.2: Typing indicators with auto-timeout
    Task 7.3: Message and status broadcasting
    """
    
    def __init__(self):
        # Active WebSocket connections: user_id -> list of WebSocket connections
        # (Users can have multiple connections from different devices)
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # Active conversations: conversation_id -> set of user_ids currently viewing
        # Used to suppress notifications when user is actively viewing
        self.active_conversations: Dict[str, Set[str]] = {}
        
        # Typing indicator timers: f"{conversation_id}:{user_id}" -> asyncio.Task
        # Automatically cancels typing after timeout
        self.typing_timers: Dict[str, asyncio.Task] = {}
    
    # ========================================================================
    # CONNECTION MANAGEMENT (Task 7.1)
    # ========================================================================
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """
        Register new WebSocket connection
        
        Args:
            user_id: User ID
            websocket: WebSocket connection
        """
        await websocket.accept()
        
        # Add connection to user's connection list
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        
        # Broadcast online status to relevant users
        await self.broadcast_user_status(user_id, "user_online")
        
        print(f"✅ WebSocket connected: user={user_id}, total_connections={len(self.active_connections[user_id])}")
    
    async def disconnect(self, user_id: str, websocket: WebSocket):
        """
        Remove WebSocket connection and cleanup
        
        Args:
            user_id: User ID
            websocket: WebSocket connection to remove
        """
        if user_id in self.active_connections:
            # Remove this specific connection
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # If no more connections, remove user completely
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
                # Broadcast offline status
                await self.broadcast_user_status(user_id, "user_offline")
                
                # Clean up active conversations
                for conv_id in list(self.active_conversations.keys()):
                    if user_id in self.active_conversations[conv_id]:
                        self.active_conversations[conv_id].discard(user_id)
                        if not self.active_conversations[conv_id]:
                            del self.active_conversations[conv_id]
                
                # Cancel any pending typing timers
                keys_to_delete = [
                    key for key in self.typing_timers.keys() 
                    if key.endswith(f":{user_id}")
                ]
                for key in keys_to_delete:
                    self.typing_timers[key].cancel()
                    del self.typing_timers[key]
        
        print(f"❌ WebSocket disconnected: user={user_id}")
    
    def is_user_online(self, user_id: str) -> bool:
        """
        Check if user has any active connections
        
        Args:
            user_id: User ID
            
        Returns:
            True if user is online
        """
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def is_user_viewing_conversation(self, user_id: str, conversation_id: str) -> bool:
        """
        Check if user is actively viewing a conversation
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            
        Returns:
            True if user is viewing the conversation
        """
        return (
            conversation_id in self.active_conversations and 
            user_id in self.active_conversations[conversation_id]
        )
    
    async def join_conversation(self, user_id: str, conversation_id: str):
        """
        Mark user as actively viewing a conversation
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
        """
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = set()
        
        self.active_conversations[conversation_id].add(user_id)
        print(f"👁️ User {user_id} joined conversation {conversation_id}")
    
    async def leave_conversation(self, user_id: str, conversation_id: str):
        """
        Mark user as no longer viewing a conversation
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
        """
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id].discard(user_id)
            
            # Clean up empty conversation sets
            if not self.active_conversations[conversation_id]:
                del self.active_conversations[conversation_id]
        
        print(f"👁️ User {user_id} left conversation {conversation_id}")
    
    # ========================================================================
    # SENDING MESSAGES (Task 7.1)
    # ========================================================================
    
    async def send_to_user(self, user_id: str, message: dict):
        """
        Send message to all of a user's active connections
        
        Args:
            user_id: User ID
            message: Message dict to send as JSON
        """
        if user_id not in self.active_connections:
            return
        
        # Send to all user's connections
        dead_connections = []
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                # Mark connection as dead
                dead_connections.append(connection)
                print(f"⚠️ Failed to send to user {user_id}: {e}")
        
        # Remove dead connections
        for dead_conn in dead_connections:
            if dead_conn in self.active_connections[user_id]:
                self.active_connections[user_id].remove(dead_conn)
        
        # Clean up if no connections left
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]
    
    async def broadcast_to_conversation(
        self,
        conversation_id: str,
        participant_ids: List[str],
        message: dict,
        exclude_user: str = None
    ):
        """
        Broadcast message to all participants in a conversation
        
        Args:
            conversation_id: Conversation ID
            participant_ids: List of participant user IDs
            message: Message dict to broadcast
            exclude_user: Optional user ID to exclude from broadcast
        """
        for user_id in participant_ids:
            # Skip excluded user (typically the sender)
            if user_id == exclude_user:
                continue
            
            await self.send_to_user(user_id, message)
    
    # ========================================================================
    # TYPING INDICATORS (Task 7.2)
    # ========================================================================
    
    async def handle_typing_indicator(
        self,
        user_id: str,
        conversation_id: str,
        participant_ids: List[str],
        is_typing: bool
    ):
        """
        Handle typing indicator with auto-timeout
        
        Args:
            user_id: User who is typing
            conversation_id: Conversation ID
            participant_ids: List of participant user IDs
            is_typing: True if typing started, False if stopped
        """
        timer_key = f"{conversation_id}:{user_id}"
        
        # Cancel existing timer for this user in this conversation
        if timer_key in self.typing_timers:
            self.typing_timers[timer_key].cancel()
            del self.typing_timers[timer_key]
        
        # Broadcast typing status
        event = TypingIndicatorEvent(
            conversation_id=conversation_id,
            user_id=user_id,
            is_typing=is_typing
        )
        
        await self.broadcast_to_conversation(
            conversation_id=conversation_id,
            participant_ids=participant_ids,
            message=event.dict(),
            exclude_user=user_id
        )
        
        # Set auto-timeout if typing started
        if is_typing:
            # Create task that will auto-cancel typing after 3 seconds
            task = asyncio.create_task(
                self._typing_timeout(user_id, conversation_id, participant_ids, timer_key)
            )
            self.typing_timers[timer_key] = task
    
    async def _typing_timeout(
        self,
        user_id: str,
        conversation_id: str,
        participant_ids: List[str],
        timer_key: str
    ):
        """
        Auto-cancel typing indicator after 3 seconds
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            participant_ids: Participant user IDs
            timer_key: Timer key for cleanup
        """
        try:
            # Wait 3 seconds
            await asyncio.sleep(3)
            
            # Send typing stopped event
            event = TypingIndicatorEvent(
                conversation_id=conversation_id,
                user_id=user_id,
                is_typing=False
            )
            
            await self.broadcast_to_conversation(
                conversation_id=conversation_id,
                participant_ids=participant_ids,
                message=event.dict(),
                exclude_user=user_id
            )
            
            # Clean up timer
            if timer_key in self.typing_timers:
                del self.typing_timers[timer_key]
            
        except asyncio.CancelledError:
            # Timer was cancelled (user sent message or manually stopped typing)
            pass
    
    async def cancel_typing_indicator(self, user_id: str, conversation_id: str):
        """
        Immediately cancel typing indicator (called when message is sent)
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
        """
        timer_key = f"{conversation_id}:{user_id}"
        
        if timer_key in self.typing_timers:
            self.typing_timers[timer_key].cancel()
            del self.typing_timers[timer_key]
    
    # ========================================================================
    # MESSAGE BROADCASTING (Task 7.3)
    # ========================================================================
    
    async def broadcast_new_message(
        self,
        conversation_id: str,
        participant_ids: List[str],
        message_response: MessageResponse
    ):
        """
        Broadcast new message to conversation participants
        
        Args:
            conversation_id: Conversation ID
            participant_ids: List of participant user IDs
            message_response: MessageResponse object
        """
        event = NewMessageEvent(
            conversation_id=conversation_id,
            message=message_response
        )
        
        # Convert to dict for JSON serialization
        message_dict = event.dict()
        
        # Convert datetime to ISO format strings
        message_dict = self._serialize_datetimes(message_dict)
        
        await self.broadcast_to_conversation(
            conversation_id=conversation_id,
            participant_ids=participant_ids,
            message=message_dict,
            exclude_user=message_response.sender_id  # Don't send back to sender
        )
        
        print(f"📨 Broadcasted new message in conversation {conversation_id}")
    
    async def broadcast_read_receipt(
        self,
        message_id: str,
        sender_id: str,
        reader_id: str,
        read_at: datetime
    ):
        """
        Broadcast read receipt to message sender
        
        Args:
            message_id: Message ID
            sender_id: Original message sender (will receive notification)
            reader_id: User who read the message
            read_at: Timestamp when message was read
        """
        event = MessageReadEvent(
            message_id=message_id,
            read_by=reader_id,
            read_at=read_at
        )
        
        # Convert to dict
        message_dict = event.dict()
        message_dict = self._serialize_datetimes(message_dict)
        
        # Send only to the message sender
        await self.send_to_user(sender_id, message_dict)
        
        print(f"✓✓ Broadcasted read receipt for message {message_id}")
    
    async def broadcast_user_status(self, user_id: str, status_type: str):
        """
        Broadcast user online/offline status
        
        Args:
            user_id: User ID
            status_type: "user_online" or "user_offline"
        """
        event = UserStatusEvent(
            type=status_type,
            user_id=user_id
        )
        
        # TODO: Send to users who should know about this user's status
        # (conversation participants, followers, etc.)
        # For now, this is a placeholder for future implementation
        
        print(f"🟢 User {user_id} status: {status_type}")
    
    async def broadcast_message_edit(
        self,
        conversation_id: str,
        participant_ids: List[str],
        message_response: MessageResponse
    ):
        """
        Broadcast message edit to conversation participants
        
        Args:
            conversation_id: Conversation ID
            participant_ids: Participant user IDs
            message_response: Updated message
        """
        event = {
            "type": "message_edited",
            "conversation_id": conversation_id,
            "message": message_response.dict()
        }
        
        event = self._serialize_datetimes(event)
        
        await self.broadcast_to_conversation(
            conversation_id=conversation_id,
            participant_ids=participant_ids,
            message=event,
            exclude_user=message_response.sender_id
        )
    
    async def broadcast_message_delete(
        self,
        conversation_id: str,
        participant_ids: List[str],
        message_id: str,
        sender_id: str
    ):
        """
        Broadcast message deletion to conversation participants
        
        Args:
            conversation_id: Conversation ID
            participant_ids: Participant user IDs
            message_id: Deleted message ID
            sender_id: Message sender ID
        """
        event = {
            "type": "message_deleted",
            "conversation_id": conversation_id,
            "message_id": message_id
        }
        
        await self.broadcast_to_conversation(
            conversation_id=conversation_id,
            participant_ids=participant_ids,
            message=event,
            exclude_user=sender_id
        )
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _serialize_datetimes(self, obj):
        """
        Recursively convert datetime objects to ISO format strings
        
        Args:
            obj: Object to serialize (dict, list, or value)
            
        Returns:
            Serialized object
        """
        if isinstance(obj, dict):
            return {k: self._serialize_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetimes(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
    
    def get_connection_stats(self) -> dict:
        """
        Get connection statistics for monitoring
        
        Returns:
            Dictionary with connection stats
        """
        total_connections = sum(len(conns) for conns in self.active_connections.values())
        
        return {
            "total_users_online": len(self.active_connections),
            "total_connections": total_connections,
            "active_conversations": len(self.active_conversations),
            "active_typing_indicators": len(self.typing_timers)
        }


# Global connection manager instance
# This will be used across all WebSocket endpoints
connection_manager = ConnectionManager()
