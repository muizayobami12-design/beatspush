"""
Email Service - Send emails using SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: str = None
    ) -> bool:
        """
        Send an email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text email body (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not settings.EMAIL_ENABLED:
            logger.warning("Email sending is disabled")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            message["To"] = to_email
            
            # Add plain text version
            if plain_content:
                part1 = MIMEText(plain_content, "plain")
                message.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()  # Secure the connection
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(email: str, reset_token: str) -> bool:
        """
        Send password reset email
        
        Args:
            email: User's email address
            reset_token: Password reset token
            
        Returns:
            True if email sent successfully
        """
        # Create reset link (frontend will handle this)
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}" if hasattr(settings, 'FRONTEND_URL') else f"https://beatspush-1.onrender.com/reset-password?token={reset_token}"
        
        # HTML email template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 BeatPush</h1>
            <p>Password Reset Request</p>
        </div>
        <div class="content">
            <h2>Hello!</h2>
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            <div style="text-align: center;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </div>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: white; padding: 10px; border-radius: 5px;">{reset_link}</p>
            <p><strong>This link will expire in 1 hour.</strong></p>
            <p>If you didn't request a password reset, you can safely ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2026 BeatPush - AI-Powered Music Promotion Platform</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Plain text version
        plain_content = f"""
BeatPush - Password Reset Request

Hello!

We received a request to reset your password. Click the link below to create a new password:

{reset_link}

This link will expire in 1 hour.

If you didn't request a password reset, you can safely ignore this email.

© 2026 BeatPush - AI-Powered Music Promotion Platform
        """
        
        return EmailService.send_email(
            to_email=email,
            subject="Reset Your BeatPush Password",
            html_content=html_content,
            plain_content=plain_content
        )
    
    @staticmethod
    def send_verification_email(email: str, verification_token: str) -> bool:
        """
        Send email verification email
        
        Args:
            email: User's email address
            verification_token: Email verification token
            
        Returns:
            True if email sent successfully
        """
        # Create verification link
        verify_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}" if hasattr(settings, 'FRONTEND_URL') else f"https://beatspush-1.onrender.com/api/v1/auth/verify-email/{verification_token}"
        
        # HTML email template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Welcome to BeatPush!</h1>
        </div>
        <div class="content">
            <h2>Verify Your Email</h2>
            <p>Thanks for signing up! Please verify your email address by clicking the button below:</p>
            <div style="text-align: center;">
                <a href="{verify_link}" class="button">Verify Email</a>
            </div>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: white; padding: 10px; border-radius: 5px;">{verify_link}</p>
            <p><strong>This link will expire in 24 hours.</strong></p>
        </div>
        <div class="footer">
            <p>© 2026 BeatPush - AI-Powered Music Promotion Platform</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Plain text version
        plain_content = f"""
Welcome to BeatPush!

Thanks for signing up! Please verify your email address by clicking the link below:

{verify_link}

This link will expire in 24 hours.

© 2026 BeatPush - AI-Powered Music Promotion Platform
        """
        
        return EmailService.send_email(
            to_email=email,
            subject="Verify Your BeatPush Email",
            html_content=html_content,
            plain_content=plain_content
        )
    
    @staticmethod
    def send_welcome_email(email: str, username: str) -> bool:
        """
        Send welcome email to new users
        
        Args:
            email: User's email address
            username: User's username
            
        Returns:
            True if email sent successfully
        """
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Welcome to BeatPush!</h1>
        </div>
        <div class="content">
            <h2>Hey {username}! 👋</h2>
            <p>Welcome to the future of music promotion! We're excited to have you join our community.</p>
            
            <h3>What you can do with BeatPush:</h3>
            <div class="feature">
                <strong>🎵 Share Your Music</strong> - Upload and promote your beats, tracks, and albums
            </div>
            <div class="feature">
                <strong>🤖 AI-Powered Marketing</strong> - Get intelligent campaign suggestions and content generation
            </div>
            <div class="feature">
                <strong>💬 Connect with Fans</strong> - Real-time messaging and fan club management
            </div>
            <div class="feature">
                <strong>📊 Track Analytics</strong> - Monitor your performance and audience engagement
            </div>
            <div class="feature">
                <strong>💰 Monetize</strong> - Sell beats, accept tips, and offer bookings
            </div>
            
            <p>Ready to get started? Log in to your dashboard and explore!</p>
        </div>
        <div class="footer">
            <p>© 2026 BeatPush - AI-Powered Music Promotion Platform</p>
            <p>Need help? Contact us anytime!</p>
        </div>
    </div>
</body>
</html>
        """
        
        plain_content = f"""
Welcome to BeatPush!

Hey {username}! 

Welcome to the future of music promotion! We're excited to have you join our community.

What you can do with BeatPush:
- 🎵 Share Your Music - Upload and promote your beats, tracks, and albums
- 🤖 AI-Powered Marketing - Get intelligent campaign suggestions
- 💬 Connect with Fans - Real-time messaging and fan club management
- 📊 Track Analytics - Monitor your performance
- 💰 Monetize - Sell beats, accept tips, and offer bookings

Ready to get started? Log in to your dashboard and explore!

© 2026 BeatPush - AI-Powered Music Promotion Platform
        """
        
        return EmailService.send_email(
            to_email=email,
            subject="Welcome to BeatPush! 🎵",
            html_content=html_content,
            plain_content=plain_content
        )
