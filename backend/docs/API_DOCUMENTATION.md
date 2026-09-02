# BeatPush Fan Club System - API Documentation

**Version:** 1.0.0  
**Base URL:** `https://api.beatpush.com/api/v1`  
**Authentication:** OAuth 2.0 + JWT Bearer Token

---

## Table of Contents

1. [Authentication](#authentication)
2. [Fan Club Management](#fan-club-management)
3. [Membership Tiers](#membership-tiers)
4. [Subscriptions](#subscriptions)
5. [Subscribers](#subscribers)
6. [Exclusive Content](#exclusive-content)
7. [Analytics](#analytics)
8. [Webhooks](#webhooks)
9. [Error Handling](#error-handling)

---

## Authentication

### Getting a Token

**Endpoint:** `POST /auth/login`

```bash
curl -X POST https://api.beatpush.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "creator@example.com",
    "password": "secure_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Token

Include in every request:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.beatpush.com/api/v1/fan-clubs
```

---

## Fan Club Management

### Create Fan Club

**Endpoint:** `POST /fan-clubs`

**Request:**
```bash
curl -X POST https://api.beatpush.com/api/v1/fan-clubs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "The Weeknd Premium",
    "description": "Exclusive content and early access",
    "welcome_message": "Welcome to my fan club!"
  }'
```

**Response (201):**
```json
{
  "id": "fc_123abc",
  "creator_id": "user_456def",
  "name": "The Weeknd Premium",
  "description": "Exclusive content and early access",
  "welcome_message": "Welcome to my fan club!",
  "is_active": true,
  "total_members": 0,
  "monthly_revenue": "0.00",
  "created_at": "2026-08-31T10:00:00Z",
  "updated_at": null
}
```

### Get Fan Club

**Endpoint:** `GET /fan-clubs/{id}`

```bash
curl -X GET https://api.beatpush.com/api/v1/fan-clubs/fc_123abc \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200):**
```json
{
  "id": "fc_123abc",
  "creator_id": "user_456def",
  "name": "The Weeknd Premium",
  "is_active": true,
  "total_members": 150,
  "monthly_revenue": "1500.00",
  "created_at": "2026-08-31T10:00:00Z",
  "updated_at": "2026-08-31T15:30:00Z"
}
```

### List My Fan Clubs

**Endpoint:** `GET /fan-clubs/my`

```bash
curl -X GET https://api.beatpush.com/api/v1/fan-clubs/my \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200):**
```json
{
  "fan_clubs": [
    {
      "id": "fc_123abc",
      "name": "The Weeknd Premium",
      "total_members": 150,
      "monthly_revenue": "1500.00"
    },
    {
      "id": "fc_789xyz",
      "name": "Extended Versions",
      "total_members": 75,
      "monthly_revenue": "750.00"
    }
  ],
  "total": 2
}
```

### Update Fan Club

**Endpoint:** `PUT /fan-clubs/{id}`

```bash
curl -X PUT https://api.beatpush.com/api/v1/fan-clubs/fc_123abc \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "welcome_message": "Updated welcome message"
  }'
```

**Response (200):** Updated fan club object

### Delete Fan Club

**Endpoint:** `DELETE /fan-clubs/{id}`

```bash
curl -X DELETE https://api.beatpush.com/api/v1/fan-clubs/fc_123abc \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** 204 No Content

---

## Membership Tiers

### Create Tier

**Endpoint:** `POST /fan-clubs/{id}/tiers`

```bash
curl -X POST https://api.beatpush.com/api/v1/fan-clubs/fc_123abc/tiers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Premium",
    "description": "Exclusive content and early releases",
    "tier_level": 2,
    "price_monthly": 9.99,
    "benefits": [
      "Exclusive content",
      "Early releases",
      "Monthly live chat"
    ]
  }'
```

**Response (201):**
```json
{
  "id": "tier_123abc",
  "fan_club_id": "fc_123abc",
  "name": "Premium",
  "description": "Exclusive content and early releases",
  "tier_level": 2,
  "price_monthly": "9.99",
  "price_yearly": "99.90",
  "benefits": [
    "Exclusive content",
    "Early releases",
    "Monthly live chat"
  ],
  "is_active": true,
  "subscriber_count": 0,
  "created_at": "2026-08-31T10:00:00Z"
}
```

### List Tiers

**Endpoint:** `GET /fan-clubs/{id}/tiers`

```bash
curl -X GET https://api.beatpush.com/api/v1/fan-clubs/fc_123abc/tiers \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Tier

**Endpoint:** `PUT /fan-clubs/{id}/tiers/{tier_id}`

### Delete Tier

**Endpoint:** `DELETE /fan-clubs/{id}/tiers/{tier_id}`

---

## Subscriptions

### Create Subscription

**Endpoint:** `POST /fan-clubs/subscribe`

```bash
curl -X POST https://api.beatpush.com/api/v1/fan-clubs/subscribe \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fan_club_id": "fc_123abc",
    "tier_id": "tier_456def",
    "billing_cycle": "monthly",
    "payment_method_token": "tok_visa_4242",
    "payment_provider": "stripe"
  }'
```

**Response (201):**
```json
{
  "id": "sub_123abc",
  "fan_club_id": "fc_123abc",
  "tier_id": "tier_456def",
  "subscriber_id": "user_789xyz",
  "status": "active",
  "billing_cycle": "monthly",
  "price_paid": "9.99",
  "currency": "USD",
  "current_period_start": "2026-08-31T10:00:00Z",
  "current_period_end": "2026-09-30T10:00:00Z",
  "started_at": "2026-08-31T10:00:00Z",
  "auto_renew": true,
  "payment_provider": "stripe",
  "created_at": "2026-08-31T10:00:00Z"
}
```

### Get Subscription

**Endpoint:** `GET /fan-clubs/subscriptions/{id}`

```bash
curl -X GET https://api.beatpush.com/api/v1/fan-clubs/subscriptions/sub_123abc \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List My Subscriptions

**Endpoint:** `GET /fan-clubs/subscriptions/my`

```bash
curl -X GET https://api.beatpush.com/api/v1/fan-clubs/subscriptions/my \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Change Tier

**Endpoint:** `PUT /fan-clubs/subscriptions/{id}/tier`

```bash
curl -X PUT https://api.beatpush.com/api/v1/fan-clubs/subscriptions/sub_123abc/tier \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_tier_id": "tier_vip_123"
  }'
```

### Pause Subscription

**Endpoint:** `POST /fan-clubs/subscriptions/{id}/pause`

```bash
curl -X POST https://api.beatpush.com/api/v1/fan-clubs/subscriptions/sub_123abc/pause \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pause_until": "2026-09-30T10:00:00Z"
  }'
```

### Resume Subscription

**Endpoint:** `POST /fan-clubs/subscriptions/{id}/resume`

```bash
curl -X POST https://api.beatpush.com/api/v1/fan-clubs/subscriptions/sub_123abc/resume \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Cancel Subscription

**Endpoint:** `POST /fan-clubs/subscriptions/{id}/cancel`

```bash
curl -X POST https://api.beatpush.com/api/v1/fan-clubs/subscriptions/sub_123abc/cancel \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Too expensive"
  }'
```

---

## Subscribers

### List Fan Club Subscribers

**Endpoint:** `GET /fan-clubs/{id}/subscribers`

```bash
curl -X GET 'https://api.beatpush.com/api/v1/fan-clubs/fc_123abc/subscribers?page=1&page_size=20' \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "subscribers": [
    {
      "subscriber_id": "user_123",
      "username": "john_doe",
      "full_name": "John Doe",
      "avatar_url": "https://...",
      "tier_name": "Premium",
      "tier_level": 2,
      "subscription_status": "active",
      "subscribed_since": "2026-06-01T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

### Send Broadcast Message

**Endpoint:** `POST /fan-clubs/{id}/broadcast`

```bash
curl -X POST https://api.beatpush.com/api/v1/fan-clubs/fc_123abc/broadcast \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Exclusive Content",
    "message": "Check out the new exclusive content available now!",
    "tier_levels": [2, 3],
    "send_email": true,
    "send_push": true
  }'
```

**Response (202):**
```json
{
  "message": "Broadcast scheduled",
  "recipients": 150,
  "status": "queued"
}
```

---

## Exclusive Content

### Mark Content Exclusive

**Endpoint:** `POST /fan-clubs/{id}/exclusive-content`

```bash
curl -X POST https://api.beatpush.com/api/v1/fan-clubs/fc_123abc/exclusive-content \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "post",
    "content_id": "post_123abc",
    "minimum_tier_level": 2,
    "teaser_text": "Check out this exclusive content!"
  }'
```

### Check Content Access

**Endpoint:** `GET /fan-clubs/{id}/exclusive-content/{content_id}/access`

```bash
curl -X GET https://api.beatpush.com/api/v1/fan-clubs/fc_123abc/exclusive-content/post_123abc/access \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "has_access": true,
  "required_tier_level": 2,
  "current_tier_level": 3
}
```

---

## Analytics

### Get MRR

**Endpoint:** `GET /analytics/revenue/mrr?fan_club_id={id}&month={YYYY-MM}`

```bash
curl -X GET 'https://api.beatpush.com/api/v1/analytics/revenue/mrr?fan_club_id=fc_123abc&month=2026-08' \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "mrr": "1500.00",
  "active_subscriptions": 150,
  "month": "2026-08",
  "currency": "USD",
  "breakdown": {
    "Basic": "500.00",
    "Premium": "750.00",
    "VIP": "250.00"
  }
}
```

### Get ARPU

**Endpoint:** `GET /analytics/revenue/arpu?fan_club_id={id}&days={days}`

```bash
curl -X GET 'https://api.beatpush.com/api/v1/analytics/revenue/arpu?fan_club_id=fc_123abc&days=30' \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Revenue Trend

**Endpoint:** `GET /analytics/revenue/trend?fan_club_id={id}&months={months}`

```bash
curl -X GET 'https://api.beatpush.com/api/v1/analytics/revenue/trend?fan_club_id=fc_123abc&months=12' \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Churn Rate

**Endpoint:** `GET /analytics/churn/rate?fan_club_id={id}&month={YYYY-MM}`

```bash
curl -X GET 'https://api.beatpush.com/api/v1/analytics/churn/rate?fan_club_id=fc_123abc' \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Revenue Forecast

**Endpoint:** `GET /analytics/forecast/revenue?fan_club_id={id}&months={months}&method={linear|seasonal}`

```bash
curl -X GET 'https://api.beatpush.com/api/v1/analytics/forecast/revenue?fan_club_id=fc_123abc&months=6&method=linear' \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Dashboard Summary

**Endpoint:** `GET /analytics/dashboard/summary?fan_club_id={id}`

```bash
curl -X GET 'https://api.beatpush.com/api/v1/analytics/dashboard/summary?fan_club_id=fc_123abc' \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "mrr": "1500.00",
  "arpu": "10.00",
  "churn_rate": 2.5,
  "retention_rate": 97.5,
  "forecast_next_month": "1550.00",
  "top_tier": "Premium",
  "new_subscribers": 15,
  "active_subscribers": 150,
  "monthly_growth_percent": 11.1,
  "trending": "up"
}
```

### Compare Periods

**Endpoint:** `GET /analytics/compare/period?fan_club_id={id}&period1_start={YYYY-MM-DD}&period1_end={YYYY-MM-DD}&period2_start={YYYY-MM-DD}&period2_end={YYYY-MM-DD}`

```bash
curl -X GET 'https://api.beatpush.com/api/v1/analytics/compare/period?fan_club_id=fc_123abc&period1_start=2026-07-01&period1_end=2026-07-31&period2_start=2026-08-01&period2_end=2026-08-31' \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Webhooks

### Stripe Webhook

**Endpoint:** `POST /webhooks/stripe`

Stripe sends webhook events to this endpoint. No authentication required (signature-verified).

**Supported Events:**
- `invoice.paid` - Payment received
- `invoice.payment_failed` - Payment failed
- `customer.subscription.updated` - Subscription updated
- `customer.subscription.deleted` - Subscription cancelled

### Paystack Webhook

**Endpoint:** `POST /webhooks/paystack`

Paystack sends webhook events to this endpoint. No authentication required (signature-verified).

**Supported Events:**
- `charge.success` - Charge successful
- `subscription.create` - Subscription created
- `subscription.disable` - Subscription disabled

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error code",
  "detail": "Detailed error message",
  "status": 400
}
```

### Common Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | BAD_REQUEST | Invalid request parameters |
| 401 | UNAUTHORIZED | Missing or invalid authentication |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource conflict (e.g., duplicate) |
| 422 | UNPROCESSABLE_ENTITY | Validation error |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

### Example Error Response

```bash
curl -X GET https://api.beatpush.com/api/v1/fan-clubs/nonexistent \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (404):**
```json
{
  "error": "NOT_FOUND",
  "detail": "Fan club not found",
  "status": 404
}
```

---

## Rate Limiting

All endpoints are rate-limited:
- **1000 requests** per hour per user
- **Rate limit headers** included in response:
  - `X-RateLimit-Limit: 1000`
  - `X-RateLimit-Remaining: 999`
  - `X-RateLimit-Reset: 1693468800`

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response:**
```json
{
  "data": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

---

## Webhooks Configuration

### Setting Up Stripe Webhooks

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://api.beatpush.com/api/v1/webhooks/stripe`
3. Select events:
   - `invoice.paid`
   - `invoice.payment_failed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`

### Setting Up Paystack Webhooks

1. Go to Paystack Dashboard → Settings → Webhooks
2. Add URL: `https://api.beatpush.com/api/v1/webhooks/paystack`
3. Events handled automatically

---

## API Version

Current API version: **1.0.0**

For older versions, use:
- `/api/v0` - Legacy (deprecated)

---

**Last Updated:** August 31, 2026  
**Status:** Production Ready ✅
