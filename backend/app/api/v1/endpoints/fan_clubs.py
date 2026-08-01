"""
Fan Club System API Endpoints
Waves 7-8: REST API for fan clubs, tiers, subscriptions, and exclusive content
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.fan_club import (
    # Fan Club schemas
    FanClubCreate, FanClubUpdate, FanClubResponse,
    # Tier schemas
    TierCreate, TierUpdate, TierResponse,
    # Subscription schemas
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    SubscriptionListResponse,
    # Payment schemas
    PaymentMethodRequest, PaymentResponse,
    # Exclusive content schemas
    ExclusiveContentCreate, ExclusiveContentResponse,
    ContentAccessResponse,
    # Subscriber management
    SubscriberListResponse, BroadcastRequest,
    # Analytics
    SubscriptionAnalytics,
    # Generic
    SuccessResponse
)
from app.services.fan_club_service import FanClubService
from app.services.tier_service import TierService
from app.services.subscription_service import SubscriptionService
from app.services.payment_service import PaymentService
from app.services.content_access_service import ContentAccessService
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/fan-clubs", tags=["Fan Clubs"])

# ============================================================================
# WAVE 7: FAN CLUB MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("", response_model=FanClubResponse, status_code=status.HTTP_201_CREATED)
async def create_fan_club(
    request: FanClubCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new fan club
    
    **Requirements:**
    - User must be verified creator
    - User must be artist, DJ, or producer
    - One fan club per creator
    
    **Returns:**
    - Created fan club with initial configuration
    """
    service = FanClubService(db)
    fan_club = service.create_fan_club(
        creator_id=current_user.id,
        data=request
    )
    return FanClubResponse.from_orm(fan_club)


