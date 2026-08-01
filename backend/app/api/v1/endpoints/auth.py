"""
Authentication endpoints
Routes for user registration, login, password reset, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenRefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    AuthResponse,
    TokenResponse,
    MessageResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account
    
    **User Types:**
    - `artist`: Musicians, singers, bands
    - `dj`: DJs, radio hosts
    - `producer`: Music producers, beat makers
    - `fan`: Music listeners, supporters
    - `admin`: Platform administrators
    
    **Password Requirements:**
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    
    **Returns:**
    - User information
    - Access token (expires in 30 minutes)
    - Refresh token (expires in 7 days)
    """
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login to an existing account
    
    **Returns:**
    - User information
    - Access token (expires in 30 minutes)
    - Refresh token (expires in 7 days)
    """
    return AuthService.login_user(db, credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Get a new access token using a refresh token
    
    Use this endpoint when your access token expires.
    Provide the refresh token to get a new access token.
    
    **Returns:**
    - New access token
    - New refresh token
    """
    return AuthService.refresh_access_token(db, token_data.refresh_token)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset email
    
    An email with a password reset link will be sent if the email exists.
    For security, this endpoint always returns success even if email doesn't exist.
    """
    return AuthService.request_password_reset(db, request_data.email)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using the token from email
    
    **Password Requirements:**
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    """
    return AuthService.reset_password(
        db,
        reset_data.token,
        reset_data.new_password
    )


@router.get("/verify-email/{token}", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify email address using the token from email
    
    Users should click the verification link in their welcome email.
    This endpoint validates the token and marks the email as verified.
    """
    return AuthService.verify_email(db, token)


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """
    Logout (client-side only)
    
    Since we're using stateless JWT tokens, logout is handled client-side
    by deleting the tokens from storage.
    
    This endpoint is provided for completeness and can be used to:
    - Track logout events
    - Invalidate refresh tokens (future feature)
    - Clear server-side sessions if implemented
    """
    return MessageResponse(
        message="Logged out successfully. Please delete tokens from client storage.",
        success=True
    )
