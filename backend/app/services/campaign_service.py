"""
Campaign Service - Business logic for Campaign Builder
"""
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.track import Track, TrackStatus
from app.models.campaign import (
    Campaign,
    CampaignContent,
    CampaignTemplate,
    CampaignActivityLog,
    CampaignStatus,
    Platform,
    ContentType,
)
from app.schemas.campaign import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    ContentUpdateRequest,
)
from app.ai.ai_service import AIService


class CampaignService:
    """Campaign business logic"""
    
    @staticmethod
    def create_campaign(
        db: Session,
        user: User,
        campaign_data: CampaignCreateRequest
    ) -> Campaign:
        """
        Create a new campaign
        
        Args:
            db: Database session
            user: Current user
            campaign_data: Campaign creation data
            
        Returns:
            Created campaign
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate user role
        if user.role not in [UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only artists, DJs, and producers can create campaigns"
            )
        
        # Validate track exists and belongs to user
        track = db.query(Track).filter(Track.id == campaign_data.track_id).first()
        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Track not found"
            )
        
        if track.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't own this track"
            )
        
        if track.status != TrackStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only published tracks can be promoted"
            )
        
        # Validate template if provided
        template = None
        if campaign_data.template_id:
            template = db.query(CampaignTemplate).filter(
                CampaignTemplate.id == campaign_data.template_id
            ).first()
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )
        
        # Generate campaign name if not provided
        campaign_name = campaign_data.name
        if not campaign_name:
            campaign_name = CampaignService.generate_campaign_name(
                track.title,
                template.name if template else None
            )
            
            # Ensure uniqueness
            base_name = campaign_name
            counter = 2
            while db.query(Campaign).filter(
                Campaign.user_id == user.id,
                Campaign.name == campaign_name
            ).first():
                campaign_name = f"{base_name} ({counter})"
                counter += 1
        
        # Create campaign
        campaign = Campaign(
            id=str(uuid.uuid4()),
            user_id=user.id,
            track_id=track.id,
            template_id=template.id if template else None,
            name=campaign_name,
            status=CampaignStatus.DRAFT,
            platforms=campaign_data.platforms
        )
        
        db.add(campaign)
        db.flush()  # Get campaign ID
        
        # Update template usage count
        if template:
            template.usage_count += 1
        
        # Log activity
        CampaignService.log_activity(
            db=db,
            campaign_id=campaign.id,
            user_id=user.id,
            action="created",
            details={
                "track_id": track.id,
                "track_title": track.title,
                "template_id": template.id if template else None,
                "platforms": campaign_data.platforms
            }
        )
        
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def generate_content(
        db: Session,
        campaign: Campaign,
        platforms: List[str]
    ) -> List[CampaignContent]:
        """
        Generate AI content for platforms
        
        Args:
            db: Database session
            campaign: Campaign instance
            platforms: List of platform names
            
        Returns:
            List of generated campaign content
            
        Raises:
            HTTPException: If AI generation fails
        """
        track = campaign.track
        user = campaign.user
        template = campaign.template
        
        ai_service = AIService()
        generated_content = []
        
        # Generate hashtags once (shared across platforms)
        try:
            hashtags_data = ai_service.generate_hashtags(
                track_title=track.title,
                artist_name=track.artist_name,
                genre=track.genre,
                location=None  # Could get from user profile if needed
            )
            # Combine all hashtag categories
            all_hashtags = []
            for category in ['genre', 'trending', 'location', 'campaign']:
                all_hashtags.extend(hashtags_data.get(category, []))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate hashtags: {str(e)}"
            )
        
        # Generate content for each platform
        for platform in platforms:
            try:
                # Determine mood from track
                mood = None
                if track.mood_tags and len(track.mood_tags) > 0:
                    mood = track.mood_tags[0]
                
                # Generate captions
                captions_response = ai_service.generate_social_captions(
                    track_title=track.title,
                    artist_name=track.artist_name,
                    genre=track.genre,
                    mood=mood,
                    platform=platform
                )
                
                # Select primary caption (first one, typically "hype" tone)
                primary_caption = captions_response[0] if captions_response else {}
                caption_text = primary_caption.get('caption', '')
                caption_tone = primary_caption.get('tone', 'hype')
                
                # Determine content type based on platform
                content_type_map = {
                    'instagram': ContentType.INSTAGRAM_FEED,
                    'tiktok': ContentType.TIKTOK_VIDEO,
                    'twitter': ContentType.TWITTER_TWEET,
                    'facebook': ContentType.FACEBOOK_POST
                }
                
                # Create content record
                content = CampaignContent(
                    id=str(uuid.uuid4()),
                    campaign_id=campaign.id,
                    platform=Platform(platform),
                    content_type=content_type_map.get(platform, ContentType.INSTAGRAM_FEED),
                    caption=caption_text,
                    hashtags=all_hashtags[:15],  # Limit hashtags
                    ai_generated_caption=caption_text,
                    caption_tone=caption_tone,
                    content_edited=False,
                    posting_status="pending"
                )
                
                db.add(content)
                generated_content.append(content)
                
            except Exception as e:
                # Log error but continue with other platforms
                print(f"❌ Failed to generate content for {platform}: {e}")
                continue
        
        if not generated_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate content for any platform"
            )
        
        # Log activity
        CampaignService.log_activity(
            db=db,
            campaign_id=campaign.id,
            user_id=campaign.user_id,
            action="content_generated",
            details={"platforms": platforms, "content_count": len(generated_content)}
        )
        
        db.commit()
        
        return generated_content
    
    @staticmethod
    def update_campaign(
        db: Session,
        campaign: Campaign,
        update_data: CampaignUpdateRequest
    ) -> Campaign:
        """
        Update campaign details
        
        Args:
            db: Database session
            campaign: Campaign instance
            update_data: Update data
            
        Returns:
            Updated campaign
            
        Raises:
            HTTPException: If validation fails
        """
        # Only DRAFT or SCHEDULED campaigns can be edited
        if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot edit campaign with status: {campaign.status}"
            )
        
        # Update fields
        if update_data.name:
            campaign.name = update_data.name
        
        if update_data.scheduled_publish_time:
            campaign.scheduled_publish_time = update_data.scheduled_publish_time
        
        if update_data.platforms:
            old_platforms = set(campaign.platforms)
            new_platforms = set(update_data.platforms)
            campaign.platforms = update_data.platforms
            
            # If platforms added, generate content for them
            added_platforms = new_platforms - old_platforms
            if added_platforms:
                CampaignService.generate_content(db, campaign, list(added_platforms))
        
        # Log activity
        CampaignService.log_activity(
            db=db,
            campaign_id=campaign.id,
            user_id=campaign.user_id,
            action="edited",
            details={
                "name": update_data.name,
                "scheduled_time": str(update_data.scheduled_publish_time) if update_data.scheduled_publish_time else None
            }
        )
        
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def schedule_campaign(
        db: Session,
        campaign: Campaign,
        scheduled_time: datetime
    ) -> Campaign:
        """
        Schedule campaign for future publication
        
        Args:
            db: Database session
            campaign: Campaign instance
            scheduled_time: When to publish
            
        Returns:
            Updated campaign
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate future time
        if scheduled_time <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Scheduled time must be in the future"
            )
        
        # Update campaign
        campaign.status = CampaignStatus.SCHEDULED
        campaign.scheduled_publish_time = scheduled_time
        
        # Log activity
        CampaignService.log_activity(
            db=db,
            campaign_id=campaign.id,
            user_id=campaign.user_id,
            action="scheduled",
            details={"scheduled_time": str(scheduled_time)}
        )
        
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def publish_campaign(
        db: Session,
        campaign: Campaign
    ) -> Campaign:
        """
        Publish campaign immediately
        
        Args:
            db: Database session
            campaign: Campaign instance
            
        Returns:
            Updated campaign
        """
        campaign.status = CampaignStatus.ACTIVE
        campaign.published_at = datetime.now(timezone.utc)
        
        # Log activity
        CampaignService.log_activity(
            db=db,
            campaign_id=campaign.id,
            user_id=campaign.user_id,
            action="published",
            details={"published_at": str(campaign.published_at)}
        )
        
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def cancel_campaign(
        db: Session,
        campaign: Campaign
    ) -> Campaign:
        """
        Cancel active or scheduled campaign
        
        Args:
            db: Database session
            campaign: Campaign instance
            
        Returns:
            Updated campaign
            
        Raises:
            HTTPException: If campaign cannot be cancelled
        """
        if campaign.status not in [CampaignStatus.ACTIVE, CampaignStatus.SCHEDULED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel campaign with status: {campaign.status}"
            )
        
        old_status = campaign.status
        campaign.status = CampaignStatus.CANCELLED
        campaign.cancelled_at = datetime.now(timezone.utc)
        
        # Log activity
        CampaignService.log_activity(
            db=db,
            campaign_id=campaign.id,
            user_id=campaign.user_id,
            action="cancelled",
            details={"old_status": old_status.value}
        )
        
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def complete_campaign(
        db: Session,
        campaign: Campaign
    ) -> Campaign:
        """
        Mark campaign as completed
        
        Args:
            db: Database session
            campaign: Campaign instance
            
        Returns:
            Updated campaign
        """
        campaign.status = CampaignStatus.COMPLETED
        campaign.completed_at = datetime.now(timezone.utc)
        
        # Log activity
        CampaignService.log_activity(
            db=db,
            campaign_id=campaign.id,
            user_id=campaign.user_id,
            action="completed",
            details={"completed_at": str(campaign.completed_at)}
        )
        
        db.commit()
        db.refresh(campaign)
        
        return campaign
    
    @staticmethod
    def delete_campaign(
        db: Session,
        campaign: Campaign
    ) -> None:
        """
        Delete campaign (cascade deletes content and logs)
        
        Args:
            db: Database session
            campaign: Campaign instance
            
        Raises:
            HTTPException: If campaign cannot be deleted
        """
        # Only DRAFT, CANCELLED, or COMPLETED campaigns can be deleted
        if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.CANCELLED, CampaignStatus.COMPLETED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete campaign with status: {campaign.status}"
            )
        
        campaign_id = campaign.id
        user_id = campaign.user_id
        
        # Delete (cascade will handle content and logs)
        db.delete(campaign)
        db.commit()
        
        print(f"✅ Deleted campaign {campaign_id}")
    
    @staticmethod
    def duplicate_campaign(
        db: Session,
        user: User,
        source_campaign: Campaign
    ) -> Campaign:
        """
        Duplicate existing campaign
        
        Args:
            db: Database session
            user: Current user
            source_campaign: Campaign to duplicate
            
        Returns:
            New campaign
            
        Raises:
            HTTPException: If validation fails
        """
        # Verify ownership
        if source_campaign.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't own this campaign"
            )
        
        # Create new campaign with copied data
        new_campaign = Campaign(
            id=str(uuid.uuid4()),
            user_id=user.id,
            track_id=source_campaign.track_id,
            template_id=source_campaign.template_id,
            name=f"{source_campaign.name} (Copy)",
            status=CampaignStatus.DRAFT,
            platforms=source_campaign.platforms.copy()
        )
        
        db.add(new_campaign)
        db.flush()
        
        # Log activity
        CampaignService.log_activity(
            db=db,
            campaign_id=new_campaign.id,
            user_id=user.id,
            action="duplicated",
            details={"source_campaign_id": source_campaign.id}
        )
        
        db.commit()
        db.refresh(new_campaign)
        
        return new_campaign
    
    @staticmethod
    def get_user_campaigns(
        db: Session,
        user_id: str,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Campaign], int]:
        """
        Get filtered list of user's campaigns
        
        Args:
            db: Database session
            user_id: User ID
            status: Filter by status
            platform: Filter by platform
            search: Search by name or track title
            limit: Number of results
            offset: Pagination offset
            
        Returns:
            Tuple of (campaigns list, total count)
        """
        # Base query
        query = db.query(Campaign).filter(Campaign.user_id == user_id)
        
        # Apply filters
        if status:
            query = query.filter(Campaign.status == status)
        
        if platform:
            query = query.filter(Campaign.platforms.contains([platform]))
        
        if search:
            # Join with Track to search track titles
            query = query.join(Track, Campaign.track_id == Track.id)
            query = query.filter(
                or_(
                    Campaign.name.ilike(f"%{search}%"),
                    Track.title.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and order
        campaigns = query.order_by(Campaign.created_at.desc()).offset(offset).limit(limit).all()
        
        return campaigns, total
    
    @staticmethod
    def update_content(
        db: Session,
        content: CampaignContent,
        update_data: ContentUpdateRequest
    ) -> CampaignContent:
        """
        Update platform content
        
        Args:
            db: Database session
            content: CampaignContent instance
            update_data: Update data
            
        Returns:
            Updated content
        """
        if update_data.caption is not None:
            content.caption = update_data.caption
            content.content_edited = True
        
        if update_data.hashtags is not None:
            content.hashtags = update_data.hashtags
            content.content_edited = True
        
        if update_data.caption_tone:
            content.caption_tone = update_data.caption_tone
        
        db.commit()
        db.refresh(content)
        
        return content
    
    @staticmethod
    def generate_campaign_name(
        track_title: str,
        template_name: Optional[str] = None
    ) -> str:
        """
        Generate campaign name
        
        Args:
            track_title: Track title
            template_name: Template name (optional)
            
        Returns:
            Generated campaign name
        """
        if template_name:
            name = f"{template_name} - {track_title}"
        else:
            name = f"Campaign - {track_title}"
        
        # Truncate if too long
        if len(name) > 100:
            # Keep template/prefix and truncate track title
            if template_name:
                max_title_len = 100 - len(template_name) - 6  # " - " + "..."
                name = f"{template_name} - {track_title[:max_title_len]}..."
            else:
                name = f"Campaign - {track_title[:87]}..."
        
        return name
    
    @staticmethod
    def log_activity(
        db: Session,
        campaign_id: str,
        user_id: str,
        action: str,
        details: Optional[Dict] = None
    ) -> None:
        """
        Log campaign activity
        
        Args:
            db: Database session
            campaign_id: Campaign ID
            user_id: User ID
            action: Action type
            details: Additional details
        """
        log = CampaignActivityLog(
            id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            user_id=user_id,
            action=action,
            details=details or {}
        )
        db.add(log)
        # Don't commit here, let caller handle commit
