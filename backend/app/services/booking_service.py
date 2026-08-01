"""
Booking Service
Task 5.3: Booking System

Handles booking creation, management, contracts, and payments
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from app.models.booking import Booking, BookingAvailability, BookingMessage, BookingStatus, EventType, PaymentStatus
from app.models.user import User
from app.schemas.booking import (
    BookingCreateRequest,
    BookingUpdateRequest,
    BookingRatingRequest,
    BookingCancellationRequest,
    BookingMessageRequest,
    AvailabilityCreateRequest,
    AvailabilityUpdateRequest,
)


class BookingService:
    """Service for booking management"""
    
    # Platform commission percentage (12.5%)
    PLATFORM_COMMISSION_RATE = 0.125
    
    # Minimum booking amount
    MIN_BOOKING_AMOUNT = 50.0
    
    # Cancellation fee percentage (25% if cancelled < 48 hours before event)
    CANCELLATION_FEE_RATE = 0.25
    
    @staticmethod
    def create_booking(db: Session, client_user_id: str, request: BookingCreateRequest) -> Booking:
        """Create a new booking request"""
        
        # Verify artist exists
        artist = db.query(User).filter(User.id == request.artist_user_id).first()
        if not artist:
            raise ValueError("Artist not found")
        
        # Can't book yourself
        if client_user_id == request.artist_user_id:
            raise ValueError("Cannot book yourself")
        
        # Verify event date is in the future
        if request.event_date <= datetime.utcnow():
            raise ValueError("Event date must be in the future")
        
        # Check minimum amount
        if request.budget < BookingService.MIN_BOOKING_AMOUNT:
            raise ValueError(f"Minimum booking amount is ${BookingService.MIN_BOOKING_AMOUNT}")
        
        # Calculate platform commission and artist payout
        platform_commission = request.budget * BookingService.PLATFORM_COMMISSION_RATE
        artist_payout = request.budget - platform_commission
        
        # Create booking
        booking = Booking(
            id=str(uuid.uuid4()),
            client_user_id=client_user_id,
            artist_user_id=request.artist_user_id,
            event_name=request.event_name,
            event_type=request.event_type,
            event_date=request.event_date,
            event_duration=request.event_duration,
            location=request.location,
            venue_name=request.venue_name,
            budget=request.budget,
            currency=request.currency,
            deposit_amount=0.0,
            platform_commission_rate=BookingService.PLATFORM_COMMISSION_RATE,
            platform_commission=platform_commission,
            artist_payout=artist_payout,
            description=request.description,
            special_requirements=request.special_requirements,
            status=BookingStatus.PENDING.value,
            payment_status=PaymentStatus.PENDING.value,
            payment_held=False,
        )
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        return booking
    
    @staticmethod
    def get_booking(db: Session, booking_id: str, user_id: str) -> Optional[Booking]:
        """Get booking by ID (must be client or artist)"""
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            or_(
                Booking.client_user_id == user_id,
                Booking.artist_user_id == user_id
            )
        ).first()
        
        return booking
    
    @staticmethod
    def get_user_bookings(
        db: Session,
        user_id: str,
        as_role: str = "both",  # "client", "artist", or "both"
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Booking], int]:
        """Get bookings for a user"""
        
        query = db.query(Booking)
        
        # Filter by role
        if as_role == "client":
            query = query.filter(Booking.client_user_id == user_id)
        elif as_role == "artist":
            query = query.filter(Booking.artist_user_id == user_id)
        else:  # both
            query = query.filter(
                or_(
                    Booking.client_user_id == user_id,
                    Booking.artist_user_id == user_id
                )
            )
        
        # Filter by status
        if status:
            query = query.filter(Booking.status == status)
        
        total = query.count()
        bookings = query.order_by(desc(Booking.created_at)).offset(skip).limit(limit).all()
        
        return bookings, total
    
    @staticmethod
    def update_booking(
        db: Session,
        booking_id: str,
        client_user_id: str,
        request: BookingUpdateRequest
    ) -> Booking:
        """Update booking (only by client and only if pending)"""
        
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.client_user_id == client_user_id
        ).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        if booking.status != BookingStatus.PENDING.value:
            raise ValueError("Can only update pending bookings")
        
        # Update fields
        if request.event_name:
            booking.event_name = request.event_name
        if request.event_date:
            if request.event_date <= datetime.utcnow():
                raise ValueError("Event date must be in the future")
            booking.event_date = request.event_date
        if request.event_duration is not None:
            booking.event_duration = request.event_duration
        if request.location:
            booking.location = request.location
        if request.venue_name is not None:
            booking.venue_name = request.venue_name
        if request.budget:
            if request.budget < BookingService.MIN_BOOKING_AMOUNT:
                raise ValueError(f"Minimum booking amount is ${BookingService.MIN_BOOKING_AMOUNT}")
            
            # Recalculate commission and payout
            booking.budget = request.budget
            booking.platform_commission = request.budget * BookingService.PLATFORM_COMMISSION_RATE
            booking.artist_payout = request.budget - booking.platform_commission
        if request.description is not None:
            booking.description = request.description
        if request.special_requirements is not None:
            booking.special_requirements = request.special_requirements
        
        booking.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(booking)
        
        return booking
    
    @staticmethod
    def accept_booking(db: Session, booking_id: str, artist_user_id: str) -> Booking:
        """Accept booking request"""
        
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.artist_user_id == artist_user_id
        ).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        if booking.status != BookingStatus.PENDING.value:
            raise ValueError("Booking is not pending")
        
        booking.status = BookingStatus.ACCEPTED.value
        booking.accepted_at = datetime.utcnow()
        booking.updated_at = datetime.utcnow()
        
        # In production, this would initiate escrow payment
        # For now, mark as held
        booking.payment_status = PaymentStatus.HELD.value
        booking.payment_held = True
        
        db.commit()
        db.refresh(booking)
        
        return booking
    
    @staticmethod
    def decline_booking(db: Session, booking_id: str, artist_user_id: str, reason: Optional[str] = None) -> Booking:
        """Decline booking request"""
        
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.artist_user_id == artist_user_id
        ).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        if booking.status != BookingStatus.PENDING.value:
            raise ValueError("Booking is not pending")
        
        booking.status = BookingStatus.DECLINED.value
        booking.declined_at = datetime.utcnow()
        booking.updated_at = datetime.utcnow()
        
        if reason:
            booking.cancellation_reason = reason
        
        db.commit()
        db.refresh(booking)
        
        return booking
    
    @staticmethod
    def complete_booking(
        db: Session,
        booking_id: str,
        user_id: str,
        rating_request: Optional[BookingRatingRequest] = None
    ) -> Booking:
        """Mark booking as completed (by client or artist)"""
        
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            or_(
                Booking.client_user_id == user_id,
                Booking.artist_user_id == user_id
            )
        ).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        if booking.status != BookingStatus.ACCEPTED.value:
            raise ValueError("Booking is not accepted")
        
        # Check if event has passed
        if booking.event_date > datetime.utcnow():
            raise ValueError("Cannot complete booking before event date")
        
        booking.status = BookingStatus.COMPLETED.value
        booking.completed_at = datetime.utcnow()
        booking.updated_at = datetime.utcnow()
        
        # Release payment from escrow
        if booking.payment_held:
            booking.payment_status = PaymentStatus.RELEASED.value
            booking.payment_held = False
        
        # Add rating if provided
        if rating_request:
            booking.rating = rating_request.rating
            booking.review = rating_request.review
        
        db.commit()
        db.refresh(booking)
        
        return booking
    
    @staticmethod
    def cancel_booking(
        db: Session,
        booking_id: str,
        user_id: str,
        request: BookingCancellationRequest
    ) -> Booking:
        """Cancel booking"""
        
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            or_(
                Booking.client_user_id == user_id,
                Booking.artist_user_id == user_id
            )
        ).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        if booking.status not in [BookingStatus.PENDING.value, BookingStatus.ACCEPTED.value]:
            raise ValueError("Booking cannot be cancelled")
        
        booking.status = BookingStatus.CANCELLED.value
        booking.cancelled_by = user_id
        booking.cancellation_reason = request.cancellation_reason
        booking.updated_at = datetime.utcnow()
        
        # Calculate cancellation fee if within 48 hours
        hours_until_event = (booking.event_date - datetime.utcnow()).total_seconds() / 3600
        
        if hours_until_event < 48 and booking.status == BookingStatus.ACCEPTED.value:
            booking.cancellation_fee = booking.budget * BookingService.CANCELLATION_FEE_RATE
        
        # Refund payment if held
        if booking.payment_held:
            booking.payment_status = PaymentStatus.REFUNDED.value
            booking.payment_held = False
        
        db.commit()
        db.refresh(booking)
        
        return booking
    
    @staticmethod
    def get_booking_stats(db: Session, user_id: str) -> Dict[str, Any]:
        """Get booking statistics for user"""
        
        # As client
        client_stats = db.query(
            func.count(Booking.id),
            func.sum(Booking.budget)
        ).filter(
            Booking.client_user_id == user_id
        ).first()
        
        total_bookings_made = client_stats[0] or 0
        total_spent = float(client_stats[1] or 0)
        
        pending_bookings = db.query(func.count(Booking.id)).filter(
            Booking.client_user_id == user_id,
            Booking.status == BookingStatus.PENDING.value
        ).scalar() or 0
        
        completed_bookings_client = db.query(func.count(Booking.id)).filter(
            Booking.client_user_id == user_id,
            Booking.status == BookingStatus.COMPLETED.value
        ).scalar() or 0
        
        # As artist
        artist_stats = db.query(
            func.count(Booking.id),
            func.sum(Booking.artist_payout)
        ).filter(
            Booking.artist_user_id == user_id
        ).first()
        
        total_bookings_received = artist_stats[0] or 0
        total_earned = float(artist_stats[1] or 0)
        
        pending_requests = db.query(func.count(Booking.id)).filter(
            Booking.artist_user_id == user_id,
            Booking.status == BookingStatus.PENDING.value
        ).scalar() or 0
        
        upcoming_events = db.query(func.count(Booking.id)).filter(
            Booking.artist_user_id == user_id,
            Booking.status == BookingStatus.ACCEPTED.value,
            Booking.event_date >= datetime.utcnow()
        ).scalar() or 0
        
        completed_events = db.query(func.count(Booking.id)).filter(
            Booking.artist_user_id == user_id,
            Booking.status == BookingStatus.COMPLETED.value
        ).scalar() or 0
        
        # Recent bookings
        recent_bookings = db.query(Booking).filter(
            or_(
                Booking.client_user_id == user_id,
                Booking.artist_user_id == user_id
            )
        ).order_by(desc(Booking.created_at)).limit(5).all()
        
        return {
            "total_bookings_made": total_bookings_made,
            "total_spent": total_spent,
            "pending_bookings": pending_bookings,
            "completed_bookings": completed_bookings_client,
            "total_bookings_received": total_bookings_received,
            "total_earned": total_earned,
            "pending_requests": pending_requests,
            "upcoming_events": upcoming_events,
            "completed_events": completed_events,
            "recent_bookings": recent_bookings,
        }
    
    # ================== AVAILABILITY ==================
    
    @staticmethod
    def set_availability(
        db: Session,
        user_id: str,
        request: AvailabilityCreateRequest
    ) -> BookingAvailability:
        """Set availability for a date"""
        
        # Check if availability already exists for this date
        existing = db.query(BookingAvailability).filter(
            BookingAvailability.user_id == user_id,
            func.date(BookingAvailability.date) == request.date.date()
        ).first()
        
        if existing:
            # Update existing
            existing.is_available = request.is_available
            existing.base_rate = request.base_rate
            existing.notes = request.notes
            existing.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new
        availability = BookingAvailability(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=request.date,
            is_available=request.is_available,
            base_rate=request.base_rate,
            notes=request.notes,
        )
        
        db.add(availability)
        db.commit()
        db.refresh(availability)
        
        return availability
    
    @staticmethod
    def get_availability(
        db: Session,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[BookingAvailability]:
        """Get availability for a user"""
        
        query = db.query(BookingAvailability).filter(
            BookingAvailability.user_id == user_id
        )
        
        if start_date:
            query = query.filter(BookingAvailability.date >= start_date)
        if end_date:
            query = query.filter(BookingAvailability.date <= end_date)
        
        return query.order_by(BookingAvailability.date).all()
    
    # ================== MESSAGES ==================
    
    @staticmethod
    def send_message(
        db: Session,
        booking_id: str,
        sender_user_id: str,
        request: BookingMessageRequest
    ) -> BookingMessage:
        """Send message for a booking"""
        
        # Verify booking exists and user is involved
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            or_(
                Booking.client_user_id == sender_user_id,
                Booking.artist_user_id == sender_user_id
            )
        ).first()
        
        if not booking:
            raise ValueError("Booking not found or you're not authorized")
        
        message = BookingMessage(
            id=str(uuid.uuid4()),
            booking_id=booking_id,
            sender_user_id=sender_user_id,
            message=request.message,
            attachment_url=request.attachment_url,
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return message
    
    @staticmethod
    def get_messages(
        db: Session,
        booking_id: str,
        user_id: str
    ) -> Tuple[List[BookingMessage], int]:
        """Get messages for a booking"""
        
        # Verify user is involved in booking
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            or_(
                Booking.client_user_id == user_id,
                Booking.artist_user_id == user_id
            )
        ).first()
        
        if not booking:
            raise ValueError("Booking not found or you're not authorized")
        
        messages = db.query(BookingMessage).filter(
            BookingMessage.booking_id == booking_id
        ).order_by(BookingMessage.created_at).all()
        
        # Count unread messages (messages not sent by current user and not read)
        unread_count = db.query(func.count(BookingMessage.id)).filter(
            BookingMessage.booking_id == booking_id,
            BookingMessage.sender_user_id != user_id,
            BookingMessage.is_read == False
        ).scalar() or 0
        
        return messages, unread_count
    
    @staticmethod
    def mark_messages_read(db: Session, booking_id: str, user_id: str) -> int:
        """Mark all messages as read for a booking"""
        
        # Verify user is involved in booking
        booking = db.query(Booking).filter(
            Booking.id == booking_id,
            or_(
                Booking.client_user_id == user_id,
                Booking.artist_user_id == user_id
            )
        ).first()
        
        if not booking:
            raise ValueError("Booking not found or you're not authorized")
        
        # Mark messages not sent by current user as read
        updated = db.query(BookingMessage).filter(
            BookingMessage.booking_id == booking_id,
            BookingMessage.sender_user_id != user_id,
            BookingMessage.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        db.commit()
        
        return updated
    
    # ================== CONTRACT & INVOICE ==================
    
    @staticmethod
    def generate_contract(db: Session, booking_id: str) -> Dict[str, Any]:
        """Generate contract for booking"""
        
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        # Get client and artist info
        client = db.query(User).filter(User.id == booking.client_user_id).first()
        artist = db.query(User).filter(User.id == booking.artist_user_id).first()
        
        # Generate contract text (simplified)
        contract_text = f"""
