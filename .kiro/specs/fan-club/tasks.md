# Fan Club System - Implementation Tasks

**Feature:** Fan Club & Membership System  
**Total Estimated Effort:** 3-4 days  
**Priority:** High (Task 7.5 in Roadmap)

---

## Wave 1: Database Schema & Models (Day 1 Morning)

### 1. Database Schema Setup
**Dependencies:** None  
**Estimated Time:** 2 hours

- [x] 1.1 Create `fan_clubs` table with all fields
- [x] 1.2 Create `membership_tiers` table with pricing constraints
- [x] 1.3 Create `subscriptions` table with status tracking
- [x] 1.4 Create `subscription_payments` table for transactions
- [x] 1.5 Create `exclusive_content` table for content gating
- [x] 1.6 Add all foreign key relationships
- [x] 1.7 Add database indexes for performance
- [x] 1.8 Add check constraints for business rules

### 2. SQLAlchemy Models
**Dependencies:** 1  
**Estimated Time:** 2 hours

- [x] 2.1 Create `FanClub` model with relationships
- [x] 2.2 Create `MembershipTier` model with JSON benefits field
- [x] 2.3 Create `Subscription` model with lifecycle fields
- [x] 2.4 Create `SubscriptionPayment` model
- [x] 2.5 Create `ExclusiveContent` model
- [x] 2.6 Add enums for statuses (SubscriptionStatus, PaymentStatus)
- [x] 2.7 Import models in `app/models/__init__.py`
- [x] 2.8 Update database initialization to include fan club tables

---

## Wave 2: Pydantic Schemas (Day 1 Afternoon)

### 3. Request/Response Schemas
**Dependencies:** 2  
**Estimated Time:** 2 hours

- [x] 3.1 Create `FanClubCreate`, `FanClubUpdate`, `FanClubResponse` schemas
- [x] 3.2 Create `TierCreate`, `TierUpdate`, `TierResponse` schemas
- [x] 3.3 Create `SubscriptionCreate`, `SubscriptionResponse` schemas
- [x] 3.4 Create `PaymentResponse`, `PaymentMethodRequest` schemas
- [x] 3.5 Create `ExclusiveContentRequest`, `ExclusiveContentResponse`
- [x] 3.6 Create `SubscriberListResponse` with pagination
- [x] 3.7 Create `AnalyticsResponse` with MRR metrics
- [x] 3.8 Add validation rules (price min/max, tier levels)

---

## Wave 3: Core Services - Fan Club & Tiers (Day 1 Evening + Day 2 Morning)

### 4. FanClubService
**Dependencies:** 3  
**Estimated Time:** 3 hours

- [x] 4.1 Implement `create_fan_club()` - validate creator eligibility
- [x] 4.2 Implement `get_fan_club()` - retrieve with tiers
- [x] 4.3 Implement `update_fan_club()` - edit name, description, welcome message
- [x] 4.4 Implement `deactivate_fan_club()` - soft delete with validation
- [x] 4.5 Implement `get_fan_club_stats()` - total members, MRR
- [x] 4.6 Add access control checks (creator ownership)

### 5. TierService
**Dependencies:** 4  
**Estimated Time:** 2 hours

- [x] 5.1 Implement `create_tier()` - validate pricing, tier level uniqueness
- [x] 5.2 Implement `update_tier()` - allow edits with subscriber notice
- [x] 5.3 Implement `delete_tier()` - check no active subscribers
- [x] 5.4 Implement `list_tiers()` - get all tiers for fan club
- [x] 5.5 Implement `pause_tier()` - prevent new subscriptions
- [x] 5.6 Calculate yearly price (10% discount from monthly)

---

## Wave 4: Subscription Service (Day 2 Afternoon)

### 6. SubscriptionService Core
**Dependencies:** 5  
**Estimated Time:** 4 hours
**Status:** ✅ COMPLETE

- [x] 6.1 Implement `create_subscription()` - initiate subscription flow
- [x] 6.2 Implement `get_subscription()` - retrieve with tier details
- [x] 6.3 Implement `list_user_subscriptions()` - user's active subscriptions
- [x] 6.4 Implement `cancel_subscription()` - cancel with end-of-period access
- [x] 6.5 Implement `pause_subscription()` - pause up to 3 months
- [x] 6.6 Implement `resume_subscription()` - resume paused subscription
- [x] 6.7 Implement `upgrade_tier()` - immediate upgrade with proration
- [x] 6.8 Implement `downgrade_tier()` - schedule for next cycle
- [x] 6.9 Implement `check_subscription_status()` - is user subscribed?
- [x] 6.10 Add validation for subscription state transitions

---

## Wave 5: Payment Integration (Day 2 Evening)

### 7. PaymentService - Stripe Integration
**Dependencies:** 6  
**Estimated Time:** 3 hours
**Status:** ✅ COMPLETE

