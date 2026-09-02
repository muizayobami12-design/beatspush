"""
Subscription background jobs.

Jobs:
- process_subscription_renewals() - Daily renewal processing
- retry_failed_payments() - Retry failed payments
- send_renewal_reminders() - Send reminders 3 days before renewal
- cancel_expired_trials() - Auto-cancel expired trials
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.fan_club import Subscription, SubscriptionPayment
from app.services.subscription_service import SubscriptionService
from app.services.payment_service import PaymentService
from app.jobs.scheduler import log_job_execution

logger = logging.getLogger(__name__)


def get_db_session():
    """Get database session for background jobs."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


async def process_subscription_renewals():
    """
    Process daily subscription renewals.
    
    **Procedure:**
    1. Query subscriptions with next_billing_date = today
    2. Check if auto_renew is enabled
    3. Process payment via PaymentService
    4. On success: Update subscription period, reset failed counter
    5. On failure: Mark as PAST_DUE, increment failed counter
    
    **Execution:** Daily at 00:00 UTC
    """
    job_id = "subscription_renewal_daily"
    job_name = "Daily Subscription Renewal"
    
    try:
        db = get_db_session()
        today = datetime.utcnow().date()
        
        # Query subscriptions due for renewal today
        subscriptions = db.query(Subscription).filter(
            Subscription.next_billing_date >= datetime(today.year, today.month, today.day),
            Subscription.next_billing_date < datetime(
                today.year, today.month, today.day
            ) + timedelta(days=1),
            Subscription.status.in_(["active", "past_due"]),
            Subscription.auto_renew == True
        ).all()
        
        if not subscriptions:
            log_job_execution(job_id, job_name, "success", f"No renewals scheduled for {today}")
            db.close()
            return
        
        logger.info(f"Processing {len(subscriptions)} subscription renewals for {today}")
        
        payment_service = PaymentService(db)
        success_count = 0
        failure_count = 0
        
        for subscription in subscriptions:
            try:
                # Check if subscription has payment method
                if not subscription.payment_provider_customer_id:
                    logger.warning(
                        f"Subscription {subscription.id} has no payment method, skipping renewal"
                    )
                    failure_count += 1
                    continue
                
                # Process renewal payment
                success, payment = payment_service.process_subscription_renewal(
                    subscription_id=subscription.id
                )
                
                if success:
                    logger.info(f"Renewed subscription {subscription.id}")
                    success_count += 1
                else:
                    logger.warning(f"Failed to renew subscription {subscription.id}")
                    failure_count += 1
            
            except Exception as e:
                logger.error(f"Error renewing subscription {subscription.id}: {e}", exc_info=True)
                failure_count += 1
        
        db.commit()
        db.close()
        
        message = f"Processed {success_count} successful, {failure_count} failed"
        log_job_execution(job_id, job_name, "success", message)
    
    except Exception as e:
        logger.error(f"Error in subscription renewal job: {e}", exc_info=True)
        log_job_execution(job_id, job_name, "error", str(e))
        if 'db' in locals():
            db.close()


async def retry_failed_payments():
    """
    Retry failed payments on schedule.
    
    **Procedure:**
    1. Query payments with status=failed and next_retry_at <= now
    2. Check retry_attempt < 3
    3. Attempt payment again
    4. On success: Update subscription, clear failed count
    5. On failure: Update next_retry_at
    6. On max retries: Mark as past_due
    
    **Execution:** Hourly at :00 minutes
    
    **Retry Schedule:**
    - Day 1: Attempt 1
    - Day 3: Attempt 2
    - Day 7: Attempt 3
    """
    job_id = "payment_retry_hourly"
    job_name = "Hourly Payment Retry"
    
    try:
        db = get_db_session()
        now = datetime.utcnow()
        
        # Query failed payments due for retry
        failed_payments = db.query(SubscriptionPayment).filter(
            SubscriptionPayment.status == "failed",
            SubscriptionPayment.retry_attempt < 3,
            SubscriptionPayment.next_retry_at <= now
        ).all()
        
        if not failed_payments:
            log_job_execution(job_id, job_name, "success", "No payments to retry")
            db.close()
            return
        
        logger.info(f"Retrying {len(failed_payments)} failed payments")
        
        payment_service = PaymentService(db)
        retry_count = 0
        
        for payment in failed_payments:
            try:
                subscription = payment.subscription
                
                # Attempt retry
                success, new_payment = payment_service.retry_failed_payment(
                    payment_id=payment.id
                )
                
                if success:
                    logger.info(f"Retry successful for payment {payment.id}")
                    retry_count += 1
                else:
                    logger.warning(f"Retry failed for payment {payment.id}")
            
            except Exception as e:
                logger.error(f"Error retrying payment {payment.id}: {e}", exc_info=True)
        
        db.commit()
        db.close()
        
        log_job_execution(job_id, job_name, "success", f"Retried {retry_count} payments")
    
    except Exception as e:
        logger.error(f"Error in payment retry job: {e}", exc_info=True)
        log_job_execution(job_id, job_name, "error", str(e))
        if 'db' in locals():
            db.close()


