# Fan Club System - Technical Design

**Feature:** Fan Club & Membership System  
**Version:** 1.0  
**Last Updated:** August 1, 2026  

---

## Architecture Overview

The Fan Club System is a subscription-based membership platform that enables creators to monetize through tiered memberships while providing exclusive content and perks to subscribers.

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Fan Club System                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Tier Config  │  │ Subscription │  │   Content    │     │
│  │  Management  │  │  Management  │  │   Gating     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Payment    │  │   Member     │  │  Analytics   │     │
│  │  Processing  │  │  Community   │  │  & Metrics   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│             External Services Integration                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Stripe    │  │   Paystack   │  │Notification  │     │
│  │      API     │  │     API      │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend:** Python 3.11+ with FastAPI
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** SQLAlchemy 2.0+
- **Payment:** Stripe API, Paystack API
- **Job Queue:** APScheduler (background tasks)
- **Email:** Existing notification service
- **Caching:** In-memory (future: Redis)

---

## Data Models

### 1. FanClub Model

**Purpose:** Represents a creator's fan club configuration

```python
class FanClub(Base):
    __tablename__ = "fan_clubs"
    
    id = Column(String(36), primary_key=True)
    creator_id = Column(String(36), ForeignKey("users.id"), unique=True)
    name = Column(String(100))  # e.g., "DJ Khaled's Squad"
    description = Column(Text)
    welcome_message = Column(Text)  # Auto-sent to new members
    is_active = Column(Boolean, default=True)
    total_members = Column(Integer, default=0)  # Cached count
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="fan_club")
    tiers = relationship("MembershipTier", back_populates="fan_club")
    subscriptions = relationship("Subscription", back_populates="fan_club")
    
    __table_args__ = (
        Index('idx_fanclub_creator', 'creator_id'),
        Index('idx_fanclub_active', 'is_active'),
    )
```

### 2. MembershipTier Model

**Purpose:** Defines subscription tiers with pricing and benefits

```python
class MembershipTier(Base):
    __tablename__ = "membership_tiers"
    
    id = Column(String(36), primary_key=True)
    fan_club_id = Column(String(36), ForeignKey("fan_clubs.id"))
    name = Column(String(50))  # Bronze, Silver, Gold
    description = Column(Text)
    tier_level = Column(Integer)  # 1=Bronze, 2=Silver, 3=Gold
    price_monthly = Column(Numeric(10, 2))  # USD
    price_yearly = Column(Numeric(10, 2))  # 10% discount
    benefits = Column(JSON)  # List of benefits
    is_active = Column(Boolean, default=True)
    subscriber_count = Column(Integer, default=0)  # Cached
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    fan_club = relationship("FanClub", back_populates="tiers")
    subscriptions = relationship("Subscription", back_populates="tier")
    
    __table_args__ = (
        UniqueConstraint('fan_club_id', 'name'),
        UniqueConstraint('fan_club_id', 'tier_level'),
        Index('idx_tier_fanclub', 'fan_club_id'),
        CheckConstraint('price_monthly >= 2.99'),
        CheckConstraint('tier_level BETWEEN 1 AND 3'),
    )
```

### 3. Subscription Model

**Purpose:** Tracks individual fan subscriptions

```python
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True)
    fan_club_id = Column(String(36), ForeignKey("fan_clubs.id"))
    tier_id = Column(String(36), ForeignKey("membership_tiers.id"))
    subscriber_id = Column(String(36), ForeignKey("users.id"))
    
    # Subscription details
    status = Column(String(20))  # active, cancelled, paused, past_due
    billing_cycle = Column(String(10))  # monthly, yearly
    price_paid = Column(Numeric(10, 2))  # Amount paid
    currency = Column(String(3), default="USD")
    
    # Dates
    started_at = Column(DateTime, server_default=func.now())
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancelled_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    paused_until = Column(DateTime, nullable=True)
    
    # Payment integration
    payment_provider = Column(String(20))  # stripe, paystack
    payment_provider_subscription_id = Column(String(100))
    payment_provider_customer_id = Column(String(100))
    
    # Metadata
    auto_renew = Column(Boolean, default=True)
    trial_ends_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    fan_club = relationship("FanClub", back_populates="subscriptions")
    tier = relationship("MembershipTier", back_populates="subscriptions")
    subscriber = relationship("User")
    payments = relationship("SubscriptionPayment", back_populates="subscription")
    
    __table_args__ = (
        UniqueConstraint('fan_club_id', 'subscriber_id'),
        Index('idx_subscription_fanclub', 'fan_club_id'),
        Index('idx_subscription_subscriber', 'subscriber_id'),
        Index('idx_subscription_status', 'status'),
        Index('idx_subscription_period_end', 'current_period_end'),
    )
```

