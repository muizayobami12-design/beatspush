"""
Error handling utilities for messaging system
Task 15.4: Implement error handling and logging
"""
import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class MessageErrorCode(str, Enum):
    """Standardized error codes for messaging system."""
    BLOCKED_USER = "BLOCKED_USER"
    USER_NOT_ACCEPTING_MESSAGES = "USER_NOT_ACCEPTING_MESSAGES"
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    MESSAGE_NOT_FOUND = "MESSAGE_NOT_FOUND"
    NOT_CONVERSATION_PARTICIPANT = "NOT_CONVERSATION_PARTICIPANT"
    NOT_MESSAGE_SENDER = "NOT_MESSAGE_SENDER"
    MESSAGE_EDIT_EXPIRED = "MESSAGE_EDIT_EXPIRED"
    MESSAGE_ALREADY_DELETED = "MESSAGE_ALREADY_DELETED"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INVALID_MESSAGE_CONTENT = "INVALID_MESSAGE_CONTENT"
    CANNOT_BLOCK_SELF = "CANNOT_BLOCK_SELF"
    USER_ALREADY_BLOCKED = "USER_ALREADY_BLOCKED"
    USER_NOT_BLOCKED = "USER_NOT_BLOCKED"


class ErrorResponse(BaseModel):
    """Standardized error response model."""
    error: str
    detail: str
    code: Optional[str] = None
    timestamp: str
    request_id: Optional[str] = None


def create_error_response(
    error: str,
    detail: str,
    code: Optional[MessageErrorCode] = None,
    request_id: Optional[str] = None
) -> dict:
    """
    Create a standardized error response dict.
    
    Args:
        error: Short error name (e.g., "Not Found")
        detail: Detailed error message
        code: Optional machine-readable error code
        request_id: Optional request trace ID
        
    Returns:
        Error response dict
    """
    return {
        "error": error,
        "detail": detail,
        "code": code.value if code else None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id
    }


def log_messaging_error(
    error: Exception,
    context: str,
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> None:
    """
    Log a messaging error with structured context.
    Never logs message content for privacy.
    
    Args:
        error: The exception that occurred
        context: Where the error occurred (e.g., "send_message")
        user_id: Optional user ID for context
        conversation_id: Optional conversation ID for context
    """
    log_data = {
        "context": context,
        "error_type": type(error).__name__,
        "error_message": str(error),
        # Never log sensitive data
        "user_id": user_id,
        "conversation_id": conversation_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if isinstance(error, HTTPException):
        logger.warning(f"HTTP error in {context}: {log_data}")
    else:
        logger.error(f"Unexpected error in {context}: {log_data}")
        logger.debug(traceback.format_exc())


async def messaging_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for messaging endpoints.
    Returns structured error responses.
    
    Args:
        request: The incoming request
        exc: The exception that was raised
        
    Returns:
        JSONResponse with error details
    """
    request_id = request.headers.get("X-Request-ID")
    
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        error_response = create_error_response(
            error=exc.detail if isinstance(exc.detail, str) else "Request Error",
            detail=str(exc.detail),
            request_id=request_id
        )
    else:
        # Unexpected errors - log but don't expose internals
        status_code = 500
        logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}")
        logger.debug(traceback.format_exc())
        
        error_response = create_error_response(
            error="Internal Server Error",
            detail="An unexpected error occurred. Please try again.",
            request_id=request_id
        )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def websocket_error_handler(user_id: str, error: Exception, websocket=None) -> None:
    """
    Handle WebSocket errors gracefully.
    Logs error and optionally sends error event to client.
    
    Args:
        user_id: User ID of the connection
        error: Exception that occurred
        websocket: WebSocket connection (optional, for sending error event)
    """
    log_messaging_error(error, "websocket", user_id=user_id)
    
    if websocket:
        try:
            import json
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "An error occurred. Please reconnect.",
                "code": "WEBSOCKET_ERROR"
            }))
        except Exception:
            pass  # Connection may already be closed
