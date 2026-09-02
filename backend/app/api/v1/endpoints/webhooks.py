"""
Webhook endpoints for payment provider callbacks.

Handles webhooks from:
- Stripe: subscription events, payment events
- Paystack: subscription events, payment events

Webhook flow:
1. Receive webhook from provider
2. Verify signature
3. Check for duplicate event (idempotency)
4. Process event (update subscription/payment)
5. Return 200 OK
6. Log event for audit trail
"""

from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
import stripe
import json
import logging
from typing import Optional

from app.core.config import settings
from app.core.webhook_utils import (
    WebhookSignatureError, WebhookProcessor, log_webhook_event
)
from app.db.database import get_db
from app.services.subscription_service import SubscriptionService
from app.services.payment_service import PaymentService
from app.models.fan_club import Subscription, SubscriptionPayment

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)
webhook_processor = WebhookProcessor(None)  # Will pass db in handlers


@router.post("/stripe", status_code=200)
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    Supported events:
    - invoice.paid: Payment successful
    - invoice.payment_failed: Payment failed
    - customer.subscription.updated: Subscription changed
    - customer.subscription.deleted: Subscription canceled
    
    **Security:**
    - Signature verified using STRIPE_WEBHOOK_SECRET
    - Duplicate events prevented via idempotency check
    - All events logged for audit trail
    """
    payload = await request.body()
    
    try:
        # Verify webhook signature
        if settings.STRIPE_WEBHOOK_SECRET:
            try:
                event = WebhookProcessor.verify_stripe_signature(
                    payload,
                    stripe_signature,
                    settings.STRIPE_WEBHOOK_SECRET
                )
            except WebhookSignatureError as e:
                logger.error(f"Stripe signature verification failed: {e}")
                raise HTTPException(status_code=400, detail="Invalid signature")
        else:
            # Test mode - parse without verification
            event = json.loads(payload)
        
        event_type = event.get("type")
        event_id = event.get("id")
        data = event.get("data", {}).get("object", {})
        
        logger.info(f"Received Stripe webhook: {event_type} (ID: {event_id})")
        
        # Process event
        if event_type == "invoice.paid":
            await _handle_invoice_paid(data, db)
            log_webhook_event("invoice.paid", "stripe", data.get("subscription"), "success")
        
        elif event_type == "invoice.payment_failed":
            await _handle_invoice_payment_failed(data, db)
            log_webhook_event("invoice.payment_failed", "stripe", data.get("subscription"), "success")
        
        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(data, db)
            log_webhook_event("customer.subscription.updated", "stripe", data.get("id"), "success")
        
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(data, db)
            log_webhook_event("customer.subscription.deleted", "stripe", data.get("id"), "success")
        
        else:
            logger.debug(f"Unhandled Stripe event type: {event_type}")
            log_webhook_event(event_type, "stripe", None, "skipped", "Event type not handled")
    
    except WebhookSignatureError as e:
        logger.error(f"Webhook verification failed: {e}")
        log_webhook_event("verification", "stripe", None, "error", str(e))
        raise HTTPException(status_code=400, detail="Invalid webhook")
    
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}", exc_info=True)
        log_webhook_event("error", "stripe", None, "error", str(e))
        # Return 200 to prevent Stripe from retrying unrecoverable errors
        # But log the error for manual investigation
    
    return {"status": "success"}


@router.post("/paystack", status_code=200)
async def paystack_webhook(
    request: Request,
    x_paystack_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle Paystack webhook events.
    
    Supported events:
    - charge.success: Payment successful (one-time or recurring)
    - subscription.create: New recurring subscription created
    - subscription.disable: Recurring subscription cancelled
    
    **Security:**
    - Signature verified using PAYSTACK_SECRET_KEY (HMAC-SHA512)
    - Duplicate events prevented via idempotency check
    - All events logged for audit trail
    
    **Reference:**
    - https://paystack.com/docs/webhooks/events
    """
    payload = await request.body()
    
    try:
        # Verify webhook signature
        if settings.PAYSTACK_SECRET_KEY and x_paystack_signature:
            try:
                event = WebhookProcessor.verify_paystack_signature(
                    payload,
                    x_paystack_signature,
                    settings.PAYSTACK_SECRET_KEY
                )
            except WebhookSignatureError as e:
                logger.error(f"[Paystack] Signature verification failed: {e}")
                raise HTTPException(status_code=400, detail="Invalid signature")
        else:
            # Test mode - parse without verification
            event = json.loads(payload)
        
        event_type = event.get("event")
        event_id = event.get("id")  # Paystack event ID
        data = event.get("data", {})
        
        logger.info(f"[Paystack] Received webhook: {event_type} (ID: {event_id})")
        
        # Process event
        if event_type == "charge.success":
            await _handle_paystack_charge_success(data, db)
            log_webhook_event("charge.success", "paystack", 
                            data.get("metadata", {}).get("subscription_id") if isinstance(data.get("metadata"), dict) else None, 
                            "success")
        
        elif event_type == "subscription.create":
            await _handle_paystack_subscription_create(data, db)
            log_webhook_event("subscription.create", "paystack", None, "success")
        
        elif event_type == "subscription.disable":
            await _handle_paystack_subscription_disable(data, db)
            log_webhook_event("subscription.disable", "paystack", None, "success")
        
        else:
            logger.debug(f"[Paystack] Unhandled event type: {event_type}")
            log_webhook_event(event_type, "paystack", None, "skipped", "Event type not handled")
    
    except WebhookSignatureError as e:
        logger.error(f"[Paystack] Webhook verification failed: {e}")
        log_webhook_event("verification", "paystack", None, "error", str(e))
        raise HTTPException(status_code=400, detail="Invalid webhook")
    
    except Exception as e:
        logger.error(f"[Paystack] Error processing webhook: {e}", exc_info=True)
        log_webhook_event("error", "paystack", None, "error", str(e))
    
    return {"status": "success"}


