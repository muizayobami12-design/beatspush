"""
Security utilities: password hashing, JWT tokens, authentication
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import JWTError, jwt
from app.core.config import settings
import secrets


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Bcrypt has a max length of 72 bytes
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Convert to bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Truncate if necessary
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Check password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ============================================================================
# JWT TOKEN GENERATION
# ============================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token (typically user_id, email, role)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Data to encode in the token (typically user_id)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ============================================================================
# PASSWORD RESET TOKENS
# ============================================================================

def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token
    
    Args:
        email: User's email address
        
    Returns:
        Password reset token string
    """
    data = {
        "email": email,
        "type": "password_reset"
    }
    
    expire = datetime.utcnow() + timedelta(minutes=10)  # Reset tokens expire in 10 minutes
    data.update({"exp": expire})
    
    token = jwt.encode(
        data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and extract email
    
    Args:
        token: Password reset token
        
    Returns:
        User's email if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "password_reset":
            return None
            
        return payload.get("email")
    except JWTError:
        return None


# ============================================================================
# EMAIL VERIFICATION TOKENS
# ============================================================================

def create_email_verification_token(email: str) -> str:
    """
    Create an email verification token
    
    Args:
        email: User's email address
        
    Returns:
        Email verification token string
    """
    data = {
        "email": email,
        "type": "email_verification"
    }
    
    expire = datetime.utcnow() + timedelta(days=7)  # Verification tokens expire in 7 days
    data.update({"exp": expire})
    
    token = jwt.encode(
        data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify an email verification token and extract email
    
    Args:
        token: Email verification token
        
    Returns:
        User's email if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "email_verification":
            return None
            
        return payload.get("email")
    except JWTError:
        return None


# ============================================================================
# RANDOM TOKEN GENERATION (for API keys, etc.)
# ============================================================================

def generate_random_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token
    
    Args:
        length: Length of the token in bytes (will be hex encoded, so output is 2x length)
        
    Returns:
        Random token string
    """
    return secrets.token_hex(length)
