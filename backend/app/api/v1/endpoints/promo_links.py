"""
Promo Links API Endpoints
Task 3.5: Promo Link Generator

Endpoints for smart link generation, tracking, and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.core.dependencies import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.promo_link import PromoLink, LinkClick
from app.services.promo_link_service import PromoLinkService
from app.schemas.promo_link import (
    PromoLinkCreateRequest,
    PromoLinkUpdateRequest,
    PromoLinkResponse,
    PromoLinkDetailResponse,
    PromoLinkListResponse,
    LinkAnalyticsResponse,
    GeoRuleCreateRequest,
    GeoRuleResponse,
    QRCodeResponse,
    MessageResponse,
)

router = APIRouter(prefix="/promo-links", tags=["Promo Links"])


# ================== LINK MANAGEMENT ==================

@router.post("/", response_model=PromoLinkResponse, status_code=201)
def create_promo_link(
    request: PromoLinkCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]))
):
    """
    Create a new promo link for a track.
    
    **Requirements:**
    - User must be an Artist, DJ, or Producer
    - Track must belong to the user
    - At least one platform URL should be provided
    
    **Returns:**
    - Promo link with unique short code
    - Short URL: beatpush.to/{short_code}
    """
    try:
        promo_link = PromoLinkService.create_promo_link(db, current_user.id, request)
        
        # Build response with URLs
        response = PromoLinkResponse(
            **promo_link.__dict__,
            short_url=f"https://beatpush.to/{promo_link.short_code}",
            full_url=f"https://beatpush.com/l/{promo_link.short_code}",
            qr_code_url=f"/api/v1/promo-links/{promo_link.id}/qr"
        )
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create promo link: {str(e)}")


@router.get("/", response_model=PromoLinkListResponse)
def list_promo_links(
    track_id: Optional[str] = Query(None, description="Filter by track ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in title, description, short code"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]))
):
    """
    List user's promo links with optional filters.
    
    **Filters:**
    - `track_id`: Show links for specific track
    - `is_active`: Show only active or inactive links
    - `search`: Search in title, description, or short code
    
    **Pagination:**
    - `page`: Page number (starts at 1)
    - `page_size`: Items per page (1-100, default 20)
    """
    skip = (page - 1) * page_size
    
    links, total = PromoLinkService.get_user_links(
        db=db,
        user_id=current_user.id,
        track_id=track_id,
        is_active=is_active,
        search=search,
        skip=skip,
        limit=page_size
    )
    
    # Build responses with URLs
    link_responses = []
    for link in links:
        response = PromoLinkResponse(
            **link.__dict__,
            short_url=f"https://beatpush.to/{link.short_code}",
            full_url=f"https://beatpush.com/l/{link.short_code}",
            qr_code_url=f"/api/v1/promo-links/{link.id}/qr"
        )
        link_responses.append(response)
    
    return PromoLinkListResponse(
        links=link_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(skip + page_size) < total
    )


@router.get("/{link_id}", response_model=PromoLinkDetailResponse)
def get_promo_link(
    link_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]))
):
    """
    Get detailed promo link information including track details and basic analytics.
    
    **Returns:**
    - Full promo link details
    - Track information
    - Platform click counts
    - Country breakdown
    - Recent 10 clicks
    """
    promo_link = PromoLinkService.get_promo_link(db, link_id, current_user.id)
    
    if not promo_link:
        raise HTTPException(status_code=404, detail="Promo link not found")
    
    # Get track info
    from app.models.track import Track
    track = db.query(Track).filter(Track.id == promo_link.track_id).first()
    
    # Get platform clicks
    platform_clicks = {}
    country_clicks = {}
    
    clicks = db.query(LinkClick).filter(LinkClick.promo_link_id == link_id).all()
    
    for click in clicks:
        platform_clicks[click.platform] = platform_clicks.get(click.platform, 0) + 1
        if click.country:
            country_clicks[click.country] = country_clicks.get(click.country, 0) + 1
    
    # Get recent clicks
    recent_clicks = db.query(LinkClick).filter(
        LinkClick.promo_link_id == link_id
    ).order_by(LinkClick.clicked_at.desc()).limit(10).all()
    
    recent_clicks_list = [
        {
            "platform": click.platform,
            "country": click.country,
            "device": click.device_type,
            "clicked_at": click.clicked_at.isoformat()
        }
        for click in recent_clicks
    ]
    
    # Build response
    response = PromoLinkDetailResponse(
        **promo_link.__dict__,
        short_url=f"https://beatpush.to/{promo_link.short_code}",
        full_url=f"https://beatpush.com/l/{promo_link.short_code}",
        qr_code_url=f"/api/v1/promo-links/{promo_link.id}/qr",
        track_title=track.title if track else "Unknown",
        track_artist=track.artist_name if track else "Unknown",
        track_cover_url=track.cover_art_url if track else None,
        platform_clicks=platform_clicks,
        country_clicks=country_clicks,
        recent_clicks=recent_clicks_list
    )
    
    return response


@router.put("/{link_id}", response_model=PromoLinkResponse)
def update_promo_link(
    link_id: str,
    request: PromoLinkUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]))
):
    """
    Update an existing promo link.
    
    **Updatable fields:**
    - Title, description
    - Platform URLs
    - Branding (colors, custom domain)
    - UTM parameters
    - Active status
    - Expiration date
    
    **Note:** Short code cannot be changed after creation.
    """
    promo_link = PromoLinkService.update_promo_link(db, link_id, current_user.id, request)
    
    if not promo_link:
        raise HTTPException(status_code=404, detail="Promo link not found")
    
    response = PromoLinkResponse(
        **promo_link.__dict__,
        short_url=f"https://beatpush.to/{promo_link.short_code}",
        full_url=f"https://beatpush.com/l/{promo_link.short_code}",
        qr_code_url=f"/api/v1/promo-links/{promo_link.id}/qr"
    )
    
    return response


@router.delete("/{link_id}", response_model=MessageResponse)
def delete_promo_link(
    link_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]))
):
    """
    Delete a promo link.
    
    **Warning:** This action:
    - Permanently deletes the link
    - Removes all click tracking data
    - Removes all geo-targeting rules
    - Cannot be undone
    
    **Note:** The short code becomes available for reuse.
    """
    success = PromoLinkService.delete_promo_link(db, link_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Promo link not found")
    
    return MessageResponse(message="Promo link deleted successfully")


# ================== ANALYTICS ==================

@router.get("/{link_id}/analytics", response_model=LinkAnalyticsResponse)
def get_link_analytics(
    link_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]))
):
    """
    Get comprehensive analytics for a promo link.
    
    **Returns:**
    - Total and unique clicks
    - Conversion rate
    - Platform breakdown with percentages
    - Geographic distribution (countries, cities)
    - Device, OS, and browser stats
    - Daily clicks for last 30 days
    - Top 10 referrers
    
    **Use this endpoint for:**
    - Analytics dashboards
    - Performance reports
    - Campaign insights
    """
    analytics = PromoLinkService.get_link_analytics(db, link_id, current_user.id)
    
    if analytics is None:
        raise HTTPException(status_code=404, detail="Promo link not found")
    
    return LinkAnalyticsResponse(**analytics)


# ================== QR CODE ==================

@router.get("/{link_id}/qr", response_model=QRCodeResponse)
def generate_qr_code(
    link_id: str,
    size: int = Query(300, ge=100, le=1000, description="QR code size in pixels"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]))
):
    """
    Generate QR code for a promo link.
    
    **Parameters:**
    - `size`: QR code size in pixels (100-1000, default 300)
    
    **Returns:**
    - QR code as base64 encoded PNG image
    - Can be used directly in <img> tags
    
    **Usage:**
    ```html
    <img src="{qr_code_data}" alt="Scan to listen" />
    ```
    """
    promo_link = PromoLinkService.get_promo_link(db, link_id, current_user.id)
    
    if not promo_link:
        raise HTTPException(status_code=404, detail="Promo link not found")
    
    qr_code_data = PromoLinkService.generate_qr_code(promo_link, size=size)
    
    if not qr_code_data:
        raise HTTPException(status_code=500, detail="Failed to generate QR code. Install 'qrcode' library.")
    
    return QRCodeResponse(
        promo_link_id=link_id,
        qr_code_url=f"https://beatpush.com/api/v1/promo-links/{link_id}/qr",
        qr_code_data=qr_code_data
    )


# ================== GEO-TARGETING ==================

@router.post("/{link_id}/geo-rules", response_model=GeoRuleResponse, status_code=201)
def create_geo_rule(
    link_id: str,
    request: GeoRuleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]))
):
    """
    Create geo-targeting rule for a promo link.
    
    **Purpose:** Direct users from specific countries to preferred platforms.
    
    **Example:**
    ```json
    {
      "country_codes": ["NG", "GH", "KE"],  // Nigeria, Ghana, Kenya
      "platform": "audiomack",               // Popular in Africa
      "priority": 1,
      "fallback_url": "https://spotify.com/..."
    }
    ```
    
    **Priority:** Higher priority rules are checked first (1 > 0 > -1)
    """
    try:
        geo_rule = PromoLinkService.create_geo_rule(db, link_id, current_user.id, request)
        return GeoRuleResponse(**geo_rule.__dict__)
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create geo rule: {str(e)}")


@router.get("/{link_id}/geo-rules", response_model=List[GeoRuleResponse])
def list_geo_rules(
    link_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]))
):
    """
    List all geo-targeting rules for a promo link.
    
    **Returns:** All rules ordered by priority (highest first)
    """
    # Verify link exists and belongs to user
    promo_link = PromoLinkService.get_promo_link(db, link_id, current_user.id)
    if not promo_link:
        raise HTTPException(status_code=404, detail="Promo link not found")
    
    from app.models.promo_link import GeoRule
    geo_rules = db.query(GeoRule).filter(
        GeoRule.promo_link_id == link_id
    ).order_by(GeoRule.priority.desc()).all()
    
    return [GeoRuleResponse(**rule.__dict__) for rule in geo_rules]


# ================== PUBLIC REDIRECT ENDPOINT ==================

@router.get("/redirect/{short_code}")
async def redirect_to_platform(
    short_code: str,
    platform: str = Query("spotify", description="Platform to redirect to"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    **PUBLIC ENDPOINT** - Redirect to streaming platform.
    
    **Usage:**
    - `GET /promo-links/redirect/{short_code}?platform=spotify`
    - Tracks click and redirects to platform URL
    
    **Platforms:**
    - spotify, apple_music, youtube, tidal, soundcloud, audiomack, boomplay, deezer
    
    **Tracking:**
    - Records IP, user agent, device info, location
    - Counts total and unique clicks
    - Can be used for analytics
    """
    from fastapi.responses import RedirectResponse
    import hashlib
    
    # Get promo link
    promo_link = PromoLinkService.get_promo_link_by_short_code(db, short_code)
    
    if not promo_link:
        raise HTTPException(status_code=404, detail="Link not found or expired")
    
    # Get platform URL
    platform_url = PromoLinkService.get_platform_url(promo_link, platform)
    
    if not platform_url:
        # Fallback to landing page if platform URL not available
        return RedirectResponse(url=f"https://beatpush.com/l/{short_code}")
    
    # Extract request info for tracking
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    referrer = request.headers.get("referer") if request else None
    
    # Generate session ID from IP + user agent
    session_data = f"{ip_address}{user_agent}".encode()
    session_id = hashlib.md5(session_data).hexdigest()
    
    # Track click
    try:
        PromoLinkService.track_click(
            db=db,
            promo_link_id=promo_link.id,
            platform=platform,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            session_id=session_id,
        )
    except Exception as e:
        # Don't fail redirect if tracking fails
        print(f"Click tracking error: {e}")
    
    # Redirect to platform
    return RedirectResponse(url=platform_url, status_code=307)
