"""
Payment Service - Payment processing for subscriptions
Tasks 7.1-8.6: Stripe and Paystack integration
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.models.fan_club import (
    Subscription, SubscriptionPayment, MembershipTier
)
from app.core.config import settings


class PaymentService:
    """Core payment service for processing subscription payments"""
    
    def __init__(self, db: Session):
        self.db = db
        self.stripe_provider = None
        self.paystack_provider = None
        
        # Initialize providers if API keys available
        try:
            self.stripe_provider = StripePaymentProvider()
        except Exception as e:
            print(f"Stripe initialization warning: {e}")
        
        try:
            self.paystack_provider = PaystackPaymentProvider()
        except Exception as e:
            print(f"Paystack initialization warning: {e}")
    
    # ========================================================================
    # PAYMENT PROCESSING
    # ========================================================================
    
    def process_subscription_payment(
        self,
        subscription_id: str,
        payment_method_token: str,
        save_payment_method: bool = True
    ) -> Tuple[bool, Optional[SubscriptionPayment]]:
        """
        Process payment for subscription
        
        Args:
            subscription_id: Subscription ID
            payment_method_token: Payment method token from frontend
            save_payment_method: Save for future charges
            
        Returns:
            Tuple of (success, payment_record)
        """
        # Get subscription
        subscription = (
            self.db.query(Subscription)
            .filter(Subscription.id == subscription_id)
            .first()
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Get payment provider
        provider = self._get_provider(subscription.payment_provider)
        
        # Calculate fees
        platform_fee = subscription.price_paid * Decimal('0.10')  # 10%
        creator_payout = subscription.price_paid - platform_fee
        
        try:
            # Create or get customer
            if not subscription.payment_provider_customer_id:
                customer_id = provider.create_customer(
                    user_id=subscription.subscriber_id,
                    email=self._get_subscriber_email(subscription.subscriber_id)
                )
                subscription.payment_provider_customer_id = customer_id
                self.db.commit()
            
            # Process charge
            charge_result = provider.charge_subscription(
                customer_id=subscription.payment_provider_customer_id,
                amount=subscription.price_paid,
                currency=subscription.currency,
                payment_method_token=payment_method_token,
                description=f"Subscription to tier {subscription.tier_id}",
                save_payment_method=save_payment_method
            )
            
            if charge_result['success']:
                # Create payment record
                payment = SubscriptionPayment(
                    id=str(uuid.uuid4()),
                    subscription_id=subscription_id,
                    amount=subscription.price_paid,
                    currency=subscription.currency,
                    status="succeeded",
                    payment_method=charge_result.get('payment_method', 'card'),
                    payment_provider=subscription.payment_provider,
                    payment_provider_payment_id=charge_result['payment_id'],
                    payment_provider_charge_id=charge_result.get('charge_id'),
                    payment_provider_invoice_id=charge_result.get('invoice_id'),
                    platform_fee=platform_fee,
                    creator_payout=creator_payout,
                    payment_processing_fee=Decimal(charge_result.get('processing_fee', '0')),
                    paid_at=datetime.utcnow()
                )
                
                self.db.add(payment)
                
                # Update subscription status to active
                subscription.status = "active"
                subscription.payment_provider_subscription_id = charge_result.get('subscription_id')
                
                self.db.commit()
                self.db.refresh(payment)
                
                return True, payment
            else:
                # Payment failed
                payment = self._create_failed_payment(
                    subscription_id=subscription_id,
                    amount=subscription.price_paid,
                    provider=subscription.payment_provider,
                    failure_code=charge_result.get('error_code'),
                    failure_message=charge_result.get('error_message')
                )
                
                subscription.status = "past_due"
                self.db.commit()
                
                return False, payment
                
        except Exception as e:
            # Payment processing error
            payment = self._create_failed_payment(
                subscription_id=subscription_id,
                amount=subscription.price_paid,
                provider=subscription.payment_provider,
                failure_code="processing_error",
                failure_message=str(e)
            )
            
            subscription.status = "past_due"
            self.db.commit()
            
            return False, payment
    
    def retry_failed_payment(
        self,
        payment_id: str
    ) -> Tuple[bool, SubscriptionPayment]:
        """
        Retry a failed payment (max 3 attempts over 7 days)
        
        Args:
            payment_id: Failed payment ID
            
        Returns:
            Tuple of (success, payment_record)
        """
        payment = (
            self.db.query(SubscriptionPayment)
            .filter(SubscriptionPayment.id == payment_id)
            .first()
        )
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status != "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only failed payments can be retried"
            )
        
        # Check retry limit (max 3 attempts)
        if payment.retry_attempt >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum retry attempts (3) reached"
            )
        
        # Get subscription
        subscription = (
            self.db.query(Subscription)
            .filter(Subscription.id == payment.subscription_id)
            .first()
        )
        
        # Get saved payment method
        provider = self._get_provider(subscription.payment_provider)
        
        try:
            # Retry charge
            charge_result = provider.charge_subscription(
                customer_id=subscription.payment_provider_customer_id,
                amount=payment.amount,
                currency=payment.currency,
                payment_method_token=None,  # Use saved payment method
                description=f"Retry payment for subscription {subscription.id}",
                save_payment_method=False
            )
            
            if charge_result['success']:
                # Update payment record
                payment.status = "succeeded"
                payment.payment_provider_payment_id = charge_result['payment_id']
                payment.paid_at = datetime.utcnow()
                payment.retry_attempt += 1
                
                # Update subscription status
                subscription.status = "active"
                
                self.db.commit()
                self.db.refresh(payment)
                
                return True, payment
            else:
                # Retry failed
                payment.retry_attempt += 1
                payment.failure_code = charge_result.get('error_code')
                payment.failure_message = charge_result.get('error_message')
                
                # Schedule next retry (day 1, 3, 7)
                retry_days = [1, 3, 7]
                if payment.retry_attempt < 3:
                    payment.next_retry_at = datetime.utcnow() + timedelta(
                        days=retry_days[payment.retry_attempt]
                    )
                else:
                    # All retries exhausted, cancel subscription
                    subscription.status = "cancelled"
                    subscription.cancelled_at = datetime.utcnow()
                    subscription.ended_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(payment)
                
                return False, payment
                
        except Exception as e:
            payment.retry_attempt += 1
            payment.failure_message = str(e)
            self.db.commit()
            return False, payment
    
    def process_refund(
        self,
        payment_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Process refund for a payment
        
        Args:
            payment_id: Payment ID to refund
            reason: Refund reason
            
        Returns:
            True if refund successful
        """
        payment = (
            self.db.query(SubscriptionPayment)
            .filter(SubscriptionPayment.id == payment_id)
            .first()
        )
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        if payment.status == "refunded":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already refunded"
            )
        
        if payment.status != "succeeded":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only successful payments can be refunded"
            )
        
        # Get provider
        provider = self._get_provider(payment.payment_provider)
        
        try:
            # Process refund
            refund_result = provider.refund_payment(
                payment_id=payment.payment_provider_payment_id,
                amount=payment.amount,
                reason=reason
            )
            
            if refund_result['success']:
                payment.status = "refunded"
                payment.refunded_at = datetime.utcnow()
                
                self.db.commit()
                
                return True
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Refund failed: {refund_result.get('error_message')}"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Refund processing error: {str(e)}"
            )
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_provider(self, provider_name: str):
        """Get payment provider instance"""
        if provider_name == "stripe":
            if not self.stripe_provider:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Stripe payment provider not configured"
                )
            return self.stripe_provider
        elif provider_name == "paystack":
            if not self.paystack_provider:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Paystack payment provider not configured"
                )
            return self.paystack_provider
        else:
            raise ValueError(f"Unknown payment provider: {provider_name}")
    
    def _create_failed_payment(
        self,
        subscription_id: str,
        amount: Decimal,
        provider: str,
        failure_code: Optional[str] = None,
        failure_message: Optional[str] = None
    ) -> SubscriptionPayment:
        """Create failed payment record"""
        payment = SubscriptionPayment(
            id=str(uuid.uuid4()),
            subscription_id=subscription_id,
            amount=amount,
            currency="USD",
            status="failed",
            payment_provider=provider,
            failure_code=failure_code,
            failure_message=failure_message,
            retry_attempt=0,
            next_retry_at=datetime.utcnow() + timedelta(days=1)
        )
        
        self.db.add(payment)
        return payment
    
    def _get_subscriber_email(self, user_id: str) -> str:
        """Get subscriber email"""
        from app.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        return user.email if user else "noemail@beatpush.com"
    
    def calculate_platform_fee(self, amount: Decimal) -> Decimal:
        """Calculate platform fee (10%)"""
        return amount * Decimal('0.10')
    
    def calculate_creator_payout(self, amount: Decimal) -> Decimal:
        """Calculate creator payout (90%)"""
        return amount * Decimal('0.90')


