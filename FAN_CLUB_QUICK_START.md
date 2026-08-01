# 🚀 Fan Club System - Quick Start Guide

**Get your fan club system running in 5 minutes!**

---

## ✅ Prerequisites

- Python 3.9+
- PostgreSQL running
- Redis running (optional, for full features)

---

## 🏃 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install stripe paystackapi apscheduler
```

(Other dependencies should already be installed)

### 2. Update Environment Variables

The system works in **TEST MODE** by default, but you can configure production keys:

```bash
# Optional - for production use
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

PAYSTACK_SECRET_KEY=sk_live_your_key
PAYSTACK_PUBLIC_KEY=pk_live_your_key
PAYSTACK_WEBHOOK_SECRET=your_secret
```

**Note:** Test mode works without these! System uses fallback values.

### 3. Start the Application

```bash
python main.py
```

You should see:
```
🚀 BeatPush v1.0.0 starting up...
✅ Database initialized successfully!
⏰ Setting up background jobs...
✅ Background jobs configured and started
📅 Active jobs: 6
✅ Application ready!
```

### 4. Test the API

Open your browser:
```
http://localhost:8000/api/v1/docs
```

You'll see **27 fan club endpoints** ready to use! 🎉

---

## 📚 API Endpoints Overview

### Fan Club Management
```
POST   /api/v1/fan-clubs              # Create fan club
GET    /api/v1/fan-clubs/me           # Get my fan club
PUT    /api/v1/fan-clubs/me           # Update fan club
DELETE /api/v1/fan-clubs/me           # Deactivate
GET    /api/v1/fan-clubs/me/stats     # Get statistics
GET    /api/v1/fan-clubs/me/analytics # Get analytics ✨
GET    /api/v1/fan-clubs/{creator_id} # Public view
```

### Tier Management
```
POST   /api/v1/fan-clubs/me/tiers     # Create tier
GET    /api/v1/fan-clubs/{id}/tiers   # List tiers
PUT    /api/v1/fan-clubs/me/tiers/{id} # Update tier
DELETE /api/v1/fan-clubs/me/tiers/{id} # Delete tier
```

### Subscriptions
```
POST   /api/v1/fan-clubs/subscriptions     # Subscribe
GET    /api/v1/fan-clubs/subscriptions/me  # My subscriptions
GET    /api/v1/fan-clubs/subscriptions/{id} # Get details
PUT    /api/v1/fan-clubs/subscriptions/{id} # Change tier
DELETE /api/v1/fan-clubs/subscriptions/{id} # Cancel
POST   /api/v1/fan-clubs/subscriptions/{id}/pause  # Pause
POST   /api/v1/fan-clubs/subscriptions/{id}/resume # Resume
```

### Webhooks
```
POST   /api/v1/webhooks/stripe         # Stripe events
POST   /api/v1/webhooks/paystack       # Paystack events
```

---

## 🎯 Quick Test Flow

### Step 1: Create a Fan Club

```bash
curl -X POST "http://localhost:8000/api/v1/fan-clubs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Exclusive Club",
    "description": "Join for exclusive content!",
    "welcome_message": "Welcome to my club!"
  }'
```

### Step 2: Add a Tier

```bash
curl -X POST "http://localhost:8000/api/v1/fan-clubs/me/tiers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gold Tier",
    "description": "Premium access",
    "tier_level": 3,
    "monthly_price": 9.99,
    "benefits": ["Exclusive tracks", "Early releases", "Direct messages"]
  }'
```

### Step 3: Subscribe (as a fan)

```bash
curl -X POST "http://localhost:8000/api/v1/fan-clubs/subscriptions" \
  -H "Authorization: Bearer FAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tier_id": "tier-id-here",
    "billing_cycle": "monthly",
    "payment_method": {
      "provider": "stripe",
      "token": "tok_visa"
    }
  }'
```

### Step 4: Check Analytics

```bash
curl -X GET "http://localhost:8000/api/v1/fan-clubs/me/analytics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

You'll get:
- MRR (Monthly Recurring Revenue)
- Churn rate
- LTV (Lifetime Value)
- Revenue forecast
- Engagement metrics

---

## 🔧 Background Jobs

**These run automatically:**

| Job | Schedule | Purpose |
|-----|----------|---------|
| Subscription Renewals | 2:00 AM daily | Process renewals |
| Failed Payment Retry | 10:00 AM daily | Retry failed payments |
| Renewal Reminders | 9:00 AM daily | Remind 3 days ahead |
| Trial Expiration | 3:00 AM daily | Cancel expired trials |
| Welcome Messages | Every hour | Welcome new subscribers |
| Engagement Messages | 11:00 AM daily | Anniversary messages |

**Check job status:**
- Jobs start automatically with the app
- Check logs for execution:
  ```bash
  grep "Processing subscription renewals" logs/app.log
  ```

---

## 🎨 Example: Complete Creator Flow

