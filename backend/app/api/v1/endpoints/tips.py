"""
Tips API Endpoints
Task 5.2: Tipping System

Endpoints for sending/receiving tips and managing balance
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.tip_service import TipService
from app.schemas.tip import (
    TipSendRequest,
    TipResponse,
    TipListResponse,
    TipStatsResponse,
    UserBalanceResponse,
    WithdrawalRequest,
    WithdrawalResponse,
    WithdrawalListResponse,
    TipLeaderboardResponse,
    MessageResponse,
)

router = APIRouter(prefix="/tips", tags=["Tips"])


# ================== SEND/RECEIVE TIPS ==================

@router.post("/send", response_model=TipResponse, status_code=201)
def send_tip(
    request: TipSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a tip to another creator.
    
    **Requirements:**
    - Amount: $1 - $10,000
    - Recipient must exist
    - Cannot tip yourself
    
    **Features:**
    - Optional message to creator
    - Anonymous tipping option
    - Link tip to specific track or campaign
    
    **Fees:**
    - Platform fee: 2.5%
    - Payment processing: Simulated (will be real in Task 5.1)
    
    **Returns:** Tip confirmation with transaction details
    """
    try:
        tip = TipService.send_tip(db, current_user.id, request)
        
        # Build response
        from_user = db.query(User).filter(User.id == tip.from_user_id).first()
        to_user = db.query(User).filter(User.id == tip.to_user_id).first()
        
        track_title = None
        if tip.track_id:
            from app.models.track import Track
            track = db.query(Track).filter(Track.id == tip.track_id).first()
            track_title = track.title if track else None
        
        response = TipResponse(
            **tip.__dict__,
            from_user_name=None if tip.is_anonymous else (from_user.username or from_user.full_name),
            to_user_name=to_user.username or to_user.full_name,
            track_title=track_title,
        )
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send tip: {str(e)}")