### 4. SubscriptionPayment Model

**Purpose:** Tracks all subscription payment transactions

```python
class SubscriptionPayment(Base):
    __tablename__ = "subscription_payments"
    
    id = Column(String(36), primary_key=True)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id"))
    amount = Column(Numeric(10, 2))
    currency = Column(String(3))
    status = Column(String(20))  # succeeded, failed, pending, refunded
    payment_method = Column(String(50))  # card, wallet, bank
    
    # Payment provider details
    payment_provider = Column(String(20))
    payment_provider_payment_id = Column(String(100))
    payment_provider_charge_id = Column(String(100))
    
    # Failure tracking
    failure_code = Column(String(50), nullable=True)
    failure_message = Column(Text, nullable=True)
    retry_attempt = Column(Integer, default=0)
    
    # Revenue split
    platform_fee = Column(Numeric(10, 2))  # 10%
    creator_payout = Column(Numeric(10, 2))  # 90%
    
    paid_at = Column(DateTime)
    refunded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="payments")
    
    __table_args__ = (
        Index('idx_payment_subscription', 'subscription_id'),
        Index('idx_payment_status', 'status'),
        Index('idx_payment_date', 'paid_at'),
    )
```

### 5. ExclusiveContent Model

**Purpose:** Marks content as tier-gated exclusive

```python
class ExclusiveContent(Base):
    __tablename__ = "exclusive_content"
    
    id = Column(String(36), primary_key=True)
    content_type = Column(String(20))  # post, track, video, image, event
    content_id = Column(String(36))  # FK to posts/tracks/etc
    fan_club_id = Column(String(36), ForeignKey("fan_clubs.id"))
    minimum_tier_level = Column(Integer)  # 1, 2, or 3
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('content_type', 'content_id'),
        Index('idx_exclusive_fanclub', 'fan_club_id'),
    )
```

---

## API Endpoints Design

### Fan Club Management

```
POST   /api/v1/fan-clubs                    # Create fan club
GET    /api/v1/fan-clubs/me                 # Get my fan club
PUT    /api/v1/fan-clubs/me                 # Update fan club
GET    /api/v1/fan-clubs/{creator_id}       # Get creator's fan club
DELETE /api/v1/fan-clubs/me                 # Deactivate fan club
```

### Membership Tiers

```
POST   /api/v1/fan-clubs/me/tiers           # Create tier
GET    /api/v1/fan-clubs/{id}/tiers         # List tiers
PUT    /api/v1/fan-clubs/me/tiers/{id}      # Update tier
DELETE /api/v1/fan-clubs/me/tiers/{id}      # Delete tier
```

### Subscriptions

```
POST   /api/v1/subscriptions                # Subscribe to tier
GET    /api/v1/subscriptions/me             # My subscriptions
GET    /api/v1/subscriptions/{id}           # Get subscription
PUT    /api/v1/subscriptions/{id}           # Upgrade/downgrade
DELETE /api/v1/subscriptions/{id}           # Cancel subscription
POST   /api/v1/subscriptions/{id}/pause     # Pause subscription
POST   /api/v1/subscriptions/{id}/resume    # Resume subscription
```

### Subscriber Management (Creator)

```
GET    /api/v1/fan-clubs/me/subscribers     # List my subscribers
GET    /api/v1/fan-clubs/me/analytics       # Subscription analytics
POST   /api/v1/fan-clubs/me/broadcast       # Send announcement
```

### Exclusive Content

```
POST   /api/v1/exclusive-content             # Mark content exclusive
GET    /api/v1/exclusive-content/{id}/access # Check access
DELETE /api/v1/exclusive-content/{id}        # Remove exclusivity
```

---

## Database Schema Diagram

```
┌──────────────┐        ┌────────────────────┐
│   users      │◄───────┤    fan_clubs       │
│              │        │                    │
└──────────────┘        └────────────────────┘
                                │
                                │ 1:N
                                ▼
                        ┌────────────────────┐
                        │ membership_tiers   │
                        └────────────────────┘
                                │
                                │ 1:N
                                ▼
            ┌───────────────────────────────┐
            │      subscriptions            │
            └───────────────────────────────┘
                        │
                        │ 1:N
                        ▼
            ┌───────────────────────────────┐
            │  subscription_payments        │
            └───────────────────────────────┘
```

---

## Service Layer Architecture

### FanClubService
- `create_fan_club(creator_id, data)` - Create new fan club
- `get_fan_club(fan_club_id)` - Retrieve fan club details
- `update_fan_club(fan_club_id, data)` - Update configuration
- `deactivate_fan_club(fan_club_id)` - Soft delete

