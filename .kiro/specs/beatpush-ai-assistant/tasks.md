# Implementation Tasks: BeatPush AI Assistant

## Overview

This task list implements the BeatPush AI Assistant feature with free-tier and premium AI capabilities. Total: 40 tasks across 4 phases.

**Target Completion:** 4-6 weeks  
**Team Size:** 2-3 developers (1 backend, 1-2 frontend)  
**Dependencies:** Redis, Hugging Face API access

---

## Phase 1: Backend Infrastructure (14 tasks)

### Task 1.1: Setup AI Service Module Structure
**Description:** Create base AI service architecture with provider abstraction

**Files to Create:**
- `backend/app/ai/providers/__init__.py`
- `backend/app/ai/providers/base.py` - Abstract provider interface
- `backend/app/ai/providers/huggingface_provider.py`
- `backend/app/ai/providers/fallback_provider.py`
- `backend/app/ai/exceptions.py` - Custom exceptions

**Acceptance Criteria:**
- [ ] Abstract `AIProvider` base class defined
- [ ] Provider interface includes `generate()`, `is_available()`, `get_model_for_type()`
- [ ] Custom exceptions: `ProviderException`, `ProviderBusyException`, `AIServiceUnavailableException`

**Dependencies:** None  
**Effort:** 4 hours

---

### Task 1.2: Implement Hugging Face API Client
**Description:** Create primary AI provider using Hugging Face Inference API

**Files to Modify:**
- `backend/app/ai/providers/huggingface_provider.py`

**Implementation Details:**
- Use free Hugging Face Inference API (no auth required)
- Model mapping: FLAN-T5 (titles, descriptions), BLOOM (press releases), BART (captions)
- Async HTTP client with aiohttp
- 10-second timeout per request
- Handle 503 (model loading) with retry logic

**Acceptance Criteria:**
- [ ] Successfully calls Hugging Face API
- [ ] Handles all 8 request types (title, description, caption, hashtags, press_release, campaign_suggestions, genre_tags, audience_insights)
- [ ] Proper error handling for API failures
- [ ] Retry logic for 503 responses (max 3 retries)

**Dependencies:** Task 1.1  
**Effort:** 8 hours

---

### Task 1.3: Create Response Cache Layer
**Description:** Implement Redis-based caching for AI responses

**Files to Create:**
- `backend/app/ai/response_cache.py`

**Implementation Details:**
- Cache key generation from request_type + normalized params
- SHA256 hash for cache keys
- 7-day TTL
- Exclude user-specific data from cache keys
- JSON serialization of responses

**Acceptance Criteria:**
- [ ] Cache keys generated consistently for identical requests
- [ ] TTL set to 7 days
- [ ] Cache hit/miss tracked
- [ ] User-specific data excluded from caching

**Dependencies:** Task 1.1  
**Effort:** 4 hours

---

### Task 1.4: Implement Rate Limiting Middleware
**Description:** Redis-based rate limiter for free/premium tiers


**Files to Create:**
- `backend/app/core/rate_limiting.py`
- `backend/app/core/dependencies.py` - Add `get_rate_limiter` dependency

**Implementation Details:**
- Free tier: 20 requests/day
- Premium tier: Unlimited
- Redis key pattern: `ai_quota:{user_id}:{date}`
- Atomic INCR operations
- Auto-expire at midnight UTC
- Return quota info in responses

**Acceptance Criteria:**
- [ ] Free users limited to 20 requests/day
- [ ] Premium users unlimited
- [ ] Quota resets at midnight UTC
- [ ] Thread-safe atomic operations
- [ ] Quota info included in API responses

**Dependencies:** Task 1.1  
**Effort:** 6 hours

---

### Task 1.5: Update User Model with AI Tier
**Description:** Add tier field to User model for free/premium tracking

**Files to Modify:**
- `backend/app/models/user.py`
- `backend/alembic/versions/` - New migration

**Implementation Details:**
```python
class User(Base):
    # ... existing fields ...
    tier = Column(
        Enum('free', 'premium', name='user_tier'),
        default='free',
        nullable=False
    )
    ai_requests_count = Column(Integer, default=0)  # Lifetime count for analytics
```

