"""
Webhook endpoints for payment provider callbacks.

Handles webhooks from:
- Stripe: subscription events, payment events
- Paystack: subscription events, payment events
"""

from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
import stripe
import hmac
import hashlib
import logging
from typing import Optional

from app.core.config import settings
from app.db.database import get_db
from app.services.subscription_service import SubscriptionService
from app.services.payment_service import PaymentService
from app.models.fan_club import Subscription, SubscriptionPayment

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


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
    """
    payload = await request.body()
    
    # Verify webhook signature
    if settings.STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, 
                stripe_signature, 
                settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid Stripe webhook payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid Stripe webhook signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        # Test mode - parse without verification
        import json
        event = json.loads(payload)
    
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})
    
    logger.info(f"Received Stripe webhook: {event_type}")
    
    try:
        if event_type == "invoice.paid":
            await _handle_invoice_paid(data, db)
        
        elif event_type == "invoice.payment_failed":
            await _handle_invoice_payment_failed(data, db)
        
        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(data, db)
        
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(data, db)
        
        else:
            logger.info(f"Unhandled Stripe event type: {event_type}")
    
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}", exc_info=True)
        # Return 200 to prevent Stripe retries for unrecoverable errors
        # Log the error for manual investigation
    
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
    - charge.success: Payment successful
    - subscription.create: New subscription
    - subscription.disable: Subscription canceled
    """
    payload = await request.body()
    
    # Verify webhook signature
    if settings.PAYSTACK_SECRET_KEY:
        expected_signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        if x_paystack_signature != expected_signature:
            logger.error("Invalid Paystack webhook signature")
            raise HTTPException(status_code=400, detail="Invalid signature")
    
    import json
    event = json.loads(payload)
    
    event_type = event.get("event")
    data = event.get("data", {})
    
    logger.info(f"Received Paystack webhook: {event_type}")
    
    try:
        if event_type == "charge.success":
            await _handle_paystack_charge_success(data, db)
        
        elif event_type == "subscription.create":
            await _handle_paystack_subscription_create(data, db)
        
        elif event_type == "subscription.disable":
            await _handle_paystack_subscription_disable(data, db)
        
        else:
            logger.info(f"Unhandled Paystack event type: {event_type}")
    
    except Exception as e:
        logger.error(f"Error processing Paystack webhook: {e}", exc_info=True)
    
    return {"status": "success"}


# Stripe Event Handlers

async def _handle_invoice_paid(invoice_data: dict, db: Session):
    """Handle successful payment (invoice.paid event)."""
    subscription_id = invoice_data.get("subscription")
    amount_paid = invoice_data.get("amount_paid", 0) / 100  # Convert cents to dollars
    currency = invoice_data.get("currency", "usd").upper()
    
    # Find subscription by Stripe subscription ID
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"Subscription not found for Stripe ID: {subscription_id}")
        return
    
    # Create payment record
    payment = SubscriptionPayment(
        subscription_id=subscription.id,
        amount=amount_paid,
        currency=currency,
        payment_method="stripe",
        status="completed",
        transaction_id=invoice_data.get("id"),
        metadata={
            "invoice_id": invoice_data.get("id"),
            "charge_id": invoice_data.get("charge"),
            "period_start": invoice_data.get("period_start"),
            "period_end": invoice_data.get("period_end")
        }
    )
    db.add(payment)
    
    # Update subscription status
    subscription.status = "active"
    subscription.failed_payment_count = 0  # Reset failed payment counter
    
    # Update next billing date
    if invoice_data.get("period_end"):
        from datetime import datetime
        subscription.next_billing_date = datetime.fromtimestamp(
            invoice_data.get("period_end")
        )
    
    db.commit()
    
    logger.info(f"Payment recorded for subscription {subscription.id}: ${amount_paid}")
    
    # TODO: Send payment confirmation email
    # TODO: Send thank you notification