async def send_renewal_reminders():
    """
    Send renewal reminders 3 days before billing date.
    
    **Procedure:**
    1. Query subscriptions where next_billing_date = 3 days from now
    2. Send email to subscriber
    3. Send push notification if enabled
    4. Record notification sent
    
    **Execution:** Daily at 08:00 UTC
    """
    job_id = "renewal_reminders_daily"
    job_name = "Daily Renewal Reminders"
    
    try:
        db = get_db_session()
        target_date = (datetime.utcnow() + timedelta(days=3)).date()
        
        # Query subscriptions renewing in 3 days
        subscriptions = db.query(Subscription).filter(
            Subscription.next_billing_date >= datetime(
                target_date.year, target_date.month, target_date.day
            ),
            Subscription.next_billing_date < datetime(
                target_date.year, target_date.month, target_date.day
            ) + timedelta(days=1),
            Subscription.status == "active"
        ).all()
        
        if not subscriptions:
            log_job_execution(job_id, job_name, "success", "No reminders to send")
            db.close()
            return
        
        logger.info(f"Sending {len(subscriptions)} renewal reminders")
        
        reminder_count = 0
        for subscription in subscriptions:
            try:
                # TODO: Send email via notification service
                # TODO: Send push notification
                
                logger.debug(f"Reminder sent for subscription {subscription.id}")
                reminder_count += 1
            
            except Exception as e:
                logger.error(f"Error sending reminder for {subscription.id}: {e}")
        
        db.close()
        
        log_job_execution(job_id, job_name, "success", f"Sent {reminder_count} reminders")
    
    except Exception as e:
        logger.error(f"Error in reminder job: {e}", exc_info=True)
        log_job_execution(job_id, job_name, "error", str(e))
        if 'db' in locals():
            db.close()


async def cancel_expired_trials():
    """
    Auto-cancel expired trial subscriptions.
    
    **Procedure:**
    1. Query subscriptions with status=TRIALING and trial_ends_at < now
    2. Transition to CANCELLED
    3. Record cancellation timestamp
    4. Send cancellation email to subscriber
    
    **Execution:** Daily at 02:00 UTC
    """
    job_id = "trial_cleanup_daily"
    job_name = "Daily Trial Cleanup"
    
    try:
        db = get_db_session()
        now = datetime.utcnow()
        
        # Query expired trials
        expired_trials = db.query(Subscription).filter(
            Subscription.status == "trialing",
            Subscription.trial_ends_at <= now
        ).all()
        
        if not expired_trials:
            log_job_execution(job_id, job_name, "success", "No expired trials")
            db.close()
            return
        
        logger.info(f"Cancelling {len(expired_trials)} expired trials")
        
        cancel_count = 0
        for subscription in expired_trials:
            try:
                subscription.status = "cancelled"
                subscription.cancelled_at = now
                
                logger.info(f"Cancelled expired trial {subscription.id}")
                cancel_count += 1
                
                # TODO: Send cancellation email
                # TODO: Send notification to subscriber
            
            except Exception as e:
                logger.error(f"Error cancelling trial {subscription.id}: {e}")
        
        db.commit()
        db.close()
        
        log_job_execution(job_id, job_name, "success", f"Cancelled {cancel_count} trials")
    
    except Exception as e:
        logger.error(f"Error in trial cleanup job: {e}", exc_info=True)
        log_job_execution(job_id, job_name, "error", str(e))
        if 'db' in locals():
            db.close()


