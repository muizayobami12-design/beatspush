"""
Authentication Service - Business logic for user registration, login, etc.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import uuid
from typing import Tuple

from app.models.user import User, UserRole
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    AuthResponse,
    UserResponse
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    create_email_verification_token,
    create_password_reset_token,
    verify_password_reset_token,
    verify_email_verification_token
)
from app.core.config import settings
from app.services.email_service import EmailService


class AuthService:
    """Authentication service for handling user auth operations"""
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegisterRequest) -> AuthResponse:
        """
        Register a new user
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            AuthResponse with user info and tokens
            
        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists (if provided)
        if user_data.username:
            existing_username = db.query(User).filter(User.username == user_data.username).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            role=user_data.role,
            full_name=user_data.full_name,
            username=user_data.username,
            is_active=True,
            is_verified=False,
            email_verified=False,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        
        # Save to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate tokens
        tokens = AuthService._generate_tokens(new_user)
        
        # Send verification email
        try:
            verification_token = create_email_verification_token(new_user.email)
            EmailService.send_verification_email(new_user.email, verification_token)
        except Exception as e:
            # Log error but don't fail registration
            print(f"Failed to send verification email: {e}")
        
        return AuthResponse(
            user=UserResponse.from_orm(new_user),
            tokens=tokens
        )
    
    @staticmethod
    def login_user(db: Session, credentials: UserLoginRequest) -> AuthResponse:
        """
        Login a user
        
        Args:
            db: Database session
            credentials: User login credentials
            
        Returns:
            AuthResponse with user info and tokens
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate tokens
        tokens = AuthService._generate_tokens(user)
        
        return AuthResponse(
            user=UserResponse.from_orm(user),
            tokens=tokens
        )
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
        """
        Generate new access token from refresh token
        
        Args:
            db: Database session
            refresh_token: Refresh token
            
        Returns:
            New TokenResponse with fresh access token
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Extract user_id
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        return AuthService._generate_tokens(user)
    
    @staticmethod
    def verify_email(db: Session, token: str) -> dict:
        """
        Verify user's email address
        
        Args:
            db: Database session
            token: Email verification token
            
        Returns:
            Success message dict
            
        Raises:
            HTTPException: If token is invalid
        """
        # Verify token and extract email
        email = verify_email_verification_token(token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update email_verified status
        user.email_verified = True
        user.is_verified = True
        db.commit()
        
        return {"message": "Email verified successfully", "success": True}
    
    @staticmethod
    def request_password_reset(db: Session, email: str) -> dict:
        """
        Send password reset email
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            Success message dict
        """
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        # Always return success even if user doesn't exist (security best practice)
        if not user:
            return {
                "message": "If that email exists, a password reset link has been sent",
                "success": True
            }
        
        # Generate reset token
        reset_token = create_password_reset_token(email)
        
        # Send password reset email
        try:
            EmailService.send_password_reset_email(email, reset_token)
        except Exception as e:
            # Log error but don't expose to user
            print(f"Failed to send password reset email: {e}")
        
        return {
            "message": "If that email exists, a password reset link has been sent",
            "success": True
        }
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> dict:
        """
        Reset user's password
        
        Args:
            db: Database session
            token: Password reset token
            new_password: New password
            
        Returns:
            Success message dict
            
        Raises:
            HTTPException: If token is invalid
        """
        # Verify token and extract email
        email = verify_password_reset_token(token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.hashed_password = hash_password(new_password)
        db.commit()
        
        return {"message": "Password reset successfully", "success": True}
    
    @staticmethod
    def _generate_tokens(user: User) -> TokenResponse:
        """
        Generate access and refresh tokens for a user
        
        Args:
            user: User object
            
        Returns:
            TokenResponse with access and refresh tokens
        """
        # Token payload
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value
        }
        
        # Generate tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
