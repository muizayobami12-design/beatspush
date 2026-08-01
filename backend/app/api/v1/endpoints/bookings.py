"""
Bookings API Endpoints
Task 5.3: Booking System

Endpoints for managing bookings, availability, and communications
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.booking_service import BookingService
from app.schemas.booking import (
    BookingCreateRequest,
    BookingUpdateRequest,
    BookingRatingRequest,
    BookingCancellationRequest,
    BookingMessageRequest,
    AvailabilityCreateRequest,
    AvailabilityUpdateRequest,
    BookingResponse,
    BookingListResponse,
    BookingStatsResponse,
    AvailabilityResponse,
    AvailabilityListResponse,
    BookingMessageResponse,
    BookingMessageListResponse,
    ContractResponse,
    InvoiceResponse,
    MessageResponse,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# ================== CREATE & MANAGE BOOKINGS ==================

@router.post("/create", response_model=BookingResponse, status_code=201)
def create_booking(
    request: BookingCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a booking request.
    
    **Requirements:**
    - Minimum budget: $50
    - Event date must be in the future
    - Cannot book yourself
    
    **Process:**
    1. Client sends booking request
    2. Artist receives notification
    3. Artist can accept or decline
    4. Upon acceptance, payment held in escrow (simulated)
    5. After event, payment released to artist
    
    **Platform Fee:**
    - Commission: 12.5% of booking amount
    - Example: $1000 booking = $125 commission, $875 to artist
    
    **Returns:** Booking confirmation with details
    """
    try:
        booking = BookingService.create_booking(db, current_user.id, request)
        
        # Build response
        client = db.query(User).filter(User.id == booking.client_user_id).first()
        artist = db.query(User).filter(User.id == booking.artist_user_id).first()
        
        response = BookingResponse(
            **booking.__dict__,
            client_name=client.username or client.full_name,
            artist_name=artist.username or artist.full_name,
        )
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")


