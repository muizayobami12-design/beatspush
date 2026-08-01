"""
User profile endpoints
Routes for viewing and managing user profiles
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest, MessageResponse
from app.core.dependencies import get_current_user, get_current_active_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile
    
    **Requires:** Authentication (Bearer token)
    
    **Returns:** Current user's profile information
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    
    **Requires:** Authentication (Bearer token)
    
    **Updatable Fields:**
    - `full_name`: User's full name
    - `username`: Unique username
    
    **Returns:** Updated user profile
    """
    # Update fields if provided
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    
    if update_data.username is not None:
        # Check if username is already taken by another user
        existing = db.query(User).filter(
            User.username == update_data.username,
            User.id != current_user.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        current_user.username = update_data.username
    
    # Save changes
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)


@router.delete("/me", response_model=MessageResponse)
async def delete_my_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate current user's account
    
    **Requires:** Authentication (Bearer token)
    
    This doesn't permanently delete the account, but deactivates it.
    User can contact support to reactivate or permanently delete.
    
    **Returns:** Success message
    """
    current_user.is_active = False
    db.commit()
    
    return MessageResponse(
        message="Account deactivated successfully",
        success=True
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get any user's public profile by ID
    
    **Public endpoint** - No authentication required
    
    **Returns:** User's public profile information
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)
