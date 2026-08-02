"""
Test email endpoint for debugging
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.email_service import EmailService
from app.core.config import settings
import traceback

router = APIRouter(prefix="/test", tags=["Testing"])


class TestEmailRequest(BaseModel):
    """Test email request"""
    to_email: EmailStr


@router.post("/send-test-email")
async def send_test_email(request: TestEmailRequest):
    """
    Send a test email to verify SMTP configuration
    
    This endpoint will:
    1. Attempt to send a test email
    2. Return detailed error information if it fails
    3. Show SMTP configuration (without password)
    """
    try:
        # Show configuration (without password)
        config_info = {
            "SMTP_HOST": settings.SMTP_HOST,
            "SMTP_PORT": settings.SMTP_PORT,
            "SMTP_USER": settings.SMTP_USER,
            "EMAILS_FROM_EMAIL": settings.EMAILS_FROM_EMAIL,
            "EMAILS_FROM_NAME": settings.EMAILS_FROM_NAME,
            "EMAIL_ENABLED": settings.EMAIL_ENABLED,
            "SMTP_PASSWORD_SET": bool(settings.SMTP_PASSWORD),
        }
        
        # Try to send email
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .success { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🎉 Email Test Successful!</h1>
    <p class="success">Your BeatPush email configuration is working correctly!</p>
    <p>If you received this email, your SMTP settings are properly configured.</p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        © 2026 BeatPush - AI-Powered Music Promotion Platform
    </p>
</body>
</html>
        """
        
        plain_content = """
Email Test Successful!

Your BeatPush email configuration is working correctly!

If you received this email, your SMTP settings are properly configured.

© 2026 BeatPush - AI-Powered Music Promotion Platform
        """
        
        success = EmailService.send_email(
            to_email=request.to_email,
            subject="BeatPush Email Test",
            html_content=html_content,
            plain_content=plain_content
        )
        
        if success:
            return {
                "success": True,
                "message": f"Test email sent successfully to {request.to_email}",
                "smtp_config": config_info
            }
        else:
            return {
                "success": False,
                "message": "Email sending returned False (check server logs for details)",
                "smtp_config": config_info
            }
            
    except Exception as e:
        # Return detailed error information
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "smtp_config": {
                "SMTP_HOST": settings.SMTP_HOST,
                "SMTP_PORT": settings.SMTP_PORT,
                "SMTP_USER": settings.SMTP_USER,
                "SMTP_PASSWORD_SET": bool(settings.SMTP_PASSWORD),
            }
        }
        
        return {
            "success": False,
            "message": "Email sending failed with error",
            "error": error_details
        }


@router.get("/smtp-config")
async def get_smtp_config():
    """
    Get current SMTP configuration (without password)
    """
    return {
        "SMTP_HOST": settings.SMTP_HOST,
        "SMTP_PORT": settings.SMTP_PORT,
        "SMTP_USER": settings.SMTP_USER,
        "SMTP_PASSWORD_LENGTH": len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 0,
        "SMTP_PASSWORD_SET": bool(settings.SMTP_PASSWORD),
        "EMAILS_FROM_EMAIL": settings.EMAILS_FROM_EMAIL,
        "EMAILS_FROM_NAME": settings.EMAILS_FROM_NAME,
        "EMAIL_ENABLED": settings.EMAIL_ENABLED,
    }
