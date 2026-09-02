"""
Cloudflare Turnstile Verification Service
Verifies CAPTCHA tokens from frontend
"""

import httpx
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class TurnstileService:
    """Service for verifying Cloudflare Turnstile tokens"""
    
    VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    
    def __init__(self):
        self.secret_key = settings.TURNSTILE_SECRET_KEY
    
    async def verify_token(
        self, 
        token: str, 
        remote_ip: Optional[str] = None
    ) -> dict:
        """
        Verify Turnstile token with Cloudflare
        
        Args:
            token: The token from frontend
            remote_ip: User's IP address (optional but recommended)
            
        Returns:
            dict with success status and details
        """
        if not self.secret_key:
            logger.warning("Turnstile secret key not configured")
            # In development, allow bypassing if not configured
            if settings.ENVIRONMENT == "development":
                return {
                    "success": True,
                    "bypass": True,
                    "message": "Turnstile bypassed in development"
                }
            return {
                "success": False,
                "error": "Turnstile not configured"
            }
        
        # Prepare verification request
        payload = {
            "secret": self.secret_key,
            "response": token,
        }
        
        if remote_ip:
            payload["remoteip"] = remote_ip
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.VERIFY_URL,
                    data=payload,
                    timeout=10.0
                )
                
                result = response.json()
                
                if result.get("success"):
                    logger.info(f"Turnstile verification successful: {result}")
                    return {
                        "success": True,
                        "challenge_ts": result.get("challenge_ts"),
                        "hostname": result.get("hostname"),
                    }
                else:
                    logger.warning(f"Turnstile verification failed: {result}")
                    return {
                        "success": False,
                        "error_codes": result.get("error-codes", []),
                        "message": "CAPTCHA verification failed"
                    }
                    
        except httpx.TimeoutException:
            logger.error("Turnstile verification timeout")
            return {
                "success": False,
                "error": "Verification timeout"
            }
        except Exception as e:
            logger.error(f"Turnstile verification error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_or_fail(
        self, 
        token: Optional[str], 
        remote_ip: Optional[str] = None
    ) -> bool:
        """
        Verify token or raise exception
        
        Returns:
            True if verification successful
            
        Raises:
            ValueError if verification fails
        """
        if not token:
            raise ValueError("CAPTCHA token required")
        
        result = await self.verify_token(token, remote_ip)
        
        if not result["success"]:
            error_msg = result.get("message", "CAPTCHA verification failed")
            raise ValueError(error_msg)
        
        return True


# Singleton instance
turnstile_service = TurnstileService()