@router.get("/received", response_model=TipListResponse)
def get_tips_received(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tips received by the current user.
    
    **Returns:**
    - List of tips received
    - Total amount received
    - Pagination info
    
    **Use this for:**
    - Viewing supporters
    - Tracking earnings
    - Thanking supporters
    """
    skip = (page - 1) * page_size
    
    tips, total, total_amount = TipService.get_tips_received(
        db, current_user.id, skip, page_size
    )
    
    # Build responses
    tip_responses = []
    for tip in tips:
        from_user = db.query(User).filter(User.id == tip.from_user_id).first()
        
        track_title = None
        if tip.track_id:
            from app.models.track import Track
            track = db.query(Track).filter(Track.id == tip.track_id).first()
            track_title = track.title if track else None
        
        tip_responses.append(TipResponse(
            **tip.__dict__,
            from_user_name=None if tip.is_anonymous else (from_user.username or from_user.full_name if from_user else "Unknown"),
            to_user_name=current_user.username or current_user.full_name,
            track_title=track_title,
        ))
    
    return TipListResponse(
        tips=tip_responses,
        total=total,
        total_amount=total_amount,
        page=page,
        page_size=page_size,
    )


@router.get("/sent", response_model=TipListResponse)
def get_tips_sent(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tips sent by the current user.
    
    **Returns:**
    - List of tips sent
    - Total amount sent
    - Pagination info
    
    **Use this for:**
    - Viewing support history
    - Tracking spending
    """
    skip = (page - 1) * page_size
    
    tips, total, total_amount = TipService.get_tips_sent(
        db, current_user.id, skip, page_size
    )
    
    # Build responses
    tip_responses = []
    for tip in tips:
        to_user = db.query(User).filter(User.id == tip.to_user_id).first()
        
        track_title = None
        if tip.track_id:
            from app.models.track import Track
            track = db.query(Track).filter(Track.id == tip.track_id).first()
            track_title = track.title if track else None
        
        tip_responses.append(TipResponse(
            **tip.__dict__,
            from_user_name=current_user.username or current_user.full_name,
            to_user_name=to_user.username or to_user.full_name if to_user else "Unknown",
            track_title=track_title,
        ))
    
    return TipListResponse(
        tips=tip_responses,
        total=total,
        total_amount=total_amount,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=TipStatsResponse)
def get_tip_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tip statistics for current user.
    
    **Returns:**
    - Total received/sent amounts
    - Tip counts
    - Top 5 supporters
    - Recent tips
    
    **Use this for:**
    - Dashboard overview
    - Supporter recognition
    - Performance tracking
    """
    stats = TipService.get_tip_stats(db, current_user.id)
    
    # Format recent tips
    recent_tip_responses = []
    for tip in stats["recent_tips"]:
        from_user = db.query(User).filter(User.id == tip.from_user_id).first()
        
        recent_tip_responses.append(TipResponse(
            **tip.__dict__,
            from_user_name=None if tip.is_anonymous else (from_user.username or from_user.full_name if from_user else "Unknown"),
            to_user_name=current_user.username or current_user.full_name,
        ))
    
    return TipStatsResponse(
        total_received=stats["total_received"],
        total_sent=stats["total_sent"],
        tips_received_count=stats["tips_received_count"],
        tips_sent_count=stats["tips_sent_count"],
        top_supporters=stats["top_supporters"],
        recent_tips=recent_tip_responses,
    )


# ================== BALANCE & WITHDRAWALS ==================

@router.get("/balance", response_model=UserBalanceResponse)
def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's tip balance.
    
    **Returns:**
    - Available balance (can be withdrawn)
    - Pending balance (withdrawal in progress)
    - Total earned (all-time)
    - Total withdrawn (all-time)
    - Withdrawable amount (available - pending)
    
    **Use this for:**
    - Balance display
    - Withdrawal eligibility check
    - Earnings tracking
    """
    balance_data = TipService.get_user_balance(db, current_user.id)
    return UserBalanceResponse(**balance_data)


@router.post("/withdraw", response_model=WithdrawalResponse, status_code=201)
def request_withdrawal(
    request: WithdrawalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request withdrawal of tips.
    
    **Requirements:**
    - Minimum amount: $10
    - Must have sufficient balance
    - Valid withdrawal method
    
    **Withdrawal Methods:**
    - bank_transfer
    - paypal
    - stripe
    - paystack (for African users)
    
    **Processing:**
    - Status starts as 'pending'
    - Admin reviews and processes
    - 2-5 business days for transfer
    
    **Returns:** Withdrawal request confirmation
    """
    try:
        withdrawal = TipService.request_withdrawal(db, current_user.id, request)
        return WithdrawalResponse(**withdrawal.__dict__)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to request withdrawal: {str(e)}")


@router.get("/withdrawals", response_model=WithdrawalListResponse)
def get_withdrawals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get withdrawal history.
    
    **Returns:**
    - List of withdrawal requests
    - Status for each (pending, processing, completed, rejected)
    - Processing dates
    
    **Statuses:**
    - pending: Awaiting review
    - processing: Being processed
    - completed: Funds transferred
    - rejected: Request denied (with reason)
    """
    skip = (page - 1) * page_size
    
    withdrawals, total = TipService.get_user_withdrawals(
        db, current_user.id, skip, page_size
    )
    
    withdrawal_responses = [WithdrawalResponse(**w.__dict__) for w in withdrawals]
    
    return WithdrawalListResponse(
        withdrawals=withdrawal_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


# ================== LEADERBOARD ==================

@router.get("/leaderboard/{creator_id}", response_model=TipLeaderboardResponse)
def get_tip_leaderboard(
    creator_id: str,
    period: str = Query("all_time", description="all_time, this_month, this_week"),
    limit: int = Query(10, ge=1, le=50, description="Number of supporters"),
    db: Session = Depends(get_db)
):
    """
    **PUBLIC ENDPOINT** - Get tip leaderboard for a creator.
    
    **Parameters:**
    - `period`: all_time, this_month, this_week
    - `limit`: Number of top supporters (1-50)
    
    **Returns:**
    - Top supporters ranked by total tipped
    - Total tips for the period
    - Total number of supporters
    
    **Privacy:**
    - Anonymous tips show as "Anonymous Supporter"
    - Only shows supporters who opted in to be visible
    
    **Use this for:**
    - Public supporter recognition
    - Leaderboard displays
    - Fan engagement
    """
    try:
        leaderboard = TipService.get_leaderboard(db, creator_id, period, limit)
        return TipLeaderboardResponse(**leaderboard)
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")
