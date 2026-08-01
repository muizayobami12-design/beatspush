"""
Campaign endpoints - Campaign Builder API (Task 3.2)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.user import User
from app.models.campaign import Campaign, CampaignContent, CampaignTemplate
from app.core.dependencies import get_current_user
from app.services.campaign_service import CampaignService
from app.schemas.campaign import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    CampaignScheduleRequest,
    ContentGenerateRequest,
    ContentUpdateRequest,
    CampaignResponse,
    CampaignDetailResponse,
    CampaignListResponse,
    CampaignContentResponse,
    CampaignTemplateResponse,
    CampaignTemplateListResponse,
    MessageResponse,
)

router = APIRouter(prefix="/campaigns", tags=["Campaign Builder"])


# ============================================================================
# CAMPAIGN MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new promotional campaign
    
    **Requires:** Authentication (Artist, DJ, or Producer)
    
    **Steps:**
    1. Select a published track to promote
    2. Choose target platforms (Instagram, TikTok, Twitter, Facebook)
    3. Optionally select a campaign template
    4. Campaign name is auto-generated if not provided
    
    **Campaign Templates:**
    - New Release - Excitement and availability
    - Pre-Release Teaser - Build anticipation
    - Behind The Scenes - Creative process
    - Fan Engagement - Interaction focus
    - Milestone Celebration - Celebrate achievements
    - Throwback Thursday - Nostalgic content
    
    **Example:**
    ```json
    {
      "track_id": "uuid-of-track",
      "template_id": "uuid-of-template",
      "platforms": ["instagram", "tiktok"],
      "name": "My Summer Release Campaign"
    }
    ```
    """
    campaign = CampaignService.create_campaign(db, current_user, campaign_data)
    return campaign


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    status: Optional[str] = Query(None, description="Filter by status (draft, scheduled, active, completed, cancelled)"),
    platform: Optional[str] = Query(None, description="Filter by platform (instagram, tiktok, twitter, facebook)"),
    search: Optional[str] = Query(None, description="Search by campaign name or track title"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all campaigns for the authenticated user
    
    **Requires:** Authentication
    
    **Filters:**
    - `status`: draft, scheduled, active, completed, cancelled, failed
    - `platform`: instagram, tiktok, twitter, facebook
    - `search`: Search in campaign name or track title
    
    **Pagination:**
    - `limit`: Results per page (1-100, default 20)
    - `offset`: Skip N results (default 0)
    
    **Returns:**
    - List of campaigns
    - Total count
    - Pagination info
    """
    campaigns, total = CampaignService.get_user_campaigns(
        db=db,
        user_id=current_user.id,
        status=status,
        platform=platform,
        search=search,
        limit=limit,
        offset=offset
    )
    
    return CampaignListResponse(
        campaigns=campaigns,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed campaign information
    
    **Requires:** Authentication (campaign owner)
    
    **Returns:**
    - Campaign details
    - Track information
    - Template information (if used)
    - All platform content
    - Performance metrics (placeholders)
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Verify ownership
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    # Build detailed response
    track_info = {
        "id": campaign.track.id,
        "title": campaign.track.title,
        "artist_name": campaign.track.artist_name,
        "genre": campaign.track.genre,
        "cover_art_url": campaign.track.cover_art_url
    } if campaign.track else None
    
    template_info = {
        "id": campaign.template.id,
        "name": campaign.template.name,
        "slug": campaign.template.slug,
        "icon": campaign.template.icon
    } if campaign.template else None
    
    # Get content
    content = db.query(CampaignContent).filter(
        CampaignContent.campaign_id == campaign_id
    ).all()
    
    return CampaignDetailResponse(
        **campaign.__dict__,
        track=track_info,
        template=template_info,
        content=content
    )



@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    update_data: CampaignUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update campaign details
    
    **Requires:** Authentication (campaign owner)
    
    **Editable for:** DRAFT and SCHEDULED campaigns only
    
    **Can update:**
    - Campaign name
    - Platform selection (adding platforms generates new content)
    - Scheduled publish time
    
    **Example:**
    ```json
    {
      "name": "Updated Campaign Name",
      "platforms": ["instagram", "twitter", "facebook"],
      "scheduled_publish_time": "2024-12-25T10:00:00Z"
    }
    ```
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    campaign = CampaignService.update_campaign(db, campaign, update_data)
    return campaign


@router.delete("/{campaign_id}", response_model=MessageResponse)
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a campaign
    
    **Requires:** Authentication (campaign owner)
    
    **Can delete:** DRAFT, CANCELLED, or COMPLETED campaigns only
    
    **Note:** This will also delete all associated content and activity logs (cascade delete)
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    CampaignService.delete_campaign(db, campaign)
    
    return MessageResponse(
        message="Campaign deleted successfully",
        success=True
    )


# ============================================================================
# CAMPAIGN ACTION ENDPOINTS
# ============================================================================

@router.post("/{campaign_id}/duplicate", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Duplicate an existing campaign
    
    **Requires:** Authentication (campaign owner)
    
    **Copies:**
    - Platform selections
    - Template selection
    - Campaign name (with " (Copy)" suffix)
    
    **Does NOT copy:**
    - Track selection (must select new track)
    - Generated content (must generate new content)
    - Campaign status (new campaign is DRAFT)
    
    **Use case:** Quickly create similar campaigns for different tracks
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    new_campaign = CampaignService.duplicate_campaign(db, current_user, campaign)
    return new_campaign


@router.post("/{campaign_id}/cancel", response_model=CampaignResponse)
async def cancel_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an active or scheduled campaign
    
    **Requires:** Authentication (campaign owner)
    
    **Can cancel:** ACTIVE or SCHEDULED campaigns only
    
    **Effect:**
    - Sets status to CANCELLED
    - Records cancellation timestamp
    - Cannot be reactivated (create new campaign instead)
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    campaign = CampaignService.cancel_campaign(db, campaign)
    return campaign


@router.post("/{campaign_id}/complete", response_model=CampaignResponse)
async def complete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark campaign as completed
    
    **Requires:** Authentication (campaign owner)
    
    **Use case:** Manually complete an active campaign when promotion period ends
    
    **Effect:**
    - Sets status to COMPLETED
    - Records completion timestamp
    - Campaign moves to "Past" tab in dashboard
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    campaign = CampaignService.complete_campaign(db, campaign)
    return campaign



@router.post("/{campaign_id}/schedule", response_model=CampaignResponse)
async def schedule_campaign(
    campaign_id: str,
    schedule_data: CampaignScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Schedule campaign for future publication
    
    **Requires:** Authentication (campaign owner)
    
    **Requirements:**
    - Scheduled time must be in the future
    - Campaign must have generated content
    
    **Effect:**
    - Sets status to SCHEDULED
    - Background task will activate at scheduled time
    - Status changes to ACTIVE when time arrives
    
    **Example:**
    ```json
    {
      "scheduled_publish_time": "2024-12-25T10:00:00Z"
    }
    ```
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    campaign = CampaignService.schedule_campaign(
        db, campaign, schedule_data.scheduled_publish_time
    )
    return campaign


@router.post("/{campaign_id}/publish", response_model=CampaignResponse)
async def publish_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publish campaign immediately
    
    **Requires:** Authentication (campaign owner)
    
    **Effect:**
    - Sets status to ACTIVE
    - Records publication timestamp
    - Campaign appears in "Active" tab
    
    **Note:** In Task 3.3 (Social Media Integration), this will trigger actual posting to social media platforms
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    campaign = CampaignService.publish_campaign(db, campaign)
    return campaign


# ============================================================================
# CAMPAIGN CONTENT ENDPOINTS
# ============================================================================

@router.post("/{campaign_id}/generate-content", response_model=MessageResponse)
async def generate_content(
    campaign_id: str,
    content_data: ContentGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI content for selected platforms
    
    **Requires:** Authentication (campaign owner)
    
    **Process:**
    1. Calls AI Service to generate captions
    2. Generates hashtags
    3. Applies campaign template strategy (if used)
    4. Creates content records for each platform
    
    **Example:**
    ```json
    {
      "platforms": ["instagram", "tiktok"]
    }
    ```
    
    **Returns:** Success message with content count
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    content = CampaignService.generate_content(db, campaign, content_data.platforms)
    
    return MessageResponse(
        message=f"Generated content for {len(content)} platforms",
        success=True
    )


@router.get("/{campaign_id}/content", response_model=list[CampaignContentResponse])
async def get_campaign_content(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all content for a campaign
    
    **Requires:** Authentication (campaign owner)
    
    **Returns:** List of content for each platform with:
    - Captions
    - Hashtags
    - Caption tone
    - Edit status
    - Performance metrics (placeholders)
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    content = db.query(CampaignContent).filter(
        CampaignContent.campaign_id == campaign_id
    ).all()
    
    return content


@router.put("/{campaign_id}/content/{platform}", response_model=CampaignContentResponse)
async def update_content(
    campaign_id: str,
    platform: str,
    update_data: ContentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update content for a specific platform
    
    **Requires:** Authentication (campaign owner)
    
    **Can update:**
    - Caption text
    - Hashtags
    - Caption tone
    
    **Note:** Marks content as edited (content_edited = true)
    
    **Example:**
    ```json
    {
      "caption": "Updated caption text with emojis 🎵",
      "hashtags": ["#afrobeats", "#newmusic", "#2024"],
      "caption_tone": "hype"
    }
    ```
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this campaign"
        )
    
    content = db.query(CampaignContent).filter(
        CampaignContent.campaign_id == campaign_id,
        CampaignContent.platform == platform
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No content found for platform: {platform}"
        )
    
    content = CampaignService.update_content(db, content, update_data)
    return content



# ============================================================================
# CAMPAIGN TEMPLATE ENDPOINTS
# ============================================================================

@router.get("/templates/list", response_model=CampaignTemplateListResponse)
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all available campaign templates
    
    **Requires:** Authentication
    
    **Returns:** All active campaign templates with:
    - Template name and description
    - Recommended platforms
    - Usage count
    - Icon
    
    **Templates:**
    - **New Release** 🎵 - Excitement and availability
    - **Pre-Release Teaser** 🔥 - Build anticipation
    - **Behind The Scenes** 🎬 - Creative process
    - **Fan Engagement** 💬 - Interaction focus
    - **Milestone Celebration** 🎉 - Celebrate achievements
    - **Throwback Thursday** ⏮️ - Nostalgic content
    """
    templates = db.query(CampaignTemplate).filter(
        CampaignTemplate.is_active == True
    ).order_by(CampaignTemplate.usage_count.desc()).all()
    
    return CampaignTemplateListResponse(templates=templates)


@router.get("/templates/{template_id}", response_model=CampaignTemplateResponse)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get template details
    
    **Requires:** Authentication
    
    **Returns:** Detailed template information including:
    - Prompt strategy (how AI generates content)
    - Recommended platforms
    - Usage statistics
    """
    template = db.query(CampaignTemplate).filter(
        CampaignTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template
