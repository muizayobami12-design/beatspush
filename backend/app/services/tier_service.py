"""
Tier Service - Business logic for membership tier management
Tasks 5.1-5.6: Tier CRUD operations
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from datetime import datetime
from decimal import Decimal
import uuid

from app.models.fan_club import MembershipTier, Subscription, FanClub
from app.schemas.fan_club import TierCreate, TierUpdate, TierResponse


class TierService:
    """Service for managing membership tiers"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # TIER MANAGEMENT
    # ========================================================================
    
    def create_tier(
        self,
        fan_club_id: str,
        creator_id: str,
        data: TierCreate
    ) -> MembershipTier:
        """
        Create a new membership tier
        
        Validation:
        - Creator must own the fan club
        - Maximum 3 tiers per fan club
        - Tier level must be unique
        - Tier name must be unique within fan club
        
        Args:
            fan_club_id: Fan club ID
            creator_id: Creator user ID (for authorization)
            data: Tier creation data
            
        Returns:
            Created MembershipTier object
        """
        # Verify fan club exists and creator owns it
        fan_club = self.db.query(FanClub).filter(FanClub.id == fan_club_id).first()
        
        if not fan_club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fan club not found"
            )
        
        if fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to add tiers to this fan club"
            )
        
        # Check maximum tier limit (3 tiers)
        existing_tiers = (
            self.db.query(MembershipTier)
            .filter(MembershipTier.fan_club_id == fan_club_id)
            .count()
        )
        
        if existing_tiers >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 3 tiers allowed per fan club"
            )
        
        # Check tier level uniqueness
        existing_level = (
            self.db.query(MembershipTier)
            .filter(
                MembershipTier.fan_club_id == fan_club_id,
                MembershipTier.tier_level == data.tier_level
            )
            .first()
        )
        
        if existing_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tier level {data.tier_level} already exists"
            )
        
        # Check tier name uniqueness
        existing_name = (
            self.db.query(MembershipTier)
            .filter(
                MembershipTier.fan_club_id == fan_club_id,
                MembershipTier.name == data.name
            )
            .first()
        )
        
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tier name '{data.name}' already exists"
            )
        
        # Calculate yearly price (10% discount)
        price_yearly = data.price_monthly * 12 * Decimal('0.9')
        
        # Create tier
        tier = MembershipTier(
            id=str(uuid.uuid4()),
            fan_club_id=fan_club_id,
            name=data.name,
            description=data.description,
            tier_level=data.tier_level,
            price_monthly=data.price_monthly,
            price_yearly=price_yearly,
            benefits=data.benefits,
            is_active=True,
            subscriber_count=0
        )
        
        self.db.add(tier)
        self.db.commit()
        self.db.refresh(tier)
        
        return tier
    
    def update_tier(
        self,
        tier_id: str,
        creator_id: str,
        data: TierUpdate
    ) -> MembershipTier:
        """
        Update membership tier
        
        Note: Price changes affect new subscriptions only.
        Existing subscribers keep their price for current period.
        
        Args:
            tier_id: Tier ID
            creator_id: Creator user ID (for authorization)
            data: Update data
            
        Returns:
            Updated MembershipTier object
        """
        tier = self.db.query(MembershipTier).filter(MembershipTier.id == tier_id).first()
        
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tier not found"
            )
        
        # Check ownership
        fan_club = self.db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        if not fan_club or fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this tier"
            )
        
        # Update fields
        if data.name is not None:
            # Check name uniqueness
            existing = (
                self.db.query(MembershipTier)
                .filter(
                    MembershipTier.fan_club_id == tier.fan_club_id,
                    MembershipTier.name == data.name,
                    MembershipTier.id != tier_id
                )
                .first()
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tier name '{data.name}' already exists"
                )
            tier.name = data.name
        
        if data.description is not None:
            tier.description = data.description
        
        if data.price_monthly is not None:
            # Notify existing subscribers about price change (30-day notice)
            # For now, just update the price
            tier.price_monthly = data.price_monthly
            tier.price_yearly = data.price_monthly * 12 * Decimal('0.9')
        
        if data.benefits is not None:
            tier.benefits = data.benefits
        
        if data.is_active is not None:
            # If deactivating, check for active subscriptions
            if not data.is_active:
                active_subs = (
                    self.db.query(Subscription)
                    .filter(
                        Subscription.tier_id == tier_id,
                        Subscription.status == "active"
                    )
                    .count()
                )
                if active_subs > 0:
                    # Allow deactivation but new subscriptions are prevented
                    # Existing subscribers keep access until they cancel
                    pass
            tier.is_active = data.is_active
        
        tier.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(tier)
        
        return tier
    
    def delete_tier(
        self,
        tier_id: str,
        creator_id: str
    ) -> bool:
        """
        Delete membership tier
        
        Only allowed if no active subscriptions exist.
        
        Args:
            tier_id: Tier ID
            creator_id: Creator user ID (for authorization)
            
        Returns:
            True if deleted successfully
        """
        tier = self.db.query(MembershipTier).filter(MembershipTier.id == tier_id).first()
        
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tier not found"
            )
        
        # Check ownership
        fan_club = self.db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        if not fan_club or fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this tier"
            )
        
        # Check for active subscriptions
        active_subs = (
            self.db.query(Subscription)
            .filter(
                Subscription.tier_id == tier_id,
                Subscription.status.in_(["active", "paused"])
            )
            .count()
        )
        
        if active_subs > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete tier with {active_subs} active subscriptions. Pause the tier instead."
            )
        
        self.db.delete(tier)
        self.db.commit()
        
        return True
    
    def list_tiers(
        self,
        fan_club_id: str,
        include_inactive: bool = False
    ) -> List[MembershipTier]:
        """
        List all tiers for a fan club
        
        Args:
            fan_club_id: Fan club ID
            include_inactive: Include inactive tiers
            
        Returns:
            List of MembershipTier objects
        """
        query = (
            self.db.query(MembershipTier)
            .filter(MembershipTier.fan_club_id == fan_club_id)
        )
        
        if not include_inactive:
            query = query.filter(MembershipTier.is_active == True)
        
        tiers = query.order_by(MembershipTier.tier_level).all()
        
        return tiers
    
    def pause_tier(
        self,
        tier_id: str,
        creator_id: str
    ) -> MembershipTier:
        """
        Pause tier (prevent new subscriptions)
        
        Existing subscribers keep access.
        
        Args:
            tier_id: Tier ID
            creator_id: Creator user ID (for authorization)
            
        Returns:
            Updated MembershipTier object
        """
        tier = self.db.query(MembershipTier).filter(MembershipTier.id == tier_id).first()
        
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tier not found"
            )
        
        # Check ownership
        fan_club = self.db.query(FanClub).filter(FanClub.id == tier.fan_club_id).first()
        if not fan_club or fan_club.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to pause this tier"
            )
        
        tier.is_active = False
        tier.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(tier)
        
        return tier
    
    def get_tier(
        self,
        tier_id: str
    ) -> MembershipTier:
        """
        Get tier by ID
        
        Args:
            tier_id: Tier ID
            
        Returns:
            MembershipTier object
        """
        tier = self.db.query(MembershipTier).filter(MembershipTier.id == tier_id).first()
        
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tier not found"
            )
        
        return tier
    
    def calculate_price(
        self,
        monthly_price: Decimal,
        billing_cycle: str
    ) -> Decimal:
        """
        Calculate price based on billing cycle
        
        Args:
            monthly_price: Monthly price
            billing_cycle: "monthly" or "yearly"
            
        Returns:
            Calculated price
        """
        if billing_cycle == "monthly":
            return monthly_price
        elif billing_cycle == "yearly":
            # 10% discount for yearly (2 months free)
            return monthly_price * 12 * Decimal('0.9')
        else:
            raise ValueError(f"Invalid billing cycle: {billing_cycle}")
