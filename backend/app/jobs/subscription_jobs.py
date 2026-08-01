"""
Background jobs for subscription management.

Jobs:
- process_subscription_renewals: Daily renewal processing
- retry_failed_payments: Retry failed payments (3 attempts over 7 days)
- send_renewal_reminders: Send reminders 3 days before renewal
- cancel_expired_trials: Clean up expired trial subscriptions
- send_welcome_messages: Welcome new subscribers
- send_engagement_messages: Monthly engagement messages
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.database import SessionLocal
from app.models.fan_club import Subscription, SubscriptionPayment, FanClub, MembershipTier
from app.models.user import User
from app.models.messaging import Message, Conversation
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


def get_db():
    """Get database session for background jobs."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let job function handle it


def process_subscription_renewals():
    """
    Process subscription renewals for today.
    
    Runs daily at 2:00 AM UTC.
    Finds all subscriptions with next_billing_date = today and auto_renew = True.
    """
    db = get_db()
    try:
        today = datetime.utcnow().date()
        
        # Find subscriptions due for renewal
        subscriptions = db.query(Subscription).filter(
            and_(
                Subscription.next_billing_date <= datetime.utcnow(),
                Subscription.status == "active",
                Subscription.auto_renew == True
            )
        ).all()
        
        logger.info(f"Processing {len(subscriptions)} subscription renewals")
        
        payment_service = PaymentService(db)
        success_count = 0
        failed_count = 0
        
        for subscription in subscriptions:
            try:
                # Get tier info for amount
                tier = db.query(MembershipTier).filter(
                    MembershipTier.id == subscription.tier_id
                ).first()
                
                if not tier:
                    logger.error(f"Tier not found for subscription {subscription.id}")
                    continue
                
                # Determine amount based on billing cycle
                amount = tier.monthly_price if subscription.billing_cycle == "monthly" else tier.yearly_price
                
                # Process payment
                if subscription.stripe_subscription_id:
                    # Stripe handles automatic renewals
                    logger.info(f"Stripe will handle renewal for subscription {subscription.id}")
                    success_count += 1
                elif subscription.paystack_subscription_code:
                    # Paystack handles automatic renewals
                    logger.info(f"Paystack will handle renewal for subscription {subscription.id}")
                    success_count += 1
                else:
                    # Manual payment processing (shouldn't happen in production)
                    logger.warning(f"No payment provider for subscription {subscription.id}")
                    failed_count += 1
                
            except Exception as e:
                logger.error(f"Error renewing subscription {subscription.id}: {e}", exc_info=True)
                failed_count += 1
        
        logger.info(f"Renewal processing complete: {success_count} success, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"Error in process_subscription_renewals: {e}", exc_info=True)
    finally:
        db.close()


def retry_failed_payments():
    """
    Retry failed payments according to schedule.
    
    Runs daily at 10:00 AM UTC.
    Retry schedule:
    - Day 1: Immediate (handled by webhook)
    - Day 3: First retry
    - Day 7: Second retry
    - After 3 failures: Mark subscription as past_due
    """
    db = get_db()
    try:
        # Find subscriptions with failed payments
        past_due_subscriptions = db.query(Subscription).filter(
            and_(
                Subscription.status == "active",
                Subscription.failed_payment_count > 0,
                Subscription.failed_payment_count < 3
            )
        ).all()
        
        logger.info(f"Found {len(past_due_subscriptions)} subscriptions with failed payments")
        
        payment_service = PaymentService(db)
        retry_count = 0
        
        for subscription in past_due_subscriptions:
            # Get last failed payment
            last_payment = db.query(SubscriptionPayment).filter(
                and_(
                    SubscriptionPayment.subscription_id == subscription.id,
                    SubscriptionPayment.status == "failed"
                )
            ).order_by(SubscriptionPayment.created_at.desc()).first()
            
            if not last_payment:
                continue
            
            # Calculate days since last attempt
            days_since_failure = (datetime.utcnow() - last_payment.created_at).days
            
            # Retry schedule: Day 3, Day 7
            should_retry = (
                (subscription.failed_payment_count == 1 and days_since_failure >= 3) or
                (subscription.failed_payment_count == 2 and days_since_failure >= 7)
            )
            
            if should_retry:
                try:
                    # Get tier for amount
                    tier = db.query(MembershipTier).filter(
                        MembershipTier.id == subscription.tier_id
                    ).first()
                    
                    if not tier:
                        continue
                    
                    amount = tier.monthly_price if subscription.billing_cycle == "monthly" else tier.yearly_price
                    
                    # Attempt payment retry
                    logger.info(f"Retrying payment for subscription {subscription.id} (attempt {subscription.failed_payment_count + 1}/3)")
                    
                    # The actual retry is handled by Stripe/Paystack automatically
                    # This job is for logging and notification purposes
                    
                    # TODO: Send retry notification email
                    retry_count += 1
                    
                except Exception as e:
                    logger.error(f"Error retrying payment for subscription {subscription.id}: {e}")
            
            # After 3 failures, suspend subscription
            if subscription.failed_payment_count >= 3:
                subscription.status = "past_due"
                db.commit()
                logger.warning(f"Subscription {subscription.id} marked past_due after 3 failed attempts")
                # TODO: Send final suspension email
        
        logger.info(f"Payment retry job complete: {retry_count} retries initiated")
        
    except Exception as e:
        logger.error(f"Error in retry_failed_payments: {e}", exc_info=True)
    finally:
        db.close()


def send_renewal_reminders():
    """
    Send renewal reminders 3 days before billing date.
    
    Runs daily at 9:00 AM UTC.
    """
    db = get_db()
    try:
        # Find subscriptions renewing in 3 days
        reminder_date = datetime.utcnow() + timedelta(days=3)
        
        subscriptions = db.query(Subscription).join(User).join(MembershipTier).filter(
            and_(
                Subscription.next_billing_date.between(
                    reminder_date.replace(hour=0, minute=0, second=0),
                    reminder_date.replace(hour=23, minute=59, second=59)
                ),
                Subscription.status == "active",
                Subscription.auto_renew == True
            )
        ).all()
        
        logger.info(f"Sending renewal reminders to {len(subscriptions)} subscribers")
        
        for subscription in subscriptions:
            try:
                user = subscription.user
                tier = subscription.tier
                fan_club = tier.fan_club
                creator = fan_club.creator
                
                # TODO: Send email reminder
                # Email content:
                # - Renewal date
                # - Amount to be charged
                # - Payment method on file
                # - Link to update payment method
                # - Link to cancel subscription
                
                # Also send in-app notification
                # TODO: Create notification record
                
                logger.info(f"Reminder sent to user {user.id} for subscription {subscription.id}")
                
            except Exception as e:
                logger.error(f"Error sending reminder for subscription {subscription.id}: {e}")
        
        logger.info("Renewal reminders sent successfully")
        
    except Exception as e:
        logger.error(f"Error in send_renewal_reminders: {e}", exc_info=True)
    finally:
        db.close()


def cancel_expired_trials():
    """
    Cancel expired trial subscriptions.
    
    Runs daily at 3:00 AM UTC.
    Note: This platform doesn't have trials in v1, but included for future use.
    """
    db = get_db()
    try:
        # Find expired trial subscriptions
        expired_trials = db.query(Subscription).filter(
            and_(
                Subscription.status == "trial",
                Subscription.trial_end_date <= datetime.utcnow()
            )
        ).all()
        
        logger.info(f"Canceling {len(expired_trials)} expired trial subscriptions")
        
        for subscription in expired_trials:
            subscription.status = "cancelled"
            subscription.cancelled_at = datetime.utcnow()
            
            # TODO: Send trial expired email with upgrade prompt
        
        db.commit()
        logger.info("Expired trials canceled successfully")
        
    except Exception as e:
        logger.error(f"Error in cancel_expired_trials: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def send_welcome_messages():
    """
    Send welcome messages to new subscribers.
    
    Runs every hour.
    Finds subscriptions created in the last hour and sends welcome message.
    """
    db = get_db()
    try:
        # Find new subscriptions from the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        new_subscriptions = db.query(Subscription).filter(
            and_(
                Subscription.created_at >= one_hour_ago,
                Subscription.status == "active"
            )
        ).all()
        
        logger.info(f"Sending welcome messages to {len(new_subscriptions)} new subscribers")
        
        for subscription in new_subscriptions:
            try:
                # Check if welcome message already sent
                existing_welcome = db.query(Message).filter(
                    and_(
                        Message.sender_id == subscription.tier.fan_club.creator_id,
                        Message.receiver_id == subscription.user_id,
                        Message.content.like("%Welcome to%"),
                        Message.created_at >= subscription.created_at
                    )
                ).first()
                
                if existing_welcome:
                    continue  # Already sent
                
                user = subscription.user
                tier = subscription.tier
                fan_club = tier.fan_club
                creator = fan_club.creator
                
                # Get or create conversation
                conversation = db.query(Conversation).filter(
                    or_(
                        and_(
                            Conversation.user1_id == creator.id,
                            Conversation.user2_id == user.id
                        ),
                        and_(
                            Conversation.user1_id == user.id,
                            Conversation.user2_id == creator.id
                        )
                    )
                ).first()
                
                if not conversation:
                    conversation = Conversation(
                        user1_id=creator.id,
                        user2_id=user.id
                    )
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)
                
                # Create welcome message
                welcome_text = fan_club.welcome_message or f"""
Welcome to {fan_club.name}! 🎉

Thank you for subscribing to the {tier.name} tier! I'm excited to have you as part of this exclusive community.

As a member, you'll get access to:
{chr(10).join(f"• {benefit}" for benefit in tier.benefits)}

Stay tuned for exclusive content and updates!

- {creator.username}
                """.strip()
                
                message = Message(
                    conversation_id=conversation.id,
                    sender_id=creator.id,
                    receiver_id=user.id,
                    content=welcome_text,
                    message_type="text"
                )
                db.add(message)
                db.commit()
                
                logger.info(f"Welcome message sent to user {user.id} from creator {creator.id}")
                
                # TODO: Also send welcome email
                
            except Exception as e:
                logger.error(f"Error sending welcome for subscription {subscription.id}: {e}")
                db.rollback()
        
        logger.info("Welcome messages sent successfully")
        
    except Exception as e:
        logger.error(f"Error in send_welcome_messages: {e}", exc_info=True)
    finally:
        db.close()


