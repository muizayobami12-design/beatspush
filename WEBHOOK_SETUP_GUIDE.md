# 🔗 Webhook Setup Guide

**For:** BeatPush Fan Club System  
**Purpose:** Configure payment provider webhooks for production

---

## 📋 Overview

Webhooks allow Stripe and Paystack to notify your application when subscription events occur (payments, cancellations, etc.).

**Required For:**
- Automatic subscription renewals
- Failed payment handling
- Subscription status updates
- Payment confirmations

---

## 🎯 Stripe Webhook Setup

### Step 1: Get Your Webhook Endpoint URL

Your webhook endpoint will be:
```
https://your-domain.com/api/v1/webhooks/stripe
```

Example:
```
https://api.beatpush.com/api/v1/webhooks/stripe
```

### Step 2: Configure Stripe Dashboard

1. **Login to Stripe Dashboard**
   - Go to https://dashboard.stripe.com
   - Navigate to **Developers** → **Webhooks**

2. **Add Endpoint**
   - Click **"Add endpoint"**
   - Enter your webhook URL
   - Description: "BeatPush Subscription Events"

3. **Select Events to Listen**
   Select these events:
   - ✅ `invoice.paid` - Payment successful
   - ✅ `invoice.payment_failed` - Payment failed
   - ✅ `customer.subscription.updated` - Subscription changed
   - ✅ `customer.subscription.deleted` - Subscription canceled

4. **Save and Get Signing Secret**
   - Click **"Add endpoint"**
   - Copy the **Signing secret** (starts with `whsec_`)
   - Add to your `.env` file:
     ```
     STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
     ```

### Step 3: Test Webhook

1. **Use Stripe CLI (Development)**
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
   ```

2. **Trigger Test Event**
   ```bash
   stripe trigger invoice.paid
   ```

3. **Check Logs**
   - Your application should log: `"Received Stripe webhook: invoice.paid"`

---

## 🌍 Paystack Webhook Setup

### Step 1: Get Your Webhook Endpoint URL

Your webhook endpoint will be:
```
https://your-domain.com/api/v1/webhooks/paystack
```

Example:
```
https://api.beatpush.com/api/v1/webhooks/paystack
```

### Step 2: Configure Paystack Dashboard

1. **Login to Paystack Dashboard**
   - Go to https://dashboard.paystack.com
   - Navigate to **Settings** → **Webhooks**

2. **Add Webhook URL**
   - Enter your webhook URL
   - Click **"Save Changes"**

3. **Get Webhook Secret**
   - In **Settings** → **API Keys & Webhooks**
   - Copy your **Secret Key** (starts with `sk_`)
   - This is used for HMAC signature verification
   - Add to your `.env` file:
     ```
     PAYSTACK_SECRET_KEY=sk_your_secret_here
     PAYSTACK_WEBHOOK_SECRET=your_webhook_secret
     ```

### Step 3: Test Webhook

1. **Use Paystack's Test Mode**
   - Make a test subscription in your app
   - Paystack will send webhooks to your endpoint

2. **Check Logs**
   - Your application should log: `"Received Paystack webhook: charge.success"`

---

## 🔐 Security Notes

### Webhook Signature Verification

**Stripe:**
- Uses `Stripe-Signature` header
- Validates using webhook secret
- Implemented in `webhooks.py`

**Paystack:**
- Uses `X-Paystack-Signature` header
- HMAC SHA512 verification
- Implemented in `webhooks.py`

### Test Mode

**Without webhook secrets configured:**
- Webhooks still work (test mode)
- Signature verification skipped
- ⚠️ **NOT for production**

**For production:**
- ✅ Always configure webhook secrets
- ✅ Use HTTPS endpoints
- ✅ Monitor webhook logs

---

## 📊 Webhook Events Handled

### Stripe Events

| Event | Handler | Action |
|-------|---------|--------|
| `invoice.paid` | `_handle_invoice_paid` | Mark payment successful, reset failed counter |
| `invoice.payment_failed` | `_handle_invoice_payment_failed` | Increment failed counter, schedule retry |
| `customer.subscription.updated` | `_handle_subscription_updated` | Sync subscription status |
| `customer.subscription.deleted` | `_handle_subscription_deleted` | Cancel subscription |

### Paystack Events

| Event | Handler | Action |
|-------|---------|--------|
| `charge.success` | `_handle_paystack_charge_success` | Record payment, update subscription |
| `subscription.create` | `_handle_paystack_subscription_create` | Log new subscription |
| `subscription.disable` | `_handle_paystack_subscription_disable` | Cancel subscription |

---

## 🧪 Testing Webhooks Locally

### Using ngrok (Recommended)

1. **Install ngrok**
   ```bash
   npm install -g ngrok
   ```

2. **Start Your App**
   ```bash
   cd backend
   python main.py
   ```

3. **Create ngrok Tunnel**
   ```bash
   ngrok http 8000
   ```

4. **Copy HTTPS URL**
   ```
   https://abc123.ngrok.io
   ```

5. **Update Webhook URLs**
   - Stripe: `https://abc123.ngrok.io/api/v1/webhooks/stripe`
   - Paystack: `https://abc123.ngrok.io/api/v1/webhooks/paystack`

