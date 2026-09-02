"""
Beats API Endpoints
Task 5.4: Beat Marketplace

Endpoints for beat marketplace, purchasing, and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.beat_service import BeatService
from app.schemas.beat import (
    BeatCreateRequest,
    BeatUpdateRequest,
    BeatPurchaseRequest,
    BeatPlayRequest,
    BeatResponse,
    BeatListResponse,
    BeatPurchaseResponse,
    BeatPurchaseListResponse,
    BeatStatsResponse,
    ProducerEarningsResponse,
    LicenseCertificateResponse,
    MessageResponse,
)

router = APIRouter(prefix="/beats", tags=["Beats"])


# ================== BEAT LISTING & MANAGEMENT ==================

@router.post("/create", response_model=BeatResponse, status_code=201)
def create_beat(
    request: BeatCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new beat listing (producers only).
    
    **Requirements:**
    - Must be a producer
    - Tagged audio URL (with producer tag)
    - Untagged audio URL (for purchasers)
    
    **Pricing:**
    - Lease: Typically $20-$200
    - Exclusive: Typically $200-$2000+
    
    **Platform Fee:** 15% of sale price
    
    **Returns:** Beat listing with all details
    """
    try:
        # Verify user is a producer
        if current_user.role not in ["PRODUCER", "producer"]:
            raise ValueError("Only producers can list beats")
        
        beat = BeatService.create_beat(db, current_user.id, request)
        
        # Build response
        producer = db.query(User).filter(User.id == beat.producer_user_id).first()
        
        # Create dict from beat, removing duplicates
        beat_dict = {k: v for k, v in beat.__dict__.items() if not k.startswith('_')}
        beat_dict['producer_name'] = producer.username or producer.full_name
        
        response = BeatResponse(**beat_dict)
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create beat: {str(e)}")


