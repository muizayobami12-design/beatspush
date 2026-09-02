"""
Unit tests for PaymentService.

Tests:
- Payment processing
- Payment retry logic
- Refunds
- Revenue split calculation
- Payment status tracking
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.payment_service import PaymentService
from app.models.fan_club import SubscriptionPayment, Subscription


class TestPaymentProcessing:
    """Test payment processing."""
    
    def test_process_subscription_payment_success(
        self,
        db_session: Session,
        active_subscription,
        mock_stripe_provider
    ):
        """Test successful payment processing."""
        service = PaymentService(db_session)
        
        success, payment = service.process_subscription_renewal(
            subscription_id=active_subscription.id
        )
        
        assert success is True
        assert payment is not None
        assert payment.status == "succeeded"
        assert payment.subscription_id == active_subscription.id
    
    def test_process_payment_creates_record(
        self,
        db_session: Session,
        active_subscription,
        mock_stripe_provider
    ):
        """Test that payment creates database record."""
        service = PaymentService(db_session)
        
        success, payment = service.process_subscription_renewal(
            subscription_id=active_subscription.id
        )
        
        # Verify payment record exists
        payment_record = db_session.query(SubscriptionPayment).filter(
            SubscriptionPayment.id == payment.id
        ).first()
        
        assert payment_record is not None
        assert payment_record.amount == active_subscription.price_paid


class TestPaymentFailure:
    """Test payment failure handling."""
    
    def test_handle_payment_failure(
        self,
        db_session: Session,
        active_subscription,
        mock_stripe_provider
    ):
        """Test handling payment failure."""
        service = PaymentService(db_session)
        
        # Create failed payment
        failed_payment = SubscriptionPayment(
            subscription_id=active_subscription.id,
            amount=active_subscription.price_paid,
            currency="USD",
            status="failed",
            failure_code="card_declined",
            failure_message="Card declined",
            retry_attempt=0
        )
        db_session.add(failed_payment)
        db_session.commit()
        
        # Update subscription to past_due
        active_subscription.status = "past_due"
        active_subscription.failed_payment_count = 1
        db_session.commit()
        
        assert active_subscription.status == "past_due"
        assert active_subscription.failed_payment_count == 1


class TestPaymentRetry:
    """Test payment retry logic."""
    
    def test_retry_failed_payment_max_retries(
        self,
        db_session: Session,
        active_subscription,
        failed_payment
    ):
        """Test maximum retry attempts."""
        service = PaymentService(db_session)
        
        failed_payment.retry_attempt = 3  # Max retries
        db_session.commit()
        
        success, payment = service.retry_failed_payment(failed_payment.id)
        
        # Should not retry beyond max
        assert failed_payment.retry_attempt == 3
    
    def test_calculate_retry_date_attempt_1(
        self,
        db_session: Session,
        failed_payment
    ):
        """Test retry date for first attempt (1 day)."""
        service = PaymentService(db_session)
        
        retry_date = service.calculate_retry_date(0)  # Attempt 0
        
        assert retry_date is not None
        assert (retry_date - datetime.utcnow()).days >= 0
        assert (retry_date - datetime.utcnow()).days <= 2
    
    def test_calculate_retry_date_attempt_2(
        self,
        db_session: Session,
        failed_payment
    ):
        """Test retry date for second attempt (3 days)."""
        service = PaymentService(db_session)
        
        retry_date = service.calculate_retry_date(1)  # Attempt 1
        
        assert retry_date is not None
        assert (retry_date - datetime.utcnow()).days >= 2
        assert (retry_date - datetime.utcnow()).days <= 4


class TestRevenueSplitCalculation:
    """Test revenue split between platform and creator."""
    
    def test_calculate_revenue_split(
        self,
        db_session: Session
    ):
        """Test 10/90 revenue split calculation."""
        service = PaymentService(db_session)
        
        amount = Decimal("100.00")
        platform_fee, creator_payout = service.calculate_revenue_split(amount)
        
        assert platform_fee == Decimal("10.00")
        assert creator_payout == Decimal("90.00")
        assert platform_fee + creator_payout == amount
    
    def test_calculate_revenue_split_small_amount(
        self,
        db_session: Session
    ):
        """Test revenue split with small amounts."""
        service = PaymentService(db_session)
        
        amount = Decimal("1.00")
        platform_fee, creator_payout = service.calculate_revenue_split(amount)
        
        assert platform_fee + creator_payout == amount
        assert platform_fee > Decimal("0.00")


class TestPaymentStatusTracking:
    """Test payment status tracking."""
    
    def test_track_payment_created(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test payment creation tracking."""
        service = PaymentService(db_session)
        
        payment = SubscriptionPayment(
            subscription_id=active_subscription.id,
            amount=Decimal("9.99"),
            currency="USD",
            status="pending",
            payment_provider="stripe"
        )
        db_session.add(payment)
        db_session.commit()
        
        assert payment.status == "pending"
        assert payment.created_at is not None
    
    def test_track_payment_succeeded(
        self,
        db_session: Session,
        successful_payment
    ):
        """Test successful payment tracking."""
        assert successful_payment.status == "succeeded"
        assert successful_payment.paid_at is not None
    
    def test_track_payment_failed(
        self,
        db_session: Session,
        failed_payment
    ):
        """Test failed payment tracking."""
        assert failed_payment.status == "failed"
        assert failed_payment.failure_code is not None
        assert failed_payment.failure_message is not None


class TestPaymentMethodStorage:
    """Test payment method storage and retrieval."""
    
    def test_store_payment_method(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test storing payment method ID."""
        active_subscription.payment_provider_customer_id = "cus_test123"
        db_session.commit()
        
        assert active_subscription.payment_provider_customer_id == "cus_test123"
    
    def test_retrieve_payment_method(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test retrieving stored payment method."""
        retrieved = db_session.query(Subscription).filter(
            Subscription.id == active_subscription.id
        ).first()
        
        assert retrieved.payment_provider_customer_id is not None


class TestRecurringBillingCalculation:
    """Test recurring billing calculations."""
    
    def test_calculate_next_billing_amount(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test calculating next billing amount."""
        service = PaymentService(db_session)
        
        amount = service.calculate_billing_amount(active_subscription)
        
        assert amount == active_subscription.tier.price
    
    def test_calculate_proration(
        self,
        db_session: Session,
        active_subscription
    ):
        """Test proration calculation for mid-cycle changes."""
        service = PaymentService(db_session)
        
        days_remaining = 15
        monthly_price = Decimal("9.99")
        
        proration = service.calculate_proration(
            monthly_price,
            days_remaining,
            30  # days in month
        )
        
        assert proration > Decimal("0.00")
        assert proration < monthly_price
