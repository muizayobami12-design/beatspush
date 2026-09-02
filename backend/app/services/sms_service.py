"""
SMS Service using Termii (Nigerian SMS Provider)
Handles OTP sending and verification
"""

import httpx
from typing import Optional, Dict
from app.core.config import settings
from app.core.security import generate_otp, create_otp_token
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS via Termii"""
    
    BASE_URL = "https://api.ng.termii.com/api"
    
    def __init__(self):
        self.api_key = settings.TERMII_API_KEY
        self.sender_id = settings.TERMII_SENDER_ID
    
    async def send_otp(
        self,
        phone_number: str,
        channel: str = "generic"
    ) -> Dict:
        """
        Send OTP to phone number
        
        Args:
            phone_number: Phone number (e.g., "2348012345678")
            channel: SMS channel (generic, dnd, whatsapp)
            
        Returns:
            dict with success status and otp_token
        """
        # Development mode: Return mock OTP
        if settings.ENVIRONMENT == "development":
            mock_otp = "123456"
            mock_token = create_otp_token(phone_number, mock_otp)
            logger.info(f"Development mode: Mock OTP sent to {phone_number}")
            return {
                "success": True,
                "otp_token": mock_token,
                "mock_otp": mock_otp,
                "message": "OTP sent (development mode)"
            }
        
        if not self.api_key:
            logger.warning("Termii API key not configured")
            return {
                "success": False,
                "error": "SMS service not configured"
            }
        
        # Generate OTP
        otp = generate_otp(length=6)
        
        # Prepare message
        message = f"Your BeatPush verification code is: {otp}. Valid for 5 minutes."
        
        # Send via Termii
        payload = {
            "to": phone_number,
            "from": self.sender_id,
            "sms": message,
            "type": "plain",
            "channel": channel,
            "api_key": self.api_key,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/sms/send",
                    json=payload,
                    timeout=30.0
                )
                
                result = response.json()
                
                if response.status_code == 200 and result.get("message_id"):
                    logger.info(f"OTP sent successfully to {phone_number}")
                    
                    # Create JWT token for OTP verification
                    otp_token = create_otp_token(phone_number, otp)
                    
                    return {
                        "success": True,
                        "otp_token": otp_token,
                        "message_id": result.get("message_id"),
                        "message": "OTP sent successfully"
                    }
                else:
                    logger.error(f"Termii error: {result}")
                    return {
                        "success": False,
                        "error": result.get("message", "Failed to send OTP")
                    }
                    
        except httpx.TimeoutException:
            logger.error("Termii API timeout")
            return {
                "success": False,
                "error": "SMS service timeout"
            }
        except Exception as e:
            logger.error(f"SMS send error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_message(
        self,
        phone_number: str,
        message: str,
        channel: str = "generic"
    ) -> Dict:
        """
        Send a custom SMS message
        
        Args:
            phone_number: Phone number
            message: Message to send
            channel: SMS channel
            
        Returns:
            dict with success status
        """
        if not self.api_key:
            logger.warning("Termii API key not configured")
            return {
                "success": False,
                "error": "SMS service not configured"
            }
        
        payload = {
            "to": phone_number,
            "from": self.sender_id,
            "sms": message,
            "type": "plain",
            "channel": channel,
            "api_key": self.api_key,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/sms/send",
                    json=payload,
                    timeout=30.0
                )
                
                result = response.json()
                
                if response.status_code == 200 and result.get("message_id"):
                    logger.info(f"SMS sent successfully to {phone_number}")
                    return {
                        "success": True,
                        "message_id": result.get("message_id")
                    }
                else:
                    logger.error(f"Termii error: {result}")
                    return {
                        "success": False,
                        "error": result.get("message", "Failed to send SMS")
                    }
                    
        except Exception as e:
            logger.error(f"SMS send error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_balance(self) -> Dict:
        """
        Get Termii account balance
        
        Returns:
            dict with balance information
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "SMS service not configured"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/get-balance",
                    params={"api_key": self.api_key},
                    timeout=10.0
                )
                
                result = response.json()
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "balance": result.get("balance"),
                        "currency": result.get("currency", "NGN")
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to get balance"
                    }
                    
        except Exception as e:
            logger.error(f"Balance check error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
sms_service = SMSService()
