"""
User schemas - Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, UserTier


# ============================================================================
# REQUEST SCHEMAS (Input from client)
# ============================================================================

class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole
    full_name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=255)
    
    # Security metadata (from frontend)
    turnstile_token: Optional[str] = None
    device_id: Optional[str] = None
    device_info: Optional[str] = None  # JSON string
    
    @validator('username')
    def validate_username(cls, v):
        """Ensure username contains only valid characters"""
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str
    
    # Security metadata (from frontend)
    turnstile_token: Optional[str] = None
    device_id: Optional[str] = None
    device_info: Optional[str] = None  # JSON string


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)


class UserUpdateRequest(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        """Ensure username contains only valid characters"""
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


# ============================================================================
# RESPONSE SCHEMAS (Output to client)
# ============================================================================

class UserResponse(BaseModel):
    """User response (public info)"""
    id: str
    email: EmailStr
    role: UserRole
    tier: UserTier  # AI subscription tier
    full_name: Optional[str]
    username: Optional[str]
    is_active: bool
    is_verified: bool
    email_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True  # Allows ORM model conversion


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    """Authentication response (login/register)"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
