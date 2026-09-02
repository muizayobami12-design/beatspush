"""
Live Streaming API Endpoints
Twitch integration, real-time chat, tipping, stream management
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.dependencies import get_current_user, get_db
from app.services.live_streaming_service import LiveStreamingService

router = APIRouter(prefix="/streams", tags=["Live Streaming"])

stream_service = LiveStreamingService()


# ============ PYDANTIC MODELS ============

class CreateStreamRequest(BaseModel):
    title: str
    description: str
    category: str
    scheduled_at: Optional[datetime] = None


class SendTipRequest(BaseModel):
    amount: float
    message: Optional[str] = None


# ============ STREAM MANAGEMENT ============

@router.post("")
async def create_stream(
    request: CreateStreamRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create new scheduled live stream
    - title: Stream title
    - description: Stream description
    - category: Stream category (DJ Set, Tutorial, Q&A, etc.)
    - scheduled_at: When to go live (optional, defaults to now + 1 hour)
    """
    result = await stream_service.create_stream(
        current_user.id,
        request.title,
        request.description,
        request.scheduled_at,
        request.category,
        db,
    )
    return result


@router.post("/{stream_id}/start")
async def start_stream(
    stream_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a scheduled stream"""
    result = await stream_service.start_stream(stream_id, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{stream_id}/end")
async def end_stream(
    stream_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """End a live stream"""
    result = await stream_service.end_stream(stream_id, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{stream_id}/stats")
async def get_stream_stats(
    stream_id: str,
    db: Session = Depends(get_db),
):
    """Get detailed stream statistics"""
    result = await stream_service.get_stream_stats(stream_id, db)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/upcoming")
async def get_upcoming_streams(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Get upcoming scheduled streams"""
    result = await stream_service.get_upcoming_streams(limit, db)
    return {"streams": result}


# ============ REAL-TIME CHAT ============

@router.websocket("/ws/{stream_id}/chat")
async def websocket_chat(
    websocket: WebSocket,
    stream_id: str,
    user_id: str,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time chat during stream
    Connect: ws://api.beatpush.com/api/v1/streams/ws/{stream_id}/chat?user_id={user_id}
    """
    await websocket.accept()

    # Track viewer
    await stream_service.on_viewer_join(stream_id, user_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            if data.get("type") == "message":
                # Send chat message
                result = await stream_service.send_chat_message(
                    stream_id,
                    user_id,
                    data.get("message", ""),
                    is_moderator=data.get("is_moderator", False),
                    db=db,
                )

                # Broadcast to all connected clients
                await websocket.send_json({
                    "type": "message",
                    "data": result,
                })

    except Exception as e:
        print(f"Chat error: {e}")
    finally:
        await stream_service.on_viewer_leave(stream_id, user_id)


@router.post("/{stream_id}/chat")
async def send_chat(
    stream_id: str,
    message: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send chat message to stream (REST alternative)"""
    result = await stream_service.send_chat_message(
        stream_id,
        current_user.id,
        message,
        db=db,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{stream_id}/chat")
async def get_chat(
    stream_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get recent chat messages from stream"""
    messages = await stream_service.get_chat_history(stream_id, limit, db)
    return {"messages": messages}


@router.delete("/{stream_id}/chat/{message_id}")
async def delete_message(
    stream_id: str,
    message_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete chat message (moderator only)"""
    result = await stream_service.delete_chat_message(message_id, current_user.id, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============ TIPPING ============

@router.post("/{stream_id}/tips")
async def send_tip(
    stream_id: str,
    request: SendTipRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send tip to streamer during live stream
    - amount: Tip amount in NGN
    - message: Optional message with the tip
    """
    result = await stream_service.send_tip(
        stream_id,
        current_user.id,
        request.amount,
        request.message,
        db,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{stream_id}/tips")
async def get_stream_tips(
    stream_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Get tip history for stream"""
    tips = await stream_service.get_stream_tips(stream_id, limit, db)
    return {
        "stream_id": stream_id,
        "tips": tips,
        "total_count": len(tips),
    }


# ============ VIEWER TRACKING ============

@router.post("/{stream_id}/viewers/join")
async def join_stream(
    stream_id: str,
    current_user = Depends(get_current_user),
):
    """Track viewer joining stream"""
    await stream_service.on_viewer_join(stream_id, current_user.id)
    return {"status": "joined", "stream_id": stream_id}


@router.post("/{stream_id}/viewers/leave")
async def leave_stream(
    stream_id: str,
    current_user = Depends(get_current_user),
):
    """Track viewer leaving stream"""
    await stream_service.on_viewer_leave(stream_id, current_user.id)
    return {"status": "left", "stream_id": stream_id}


@router.get("/{stream_id}/viewers")
async def get_viewer_count(stream_id: str):
    """Get current viewer count for stream"""
    count = stream_service.get_viewer_count(stream_id)
    return {"stream_id": stream_id, "viewer_count": count}