**Acceptance Criteria:**
- [ ] `tier` field added (enum: free, premium)
- [ ] Migration created and tested
- [ ] Default value is 'free'
- [ ] Analytics counter added

**Dependencies:** None  
**Effort:** 2 hours

---

### Task 1.6: Create AI Request/Response Models
**Description:** SQLAlchemy models for AI request logging

**Files to Create:**
- `backend/app/models/ai_request.py`

**Implementation Details:**
```python
class AIRequest(Base):
    __tablename__ = "ai_requests"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    request_type = Column(String(50))
    params = Column(JSON)
    response_time_ms = Column(Integer)
    provider = Column(String(50))
    cached = Column(Boolean, default=False)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="ai_requests")
```

**Acceptance Criteria:**
- [ ] Model captures all request metadata
- [ ] Relationship with User model
- [ ] Index on user_id and created_at

**Dependencies:** Task 1.5  
**Effort:** 3 hours

---

### Task 1.7: Create Unified AI Generation Endpoint
**Description:** Single REST endpoint for all AI generation types

**Files to Modify:**
- `backend/app/api/v1/endpoints/ai.py` - Refactor existing endpoints

**Implementation Details:**
- `POST /api/v1/ai/generate`
- Request schema: `{request_type, params}`
- Response includes: content, metadata, quota info
- Rate limiting middleware applied
- Request logging

**Acceptance Criteria:**
- [ ] Endpoint accepts all 8 request types
- [ ] Rate limiting enforced
- [ ] Quota info in response
- [ ] Request logged to database
- [ ] Proper error handling (401, 429, 503)

**Dependencies:** Tasks 1.2, 1.3, 1.4  
**Effort:** 6 hours

---

### Task 1.8: Implement WebSocket Streaming Endpoint
**Description:** WebSocket support for real-time AI response streaming

**Files to Create:**
- `backend/app/api/v1/endpoints/ai_ws.py`

**Implementation Details:**
- `/api/v1/ai/ws?token=<jwt>`
- JWT authentication in connection params
- Streaming for long-form content
- Progress indicators
- Handle disconnections gracefully

**Acceptance Criteria:**
- [ ] WebSocket connection authenticated via JWT
- [ ] Responses streamed in chunks
- [ ] Progress indicators sent
- [ ] Clean disconnection handling
- [ ] Same rate limiting as REST

**Dependencies:** Task 1.7  
**Effort:** 8 hours

---


### Task 1.9: Add Configuration for AI Providers
**Description:** Add AI provider settings to config

**Files to Modify:**
- `backend/app/core/config.py`
- `backend/.env.example`

**Implementation Details:**
```python
# AI Configuration
HUGGINGFACE_API_URL: str = "https://api-inference.huggingface.co"
AI_CACHE_TTL_DAYS: int = 7
AI_FREE_TIER_DAILY_LIMIT: int = 20
AI_RESPONSE_TIMEOUT_SECONDS: int = 10
AI_MAX_RETRIES: int = 3
```

**Acceptance Criteria:**
- [ ] All AI settings configurable via .env
- [ ] Sensible defaults provided
- [ ] Documentation in .env.example

**Dependencies:** None  
**Effort:** 1 hour

---

### Task 1.10: Create AI Service Dependency Injection
**Description:** FastAPI dependency for AI service

**Files to Modify:**
- `backend/app/core/dependencies.py`

**Implementation Details:**
```python
def get_ai_service(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> AIService:
    return AIService(db=db, redis=redis)
```

**Acceptance Criteria:**
- [ ] AI service injectable in endpoints
- [ ] Proper dependency chain (db, redis)
- [ ] Singleton pattern for providers

**Dependencies:** Tasks 1.1, 1.2, 1.3  
**Effort:** 2 hours

---

### Task 1.11: Implement Prompt Templates
**Description:** Create optimized prompts for each AI request type

**Files to Create:**
- `backend/app/ai/prompts.py`

**Implementation Details:**
- Template for each of 8 request types
- Optimized for smaller models (FLAN-T5, BLOOM)
- Include few-shot examples
- Context window management (1024-2048 tokens)

**Acceptance Criteria:**
- [ ] Prompt template for each request type
- [ ] Few-shot examples included
- [ ] Optimized token usage
- [ ] African music context incorporated