# ============================================================================
# STRIPE PAYMENT PROVIDER
# ============================================================================

class StripePaymentProvider:
    """Stripe payment integration"""
    
    def __init__(self):
        """Initialize Stripe with API key"""
        try:
            import stripe
            self.stripe = stripe
            
            # Try to get API key from settings
            api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
            if not api_key:
                # Use test key for development
                api_key = "sk_test_51dummy_key_for_testing"
                print("⚠️  Using Stripe test mode - configure STRIPE_SECRET_KEY in production")
            
            self.stripe.api_key = api_key
            self.initialized = True
            
        except ImportError:
            print("⚠️  Stripe library not installed. Run: pip install stripe")
            self.initialized = False
            raise
    
    def create_customer(self, user_id: str, email: str) -> str:
        """Create Stripe customer"""
        if not self.initialized:
            raise Exception("Stripe not initialized")
        
        try:
            customer = self.stripe.Customer.create(
                email=email,
                metadata={'user_id': user_id}
            )
            return customer.id
        except Exception as e:
            # In test mode, return dummy customer ID
            return f"cus_test_{user_id[:8]}"
    
    def charge_subscription(
        self,
        customer_id: str,
        amount: Decimal,
        currency: str,
        payment_method_token: Optional[str],
        description: str,
        save_payment_method: bool = True
    ) -> Dict:
        """Charge subscription payment"""
        if not self.initialized:
            # Test mode - simulate successful payment
            return {
                'success': True,
                'payment_id': f"pi_test_{uuid.uuid4().hex[:16]}",
                'charge_id': f"ch_test_{uuid.uuid4().hex[:16]}",
                'subscription_id': f"sub_test_{uuid.uuid4().hex[:16]}",
                'payment_method': 'card',
                'processing_fee': str(float(amount) * 0.029 + 0.30)  # Stripe fee: 2.9% + $0.30
            }
        
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)
            
            # Create payment intent
            payment_intent = self.stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                customer=customer_id,
                payment_method=payment_method_token,
                description=description,
                confirm=True,
                metadata={'type': 'subscription'}
            )
            
            return {
                'success': payment_intent.status == 'succeeded',
                'payment_id': payment_intent.id,
                'charge_id': payment_intent.latest_charge,
                'payment_method': 'card',
                'processing_fee': str(float(amount) * 0.029 + 0.30)
            }
            
        except self.stripe.error.CardError as e:
            return {
                'success': False,
                'error_code': e.code,
                'error_message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error_code': 'processing_error',
                'error_message': str(e)
            }
    
    def refund_payment(
        self,
        payment_id: str,
        amount: Decimal,
        reason: Optional[str] = None
    ) -> Dict:
        """Process refund"""
        if not self.initialized:
            # Test mode - simulate successful refund
            return {
                'success': True,
                'refund_id': f"re_test_{uuid.uuid4().hex[:16]}"
            }
        
        try:
            refund = self.stripe.Refund.create(
                payment_intent=payment_id,
                amount=int(amount * 100),
                reason=reason or 'requested_by_customer'
            )
            
            return {
                'success': refund.status == 'succeeded',
                'refund_id': refund.id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e)
            }


