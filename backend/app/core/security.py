"""
Security Hardening Module
CORS, rate limiting, input validation, SQL injection prevention
CSRF protection, authentication, encryption
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import logging
from fastapi import HTTPException, Depends, status, Response
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import jwt
from passlib.context import CryptContext
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

# ============ PASSWORD HASHING ============

# Use PBKDF2-SHA256 for maximum compatibility and reliability
import hashlib
from binascii import hexlify, unhexlify

class PasswordService:
    """Secure password handling using PBKDF2-SHA256"""
    
    ITERATIONS = 100000  # NIST recommends 100,000+
    HASH_ALGORITHM = 'sha256'
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with PBKDF2-SHA256"""
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        
        # Generate random salt
        salt = secrets.token_bytes(32)
        
        # Hash password
        pwd_hash = hashlib.pbkdf2_hmac(
            PasswordService.HASH_ALGORITHM,
            password.encode('utf-8'),
            salt,
            PasswordService.ITERATIONS
        )
        
        # Return format: $pbkdf2$salt$hash
        salt_hex = hexlify(salt).decode('utf-8')
        hash_hex = hexlify(pwd_hash).decode('utf-8')
        return f"$pbkdf2${salt_hex}${hash_hex}"
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            # Parse stored hash
            if not hashed_password.startswith('$pbkdf2$'):
                return False
            
            parts = hashed_password.split('$')
            if len(parts) != 4:
                return False
            
            salt_hex = parts[2]
            stored_hash = parts[3]
            
            # Convert hex back to bytes
            salt = unhexlify(salt_hex)
            
            # Compute hash for provided password
            computed_pwd_hash = hashlib.pbkdf2_hmac(
                PasswordService.HASH_ALGORITHM,
                plain_password.encode('utf-8'),
                salt,
                PasswordService.ITERATIONS
            )
            
            computed_hash = hexlify(computed_pwd_hash).decode('utf-8')
            
            # Compare using constant-time comparison
            return secrets.compare_digest(computed_hash, stored_hash)
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False


# ============ JWT & AUTHENTICATION ============

class JWTService:
    """JWT token management"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
        self.algorithm = "HS256"
        self.access_token_expire = 3600  # 1 hour
        self.refresh_token_expire = 604800  # 7 days
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=self.access_token_expire)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=self.refresh_token_expire)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# ============ INPUT VALIDATION ============

class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        return email.lower()
    
    @staticmethod
    def validate_username(username: str) -> str:
        """Validate username format"""
        import re
        if len(username) < 3 or len(username) > 30:
            raise ValueError("Username must be 3-30 characters")
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValueError("Username can only contain letters, numbers, underscore, and hyphen")
        return username
    
    @staticmethod
    def sanitize_string(text: str) -> str:
        """Remove potentially dangerous characters"""
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        for char in dangerous_chars:
            text = text.replace(char, "")
        return text
    
    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URL format"""
        import re
        url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        if not re.match(url_pattern, url):
            raise ValueError("Invalid URL format")
        return url
    
    @staticmethod
    def prevent_sql_injection(value: str) -> str:
        """Prevent SQL injection"""
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'UNION', 'SELECT', ';', '--']
        value_upper = value.upper()
        for keyword in dangerous_keywords:
            if keyword in value_upper:
                logger.warning(f"Potential SQL injection detected: {value}")
                raise ValueError("Invalid input detected")
        return value


# ============ CORS CONFIGURATION ============

def get_cors_middleware():
    """Configure CORS middleware"""
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://beatpush.com",
        "https://www.beatpush.com",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ]
    
    return CORSMiddleware(
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Type", "Authorization"],
        max_age=86400
    )


# ============ TRUSTED HOST ============

def get_trusted_host_middleware():
    """Configure trusted host middleware"""
    allowed_hosts = [
        "beatpush.com",
        "www.beatpush.com",
        "localhost",
        "127.0.0.1",
        os.getenv("API_HOST", "localhost")
    ]
    
    return TrustedHostMiddleware(
        allowed_hosts=allowed_hosts,
        www_redirect=True
    )


# ============ RATE LIMITING ============

class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.limits = {
            "global": 10000,  # 10k requests per hour
            "auth": 5,        # 5 auth attempts per minute
            "api": 100,       # 100 API calls per minute
            "upload": 10      # 10 uploads per hour
        }
    
    def is_rate_limited(self, key: str, limit_type: str = "api") -> bool:
        """Check if request exceeds rate limit"""
        try:
            limit = self.limits.get(limit_type, 100)
            window = 60 if limit_type == "auth" else 3600
            
            current = int(self.redis.get(f"rate:{key}:{limit_type}") or 0)
            
            if current >= limit:
                return True
            
            self.redis.incr(f"rate:{key}:{limit_type}")
            self.redis.expire(f"rate:{key}:{limit_type}", window)
            return False
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            return False


# ============ CSRF PROTECTION ============

class CSRFProtection:
    """CSRF token generation and validation"""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_csrf_token(token: str, session_token: str) -> bool:
        """Validate CSRF token"""
        return secrets.compare_digest(token, session_token)


# ============ ENCRYPTION ============

class EncryptionService:
    """Data encryption/decryption"""
    
    @staticmethod
    def hash_data(data: str) -> str:
        """Hash data (one-way)"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def hash_file(file_path: str) -> str:
        """Hash file for integrity checking"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


