# Phase 4 Implementation Plan: Shared Components & Remaining Pages

**Current Status**: Phase 3 Complete (3 dashboards + marketplace)  
**Next Phase**: Phase 4 - Shared Components & Remaining Dashboard Pages  
**Date**: September 1, 2026  
**Goal**: Implement critical shared components and remaining dashboard pages with full Stitch design compliance

---

## Executive Summary

Phase 3 successfully completed the remaining Stitch-designed dashboards (Producer, Fan) and marketplace. Phase 4 will focus on:

1. **Critical Shared Components** - Reusable elements used across multiple pages
2. **E-Commerce Flow** - Cart and checkout pages for beat licensing
3. **Remaining Dashboard Pages** - Bookings, fan clubs, campaigns, trending, search
4. **Standardization** - Apply consistent patterns across all new implementations

All work will follow established patterns from Phase 2/3, maintain 100% Stitch design compliance, and build incrementally with verification at each step.

---

## Current Implementation Status (End of Phase 3)

### Fully Complete ✅
- **Dashboards**: Artist, DJ, Producer, Fan (all with Stitch design)
- **Marketplace**: Beat marketplace with filters and grid
- **Pages**: Profile, Settings, Analytics, Messaging, Social Feed
- **Layout**: AppShell, Sidebar, TopNav (Phase 2)
- **Foundation**: Tailwind config with 32 Stitch colors, globals.css utilities

### Partial Implementation ⚠️
- **Beats Page**: Header only, no beat listing
- **Discover Page**: Basic structure, needs filters and grid
- **BeatCard/BeatGrid**: Exist but not integrated into pages
- **BeatFilters**: Exist but not connected

### Not Started ❌
- Cart, Checkout, Bookings, Campaigns, DJ Submissions, Fan Clubs, Promo Links, Purchases, Tips, Tracks, Trending, Admin, Notifications, Search

---

## Phase 4 Task Breakdown

### Section 1: Critical Shared Components (Tasks 1-5)

These components are prerequisites for multiple pages and must be completed first.

#### Task 1: Implement PaginationComponent
**Priority**: 🔴 CRITICAL  
**Estimated Time**: 2 hours  
**Files to Create**:
- `frontend/src/components/ui/pagination.tsx` (NEW)
- `frontend/src/hooks/usePagination.ts` (NEW)

**Requirements**:
- Display previous/next buttons with disabled state
- Show page numbers: first, last, and 2 pages on each side of current
- Support custom page size options (10, 20, 50)
- Mobile-optimized: hide page numbers, show only prev/next
- Stitch styling: button variants from component library
- Accept `totalItems`, `currentPage`, `pageSize` props
- Emit `onPageChange` callback

**Why Critical**: Used in Analytics, Bookings, DJ Submissions, Purchases, Trending

**Test Cases**:
- Single page (no pagination shown)
- Multiple pages (all buttons enabled)
- First page (previous disabled)
- Last page (next disabled)
- Mobile view hides individual page numbers

---

#### Task 2: Implement DateRangePicker Component
**Priority**: 🟡 HIGH  
**Estimated Time**: 4 hours  
**Files to Create**:
- `frontend/src/components/ui/date-range-picker.tsx` (NEW)
- `frontend/src/components/features/calendar/Calendar.tsx` (NEW - optional reusable)

**Requirements**:
- Two calendar pickers (start date, end date)
- Keyboard navigation support (arrow keys, enter)
- Preset ranges: Last 7 days, Last 30 days, Last 90 days, Custom
- Display selected range as readable text
- Mobile: single calendar with swipe/tap
- Stitch styling: consistent with Input, Button components
- Support time selection (hours, minutes) optional
- Clear and Apply buttons

**Why High Priority**: Used in Analytics filters, Booking calendars, Campaign scheduling

**Test Cases**:
- Select preset range
- Custom date range selection
- Date validation (start before end)
- Mobile layout
- Keyboard navigation

---