**Dependencies:** None  
**Effort:** 6 hours

---

### Task 1.12: Add Error Handling and Fallback Logic
**Description:** Robust error handling with provider fallbacks

**Files to Modify:**
- `backend/app/ai/ai_service.py`

**Implementation Details:**
- Try providers in priority order
- Exponential backoff between retries
- Graceful degradation
- Detailed error logging
- User-friendly error messages

**Acceptance Criteria:**
- [ ] Falls back to secondary providers on failure
- [ ] Exponential backoff (1s, 2s, 4s)
- [ ] All errors logged with context
- [ ] User receives helpful error messages
- [ ] Service returns 503 only when all providers fail

**Dependencies:** Task 1.2  
**Effort:** 5 hours

---

### Task 1.13: Implement Usage Analytics Logging
**Description:** Track AI usage for analytics and monitoring

**Files to Create:**
- `backend/app/services/ai_analytics.py`

**Implementation Details:**
- Log every request (success/failure)
- Track provider performance
- Cache hit rates
- Response times by request type
- Daily aggregates
- Prometheus metrics endpoint

**Acceptance Criteria:**
- [ ] All requests logged to database
- [ ] Metrics exposed for Prometheus
- [ ] Daily aggregates calculated
- [ ] Dashboard-ready data structure

**Dependencies:** Task 1.6  
**Effort:** 4 hours

---

### Task 1.14: Content Safety and Moderation
**Description:** Filter AI responses for inappropriate content

**Files to Create:**
- `backend/app/ai/content_filter.py`

**Implementation Details:**
- Profanity filter
- Offensive language detection
- Off-topic response detection
- Injection attempt blocking
- Retry with stricter prompts on violations

**Acceptance Criteria:**
- [ ] Filters profanity and offensive content
- [ ] Blocks prompt injection attempts
- [ ] Validates response relevance
- [ ] Logs flagged content for review

**Dependencies:** Task 1.2  
**Effort:** 5 hours

---

## Phase 2: AI Capabilities (8 tasks)

### Task 2.1: Beat Title Generation
**Description:** Generate 5 creative title variations for beats

**Files to Modify:**
- `backend/app/ai/generators/title_generator.py` (new)

**Parameters:**
- genre, mood, bpm, instruments, keywords

**Output:**
- Array of 5 titles (10-60 characters each)

**Acceptance Criteria:**
- [ ] Generates 5 unique titles
- [ ] Titles appropriate for genre/mood
- [ ] Length validation (10-60 chars)
- [ ] No duplicate suggestions

**Dependencies:** Task 1.11  
**Effort:** 4 hours

---

### Task 2.2: Beat Description Generation
**Description:** Generate 3 description lengths (short, medium, long)

**Files to Modify:**
- `backend/app/ai/generators/description_generator.py` (new)

**Parameters:**
- title, genre, mood, bpm, instruments, target_audience

**Output:**
- short (50-100 words), medium (150-200 words), long (300-400 words)

**Acceptance Criteria:**
- [ ] 3 length variations generated
- [ ] Highlights unique selling points
- [ ] Music terminology appropriate to genre
- [ ] Commercial appeal emphasized

**Dependencies:** Task 1.11  
**Effort:** 4 hours

---


### Task 2.3: Social Media Caption Generation
**Description:** Generate 5 caption variations with different tones

**Files to Keep (Already Implemented):**
- `backend/app/ai/ai_service.py` - `generate_social_captions()`

**Refactoring Required:**
- Replace OpenAI with Hugging Face provider
- Maintain existing tone variations (hype, emotional, professional, fun, mysterious)
- Platform-specific formatting (Instagram, Twitter, TikTok, Facebook)

**Acceptance Criteria:**
- [ ] Works with Hugging Face instead of OpenAI
- [ ] 5 tone variations maintained
- [ ] Platform character limits respected
- [ ] Emoji suggestions included

**Dependencies:** Task 1.2  
**Effort:** 3 hours

---

### Task 2.4: Hashtag Generation
**Description:** Generate categorized hashtags (genre, trending, location, campaign)

**Files to Keep (Already Implemented):**
- `backend/app/ai/ai_service.py` - `generate_hashtags()`