async def _handle_invoice_payment_failed(invoice_data: dict, db: Session):
    """Handle failed payment (invoice.payment_failed event)."""
    subscription_id = invoice_data.get("subscription")
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"Subscription not found for Stripe ID: {subscription_id}")
        return
    
    # Increment failed payment counter
    subscription.failed_payment_count += 1
    
    # Create failed payment record
    amount = invoice_data.get("amount_due", 0) / 100
    payment = SubscriptionPayment(
        subscription_id=subscription.id,
        amount=amount,
        currency=invoice_data.get("currency", "usd").upper(),
        payment_method="stripe",
        status="failed",
        transaction_id=invoice_data.get("id"),
        metadata={
            "invoice_id": invoice_data.get("id"),
            "attempt_count": invoice_data.get("attempt_count"),
            "next_payment_attempt": invoice_data.get("next_payment_attempt")
        }
    )
    db.add(payment)
    
    # Update subscription status based on retry count
    if subscription.failed_payment_count >= 3:
        subscription.status = "past_due"
        logger.warning(f"Subscription {subscription.id} marked past_due after 3 failed attempts")
        # TODO: Send final warning email
    else:
        logger.info(f"Payment failed for subscription {subscription.id} (attempt {subscription.failed_payment_count}/3)")
        # TODO: Send payment failed notification with retry info
    
    db.commit()


async def _handle_subscription_updated(subscription_data: dict, db: Session):
    """Handle subscription updates (customer.subscription.updated event)."""
    stripe_subscription_id = subscription_data.get("id")
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"Subscription not found for Stripe ID: {stripe_subscription_id}")
        return
    
    # Sync status
    stripe_status = subscription_data.get("status")
    status_mapping = {
        "active": "active",
        "past_due": "past_due",
        "canceled": "cancelled",
        "unpaid": "past_due",
        "trialing": "active"
    }
    subscription.status = status_mapping.get(stripe_status, subscription.status)
    
    # Update billing info
    if subscription_data.get("current_period_end"):
        from datetime import datetime
        subscription.next_billing_date = datetime.fromtimestamp(
            subscription_data.get("current_period_end")
        )
    
    db.commit()
    logger.info(f"Subscription {subscription.id} status updated to {subscription.status}")


async def _handle_subscription_deleted(subscription_data: dict, db: Session):
    """Handle subscription cancellation (customer.subscription.deleted event)."""
    stripe_subscription_id = subscription_data.get("id")
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"Subscription not found for Stripe ID: {stripe_subscription_id}")
        return
    
    subscription.status = "cancelled"
    
    from datetime import datetime
    subscription.cancelled_at = datetime.utcnow()
    
    db.commit()
    logger.info(f"Subscription {subscription.id} canceled")
    
    # TODO: Send cancellation confirmation email


# Paystack Event Handlers

async def _handle_paystack_charge_success(charge_data: dict, db: Session):
    """Handle successful Paystack payment."""
    reference = charge_data.get("reference")
    amount = charge_data.get("amount", 0) / 100  # Convert kobo to naira/dollar
    currency = charge_data.get("currency", "NGN")
    
    # Find subscription by payment reference (stored in metadata)
    # Note: This assumes reference contains subscription_id
    subscription_id = charge_data.get("metadata", {}).get("subscription_id")
    
    if not subscription_id:
        logger.warning(f"No subscription_id in Paystack charge metadata: {reference}")
        return
    
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    if not subscription:
        logger.warning(f"Subscription not found: {subscription_id}")
        return
    
    # Create payment record
    payment = SubscriptionPayment(
        subscription_id=subscription.id,
        amount=amount,
        currency=currency,
        payment_method="paystack",
        status="completed",
        transaction_id=reference,
        metadata=charge_data
    )
    db.add(payment)
    
    # Update subscription
    subscription.status = "active"
    subscription.failed_payment_count = 0
    
    db.commit()
    logger.info(f"Paystack payment recorded for subscription {subscription.id}: {amount} {currency}")


async def _handle_paystack_subscription_create(subscription_data: dict, db: Session):
    """Handle new Paystack subscription."""
    # Similar to charge.success but for subscription creation
    logger.info(f"Paystack subscription created: {subscription_data.get('subscription_code')}")


async def _handle_paystack_subscription_disable(subscription_data: dict, db: Session):
    """Handle Paystack subscription cancellation."""
    subscription_code = subscription_data.get("subscription_code")
    
    subscription = db.query(Subscription).filter(
        Subscription.paystack_subscription_code == subscription_code
    ).first()
    
    if not subscription:
        logger.warning(f"Subscription not found for Paystack code: {subscription_code}")
        return
    
    subscription.status = "cancelled"
    
    from datetime import datetime
    subscription.cancelled_at = datetime.utcnow()
    
    db.commit()
    logger.info(f"Paystack subscription {subscription.id} disabled")