@router.get("/list", response_model=BookingListResponse)
def list_bookings(
    as_role: str = Query("both", description="client, artist, or both"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bookings for current user.
    
    **Parameters:**
    - `as_role`: View as client, artist, or both
    - `status`: Filter by status (pending, accepted, declined, completed, cancelled)
    - `page`: Page number
    - `page_size`: Items per page
    
    **Returns:**
    - List of bookings
    - Total count
    - Pagination info
    
    **Use this for:**
    - Viewing sent booking requests (as_role=client)
    - Viewing received booking requests (as_role=artist)
    - Dashboard overviews
    """
    skip = (page - 1) * page_size
    
    bookings, total = BookingService.get_user_bookings(
        db, current_user.id, as_role, status, skip, page_size
    )
    
    # Build responses
    booking_responses = []
    for booking in bookings:
        client = db.query(User).filter(User.id == booking.client_user_id).first()
        artist = db.query(User).filter(User.id == booking.artist_user_id).first()
        
        booking_responses.append(BookingResponse(
            **booking.__dict__,
            client_name=client.username or client.full_name if client else "Unknown",
            artist_name=artist.username or artist.full_name if artist else "Unknown",
        ))
    
    return BookingListResponse(
        bookings=booking_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get booking details.
    
    **Authorization:** Must be the client or artist of the booking
    
    **Returns:** Complete booking information including:
    - Event details
    - Financial breakdown
    - Status and timeline
    - Contract and payment info
    """
    booking = BookingService.get_booking(db, booking_id, current_user.id)
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Build response
    client = db.query(User).filter(User.id == booking.client_user_id).first()
    artist = db.query(User).filter(User.id == booking.artist_user_id).first()
    
    return BookingResponse(
        **booking.__dict__,
        client_name=client.username or client.full_name if client else "Unknown",
        artist_name=artist.username or artist.full_name if artist else "Unknown",
    )


@router.put("/{booking_id}/update", response_model=BookingResponse)
def update_booking(
    booking_id: str,
    request: BookingUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update booking details (client only, pending bookings only).
    
    **Authorization:** Must be the client who created the booking
    
    **Restrictions:**
    - Can only update pending bookings
    - Cannot update after artist accepts
    
    **Updatable Fields:**
    - Event details (name, date, location, venue)
    - Budget (commission recalculated automatically)
    - Description and requirements
    
    **Returns:** Updated booking
    """
    try:
        booking = BookingService.update_booking(db, booking_id, current_user.id, request)
        
        # Build response
        client = db.query(User).filter(User.id == booking.client_user_id).first()
        artist = db.query(User).filter(User.id == booking.artist_user_id).first()
        
        return BookingResponse(
            **booking.__dict__,
            client_name=client.username or client.full_name,
            artist_name=artist.username or artist.full_name,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update booking: {str(e)}")


@router.post("/{booking_id}/accept", response_model=BookingResponse)
def accept_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accept a booking request (artist only).
    
    **Authorization:** Must be the artist who received the booking
    
    **Effect:**
    - Status changes to 'accepted'
    - Payment held in escrow (simulated)
    - Contract can now be generated
    - Client notified
    
    **Returns:** Updated booking
    """
    try:
        booking = BookingService.accept_booking(db, booking_id, current_user.id)
        
        # Build response
        client = db.query(User).filter(User.id == booking.client_user_id).first()
        artist = db.query(User).filter(User.id == booking.artist_user_id).first()
        
        return BookingResponse(
            **booking.__dict__,
            client_name=client.username or client.full_name,
            artist_name=artist.username or artist.full_name,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to accept booking: {str(e)}")


@router.post("/{booking_id}/decline", response_model=BookingResponse)
def decline_booking(
    booking_id: str,
    reason: Optional[str] = Query(None, description="Optional reason for declining"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Decline a booking request (artist only).
    
    **Authorization:** Must be the artist who received the booking
    
    **Optional:** Provide reason for declining
    
    **Effect:**
    - Status changes to 'declined'
    - No payment held
    - Client notified
    
    **Returns:** Updated booking
    """
    try:
        booking = BookingService.decline_booking(db, booking_id, current_user.id, reason)
        
        # Build response
        client = db.query(User).filter(User.id == booking.client_user_id).first()
        artist = db.query(User).filter(User.id == booking.artist_user_id).first()
        
        return BookingResponse(
            **booking.__dict__,
            client_name=client.username or client.full_name,
            artist_name=artist.username or artist.full_name,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decline booking: {str(e)}")


@router.post("/{booking_id}/complete", response_model=BookingResponse)
def complete_booking(
    booking_id: str,
    rating: Optional[BookingRatingRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark booking as completed.
    
    **Authorization:** Must be client or artist involved in booking
    
    **Requirements:**
    - Event date must have passed
    - Booking must be in 'accepted' status
    
    **Effect:**
    - Status changes to 'completed'
    - Payment released from escrow to artist
    - Optional: Client can rate the artist
    
    **Returns:** Updated booking
    """
    try:
        booking = BookingService.complete_booking(db, booking_id, current_user.id, rating)
        
        # Build response
        client = db.query(User).filter(User.id == booking.client_user_id).first()
        artist = db.query(User).filter(User.id == booking.artist_user_id).first()
        
        return BookingResponse(
            **booking.__dict__,
            client_name=client.username or client.full_name,
            artist_name=artist.username or artist.full_name,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete booking: {str(e)}")


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: str,
    request: BookingCancellationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a booking.
    
    **Authorization:** Must be client or artist involved in booking
    
    **Cancellation Fees:**
    - More than 48 hours before event: No fee
    - Less than 48 hours before event: 25% cancellation fee
    
    **Effect:**
    - Status changes to 'cancelled'
    - Payment refunded (minus cancellation fee if applicable)
    - Reason recorded
    
    **Returns:** Updated booking with cancellation details
    """
    try:
        booking = BookingService.cancel_booking(db, booking_id, current_user.id, request)
        
        # Build response
        client = db.query(User).filter(User.id == booking.client_user_id).first()
        artist = db.query(User).filter(User.id == booking.artist_user_id).first()
        
        return BookingResponse(
            **booking.__dict__,
            client_name=client.username or client.full_name,
            artist_name=artist.username or artist.full_name,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel booking: {str(e)}")


@router.get("/stats/summary", response_model=BookingStatsResponse)
def get_booking_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get booking statistics for current user.
    
    **Returns:**
    - As Client: Total bookings made, spent, pending, completed
    - As Artist: Total bookings received, earned, pending requests, upcoming/completed events
    - Recent bookings (last 5)
    
    **Use this for:**
    - Dashboard overview
    - Earnings tracking
    - Performance metrics
    """
    stats = BookingService.get_booking_stats(db, current_user.id)
    
    # Format recent bookings
    recent_booking_responses = []
    for booking in stats["recent_bookings"]:
        client = db.query(User).filter(User.id == booking.client_user_id).first()
        artist = db.query(User).filter(User.id == booking.artist_user_id).first()
        
        recent_booking_responses.append(BookingResponse(
            **booking.__dict__,
            client_name=client.username or client.full_name if client else "Unknown",
            artist_name=artist.username or artist.full_name if artist else "Unknown",
        ))
    
    return BookingStatsResponse(
        total_bookings_made=stats["total_bookings_made"],
        total_spent=stats["total_spent"],
        pending_bookings=stats["pending_bookings"],
        completed_bookings=stats["completed_bookings"],
        total_bookings_received=stats["total_bookings_received"],
        total_earned=stats["total_earned"],
        pending_requests=stats["pending_requests"],
        upcoming_events=stats["upcoming_events"],
        completed_events=stats["completed_events"],
        recent_bookings=recent_booking_responses,
    )


# ================== AVAILABILITY ==================

@router.post("/availability/set", response_model=AvailabilityResponse, status_code=201)
def set_availability(
    request: AvailabilityCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set availability for a date (artist only).
    
    **Use this to:**
    - Mark dates as available/unavailable
    - Set base rates for specific dates
    - Add notes about availability
    
    **Features:**
    - If date already has availability, it will be updated
    - Can set different rates for different dates
    - Notes can include requirements or preferences
    
    **Returns:** Availability slot
    """
    try:
        availability = BookingService.set_availability(db, current_user.id, request)
        return AvailabilityResponse(**availability.__dict__)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set availability: {str(e)}")


@router.get("/availability/{user_id}", response_model=AvailabilityListResponse)
def get_availability(
    user_id: str,
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db)
):
    """
    **PUBLIC ENDPOINT** - Get availability for an artist.
    
    **Parameters:**
    - `user_id`: Artist user ID
    - `start_date`: Optional start date filter
    - `end_date`: Optional end date filter
    
    **Returns:**
    - List of availability slots
    - Shows which dates are available
    - Base rates if set
    
    **Use this for:**
    - Checking artist availability before booking
    - Calendar displays
    - Rate information
    """
    try:
        availabilities = BookingService.get_availability(db, user_id, start_date, end_date)
        
        availability_responses = [
            AvailabilityResponse(**avail.__dict__)
            for avail in availabilities
        ]
        
        return AvailabilityListResponse(
            availabilities=availability_responses,
            total=len(availability_responses),
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get availability: {str(e)}")


# ================== MESSAGES ==================

@router.post("/{booking_id}/messages/send", response_model=BookingMessageResponse, status_code=201)
def send_message(
    booking_id: str,
    request: BookingMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message for a booking.
    
    **Authorization:** Must be client or artist involved in booking
    
    **Features:**
    - Send text messages
    - Optional file attachments
    - Real-time communication
    
    **Use this for:**
    - Discussing event details
    - Asking questions
    - Sharing requirements
    - Coordinating logistics
    
    **Returns:** Message confirmation
    """
    try:
        message = BookingService.send_message(db, booking_id, current_user.id, request)
        
        # Get sender info
        sender = db.query(User).filter(User.id == message.sender_user_id).first()
        
        return BookingMessageResponse(
            **message.__dict__,
            sender_name=sender.username or sender.full_name if sender else "Unknown",
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/{booking_id}/messages", response_model=BookingMessageListResponse)
def get_messages(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get messages for a booking.
    
    **Authorization:** Must be client or artist involved in booking
    
    **Returns:**
    - All messages for the booking (chronological order)
    - Unread message count
    
    **Use this for:**
    - Viewing conversation history
    - Checking for new messages
    - Message threads
    """
    try:
        messages, unread_count = BookingService.get_messages(db, booking_id, current_user.id)
        
        # Build responses
        message_responses = []
        for msg in messages:
            sender = db.query(User).filter(User.id == msg.sender_user_id).first()
            
            message_responses.append(BookingMessageResponse(
                **msg.__dict__,
                sender_name=sender.username or sender.full_name if sender else "Unknown",
            ))
        
        return BookingMessageListResponse(
            messages=message_responses,
            total=len(message_responses),
            unread_count=unread_count,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.post("/{booking_id}/messages/mark-read", response_model=MessageResponse)
def mark_messages_read(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all messages as read for a booking.
    
    **Authorization:** Must be client or artist involved in booking
    
    **Effect:**
    - Marks all messages sent by the other party as read
    - Updates read timestamps
    
    **Returns:** Count of messages marked as read
    """
    try:
        count = BookingService.mark_messages_read(db, booking_id, current_user.id)
        
        return MessageResponse(
            message=f"Marked {count} messages as read",
            data={"count": count}
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark messages as read: {str(e)}")


# ================== CONTRACT & INVOICE ==================

@router.get("/{booking_id}/contract", response_model=ContractResponse)
def generate_contract(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate contract for a booking.
    
    **Authorization:** Must be client or artist involved in booking
    
    **Returns:**
    - Contract text with all terms
    - Contract URL (PDF in production)
    
    **Contract Includes:**
    - Party information
    - Event details
    - Financial terms
    - Cancellation policy
    - Platform terms
    
    **Note:** In production, this generates a PDF and stores it
    """
    try:
        # Verify user is involved
        booking = BookingService.get_booking(db, booking_id, current_user.id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        contract = BookingService.generate_contract(db, booking_id)
        return ContractResponse(**contract)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate contract: {str(e)}")


@router.get("/{booking_id}/invoice", response_model=InvoiceResponse)
def generate_invoice(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate invoice for a booking.
    
    **Authorization:** Must be client or artist involved in booking
    
    **Returns:**
    - Invoice number
    - Invoice URL (PDF in production)
    - Amount and currency
    
    **Use this for:**
    - Payment records
    - Accounting
    - Tax purposes
    
    **Note:** In production, this generates a PDF invoice and stores it
    """
    try:
        # Verify user is involved
        booking = BookingService.get_booking(db, booking_id, current_user.id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        invoice = BookingService.generate_invoice(db, booking_id)
        return InvoiceResponse(**invoice)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate invoice: {str(e)}")