**Refactoring Required:**
- Replace OpenAI with Hugging Face provider
- Maintain 4 categories
- African music focus

**Acceptance Criteria:**
- [ ] Works with Hugging Face
- [ ] 4 categories maintained (genre 5-7, trending 3-5, location 3-5, campaign 2-3)
- [ ] Mix of popular and niche tags

**Dependencies:** Task 1.2  
**Effort:** 3 hours

---

### Task 2.5: Press Release Generation
**Description:** Generate professional press releases (300-400 words)

**Files to Keep (Already Implemented):**
- `backend/app/ai/ai_service.py` - `generate_press_release()`

**Refactoring Required:**
- Replace OpenAI with Hugging Face (use BLOOM model)
- Maintain AP style formatting
- Include all sections (headline, opening, details, quote, availability)

**Acceptance Criteria:**
- [ ] Works with Hugging Face/BLOOM
- [ ] 300-400 word length
- [ ] All required sections included
- [ ] Professional tone maintained

**Dependencies:** Task 1.2  
**Effort:** 4 hours

---

### Task 2.6: Campaign Optimization Suggestions
**Description:** Analyze campaigns and provide actionable recommendations

**Files to Create:**
- `backend/app/ai/generators/campaign_optimizer.py`

**Parameters:**
- campaign_metrics (reach, engagement, conversion), target_audience, budget, platform

**Output:**
- 3-5 specific, actionable suggestions
- Budget allocation recommendations
- A/B testing opportunities
- Optimal posting times

**Acceptance Criteria:**
- [ ] Analyzes campaign performance
- [ ] Provides 3-5 actionable suggestions
- [ ] Budget recommendations included
- [ ] A/B testing ideas suggested

**Dependencies:** Task 1.11  
**Effort:** 6 hours

---

### Task 2.7: Genre and Mood Tagging
**Description:** Suggest genres and mood tags for beats

**Files to Create:**
- `backend/app/ai/generators/genre_tagger.py`

**Parameters:**
- title, description, bpm, key, instruments

**Output:**
- 3-5 primary genres with confidence scores
- 5-10 mood tags
- Both broad and niche tags

**Acceptance Criteria:**
- [ ] 3-5 genre suggestions with confidence
- [ ] 5-10 mood tags
- [ ] No contradictory combinations
- [ ] Mix of broad/niche tags

**Dependencies:** Task 1.11  
**Effort:** 5 hours

---

### Task 2.8: Target Audience Insights
**Description:** Provide demographic and behavioral insights

**Files to Create:**
- `backend/app/ai/generators/audience_analyzer.py`

**Parameters:**
- genre, style, existing_audience_data (optional)

**Output:**
- Demographics (age, gender, location)
- Platform recommendations
- Content themes
- Growth strategies

**Acceptance Criteria:**
- [ ] Demographic insights provided
- [ ] Platform recommendations specific
- [ ] Content themes suggested
- [ ] Growth strategies actionable

**Dependencies:** Task 1.11  
**Effort:** 5 hours

---

## Phase 3: Frontend Components (10 tasks)

### Task 3.1: Create AI Chat UI Base Component
**Description:** Gemini-style chat interface component

**Files to Create:**
- `frontend/src/components/ai/AIChat.tsx`
- `frontend/src/components/ai/ChatMessage.tsx`
- `frontend/src/components/ai/ChatInput.tsx`

**Styling:**
- Gradient theme (purple/blue)
- Glassmorphism effects
- Smooth animations (300ms transitions)
- Modern typography (sans-serif, 16px base)

**Features:**
- User messages on right
- AI responses on left
- Markdown rendering
- Typing indicator
- Auto-scroll to latest

**Acceptance Criteria:**
- [ ] Gemini-style visual design
- [ ] Responsive (mobile, tablet, desktop)
- [ ] Smooth animations
- [ ] Markdown support in AI responses
- [ ] Auto-scroll behavior

**Dependencies:** None  
**Effort:** 8 hours

---

### Task 3.2: Implement API Client for AI Endpoints
**Description:** Frontend service for AI API calls

**Files to Create:**
- `frontend/src/services/aiService.ts`