BOOKING CONTRACT

Contract ID: {booking_id}
Date: {datetime.utcnow().strftime('%B %d, %Y')}

PARTIES:
Client: {client.full_name or client.username} ({client.email})
Artist: {artist.full_name or artist.username} ({artist.email})

EVENT DETAILS:
Event Name: {booking.event_name}
Event Type: {booking.event_type}
Event Date: {booking.event_date.strftime('%B %d, %Y at %I:%M %p')}
Duration: {booking.event_duration or 'TBD'} minutes
Location: {booking.location}
Venue: {booking.venue_name or 'TBD'}

FINANCIAL TERMS:
Total Budget: {booking.currency} {booking.budget:.2f}
Platform Commission ({booking.platform_commission_rate * 100}%): {booking.currency} {booking.platform_commission:.2f}
Artist Payout: {booking.currency} {booking.artist_payout:.2f}

DESCRIPTION:
{booking.description or 'N/A'}

SPECIAL REQUIREMENTS:
{booking.special_requirements or 'None'}

TERMS AND CONDITIONS:
1. Payment will be held in escrow until event completion
2. Cancellation within 48 hours incurs a {BookingService.CANCELLATION_FEE_RATE * 100}% fee
3. Both parties agree to the terms above
4. Payment released upon event completion confirmation

Managed by BeatPush Platform
"""
        
        # In production, generate PDF and upload to storage
        # For now, return text
        return {
            "booking_id": booking_id,
            "contract_text": contract_text,
            "contract_url": None,  # Would be storage URL
            "generated_at": datetime.utcnow(),
        }
    
    @staticmethod
    def generate_invoice(db: Session, booking_id: str) -> Dict[str, Any]:
        """Generate invoice for booking"""
        
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        
        if not booking:
            raise ValueError("Booking not found")
        
        # Generate invoice number
        invoice_number = f"INV-{booking.id[:8].upper()}-{datetime.utcnow().strftime('%Y%m%d')}"
        
        # In production, generate PDF and upload
        # For now, return data
        return {
            "booking_id": booking_id,
            "invoice_number": invoice_number,
            "invoice_url": None,  # Would be storage URL
            "amount": booking.budget,
            "currency": booking.currency,
            "generated_at": datetime.utcnow(),
        }