#### Task 3: Implement SearchAutocomplete Component
**Priority**: 🟡 HIGH  
**Estimated Time**: 3 hours  
**Files to Create**:
- `frontend/src/components/ui/search-autocomplete.tsx` (NEW)
- `frontend/src/hooks/useSearchAutocomplete.ts` (NEW)

**Requirements**:
- Input field with debounced search (300ms)
- Dropdown showing suggestions while typing
- Categories: Beats, Artists, Playlists, Sounds (6-8 results per category)
- Highlight matching text in suggestions
- Arrow key navigation through suggestions
- Enter key to select or search
- Recent searches storage (last 5)
- Mobile-friendly: full-width dropdown
- Stitch styling: consistent Input + dropdown

**Why High Priority**: Core UX improvement for beat discovery and messaging

**Test Cases**:
- Debouncing works correctly
- Suggestions display and filter correctly
- Arrow key navigation
- Selection handling
- Recent searches persistence

---

#### Task 4: Implement NotificationCenter Component
**Priority**: 🟡 HIGH  
**Estimated Time**: 3 hours  
**Files to Create**:
- `frontend/src/components/features/notifications/NotificationCenter.tsx` (NEW)
- `frontend/src/components/features/notifications/NotificationItem.tsx` (NEW)
- `frontend/src/hooks/useNotifications.ts` (NEW - if not exists)

**Requirements**:
- Modal or sidebar drawer showing 10 most recent notifications
- Notification types: message, follow, purchase, like, tip, system
- Read/unread state with visual indicator (dot, background color)
- Mark as read / Mark all as read buttons
- Delete individual notifications
- Real-time updates via WebSocket
- Grouped by type with collapsible sections
- Show timestamp (relative time: "2 minutes ago")
- Stitch styling: consistent with existing components

**Why High Priority**: Completes messaging and engagement system

**Test Cases**:
- Display various notification types
- Mark as read/unread
- Real-time WebSocket updates
- Delete functionality
- Grouping logic

---

#### Task 5: Implement PaymentForm Component
**Priority**: 🔴 CRITICAL  
**Estimated Time**: 4 hours  
**Files to Create**:
- `frontend/src/components/features/payment/PaymentForm.tsx` (NEW)
- `frontend/src/services/paymentService.ts` (UPDATE if exists)
- `frontend/src/hooks/usePayment.ts` (NEW)

**Requirements**:
- Integrate with Paystack payment service
- Display beat/product details and pricing
- Email field (pre-filled if user logged in)
- Payment summary section
- "Pay with Paystack" button
- Handle payment responses (success/failed)
- Display error messages
- Loading state during payment processing
- Stitch styling: consistent with form components
- Support multiple currencies (NGN, USD)

**Why Critical**: Essential for e-commerce (Cart, Checkout, Tips, Bookings)

**Test Cases**:
- Form displays correctly
- Form validation
- Paystack integration works
- Error handling
- Currency conversion
- Success/failure responses

---

### Section 2: E-Commerce Pages (Tasks 6-7)

These are high-impact pages that enable monetization.

#### Task 6: Implement Cart Page
**Priority**: 🔴 CRITICAL  
**Estimated Time**: 3 hours  
**Files to Create**:
- `frontend/src/app/(dashboard)/cart/page.tsx` (NEW)
- `frontend/src/components/features/cart/CartItem.tsx` (NEW)
- `frontend/src/hooks/useCart.ts` (NEW or UPDATE)

**Requirements**:
- Display list of beats/items in cart (using CartItem component)
- Each item: thumbnail, title, artist, price, quantity, remove button
- Cart summary: subtotal, tax, total, savings if applicable
- Apply coupon code field
- "Proceed to Checkout" button (disabled if cart empty)
- Empty cart state with CTA to browse beats
- Update cart count in navigation
- Responsive: single column mobile, proper spacing tablet/desktop
- Stitch styling: consistent card layout and colors

**Why Critical**: Core e-commerce feature

**Test Cases**:
- Display cart items
- Remove item from cart
- Apply coupon (or show placeholder)
- Empty cart state
- Proceed to checkout routing
- Cart persistence (localStorage or API)

