"""
Tip Schemas
Task 5.2: Tipping System
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ================== REQUEST SCHEMAS ==================

class TipSendRequest(BaseModel):
    """Send tip request"""
    to_user_id: str = Field(..., description="User ID to tip")
    amount: float = Field(..., ge=1.0, le=10000.0, description="Tip amount ($1-$10000)")
    currency: str = Field("USD", description="Currency code")
    
    # Optional context
    track_id: Optional[str] = Field(None, description="Tip for specific track")
    campaign_id: Optional[str] = Field(None, description="Tip for specific campaign")
    message: Optional[str] = Field(None, max_length=500, description="Message to creator")
    
    # Privacy
    is_anonymous: bool = Field(False, description="Hide your name from creator")
    
    # Payment (for now, we'll simulate - real payment in Task 5.1)
    payment_method: str = Field("card", description="Payment method")


class WithdrawalRequest(BaseModel):
    """Request withdrawal"""
    amount: float = Field(..., ge=10.0, description="Amount to withdraw (minimum $10)")
    withdrawal_method: str = Field(..., description="bank_transfer, paypal, stripe, paystack")
    account_details: str = Field(..., description="Account details (encrypted in production)")
    notes: Optional[str] = Field(None, description="Additional notes")


# ================== RESPONSE SCHEMAS ==================

class TipResponse(BaseModel):
    """Tip response"""
    id: str
    from_user_id: str
    to_user_id: str
    amount: float
    currency: str
    
    # Context
    track_id: Optional[str]
    campaign_id: Optional[str]
    message: Optional[str]
    
    # Privacy
    is_anonymous: bool
    
    # Payment
    payment_status: str
    platform_fee: float
    net_amount: float
    
    # Status
    status: str
    
    # Timestamps
    created_at: datetime
    paid_at: Optional[datetime]
    
    # Display fields
    from_user_name: Optional[str] = Field(None, description="Null if anonymous")
    to_user_name: str
    track_title: Optional[str] = None
    
    class Config:
        from_attributes = True


class TipListResponse(BaseModel):
    """List of tips"""
    tips: List[TipResponse]
    total: int
    total_amount: float
    page: int
    page_size: int


class TipStatsResponse(BaseModel):
    """Tip statistics"""
    total_received: float
    total_sent: float
    tips_received_count: int
    tips_sent_count: int
    
    # Top supporters
    top_supporters: List[dict] = Field(..., description="Top 5 supporters")
    
    # Recent tips
    recent_tips: List[TipResponse]


class UserBalanceResponse(BaseModel):
    """User balance"""
    user_id: str
    available_balance: float
    pending_balance: float
    total_earned: float
    total_withdrawn: float
    currency: str
    
    # Calculated
    withdrawable_amount: float = Field(..., description="Amount that can be withdrawn")
    
    class Config:
        from_attributes = True


class WithdrawalResponse(BaseModel):
    """Withdrawal response"""
    id: str
    user_id: str
    amount: float
    currency: str
    withdrawal_method: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime]
    rejection_reason: Optional[str]
    
    class Config:
        from_attributes = True


class WithdrawalListResponse(BaseModel):
    """List of withdrawals"""
    withdrawals: List[WithdrawalResponse]
    total: int
    page: int
    page_size: int


class TipLeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: str
    username: str
    total_tipped: float
    tip_count: int
    is_anonymous: bool = False


class TipLeaderboardResponse(BaseModel):
    """Tip leaderboard"""
    creator_id: str
    creator_name: str
    period: str = Field(..., description="all_time, this_month, this_week")
    top_supporters: List[TipLeaderboardEntry]
    total_tips: float
    total_supporters: int


class MessageResponse(BaseModel):
    """Generic message"""
    message: str
    data: Optional[dict] = None