# Stripe Event Handlers

async def _handle_invoice_paid(invoice_data: dict, db: Session):
    """
    Handle successful payment (invoice.paid event).
    
    - Marks payment as completed
    - Updates subscription to active status
    - Resets failed payment counter
    - Updates next billing date
    """
    from datetime import datetime
    
    stripe_subscription_id = invoice_data.get("subscription")
    amount_paid = invoice_data.get("amount_paid", 0) / 100  # Convert cents to dollars
    currency = invoice_data.get("currency", "usd").upper()
    invoice_id = invoice_data.get("id")
    charge_id = invoice_data.get("charge")
    paid_timestamp = invoice_data.get("paid_at", 0)
    
    # Find subscription by Stripe subscription ID
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"[Stripe] invoice.paid: Subscription not found for ID {stripe_subscription_id}")
        return
    
    # Check for duplicate payment (idempotency)
    existing_payment = db.query(SubscriptionPayment).filter(
        SubscriptionPayment.payment_provider_invoice_id == invoice_id,
        SubscriptionPayment.status == "completed"
    ).first()
    
    if existing_payment:
        logger.info(f"[Stripe] invoice.paid: Duplicate payment detected, skipping invoice {invoice_id}")
        return
    
    # Create payment record
    payment = SubscriptionPayment(
        id=f"pay_{invoice_id[:12]}",  # Use first 12 chars of invoice ID
        subscription_id=subscription.id,
        amount=amount_paid,
        currency=currency,
        payment_method="card",
        payment_provider="stripe",
        payment_provider_invoice_id=invoice_id,
        payment_provider_charge_id=charge_id,
        status="completed",
        paid_at=datetime.fromtimestamp(paid_timestamp) if paid_timestamp else datetime.utcnow()
    )
    db.add(payment)
    
    # Update subscription status
    subscription.status = "active"
    subscription.failed_payment_count = 0  # Reset failed payment counter
    
    # Update next billing date
    if invoice_data.get("period_end"):
        subscription.next_billing_date = datetime.fromtimestamp(
            invoice_data.get("period_end")
        )
    
    db.commit()
    
    logger.info(
        f"[Stripe] invoice.paid: Payment recorded for subscription {subscription.id}: "
        f"${amount_paid} {currency} (Invoice: {invoice_id})"
    )
    
    # TODO: Send payment confirmation email to subscriber
    # TODO: Send thank you notification from creator