**Functions:**
```typescript
async generateContent(requestType: AIRequestType, params: any): Promise<AIResponse>
async getQuotaStatus(): Promise<QuotaInfo>
async connectWebSocket(token: string): Promise<WebSocket>
```

**Acceptance Criteria:**
- [ ] REST API client methods
- [ ] WebSocket connection handling
- [ ] Error handling with retry logic
- [ ] TypeScript types for all requests/responses
- [ ] Token management

**Dependencies:** None  
**Effort:** 4 hours

---


### Task 3.3: Add Quota Display Component
**Description:** Show remaining AI requests for free tier users

**Files to Create:**
- `frontend/src/components/ai/QuotaDisplay.tsx`

**Display:**
- Remaining requests count
- Reset time countdown
- Visual progress bar
- Tier indicator (free/premium)

**Acceptance Criteria:**
- [ ] Shows remaining requests
- [ ] Countdown to reset
- [ ] Warning state at 5 or fewer
- [ ] Hidden for premium users (or shows "Unlimited")

**Dependencies:** Task 3.2  
**Effort:** 3 hours

---

### Task 3.4: Create Upgrade Prompt Component
**Description:** Prompt shown when quota exceeded

**Files to Create:**
- `frontend/src/components/ai/UpgradePrompt.tsx`

**Content:**
- Quota exceeded message
- Feature comparison table (free vs premium)
- Call-to-action button
- Benefits list

**Acceptance Criteria:**
- [ ] Shown on 429 response
- [ ] Feature comparison clear
- [ ] Links to pricing page
- [ ] Dismissible but persistent

**Dependencies:** None  
**Effort:** 3 hours

---

### Task 3.5: Implement Quick Action Buttons
**Description:** Contextual quick actions for common AI tasks

**Files to Create:**
- `frontend/src/components/ai/QuickActions.tsx`

**Actions:**
- "Generate Title" - For beat upload
- "Create Caption" - For social sharing
- "Optimize Campaign" - For campaign dashboard
- "Suggest Tags" - For beat metadata
- "Write Description" - For beat details

**Acceptance Criteria:**
- [ ] Context-aware buttons
- [ ] One-click AI generation
- [ ] Loading states
- [ ] Result insertion into forms

**Dependencies:** Task 3.2  
**Effort:** 5 hours

---

### Task 3.6: Create AI Sidebar Component
**Description:** Collapsible AI assistant sidebar for contextual help

**Files to Create:**
- `frontend/src/components/ai/AISidebar.tsx`
- `frontend/src/hooks/useAISidebar.ts`

**Features:**
- Collapsible/expandable
- Persistent across navigation
- Context injection (current page data)
- Chat history for session

**Acceptance Criteria:**
- [ ] Sidebar toggleable
- [ ] Maintains state across pages
- [ ] Injects page context automatically
- [ ] Session chat history

**Dependencies:** Task 3.1  
**Effort:** 6 hours

---

### Task 3.7: Add Markdown Rendering for AI Responses
**Description:** Render AI responses with formatting

**Files to Modify:**
- `frontend/src/components/ai/ChatMessage.tsx`

**Install:** `react-markdown`, `remark-gfm`

**Features:**
- Bold, italic, lists
- Code blocks with syntax highlighting
- Links
- Tables (for comparisons)

**Acceptance Criteria:**
- [ ] Markdown fully rendered
- [ ] Code syntax highlighting
- [ ] Links open in new tab
- [ ] Responsive formatting

**Dependencies:** Task 3.1  
**Effort:** 3 hours

---

### Task 3.8: Implement WebSocket Client for Streaming
**Description:** Real-time streaming of AI responses

**Files to Modify:**
- `frontend/src/components/ai/AIChat.tsx`
- `frontend/src/services/aiService.ts`

**Features:**
- Establish WebSocket connection
- Stream response chunks
- Typing effect animation
- Handle reconnection
- Progress indicators

**Acceptance Criteria:**
- [ ] WebSocket connection established
- [ ] Chunks streamed and displayed
- [ ] Typing animation smooth
- [ ] Reconnects on disconnect
- [ ] Progress shown for long generations

**Dependencies:** Task 3.1, 3.2  
**Effort:** 6 hours