---

#### Task 7: Implement Checkout Page
**Priority**: 🔴 CRITICAL  
**Estimated Time**: 4 hours  
**Files to Create**:
- `frontend/src/app/(dashboard)/checkout/page.tsx` (NEW)
- `frontend/src/components/features/checkout/CheckoutSummary.tsx` (NEW)

**Requirements**:
- Two-column layout: form (left), order summary (right); single column mobile
- Order summary with items and pricing
- PaymentForm component integration
- Billing address fields (pre-populate from profile)
- Order confirmation on successful payment
- Success modal with order number, receipt link
- Error handling with retry option
- Loading states
- Stitch styling: consistent with other pages

**Why Critical**: Completes purchase flow

**Test Cases**:
- Form displays correctly
- Payment form integration
- Successful payment flow
- Error handling
- Order confirmation display
- Mobile layout

---

### Section 3: Discovery & Content Pages (Tasks 8-10)

These pages help users discover and browse content.

#### Task 8: Complete Beats (My Beats) Page
**Priority**: 🟡 HIGH  
**Estimated Time**: 3 hours  
**Files to Update**:
- `frontend/src/app/(dashboard)/beats/page.tsx` (UPDATE - currently header only)

**Requirements**:
- Header with "My Beats" title and upload button
- Tabs: All, Published, Drafts, Archived
- BeatGrid component showing user's beats
- Sorting: Most Recent, Most Popular, Most Played, Highest Earning
- Search field to filter beats
- Bulk actions: select, delete, archive
- Empty state with upload CTA
- Edit/delete menu on each beat
- Pagination or infinite scroll
- Stitch styling: consistent with other pages

**Why High Priority**: Essential for producers to manage content

**Test Cases**:
- Display beats grid
- Tab filtering
- Sorting changes grid order
- Search filtering
- Bulk selection
- Empty state

---

#### Task 9: Implement Discover Page
**Priority**: 🟡 HIGH  
**Estimated Time**: 4 hours  
**Files to Create**:
- `frontend/src/app/(dashboard)/discover/page.tsx` (UPDATE - currently basic)
- `frontend/src/components/features/discover/DiscoverCategories.tsx` (NEW)

**Requirements**:
- Hero section: featured beat/artist
- Category cards: Trending, New Releases, Top Artists, Playlists
- BeatGrid with advanced filters (BeatFilters integration)
- Genre carousel at top
- Infinite scroll with pagination
- Filter sidebar (genre, tempo, key, mood, price)
- Sort dropdown
- Responsive: mobile sidebar becomes bottom drawer
- Stitch styling: consistent with other pages

**Why High Priority**: Core discovery feature for all users

**Test Cases**:
- Categories display
- Filter functionality
- Search integration
- Infinite scroll
- Mobile layout
- Genre selection

---

#### Task 10: Implement Trending Page
**Priority**: 🟠 MEDIUM  
**Estimated Time**: 2 hours  
**Files to Create**:
- `frontend/src/app/(dashboard)/trending/page.tsx` (NEW)

**Requirements**:
- Hero: current #1 trending beat
- Trending chart: top 50 beats this week/month
- Tabs: Daily Trending, Weekly Trending, Monthly Trending, All-Time
- Each beat shown with: rank badge, cover, title, artist, plays, engagement
- Genre filter dropdown
- Share button on each beat
- ListLayout or TableLayout options
- Responsive: card view mobile, table view desktop
- Stitch styling: consistent with analytics charts

**Why Medium Priority**: Good for user engagement and discovery

**Test Cases**:
- Display trending list
- Tab filtering
- Genre filter
- Layout toggle
- Share functionality

---

### Section 4: Community & Management Pages (Tasks 11-13)

#### Task 11: Implement Bookings Page
**Priority**: 🟠 MEDIUM  
**Estimated Time**: 3 hours  
**Files to Create**:
- `frontend/src/app/(dashboard)/bookings/page.tsx` (NEW)
- `frontend/src/components/features/bookings/BookingCard.tsx` (NEW)