- [x] 7.1 Install Stripe Python SDK (`pip install stripe`)
- [x] 7.2 Create `StripePaymentProvider` class
- [x] 7.3 Implement `create_customer()` - Stripe customer creation
- [x] 7.4 Implement `create_payment_method()` - save payment method
- [x] 7.5 Implement `charge_subscription()` - process subscription payment
- [x] 7.6 Implement `handle_failed_payment()` - retry logic (3 attempts)
- [x] 7.7 Implement `process_refund()` - issue refund
- [x] 7.8 Calculate platform fee (10%) and creator payout (90%)

### 8. PaymentService - Paystack Integration
**Dependencies:** 7  
**Estimated Time:** 2 hours
**Status:** ✅ COMPLETE

- [x] 8.1 Install Paystack Python SDK (`pip install paystackapi`)
- [x] 8.2 Create `PaystackPaymentProvider` class
- [x] 8.3 Implement `initialize_transaction()` - Paystack charge
- [x] 8.4 Implement `verify_transaction()` - verify payment status
- [x] 8.5 Implement subscription creation via Paystack plans
- [x] 8.6 Add fallback logic (try Stripe, then Paystack)

---

## Wave 6: Content Access Control (Day 3 Morning)

### 9. ContentAccessService
**Dependencies:** 6  
**Estimated Time:** 2 hours
**Status:** ✅ COMPLETE

- [x] 9.1 Implement `mark_content_exclusive()` - gate content by tier
- [x] 9.2 Implement `check_content_access()` - verify user can access
- [x] 9.3 Implement `get_exclusive_content()` - list creator's exclusive content
- [x] 9.4 Implement `remove_exclusivity()` - make content public
- [x] 9.5 Integrate with `Post` model - add access check
- [x] 9.6 Integrate with `Track` model - add access check
- [x] 9.7 Add "Unlock with [Tier]" teaser logic (show first 20%)

---

## Wave 7: API Endpoints - Fan Club Management (Day 3 Afternoon)

### 10. Fan Club Endpoints
**Dependencies:** 4, 9  
**Estimated Time:** 2 hours
**Status:** ✅ COMPLETE

- [x] 10.1 POST `/api/v1/fan-clubs` - Create fan club (creator only)
- [x] 10.2 GET `/api/v1/fan-clubs/me` - Get my fan club (creator)
- [x] 10.3 PUT `/api/v1/fan-clubs/me` - Update fan club
- [x] 10.4 GET `/api/v1/fan-clubs/{creator_id}` - View creator's fan club (public)
- [x] 10.5 DELETE `/api/v1/fan-clubs/me` - Deactivate fan club

### 11. Tier Management Endpoints
**Dependencies:** 5  
**Estimated Time:** 1.5 hours

- [ ] 11.1 POST `/api/v1/fan-clubs/me/tiers` - Create tier
- [ ] 11.2 GET `/api/v1/fan-clubs/{id}/tiers` - List tiers
- [ ] 11.3 PUT `/api/v1/fan-clubs/me/tiers/{id}` - Update tier
- [ ] 11.4 DELETE `/api/v1/fan-clubs/me/tiers/{id}` - Delete tier

---

## Wave 8: API Endpoints - Subscriptions (Day 3 Evening)

### 12. Subscription Endpoints
**Dependencies:** 6, 7  
**Estimated Time:** 3 hours

- [ ] 12.1 POST `/api/v1/subscriptions` - Subscribe to tier (payment required)
- [ ] 12.2 GET `/api/v1/subscriptions/me` - My active subscriptions
- [ ] 12.3 GET `/api/v1/subscriptions/{id}` - Get subscription details
- [ ] 12.4 PUT `/api/v1/subscriptions/{id}` - Upgrade/downgrade tier
- [ ] 12.5 DELETE `/api/v1/subscriptions/{id}` - Cancel subscription
- [ ] 12.6 POST `/api/v1/subscriptions/{id}/pause` - Pause subscription
- [ ] 12.7 POST `/api/v1/subscriptions/{id}/resume` - Resume subscription

### 13. Subscriber Management Endpoints (Creator)
**Dependencies:** 6  
**Estimated Time:** 2 hours

- [ ] 13.1 GET `/api/v1/fan-clubs/me/subscribers` - List my subscribers
- [ ] 13.2 GET `/api/v1/fan-clubs/me/subscribers/{id}` - Get subscriber details
- [ ] 13.3 GET `/api/v1/fan-clubs/me/analytics` - Subscription analytics
- [ ] 13.4 POST `/api/v1/fan-clubs/me/broadcast` - Send announcement to members

---

## Wave 9: Exclusive Content API (Day 4 Morning)

### 14. Exclusive Content Endpoints
**Dependencies:** 9  
**Estimated Time:** 1.5 hours

- [ ] 14.1 POST `/api/v1/exclusive-content` - Mark content exclusive
- [ ] 14.2 GET `/api/v1/exclusive-content/{content_type}/{content_id}/access` - Check access
- [ ] 14.3 DELETE `/api/v1/exclusive-content/{id}` - Remove exclusivity
- [ ] 14.4 GET `/api/v1/fan-clubs/{id}/exclusive-content` - List exclusive content

---

## Wave 10: Payment Webhooks (Day 4 Morning)

### 15. Webhook Handlers
**Dependencies:** 7, 8  
**Estimated Time:** 2 hours

