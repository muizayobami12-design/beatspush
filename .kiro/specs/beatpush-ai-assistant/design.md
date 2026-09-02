# Technical Design: BeatPush AI Assistant

## Executive Summary

The BeatPush AI Assistant is a comprehensive AI integration that provides free-tier and premium AI-powered content generation throughout the platform. This design leverages free AI providers (Hugging Face Inference API) to eliminate API key barriers while maintaining a modern, Gemini-style user experience. The architecture prioritizes cost-effectiveness, clean backend-frontend separation, and scalability.

## Design Goals

1. **Zero API Key Barrier** - Use free AI providers (Hugging Face, local models)
2. **Freemium Model** - 20 requests/day for free users, unlimited for premium
3. **Modern UX** - Gemini-style chat interface with contextual integration
4. **Clean Architecture** - Backend APIs, no frontend duplication
5. **Cost-Effective** - Target < $50/month for 10,000 active users
6. **Performance** - 90th percentile response time < 5s (free) / < 3s (premium)
7. **Reliability** - Fallback providers, caching, error handling

## High-Level Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  AI Chat UI      │  │  Beat Upload     │  │  Campaign Dash   │  │
│  │  (Gemini Style)  │  │  AI Sidebar      │  │  AI Insights     │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                      │            │
│           └──────────────┬──────┴──────────┬───────────┘            │
│                          │                  │                        │
└──────────────────────────┼──────────────────┼────────────────────────┘
                           │                  │
                      REST API          WebSocket
                           │                  │
┌──────────────────────────┼──────────────────┼────────────────────────┐
│                     Backend Layer            │                        │
│  ┌────────────────────────┴──────────────────┴───────────────┐       │
│  │              FastAPI Application                           │       │
│  │  ┌──────────────────┐  ┌──────────────────┐              │       │
│  │  │  AI Endpoints    │  │  WebSocket       │              │       │
│  │  │  /ai/generate    │  │  /ai/ws          │              │       │
│  │  └────────┬─────────┘  └────────┬─────────┘              │       │
│  │           │                     │                          │       │
│  │  ┌────────▼──────────────────────▼─────────────┐          │       │
│  │  │      Rate Limiting Middleware                │          │       │
│  │  │      (Check Quota, Enforce Limits)           │          │       │
│  │  └────────┬──────────────────────┬──────────────┘          │       │
│  │           │                      │                          │       │
│  │  ┌────────▼─────────┐  ┌────────▼──────────┐              │       │
│  │  │  AI Service      │  │  Response Cache   │              │       │
│  │  │  - Generation    │  │  (Redis)          │              │       │
│  │  │  - Validation    │  │  - TTL: 7 days    │              │       │
│  │  │  - Fallbacks     │  │  - Hit rate: 40%+ │              │       │
│  │  └────────┬─────────┘  └───────────────────┘              │       │
│  └───────────┼──────────────────────────────────────────────┘       │
│              │                                                        │
└──────────────┼────────────────────────────────────────────────────────┘
               │
     ┌─────────▼──────────┐
     │   Provider Layer   │
     │  ┌──────────────┐  │
     │  │ HuggingFace  │──┼─── Primary: FLAN-T5, BLOOM
     │  │  Free API    │  │
     │  └──────────────┘  │
     │  ┌──────────────┐  │
     │  │  Fallback 1  │──┼─── GPT-2 (local)
     │  │  Local Model │  │
     │  └──────────────┘  │
     │  ┌──────────────┐  │
     │  │  Fallback 2  │──┼─── Alternative free API
     │  │  Alternative │  │
     │  └──────────────┘  │
     └───────────────────┘
