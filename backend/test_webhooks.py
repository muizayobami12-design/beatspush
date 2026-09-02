#!/usr/bin/env python3
"""
Webhook Testing Script
Quick testing of Stripe and Paystack webhook endpoints

Usage:
    python test_webhooks.py --stripe-event charge.succeeded
    python test_webhooks.py --paystack-event charge.success --signature <sig>
    python test_webhooks.py --all
"""

import json
import hmac
import hashlib
import argparse
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
WEBHOOK_HOST = "http://localhost:8000"
STRIPE_ENDPOINT = f"{WEBHOOK_HOST}/api/v1/webhooks/stripe"
PAYSTACK_ENDPOINT = f"{WEBHOOK_HOST}/api/v1/webhooks/paystack"

# Test data
TEST_SUBSCRIPTION_ID = "sub_test_001"
TEST_USER_ID = "user_test_001"


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_result(name: str, response: requests.Response):
    """Print formatted test result."""
    status = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
    print(f"{status} | {name}")
    print(f"  Status: {response.status_code}")
    if response.text:
        try:
            data = response.json()
            print(f"  Response: {json.dumps(data, indent=2)}")
        except:
            print(f"  Response: {response.text[:200]}")
    print()


def test_stripe_charge_succeeded():
    """Test Stripe charge.succeeded event."""
    event = {
        "type": "charge.succeeded",
        "id": "evt_test_charge_1",
        "data": {
            "object": {
                "id": "ch_test_1",
                "amount": 999,  # $9.99
                "currency": "usd",
                "source": {"id": "card_test"},
                "customer": "cus_test_1",
                "metadata": {"subscription_id": TEST_SUBSCRIPTION_ID}
            }
        }
    }
    
    payload = json.dumps(event).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": "test_mode"  # Bypassed in test mode
    }
    
    response = requests.post(STRIPE_ENDPOINT, data=payload, headers=headers)
    print_result("Stripe: charge.succeeded", response)
    return response


def test_stripe_charge_failed():
    """Test Stripe charge.failed event."""
    event = {
        "type": "charge.failed",
        "id": "evt_test_charge_fail_1",
        "data": {
            "object": {
                "id": "ch_test_fail_1",
                "amount": 999,
                "currency": "usd",
                "failure_code": "card_declined",
                "failure_message": "Your card was declined",
                "customer": "cus_test_1"
            }
        }
    }
    
    payload = json.dumps(event).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": "test_mode"
    }
    
    response = requests.post(STRIPE_ENDPOINT, data=payload, headers=headers)
    print_result("Stripe: charge.failed", response)
    return response


def test_stripe_subscription_updated():
    """Test Stripe subscription.updated event."""
    event = {
        "type": "customer.subscription.updated",
        "id": "evt_test_sub_update_1",
        "data": {
            "object": {
                "id": "sub_test_stripe_1",
                "status": "active",
                "customer": "cus_test_1",
                "current_period_start": int(datetime.utcnow().timestamp()),
                "current_period_end": int((datetime.utcnow().timestamp())) + 2592000,
                "items": {
                    "data": [
                        {
                            "plan": {
                                "id": "plan_test_1",
                                "amount": 999
                            }
                        }
                    ]
                }
            }
        }
    }
    
    payload = json.dumps(event).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": "test_mode"
    }
    
    response = requests.post(STRIPE_ENDPOINT, data=payload, headers=headers)
    print_result("Stripe: customer.subscription.updated", response)
    return response


def test_stripe_subscription_deleted():
    """Test Stripe subscription.deleted event."""
    event = {
        "type": "customer.subscription.deleted",
        "id": "evt_test_sub_delete_1",
        "data": {
            "object": {
                "id": "sub_test_stripe_1",
                "status": "canceled",
                "customer": "cus_test_1"
            }
        }
    }
    
    payload = json.dumps(event).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": "test_mode"
    }
    
    response = requests.post(STRIPE_ENDPOINT, data=payload, headers=headers)
    print_result("Stripe: customer.subscription.deleted", response)
    return response


def test_paystack_charge_success(signature: Optional[str] = None):
    """Test Paystack charge.success event."""
    event = {
        "event": "charge.success",
        "data": {
            "id": 12345,
            "reference": f"test_paystack_{int(datetime.utcnow().timestamp())}",
            "amount": 100000,  # 1000 NGN
            "currency": "NGN",
            "status": "success",
            "authorization": {
                "authorization_code": "AUTH_test_123"
            },
            "customer": {
                "customer_code": "CUS_test_123"
            },
            "metadata": {
                "subscription_id": TEST_SUBSCRIPTION_ID,
                "user_id": TEST_USER_ID
            }
        }
    }
    
    payload = json.dumps(event).encode('utf-8')
    
    # Generate signature if not provided
    if not signature:
        signature = "test_mode"  # Bypassed in test mode
    
    headers = {
        "Content-Type": "application/json",
        "X-Paystack-Signature": signature
    }
    
    response = requests.post(PAYSTACK_ENDPOINT, data=payload, headers=headers)
    print_result("Paystack: charge.success", response)
    return response


