"""
Content Access Service - Business logic for exclusive content gating
Tasks 9.1-9.7: Content access control and tier validation
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import uuid

from app.models.fan_club import (
    ExclusiveContent, FanClub, Subscription, MembershipTier
)
from app.models.social import Post
from app.models.track import Track
from app.schemas.fan_club import (
    ExclusiveContentCreate, ExclusiveContentResponse,
    ContentAccessResponse
)


class ContentAccessService:
    """Service for managing exclusive content access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # CONTENT GATING
    # ========================================================================
    
    def mark_content_exclusive(
        self,
        creator_id: str,
        data: ExclusiveContentCreate
    ) -> ExclusiveContent:
        """
        Mark content as tier-exclusive
        
        Args:
            creator_id: Creator user ID
            data: Exclusive content data
            
        Returns:
            ExclusiveContent object
        """
        # Get creator's fan club
        fan_club = (
            self.db.query(FanClub)
            .filter(FanClub.creator_id == creator_id)
            .first()
        )
        
        if not fan_club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You don't have a fan club. Create one first."
            )
        
        if not fan_club.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your fan club is not active"
            )
        
        # Verify tier level exists
        tier = (
            self.db.query(MembershipTier)
            .filter(
                MembershipTier.fan_club_id == fan_club.id,
                MembershipTier.tier_level == data.minimum_tier_level,
                MembershipTier.is_active == True
            )
            .first()
        )
        
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No active tier at level {data.minimum_tier_level} found"
            )
        
        # Verify content exists and creator owns it
        self._verify_content_ownership(
            content_type=data.content_type.value,
            content_id=data.content_id,
            creator_id=creator_id
        )
        
        # Check if content is already exclusive
        existing = (
            self.db.query(ExclusiveContent)
            .filter(
                ExclusiveContent.content_type == data.content_type.value,
                ExclusiveContent.content_id == data.content_id
            )
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This content is already marked as exclusive"
            )
        
        # Generate teaser if not provided
        teaser_text = data.teaser_text
        if not teaser_text:
            teaser_text = self._generate_teaser(
                content_type=data.content_type.value,
                content_id=data.content_id
            )
        
        # Create exclusive content record
        exclusive_content = ExclusiveContent(
            id=str(uuid.uuid4()),
            fan_club_id=fan_club.id,
            content_type=data.content_type.value,
            content_id=data.content_id,
            minimum_tier_level=data.minimum_tier_level,
            teaser_text=teaser_text,
            preview_url=data.preview_url,
            view_count=0,
            engagement_count=0
        )
        
        self.db.add(exclusive_content)
        self.db.commit()
        self.db.refresh(exclusive_content)
        
        return exclusive_content
    
    def remove_exclusivity(
        self,
        content_type: str,
        content_id: str,
        creator_id: str
    ) -> bool:
        """
        Remove exclusive status from content (make public)
        
        Args:
            content_type: Type of content
            content_id: Content ID
            creator_id: Creator user ID (for authorization)
            
        Returns:
            True if removed successfully
        """
        exclusive_content = (
            self.db.query(ExclusiveContent)
            .filter(
                ExclusiveContent.content_type == content_type,
                ExclusiveContent.content_id == content_id
            )
            .first()
        )
        
        if not exclusive_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exclusive content record not found"
            )
        
        # Verify creator owns the fan club
        fan_club = (
            self.db.query(FanClub)
            .filter(FanClub.id == exclusive_content.fan_club_id)
            .first()
        )
        
        if not fan_club or fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this content"
            )
        
        self.db.delete(exclusive_content)
        self.db.commit()
        
        return True
    
    # ========================================================================
    # ACCESS CHECKS
    # ========================================================================
    
    def check_content_access(
        self,
        user_id: str,
        content_type: str,
        content_id: str
    ) -> ContentAccessResponse:
        """
        Check if user has access to exclusive content
        
        Args:
            user_id: User ID
            content_type: Type of content (post, track, video, etc.)
            content_id: Content ID
            
        Returns:
            ContentAccessResponse with access decision
        """
        # Check if content is exclusive
        exclusive_content = (
            self.db.query(ExclusiveContent)
            .filter(
                ExclusiveContent.content_type == content_type,
                ExclusiveContent.content_id == content_id
            )
            .first()
        )
        
        # Content is public (not exclusive)
        if not exclusive_content:
            return ContentAccessResponse(
                has_access=True,
                reason=None,
                required_tier_level=None,
                current_tier_level=None,
                unlock_url=None
            )
        
        # Check if user is the creator (creators always have access to their own content)
        fan_club = (
            self.db.query(FanClub)
            .filter(FanClub.id == exclusive_content.fan_club_id)
            .first()
        )
        
        if fan_club and fan_club.creator_id == user_id:
            return ContentAccessResponse(
                has_access=True,
                reason="Creator access",
                required_tier_level=exclusive_content.minimum_tier_level,
                current_tier_level=999,  # Creator has highest level
                unlock_url=None
            )
        
        # Check if user has active subscription at required tier level
        subscription = (
            self.db.query(Subscription)
            .join(MembershipTier, Subscription.tier_id == MembershipTier.id)
            .filter(
                Subscription.fan_club_id == exclusive_content.fan_club_id,
                Subscription.subscriber_id == user_id,
                Subscription.status.in_(["active", "trialing"]),
                MembershipTier.tier_level >= exclusive_content.minimum_tier_level
            )
            .first()
        )
        
        if subscription:
            # User has access
            return ContentAccessResponse(
                has_access=True,
                reason=None,
                required_tier_level=exclusive_content.minimum_tier_level,
                current_tier_level=subscription.tier.tier_level,
                unlock_url=None
            )
        
        # User doesn't have access - check if they have lower tier
        lower_tier_sub = (
            self.db.query(Subscription)
            .join(MembershipTier, Subscription.tier_id == MembershipTier.id)
            .filter(
                Subscription.fan_club_id == exclusive_content.fan_club_id,
                Subscription.subscriber_id == user_id,
                Subscription.status.in_(["active", "trialing"])
            )
            .first()
        )
        
        if lower_tier_sub:
            # User has subscription but lower tier
            current_tier = lower_tier_sub.tier.tier_level
            reason = f"This content requires tier level {exclusive_content.minimum_tier_level}. You have tier {current_tier}. Upgrade to access."
        else:
            # User not subscribed at all
            current_tier = 0
            reason = f"This content is exclusive to tier {exclusive_content.minimum_tier_level} members. Subscribe to unlock."
        
        return ContentAccessResponse(
            has_access=False,
            reason=reason,
            required_tier_level=exclusive_content.minimum_tier_level,
            current_tier_level=current_tier,
            unlock_url=f"/fan-clubs/{fan_club.id}/subscribe"
        )
    
    def get_exclusive_content(
        self,
        fan_club_id: str,
        tier_level: Optional[int] = None,
        content_type: Optional[str] = None
    ) -> List[ExclusiveContent]:
        """
        Get exclusive content for a fan club
        
        Args:
            fan_club_id: Fan club ID
            tier_level: Filter by tier level
            content_type: Filter by content type
            
        Returns:
            List of ExclusiveContent objects
        """
        query = (
            self.db.query(ExclusiveContent)
            .filter(ExclusiveContent.fan_club_id == fan_club_id)
        )
        
        if tier_level is not None:
            query = query.filter(ExclusiveContent.minimum_tier_level == tier_level)
        
        if content_type:
            query = query.filter(ExclusiveContent.content_type == content_type)
        
        # Order by most recent
        query = query.order_by(ExclusiveContent.created_at.desc())
        
        return query.all()
    
    # ========================================================================
    # CONTENT INTEGRATION
    # ========================================================================
    
    def get_content_with_access_check(
        self,
        user_id: str,
        content_type: str,
        content_id: str
    ) -> Dict:
        """
        Get content with access check applied
        
        Returns content with access information and teaser if locked
        
        Args:
            user_id: User ID
            content_type: Content type
            content_id: Content ID
            
        Returns:
            Dict with content and access info
        """
        # Check access
        access_response = self.check_content_access(user_id, content_type, content_id)
        
        # Get content
        content = self._get_content(content_type, content_id)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # If no access, return teaser only
        if not access_response.has_access:
            exclusive_content = (
                self.db.query(ExclusiveContent)
                .filter(
                    ExclusiveContent.content_type == content_type,
                    ExclusiveContent.content_id == content_id
                )
                .first()
            )
            
            return {
                "content": {
                    "id": content_id,
                    "type": content_type,
                    "teaser": exclusive_content.teaser_text if exclusive_content else "Exclusive content",
                    "preview_url": exclusive_content.preview_url if exclusive_content else None
                },
                "access": access_response.dict(),
                "locked": True
            }
        
        # User has access - return full content
        # Track view (increment view_count)
        self._increment_view_count(content_type, content_id)
        
        return {
            "content": self._serialize_content(content_type, content),
            "access": access_response.dict(),
            "locked": False
        }
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _verify_content_ownership(
        self,
        content_type: str,
        content_id: str,
        creator_id: str
    ) -> bool:
        """Verify creator owns the content"""
        if content_type == "post":
            content = self.db.query(Post).filter(Post.id == content_id).first()
            if not content or content.user_id != creator_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't own this post"
                )
        elif content_type == "track":
            content = self.db.query(Track).filter(Track.id == content_id).first()
            if not content or content.user_id != creator_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't own this track"
                )
        # Add more content types as needed (video, image, event)
        
        return True
    
    def _generate_teaser(self, content_type: str, content_id: str) -> str:
        """Generate teaser text (first 20% of content)"""
        if content_type == "post":
            post = self.db.query(Post).filter(Post.id == content_id).first()
            if post and post.content:
                teaser_length = len(post.content) // 5  # 20%
                teaser = post.content[:teaser_length]
                return teaser + "..." if len(post.content) > teaser_length else teaser
        
        return "Exclusive content for members only 🔒"
    
    def _get_content(self, content_type: str, content_id: str):
        """Get content object by type"""
        if content_type == "post":
            return self.db.query(Post).filter(Post.id == content_id).first()
        elif content_type == "track":
            return self.db.query(Track).filter(Track.id == content_id).first()
        # Add more content types
        return None
    
    def _serialize_content(self, content_type: str, content) -> Dict:
        """Serialize content to dict"""
        if content_type == "post":
            return {
                "id": content.id,
                "type": "post",
                "content": content.content,
                "created_at": content.created_at,
                "user_id": content.user_id
            }
        elif content_type == "track":
            return {
                "id": content.id,
                "type": "track",
                "title": content.title,
                "file_url": content.file_url,
                "created_at": content.created_at,
                "user_id": content.user_id
            }
        return {}
    
    def _increment_view_count(self, content_type: str, content_id: str):
        """Increment view count for exclusive content"""
        exclusive_content = (
            self.db.query(ExclusiveContent)
            .filter(
                ExclusiveContent.content_type == content_type,
                ExclusiveContent.content_id == content_id
            )
            .first()
        )
        
        if exclusive_content:
            exclusive_content.view_count += 1
            self.db.commit()