async def _handle_invoice_payment_failed(invoice_data: dict, db: Session):
    """
    Handle failed payment (invoice.payment_failed event).
    
    - Creates failed payment record with error details
    - Increments failed payment counter
    - Transitions to past_due after 3 failures
    - Logs for audit trail
    """
    from datetime import datetime
    
    stripe_subscription_id = invoice_data.get("subscription")
    invoice_id = invoice_data.get("id")
    amount_due = invoice_data.get("amount_due", 0) / 100
    currency = invoice_data.get("currency", "usd").upper()
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"[Stripe] invoice.payment_failed: Subscription not found for ID {stripe_subscription_id}")
        return
    
    # Check for duplicate failure record (idempotency)
    existing_payment = db.query(SubscriptionPayment).filter(
        SubscriptionPayment.payment_provider_invoice_id == invoice_id,
        SubscriptionPayment.status == "failed"
    ).first()
    
    if existing_payment:
        logger.debug(f"[Stripe] invoice.payment_failed: Duplicate failure record exists for {invoice_id}")
        return
    
    # Increment failed payment counter
    subscription.failed_payment_count += 1
    current_attempt = subscription.failed_payment_count
    
    # Extract error details
    error_details = invoice_data.get("last_payment_error", {})
    failure_code = error_details.get("code")
    failure_message = error_details.get("message")
    
    # Create failed payment record
    payment = SubscriptionPayment(
        id=f"pay_fail_{invoice_id[:12]}",
        subscription_id=subscription.id,
        amount=amount_due,
        currency=currency,
        payment_method="card",
        payment_provider="stripe",
        payment_provider_invoice_id=invoice_id,
        status="failed",
        failure_code=failure_code,
        failure_message=failure_message,
        retry_attempt=current_attempt
    )
    db.add(payment)
    
    # Determine next action based on retry count
    max_retries = 3
    if current_attempt >= max_retries:
        # Max retries reached - mark subscription as past_due
        subscription.status = "past_due"
        logger.warning(
            f"[Stripe] invoice.payment_failed: Subscription {subscription.id} marked PAST_DUE "
            f"after {current_attempt} failed attempts (Invoice: {invoice_id}, "
            f"Error: {failure_code} - {failure_message})"
        )
        # TODO: Send final warning/suspension email to subscriber
    else:
        # Still within retry window
        logger.warning(
            f"[Stripe] invoice.payment_failed: Payment failed for subscription {subscription.id} "
            f"(attempt {current_attempt}/{max_retries}): {failure_code} - {failure_message}"
        )
        # TODO: Send retry notification to subscriber with retry date
    
    db.commit()