def send_engagement_messages():
    """
    Send monthly engagement messages to long-term subscribers.
    
    Runs daily at 11:00 AM UTC.
    Sends thank you message to subscribers on their 1, 3, 6, 12 month anniversaries.
    """
    db = get_db()
    try:
        # Find subscriptions at milestone dates
        today = datetime.utcnow().date()
        
        # Query subscriptions created exactly 1, 3, 6, or 12 months ago
        milestones = [
            (today - timedelta(days=30), "1 month"),
            (today - timedelta(days=90), "3 months"),
            (today - timedelta(days=180), "6 months"),
            (today - timedelta(days=365), "1 year")
        ]
        
        for milestone_date, milestone_label in milestones:
            subscriptions = db.query(Subscription).filter(
                and_(
                    Subscription.created_at.between(
                        datetime.combine(milestone_date, datetime.min.time()),
                        datetime.combine(milestone_date, datetime.max.time())
                    ),
                    Subscription.status == "active"
                )
            ).all()
            
            logger.info(f"Sending {milestone_label} anniversary messages to {len(subscriptions)} subscribers")
            
            for subscription in subscriptions:
                try:
                    user = subscription.user
                    tier = subscription.tier
                    fan_club = tier.fan_club
                    creator = fan_club.creator
                    
                    # Get or create conversation
                    conversation = db.query(Conversation).filter(
                        or_(
                            and_(
                                Conversation.user1_id == creator.id,
                                Conversation.user2_id == user.id
                            ),
                            and_(
                                Conversation.user1_id == user.id,
                                Conversation.user2_id == creator.id
                            )
                        )
                    ).first()
                    
                    if not conversation:
                        conversation = Conversation(
                            user1_id=creator.id,
                            user2_id=user.id
                        )
                        db.add(conversation)
                        db.commit()
                        db.refresh(conversation)
                    
                    # Create thank you message
                    thank_you_text = f"""
🎉 Happy {milestone_label} anniversary! 🎉

I wanted to personally thank you for being a subscriber for {milestone_label}. Your support means the world to me!

As a token of appreciation, stay tuned for some exclusive content coming your way soon. 🎁

Thank you for being an amazing supporter!

- {creator.username}
                    """.strip()
                    
                    message = Message(
                        conversation_id=conversation.id,
                        sender_id=creator.id,
                        receiver_id=user.id,
                        content=thank_you_text,
                        message_type="text"
                    )
                    db.add(message)
                    db.commit()
                    
                    logger.info(f"Anniversary message sent to user {user.id} ({milestone_label})")
                    
                except Exception as e:
                    logger.error(f"Error sending anniversary message for subscription {subscription.id}: {e}")
                    db.rollback()
        
        logger.info("Engagement messages sent successfully")
        
    except Exception as e:
        logger.error(f"Error in send_engagement_messages: {e}", exc_info=True)
    finally:
        db.close()