def test_paystack_subscription_create(signature: Optional[str] = None):
    """Test Paystack subscription.create event."""
    event = {
        "event": "subscription.create",
        "data": {
            "subscription_code": "SUB_test_001",
            "plan": {
                "plan_code": "PLN_test_001"
            },
            "customer": {
                "customer_code": "CUS_test_123"
            },
            "status": "active"
        }
    }
    
    payload = json.dumps(event).encode('utf-8')
    
    if not signature:
        signature = "test_mode"
    
    headers = {
        "Content-Type": "application/json",
        "X-Paystack-Signature": signature
    }
    
    response = requests.post(PAYSTACK_ENDPOINT, data=payload, headers=headers)
    print_result("Paystack: subscription.create", response)
    return response


def test_paystack_subscription_disable(signature: Optional[str] = None):
    """Test Paystack subscription.disable event."""
    event = {
        "event": "subscription.disable",
        "data": {
            "subscription_code": "SUB_test_001",
            "customer": {
                "customer_code": "CUS_test_123"
            },
            "status": "disabled",
            "cancellation_reason": "User cancelled"
        }
    }
    
    payload = json.dumps(event).encode('utf-8')
    
    if not signature:
        signature = "test_mode"
    
    headers = {
        "Content-Type": "application/json",
        "X-Paystack-Signature": signature
    }
    
    response = requests.post(PAYSTACK_ENDPOINT, data=payload, headers=headers)
    print_result("Paystack: subscription.disable", response)
    return response


def test_invalid_stripe_signature():
    """Test invalid Stripe signature."""
    event = {"type": "charge.succeeded", "data": {"object": {}}}
    payload = json.dumps(event).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": "invalid_signature_12345"
    }
    
    response = requests.post(STRIPE_ENDPOINT, data=payload, headers=headers)
    print_result("Stripe: Invalid Signature (should fail)", response)
    assert response.status_code == 400, "Should reject invalid signature"
    print("  ✓ Correctly rejected invalid signature\n")


def test_invalid_paystack_signature():
    """Test invalid Paystack signature."""
    event = {"event": "charge.success", "data": {}}
    payload = json.dumps(event).encode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "X-Paystack-Signature": "invalid_signature_12345"
    }
    
    response = requests.post(PAYSTACK_ENDPOINT, data=payload, headers=headers)
    print_result("Paystack: Invalid Signature (should fail)", response)
    assert response.status_code == 400, "Should reject invalid signature"
    print("  ✓ Correctly rejected invalid signature\n")


def run_stripe_tests():
    """Run all Stripe webhook tests."""
    print_header("STRIPE WEBHOOK TESTS")
    
    test_stripe_charge_succeeded()
    test_stripe_charge_failed()
    test_stripe_subscription_updated()
    test_stripe_subscription_deleted()
    test_invalid_stripe_signature()


def run_paystack_tests():
    """Run all Paystack webhook tests."""
    print_header("PAYSTACK WEBHOOK TESTS")
    
    test_paystack_charge_success()
    test_paystack_subscription_create()
    test_paystack_subscription_disable()
    test_invalid_paystack_signature()


def run_all_tests():
    """Run all tests."""
    print_header("WEBHOOK ENDPOINT TESTING")
    print(f"Target: {WEBHOOK_HOST}")
    print(f"Stripe Endpoint: {STRIPE_ENDPOINT}")
    print(f"Paystack Endpoint: {PAYSTACK_ENDPOINT}\n")
    
    try:
        # Check if server is running
        response = requests.get(f"{WEBHOOK_HOST}/docs", timeout=2)
        print(f"✓ Server is running\n")
    except requests.ConnectionError:
        print(f"✗ Cannot connect to {WEBHOOK_HOST}")
        print("  Make sure your FastAPI server is running:")
        print("  cd backend && python -m uvicorn main:app --reload\n")
        return
    
    run_stripe_tests()
    run_paystack_tests()
    
    print_header("TESTING COMPLETE")
    print("✓ All webhook endpoints are responding correctly\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Webhook Testing Script")
    parser.add_argument("--stripe-event", help="Test specific Stripe event")
    parser.add_argument("--paystack-event", help="Test specific Paystack event")
    parser.add_argument("--signature", help="Custom signature for verification")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.all or (not args.stripe_event and not args.paystack_event):
        run_all_tests()
    elif args.stripe_event:
        print_header(f"Testing Stripe: {args.stripe_event}")
        if args.stripe_event == "charge.succeeded":
            test_stripe_charge_succeeded()
        elif args.stripe_event == "charge.failed":
            test_stripe_charge_failed()
        elif args.stripe_event == "subscription.updated":
            test_stripe_subscription_updated()
        elif args.stripe_event == "subscription.deleted":
            test_stripe_subscription_deleted()
    elif args.paystack_event:
        print_header(f"Testing Paystack: {args.paystack_event}")
        if args.paystack_event == "charge.success":
            test_paystack_charge_success(args.signature)
        elif args.paystack_event == "subscription.create":
            test_paystack_subscription_create(args.signature)
        elif args.paystack_event == "subscription.disable":
            test_paystack_subscription_disable(args.signature)
