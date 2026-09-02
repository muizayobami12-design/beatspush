"""
Webhook utilities for handling payment provider events.
Includes signature verification, idempotency handling, and retry logic.

**Idempotency Strategy:**
- Each webhook is uniquely identified by provider + event_id
- Duplicate events are detected by checking existing payment records
- Payment records are immutable once created (idempotent)
- Failed attempts are logged separately without duplicating state changes

**Error Handling:**
- Signature verification failures raise WebhookSignatureError
- Missing subscriptions are logged as warnings, not errors
- Processing errors are caught and logged but don't crash the handler
- All webhook endpoints return 200 OK to prevent provider retries
"""

import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import stripe
import json

logger = logging.getLogger(__name__)


class WebhookSignatureError(Exception):
    """Raised when webhook signature validation fails."""
    pass


class WebhookProcessor:
    """
    Base class for processing webhooks with idempotency and error handling.
    
    Key features:
    - Signature verification (Stripe + Paystack)
    - Idempotency checking to prevent duplicate processing
    - Retry calculation for failed payments
    - Status mapping between providers and our schema
    """
    
    def __init__(self, db=None):
        self.db = db
    
    def is_duplicate_event(
        self,
        provider: str,
        event_id: str,
        event_type: str,
        subscription_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if we've already processed this webhook event (idempotency).
        
        **Idempotency Strategy:**
        - For Stripe: Check payment_provider_invoice_id
        - For Paystack: Check payment_provider_payment_id
        - Only counts as duplicate if status is "completed" or "failed"
        
        Args:
            provider: Payment provider name (stripe, paystack)
            event_id: Unique event ID from provider
            event_type: Type of event (invoice.paid, charge.success, etc)
            subscription_id: Related subscription ID (optional, for filtering)
        
        Returns:
            Tuple of (is_duplicate, reason)
            - (True, "payment_already_processed") if payment already recorded
            - (True, "cancellation_already_recorded") if already cancelled
            - (False, None) if not a duplicate
        """
        if not self.db:
            return False, None
        
        from app.models.fan_club import SubscriptionPayment, Subscription
        
        try:
            if provider == "stripe":
                # For Stripe invoice events, check by invoice ID
                if event_type in ["invoice.paid", "invoice.payment_failed"]:
                    payment = self.db.query(SubscriptionPayment).filter(
                        SubscriptionPayment.payment_provider_invoice_id == event_id,
                        SubscriptionPayment.status.in_(["completed", "failed"])
                    ).first()
                    if payment:
                        return True, f"payment_already_{payment.status}"
                
                # For subscription events, check subscription status
                elif event_type in ["customer.subscription.deleted"]:
                    subscription = self.db.query(Subscription).filter(
                        Subscription.stripe_subscription_id == event_id,
                        Subscription.status == "cancelled"
                    ).first()
                    if subscription:
                        return True, "cancellation_already_recorded"
            
            elif provider == "paystack":
                # For Paystack charge events, check by reference
                if event_type == "charge.success":
                    payment = self.db.query(SubscriptionPayment).filter(
                        SubscriptionPayment.payment_provider_payment_id == event_id,
                        SubscriptionPayment.status == "completed"
                    ).first()
                    if payment:
                        return True, "payment_already_processed"
                
                # For subscription events, check subscription status
                elif event_type == "subscription.disable":
                    subscription = self.db.query(Subscription).filter(
                        Subscription.paystack_subscription_code == event_id,
                        Subscription.status == "cancelled"
                    ).first()
                    if subscription:
                        return True, "cancellation_already_recorded"
        
        except Exception as e:
            logger.error(f"Error checking for duplicate event: {e}")
            # If we can't check, proceed anyway (better to process duplicate than lose event)
        
        return False, None
    
    @staticmethod
    def verify_stripe_signature(
        payload: bytes,
        signature: str,
        webhook_secret: str
    ) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature and return parsed event.
        
        **Security:**
        - Uses stripe.Webhook.construct_event() for secure verification
        - Raises WebhookSignatureError if signature is invalid
        - Tolerates clock skew up to 5 minutes (Stripe default)
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header value
            webhook_secret: Stripe webhook signing secret
        
        Returns:
            Parsed event dictionary
        
        Raises:
            WebhookSignatureError: If signature is invalid or payload is malformed
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                webhook_secret
            )
            logger.debug(f"[Stripe] Signature verified for event {event.get('id')}")
            return event
        except ValueError as e:
            logger.error(f"[Stripe] Invalid webhook payload: {e}")
            raise WebhookSignatureError(f"Invalid Stripe webhook payload: {e}")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"[Stripe] Signature verification failed: {e}")
            raise WebhookSignatureError(f"Invalid Stripe webhook signature: {e}")
    
    @staticmethod
    def verify_paystack_signature(
        payload: bytes,
        signature: str,
        webhook_secret: str
    ) -> Dict[str, Any]:
        """
        Verify Paystack webhook signature and return parsed event.
        
        **Security:**
        - Uses HMAC-SHA512 for signature verification
        - Raises WebhookSignatureError if signature is invalid
        - Constant-time comparison to prevent timing attacks
        
        Args:
            payload: Raw request body
            signature: X-Paystack-Signature header value
            webhook_secret: Paystack secret key (used for HMAC)
        
        Returns:
            Parsed event dictionary
        
        Raises:
            WebhookSignatureError: If signature is invalid or payload is malformed
        """
        try:
            # Paystack uses HMAC-SHA512 for signature verification
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            if not hmac.compare_digest(signature or "", expected_signature):
                logger.error("[Paystack] Signature verification failed - mismatch")
                raise WebhookSignatureError("Invalid Paystack webhook signature")
            
            logger.debug("[Paystack] Signature verified")
            event = json.loads(payload)
            return event
        except json.JSONDecodeError as e:
            logger.error(f"[Paystack] Invalid webhook payload: {e}")
            raise WebhookSignatureError(f"Invalid Paystack webhook payload: {e}")
    
    @staticmethod
    def calculate_retry_date(
        attempt: int,
        retry_days: Optional[list] = None
    ) -> Optional[datetime]:
        """
        Calculate when next payment retry should occur.
        
        **Retry Schedule:**
        - Attempt 1 (Day 1): First automatic retry
        - Attempt 2 (Day 3): Second automatic retry  
        - Attempt 3 (Day 7): Final automatic retry
        - After attempt 3: Manual intervention required
        
        Args:
            attempt: Current retry attempt (1, 2, 3)
            retry_days: List of days for each retry [1, 3, 7]
        
        Returns:
            datetime for next retry, or None if max retries reached
        """
        if retry_days is None:
            retry_days = [1, 3, 7]  # Day 1, 3, 7
        
        if attempt >= len(retry_days):
            logger.info(f"Max retries ({len(retry_days)}) reached")
            return None  # Max retries reached
        
        delay_days = retry_days[attempt]
        next_retry = datetime.utcnow() + timedelta(days=delay_days)
        logger.debug(f"Next payment retry scheduled for day {delay_days}: {next_retry}")
        return next_retry
    
    @staticmethod
    def map_stripe_status(stripe_status: str) -> str:
        """
        Map Stripe subscription status to our internal status.
        
        Stripe Status → Our Status:
        - active → active
        - past_due → past_due
        - canceled → cancelled
        - unpaid → past_due
        - trialing → active
        
        Args:
            stripe_status: Status from Stripe API
        
        Returns:
            Mapped status for our schema
        """
        mapping = {
            "active": "active",
            "past_due": "past_due",
            "canceled": "cancelled",
            "unpaid": "past_due",
            "trialing": "active"
        }
        mapped = mapping.get(stripe_status, stripe_status)
        if mapped != stripe_status:
            logger.debug(f"[Stripe] Status mapped: {stripe_status} → {mapped}")
        return mapped
    
    @staticmethod
    def should_retry_payment(
        payment_provider: str,
        failure_code: Optional[str] = None,
        attempt: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if a payment failure should be retried.
        
        Some failures are permanent and shouldn't be retried (e.g., expired card).
        Some failures are temporary and should be retried (e.g., temporary gateway error).
        
        **Permanent Failures (don't retry):**
        - card_declined, card_error, authentication_error
        - do_not_honor, invalid_account, account_closed
        
        **Temporary Failures (retry):**
        - insufficient_funds (user might add funds)
        - rate_limit, timeout, gateway_error
        - network_error, service_error
        
        Args:
            payment_provider: stripe or paystack
            failure_code: Error code from payment provider
            attempt: Current retry attempt number
        
        Returns:
            Tuple of (should_retry, reason)
            - (True, None) if payment should be retried
            - (False, reason) if payment should not be retried
        """
        # Permanent failure codes that shouldn't be retried
        permanent_failures = {
            # Stripe codes
            "card_declined",
            "card_error",
            "authentication_error",
            "invalid_account",
            "account_closed",
            # Paystack codes
            "do_not_honor",
            "account_restriction",
            "card_expired",
            "restricted_card",
        }
        
        # Temporary failures that CAN be retried
        temporary_failures = {
            "insufficient_funds",
            "temporary_failure",
            "gateway_timeout",
            "rate_limit",
        }
        
        if failure_code in permanent_failures:
            reason = f"Permanent failure ({failure_code})"
            logger.info(f"Payment failure is permanent, won't retry: {reason}")
            return False, reason
        
        if failure_code in temporary_failures:
            return True, None
        
        # Unknown codes: retry unless max attempts reached
        if attempt >= 3:
            return False, "Max retry attempts reached"
        
        return True, None


def log_webhook_event(
    event_type: str,
    provider: str,
    subscription_id: Optional[str],
    status: str,
    details: Optional[str] = None
):
    """
    Log webhook event for audit trail and debugging.
    
    Args:
        event_type: Type of webhook event
        provider: Payment provider
        subscription_id: Related subscription ID
        status: success, failed, skipped, error
        details: Additional details
    """
    message = f"[{provider.upper()}] {event_type} - {status}"
    if subscription_id:
        message += f" (subscription: {subscription_id})"
    if details:
        message += f" - {details}"
    
    if status == "error":
        logger.error(message)
    elif status == "failed":
        logger.warning(message)
    else:
        logger.info(message)