# ============ PERMISSION CHECKING ============

class PermissionService:
    """Role-based permission management"""
    
    PERMISSIONS = {
        "admin": ["read", "write", "delete", "moderate", "configure"],
        "producer": ["read", "write", "upload", "sell"],
        "artist": ["read", "write", "upload", "buy", "tip"],
        "dj": ["read", "write", "upload", "book", "review"],
        "fan": ["read", "tip", "subscribe", "comment"]
    }
    
    @staticmethod
    def has_permission(user_role: str, action: str) -> bool:
        """Check if user has permission for action"""
        permissions = PermissionService.PERMISSIONS.get(user_role, [])
        return action in permissions
    
    @staticmethod
    def require_permission(user_role: str, action: str):
        """Require permission or raise exception"""
        if not PermissionService.has_permission(user_role, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action}"
            )


# ============ AUDIT LOGGING ============

class AuditLogger:
    """Audit trail for security events"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def log_event(self, event_type: str, user_id: str, 
                       details: Dict[str, Any], ip_address: str = None):
        """Log security event"""
        try:
            audit_entry = {
                "event_type": event_type,
                "user_id": user_id,
                "details": details,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Audit: {audit_entry}")
            # Save to database
            return True
        except Exception as e:
            logger.error(f"Audit logging error: {str(e)}")
            return False


# ============ FILE UPLOAD SECURITY ============

class FileUploadValidator:
    """Validate file uploads for security"""
    
    ALLOWED_EXTENSIONS = {
        "audio": ["mp3", "wav", "flac", "aac", "ogg"],
        "image": ["jpg", "jpeg", "png", "gif", "webp"],
        "video": ["mp4", "mov", "avi", "mkv"]
    }
    
    MAX_FILE_SIZES = {
        "audio": 100 * 1024 * 1024,    # 100 MB
        "image": 10 * 1024 * 1024,     # 10 MB
        "video": 1024 * 1024 * 1024    # 1 GB
    }
    
    @staticmethod
    def validate_file(file_path: str, file_type: str) -> bool:
        """Validate file upload"""
        import os
        
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        allowed = FileUploadValidator.ALLOWED_EXTENSIONS.get(file_type, [])
        if ext not in allowed:
            raise ValueError(f"Invalid file type: {ext}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        max_size = FileUploadValidator.MAX_FILE_SIZES.get(file_type, 0)
        if file_size > max_size:
            raise ValueError(f"File too large: {file_size} > {max_size}")
        
        return True


# ============ GLOBAL INSTANCES ============

jwt_service = JWTService()
password_service = PasswordService()
input_validator = InputValidator()
encryption_service = EncryptionService()
permission_service = PermissionService()
csrf_protection = CSRFProtection()


# ============ MODULE-LEVEL FUNCTION WRAPPERS ============
# These wrappers provide backward compatibility for existing imports

def hash_password(password: str) -> str:
    """Wrapper for PasswordService.hash_password"""
    return PasswordService.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Wrapper for PasswordService.verify_password"""
    return PasswordService.verify_password(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta=None) -> str:
    """Wrapper for JWTService.create_access_token"""
    return jwt_service.create_access_token(data, expires_delta)


def create_refresh_token(data: dict) -> str:
    """Wrapper for JWTService.create_refresh_token"""
    return jwt_service.create_refresh_token(data)


def decode_token(token: str) -> dict:
    """Wrapper for JWTService.verify_token"""
    return jwt_service.verify_token(token)


def create_email_verification_token(email: str) -> str:
    """Create a verification token for email confirmation"""
    token_data = {
        "sub": email,
        "type": "email_verification"
    }
    return create_access_token(token_data, expires_delta=timedelta(hours=24))


def verify_email_verification_token(token: str) -> str:
    """Verify email verification token and return email if valid"""
    try:
        payload = decode_token(token)
        if payload.get("type") != "email_verification":
            return None
        return payload.get("sub")
    except Exception:
        return None


def create_password_reset_token(email: str) -> str:
    """Create a password reset token"""
    token_data = {
        "sub": email,
        "type": "password_reset"
    }
    return create_access_token(token_data, expires_delta=timedelta(hours=1))


def verify_password_reset_token(token: str) -> str:
    """Verify password reset token and return email if valid"""
    try:
        payload = decode_token(token)
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except Exception:
        return None


def set_auth_cookies(response: "Response", access_token: str, refresh_token: str):
    """Set secure HttpOnly cookies for authentication tokens"""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=3600  # 1 hour
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800  # 7 days
    )


def clear_auth_cookies(response: "Response"):
    """Clear authentication cookies"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


def create_token_pair(user_id: str, email: str, role: str) -> tuple:
    """Create both access and refresh tokens"""
    token_data = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access"
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": user_id, "type": "refresh"})
    return access_token, refresh_token


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP"""
    import random
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def create_otp_token(phone_number: str, otp: str) -> str:
    """Create an OTP verification token"""
    token_data = {
        "sub": phone_number,
        "type": "otp",
        "otp": otp
    }
    return create_access_token(token_data, expires_delta=timedelta(minutes=5))


def verify_otp_token(token: str) -> dict:
    """Verify OTP token and return payload"""
    try:
        payload = decode_token(token)
        if payload.get("type") != "otp":
            return None
        return payload
    except Exception:
        return None
