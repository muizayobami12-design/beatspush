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
        
        Validation:
        - Creator must be verified
        - Creator must have at least 100 followers
        - Creator must have at least 10 published tracks/posts
        - Creator can only have one fan club
        
        Args:
            creator_id: Creator user ID
            data: Fan club creation data
            
        Returns:
            Created FanClub object
        """
        # Check if creator exists
        creator = self.db.query(User).filter(User.id == creator_id).first()
        if not creator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Creator not found"
            )
        
        # Check if creator is eligible
        if not creator.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only verified creators can create fan clubs"
            )
        
        if creator.role not in [UserRole.ARTIST, UserRole.DJ, UserRole.PRODUCER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only artists, DJs, and producers can create fan clubs"
            )
        
        # Check if fan club already exists
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
        
        # Create fan club
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
        
        return fan_club
    
    def get_fan_club(
        self,
        fan_club_id: Optional[str] = None,
        creator_id: Optional[str] = None
    ) -> FanClub:
        """
        Get fan club by ID or creator ID
        
        Args:
            fan_club_id: Fan club ID (optional)
            creator_id: Creator user ID (optional)
            
        Returns:
            FanClub object
        """
        query = self.db.query(FanClub).options(
            joinedload(FanClub.tiers),
            joinedload(FanClub.creator)
        )
        
        if fan_club_id:
            fan_club = query.filter(FanClub.id == fan_club_id).first()
        elif creator_id:
            fan_club = query.filter(FanClub.creator_id == creator_id).first()
        else:
            raise ValueError("Either fan_club_id or creator_id must be provided")
        
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
        Update fan club details
        
        Args:
            fan_club_id: Fan club ID
            creator_id: Creator user ID (for authorization)
            data: Update data
            
        Returns:
            Updated FanClub object
        """
        fan_club = self.get_fan_club(fan_club_id=fan_club_id)
        
        # Check ownership
        if fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this fan club"
            )
        
        # Update fields
        if data.name is not None:
            fan_club.name = data.name
        if data.description is not None:
            fan_club.description = data.description
        if data.welcome_message is not None:
            fan_club.welcome_message = data.welcome_message
        if data.is_active is not None:
            # If deactivating, check if there are active subscriptions
            if not data.is_active:
                active_subs = (
                    self.db.query(Subscription)
                    .filter(
                        Subscription.fan_club_id == fan_club_id,
                        Subscription.status == "active"
                    )
                    .count()
                )
                if active_subs > 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot deactivate fan club with {active_subs} active subscriptions"
                    )
            fan_club.is_active = data.is_active
        
        fan_club.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(fan_club)
        
        return fan_club
    
    def deactivate_fan_club(
        self,
        fan_club_id: str,
        creator_id: str
    ) -> bool:
        """
        Deactivate fan club (soft delete)
        
        Args:
            fan_club_id: Fan club ID
            creator_id: Creator user ID (for authorization)
            
        Returns:
            True if deactivated successfully
        """
        fan_club = self.get_fan_club(fan_club_id=fan_club_id)
        
        # Check ownership
        if fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to deactivate this fan club"
            )
        
        # Check for active subscriptions
        active_subs = (
            self.db.query(Subscription)
            .filter(
                Subscription.fan_club_id == fan_club_id,
                Subscription.status == "active"
            )
            .count()
        )
        
        if active_subs > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot deactivate fan club with {active_subs} active subscriptions. Cancel all subscriptions first."
            )
        
        fan_club.is_active = False
        fan_club.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def get_fan_club_stats(
        self,
        fan_club_id: str
    ) -> Dict:
        """
        Get fan club statistics
        
        Args:
            fan_club_id: Fan club ID
            
        Returns:
            Dictionary with statistics
        """
        fan_club = self.get_fan_club(fan_club_id=fan_club_id)
        
        # Get active subscriptions
        active_subs = (
            self.db.query(Subscription)
            .filter(
                Subscription.fan_club_id == fan_club_id,
                Subscription.status == "active"
            )
            .all()
        )
        
        # Calculate MRR (Monthly Recurring Revenue)
        mrr = Decimal('0.00')
        for sub in active_subs:
            if sub.billing_cycle == "monthly":
                mrr += sub.price_paid
            elif sub.billing_cycle == "yearly":
                # Convert yearly to monthly
                mrr += sub.price_paid / 12
        
        # Get subscribers by tier
        tier_distribution = (
            self.db.query(
                MembershipTier.name,
                func.count(Subscription.id).label('count')
            )
            .join(Subscription, Subscription.tier_id == MembershipTier.id)
            .filter(
                Subscription.fan_club_id == fan_club_id,
                Subscription.status == "active"
            )
            .group_by(MembershipTier.name)
            .all()
        )
        
        subscribers_by_tier = {tier: count for tier, count in tier_distribution}
        
        return {
            "fan_club_id": fan_club_id,
            "fan_club_name": fan_club.name,
            "total_members": len(active_subs),
            "monthly_recurring_revenue": float(mrr),
            "subscribers_by_tier": subscribers_by_tier,
            "is_active": fan_club.is_active,
            "created_at": fan_club.created_at
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