6. **Test**
   - Create a subscription in your app
   - Watch ngrok logs + app logs

---

## 🔍 Debugging Webhooks

### Check Application Logs

```bash
# Your app should log webhook events
grep "Received Stripe webhook" logs/app.log
grep "Received Paystack webhook" logs/app.log
```

### Common Issues

#### 1. Webhook Not Received
- ✅ Check firewall settings
- ✅ Verify URL is publicly accessible
- ✅ Check webhook URL in provider dashboard
- ✅ Ensure app is running

#### 2. Signature Verification Failed
- ✅ Check webhook secret is correct
- ✅ Verify secret matches provider dashboard
- ✅ Check for whitespace in `.env` file

#### 3. Subscription Not Updated
- ✅ Check database logs
- ✅ Verify subscription ID matches
- ✅ Check error logs for exceptions
- ✅ Verify database connection

### Enable Debug Logging

Add to your `.env`:
```
DEBUG=True
DATABASE_ECHO=True
```

---

## ✅ Production Checklist

Before going live:

- [ ] Webhook URLs configured in Stripe dashboard
- [ ] Webhook URLs configured in Paystack dashboard
- [ ] Webhook secrets added to `.env`
- [ ] HTTPS enabled on webhook endpoints
- [ ] Firewall allows webhook traffic
- [ ] Test webhook with real provider
- [ ] Monitor logs for webhook events
- [ ] Setup error alerting (Sentry)
- [ ] Document webhook URLs in runbook

---

## 📞 Support

**Stripe Webhooks Documentation:**
https://stripe.com/docs/webhooks

**Paystack Webhooks Documentation:**
https://paystack.com/docs/payments/webhooks

**Webhook Testing Tool:**
https://webhook.site (for testing HTTP requests)

---

## 🎯 Quick Reference

### Environment Variables

```bash
# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Paystack
PAYSTACK_SECRET_KEY=sk_live_...
PAYSTACK_PUBLIC_KEY=pk_live_...
PAYSTACK_WEBHOOK_SECRET=...
```

### Webhook URLs

```
Production:
https://api.beatpush.com/api/v1/webhooks/stripe
https://api.beatpush.com/api/v1/webhooks/paystack

Development (ngrok):
https://abc123.ngrok.io/api/v1/webhooks/stripe
https://abc123.ngrok.io/api/v1/webhooks/paystack

Local (no external access):
http://localhost:8000/api/v1/webhooks/stripe
http://localhost:8000/api/v1/webhooks/paystack
```

---

**Setup Complete!** ✅

Your webhook system is now configured to automatically process subscription events.

