"""
Booking Schemas
Task 5.3: Booking System
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ================== REQUEST SCHEMAS ==================

class BookingCreateRequest(BaseModel):
    """Create booking request"""
    artist_user_id: str = Field(..., description="Artist/DJ/Producer to book")
    
    # Event details
    event_name: str = Field(..., max_length=255, description="Event name")
    event_type: str = Field(..., description="club, festival, private_event, radio_show, etc.")
    event_date: datetime = Field(..., description="Event date and time")
    event_duration: Optional[int] = Field(None, description="Duration in minutes")
    location: str = Field(..., max_length=500, description="Event location")
    venue_name: Optional[str] = Field(None, max_length=255, description="Venue name")
    
    # Financial
    budget: float = Field(..., ge=50.0, description="Budget/offer amount (minimum $50)")
    currency: str = Field("USD", description="Currency code")
    
    # Details
    description: Optional[str] = Field(None, description="Event description and expectations")
    special_requirements: Optional[str] = Field(None, description="Special requirements (equipment, etc.)")


class BookingUpdateRequest(BaseModel):
    """Update booking details"""
    event_name: Optional[str] = Field(None, max_length=255)
    event_date: Optional[datetime] = None
    event_duration: Optional[int] = None
    location: Optional[str] = Field(None, max_length=500)
    venue_name: Optional[str] = Field(None, max_length=255)
    budget: Optional[float] = Field(None, ge=50.0)
    description: Optional[str] = None
    special_requirements: Optional[str] = None


class BookingRatingRequest(BaseModel):
    """Rate a completed booking"""
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 stars")
    review: Optional[str] = Field(None, max_length=1000, description="Review text")


class BookingCancellationRequest(BaseModel):
    """Cancel a booking"""
    cancellation_reason: str = Field(..., max_length=1000, description="Reason for cancellation")


class BookingMessageRequest(BaseModel):
    """Send message for a booking"""
    message: str = Field(..., max_length=2000, description="Message text")
    attachment_url: Optional[str] = Field(None, description="Optional attachment URL")


class AvailabilityCreateRequest(BaseModel):
    """Set availability"""
    date: datetime = Field(..., description="Date to set availability for")
    is_available: bool = Field(True, description="Whether available on this date")
    base_rate: Optional[float] = Field(None, description="Base rate for this date")
    notes: Optional[str] = Field(None, description="Notes about availability")


class AvailabilityUpdateRequest(BaseModel):
    """Update availability"""
    is_available: Optional[bool] = None
    base_rate: Optional[float] = None
    notes: Optional[str] = None


# ================== RESPONSE SCHEMAS ==================

class BookingResponse(BaseModel):
    """Booking response"""
    id: str
    
    # Parties
    client_user_id: str
    artist_user_id: str
    client_name: Optional[str] = None
    artist_name: Optional[str] = None
    
    # Event details
    event_name: str
    event_type: str
    event_date: datetime
    event_duration: Optional[int]
    location: str
    venue_name: Optional[str]
    
    # Financial
    budget: float
    currency: str
    deposit_amount: float
    platform_commission_rate: float
    platform_commission: float
    artist_payout: float
    
    # Details
    description: Optional[str]
    special_requirements: Optional[str]
    
    # Status
    status: str
    
    # Contract & Payment
    contract_url: Optional[str]
    contract_signed: bool
    contract_signed_at: Optional[datetime]
    invoice_url: Optional[str]
    payment_status: str
    payment_held: bool
    
    # Completion
    completed_at: Optional[datetime]
    rating: Optional[int]
    review: Optional[str]
    
    # Cancellation
    cancelled_by: Optional[str]
    cancellation_reason: Optional[str]
    cancellation_fee: float
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    accepted_at: Optional[datetime]
    declined_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """List of bookings"""
    bookings: List[BookingResponse]
    total: int
    page: int
    page_size: int


class BookingStatsResponse(BaseModel):
    """Booking statistics"""
    # As client
    total_bookings_made: int
    total_spent: float
    pending_bookings: int
    completed_bookings: int
    
    # As artist
    total_bookings_received: int
    total_earned: float
    pending_requests: int
    upcoming_events: int
    completed_events: int
    
    # Recent
    recent_bookings: List[BookingResponse]


class AvailabilityResponse(BaseModel):
    """Availability response"""
    id: str
    user_id: str
    date: datetime
    is_available: bool
    base_rate: Optional[float]
    currency: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AvailabilityListResponse(BaseModel):
    """List of availability slots"""
    availabilities: List[AvailabilityResponse]
    total: int


class BookingMessageResponse(BaseModel):
    """Booking message response"""
    id: str
    booking_id: str
    sender_user_id: str
    sender_name: Optional[str] = None
    message: str
    attachment_url: Optional[str]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookingMessageListResponse(BaseModel):
    """List of booking messages"""
    messages: List[BookingMessageResponse]
    total: int
    unread_count: int


class ContractResponse(BaseModel):
    """Generated contract"""
    booking_id: str
    contract_text: str
    contract_url: Optional[str] = None
    generated_at: datetime


class InvoiceResponse(BaseModel):
    """Generated invoice"""
    booking_id: str
    invoice_number: str
    invoice_url: Optional[str] = None
    amount: float
    currency: str
    generated_at: datetime


class MessageResponse(BaseModel):
    """Generic message"""
    message: str
    data: Optional[dict] = None