---

### Task 3.9: Add Copy-to-Clipboard Functionality
**Description:** Allow users to copy AI-generated content

**Files to Modify:**
- `frontend/src/components/ai/ChatMessage.tsx`

**Features:**
- Copy button on each AI message
- Visual feedback on copy
- Clipboard API usage

**Acceptance Criteria:**
- [ ] Copy button on all AI messages
- [ ] Confirmation animation
- [ ] Works across browsers
- [ ] Fallback for older browsers

**Dependencies:** Task 3.1  
**Effort:** 2 hours

---

### Task 3.10: Create AI Loading States and Animations
**Description:** Smooth loading indicators and transitions

**Files to Create:**
- `frontend/src/components/ai/AILoadingStates.tsx`

**Animations:**
- Typing dots animation
- Shimmer effect for loading
- Fade-in transitions
- Progress bars for long operations

**Acceptance Criteria:**
- [ ] Typing indicator animation
- [ ] Smooth transitions (300ms)
- [ ] Progress shown appropriately
- [ ] 60fps performance

**Dependencies:** None  
**Effort:** 4 hours

---

## Phase 4: Integration & Polish (8 tasks)

### Task 4.1: Integrate AI into Beat Upload Page
**Description:** Add AI assistant to beat upload flow

**Files to Modify:**
- `frontend/src/app/(dashboard)/beats/upload/page.tsx`

**Features:**
- AI sidebar for help
- "Generate Title" button
- "Generate Description" button
- "Suggest Tags" button
- Auto-fill form fields with AI output

**Acceptance Criteria:**
- [ ] AI sidebar accessible
- [ ] Quick actions for title/description/tags
- [ ] One-click form field population
- [ ] Context passed to AI (uploaded file metadata)

**Dependencies:** Tasks 3.1, 3.5, 3.6  
**Effort:** 5 hours

---


### Task 4.2: Integrate AI into Beat Edit Page
**Description:** Add AI assistance to beat editing

**Files to Modify:**
- `frontend/src/app/(dashboard)/beats/[id]/page.tsx`

**Features:**
- AI sidebar with beat context
- Improve existing descriptions
- Generate additional metadata
- SEO keyword suggestions

**Acceptance Criteria:**
- [ ] AI sidebar with beat data context
- [ ] Metadata enhancement actions
- [ ] SEO keyword generation
- [ ] Update form fields with AI suggestions

**Dependencies:** Tasks 3.1, 3.6  
**Effort:** 4 hours

---

### Task 4.3: Integrate AI into Campaign Dashboard
**Description:** AI optimization insights for campaigns

**Files to Modify:**
- `frontend/src/app/(dashboard)/campaigns/page.tsx`
- `frontend/src/components/features/campaigns/CampaignCard.tsx`

**Features:**
- "Optimize Campaign" button per campaign
- AI insights panel
- Actionable recommendations display
- Budget allocation suggestions

**Acceptance Criteria:**
- [ ] Optimize button on each campaign
- [ ] AI insights displayed in modal/panel
- [ ] Recommendations actionable (clickable)
- [ ] Campaign metrics passed to AI

**Dependencies:** Tasks 3.1, 3.5  
**Effort:** 5 hours

---

### Task 4.4: Add AI Insights to Analytics Page
**Description:** AI-powered analytics insights

**Files to Modify:**
- `frontend/src/app/(dashboard)/analytics/page.tsx`

**Features:**
- AI insights widget
- Trend analysis
- Growth recommendations
- Audience behavior insights

**Acceptance Criteria:**
- [ ] AI insights widget prominent
- [ ] Analyzes current metrics
- [ ] Provides growth recommendations
- [ ] Updates based on date range

**Dependencies:** Task 3.1  
**Effort:** 5 hours

---

### Task 4.5: Integrate AI into Social Sharing Flow
**Description:** AI caption and hashtag generation for sharing

**Files to Modify:**
- `frontend/src/components/features/social/ShareModal.tsx` (or similar)

**Features:**
- "Generate Caption" button
- "Generate Hashtags" button
- Platform selection
- Caption tone selection

**Acceptance Criteria:**
- [ ] Generate captions for selected platform
- [ ] Generate categorized hashtags
- [ ] Tone selection (hype, emotional, professional, etc.)
- [ ] Copy to clipboard