- [ ] 15.1 POST `/webhooks/stripe` - Handle Stripe events
- [ ] 15.2 Validate Stripe webhook signatures
- [ ] 15.3 Handle `invoice.paid` event - mark payment successful
- [ ] 15.4 Handle `invoice.payment_failed` event - schedule retry
- [ ] 15.5 Handle `customer.subscription.updated` event - sync status
- [ ] 15.6 Handle `customer.subscription.deleted` event - cancel subscription
- [ ] 15.7 POST `/webhooks/paystack` - Handle Paystack events
- [ ] 15.8 Validate Paystack webhook signatures

---

## Wave 11: Background Jobs & Automation (Day 4 Afternoon)

### 16. Subscription Background Jobs
**Dependencies:** 6, 7  
**Estimated Time:** 2 hours

- [ ] 16.1 Create `process_subscription_renewals()` job - run daily
- [ ] 16.2 Create `retry_failed_payments()` job - retry 3 times over 7 days
- [ ] 16.3 Create `send_renewal_reminders()` job - 3 days before renewal
- [ ] 16.4 Create `cancel_expired_trials()` job - clean up trials
- [ ] 16.5 Configure APScheduler for cron jobs
- [ ] 16.6 Add error handling and logging

### 17. Welcome & Engagement Automation
**Dependencies:** 6  
**Estimated Time:** 2 hours

- [ ] 17.1 Send welcome email on new subscription
- [ ] 17.2 Send welcome DM from creator (customizable template)
- [ ] 17.3 Send monthly thank you message (3+ months subscribers)
- [ ] 17.4 Send subscription anniversary message
- [ ] 17.5 Create notification for exclusive content (push + email)
- [ ] 17.6 Weekly digest email of exclusive content (opt-in)

---

## Wave 12: Analytics & Reporting (Day 4 Evening)

### 18. Analytics Service
**Dependencies:** 6  
**Estimated Time:** 2 hours

- [ ] 18.1 Calculate MRR (Monthly Recurring Revenue)
- [ ] 18.2 Calculate churn rate (monthly)
- [ ] 18.3 Calculate subscriber retention cohorts
- [ ] 18.4 Calculate average subscription lifetime value (LTV)
- [ ] 18.5 Track conversion rate (profile visits → subscriptions)
- [ ] 18.6 Generate revenue forecast (next 3 months)
- [ ] 18.7 Track engagement metrics (exclusive content views)

---

## Wave 13: Testing & Quality Assurance (Throughout)

### 19. Unit Tests
**Dependencies:** All services  
**Estimated Time:** 3 hours

- [ ] 19.1 Test fan club CRUD operations
- [ ] 19.2 Test tier management with validation
- [ ] 19.3 Test subscription lifecycle (create, upgrade, cancel)
- [ ] 19.4 Test payment processing and retry logic
- [ ] 19.5 Test content access control
- [ ] 19.6 Test proration calculations
- [ ] 19.7 Test platform fee calculations

### 20. Integration Tests
**Dependencies:** All endpoints  
**Estimated Time:** 2 hours

- [ ] 20.1 Test complete subscription flow (E2E)
- [ ] 20.2 Test payment webhook processing
- [ ] 20.3 Test tier upgrade/downgrade
- [ ] 20.4 Test subscription cancellation and refund
- [ ] 20.5 Test exclusive content access
- [ ] 20.6 Test background job execution

---

## Wave 14: Documentation & Polish (Final)

### 21. Documentation
**Dependencies:** All features  
**Estimated Time:** 1 hour

- [ ] 21.1 Update API documentation (OpenAPI/Swagger)
- [ ] 21.2 Create creator guide (how to set up fan club)
- [ ] 21.3 Create fan guide (how to subscribe)
- [ ] 21.4 Document webhook setup instructions
- [ ] 21.5 Add code comments and docstrings

### 22. Final Integration
**Dependencies:** All  
**Estimated Time:** 1 hour

- [ ] 22.1 Register fan club router in main API
- [ ] 22.2 Add fan club to user profile response
- [ ] 22.3 Add subscriber badge to user display
- [ ] 22.4 Update navigation/UI to show fan club link
- [ ] 22.5 Verify all database migrations applied

---

## Summary

**Total Tasks:** 22 major tasks, ~130 subtasks  
**Estimated Timeline:** 3-4 days  
**Total Estimated Hours:** 32-40 hours

**Day 1:** Database + Models + Schemas (Waves 1-2)  
**Day 2:** Services + Payment Integration (Waves 3-5)  
**Day 3:** Content Access + API Endpoints (Waves 6-9)  
**Day 4:** Webhooks + Jobs + Analytics + Testing (Waves 10-14)

**Dependencies Chart:**
- Wave 1 → Wave 2 → Wave 3
- Wave 3 → Wave 4 → Wave 5
- Wave 4 → Wave 6
- Waves 4,5,6 → Waves 7,8,9
- Waves 5,6 → Wave 10
- Wave 6 → Wave 11
- Wave 6 → Wave 12
- All → Waves 13,14