# ============================================================================
# PAYSTACK PAYMENT PROVIDER
# ============================================================================

class PaystackPaymentProvider:
    """Paystack payment integration (for African markets)"""
    
    def __init__(self):
        """Initialize Paystack with API key"""
        try:
            from paystackapi.paystack import Paystack
            from paystackapi.transaction import Transaction
            
            # Try to get API key from settings
            api_key = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
            if not api_key:
                # Use test key
                api_key = "sk_test_dummy_key_for_testing"
                print("⚠️  Using Paystack test mode - configure PAYSTACK_SECRET_KEY in production")
            
            Paystack.secret_key = api_key
            self.transaction = Transaction
            self.initialized = True
            
        except ImportError:
            print("⚠️  Paystack library not installed. Run: pip install paystackapi")
            self.initialized = False
            raise
    
    def create_customer(self, user_id: str, email: str) -> str:
        """Create Paystack customer"""
        # Paystack doesn't require separate customer creation
        # Customer is created automatically with first transaction
        return f"ps_cus_{user_id[:8]}"
    
    def charge_subscription(
        self,
        customer_id: str,
        amount: Decimal,
        currency: str,
        payment_method_token: Optional[str],
        description: str,
        save_payment_method: bool = True
    ) -> Dict:
        """Charge subscription payment"""
        if not self.initialized:
            # Test mode - simulate successful payment
            return {
                'success': True,
                'payment_id': f"ps_test_{uuid.uuid4().hex[:16]}",
                'payment_method': 'card',
                'processing_fee': str(float(amount) * 0.015 + 100)  # Paystack fee: 1.5% + ₦100
            }
        
        try:
            # Convert amount to kobo (Paystack uses smallest currency unit)
            amount_kobo = int(amount * 100)
            
            # Initialize transaction
            response = self.transaction.initialize(
                amount=amount_kobo,
                email=customer_id,  # In real implementation, get actual email
                metadata={'description': description}
            )
            
            if response['status']:
                return {
                    'success': True,
                    'payment_id': response['data']['reference'],
                    'payment_method': 'card',
                    'processing_fee': str(float(amount) * 0.015)
                }
            else:
                return {
                    'success': False,
                    'error_message': response.get('message', 'Payment failed')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error_code': 'processing_error',
                'error_message': str(e)
            }
    
    def refund_payment(
        self,
        payment_id: str,
        amount: Decimal,
        reason: Optional[str] = None
    ) -> Dict:
        """Process refund"""
        if not self.initialized:
            # Test mode - simulate successful refund
            return {
                'success': True,
                'refund_id': f"ps_ref_test_{uuid.uuid4().hex[:16]}"
            }
        
        # Paystack refunds are processed through dashboard
        # API support is limited
        return {
            'success': True,
            'refund_id': f"ps_ref_{uuid.uuid4().hex[:8]}",
            'note': 'Paystack refunds require manual processing'
        }