```

### Data Flow

#### Request Flow (REST)
1. User triggers AI action in frontend
2. Frontend sends POST to `/api/v1/ai/generate`
3. Backend validates JWT authentication
4. Rate limiting middleware checks user quota
5. Check response cache (Redis) for matching request
6. If cache miss, AI Service generates content
7. Response cached and returned to frontend
8. Frontend renders in Gemini-style UI


#### Request Flow (WebSocket)
1. Frontend establishes WebSocket connection `/api/v1/ai/ws?token=<jwt>`
2. Backend validates JWT and opens connection
3. User sends message through WebSocket
4. Rate limiting checks quota
5. AI Service streams response chunks
6. Frontend displays chunks in real-time (typing effect)
7. Connection persists for conversation

#### Rate Limiting Flow
1. Extract user_id from JWT
2. Build Redis key: `ai_quota:{user_id}:{date}`
3. Check user tier (free/premium)
4. If premium: allow and continue
5. If free: atomic Redis INCR operation
6. If count > 20: return 429 error with upgrade prompt
7. If count ≤ 20: allow and continue
8. Set TTL to midnight UTC if key is new

## Component Design

### 1. AI Service Layer

**Location:** `backend/app/ai/ai_service.py`

**Responsibilities:**
- Manage AI provider connections
- Generate content for all request types
- Handle provider fallbacks
- Validate and sanitize responses
- Track performance metrics

**Architecture:**

```python
class AIService:
    """Core AI service with provider abstraction"""
    
    def __init__(self):
        self.providers = [
            HuggingFaceProvider(priority=1),
            LocalModelProvider(priority=2),
            FallbackAPIProvider(priority=3)
        ]
        self.cache = ResponseCache()
        self.metrics = MetricsCollector()
    
    async def generate(
        self,
        request_type: AIRequestType,
        params: Dict[str, Any],
        user_tier: UserTier
    ) -> AIResponse:
        """Generate AI content with fallback chain"""
        
        # Check cache first
        cache_key = self.cache.build_key(request_type, params)
        cached = await self.cache.get(cache_key)
        if cached:
            self.metrics.record_cache_hit()
            return cached
        
        # Try providers in order
        for provider in sorted(self.providers, key=lambda p: p.priority):
            try:
                result = await provider.generate(request_type, params)
                await self.cache.set(cache_key, result, ttl=604800)  # 7 days
                self.metrics.record_generation(provider.name, success=True)
                return result
            except ProviderException as e:
                self.metrics.record_generation(provider.name, success=False)
                continue
        
        raise AIServiceUnavailableException()
```


**Provider Interface:**

```python
class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate(
        self,
        request_type: AIRequestType,
        params: Dict[str, Any]
    ) -> AIResponse:
        """Generate content"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check provider availability"""
        pass
    
    @abstractmethod
    def get_model_for_type(self, request_type: AIRequestType) -> str:
        """Get optimal model for request type"""
        pass
