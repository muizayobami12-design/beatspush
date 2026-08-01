"""
Profile Service - Business logic for user profile management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Union

from app.models.user import User, UserRole
from app.models.profile import ArtistProfile, DJProfile, ProducerProfile, FanProfile
from app.schemas.profile import (
    ArtistProfileUpdate,
    ArtistProfileResponse,
    DJProfileUpdate,
    DJProfileResponse,
    ProducerProfileUpdate,
    ProducerProfileResponse,
    FanProfileUpdate,
    FanProfileResponse
)


class ProfileService:
    """Profile management service"""
    
    @staticmethod
    def get_or_create_profile(db: Session, user: User):
        """
        Get user's profile or create if doesn't exist
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Profile object based on user role
        """
        if user.role == UserRole.ARTIST:
            profile = db.query(ArtistProfile).filter(ArtistProfile.user_id == user.id).first()
            if not profile:
                profile = ArtistProfile(user_id=user.id)
                db.add(profile)
                db.commit()
                db.refresh(profile)
            return profile
        
        elif user.role == UserRole.DJ:
            profile = db.query(DJProfile).filter(DJProfile.user_id == user.id).first()
            if not profile:
                profile = DJProfile(user_id=user.id)
                db.add(profile)
                db.commit()
                db.refresh(profile)
            return profile
        
        elif user.role == UserRole.PRODUCER:
            profile = db.query(ProducerProfile).filter(ProducerProfile.user_id == user.id).first()
            if not profile:
                profile = ProducerProfile(user_id=user.id)
                db.add(profile)
                db.commit()
                db.refresh(profile)
            return profile
        
        elif user.role == UserRole.FAN:
            profile = db.query(FanProfile).filter(FanProfile.user_id == user.id).first()
            if not profile:
                profile = FanProfile(user_id=user.id)
                db.add(profile)
                db.commit()
                db.refresh(profile)
            return profile
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin users do not have extended profiles"
            )
    
    @staticmethod
    def update_artist_profile(db: Session, user: User, update_data: ArtistProfileUpdate):
        """Update artist profile"""
        if user.role != UserRole.ARTIST:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an artist"
            )
        
        profile = ProfileService.get_or_create_profile(db, user)
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return ArtistProfileResponse.from_orm(profile)
    
    @staticmethod
    def update_dj_profile(db: Session, user: User, update_data: DJProfileUpdate):
        """Update DJ profile"""
        if user.role != UserRole.DJ:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a DJ"
            )
        
        profile = ProfileService.get_or_create_profile(db, user)
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return DJProfileResponse.from_orm(profile)
    
    @staticmethod
    def update_producer_profile(db: Session, user: User, update_data: ProducerProfileUpdate):
        """Update producer profile"""
        if user.role != UserRole.PRODUCER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a producer"
            )
        
        profile = ProfileService.get_or_create_profile(db, user)
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return ProducerProfileResponse.from_orm(profile)
    
    @staticmethod
    def update_fan_profile(db: Session, user: User, update_data: FanProfileUpdate):
        """Update fan profile"""
        if user.role != UserRole.FAN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a fan"
            )
        
        profile = ProfileService.get_or_create_profile(db, user)
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return FanProfileResponse.from_orm(profile)
    
    @staticmethod
    def get_profile_response(db: Session, user: User):
        """
        Get profile response based on user role
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Profile response schema
        """
        profile = ProfileService.get_or_create_profile(db, user)
        
        if user.role == UserRole.ARTIST:
            return ArtistProfileResponse.from_orm(profile)
        elif user.role == UserRole.DJ:
            return DJProfileResponse.from_orm(profile)
        elif user.role == UserRole.PRODUCER:
            return ProducerProfileResponse.from_orm(profile)
        elif user.role == UserRole.FAN:
            return FanProfileResponse.from_orm(profile)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user role"
            )
    
    @staticmethod
    def get_public_profile(db: Session, user_id: str):
        """
        Get public profile for any user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Public profile data
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return ProfileService.get_profile_response(db, user)