@router.get("/browse", response_model=BeatListResponse)
def browse_beats(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    min_bpm: Optional[int] = Query(None, description="Minimum BPM"),
    max_bpm: Optional[int] = Query(None, description="Maximum BPM"),
    musical_key: Optional[str] = Query(None, description="Musical key"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    search: Optional[str] = Query(None, description="Search in title, description, tags"),
    sort_by: str = Query("newest", description="newest, popular, price_low, price_high"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    **PUBLIC ENDPOINT** - Browse beat marketplace with filters.
    
    **Filters:**
    - `genre`: Filter by genre
    - `min_bpm`, `max_bpm`: BPM range
    - `musical_key`: Musical key (e.g., "C minor")
    - `min_price`, `max_price`: Price range
    - `search`: Search text
    
    **Sorting:**
    - `newest`: Recently added (default)
    - `popular`: Most played
    - `price_low`: Lowest price first
    - `price_high`: Highest price first
    
    **Returns:**
    - List of beats with pagination
    - User-specific data (favorited, purchased) if authenticated
    """
    skip = (page - 1) * page_size
    user_id = current_user.id if current_user else None
    
    beats, total = BeatService.browse_beats(
        db, genre, min_bpm, max_bpm, musical_key, min_price, max_price,
        search, sort_by, skip, page_size, user_id
    )
    
    # Build responses
    beat_responses = []
    for beat in beats:
        producer = db.query(User).filter(User.id == beat.producer_user_id).first()
        
        # Create dict from beat, removing duplicates
        beat_dict = {k: v for k, v in beat.__dict__.items() if not k.startswith('_')}
        beat_dict['producer_name'] = producer.username or producer.full_name if producer else "Unknown"
        
        # Only set if not already present from query
        if 'is_favorited' not in beat_dict:
            beat_dict['is_favorited'] = False
        if 'is_purchased' not in beat_dict:
            beat_dict['is_purchased'] = False
            
        beat_responses.append(BeatResponse(**beat_dict))
    
    return BeatListResponse(
        beats=beat_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{beat_id}", response_model=BeatResponse)
def get_beat(
    beat_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    **PUBLIC ENDPOINT** - Get beat details.
    
    **Returns:**
    - Complete beat information
    - Producer details
    - Statistics (plays, favorites, purchases)
    - User interaction status (if authenticated)
    """
    user_id = current_user.id if current_user else None
    beat = BeatService.get_beat(db, beat_id, user_id)
    
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")
    
    # Build response
    producer = db.query(User).filter(User.id == beat.producer_user_id).first()
    
    # Create dict from beat, removing duplicates
    beat_dict = {k: v for k, v in beat.__dict__.items() if not k.startswith('_')}
    beat_dict['producer_name'] = producer.username or producer.full_name if producer else "Unknown"
    
    # Only set if not already present from query
    if 'is_favorited' not in beat_dict:
        beat_dict['is_favorited'] = False
    if 'is_purchased' not in beat_dict:
        beat_dict['is_purchased'] = False
        
    return BeatResponse(**beat_dict)


@router.put("/{beat_id}", response_model=BeatResponse)
def update_beat(
    beat_id: str,
    request: BeatUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update beat listing (producer only).
    
    **Authorization:** Must be the producer who created the beat
    
    **Updatable Fields:**
    - Title, description, cover art
    - Technical details (BPM, key, genre, mood)
    - Pricing (lease, exclusive)
    - License terms
    - Tags
    - Availability status
    
    **Returns:** Updated beat
    """
    try:
        beat = BeatService.update_beat(db, beat_id, current_user.id, request)
        
        producer = db.query(User).filter(User.id == beat.producer_user_id).first()
        
        # Create dict from beat, removing duplicates
        beat_dict = {k: v for k, v in beat.__dict__.items() if not k.startswith('_')}
        beat_dict['producer_name'] = producer.username or producer.full_name
        
        return BeatResponse(**beat_dict)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update beat: {str(e)}")


@router.delete("/{beat_id}", response_model=MessageResponse)
def delete_beat(
    beat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete beat listing (producer only, no sales).
    
    **Authorization:** Must be the producer who created the beat
    
    **Restriction:** Cannot delete beats with existing sales
    
    **Returns:** Confirmation message
    """
    try:
        BeatService.delete_beat(db, beat_id, current_user.id)
        
        return MessageResponse(
            message="Beat deleted successfully",
            data={"beat_id": beat_id}
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete beat: {str(e)}")


@router.get("/my/beats", response_model=BeatListResponse)
def get_my_beats(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's beat listings.
    
    **Returns:**
    - All beats created by current user
    - Includes drafts and sold beats
    """
    skip = (page - 1) * page_size
    
    from app.models.beat import Beat
    query = db.query(Beat).filter(Beat.producer_user_id == current_user.id)
    
    total = query.count()
    beats = query.order_by(Beat.created_at.desc()).offset(skip).limit(page_size).all()
    
    beat_responses = []
    for beat in beats:
        beat_dict = {k: v for k, v in beat.__dict__.items() if not k.startswith('_')}
        beat_dict['producer_name'] = current_user.username or current_user.full_name
        beat_responses.append(BeatResponse(**beat_dict))
    
    return BeatListResponse(
        beats=beat_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


# ================== PURCHASING ==================

@router.post("/{beat_id}/purchase", response_model=BeatPurchaseResponse, status_code=201)
def purchase_beat(
    beat_id: str,
    request: BeatPurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Purchase a beat.
    
    **License Types:**
    - `lease`: Non-exclusive, limited usage
    - `exclusive`: Full exclusive rights
    
    **Process:**
    1. Payment processed (simulated)
    2. License generated
    3. Download link provided
    4. Producer earns payout (85%)
    5. Platform takes commission (15%)
    
    **Exclusive Purchase:**
    - Beat removed from marketplace
    - No further sales allowed
    - Buyer gets full rights
    
    **Returns:** Purchase confirmation with license details
    """
    try:
        purchase = BeatService.purchase_beat(db, beat_id, current_user.id, request)
        
        # Get details
        from app.models.beat import Beat
        beat = db.query(Beat).filter(Beat.id == purchase.beat_id).first()
        producer = db.query(User).filter(User.id == purchase.producer_user_id).first()
        
        return BeatPurchaseResponse(
            **purchase.__dict__,
            beat_title=beat.title if beat else None,
            producer_name=producer.username or producer.full_name if producer else "Unknown",
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to purchase beat: {str(e)}")


@router.get("/purchases/my", response_model=BeatPurchaseListResponse)
def get_my_purchases(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's beat purchases.
    
    **Returns:**
    - All beats purchased by current user
    - License details
    - Download links
    """
    skip = (page - 1) * page_size
    
    purchases, total = BeatService.get_user_purchases(db, current_user.id, skip, page_size)
    
    # Build responses
    purchase_responses = []
    for purchase in purchases:
        from app.models.beat import Beat
        beat = db.query(Beat).filter(Beat.id == purchase.beat_id).first()
        producer = db.query(User).filter(User.id == purchase.producer_user_id).first()
        
        purchase_responses.append(BeatPurchaseResponse(
            **purchase.__dict__,
            beat_title=beat.title if beat else "Deleted Beat",
            producer_name=producer.username or producer.full_name if producer else "Unknown",
        ))
    
    return BeatPurchaseListResponse(
        purchases=purchase_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/sales/my", response_model=BeatPurchaseListResponse)
def get_my_sales(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's beat sales (producer only).
    
    **Returns:**
    - All sales of beats by current user
    - Buyer information
    - Revenue details
    """
    skip = (page - 1) * page_size
    
    sales, total = BeatService.get_producer_sales(db, current_user.id, skip, page_size)
    
    # Build responses
    sale_responses = []
    for sale in sales:
        from app.models.beat import Beat
        beat = db.query(Beat).filter(Beat.id == sale.beat_id).first()
        buyer = db.query(User).filter(User.id == sale.buyer_user_id).first()
        
        sale_responses.append(BeatPurchaseResponse(
            **sale.__dict__,
            beat_title=beat.title if beat else "Deleted Beat",
            producer_name=buyer.username or buyer.full_name if buyer else "Unknown",  # Buyer name in sales view
        ))
    
    return BeatPurchaseListResponse(
        purchases=sale_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


# ================== FAVORITES ==================

@router.post("/{beat_id}/favorite", response_model=MessageResponse)
def toggle_favorite(
    beat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle favorite status for a beat.
    
    **Effect:**
    - If not favorited: Add to favorites
    - If favorited: Remove from favorites
    
    **Returns:** Current favorite status
    """
    try:
        is_favorited = BeatService.toggle_favorite(db, beat_id, current_user.id)
        
        return MessageResponse(
            message="Favorited" if is_favorited else "Unfavorited",
            data={"is_favorited": is_favorited}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle favorite: {str(e)}")


@router.get("/favorites/my", response_model=BeatListResponse)
def get_my_favorites(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's favorite beats.
    
    **Returns:** List of favorited beats
    """
    skip = (page - 1) * page_size
    
    beats, total = BeatService.get_user_favorites(db, current_user.id, skip, page_size)
    
    # Build responses
    beat_responses = []
    for beat in beats:
        producer = db.query(User).filter(User.id == beat.producer_user_id).first()
        
        # Create dict from beat, removing duplicates
        beat_dict = {k: v for k, v in beat.__dict__.items() if not k.startswith('_')}
        beat_dict['producer_name'] = producer.username or producer.full_name if producer else "Unknown"
        beat_dict['is_favorited'] = True
        
        beat_responses.append(BeatResponse(**beat_dict))
    
    return BeatListResponse(
        beats=beat_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


# ================== PLAY TRACKING ==================

@router.post("/{beat_id}/play", response_model=MessageResponse, status_code=201)
def track_play(
    beat_id: str,
    request: BeatPlayRequest,
    req: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    **PUBLIC ENDPOINT** - Track beat play.
    
    **Parameters:**
    - `duration_played`: Seconds played
    - `completed`: Whether full beat was played
    
    **Use this when:**
    - User clicks play on beat
    - Track listening analytics
    - Count towards popularity
    
    **Returns:** Confirmation
    """
    try:
        user_id = current_user.id if current_user else None
        ip_address = req.client.host if req.client else None
        user_agent = req.headers.get("user-agent")
        
        BeatService.track_play(db, beat_id, user_id, request, ip_address, user_agent)
        
        return MessageResponse(message="Play tracked")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track play: {str(e)}")


# ================== STATISTICS & ANALYTICS ==================

@router.get("/stats/my", response_model=BeatStatsResponse)
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get beat statistics for current user (producer).
    
    **Returns:**
    - Total beats, active beats
    - Sales statistics
    - Revenue breakdown (lease vs exclusive)
    - Top performing beats
    - Recent purchases
    
    **Use this for:**
    - Producer dashboard
    - Performance tracking
    """
    stats = BeatService.get_beat_stats(db, current_user.id)
    
    # Format top beats
    top_beat_responses = []
    for beat in stats["top_beats"]:
        beat_dict = {k: v for k, v in beat.__dict__.items() if not k.startswith('_')}
        beat_dict['producer_name'] = current_user.username or current_user.full_name
        top_beat_responses.append(BeatResponse(**beat_dict))
    
    # Format recent purchases
    recent_purchase_responses = []
    for purchase in stats["recent_purchases"]:
        from app.models.beat import Beat
        beat = db.query(Beat).filter(Beat.id == purchase.beat_id).first()
        buyer = db.query(User).filter(User.id == purchase.buyer_user_id).first()
        
        recent_purchase_responses.append(BeatPurchaseResponse(
            **purchase.__dict__,
            beat_title=beat.title if beat else "Deleted",
            producer_name=buyer.username or buyer.full_name if buyer else "Unknown",
        ))
    
    return BeatStatsResponse(
        total_beats=stats["total_beats"],
        active_beats=stats["active_beats"],
        total_sales=stats["total_sales"],
        total_revenue=stats["total_revenue"],
        lease_sales=stats["lease_sales"],
        exclusive_sales=stats["exclusive_sales"],
        top_beats=top_beat_responses,
        recent_purchases=recent_purchase_responses,
    )


@router.get("/earnings/my", response_model=ProducerEarningsResponse)
def get_my_earnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get earnings dashboard (producer only).
    
    **Returns:**
    - Total earned (all-time)
    - Pending earnings
    - Withdrawn earnings
    - Total sales count
    - Average sale price
    - Revenue breakdown (lease vs exclusive)
    - Top selling beats
    
    **Use this for:**
    - Financial tracking
    - Revenue analysis
    - Withdrawal planning
    """
    earnings = BeatService.get_producer_earnings(db, current_user.id)
    
    return ProducerEarningsResponse(**earnings)


# ================== LICENSE CERTIFICATE ==================

@router.get("/purchases/{purchase_id}/certificate", response_model=LicenseCertificateResponse)
def get_license_certificate(
    purchase_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get license certificate for a purchase.
    
    **Authorization:** Must be the buyer or producer
    
    **Returns:**
    - License certificate text
    - License key
    - Beat and buyer details
    - Terms and conditions
    
    **Note:** In production, generates PDF certificate
    """
    try:
        # Verify user is buyer or producer
        from app.models.beat import BeatPurchase
        purchase = db.query(BeatPurchase).filter(BeatPurchase.id == purchase_id).first()
        
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase not found")
        
        if purchase.buyer_user_id != current_user.id and purchase.producer_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        certificate = BeatService.generate_license_certificate(db, purchase_id)
        
        return LicenseCertificateResponse(**certificate)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate certificate: {str(e)}")
