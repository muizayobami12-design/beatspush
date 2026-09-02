"""
Authentication endpoints
Routes for user registration, login, password reset, etc.
Enhanced with HttpOnly cookies and 2FA support
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from sqlalchemy.orm import Session
from redis import Redis
from typing import Optional

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
from app.services.turnstile_service import turnstile_service
from app.services.fraud_detection_service import fraud_detector
from app.services.rate_limiter import RateLimiter, get_rate_limit_config
from app.services.security_logger import security_logger
from app.services.sms_service import sms_service
from app.core.config import settings
from app.core.security import (
    set_auth_cookies,
    clear_auth_cookies,
    decode_token,
    create_token_pair,
    verify_otp_token
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Register a new user account (with Fort Knox security)
    
    **Security Features:**
    - Cloudflare Turnstile CAPTCHA verification
    - Device fingerprinting
    - Fraud detection scoring
    - Rate limiting (3 attempts per hour per IP)
    - Email validation
    - HttpOnly cookies for JWT storage
    
    **User Types:**
    - `artist`: Musicians, singers, bands
    - `dj`: DJs, radio hosts
    - `producer`: Music producers, beat makers
    - `fan`: Music listeners, supporters
    - `admin`: Platform administrators
    
    **Password Requirements:**
    - Minimum 6 characters
    
    **Returns:**
    - User information
    - Access token (in HttpOnly cookie)
    - Refresh token (in HttpOnly cookie)
    """
    # Get IP address
    ip_address = request.client.host
    
    # Step 1: Rate limiting
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    rate_limiter = RateLimiter(redis_client)
    rate_limit_config = get_rate_limit_config("register")
    
    is_allowed = await rate_limiter.is_allowed(
        identifier=ip_address,
        action="register",
        max_requests=rate_limit_config["max_requests"],
        window_seconds=rate_limit_config["window_seconds"]
    )
    
    if not is_allowed:
        logger.warning(f"Registration rate limit exceeded: {ip_address}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Step 2: Verify Turnstile token
    if user_data.turnstile_token:
        turnstile_result = await turnstile_service.verify_token(
            token=user_data.turnstile_token,
            remote_ip=ip_address
        )
        
        if not turnstile_result["success"]:
            logger.warning(f"Turnstile verification failed: {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CAPTCHA verification failed. Please try again."
            )
    elif settings.ENVIRONMENT == "production":
        # Require Turnstile in production
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPTCHA verification required"
        )
    
    # Step 3: Fraud detection
    fraud_result = await fraud_detector.score_registration(
        email=user_data.email,
        ip_address=ip_address,
        device_id=user_data.device_id,
        country=None,  # TODO: Add IP geolocation
        db=db
    )
    
    # Block high-risk registrations
    if fraud_result["decision"] == "block":
        logger.warning(
            f"Registration blocked: {user_data.email} - "
            f"Risk: {fraud_result['risk_score']} - "
            f"Flags: {fraud_result['flags']}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration blocked for security reasons. Please contact support."
        )
    
    # Step 4: Register user
    try:
        auth_response = AuthService.register_user(db, user_data)
        
        # Step 5: Set HttpOnly cookies
        set_auth_cookies(
            response,
            auth_response.access_token,
            auth_response.refresh_token
        )
        
        # Step 6: Log security event
        security_logger.log_registration(
            db=db,
            user_id=auth_response.user.id,
            email=user_data.email,
            ip_address=ip_address,
            device_id=user_data.device_id,
            risk_score=fraud_result["risk_score"],
            flags=fraud_result["flags"],
            decision=fraud_result["decision"]
        )
        
        # Clear rate limit on successful registration
        rate_limiter.clear_rate_limit(ip_address, "register")
        
        logger.info(
            f"User registered successfully: {user_data.email} - "
            f"Risk: {fraud_result['risk_score']}"
        )
        
        return auth_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login to an existing account (with Fort Knox security + HttpOnly cookies)
    
    **Security Features:**
    - Cloudflare Turnstile CAPTCHA verification (after 3 failed attempts)
    - Device fingerprinting
    - Suspicious login detection
    - Rate limiting (5 attempts per 15 minutes per IP)
    - Failed attempt tracking
    - HttpOnly cookies for JWT storage
    
    **Returns:**
    - User information
    - Access token (in HttpOnly cookie)
    - Refresh token (in HttpOnly cookie)
    """
    # Get IP address
    ip_address = request.client.host
    
    # Step 1: Rate limiting
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    rate_limiter = RateLimiter(redis_client)
    rate_limit_config = get_rate_limit_config("login")
    
    is_allowed = await rate_limiter.is_allowed(
        identifier=ip_address,
        action="login",
        max_requests=rate_limit_config["max_requests"],
        window_seconds=rate_limit_config["window_seconds"]
    )
    
    if not is_allowed:
        logger.warning(f"Login rate limit exceeded: {ip_address}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again in 15 minutes."
        )
    
    # Step 2: Verify Turnstile token (if provided)
    if credentials.turnstile_token:
        turnstile_result = await turnstile_service.verify_token(
            token=credentials.turnstile_token,
            remote_ip=ip_address
        )
        
        if not turnstile_result["success"]:
            logger.warning(f"Turnstile verification failed during login: {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CAPTCHA verification failed. Please try again."
            )
    
    # Step 3: Attempt login
    try:
        auth_response = AuthService.login_user(db, credentials)
        user = auth_response.user
        
        # Step 4: Suspicious login detection
        from app.models.user import User
        db_user = db.query(User).filter(User.id == user.id).first()
        
        if db_user:
            user_data = {
                "last_login_at": db_user.last_login,
                "last_login_ip": db_user.last_login_ip,
                "device_id": db_user.device_id,
                "failed_login_attempts": db_user.failed_login_attempts or 0
            }
            
            fraud_result = await fraud_detector.score_login(
                user_id=user.id,
                ip_address=ip_address,
                device_id=credentials.device_id,
                user_data=user_data,
                db=db
            )
            
            # Log suspicious login
            if fraud_result["risk_score"] > 50:
                security_logger.log_suspicious_activity(
                    db=db,
                    user_id=user.id,
                    activity_type="suspicious_login",
                    ip_address=ip_address,
                    device_id=credentials.device_id,
                    risk_score=fraud_result["risk_score"],
                    flags=fraud_result["flags"],
                    details={
                        "action": fraud_result["action"],
                        "reasons": fraud_result["reasons"]
                    }
                )
            
            # Update user login tracking
            from datetime import datetime
            db_user.last_login = datetime.utcnow()
            db_user.last_login_ip = ip_address
            db_user.failed_login_attempts = 0
            
            if credentials.device_id:
                db_user.device_id = credentials.device_id
            if credentials.device_info:
                db_user.device_info = credentials.device_info
            
            db.commit()
        
        # Step 5: Set HttpOnly cookies
        set_auth_cookies(
            response,
            auth_response.access_token,
            auth_response.refresh_token
        )
        
        # Step 6: Log login success
        security_logger.log_login_attempt(
            db=db,
            user_id=user.id,
            email=credentials.email,
            ip_address=ip_address,
            device_id=credentials.device_id,
            success=True,
            risk_score=fraud_result.get("risk_score") if 'fraud_result' in locals() else None,
            flags=fraud_result.get("flags") if 'fraud_result' in locals() else None
        )
        
        # Clear rate limit on successful login
        rate_limiter.clear_rate_limit(ip_address, "login")
        
        logger.info(f"User logged in successfully: {credentials.email}")
        
        return auth_response
        
    except HTTPException as e:
        # Step 7: Track failed login attempt
        from app.models.user import User
        db_user = db.query(User).filter(User.email == credentials.email).first()
        
        if db_user:
            db_user.failed_login_attempts = (db_user.failed_login_attempts or 0) + 1
            db.commit()
            
            # Log failed attempt
            security_logger.log_login_attempt(
                db=db,
                user_id=db_user.id,
                email=credentials.email,
                ip_address=ip_address,
                device_id=credentials.device_id,
                success=False
            )
        
        raise e
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.get("/me")
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information
    
    **Returns:**
    - User profile data
    """
    from app.core.dependencies import get_current_user
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        # Decode token to get user ID
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "username": user.username,
            "role": user.role,
            "is_verified": getattr(user, "is_verified", False),
            "created_at": user.created_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


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
    - Minimum 6 characters
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
async def logout(response: Response):
    """
    Logout (clears HttpOnly cookies)
    
    Securely logs out user by clearing authentication cookies.
    This invalidates both access and refresh tokens.
    
    **Security:**
    - Clears HttpOnly cookies
    - Immediate effect (tokens no longer sent)
    - Works with cookie-based auth
    """
    # Clear authentication cookies
    clear_auth_cookies(response)
    
    logger.info("User logged out successfully")
    
    return MessageResponse(
        message="Logged out successfully. Cookies cleared.",
        success=True
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token (with rotation)
    
    **Token Rotation:**
    - Old refresh token is invalidated
    - New refresh token is issued
    - Access token is refreshed
    - Both set as HttpOnly cookies
    
    **Security:**
    - Stolen refresh tokens become invalid after first use
    - Automatic rotation on every refresh
    - HttpOnly cookies prevent XSS theft
    
    **Returns:**
    - New access token (in cookie)
    - New refresh token (in cookie)
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    # Decode refresh token
    payload = decode_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new token pair (rotation)
    new_access_token, new_refresh_token = create_token_pair(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    # Set new cookies
    set_auth_cookies(response, new_access_token, new_refresh_token)
    
    logger.info(f"Token refreshed for user: {user.email}")
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
