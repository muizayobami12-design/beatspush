"""
WhatsApp Service - Twilio Integration
Handles WhatsApp messaging for BeatPush
Broadcasts to fans, notifications, fan club groups
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Manages WhatsApp communications for the platform"""
    
    def __init__(self):
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.client = Client(account_sid, auth_token)
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+1234567890")
    
    # ============ INDIVIDUAL MESSAGES ============
    
    async def send_message(self, recipient_number: str, message_text: str, 
                          media_url: Optional[str] = None):
        """Send WhatsApp message to individual user"""
        try:
            recipient = f"whatsapp:{recipient_number}"
            
            if media_url:
                message = self.client.messages.create(
                    from_=self.whatsapp_number,
                    body=message_text,
                    media_url=media_url,
                    to=recipient
                )
            else:
                message = self.client.messages.create(
                    from_=self.whatsapp_number,
                    body=message_text,
                    to=recipient
                )
            
            logger.info(f"WhatsApp message sent to {recipient_number}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return False
    
    # ============ TRANSACTION NOTIFICATIONS ============
    
    async def notify_tip_received(self, recipient_number: str, 
                                 tipper_name: str, amount: float):
        """Notify user about received tip"""
        try:
            message_text = f"""
🎵 *New Tip Received!*

{tipper_name} sent you ₦{amount:,.0f} 💰

Thank you for amazing content! 🙏

Visit BeatPush to see more: https://beatpush.com/tips
            """.strip()
            
            return await self.send_message(recipient_number, message_text)
        except Exception as e:
            logger.error(f"Failed to send tip notification: {str(e)}")
            return False
    
    async def notify_beat_purchased(self, producer_number: str, 
                                   buyer_name: str, beat_title: str, 
                                   amount: float):
        """Notify producer about beat purchase"""
        try:
            message_text = f"""
🎉 *Beat Sold!*

{buyer_name} purchased "{beat_title}"
Earnings: ₦{amount:,.0f}

Check your dashboard: https://beatpush.com/dashboard/analytics
            """.strip()
            
            return await self.send_message(producer_number, message_text)
        except Exception as e:
            logger.error(f"Failed to send beat sold notification: {str(e)}")
            return False
    
    async def notify_booking_confirmed(self, dj_number: str, 
                                      client_name: str, event_date: str):
        """Notify DJ about confirmed booking"""
        try:
            message_text = f"""
📅 *Booking Confirmed!*

Client: {client_name}
Date: {event_date}

View details: https://beatpush.com/bookings
            """.strip()
            
            return await self.send_message(dj_number, message_text)
        except Exception as e:
            logger.error(f"Failed to send booking notification: {str(e)}")
            return False
    
    async def notify_new_follower(self, creator_number: str, 
                                 follower_name: str):
        """Notify creator about new follower"""
        try:
            message_text = f"""
👥 *New Follower!*

{follower_name} is now following you!

Keep creating amazing content! 🎵
            """.strip()
            
            return await self.send_message(creator_number, message_text)
        except Exception as e:
            logger.error(f"Failed to send follower notification: {str(e)}")
            return False
    
    async def notify_submission_status(self, artist_number: str, 
                                      dj_name: str, status: str, 
                                      notes: Optional[str] = None):
        """Notify artist about submission status"""
        try:
            status_emoji = "✅" if status == "accepted" else "❌"
            message_text = f"""
{status_emoji} *Submission {status.upper()}!*

DJ: {dj_name}
Notes: {notes or 'No additional notes'}

View submission: https://beatpush.com/submissions
            """.strip()
            
            return await self.send_message(artist_number, message_text)
        except Exception as e:
            logger.error(f"Failed to send submission notification: {str(e)}")
            return False
    
    # ============ FAN CLUB GROUP MESSAGES ============
    
    async def create_fan_club_group(self, creator_name: str, 
                                   group_name: str) -> Optional[str]:
        """Create WhatsApp fan club group"""
        try:
            # In production, use Twilio Group API
            # For now, return group ID format
            group_id = f"fc_{creator_name.lower()}_{datetime.now().timestamp()}"
            logger.info(f"Fan club group created: {group_id}")
            return group_id
        except Exception as e:
            logger.error(f"Failed to create fan club group: {str(e)}")
            return None
    
    async def add_member_to_group(self, group_id: str, 
                                 member_number: str):
        """Add member to fan club group"""
        try:
            # In production, use Twilio Group API
            logger.info(f"Added {member_number} to group {group_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add member to group: {str(e)}")
            return False
    
    async def remove_member_from_group(self, group_id: str, 
                                      member_number: str):
        """Remove member from fan club group"""
        try:
            logger.info(f"Removed {member_number} from group {group_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove member from group: {str(e)}")
            return False
    
    async def send_group_message(self, group_id: str, message_text: str):
        """Send message to entire fan club group"""
        try:
            # In production, use Twilio Group messaging API
            logger.info(f"Group message sent to {group_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send group message: {str(e)}")
            return False
    
    # ============ BROADCAST MESSAGES ============
    
    async def broadcast_announcement(self, recipient_numbers: List[str], 
                                    announcement_text: str):
        """Send announcement to multiple users"""
        try:
            success_count = 0
            for number in recipient_numbers:
                if await self.send_message(number, announcement_text):
                    success_count += 1
            
            logger.info(f"Broadcast sent to {success_count}/{len(recipient_numbers)} recipients")
            return success_count
        except Exception as e:
            logger.error(f"Failed to send broadcast: {str(e)}")
            return 0
    
    async def broadcast_new_release(self, creator_name: str, 
                                   content_title: str, 
                                   content_type: str,
                                   recipient_numbers: List[str]):
        """Broadcast new content release to followers"""
        try:
            announcement_text = f"""
🎵 *New {content_type.capitalize()} Released!*

Artist: {creator_name}
Title: {content_title}

Listen now: https://beatpush.com/discover

*Available for a limited time!* ⏰
            """.strip()
            
            return await self.broadcast_announcement(recipient_numbers, announcement_text)
        except Exception as e:
            logger.error(f"Failed to broadcast new release: {str(e)}")
            return 0
    
    async def broadcast_exclusive_content(self, creator_name: str, 
                                         fan_club_subscribers: List[str]):
        """Broadcast exclusive content to fan club members"""
        try:
            announcement_text = f"""
⭐ *Exclusive Content from {creator_name}!*

Check your fan club for special content 🎁
Only for subscribers like you!

Access now: https://beatpush.com/fanclubs/{creator_name}
            """.strip()
            
            return await self.broadcast_announcement(fan_club_subscribers, announcement_text)
        except Exception as e:
            logger.error(f"Failed to broadcast exclusive content: {str(e)}")
            return 0
    
    # ============ PROMOTIONAL MESSAGES ============
    
    async def send_promotional_message(self, recipient_numbers: List[str], 
                                      promotion_text: str, 
                                      image_url: Optional[str] = None):
        """Send promotional message to users"""
        try:
            success_count = 0
            for number in recipient_numbers:
                if await self.send_message(number, promotion_text, image_url):
                    success_count += 1
            
            logger.info(f"Promotional messages sent to {success_count}/{len(recipient_numbers)}")
            return success_count
        except Exception as e:
            logger.error(f"Failed to send promotional message: {str(e)}")
            return 0
    
    # ============ REMINDERS ============
    
    async def send_subscription_reminder(self, subscriber_number: str, 
                                        creator_name: str, 
                                        renewal_date: str):
        """Send subscription renewal reminder"""
        try:
            message_text = f"""
🔔 *Subscription Renewal Reminder*

Your subscription to {creator_name}'s fan club
renews on {renewal_date}

Manage subscription: https://beatpush.com/subscriptions
            """.strip()
            
            return await self.send_message(subscriber_number, message_text)
        except Exception as e:
            logger.error(f"Failed to send reminder: {str(e)}")
            return False
    
    async def send_payment_reminder(self, user_number: str, 
                                   amount: float, 
                                   due_date: str):
        """Send payment due reminder"""
        try:
            message_text = f"""
💳 *Payment Reminder*

Amount due: ₦{amount:,.0f}
Due date: {due_date}

Pay now: https://beatpush.com/payments
            """.strip()
            
            return await self.send_message(user_number, message_text)
        except Exception as e:
            logger.error(f"Failed to send payment reminder: {str(e)}")
            return False
    
    # ============ OTP & AUTHENTICATION ============
    
    async def send_otp(self, recipient_number: str, otp_code: str):
        """Send one-time password for authentication"""
        try:
            message_text = f"""
🔐 BeatPush OTP: {otp_code}

This code expires in 10 minutes.
Do not share this code with anyone.
            """.strip()
            
            return await self.send_message(recipient_number, message_text)
        except Exception as e:
            logger.error(f"Failed to send OTP: {str(e)}")
            return False
    
    # ============ SUPPORT MESSAGES ============
    
    async def send_support_response(self, user_number: str, 
                                   ticket_id: str, 
                                   response_text: str):
        """Send support ticket response"""
        try:
            message_text = f"""
🆘 *Support Response*

Ticket ID: {ticket_id}

{response_text}

Reply to this message or visit: https://beatpush.com/support
            """.strip()
            
            return await self.send_message(user_number, message_text)
        except Exception as e:
            logger.error(f"Failed to send support response: {str(e)}")
            return False


# Global instance
whatsapp_service = WhatsAppService()
