"""
Fan Club Service - Business logic for fan club management
Tasks 4.1-4.6: Core fan club operations
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import Optional, Dict
from datetime import datetime
import uuid

from app.models.fan_club import FanClub, MembershipTier, Subscription
from app.models.user import User, UserRole
from app.schemas.fan_club import (
    FanClubCreate, FanClubUpdate, FanClubResponse,
    SubscriptionAnalytics
)
from decimal import Decimal


class FanClubService:
    """Core fan club service for creators"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # FAN CLUB MANAGEMENT
    # ========================================================================
    
    def create_fan_club(
        self,
        creator_id: str,
        data: FanClubCreate
    ) -> FanClub:
        """
        Create a new fan club for creator
        
        Business Rules (BR-4):
        - Creator must have verified account
        - Creator must have at least 100 followers
        - Creator must have at least 10 published tracks/posts
        - Creator must complete payout setup (bank account)
        - One fan club per creator (unique constraint)
        
        Args:
            creator_id: Creator user ID
            data: Fan club creation data
            
        Returns:
            Created FanClub object
            
        Raises:
            HTTPException 404: Creator not found
            HTTPException 403: Creator not eligible (with specific reason)
            HTTPException 400: Fan club already exists
        """
        # Import here to avoid circular dependency
        from app.models.social import Follow, Post
        from app.models.track import Track, TrackStatus
        
        # 1. Check if fan club already exists
        existing = (
            self.db.query(FanClub)
            .filter(FanClub.creator_id == creator_id)
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a fan club"
            )
        
        # 2. Validate creator exists
        creator = self.db.query(User).filter(User.id == creator_id).first()
        if not creator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Creator not found"
            )
        
        # 3. Check if creator is verified
        if not creator.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must have a verified account to create a fan club. Please complete account verification first."
            )
        
        # Check creator role eligibility
        if creator.role not in [UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only artists, DJs, and producers can create fan clubs"
            )
        
        # 4. Check follower count >= 100
        follower_count = (
            self.db.query(Follow)
            .filter(Follow.following_id == creator_id)
            .count()
        )
        
        if follower_count < 100:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You need at least 100 followers to create a fan club. You currently have {follower_count} followers."
            )
        
        # 5. Check published tracks >= 10
        published_tracks_count = (
            self.db.query(Track)
            .filter(
                Track.user_id == creator_id,
                Track.status == TrackStatus.PUBLISHED
            )
            .count()
        )
        
        published_posts_count = (
            self.db.query(Post)
            .filter(Post.user_id == creator_id)
            .count()
        )
        
        total_published_content = published_tracks_count + published_posts_count
        
        if total_published_content < 10:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You need at least 10 published tracks or posts to create a fan club. You currently have {total_published_content} ({published_tracks_count} tracks, {published_posts_count} posts)."
            )
        
        # 6. Check payout setup completed
        # Note: In a full implementation, this would check for payout_setup_completed
        # field or bank_account_verified field on the User model.
        # For now, we'll check if the user has basic payout information.
        # TODO: Add payout setup validation when User model includes payout fields
        
        # Placeholder for payout check - assumes verified creators have payout setup
        # In production, you would check:
        # if not creator.has_payout_setup:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="You must complete payout setup before creating a fan club. Please add your bank account details in settings."
        #     )
        
        # 7. Create fan club with UUID
        fan_club = FanClub(
            id=str(uuid.uuid4()),
            creator_id=creator_id,
            name=data.name,
            description=data.description,
            welcome_message=data.welcome_message or f"Welcome to {data.name}! 🎉",
            is_active=True,
            total_members=0,
            monthly_revenue=Decimal('0.00')
        )
        
        self.db.add(fan_club)
        self.db.commit()
        self.db.refresh(fan_club)
        
        # 8. Return created fan club
        return fan_club
    
    def get_fan_club(self, fan_club_id: str) -> FanClub:
        """
        Task 4.2: Retrieve fan club with tiers
        
        Steps:
        1. Query fan club by ID
        2. Eager load tiers relationship
        3. Raise 404 if not found
        4. Return fan club with tiers
        
        Args:
            fan_club_id: Fan club ID
            
        Returns:
            FanClub object with eager-loaded tiers
            
        Raises:
            HTTPException 404: Fan club not found
        """
        # Query with eager loading of tiers
        fan_club = (
            self.db.query(FanClub)
            .options(joinedload(FanClub.tiers))
            .filter(FanClub.id == fan_club_id)
            .first()
        )
        
        if not fan_club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fan club not found"
            )
        
        return fan_club
    
    def update_fan_club(
        self,
        fan_club_id: str,
        creator_id: str,
        data: FanClubUpdate
    ) -> FanClub:
        """
        Task 4.3: Update fan club details (name, description, welcome message)
        
        Steps:
        1. Get fan club
        2. Verify creator ownership
        3. Update only provided fields (exclude_unset=True)
        4. Commit changes
        5. Return updated fan club
        
        Args:
            fan_club_id: Fan club ID
            creator_id: Creator user ID (for authorization)
            data: Update data
            
        Returns:
            Updated FanClub object
            
        Raises:
            HTTPException 404: Fan club not found
            HTTPException 403: Not the owner
        """
        # 1. Get fan club
        fan_club = self.get_fan_club(fan_club_id=fan_club_id)
        
        # 2. Verify creator ownership
        if fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this fan club"
            )
        
        # 3. Update only provided fields (exclude_unset=True)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(fan_club, field, value)
        
        # Update timestamp
        fan_club.updated_at = datetime.utcnow()
        
        # 4. Commit changes
        self.db.commit()
        self.db.refresh(fan_club)
        
        # 5. Return updated fan club
        return fan_club
    
    def deactivate_fan_club(
        self,
        fan_club_id: str,
        creator_id: str
    ) -> None:
        """
        Task 4.4: Deactivate fan club (soft delete with validation)
        
        Steps:
        1. Get fan club
        2. Verify creator ownership
        3. Check for active subscriptions
        4. If active subscriptions exist, raise 400 error
        5. Set is_active=False
        6. Commit
        
        Args:
            fan_club_id: Fan club ID
            creator_id: Creator user ID (for authorization)
            
        Returns:
            None
            
        Raises:
            HTTPException 404: Fan club not found
            HTTPException 403: Not the owner
            HTTPException 400: Has active subscriptions
        """
        # 1. Get fan club
        fan_club = self.get_fan_club(fan_club_id=fan_club_id)
        
        # 2. Verify creator ownership
        if fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to deactivate this fan club"
            )
        
        # 3. Check for active subscriptions
        active_subs = (
            self.db.query(Subscription)
            .filter(
                Subscription.fan_club_id == fan_club_id,
                Subscription.status == "active"
            )
            .count()
        )
        
        # 4. If active subscriptions exist, raise 400
        if active_subs > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot deactivate fan club with {active_subs} active subscriptions. Cancel all subscriptions first."
            )
        
        # 5. Set is_active=False
        fan_club.is_active = False
        fan_club.updated_at = datetime.utcnow()
        
        # 6. Commit
        self.db.commit()
    
    def get_fan_club_stats(
        self,
        fan_club_id: str,
        creator_id: str
    ) -> dict:
        """
        Task 4.5: Get fan club statistics (total members, MRR, tier breakdown)
        
        Steps:
        1. Verify ownership
        2. Count active subscriptions
        3. Calculate MRR (sum of active subscription prices)
        4. Get tier breakdown (subscribers per tier)
        5. Return stats dict
        
        Args:
            fan_club_id: Fan club ID
            creator_id: Creator user ID (for authorization)
            
        Returns:
            Dictionary with structure:
            {
                "total_members": int,
                "active_subscriptions": int,
                "mrr": Decimal,
                "tier_breakdown": List[dict]
            }
            
        Raises:
            HTTPException 404: Fan club not found
            HTTPException 403: Not the owner
        """
        # 1. Verify ownership
        fan_club = self.get_fan_club(fan_club_id=fan_club_id)
        
        if fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this fan club's stats"
            )
        
        # 2. Count active subscriptions and get them
        active_subscriptions = (
            self.db.query(Subscription)
            .filter(
                Subscription.fan_club_id == fan_club_id,
                Subscription.status == "active"
            )
            .all()
        )
        
        total_members = len(active_subscriptions)
        
        # 3. Calculate MRR (Monthly Recurring Revenue)
        mrr = Decimal('0.00')
        for sub in active_subscriptions:
            if sub.billing_cycle == "monthly":
                mrr += sub.price_paid
            elif sub.billing_cycle == "yearly":
                # Convert yearly to monthly equivalent
                mrr += sub.price_paid / 12
        
        # 4. Get tier breakdown (subscribers per tier)
        tier_breakdown_query = (
            self.db.query(
                MembershipTier.id,
                MembershipTier.name,
                MembershipTier.tier_level,
                func.count(Subscription.id).label('subscriber_count')
            )
            .join(Subscription, Subscription.tier_id == MembershipTier.id)
            .filter(
                Subscription.fan_club_id == fan_club_id,
                Subscription.status == "active"
            )
            .group_by(MembershipTier.id, MembershipTier.name, MembershipTier.tier_level)
            .order_by(MembershipTier.tier_level)
            .all()
        )
        
        tier_breakdown = [
            {
                "tier_id": tier_id,
                "tier_name": tier_name,
                "tier_level": tier_level,
                "subscriber_count": subscriber_count
            }
            for tier_id, tier_name, tier_level, subscriber_count in tier_breakdown_query
        ]
        
        # 5. Return stats dict
        return {
            "total_members": total_members,
            "active_subscriptions": total_members,
            "mrr": mrr,
            "tier_breakdown": tier_breakdown
        }
    
    def check_creator_ownership(
        self,
        fan_club_id: str,
        creator_id: str
    ) -> bool:
        """
        Check if user owns the fan club
        
        Args:
            fan_club_id: Fan club ID
            creator_id: Creator user ID
            
        Returns:
            True if creator owns the fan club
        """
        fan_club = self.db.query(FanClub).filter(FanClub.id == fan_club_id).first()
        
        if not fan_club:
            return False
        
        return fan_club.creator_id == creator_id