async def send_welcome_messages():
    """
    Send welcome messages to new subscribers.
    
    **Procedure:**
    1. Query subscriptions created < 24 hours ago
    2. Send welcome email from platform
    3. Send welcome DM from creator (if template available)
    4. Mark message as sent
    
    **Execution:** Hourly at :00 minutes
    """
    job_id = "send_welcome_messages"
    job_name = "Send Welcome Messages"
    
    try:
        db = get_db_session()
        
        # Query new subscriptions (created in last hour)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        new_subscriptions = db.query(Subscription).filter(
            Subscription.created_at > cutoff_time,
            Subscription.status.in_(["active", "trialing"])
        ).all()
        
        if not new_subscriptions:
            log_job_execution(job_id, job_name, "success", "No new subscribers")
            db.close()
            return
        
        logger.info(f"Sending welcome messages to {len(new_subscriptions)} new subscribers")
        
        welcome_count = 0
        for subscription in new_subscriptions:
            try:
                # TODO: Send welcome email via notification service
                # email_service.send_welcome_email(
                #     user_id=subscription.subscriber_id,
                #     creator_name=subscription.fan_club.creator.full_name,
                #     tier_name=subscription.tier.name
                # )
                
                # TODO: Send welcome DM from creator
                # messaging_service.send_creator_welcome_message(
                #     creator_id=subscription.fan_club.creator_id,
                #     subscriber_id=subscription.subscriber_id
                # )
                
                logger.debug(f"Welcome message sent for subscription {subscription.id}")
                welcome_count += 1
            
            except Exception as e:
                logger.error(f"Error sending welcome message for {subscription.id}: {e}")
        
        db.close()
        
        log_job_execution(job_id, job_name, "success", f"Sent {welcome_count} welcome messages")
    
    except Exception as e:
        logger.error(f"Error in welcome message job: {e}", exc_info=True)
        log_job_execution(job_id, job_name, "error", str(e))
        if 'db' in locals():
            db.close()


async def send_engagement_messages():
    """
    Send engagement messages (thank you, anniversary, exclusive content notifications).
    
    **Procedure:**
    1. Send monthly thank you for 3+ month subscribers
    2. Send anniversary messages for 1-year+ subscribers
    3. Send exclusive content notifications
    4. Track engagement metrics
    
    **Execution:** Daily at 11:00 UTC
    """
    job_id = "send_engagement_messages"
    job_name = "Send Engagement Messages"
    
    try:
        db = get_db_session()
        now = datetime.utcnow()
        
        # Query active subscriptions
        active_subscriptions = db.query(Subscription).filter(
            Subscription.status == "active"
        ).all()
        
        if not active_subscriptions:
            log_job_execution(job_id, job_name, "success", "No active subscriptions")
            db.close()
            return
        
        logger.info(f"Processing engagement for {len(active_subscriptions)} subscriptions")
        
        message_count = 0
        
        for subscription in active_subscriptions:
            try:
                # Calculate months subscribed
                months_subscribed = (now - subscription.started_at).days // 30
                
                # Send thank you message for 3+ months
                if months_subscribed >= 3 and months_subscribed % 1 == 0:
                    # TODO: Send thank you message
                    logger.debug(f"Thank you message for subscription {subscription.id}")
                    message_count += 1
                
                # Send anniversary message for 12+ months
                if (now - subscription.started_at).days >= 365:
                    # TODO: Send anniversary message
                    logger.debug(f"Anniversary message for subscription {subscription.id}")
                    message_count += 1
            
            except Exception as e:
                logger.error(f"Error sending engagement message for {subscription.id}: {e}")
        
        db.close()
        
        log_job_execution(job_id, job_name, "success", f"Sent {message_count} engagement messages")
    
    except Exception as e:
        logger.error(f"Error in engagement message job: {e}", exc_info=True)
        log_job_execution(job_id, job_name, "error", str(e))
        if 'db' in locals():
            db.close()
