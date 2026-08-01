# 📚 Fan Club System - API Documentation

**Version:** 1.0.0  
**Base URL:** `https://api.beatpush.com/api/v1`  
**Authentication:** Bearer Token (JWT)

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Fan Club Management](#fan-club-management)
3. [Tier Management](#tier-management)
4. [Subscriptions](#subscriptions)
5. [Subscriber Management](#subscriber-management)
6. [Exclusive Content](#exclusive-content)
7. [Analytics](#analytics)
8. [Webhooks](#webhooks)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication

All endpoints require authentication via JWT Bearer token.

**Header:**
```
Authorization: Bearer <your_jwt_token>
```

**Get Token:**
```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

---

## 🎪 Fan Club Management

### Create Fan Club

**Creator only**

```http
POST /api/v1/fan-clubs
```

**Request Body:**
```json
{
  "name": "My Exclusive Club",
  "description": "Join for exclusive content and perks!",
  "welcome_message": "Welcome to my exclusive community! 🎉"
}
```

**Response:** `201 Created`
```json
{
  "id": "fanclub-uuid",
  "creator_id": "user-uuid",
  "name": "My Exclusive Club",
  "description": "Join for exclusive content and perks!",
  "welcome_message": "Welcome to my exclusive community! 🎉",
  "is_active": true,
  "total_members": 0,
  "monthly_revenue": "0.00",
  "created_at": "2026-08-01T12:00:00Z"
}
```

**Eligibility:**
- Must be a creator account
- Must not already have a fan club
- Account must be verified

---

### Get My Fan Club

**Creator only**

```http
GET /api/v1/fan-clubs/me
```

**Response:** `200 OK`
```json
{
  "id": "fanclub-uuid",
  "name": "My Exclusive Club",
  "description": "...",
  "total_members": 42,
  "monthly_revenue": "420.00",
  "tiers": [
    {
      "id": "tier-uuid",
      "name": "Gold",
      "tier_level": 3,
      "monthly_price": "19.99",
      "subscriber_count": 15
    }
  ]
}
```

---

### Update Fan Club

**Creator only**

```http
PUT /api/v1/fan-clubs/me
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "welcome_message": "New welcome message"
}
```

**Response:** `200 OK`
```json
{
  "id": "fanclub-uuid",
  "name": "Updated Name",
  "description": "Updated description",
  ...
}
```

---

### Get Fan Club Statistics

**Creator only**

```http
GET /api/v1/fan-clubs/me/stats
```

**Response:** `200 OK`
```json
{
  "total_members": 42,
  "monthly_revenue": "420.00",
  "active_subscriptions": 40,
  "revenue_by_tier": {
    "Bronze": "100.00",
    "Silver": "180.00",
    "Gold": "140.00"
  },
  "subscribers_by_tier": {
    "Bronze": 20,
    "Silver": 18,
    "Gold": 4
  }
}
```

---

### View Public Fan Club

**Anyone can access**

```http
GET /api/v1/fan-clubs/{creator_id}
```

**Response:** `200 OK`
```json
{
  "id": "fanclub-uuid",
  "creator": {
    "id": "user-uuid",
    "username": "creator_name",
    "display_name": "Creator Name"
  },
  "name": "My Exclusive Club",
  "description": "...",
  "total_members": 42,
  "tiers": [
    {
      "name": "Gold",
      "tier_level": 3,
      "monthly_price": "19.99",
      "benefits": ["Benefit 1", "Benefit 2"]
    }
  ]
}
```

---

### Deactivate Fan Club

**Creator only**

```http
DELETE /api/v1/fan-clubs/me
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Fan club deactivated successfully"
}
```

**Requirements:**
- No active subscribers
- All subscriptions must be cancelled first

---

## 🎯 Tier Management

### Create Tier

**Creator only**

```http
POST /api/v1/fan-clubs/me/tiers
```

**Request Body:**
```json
{
  "name": "Gold Tier",
  "description": "Premium access to all content",
  "tier_level": 3,
  "monthly_price": 19.99,
  "benefits": [
    "All exclusive content",
    "Early music releases",
    "Direct messaging",
    "Discord access"
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": "tier-uuid",
  "name": "Gold Tier",
  "tier_level": 3,
  "monthly_price": "19.99",
  "yearly_price": "199.90",
  "benefits": [...],
  "is_active": true,
  "subscriber_count": 0
}
```

**Validation:**
- `tier_level`: 1-3 (Bronze, Silver, Gold)
- `monthly_price`: $2.99 - $99.99
- `yearly_price`: Auto-calculated (10% discount)
- Maximum 3 tiers per fan club

---

### List Tiers

**Anyone can access**

```http
GET /api/v1/fan-clubs/{fan_club_id}/tiers
```

**Response:** `200 OK`
```json
[
  {
    "id": "tier-1",
    "name": "Bronze",
    "tier_level": 1,
    "monthly_price": "4.99",
    "yearly_price": "49.90",
    "benefits": ["Exclusive posts"],
    "subscriber_count": 20
  },
  {
    "id": "tier-2",
    "name": "Silver",
    "tier_level": 2,
    "monthly_price": "9.99",
    "yearly_price": "99.90",
    "benefits": ["Exclusive posts", "Early releases"],
    "subscriber_count": 15
  }
]
```

---

### Update Tier

**Creator only**

```http
PUT /api/v1/fan-clubs/me/tiers/{tier_id}
```

**Request Body:**
```json
{
  "description": "Updated description",
  "benefits": ["New benefit 1", "New benefit 2"]
}
```

**Response:** `200 OK`

**Note:** Existing subscribers are notified of changes.

---

### Delete Tier

**Creator only**

```http
DELETE /api/v1/fan-clubs/me/tiers/{tier_id}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Tier deleted successfully"
}
```

**Requirements:**
- No active subscribers on this tier

---

## 💳 Subscriptions

### Subscribe to Tier

**Fan/User**

```http
POST /api/v1/fan-clubs/subscriptions
```

**Request Body:**
```json
{
  "tier_id": "tier-uuid",
  "billing_cycle": "monthly",
  "payment_method": {
    "provider": "stripe",
    "token": "pm_card_visa",
    "save_card": true
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "subscription-uuid",
  "tier_id": "tier-uuid",
  "tier_name": "Gold Tier",
  "status": "active",
  "billing_cycle": "monthly",
  "price_paid": "19.99",
  "currency": "USD",
  "current_period_start": "2026-08-01T00:00:00Z",
  "current_period_end": "2026-09-01T00:00:00Z",
  "next_billing_date": "2026-09-01T00:00:00Z",
  "auto_renew": true
}
```

**Payment Providers:**
- `stripe` - Credit/debit cards worldwide
- `paystack` - African payment methods

**Billing Cycles:**
- `monthly` - Charged monthly
- `yearly` - Charged yearly (10% discount)

---

### List My Subscriptions

**User**

```http
GET /api/v1/fan-clubs/subscriptions/me
```

**Query Parameters:**
- `skip`: Offset for pagination (default: 0)
- `limit`: Limit results (default: 10)

**Response:** `200 OK`
```json
{
  "subscriptions": [
    {
      "id": "sub-uuid",
      "fan_club": {
        "name": "Creator's Club",
        "creator": "creator_username"
      },
      "tier": {
        "name": "Gold",
        "tier_level": 3
      },
      "status": "active",
      "billing_cycle": "monthly",
      "next_billing_date": "2026-09-01T00:00:00Z"
    }
  ],
  "total": 3
}
```

---

### Get Subscription Details

**User (subscriber only)**

```http
GET /api/v1/fan-clubs/subscriptions/{subscription_id}
```

**Response:** `200 OK`
```json
{
  "id": "sub-uuid",
  "tier": {...},
  "status": "active",
  "price_paid": "19.99",
  "billing_cycle": "monthly",
  "current_period_start": "2026-08-01T00:00:00Z",
  "current_period_end": "2026-09-01T00:00:00Z",
  "auto_renew": true,
  "payment_history": [
    {
      "amount": "19.99",
      "status": "completed",
      "date": "2026-08-01T12:00:00Z"
    }
  ]
}
```

---

### Change Tier (Upgrade/Downgrade)

**User (subscriber only)**

```http
PUT /api/v1/fan-clubs/subscriptions/{subscription_id}
```

**Request Body:**
```json
{
  "new_tier_id": "tier-uuid"
}
```

**Response:** `200 OK`

**Behavior:**
- **Upgrade:** Immediate, prorated charge
- **Downgrade:** Scheduled for next billing cycle

---

### Cancel Subscription

**User (subscriber only)**

```http
DELETE /api/v1/fan-clubs/subscriptions/{subscription_id}
```

**Query Parameters:**
- `immediate`: `true` or `false` (default: false)

**Response:** `200 OK`
```json
{
  "id": "sub-uuid",
  "status": "cancelled",
  "cancelled_at": "2026-08-01T12:00:00Z",
  "access_until": "2026-09-01T00:00:00Z"
}
```

**Behavior:**
- `immediate=false`: Access until end of current period
- `immediate=true`: Access ends immediately, prorated refund

---

### Pause Subscription

**User (subscriber only)**

```http
POST /api/v1/fan-clubs/subscriptions/{subscription_id}/pause
```

**Request Body:**
```json
{
  "pause_until": "2026-09-01T00:00:00Z"
}
```

**Response:** `200 OK`

**Limits:**
- Maximum 90 days pause
- Can resume anytime before pause_until date

---

### Resume Subscription

**User (subscriber only)**

```http
POST /api/v1/fan-clubs/subscriptions/{subscription_id}/resume
```

**Response:** `200 OK`
```json
{
  "id": "sub-uuid",
  "status": "active",
  "resumed_at": "2026-08-01T12:00:00Z"
}
```

---

## 👥 Subscriber Management

### List My Subscribers

**Creator only**

```http
GET /api/v1/fan-clubs/me/subscribers
```

**Query Parameters:**
- `tier_id`: Filter by tier (optional)
- `skip`: Offset (default: 0)
- `limit`: Limit (default: 20)

**Response:** `200 OK`
```json
{
  "subscribers": [
    {
      "id": "user-uuid",
      "username": "subscriber_name",
      "tier": {
        "name": "Gold",
        "tier_level": 3
      },
      "subscribed_at": "2026-07-01T00:00:00Z",
      "status": "active"
    }
  ],
  "total": 42
}
```

---

### Broadcast to Subscribers

**Creator only**

```http
POST /api/v1/fan-clubs/me/broadcast
```

**Request Body:**
```json
{
  "message": "New exclusive track dropping tomorrow! 🎵",
  "tier_ids": ["tier-1", "tier-2"]
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "recipients": 35,
  "message": "Broadcast sent successfully"
}
```

**Delivery:**
- In-app notification
- Email (if enabled)
- Push notification (if enabled)

---

## 🔒 Exclusive Content

### Mark Content Exclusive

**Creator only**

```http
POST /api/v1/fan-clubs/exclusive-content
```

**Request Body:**
```json
{
  "content_type": "track",
  "content_id": "track-uuid",
  "tier_id": "tier-uuid"
}
```

**Response:** `201 Created`

**Content Types:**
- `track` - Music tracks
- `post` - Social posts
- `video` - Video content
- `image` - Image galleries

---

### Check Content Access

**User**

```http
GET /api/v1/fan-clubs/exclusive-content/{content_type}/{content_id}/access
```

**Response:** `200 OK`
```json
{
  "has_access": true,
  "tier_required": {
    "name": "Gold",
    "tier_level": 3,
    "price": "19.99"
  },
  "user_tier": {
    "name": "Gold",
    "tier_level": 3
  }
}
```

**If no access:**
```json
{
  "has_access": false,
  "tier_required": {
    "name": "Gold",
    "tier_level": 3,
    "price": "19.99"
  },
  "upgrade_url": "/api/v1/fan-clubs/subscriptions",
  "teaser": {
    "available": true,
    "preview_percent": 20
  }
}
```

---

### List Exclusive Content

**Anyone can access**

```http
GET /api/v1/fan-clubs/{fan_club_id}/exclusive-content
```

**Query Parameters:**
- `tier_id`: Filter by tier (optional)
- `content_type`: Filter by type (optional)

**Response:** `200 OK`
```json
{
  "content": [
    {
      "content_type": "track",
      "content_id": "track-uuid",
      "tier": {
        "name": "Gold",
        "tier_level": 3
      },
      "created_at": "2026-08-01T00:00:00Z"
    }
  ],
  "total": 15
}
```

---

### Remove Exclusivity

**Creator only**

```http
DELETE /api/v1/fan-clubs/exclusive-content/{content_type}/{content_id}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Content is now public"
}
```

---

## 📊 Analytics

### Get Comprehensive Analytics

**Creator only**

```http
GET /api/v1/fan-clubs/me/analytics
```

**Response:** `200 OK`
```json
{
  "mrr": {
    "total_mrr": 420.00,
    "creator_mrr": 378.00,
    "platform_fee": 42.00,
    "by_tier": {
      "Bronze": {
        "mrr": 100.00,
        "subscriber_count": 20
      },
      "Silver": {
        "mrr": 180.00,
        "subscriber_count": 18
      },
      "Gold": {
        "mrr": 140.00,
        "subscriber_count": 7
      }
    },
    "total_active_subscribers": 45
  },
  "churn": {
    "period_months": 1,
    "churn_rate_percent": 5.2,
    "new_subscribers": 8,
    "canceled_subscribers": 3,
    "net_growth": 5,
    "growth_rate_percent": 11.1
  },
  "ltv": {
    "total_revenue": 5040.00,
    "avg_revenue_per_subscriber": 112.00,
    "projected_ltv_12_months": 240.00
  },
  "retention_cohorts": [
    {
      "cohort_month": "2026-06",
      "initial_subscribers": 30,
      "still_active": 27,
      "retention_rate_percent": 90.0
    }
  ],
  "revenue_forecast": [
    {
      "month": "2026-09",
      "projected_mrr": 441.00,
      "creator_revenue": 396.90,
      "confidence": "medium"
    },
    {
      "month": "2026-10",
      "projected_mrr": 463.05,
      "creator_revenue": 416.75,
      "confidence": "medium"
    },
    {
      "month": "2026-11",
      "projected_mrr": 486.20,
      "creator_revenue": 437.58,
      "confidence": "low"
    }
  ],
  "engagement": {
    "exclusive_content_count": 25,
    "total_views": 1500,
    "avg_views_per_content": 60.0,
    "engagement_rate_percent": 133.3,
    "views_per_subscriber": 33.3
  },
  "generated_at": "2026-08-01T12:00:00Z"
}
```

---

## 🔗 Webhooks

### Stripe Webhook

**Internal endpoint - configured in Stripe Dashboard**

```http
POST /api/v1/webhooks/stripe
```

**Events Handled:**
- `invoice.paid` - Payment successful
- `invoice.payment_failed` - Payment failed
- `customer.subscription.updated` - Subscription changed
- `customer.subscription.deleted` - Subscription canceled

---

### Paystack Webhook

**Internal endpoint - configured in Paystack Dashboard**

```http
POST /api/v1/webhooks/paystack
```

**Events Handled:**
- `charge.success` - Payment successful
- `subscription.create` - New subscription
- `subscription.disable` - Subscription canceled

---

## ❌ Error Handling

### Error Response Format

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR"
}
```

### Common Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Validation Error | Invalid data format |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal error |

---

## ⚡ Rate Limiting

**Default Limits:**
- 60 requests per minute per user
- 1000 requests per hour per user

**Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1659369600
```

**429 Response:**
```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds",
  "retry_after": 30
}
```

---

## 🚀 Quick Start Examples

### Complete Flow: Create Fan Club → Add Tier → Get First Subscriber

```bash
# 1. Create fan club
curl -X POST https://api.beatpush.com/api/v1/fan-clubs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Club",
    "description": "Exclusive content!"
  }'

# 2. Add tier
curl -X POST https://api.beatpush.com/api/v1/fan-clubs/me/tiers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gold",
    "tier_level": 3,
    "monthly_price": 19.99,
    "benefits": ["All content", "Direct messaging"]
  }'

# 3. Fan subscribes
curl -X POST https://api.beatpush.com/api/v1/fan-clubs/subscriptions \
  -H "Authorization: Bearer $FAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tier_id": "tier-uuid",
    "billing_cycle": "monthly",
    "payment_method": {
      "provider": "stripe",
      "token": "pm_card_visa"
    }
  }'

# 4. Check analytics
curl -X GET https://api.beatpush.com/api/v1/fan-clubs/me/analytics \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📞 Support

**Documentation:** https://docs.beatpush.com  
**API Status:** https://status.beatpush.com  
**Support Email:** support@beatpush.com

---

**Last Updated:** August 1, 2026  
**API Version:** 1.0.0