```

**Hugging Face Provider Implementation:**

```python
class HuggingFaceProvider(AIProvider):
    """Primary provider using Hugging Face Inference API"""
    
    MODELS = {
        AIRequestType.TITLE: "google/flan-t5-large",
        AIRequestType.DESCRIPTION: "google/flan-t5-large",
        AIRequestType.CAPTION: "facebook/bart-large-cnn",
        AIRequestType.HASHTAGS: "google/flan-t5-base",
        AIRequestType.PRESS_RELEASE: "bigscience/bloom-1b7",
        AIRequestType.CAMPAIGN_SUGGESTIONS: "google/flan-t5-large",
        AIRequestType.GENRE_TAGS: "google/flan-t5-base",
        AIRequestType.AUDIENCE_INSIGHTS: "google/flan-t5-large"
    }
    
    def __init__(self, api_url: str = "https://api-inference.huggingface.co"):
        self.api_url = api_url
        self.session = aiohttp.ClientSession()
        self.priority = 1
        self.name = "huggingface"
    
    async def generate(
        self,
        request_type: AIRequestType,
        params: Dict[str, Any]
    ) -> AIResponse:
        """Generate using Hugging Face API"""
        
        model = self.get_model_for_type(request_type)
        prompt = self._build_prompt(request_type, params)
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": self._get_max_length(request_type),
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        async with self.session.post(
            f"{self.api_url}/models/{model}",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_response(request_type, data, params)
            elif response.status == 503:
                raise ProviderBusyException()
            else:
                raise ProviderException(f"API error: {response.status}")
```

### 2. Rate Limiting Middleware

**Location:** `backend/app/core/rate_limiting.py`

**Responsibilities:**
- Track daily request quotas per user
- Enforce limits for free-tier users
- Allow unlimited for premium users
- Provide quota information in responses


**Architecture:**

```python
class AIRateLimiter:
    """Redis-based rate limiter for AI requests"""
    
    FREE_TIER_DAILY_LIMIT = 20
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def check_and_increment(
        self,
        user_id: int,
        user_tier: UserTier
    ) -> QuotaStatus:
        """Check quota and increment if allowed"""
        
        # Premium users have unlimited access
        if user_tier == UserTier.PREMIUM:
            return QuotaStatus(
                allowed=True,
                remaining=None,  # Unlimited
                reset_at=None,
                tier=UserTier.PREMIUM
            )
        
        # Free tier: check and increment
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"ai_quota:{user_id}:{today}"
        
        # Atomic increment
        current = await self.redis.incr(key)
        
        # Set expiry if this is first request of the day
        if current == 1:
            midnight = self._get_next_midnight_utc()
            ttl = int((midnight - datetime.utcnow()).total_seconds())
            await self.redis.expire(key, ttl)
        
        # Check limit
        if current > self.FREE_TIER_DAILY_LIMIT:
            return QuotaStatus(
                allowed=False,
                remaining=0,
                reset_at=self._get_next_midnight_utc(),
                tier=UserTier.FREE,
                exceeded=True
            )
        
        return QuotaStatus(
            allowed=True,
            remaining=self.FREE_TIER_DAILY_LIMIT - current,
            reset_at=self._get_next_midnight_utc(),
            tier=UserTier.FREE
        )
    
    async def get_quota_info(
        self,
        user_id: int,
        user_tier: UserTier
    ) -> QuotaStatus:
        """Get current quota status without incrementing"""
        
        if user_tier == UserTier.PREMIUM:
            return QuotaStatus(
                allowed=True,
                remaining=None,
                reset_at=None,
                tier=UserTier.PREMIUM
            )
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"ai_quota:{user_id}:{today}"
        
        current = await self.redis.get(key)
        current = int(current) if current else 0
        
        return QuotaStatus(
            allowed=current < self.FREE_TIER_DAILY_LIMIT,
            remaining=max(0, self.FREE_TIER_DAILY_LIMIT - current),
            reset_at=self._get_next_midnight_utc(),
            tier=UserTier.FREE
        )
```


### 3. Response Cache

**Location:** `backend/app/ai/response_cache.py`

**Responsibilities:**
- Cache AI responses in Redis
- Generate cache keys from request parameters
- Manage TTL (7 days)
- Track cache hit rates

**Architecture:**

```python
class ResponseCache:
    """Redis-based response caching"""
    
    TTL_DAYS = 7
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = self.TTL_DAYS * 24 * 60 * 60  # seconds
    
    def build_key(
        self,
        request_type: AIRequestType,
        params: Dict[str, Any]
    ) -> str:
        """Build cache key from request"""
        
        # Normalize params (sort, lowercase, remove user-specific data)
        normalized = self._normalize_params(params)
        
        # Create hash
        param_str = json.dumps(normalized, sort_keys=True)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        
        return f"ai_cache:{request_type.value}:{param_hash}"
    
    async def get(self, cache_key: str) -> Optional[AIResponse]:
        """Get cached response"""
        
        data = await self.redis.get(cache_key)
        if data:
            return AIResponse.parse_raw(data)
        return None
    
    async def set(
        self,
        cache_key: str,
        response: AIResponse,
        ttl: int = None
    ):
        """Cache response"""
        
        ttl = ttl or self.ttl
        await self.redis.setex(
            cache_key,
            ttl,
            response.json()
        )
    
    def _normalize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize params for consistent caching"""
        
        # Remove user-specific fields
        exclude_fields = {'user_id', 'request_id', 'timestamp'}
        normalized = {
            k: v.lower() if isinstance(v, str) else v
            for k, v in params.items()
            if k not in exclude_fields and v is not None
        }
        
        return normalized
```

### 4. REST API Endpoints

**Location:** `backend/app/api/v1/endpoints/ai.py`

**Endpoint:** `POST /api/v1/ai/generate`

**Request Schema:**

```python
class AIGenerateRequest(BaseModel):
    """Unified AI generation request"""
    
    request_type: AIRequestType  # Enum: title, description, caption, etc.
    params: Dict[str, Any]       # Type-specific parameters
    
    # Example for title generation:
    # {
    #   "request_type": "title",
    #   "params": {
    #     "genre": "afrobeats",
    #     "mood": "energetic",
    #     "bpm": 120,
    #     "instruments": ["drums", "bass", "synth"]
    #   }
    # }
```