### 1. Creator Signs Up
```bash
# Register as creator
POST /api/v1/auth/register
{
  "email": "creator@example.com",
  "username": "creator",
  "account_type": "creator"
}
```

### 2. Creator Creates Fan Club
```bash
POST /api/v1/fan-clubs
{
  "name": "Creator's Exclusive Club",
  "description": "Get exclusive content and perks!"
}
```

### 3. Creator Adds Tiers
```bash
# Bronze Tier
POST /api/v1/fan-clubs/me/tiers
{
  "name": "Bronze",
  "tier_level": 1,
  "monthly_price": 4.99,
  "benefits": ["Exclusive posts"]
}

# Silver Tier
POST /api/v1/fan-clubs/me/tiers
{
  "name": "Silver",
  "tier_level": 2,
  "monthly_price": 9.99,
  "benefits": ["Exclusive posts", "Early music releases"]
}

# Gold Tier
POST /api/v1/fan-clubs/me/tiers
{
  "name": "Gold",
  "tier_level": 3,
  "monthly_price": 19.99,
  "benefits": ["Everything", "1-on-1 Q&A", "Discord access"]
}
```

### 4. Creator Posts Exclusive Content
```bash
POST /api/v1/fan-clubs/exclusive-content
{
  "content_type": "track",
  "content_id": "track-123",
  "tier_id": "gold-tier-id"
}
```

### 5. Fan Subscribes
```bash
POST /api/v1/fan-clubs/subscriptions
{
  "tier_id": "silver-tier-id",
  "billing_cycle": "monthly",
  "payment_method": {
    "provider": "stripe",
    "token": "pm_card_visa"
  }
}
```

### 6. Creator Checks Analytics
```bash
GET /api/v1/fan-clubs/me/analytics

Response:
{
  "mrr": {
    "total_mrr": 150.00,
    "creator_mrr": 135.00,
    "by_tier": {
      "Bronze": {"mrr": 20.00, "subscriber_count": 4},
      "Silver": {"mrr": 80.00, "subscriber_count": 8},
      "Gold": {"mrr": 50.00, "subscriber_count": 2}
    }
  },
  "churn": {
    "churn_rate_percent": 3.5
  },
  "ltv": {
    "projected_ltv_12_months": 120.00
  }
}
```

---

## 🔍 Monitoring & Debugging

### Check Application Logs
```bash
# All logs
tail -f logs/app.log

# Webhook events
grep "Received.*webhook" logs/app.log

# Background jobs
grep "Processing.*subscription" logs/app.log

# Errors
grep "ERROR" logs/app.log
```

### Database Queries
```sql
-- Check fan clubs
SELECT * FROM fan_clubs;

-- Check tiers
SELECT * FROM membership_tiers;

-- Check subscriptions
SELECT * FROM subscriptions WHERE status = 'active';

-- Check payments
SELECT * FROM subscription_payments ORDER BY created_at DESC LIMIT 10;
```

---

## 🚨 Common Issues

### Issue: "Module not found: stripe"
**Fix:**
```bash
pip install stripe paystackapi apscheduler
```

### Issue: "Database connection failed"
**Fix:** Make sure PostgreSQL is running
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (if needed)
# Mac: brew services start postgresql
# Ubuntu: sudo service postgresql start
# Windows: Start PostgreSQL service
```

### Issue: "Background jobs not starting"
**Fix:** Jobs start automatically. Check logs:
```bash
grep "Background jobs configured" logs/app.log
```

### Issue: "Webhook signature verification failed"
**Fix:** Set webhook secrets in `.env` or they'll work in test mode (no verification)

---

## 🎯 What Works in Test Mode

**Without any configuration:**
- ✅ Create fan clubs
- ✅ Add tiers
- ✅ Subscribe (test payments)
- ✅ Content gating
- ✅ Analytics
- ✅ Background jobs (except webhooks)

**Needs configuration:**
- ⚠️ Real payment processing
- ⚠️ Webhook handling from providers

---

## 📖 Full Documentation

- **Implementation Status:** `FAN_CLUB_STATUS_SUMMARY.md`
- **Webhook Setup:** `WEBHOOK_SETUP_GUIDE.md`
- **Wave 9-11 Details:** `FAN_CLUB_WAVE_9_11_COMPLETE.md`
- **API Docs:** http://localhost:8000/api/v1/docs

---

## 🎉 You're Ready!

Your fan club system is now running with:
- ✅ 27 API endpoints
- ✅ Payment processing (2 providers)
- ✅ 6 automated background jobs
- ✅ Comprehensive analytics
- ✅ Webhook handlers

**Start building your creator economy! 🚀**

---

## 💡 Next Steps

1. **Test the API** - Use Swagger UI at `/api/v1/docs`
2. **Configure webhooks** - See `WEBHOOK_SETUP_GUIDE.md`
3. **Add production keys** - Update `.env` with real API keys
4. **Monitor analytics** - Check `/api/v1/fan-clubs/me/analytics`
5. **Deploy** - Move to production when ready!

---

**Questions? Check the full docs or API documentation!**