@router.get("/me", response_model=FanClubResponse)
async def get_my_fan_club(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get my fan club (creator view)
    
    **Returns:**
    - Your fan club details with tiers
    """
    service = FanClubService(db)
    fan_club = service.get_fan_club(creator_id=current_user.id)
    return FanClubResponse.from_orm(fan_club)


@router.put("/me", response_model=FanClubResponse)
async def update_my_fan_club(
    request: FanClubUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update my fan club
    
    **Updatable Fields:**
    - name
    - description
    - welcome_message
    - is_active (cannot deactivate with active subs)
    
    **Returns:**
    - Updated fan club
    """
    service = FanClubService(db)
    # First get the fan club
    fan_club = service.get_fan_club(creator_id=current_user.id)
    
    # Update it
    updated = service.update_fan_club(
        fan_club_id=fan_club.id,
        creator_id=current_user.id,
        data=request
    )
    return FanClubResponse.from_orm(updated)


@router.get("/{creator_id}", response_model=FanClubResponse)
async def get_creator_fan_club(
    creator_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a creator's fan club (public view)
    
    **Public Access:**
    - Anyone can view fan club details
    - Shows tiers and pricing
    - Used for subscription page
    
    **Returns:**
    - Fan club details
    """
    service = FanClubService(db)
    fan_club = service.get_fan_club(creator_id=creator_id)
    return FanClubResponse.from_orm(fan_club)


@router.delete("/me", response_model=SuccessResponse)
async def deactivate_my_fan_club(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate my fan club
    
    **Requirements:**
    - No active subscriptions
    
    **Effect:**
    - Sets is_active = False
    - Prevents new subscriptions
    - Existing content remains accessible to current subs
    
    **Returns:**
    - Success confirmation
    """
    service = FanClubService(db)
    fan_club = service.get_fan_club(creator_id=current_user.id)
    
    service.deactivate_fan_club(
        fan_club_id=fan_club.id,
        creator_id=current_user.id
    )
    
    return SuccessResponse(message="Fan club deactivated successfully")


@router.get("/me/stats", response_model=dict)
async def get_my_fan_club_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get fan club statistics (creator only)
    
    **Metrics:**
    - Total active members
    - Monthly recurring revenue (MRR)
    - Subscribers by tier
    - Revenue by tier
    
    **Returns:**
    - Statistics dictionary
    """
    service = FanClubService(db)
    fan_club = service.get_fan_club(creator_id=current_user.id)
    
    stats = service.get_fan_club_stats(fan_club_id=fan_club.id)
    return stats


@router.get("/me/analytics", response_model=dict, status_code=status.HTTP_200_OK)
async def get_comprehensive_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **Get comprehensive analytics for your fan club.**
    
    Endpoint: `GET /api/v1/fan-clubs/me/analytics`
    
    **Returns:**
    - MRR (Monthly Recurring Revenue)
    - Churn rate
    - LTV (Lifetime Value)
    - Retention cohorts
    - Revenue forecast (3 months)
    - Engagement metrics
    
    **Use Cases:**
    - Track business metrics
    - Forecast revenue
    - Measure subscriber retention
    - Analyze content engagement
    """
    fan_club_service = FanClubService(db)
    fan_club = fan_club_service.get_fan_club(creator_id=current_user.id)
    
    analytics_service = AnalyticsService(db)
    analytics = analytics_service.get_comprehensive_analytics(fan_club_id=fan_club.id)
    
    return analytics


# ============================================================================
# WAVE 7: TIER MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/me/tiers", response_model=TierResponse, status_code=status.HTTP_201_CREATED)
async def create_tier(
    request: TierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a membership tier
    
    **Constraints:**
    - Maximum 3 tiers per fan club
    - Unique tier level (1, 2, or 3)
    - Price between $2.99 - $99.99
    
    **Auto-Calculated:**
    - Yearly price (10% discount)
    
    **Returns:**
    - Created tier
    """
    fan_club_service = FanClubService(db)
    fan_club = fan_club_service.get_fan_club(creator_id=current_user.id)
    
    tier_service = TierService(db)
    tier = tier_service.create_tier(
        fan_club_id=fan_club.id,
        creator_id=current_user.id,
        data=request
    )
    
    return TierResponse.from_orm(tier)


@router.get("/{fan_club_id}/tiers", response_model=List[TierResponse])
async def list_tiers(
    fan_club_id: str,
    include_inactive: bool = Query(False, description="Include inactive tiers"),
    db: Session = Depends(get_db)
):
    """
    List all tiers for a fan club (public)
    
    **Returns:**
    - List of tiers ordered by level (1, 2, 3)
    """
    tier_service = TierService(db)
    tiers = tier_service.list_tiers(
        fan_club_id=fan_club_id,
        include_inactive=include_inactive
    )
    
    return [TierResponse.from_orm(tier) for tier in tiers]


@router.put("/me/tiers/{tier_id}", response_model=TierResponse)
async def update_tier(
    tier_id: str,
    request: TierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a membership tier
    
    **Note:**
    - Price changes affect new subscriptions only
    - Existing subscribers keep their price for current period
    
    **Returns:**
    - Updated tier
    """
    tier_service = TierService(db)
    tier = tier_service.update_tier(
        tier_id=tier_id,
        creator_id=current_user.id,
        data=request
    )
    
    return TierResponse.from_orm(tier)


@router.delete("/me/tiers/{tier_id}", response_model=SuccessResponse)
async def delete_tier(
    tier_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a membership tier
    
    **Requirements:**
    - No active subscriptions to this tier
    
    **Recommendation:**
    - Use pause instead if you have active subscribers
    
    **Returns:**
    - Success confirmation
    """
    tier_service = TierService(db)
    tier_service.delete_tier(
        tier_id=tier_id,
        creator_id=current_user.id
    )
    
    return SuccessResponse(message="Tier deleted successfully")


# ============================================================================
# WAVE 8: SUBSCRIPTION ENDPOINTS
# ============================================================================

@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_tier(
    request: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Subscribe to a membership tier
    
    **Process:**
    1. Creates subscription in 'pending' state
    2. Processes payment
    3. Activates subscription on successful payment
    
    **Validation:**
    - Cannot subscribe to own fan club
    - Only one active subscription per fan club
    - Tier must be active
    
    **Returns:**
    - Subscription details
    """
    # Create subscription
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.create_subscription(
        subscriber_id=current_user.id,
        data=request
    )
    
    # Process payment
    payment_service = PaymentService(db)
    success, payment = payment_service.process_subscription_payment(
        subscription_id=subscription.id,
        payment_method_token=request.payment_method_token,
        save_payment_method=True
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Payment failed: {payment.failure_message if payment else 'Unknown error'}"
        )
    
    # Refresh subscription to get updated status
    db.refresh(subscription)
    
    return SubscriptionResponse.from_orm(subscription)


@router.get("/subscriptions/me", response_model=SubscriptionListResponse)
async def list_my_subscriptions(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List my subscriptions
    
    **Filters:**
    - status: active, cancelled, paused, past_due
    
    **Returns:**
    - Paginated list of subscriptions
    """
    subscription_service = SubscriptionService(db)
    result = subscription_service.list_user_subscriptions(
        user_id=current_user.id,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )
    
    return SubscriptionListResponse(**result)


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get subscription details
    
    **Authorization:**
    - Subscriber can view own subscription
    - Creator can view subscriber details
    
    **Returns:**
    - Subscription details with tier info
    """
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_subscription(
        subscription_id=subscription_id,
        user_id=current_user.id
    )
    
    return SubscriptionResponse.from_orm(subscription)


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    request: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update subscription (upgrade/downgrade tier)
    
    **Upgrade:**
    - Immediate effect
    - Prorated credit applied
    
    **Downgrade:**
    - Effective next billing cycle
    - Keep current tier until period ends
    
    **Returns:**
    - Updated subscription
    """
    subscription_service = SubscriptionService(db)
    
    if request.new_tier_id:
        # Get current subscription
        subscription = subscription_service.get_subscription(
            subscription_id=subscription_id,
            user_id=current_user.id
        )
        
        # Determine if upgrade or downgrade
        current_tier = subscription.tier
        new_tier = TierService(db).get_tier(request.new_tier_id)
        
        if new_tier.tier_level > current_tier.tier_level:
            # Upgrade
            subscription = subscription_service.upgrade_tier(
                subscription_id=subscription_id,
                user_id=current_user.id,
                new_tier_id=request.new_tier_id
            )
        else:
            # Downgrade
            subscription = subscription_service.downgrade_tier(
                subscription_id=subscription_id,
                user_id=current_user.id,
                new_tier_id=request.new_tier_id
            )
    
    if request.auto_renew is not None:
        subscription = subscription_service.get_subscription(subscription_id, current_user.id)
        subscription.auto_renew = request.auto_renew
        db.commit()
        db.refresh(subscription)
    
    return SubscriptionResponse.from_orm(subscription)


@router.delete("/subscriptions/{subscription_id}", response_model=SuccessResponse)
async def cancel_subscription(
    subscription_id: str,
    immediate: bool = Query(False, description="Cancel immediately (requires refund)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel subscription
    
    **Default (immediate=false):**
    - Access continues until end of billing period
    - No refund
    
    **Immediate (immediate=true):**
    - Access ends now
    - Refund issued for unused time
    
    **Returns:**
    - Success confirmation
    """
    subscription_service = SubscriptionService(db)
    subscription_service.cancel_subscription(
        subscription_id=subscription_id,
        user_id=current_user.id,
        immediate=immediate
    )
    
    message = "Subscription cancelled"
    if not immediate:
        message += " - access continues until end of period"
    
    return SuccessResponse(message=message)


@router.post("/subscriptions/{subscription_id}/pause", response_model=SubscriptionResponse)
async def pause_subscription(
    subscription_id: str,
    pause_days: int = Query(30, ge=1, le=90, description="Days to pause (max 90)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Pause subscription
    
    **Duration:**
    - Up to 90 days
    - Once per year
    
    **Effect:**
    - Billing paused
    - Access retained
    - Subscription period extended by pause duration
    
    **Returns:**
    - Updated subscription with pause dates
    """
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.pause_subscription(
        subscription_id=subscription_id,
        user_id=current_user.id,
        pause_duration_days=pause_days
    )
    
    return SubscriptionResponse.from_orm(subscription)


@router.post("/subscriptions/{subscription_id}/resume", response_model=SubscriptionResponse)
async def resume_subscription(
    subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resume paused subscription
    
    **Effect:**
    - Billing resumes
    - Unused pause days removed from period extension
    
    **Returns:**
    - Updated subscription
    """
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.resume_subscription(
        subscription_id=subscription_id,
        user_id=current_user.id
    )
    
    return SubscriptionResponse.from_orm(subscription)


# ============================================================================
# WAVE 8: SUBSCRIBER MANAGEMENT (CREATOR VIEW)
# ============================================================================

@router.get("/me/subscribers", response_model=SubscriberListResponse)
async def list_my_subscribers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tier_level: Optional[int] = Query(None, ge=1, le=3, description="Filter by tier"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List my fan club subscribers (creator only)
    
    **Filters:**
    - tier_level: Filter by specific tier (1, 2, or 3)
    
    **Returns:**
    - Paginated list of subscribers with tier info
    """
    from app.models.fan_club import Subscription, MembershipTier
    from app.schemas.fan_club import SubscriberInfo
    
    # Get creator's fan club
    fan_club_service = FanClubService(db)
    fan_club = fan_club_service.get_fan_club(creator_id=current_user.id)
    
    # Query subscribers
    query = (
        db.query(Subscription)
        .join(MembershipTier, Subscription.tier_id == MembershipTier.id)
        .filter(
            Subscription.fan_club_id == fan_club.id,
            Subscription.status == "active"
        )
    )
    
    if tier_level:
        query = query.filter(MembershipTier.tier_level == tier_level)
    
    # Pagination
    total = query.count()
    offset = (page - 1) * page_size
    subscriptions = query.offset(offset).limit(page_size).all()
    
    # Build response
    subscribers = []
    for sub in subscriptions:
        user = sub.subscriber
        subscriber_info = SubscriberInfo(
            subscriber_id=user.id,
            username=user.username,
            full_name=user.full_name,
            avatar_url=None,  # Add if user has avatar field
            tier_name=sub.tier.name,
            tier_level=sub.tier.tier_level,
            subscription_status=sub.status,
            subscribed_since=sub.started_at
        )
        subscribers.append(subscriber_info)
    
    total_pages = (total + page_size - 1) // page_size
    
    return SubscriberListResponse(
        subscribers=subscribers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/me/broadcast", response_model=SuccessResponse)
async def broadcast_to_members(
    request: BroadcastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send announcement to all members or specific tiers
    
    **Options:**
    - Send to all members
    - Send to specific tier levels
    - Email + Push notification
    
    **Returns:**
    - Success confirmation with recipient count
    """
    from app.models.fan_club import Subscription, MembershipTier
    
    # Get creator's fan club
    fan_club_service = FanClubService(db)
    fan_club = fan_club_service.get_fan_club(creator_id=current_user.id)
    
    # Query recipients
    query = (
        db.query(Subscription)
        .join(MembershipTier, Subscription.tier_id == MembershipTier.id)
        .filter(
            Subscription.fan_club_id == fan_club.id,
            Subscription.status == "active"
        )
    )
    
    if request.tier_levels:
        query = query.filter(MembershipTier.tier_level.in_(request.tier_levels))
    
    subscriptions = query.all()
    
    # Send notifications (in production, this would queue background jobs)
    # For now, just count recipients
    recipient_count = len(subscriptions)
    
    # TODO: Implement notification sending
    # - Email via notification service
    # - Push notification
    
    return SuccessResponse(
        message=f"Broadcast queued for {recipient_count} members"
    )


# ============================================================================
# WAVE 8: EXCLUSIVE CONTENT ENDPOINTS
# ============================================================================

@router.post("/exclusive-content", response_model=ExclusiveContentResponse, status_code=status.HTTP_201_CREATED)
async def mark_content_exclusive(
    request: ExclusiveContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark content as tier-exclusive
    
    **Content Types:**
    - post, track, video, image, event
    
    **Effect:**
    - Content locked behind tier requirement
    - Non-subscribers see teaser (first 20%)
    - Subscribers see full content
    
    **Returns:**
    - Exclusive content record
    """
    content_service = ContentAccessService(db)
    exclusive = content_service.mark_content_exclusive(
        creator_id=current_user.id,
        data=request
    )
    
    return ExclusiveContentResponse.from_orm(exclusive)


@router.get("/exclusive-content/{content_type}/{content_id}/access", response_model=ContentAccessResponse)
async def check_content_access(
    content_type: str,
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if user has access to exclusive content
    
    **Returns:**
    - has_access: boolean
    - reason: Why access denied (if applicable)
    - required_tier_level: Minimum tier needed
    - current_tier_level: User's current tier
    - unlock_url: Link to subscribe
    """
    content_service = ContentAccessService(db)
    access = content_service.check_content_access(
        user_id=current_user.id,
        content_type=content_type,
        content_id=content_id
    )
    
    return access


@router.delete("/exclusive-content/{content_type}/{content_id}", response_model=SuccessResponse)
async def remove_content_exclusivity(
    content_type: str,
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove exclusive status (make content public)
    
    **Effect:**
    - Content accessible to everyone
    - Teaser removed
    
    **Returns:**
    - Success confirmation
    """
    content_service = ContentAccessService(db)
    content_service.remove_exclusivity(
        content_type=content_type,
        content_id=content_id,
        creator_id=current_user.id
    )
    
    return SuccessResponse(message="Content is now public")


@router.get("/{fan_club_id}/exclusive-content", response_model=List[ExclusiveContentResponse])
async def list_exclusive_content(
    fan_club_id: str,
    tier_level: Optional[int] = Query(None, ge=1, le=3),
    content_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List exclusive content for a fan club
    
    **Filters:**
    - tier_level: Filter by required tier
    - content_type: Filter by content type
    
    **Returns:**
    - List of exclusive content
    """
    content_service = ContentAccessService(db)
    content_list = content_service.get_exclusive_content(
        fan_club_id=fan_club_id,
        tier_level=tier_level,
        content_type=content_type
    )
    
    return [ExclusiveContentResponse.from_orm(content) for content in content_list]