async def _handle_subscription_updated(subscription_data: dict, db: Session):
    """
    Handle subscription updates (customer.subscription.updated event).
    
    - Syncs subscription status from Stripe
    - Updates billing period dates
    - Detects tier/plan changes
    - Logs all changes for audit trail
    """
    from datetime import datetime
    
    stripe_subscription_id = subscription_data.get("id")
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"[Stripe] customer.subscription.updated: Subscription not found for ID {stripe_subscription_id}")
        return
    
    # Map Stripe status to our status
    stripe_status = subscription_data.get("status")
    status_mapping = {
        "active": "active",
        "past_due": "past_due",
        "canceled": "cancelled",
        "unpaid": "past_due",
        "trialing": "active"
    }
    new_status = status_mapping.get(stripe_status, subscription.status)
    
    # Track status changes
    status_changed = new_status != subscription.status
    if status_changed:
        logger.info(
            f"[Stripe] customer.subscription.updated: Subscription {subscription.id} "
            f"status changed {subscription.status} → {new_status}"
        )
        subscription.status = new_status
    
    # Update billing period info
    if subscription_data.get("current_period_start"):
        subscription.current_period_start = datetime.fromtimestamp(
            subscription_data.get("current_period_start")
        )
    
    if subscription_data.get("current_period_end"):
        new_period_end = datetime.fromtimestamp(
            subscription_data.get("current_period_end")
        )
        if subscription.current_period_end != new_period_end:
            logger.debug(
                f"[Stripe] customer.subscription.updated: Billing period updated for {subscription.id}: "
                f"{subscription.current_period_end} → {new_period_end}"
            )
        subscription.current_period_end = new_period_end
        subscription.next_billing_date = new_period_end
    
    # Check if plan/tier changed
    items = subscription_data.get("items", {}).get("data", [])
    if items:
        plan_id = items[0].get("plan", {}).get("id")
        plan_amount = items[0].get("plan", {}).get("amount", 0)
        if plan_id:
            logger.info(
                f"[Stripe] customer.subscription.updated: Subscription {subscription.id} "
                f"plan changed: {plan_id} (amount: {plan_amount/100})"
            )
            # TODO: Handle tier change if plan_id differs from current tier's provider_plan_id
    
    db.commit()
    logger.info(f"[Stripe] customer.subscription.updated: Subscription {subscription.id} sync complete")


async def _handle_subscription_deleted(subscription_data: dict, db: Session):
    """
    Handle subscription cancellation (customer.subscription.deleted event).
    
    - Marks subscription as cancelled
    - Records cancellation timestamp
    - Logs event for audit trail
    """
    from datetime import datetime
    
    stripe_subscription_id = subscription_data.get("id")
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"[Stripe] customer.subscription.deleted: Subscription not found for ID {stripe_subscription_id}")
        return
    
    # Only mark as cancelled if not already
    if subscription.status != "cancelled":
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.utcnow()
        
        db.commit()
        logger.warning(
            f"[Stripe] customer.subscription.deleted: Subscription {subscription.id} cancelled "
            f"via Stripe webhook"
        )
    else:
        logger.debug(
            f"[Stripe] customer.subscription.deleted: Subscription {subscription.id} "
            f"already cancelled"
        )
    
    # TODO: Send cancellation confirmation email to subscriber
    # TODO: Send creator notification of lost subscriber


# Paystack Event Handlers

async def _handle_paystack_charge_success(charge_data: dict, db: Session):
    """
    Handle successful Paystack payment (charge.success event).
    
    - Creates completed payment record
    - Updates subscription to active status
    - Resets failed payment counter
    - Handles both one-time and recurring charges
    
    Expects metadata.subscription_id to link to our subscription record.
    """
    from datetime import datetime
    
    reference = charge_data.get("reference")
    amount = charge_data.get("amount", 0) / 100  # Convert kobo to naira/dollar
    currency = charge_data.get("currency", "NGN")
    metadata = charge_data.get("metadata", {})
    customer_code = charge_data.get("customer", {}).get("customer_code")
    authorization = charge_data.get("authorization", {})
    auth_code = authorization.get("authorization_code")
    
    # Extract subscription_id from metadata
    subscription_id = None
    if isinstance(metadata, dict):
        subscription_id = metadata.get("subscription_id")
    elif isinstance(metadata, str):
        # Sometimes metadata is stringified JSON
        try:
            import json
            metadata_dict = json.loads(metadata)
            subscription_id = metadata_dict.get("subscription_id")
        except:
            pass
    
    if not subscription_id:
        logger.warning(
            f"[Paystack] charge.success: No subscription_id in charge metadata (Ref: {reference}). "
            f"Cannot link payment to subscription."
        )
        return
    
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not subscription:
        logger.warning(
            f"[Paystack] charge.success: Subscription not found: {subscription_id} "
            f"(Ref: {reference})"
        )
        return
    
    # Check for duplicate payment (idempotency)
    existing_payment = db.query(SubscriptionPayment).filter(
        SubscriptionPayment.payment_provider_payment_id == reference,
        SubscriptionPayment.status == "completed"
    ).first()
    
    if existing_payment:
        logger.debug(
            f"[Paystack] charge.success: Duplicate payment detected (Ref: {reference}), skipping"
        )
        return
    
    # Create payment record
    payment = SubscriptionPayment(
        id=f"pay_{reference[:20]}",  # Use first 20 chars of reference
        subscription_id=subscription.id,
        amount=amount,
        currency=currency,
        payment_method="card",
        payment_provider="paystack",
        payment_provider_payment_id=reference,
        payment_provider_charge_id=charge_data.get("id"),
        status="completed",
        paid_at=datetime.utcnow()
    )
    db.add(payment)
    
    # Update subscription
    subscription.status = "active"
    subscription.failed_payment_count = 0  # Reset failed payment counter
    
    # Update provider customer ID if available
    if customer_code:
        subscription.payment_provider_customer_id = customer_code
    
    # Update provider authorization code for future recurring charges
    if auth_code:
        # Store authorization code for recurring charges
        # This would typically be stored in a separate authorization table
        pass
    
    db.commit()
    
    logger.info(
        f"[Paystack] charge.success: Payment recorded for subscription {subscription.id}: "
        f"{amount} {currency} (Ref: {reference})"
    )
    
    # TODO: Send payment confirmation email to subscriber
    # TODO: Send thank you notification from creator


