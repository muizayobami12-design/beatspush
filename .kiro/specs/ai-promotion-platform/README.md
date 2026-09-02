# AI Promotion Platform - Spec Overview

## 🎯 Goal

Transform BeatPush into a comprehensive music promotion platform for the African market with:
- **Autonomous AI Agent** (BeatPush AI) for proactive assistance
- **Multi-Platform Publishing** to TikTok, Instagram, Facebook, Spotify, Apple Music
- **Promotion Packages** instead of wallet top-up (Basic ₦5K, Pro ₦15K, Premium ₦50K)
- **Post Approval Workflow** - BeatPush prepares, you approve
- **Unified Analytics** across all platforms
- **Real-Time Tracking** of spending, earnings, and performance
- **African Market Focus** - Design, pricing, and targeting for NG, GH, KE, ZA

---

## 📚 Specification Documents

### 1. **requirements.md** - WHAT We're Building
- 20 detailed requirements with acceptance criteria
- Covers all 3 major feature sets
- Defines success metrics and constraints
- User stories for each feature

### 2. **design.md** - HOW We're Building It
- Complete system architecture
- Database schema (10 new tables)
- API endpoint specifications
- AI service design patterns
- Social platform integration flows
- Frontend component structure
- Background job definitions
- Security and performance strategies

### 3. **tasks.md** - Implementation Roadmap
- 50+ granular tasks organized into 10 phases
- Priority levels (Critical → Future)
- 6-8 week estimated timeline
- Files to create/modify for each task

---

## 🎨 Design Philosophy

Following **BEATPUSH_DESIGN_PREVIEW.md**:
- Dark background: `#101012` (near-black)
- Gradient accents: Orange `#FF6B35` → Gold `#F7931E` → Magenta `#C2185B`
- Action buttons: Spotify green `#1DB954`
- Bold white text for maximum readability
- African sunset-inspired color palette
- Professional, modern, unique

---

## 🚀 Key Features

### Feature 1: Real-Time AI Agent (BeatPush AI)
- Works autonomously 24/7
- Music production tips & marketing advice
- Copyright detection (detect if music published elsewhere)
- Smart beat recommendations matching artist needs
- Artist-Producer matchmaking
- 24-hour conversation memory
- Real-time streaming responses

### Feature 2: Multi-Platform Publishing & Promotion
**Part A: No Wallet - Promotion Packages**
- Basic: ₦5,000 (1 platform, 1 week, Nigeria, 10K reach)
- Pro: ₦15,000 (3 platforms, 2 weeks, 2 countries, 50K reach)
- Premium: ₦50,000 (All platforms, 1 month, all countries, 200K reach)
- Real-time spending & earnings tracking

**Part B: Social Media Integration (Middleman Model)**
- Connect TikTok, Facebook, Instagram, Spotify, Apple Music
- BeatPush prepares posts → You approve → BeatPush publishes
- Unified analytics dashboard
- Track: plays, likes, shares, comments, sales
- Different prices per platform

**Part C: Payment & Targeting**
- Paystack multi-currency (USD, NGN, GHS, KES, ZAR)
- Target: Nigeria, Ghana, Kenya, South Africa
- Durations: 1 week, 2 weeks, 1 month

### Feature 3: Full Campaign Management
- BeatPush handles entire promotion
- Automated optimization
- Show real-time results with live activity feed
- African market optimized

---

## 🗄️ Database Changes

### New Tables (9)
1. `ai_conversations` - 24-hour conversation memory
2. `copyright_detections` - Audio fingerprint matching
3. `promotion_packages` - Basic/Pro/Premium tiers
4. `campaigns` - Campaign tracking
5. `social_accounts` - OAuth tokens for platforms
6. `post_drafts` - Post approval workflow
7. `platform_metrics` - Performance from all platforms
8. `beat_recommendations` - AI recommendations
9. `producer_matchmaking` - Artist-producer connections

### Modified Tables (2)
1. `beats` - Add platform-specific pricing columns
2. `users` - Add AI preferences

---

## 🔌 External Integrations

### AI & ML
- **HuggingFace API** - NLP and text generation
- **Chromaprint/AcoustID** - Audio fingerprinting for copyright

### Payments
- **Paystack** - Multi-currency payment processing

### Social Platforms
- **TikTok API** - OAuth, posting, metrics
- **Facebook Graph API** - OAuth, posting, metrics
- **Instagram Graph API** - OAuth, posting, metrics
- **Spotify for Developers** - OAuth, distribution, metrics
- **Apple Music API** - OAuth, distribution, metrics

### Infrastructure
- **Redis** - 24-hour conversation memory, caching
- **Celery** - Background jobs (metrics sync, optimization, notifications)
- **WebSocket** - Real-time updates for metrics and AI status

---

## 📊 Implementation Phases

### Phase 1: Foundation (Week 1-2) 🔴 CRITICAL
- Database schema + migrations
- Redis configuration
- Design system implementation
- Promotion packages setup

### Phase 2: AI Core (Week 2-3) 🟠 HIGH
- Autonomous AI agent
- Copyright detection
- Beat recommendations
- AI chat interface

### Phase 3: Campaigns (Week 3-4) 🟡 MEDIUM
- Campaign creation + Paystack
- Budget tracking
- Campaign dashboard

### Phase 4: Social Integration (Week 4-5) 🟢 NORMAL
- OAuth for 5 platforms
- Post draft generation with AI
- Post approval workflow
- Multi-platform publishing

### Phase 5: Analytics (Week 5-6) 🔵 LOW
- Platform metrics sync (every 15 min)
- Unified analytics dashboard
- Real-time activity feed
- Campaign optimization

### Phase 6-10: Polish & Enhancement ⚪ FUTURE
- Producer matchmaking
- PWA implementation
- Testing suite
- Documentation

---

## 🎯 Success Metrics

1. **AI Engagement**: 70%+ users interact with BeatPush AI in first week
2. **Campaign Adoption**: 40%+ of beat uploads use promotion packages
3. **Multi-Platform Usage**: Average 3+ platforms connected per user
4. **Approval Rate**: 95%+ approval on AI-generated posts
5. **ROI**: 60%+ Premium campaigns achieve positive ROI
6. **Geographic Distribution**: Equal reach across all 4 countries
7. **User Satisfaction**: 4.5+ star rating

---

## 🚦 Next Steps

### Before Implementation
- [ ] Review all 3 spec documents (requirements, design, tasks)
- [ ] Discuss pricing strategy for promotion packages
- [ ] Confirm OAuth app setup for social platforms
- [ ] Verify Paystack account configuration
- [ ] Confirm HuggingFace API access

### To Start Building
1. **Run migrations**: Create new database tables (Task 1.1)
2. **Update design**: Implement new color system (Task 6.1)
3. **Build AI agent**: Core autonomous service (Task 2.1)
4. **Create packages**: Seed promotion tiers (Task 3.1)

### Discussion Topics
1. **Promotion Package Pricing**: Are ₦5K / ₦15K / ₦50K good starting prices?
2. **Platform Priority**: Which platforms should we launch with first?
3. **AI Provider**: HuggingFace vs OpenAI vs other?
4. **Copyright Detection**: Free AcoustID vs paid service?

---

## 📁 Files Created

```
.kiro/specs/ai-promotion-platform/
├── README.md          ← You are here
├── requirements.md    ← 20 requirements with acceptance criteria
├── design.md          ← Technical architecture & design
└── tasks.md           ← 50+ implementation tasks
```

---

**Ready to build?** Start with Phase 1 tasks or discuss any questions about the spec! 🚀