**Requirements**:
- Calendar view (month/week/day)
- Booking list with status (pending, confirmed, completed, cancelled)
- Each booking: date, time, service, client, price, status badge
- Filter by status, date range (DateRangePicker)
- Pagination
- Booking details modal
- Accept/decline booking buttons
- Message client button (links to messaging)
- Responsive: mobile shows list only, desktop shows calendar
- Stitch styling: calendar colors, status badge colors

**Why Medium Priority**: Important for artists providing services

**Test Cases**:
- Calendar displays bookings
- List filtering by status
- Date range filtering
- Booking details modal
- Accept/decline actions
- Mobile layout

---

#### Task 12: Implement Fan Clubs Page
**Priority**: 🟠 MEDIUM  
**Estimated Time**: 3 hours  
**Files to Create**:
- `frontend/src/app/(dashboard)/fan-clubs/page.tsx` (NEW)
- `frontend/src/components/features/fan-clubs/FanClubCard.tsx` (NEW)

**Requirements**:
- Grid of fan clubs (for members viewing)
- Each card: club cover, name, creator, member count, tier options, join button
- Tabs: All, Joined, Featured
- Search and filter by category
- Join modal showing tier options and benefits
- For creators: manage fan club tab
- Member list view
- Content management section
- Subscription settings
- Responsive grid layout
- Stitch styling: consistent with other pages

**Why Medium Priority**: Important community building feature

**Test Cases**:
- Display fan clubs grid
- Join fan club flow
- Filter and search
- Creator management view
- Responsive layout

---

#### Task 13: Implement Campaigns Page
**Priority**: 🟠 MEDIUM  
**Estimated Time**: 4 hours  
**Files to Create**:
- `frontend/src/app/(dashboard)/campaigns/page.tsx` (NEW)
- `frontend/src/components/features/campaigns/CampaignCard.tsx` (NEW)
- `frontend/src/components/features/campaigns/CampaignBuilder.tsx` (NEW - optional)

**Requirements**:
- List all campaigns (for AI promotion platform)
- Each campaign: name, status, start date, end date, budget, reach, engagement
- Create campaign button → modal/drawer
- Campaign details view
- Edit campaign
- Pause/resume campaign
- Delete campaign with confirmation
- Analytics for each campaign (clicks, conversions, ROI)
- Filter by status, date range
- Pagination
- Responsive layout
- Stitch styling: consistent with analytics

**Why Medium Priority**: Important for marketing and promotion

**Test Cases**:
- Display campaigns list
- Create campaign flow
- Campaign editing
- Status filtering
- Analytics display
- Campaign deletion with confirmation

---

## Implementation Roadmap

### Week 1 (Priority Tasks)
1. ✅ PaginationComponent (2h)
2. ✅ PaymentForm (4h)
3. ✅ Cart Page (3h)
4. ✅ Checkout Page (4h)

**Milestone**: E-commerce flow complete and testable

### Week 2 (Core Features)
5. ✅ DateRangePicker (4h)
6. ✅ Complete Beats Page (3h)
7. ✅ Discover Page (4h)
8. ✅ SearchAutocomplete (3h)

**Milestone**: Full beat discovery and management system

### Week 3 (Engagement Features)
9. ✅ NotificationCenter (3h)
10. ✅ Trending Page (2h)
11. ✅ Bookings Page (3h)
12. ✅ Fan Clubs Page (3h)

**Milestone**: Community and engagement features complete

### Week 4 (Final Features & Polish)
13. ✅ Campaigns Page (4h)
14. ✅ Admin Dashboard (if required)
15. ✅ Bug fixes and optimization
16. ✅ Comprehensive testing

**Milestone**: Phase 4 complete, all pages styled with Stitch design

---

## Design & Implementation Standards

### Stitch Design Compliance Checklist
For each component/page implementation:

- [ ] Colors: Use only Stitch palette tokens from globals.css
- [ ] Typography: Apply Stitch typography classes (headline, body, label)
- [ ] Spacing: Use Stitch spacing tokens (margin, padding, gap)
- [ ] Borders: Use ghost-border utility or outline-variant class
- [ ] Buttons: Use Button component with Stitch variants
- [ ] Cards: Use Card component with proper styling
- [ ] Icons: Use lucide-react or Material Symbols
- [ ] Responsive: Mobile (375px) → Tablet (768px) → Desktop (1024px+)
- [ ] Accessibility: ARIA labels, keyboard navigation, semantic HTML
- [ ] Animations: Smooth transitions (200-300ms), no flashing

### Code Quality Standards

- [ ] TypeScript: Strict mode, no `any` types
- [ ] Components: Functional, hooks-based, with proper prop types
- [ ] State: Use Zustand for UI state, React Query for server data
- [ ] Testing: Unit tests for components, integration tests for flows
- [ ] Documentation: JSDoc comments for complex logic
- [ ] Performance: Optimize with React.memo, useCallback, useMemo
- [ ] Error Handling: Try-catch blocks, error boundaries, user feedback

### Testing Strategy

Each task includes:
- [ ] Unit tests for components (Jest + React Testing Library)
- [ ] Integration tests for flows (user journey testing)
- [ ] Visual regression testing (Stitch design consistency)
- [ ] Responsive testing (mobile/tablet/desktop)
- [ ] Accessibility testing (keyboard, screen reader, ARIA)
- [ ] Performance testing (load times, animations smoothness)

---

## Success Criteria

### Phase 4 Complete When:
- ✅ All 13 tasks implemented and tested
- ✅ All components follow Stitch design system
- ✅ All pages responsive across breakpoints
- ✅ Build passes with zero errors
- ✅ No console errors or warnings
- ✅ Comprehensive documentation created
- ✅ Ready for backend API integration

### Quality Metrics:
- 100% Stitch design token usage (no hardcoded colors)
- 95%+ unit test coverage for components
- Zero TypeScript strict mode violations
- < 3 second load time for any page
- Mobile accessibility score ≥ 90

---

## Risk Mitigation

### Technical Risks:
1. **Payment Integration Complexity** → Start with test/sandbox environment
2. **Real-time Features (WebSocket)** → Use existing WebSocket manager from Phase 1
3. **Large Grid Performance** → Implement virtual scrolling if needed
4. **Form Complexity** → Use existing React Hook Form + Zod patterns

### Timeline Risks:
1. Prioritize critical e-commerce tasks first (weeks 1-2)
2. Run tasks in parallel where possible
3. Have fallback implementations (mock data) for blocked tasks
4. Weekly progress reviews with build verification

---

## Next Steps

1. **Before Starting**: Confirm Phase 4 priority with user
2. **Task 1-2**: Implement core shared components this week
3. **Task 3-4**: Complete e-commerce flow by week end
4. **Weekly**: Build verification, responsive testing, Stitch compliance check
5. **After Each Task**: Documentation update, test coverage verification

---

## Files Reference

**Base Styling & Config**:
- `frontend/src/styles/globals.css` - Stitch palette, utilities
- `frontend/tailwind.config.ts` - Tailwind theme with Stitch colors
- `frontend/src/components/ui/` - Base UI component library

**Established Patterns to Follow**:
- `frontend/src/app/(dashboard)/analytics/page.tsx` - Dashboard template
- `frontend/src/app/(dashboard)/profile/page.tsx` - Form + modal pattern
- `frontend/src/app/(dashboard)/messages/page.tsx` - List + detail pattern
- `frontend/src/components/features/analytics/` - Chart components

**Hooks & Services**:
- `frontend/src/hooks/useProfile.ts` - Data fetching pattern
- `frontend/src/services/authService.ts` - API service pattern
- `frontend/src/store/authStore.ts` - State management pattern

---

**Created**: September 1, 2026  
**Author**: Kiro Agent  
**Status**: Ready for Phase 4 Implementation