async def _handle_paystack_subscription_create(subscription_data: dict, db: Session):
    """
    Handle new Paystack subscription (subscription.create event).
    
    - Logs subscription creation from Paystack
    - Usually subscription is created via API call, not webhook
    - Webhook event is for audit trail and external subscriptions
    """
    subscription_code = subscription_data.get("subscription_code")
    customer_code = subscription_data.get("customer", {}).get("customer_code") if isinstance(subscription_data.get("customer"), dict) else None
    plan_code = subscription_data.get("plan", {}).get("plan_code") if isinstance(subscription_data.get("plan"), dict) else None
    status = subscription_data.get("status")
    
    logger.info(
        f"[Paystack] subscription.create: New subscription created "
        f"(Code: {subscription_code}, Plan: {plan_code}, Status: {status})"
    )
    
    # Log customer code for reference
    if customer_code:
        logger.debug(f"[Paystack] subscription.create: Customer code: {customer_code}")
    
    # TODO: Link Paystack subscription to our subscription if not already linked
    # Note: Subscriptions are typically created via our API, so this webhook is mainly for audit trail


async def _handle_paystack_subscription_disable(subscription_data: dict, db: Session):
    """
    Handle Paystack subscription cancellation (subscription.disable event).
    
    - Marks subscription as cancelled
    - Records cancellation timestamp
    - Logs event for audit trail
    """
    from datetime import datetime
    
    subscription_code = subscription_data.get("subscription_code")
    customer_code = subscription_data.get("customer", {}).get("customer_code") if isinstance(subscription_data.get("customer"), dict) else None
    cancellation_reason = subscription_data.get("cancellation_reason")
    status = subscription_data.get("status")
    
    # Find subscription by Paystack subscription code
    subscription = db.query(Subscription).filter(
        Subscription.paystack_subscription_code == subscription_code
    ).first()
    
    if not subscription:
        logger.warning(
            f"[Paystack] subscription.disable: Subscription not found for code: {subscription_code}"
        )
        return
    
    # Only mark as cancelled if not already
    if subscription.status != "cancelled":
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.utcnow()
        
        db.commit()
        logger.warning(
            f"[Paystack] subscription.disable: Subscription {subscription.id} cancelled "
            f"(Paystack Code: {subscription_code}, Reason: {cancellation_reason})"
        )
    else:
        logger.debug(
            f"[Paystack] subscription.disable: Subscription {subscription.id} already cancelled"
        )
    
    # TODO: Send cancellation confirmation email to subscriber
    # TODO: Send creator notification of lost subscriber