### TierService
- `create_tier(fan_club_id, tier_data)` - Create membership tier
- `update_tier(tier_id, data)` - Update tier details
- `delete_tier(tier_id)` - Remove tier (if no subscribers)
- `list_tiers(fan_club_id)` - Get all tiers

### SubscriptionService
- `create_subscription(subscriber_id, tier_id)` - Subscribe
- `cancel_subscription(subscription_id)` - Cancel
- `pause_subscription(subscription_id)` - Pause
- `resume_subscription(subscription_id)` - Resume
- `upgrade_tier(subscription_id, new_tier_id)` - Upgrade
- `process_renewal(subscription_id)` - Handle renewal

### PaymentService
- `process_payment(subscription_id, amount)` - Process charge
- `handle_failed_payment(payment_id)` - Retry logic
- `process_refund(payment_id)` - Issue refund
- `calculate_platform_fee(amount)` - 10% fee

### ContentAccessService
- `check_access(user_id, content_id)` - Verify tier access
- `mark_exclusive(content_id, tier_level)` - Gate content
- `get_exclusive_content(fan_club_id)` - List exclusive content

---

## Payment Flow Design

### Subscription Creation Flow

```
1. Fan clicks "Subscribe" on tier
2. Frontend collects payment method (Stripe/Paystack)
3. Backend creates subscription record (status: pending)
4. Backend charges payment method via API
5. If successful:
   - Update subscription status → active
   - Create payment record
   - Send welcome email
   - Grant content access
6. If failed:
   - Update subscription status → failed
   - Notify user
   - Schedule retry
```

### Auto-Renewal Flow

```
1. Cron job runs daily checking subscriptions ending in 3 days
2. For each subscription:
   - Attempt payment charge
   - If successful: extend period, create payment record
   - If failed: retry 3 times over 7 days
   - After 3 failures: cancel subscription, notify user
```

---

## Integration Points

### Stripe Integration
```python
# Create customer
stripe.Customer.create(email=user.email)

# Create subscription
stripe.Subscription.create(
    customer=customer_id,
    items=[{'price': price_id}],
    payment_behavior='default_incomplete'
)

# Handle webhooks
@app.post("/webhooks/stripe")
async def stripe_webhook(request):
    # Handle: invoice.paid, invoice.payment_failed, customer.subscription.updated
```

### Paystack Integration
```python
# Initialize transaction
paystack.Transaction.initialize(
    email=user.email,
    amount=amount * 100,  # In kobo
    plan=plan_code
)

# Verify transaction
paystack.Transaction.verify(reference=ref)
```

---

## Background Jobs

### Daily Jobs
- Check subscriptions expiring in 3 days → send reminder
- Process auto-renewals for subscriptions ending today
- Retry failed payments (attempt 1, 2, 3)
- Calculate daily MRR metrics

### Weekly Jobs
- Send weekly exclusive content digest
- Generate analytics reports for creators
- Clean up expired trial subscriptions

### Monthly Jobs
- Process creator payouts (minimum $50)
- Send monthly thank you messages
- Generate cohort retention reports

---

## Testing Strategy

### Unit Tests
- Model validation (price constraints, tier levels)
- Service layer logic (subscription lifecycle)
- Payment calculations (fees, prorations)
- Access control logic

### Integration Tests
- API endpoints (CRUD operations)
- Payment webhooks (Stripe/Paystack)
- Email sending (welcome, renewal reminders)
- Background job execution

### End-to-End Tests
- Complete subscription flow
- Payment failure and retry
- Tier upgrade/downgrade
- Cancellation and refund

---

## Security Considerations

1. **Payment Security**
   - Never store raw card data
   - Use Stripe/Paystack tokens
   - Validate webhook signatures

2. **Access Control**
   - Verify subscriber status before content access
   - Check tier level for exclusive content
   - Prevent subscription manipulation

3. **Rate Limiting**
   - Limit subscription creation (prevent abuse)
   - Throttle payment attempts
   - Limit webhook processing

4. **Data Privacy**
   - Encrypt payment method tokens
   - Anonymize analytics data
   - GDPR-compliant data deletion

---

## Performance Optimization

1. **Caching**
   - Cache fan club data (30 min TTL)
   - Cache subscriber counts
   - Cache tier lists

2. **Database Indexing**
   - Index subscription lookups
   - Index payment queries
   - Index content access checks

3. **Background Processing**
   - Async email sending
   - Batch payment processing
   - Deferred analytics calculation

---

## Monitoring & Alerts

### Key Metrics
- Active subscriptions count
- MRR (Monthly Recurring Revenue)
- Churn rate
- Payment success rate
- Average subscription lifetime

### Alerts
- Payment failure rate > 10%
- Churn rate spike > 15%
- Webhook processing delays
- Creator payout failures

---

**Design Status:** Complete  
**Ready for:** Task Breakdown & Implementation
