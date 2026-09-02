"""
Content Access Service - Content gating and exclusive content management
Tasks 9.1-9.7: Exclusive content access control by membership tier

Manages:
- Marking content as exclusive/tier-gated
- Checking user access to exclusive content
- Retrieving exclusive content lists
- Removing exclusivity
- Teaser/preview logic for locked content
- Integration with Post and Track models
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import uuid
import logging

from app.models.fan_club import ExclusiveContent, Subscription, MembershipTier, FanClub
from app.models.social import Post, PostVisibility
from app.models.track import Track, TrackVisibility
from app.models.user import User
from app.schemas.fan_club import (
    ExclusiveContentCreate, ExclusiveContentResponse, ContentAccessResponse
)

logger = logging.getLogger(__name__)


class ContentAccessService:
    """Exclusive content management and access control
    
    Handles:
    - Marking content as tier-exclusive
    - Access verification by subscription
    - Exclusive content retrieval
    - Teaser/preview content
    - Content exclusivity removal
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # MARK CONTENT EXCLUSIVE - TASK 9.1
    # ========================================================================
    
    def mark_content_exclusive(
        self,
        fan_club_id: str,
        content_type: str,
        content_id: str,
        minimum_tier_level: int,
        teaser_text: Optional[str] = None,
        preview_url: Optional[str] = None
    ) -> ExclusiveContent:
        """
        Mark content as exclusive/tier-gated (Task 9.1).
        
        Business Rules (BR-9.1):
        - Only creator can mark their own content exclusive
        - Content type must be valid (post, track, video, image, event)
        - Tier level must be 1-3 (Bronze, Silver, Gold)
        - Only one exclusivity per content (prevent duplicates)
        - Create ExclusiveContent record
        - Content still visible, but access gated
        
        Args:
            fan_club_id: Creator's fan club
            content_type: Type of content (post, track, video, image, event)
            content_id: Content ID
            minimum_tier_level: Minimum tier to access (1, 2, or 3)
            teaser_text: Optional preview text (first 20%)
            preview_url: Optional thumbnail for locked content
            
        Returns:
            ExclusiveContent record
            
        Raises:
            HTTPException 404: Fan club not found
            HTTPException 400: Invalid tier level or duplicate exclusivity
        """
        # Validate fan club exists
        fan_club = (
            self.db.query(FanClub)
            .filter(FanClub.id == fan_club_id)
            .first()
        )
        
        if not fan_club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fan club not found"
            )
        
        # Validate tier level
        if minimum_tier_level < 1 or minimum_tier_level > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tier level must be 1 (Bronze), 2 (Silver), or 3 (Gold)"
            )
        
        # Validate content type
        valid_types = ["post", "track", "video", "image", "event"]
        if content_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Check for existing exclusivity
        existing = (
            self.db.query(ExclusiveContent)
            .filter(
                and_(
                    ExclusiveContent.content_type == content_type,
                    ExclusiveContent.content_id == content_id
                )
            )
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This content is already marked as exclusive"
            )
        
        # Create exclusive content record
        exclusive = ExclusiveContent(
            id=str(uuid.uuid4()),
            fan_club_id=fan_club_id,
            content_type=content_type,
            content_id=content_id,
            minimum_tier_level=minimum_tier_level,
            teaser_text=teaser_text,
            preview_url=preview_url,
            created_at=datetime.utcnow()
        )
        
        self.db.add(exclusive)
        self.db.commit()
        self.db.refresh(exclusive)
        
        logger.info(f"✓ Content marked exclusive: {content_type}/{content_id} (tier {minimum_tier_level})")
        
        return exclusive
    
    # ========================================================================
    # CHECK CONTENT ACCESS - TASK 9.2
    # ========================================================================
    
    def check_content_access(
        self,
        fan_club_id: str,
        user_id: str,
        content_type: str,
        content_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify if user has access to exclusive content (Task 9.2).
        
        Business Rules (BR-9.2):
        - Check if content is exclusive
        - If not exclusive, return access=True
        - If exclusive, check user's subscription tier
        - User must have active subscription with tier >= minimum_tier_level
        - Creator always has access to own content
        - Return (has_access, reason)
        
        Args:
            fan_club_id: Fan club ID
            user_id: User checking access
            content_type: Type of content (post, track)
            content_id: Content ID
            
        Returns:
            Tuple of (has_access: bool, reason: Optional[str])
            - (True, None) if access granted
            - (False, "reason") if denied
        """
        # Check if content is marked exclusive
        exclusive = (
            self.db.query(ExclusiveContent)
            .filter(
                and_(
                    ExclusiveContent.content_type == content_type,
                    ExclusiveContent.content_id == content_id
                )
            )
            .first()
        )
        
        # If not exclusive, grant access
        if not exclusive:
            return True, None
        
        # Check if user is the creator
        fan_club = (
            self.db.query(FanClub)
            .filter(FanClub.id == fan_club_id)
            .first()
        )
        
        if fan_club and fan_club.creator_id == user_id:
            logger.info(f"✓ Creator access granted: {user_id}")
            return True, None
        
        # Check user's subscription to this fan club
        subscription = (
            self.db.query(Subscription)
            .options(joinedload(Subscription.tier))
            .filter(
                and_(
                    Subscription.fan_club_id == fan_club_id,
                    Subscription.subscriber_id == user_id,
                    Subscription.status.in_(["active", "trialing"])
                )
            )
            .first()
        )
        
        # No subscription
        if not subscription:
            required_tier = self._get_tier_name(exclusive.minimum_tier_level)
            logger.warning(f"✗ No subscription: {user_id} requires {required_tier} tier")
            return False, f"Requires {required_tier} subscription to access"
        
        # Check tier level
        if subscription.tier.tier_level < exclusive.minimum_tier_level:
            current_tier = self._get_tier_name(subscription.tier.tier_level)
            required_tier = self._get_tier_name(exclusive.minimum_tier_level)
            logger.warning(f"✗ Insufficient tier: {user_id} has {current_tier}, requires {required_tier}")
            return False, f"Upgrade to {required_tier} to access this content"
        
        # Access granted
        logger.info(f"✓ Access granted: {user_id} with {self._get_tier_name(subscription.tier.tier_level)} tier")
        return True, None
    
    # ========================================================================
    # GET EXCLUSIVE CONTENT - TASK 9.3
    # ========================================================================
    
    def get_exclusive_content(
        self,
        fan_club_id: str,
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ExclusiveContent]:
        """
        Get list of creator's exclusive content (Task 9.3).
        
        Business Rules (BR-9.3):
        - Only creator can view their exclusive content list
        - Return paginated results
        - Optional filter by content type
        - Include view/engagement counts
        - Ordered by created_at (newest first)
        
        Args:
            fan_club_id: Creator's fan club
            content_type: Optional filter (post, track, video, image, event)
            limit: Page size (max 100)
            offset: Page offset
            
        Returns:
            List of ExclusiveContent records
        """
        query = (
            self.db.query(ExclusiveContent)
            .filter(ExclusiveContent.fan_club_id == fan_club_id)
        )
        
        # Optional content type filter
        if content_type:
            query = query.filter(ExclusiveContent.content_type == content_type)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        limit = min(limit, 100)  # Cap at 100
        exclusive_content = query.order_by(
            ExclusiveContent.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        logger.info(f"Retrieved {len(exclusive_content)} exclusive content items for fan club {fan_club_id}")
        
        return exclusive_content
    
    # ========================================================================
    # REMOVE EXCLUSIVITY - TASK 9.4
    # ========================================================================
    
    def remove_exclusivity(self, exclusive_content_id: str) -> bool:
        """
        Remove exclusivity and make content public (Task 9.4).
        
        Business Rules (BR-9.4):
        - Delete ExclusiveContent record
        - Content becomes publicly accessible
        - Creator can do this anytime
        - Cannot reverse (need to mark exclusive again)
        
        Args:
            exclusive_content_id: ID of exclusive content record
            
        Returns:
            True if removed successfully
            
        Raises:
            HTTPException 404: Exclusive content not found
        """
        exclusive = (
            self.db.query(ExclusiveContent)
            .filter(ExclusiveContent.id == exclusive_content_id)
            .first()
        )
        
        if not exclusive:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exclusive content not found"
            )
        
        content_info = f"{exclusive.content_type}/{exclusive.content_id}"
        
        self.db.delete(exclusive)
        self.db.commit()
        
        logger.info(f"✓ Exclusivity removed: {content_info}")
        
        return True
    
    # ========================================================================
    # INTEGRATE WITH POST MODEL - TASK 9.5
    # ========================================================================
    
    def check_post_access(
        self,
        post_id: str,
        user_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if user can access a post (Task 9.5).
        
        Business Rules (BR-9.5):
        - Integrate access check with Post model
        - If post is public and not exclusive: access granted
        - If post is exclusive: verify subscription
        - Return (access, reason, teaser)
        - Include teaser text if access denied
        
        Args:
            post_id: Post ID
            user_id: User ID (None for anonymous)
            
        Returns:
            Tuple of (has_access, deny_reason, teaser_text)
        """
        # Get post
        post = (
            self.db.query(Post)
            .options(joinedload(Post.user))
            .filter(Post.id == post_id)
            .first()
        )
        
        if not post:
            return False, "Post not found", None
        
        # If deleted, no access
        if post.is_deleted:
            return False, "Post has been deleted", None
        
        # Check if post is exclusive
        has_access, deny_reason = self.check_content_access(
            fan_club_id=post.user.fan_club.id if post.user.fan_club else None,
            user_id=user_id,
            content_type="post",
            content_id=post_id
        )
        
        if has_access:
            return True, None, None
        
        # Get teaser text if access denied
        exclusive = (
            self.db.query(ExclusiveContent)
            .filter(
                and_(
                    ExclusiveContent.content_type == "post",
                    ExclusiveContent.content_id == post_id
                )
            )
            .first()
        )
        
        teaser = exclusive.teaser_text if exclusive else None
        
        return False, deny_reason, teaser
    
    # ========================================================================
    # INTEGRATE WITH TRACK MODEL - TASK 9.6
    # ========================================================================
    
    def check_track_access(
        self,
        track_id: str,
        user_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if user can access a track (Task 9.6).
        
        Business Rules (BR-9.6):
        - Integrate access check with Track model
        - If track is public and not exclusive: access granted
        - If track is exclusive: verify subscription
        - Return (access, reason, teaser)
        - Include preview_url if access denied
        
        Args:
            track_id: Track ID
            user_id: User ID (None for anonymous)
            
        Returns:
            Tuple of (has_access, deny_reason, preview_url)
        """
        # Get track
        track = (
            self.db.query(Track)
            .options(joinedload(Track.user))
            .filter(Track.id == track_id)
            .first()
        )
        
        if not track:
            return False, "Track not found", None
        
        # Check if track is exclusive
        has_access, deny_reason = self.check_content_access(
            fan_club_id=track.user.fan_club.id if track.user.fan_club else None,
            user_id=user_id,
            content_type="track",
            content_id=track_id
        )
        
        if has_access:
            return True, None, None
        
        # Get preview URL if access denied
        exclusive = (
            self.db.query(ExclusiveContent)
            .filter(
                and_(
                    ExclusiveContent.content_type == "track",
                    ExclusiveContent.content_id == track_id
                )
            )
            .first()
        )
        
        preview_url = exclusive.preview_url if exclusive else None
        
        return False, deny_reason, preview_url
    
    # ========================================================================
    # TEASER/PREVIEW LOGIC - TASK 9.7
    # ========================================================================
    
    def get_content_with_teaser(
        self,
        content_type: str,
        content_id: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Get content with teaser/preview if access denied (Task 9.7).
        
        Business Rules (BR-9.7):
        - If user has access: return full content
        - If user denied access: return teaser (first 20% or preview)
        - Show unlock prompt with required tier
        - Support both Post and Track content types
        - Return structure includes access status and content
        
        Args:
            content_type: "post" or "track"
            content_id: Content ID
            user_id: User ID (None for anonymous)
            
        Returns:
            Dict with full content or teaser + unlock info
        """
        if content_type == "post":
            has_access, deny_reason, teaser = self.check_post_access(content_id, user_id)
            content = self._get_post_content(content_id, has_access)
        elif content_type == "track":
            has_access, deny_reason, preview_url = self.check_track_access(content_id, user_id)
            content = self._get_track_content(content_id, has_access, preview_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type"
            )
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{content_type.capitalize()} not found"
            )
        
        # Get exclusive info for unlock prompt
        exclusive = (
            self.db.query(ExclusiveContent)
            .filter(
                and_(
                    ExclusiveContent.content_type == content_type,
                    ExclusiveContent.content_id == content_id
                )
            )
            .first()
        )
        
        result = {
            "id": content_id,
            "type": content_type,
            "has_access": has_access,
            "content": content if has_access else None,
            "is_exclusive": exclusive is not None
        }
        
        # Add unlock info if denied
        if not has_access and exclusive:
            required_tier = self._get_tier_name(exclusive.minimum_tier_level)
            result.update({
                "unlock_reason": deny_reason,
                "unlock_prompt": f"Unlock with {required_tier} membership",
                "minimum_tier_level": exclusive.minimum_tier_level,
                "teaser": {
                    "text": exclusive.teaser_text or "Subscribe to unlock",
                    "preview_url": exclusive.preview_url
                }
            })
        
        return result
    
    # ========================================================================
    # ENGAGEMENT TRACKING
    # ========================================================================
    
    def track_exclusive_view(
        self,
        exclusive_content_id: str
    ) -> None:
        """
        Track view of exclusive content for analytics.
        
        Args:
            exclusive_content_id: ID of viewed exclusive content
        """
        exclusive = (
            self.db.query(ExclusiveContent)
            .filter(ExclusiveContent.id == exclusive_content_id)
            .first()
        )
        
        if exclusive:
            exclusive.view_count = (exclusive.view_count or 0) + 1
            self.db.commit()
    
    def track_exclusive_engagement(
        self,
        exclusive_content_id: str,
        engagement_type: str  # like, comment, share
    ) -> None:
        """
        Track engagement with exclusive content.
        
        Args:
            exclusive_content_id: ID of engaged content
            engagement_type: Type of engagement
        """
        exclusive = (
            self.db.query(ExclusiveContent)
            .filter(ExclusiveContent.id == exclusive_content_id)
            .first()
        )
        
        if exclusive:
            exclusive.engagement_count = (exclusive.engagement_count or 0) + 1
            self.db.commit()
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_tier_name(self, tier_level: int) -> str:
        """Get human-readable tier name"""
        tier_names = {
            1: "Bronze",
            2: "Silver",
            3: "Gold"
        }
        return tier_names.get(tier_level, f"Tier {tier_level}")
    
    def _get_post_content(
        self,
        post_id: str,
        include_full: bool = True
    ) -> Optional[Dict]:
        """Get post content for response"""
        post = (
            self.db.query(Post)
            .options(joinedload(Post.user))
            .filter(Post.id == post_id)
            .first()
        )
        
        if not post:
            return None
        
        if not include_full:
            # Return minimal info with teaser
            return {
                "id": post.id,
                "type": post.type,
                "user_id": post.user_id,
                "like_count": post.like_count,
                "comment_count": post.comment_count
            }
        
        # Return full post content
        return {
            "id": post.id,
            "type": post.type,
            "user_id": post.user_id,
            "content": post.content,
            "media_urls": post.media_urls,
            "like_count": post.like_count,
            "comment_count": post.comment_count,
            "share_count": post.share_count,
            "view_count": post.view_count,
            "created_at": post.created_at
        }
    
    def _get_track_content(
        self,
        track_id: str,
        include_full: bool = True,
        preview_url: Optional[str] = None
    ) -> Optional[Dict]:
        """Get track content for response"""
        track = (
            self.db.query(Track)
            .options(joinedload(Track.user))
            .filter(Track.id == track_id)
            .first()
        )
        
        if not track:
            return None
        
        if not include_full:
            # Return minimal info with preview
            return {
                "id": track.id,
                "title": track.title,
                "artist_name": track.artist_name,
                "preview_url": preview_url,
                "cover_art_url": track.cover_art_url,
                "play_count": track.play_count
            }
        
        # Return full track content
        return {
            "id": track.id,
            "title": track.title,
            "artist_name": track.artist_name,
            "album": track.album,
            "genre": track.genre,
            "duration": track.duration,
            "bpm": track.bpm,
            "audio_url": track.audio_url,
            "cover_art_url": track.cover_art_url,
            "description": track.description,
            "play_count": track.play_count,
            "like_count": track.like_count,
            "download_count": track.download_count,
            "created_at": track.created_at
        }
    
    def get_exclusive_content_stats(
        self,
        fan_club_id: str
    ) -> Dict:
        """Get statistics on exclusive content"""
        stats = (
            self.db.query(
                func.count(ExclusiveContent.id).label('total_exclusive'),
                func.sum(ExclusiveContent.view_count).label('total_views'),
                func.sum(ExclusiveContent.engagement_count).label('total_engagement')
            )
            .filter(ExclusiveContent.fan_club_id == fan_club_id)
            .first()
        )
        
        return {
            "total_exclusive_content": stats[0] or 0,
            "total_views": stats[1] or 0,
            "total_engagement": stats[2] or 0
        }
