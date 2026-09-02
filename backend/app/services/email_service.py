"""
Email Service - SendGrid Integration
Handles transactional and marketing emails for BeatPush
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from jinja2 import Template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Manages all email communications for the platform"""
    
    def __init__(self):
        self.sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@beatpush.com")
        self.from_name = "BeatPush"
    
    # ============ EMAIL TEMPLATES ============
    
    EMAIL_TEMPLATES = {
        "welcome": {
            "subject": "Welcome to BeatPush! 🎵",
            "template_id": "d-welcome-email"
        },
        "verify_email": {
            "subject": "Verify Your BeatPush Email",
            "template_id": "d-verify-email"
        },
        "password_reset": {
            "subject": "Reset Your BeatPush Password",
            "template_id": "d-password-reset"
        },
        "tip_received": {
            "subject": "You received a tip! 💰",
            "template_id": "d-tip-received"
        },
        "beat_sold": {
            "subject": "Your beat was purchased! 🎉",
            "template_id": "d-beat-sold"
        },
        "booking_confirmed": {
            "subject": "Booking Confirmed ✅",
            "template_id": "d-booking-confirmed"
        },
        "subscription_active": {
            "subject": "Fan Club Subscription Active",
            "template_id": "d-subscription-active"
        },
        "submission_accepted": {
            "subject": "Your submission was accepted! 🎉",
            "template_id": "d-submission-accepted"
        },
        "daily_digest": {
            "subject": "Your Daily BeatPush Summary",
            "template_id": "d-daily-digest"
        },
        "weekly_report": {
            "subject": "Your Weekly Performance Report",
            "template_id": "d-weekly-report"
        }
    }
    
    # ============ TRANSACTIONAL EMAILS ============
    
    async def send_welcome_email(self, email: str, full_name: str, user_type: str):
        """Send welcome email to new user"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(email),
                subject=self.EMAIL_TEMPLATES["welcome"]["subject"],
                plain_text_content=f"Welcome {full_name}! You're now a {user_type} on BeatPush."
            )
            
            message.template_id = self.EMAIL_TEMPLATES["welcome"]["template_id"]
            message.dynamic_template_data = {
                "full_name": full_name,
                "user_type": user_type,
                "dashboard_url": "https://beatpush.com/dashboard",
                "support_email": "support@beatpush.com"
            }
            
            response = self.sg.send(message)
            logger.info(f"Welcome email sent to {email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False
    
    async def send_email_verification(self, email: str, verification_code: str):
        """Send email verification code"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(email),
                subject=self.EMAIL_TEMPLATES["verify_email"]["subject"]
            )
            
            message.template_id = self.EMAIL_TEMPLATES["verify_email"]["template_id"]
            message.dynamic_template_data = {
                "verification_code": verification_code,
                "verification_url": f"https://beatpush.com/verify/{verification_code}",
                "expires_in": "24 hours"
            }
            
            response = self.sg.send(message)
            logger.info(f"Verification email sent to {email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False
    
    async def send_password_reset(self, email: str, reset_token: str):
        """Send password reset link"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(email),
                subject=self.EMAIL_TEMPLATES["password_reset"]["subject"]
            )
            
            message.template_id = self.EMAIL_TEMPLATES["password_reset"]["template_id"]
            message.dynamic_template_data = {
                "reset_url": f"https://beatpush.com/reset-password/{reset_token}",
                "expires_in": "2 hours",
                "support_email": "support@beatpush.com"
            }
            
            response = self.sg.send(message)
            logger.info(f"Password reset email sent to {email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False
    
    async def send_tip_received(self, recipient_email: str, tipper_name: str, 
                               amount: float, message: str = None):
        """Send tip received notification"""
        try:
            subject = f"You received a tip from {tipper_name}! 💰"
            message_obj = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(recipient_email),
                subject=subject
            )
            
            message_obj.template_id = self.EMAIL_TEMPLATES["tip_received"]["template_id"]
            message_obj.dynamic_template_data = {
                "tipper_name": tipper_name,
                "amount": f"₦{amount:,.0f}",
                "message": message or "No message",
                "dashboard_url": "https://beatpush.com/dashboard/tips"
            }
            
            response = self.sg.send(message_obj)
            logger.info(f"Tip notification sent to {recipient_email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send tip notification: {str(e)}")
            return False
    
    async def send_beat_sold(self, producer_email: str, buyer_name: str, 
                            beat_title: str, amount: float):
        """Send beat purchase notification"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(producer_email),
                subject=self.EMAIL_TEMPLATES["beat_sold"]["subject"]
            )
            
            message.template_id = self.EMAIL_TEMPLATES["beat_sold"]["template_id"]
            message.dynamic_template_data = {
                "buyer_name": buyer_name,
                "beat_title": beat_title,
                "amount": f"₦{amount:,.0f}",
                "earnings_dashboard": "https://beatpush.com/dashboard/analytics"
            }
            
            response = self.sg.send(message)
            logger.info(f"Beat sold notification sent to {producer_email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send beat sold notification: {str(e)}")
            return False
    
    async def send_booking_confirmed(self, dj_email: str, client_name: str,
                                    event_date: str, location: str):
        """Send booking confirmation email"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(dj_email),
                subject=self.EMAIL_TEMPLATES["booking_confirmed"]["subject"]
            )
            
            message.template_id = self.EMAIL_TEMPLATES["booking_confirmed"]["template_id"]
            message.dynamic_template_data = {
                "client_name": client_name,
                "event_date": event_date,
                "location": location,
                "bookings_url": "https://beatpush.com/dashboard/bookings"
            }
            
            response = self.sg.send(message)
            logger.info(f"Booking confirmation sent to {dj_email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send booking confirmation: {str(e)}")
            return False
    
    async def send_subscription_active(self, fan_email: str, creator_name: str, 
                                      tier_price: float):
        """Send subscription confirmation"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(fan_email),
                subject=self.EMAIL_TEMPLATES["subscription_active"]["subject"]
            )
            
            message.template_id = self.EMAIL_TEMPLATES["subscription_active"]["template_id"]
            message.dynamic_template_data = {
                "creator_name": creator_name,
                "tier_price": f"₦{tier_price:,.0f}",
                "renews_on": (datetime.now().replace(day=1).replace(month=(datetime.now().month % 12) + 1)).strftime("%B %d"),
                "exclusive_content_url": "https://beatpush.com/dashboard/subscriptions"
            }
            
            response = self.sg.send(message)
            logger.info(f"Subscription confirmation sent to {fan_email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send subscription confirmation: {str(e)}")
            return False
    
    async def send_submission_accepted(self, artist_email: str, dj_name: str):
        """Send submission accepted notification"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(artist_email),
                subject=self.EMAIL_TEMPLATES["submission_accepted"]["subject"]
            )
            
            message.template_id = self.EMAIL_TEMPLATES["submission_accepted"]["template_id"]
            message.dynamic_template_data = {
                "dj_name": dj_name,
                "submissions_url": "https://beatpush.com/dashboard/submissions",
                "share_url": "https://beatpush.com/share/success"
            }
            
            response = self.sg.send(message)
            logger.info(f"Submission accepted email sent to {artist_email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send submission accepted email: {str(e)}")
            return False
    
    # ============ DIGEST EMAILS ============
    
    async def send_daily_digest(self, email: str, user_name: str, 
                               stats: Dict[str, Any]):
        """Send daily performance digest"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(email),
                subject=self.EMAIL_TEMPLATES["daily_digest"]["subject"]
            )
            
            message.template_id = self.EMAIL_TEMPLATES["daily_digest"]["template_id"]
            message.dynamic_template_data = {
                "user_name": user_name,
                "plays_today": stats.get("plays", 0),
                "tips_today": f"₦{stats.get('tips', 0):,.0f}",
                "new_followers": stats.get("new_followers", 0),
                "dashboard_url": "https://beatpush.com/dashboard/analytics"
            }
            
            response = self.sg.send(message)
            logger.info(f"Daily digest sent to {email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send daily digest: {str(e)}")
            return False
    
    async def send_weekly_report(self, email: str, user_name: str, 
                                report_data: Dict[str, Any]):
        """Send weekly performance report"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(email),
                subject=self.EMAIL_TEMPLATES["weekly_report"]["subject"]
            )
            
            message.template_id = self.EMAIL_TEMPLATES["weekly_report"]["template_id"]
            message.dynamic_template_data = {
                "user_name": user_name,
                "total_plays": report_data.get("total_plays", 0),
                "total_revenue": f"₦{report_data.get('total_revenue', 0):,.0f}",
                "top_content": report_data.get("top_content", "N/A"),
                "audience_growth": f"{report_data.get('audience_growth', 0)}%",
                "report_url": "https://beatpush.com/dashboard/analytics"
            }
            
            response = self.sg.send(message)
            logger.info(f"Weekly report sent to {email}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send weekly report: {str(e)}")
            return False
    
    # ============ BULK EMAIL ============
    
    async def send_bulk_announcement(self, recipients: List[str], 
                                    subject: str, content: str):
        """Send bulk announcement to multiple recipients"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                subject=subject,
                plain_text_content=content
            )
            
            for recipient in recipients:
                message.add_to(To(recipient))
            
            response = self.sg.send(message)
            logger.info(f"Announcement sent to {len(recipients)} recipients")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send bulk announcement: {str(e)}")
            return False
    
    # ============ BATCH OPERATIONS ============
    
    async def queue_transactional_email(self, email_type: str, 
                                       recipient_email: str, 
                                       data: Dict[str, Any]):
        """Queue email for async processing"""
        try:
            # In production, this would queue to Celery/RabbitMQ
            email_queue = {
                "type": email_type,
                "recipient": recipient_email,
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
            
            logger.info(f"Email queued: {email_type} to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to queue email: {str(e)}")
            return False


# Global instance
email_service = EmailService()