**Dependencies:** Tasks 3.1, 3.5  
**Effort:** 4 hours

---

### Task 4.6: Add User Preference Storage
**Description:** Remember user AI preferences and style

**Files to Create:**
- `backend/app/models/ai_preference.py`
- `backend/app/api/v1/endpoints/ai_preferences.py`

**Data Stored:**
- Preferred tone
- Genre focus
- Target audience
- Style examples (thumbs up/down feedback)

**Acceptance Criteria:**
- [ ] User preferences stored in DB
- [ ] Applied to AI prompts automatically
- [ ] User can reset preferences
- [ ] Feedback mechanism (thumbs up/down)

**Dependencies:** Phase 1 complete  
**Effort:** 6 hours

---

### Task 4.7: Create Admin AI Monitoring Dashboard
**Description:** Admin view for AI usage and health

**Files to Create:**
- `frontend/src/app/(admin)/ai-monitoring/page.tsx`
- `backend/app/api/v1/endpoints/ai_admin.py`

**Metrics Displayed:**
- Total requests (daily, weekly, monthly)
- Requests by type
- Average response times
- Cache hit rate
- Provider success rates
- Top users by AI usage
- Quota utilization

**Acceptance Criteria:**
- [ ] Real-time metrics dashboard
- [ ] Filterable by date range
- [ ] Provider performance comparison
- [ ] User tier distribution
- [ ] Cost estimates

**Dependencies:** Task 1.13  
**Effort:** 8 hours

---

### Task 4.8: Performance Optimization and Testing
**Description:** Optimize and test entire AI system

**Activities:**
1. Load testing (simulate 10,000 users)
2. Cache hit rate optimization (target 40%+)
3. Response time optimization (< 5s goal)
4. Memory leak testing
5. Error rate monitoring
6. Cost analysis

**Acceptance Criteria:**
- [ ] Load test: 10,000 concurrent users
- [ ] Cache hit rate > 40%
- [ ] 90th percentile response time < 5s (free), < 3s (premium)
- [ ] No memory leaks in 24h run
- [ ] Error rate < 1%
- [ ] Monthly cost < $50 for 10,000 users

**Dependencies:** All previous tasks  
**Effort:** 12 hours

---

## Summary

### Effort Breakdown

**Phase 1 (Backend):** 14 tasks = 64 hours (~1.5 weeks)
**Phase 2 (AI Capabilities):** 8 tasks = 34 hours (~1 week)
**Phase 3 (Frontend):** 10 tasks = 44 hours (~1 week)
**Phase 4 (Integration):** 8 tasks = 49 hours (~1.5 weeks)

**Total:** 40 tasks = 191 hours (~5 weeks with 1 developer, ~3 weeks with 2 developers)

### Critical Path

1. Phase 1: Tasks 1.1 → 1.2 → 1.3 → 1.4 → 1.7 (Backend foundation)
2. Phase 2: Tasks 2.1-2.8 can run in parallel after 1.11
3. Phase 3: Tasks 3.1 → 3.2 → 3.6 (Frontend foundation)
4. Phase 4: Integration tasks require Phase 1-3 complete

### Testing Strategy

**Unit Tests:**
- AI providers (mock API responses)
- Rate limiter (Redis operations)
- Response cache (cache hit/miss)
- Content filter (safety checks)

**Integration Tests:**
- End-to-end AI generation flow
- WebSocket streaming
- Rate limiting enforcement
- Quota reset timing

**Load Tests:**
- 10,000 concurrent users
- Cache performance under load
- Provider fallback behavior

**User Acceptance Tests:**
- AI quality (human review of generations)
- UX flow (beat upload with AI)
- Mobile responsiveness
- Cross-browser compatibility

---

## Deployment Checklist

- [ ] Redis configured and accessible
- [ ] Hugging Face API accessible (no firewall blocks)
- [ ] Database migration run (user tier, ai_requests table)
- [ ] Environment variables set (AI config)
- [ ] Monitoring/alerts configured
- [ ] Cost tracking enabled
- [ ] User documentation updated
- [ ] Admin trained on monitoring dashboard

