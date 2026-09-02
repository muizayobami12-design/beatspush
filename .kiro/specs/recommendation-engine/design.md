# Design Document: BeatPush Recommendation Engine

## 1. Introduction

### 1.1 Overview

The BeatPush Recommendation Engine is a sophisticated, high-performance content recommendation system designed to deliver personalized beat and artist suggestions to users. The system employs a hybrid approach combining collaborative filtering, content-based filtering, and behavioral analytics to generate relevant recommendations with sub-200ms response times while supporting 1000+ concurrent users.

### 1.2 Design Goals

- **Performance**: Sub-200ms response time for all recommendation requests
- **Scalability**: Support 1000+ concurrent users with efficient caching
- **Personalization**: Deliver relevant recommendations based on user behavior and preferences
- **Diversity**: Prevent filter bubbles through diversity constraints and exploration
- **Regional Awareness**: Support Nigerian/African music preferences with regional boosting
- **Cold Start Handling**: Provide quality recommendations for new users and beats
- **Real-time Processing**: Process user signals within 5 seconds for fresh recommendations
- **Quality Filtering**: Exclude low-quality and problematic content automatically

### 1.3 Key Features

1. **Personalized Beat Recommendations** - Hybrid scoring combining collaborative and content-based filtering
2. **Artist/Producer Suggestions** - Discover new creators based on taste overlap and social signals
3. **Similar Beats** - Find related music on beat detail pages
4. **Personalized Discover Feed** - Continuous stream of relevant music (50+ beats)
5. **Purchase-Based Suggestions** - "Customers also bought" recommendations
6. **Trending Beats by Genre** - Time-decay weighted trending with regional support
7. **Anonymous User Support** - Genre-based recommendations without authentication
8. **Real-time Signal Processing** - Immediate incorporation of user behavior

## 2. Architecture Overview

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Layer                             │
│  /api/recommendations/beats, /artists, /similar/{id}, /discover  │
│              /also-bought/{id}, /trending/{genre}                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  RecommendationService                            │
│  • Request routing & orchestration                                │
│  • Authentication & user context                                  │
│  • Response formatting & pagination                               │
│  • Performance monitoring & logging                               │
└───┬─────────────┬──────────────┬──────────────┬─────────────────┘
    │             │              │              │
    │     ┌───────▼────────┐    │      ┌───────▼───────┐
    │     │ CacheManager   │    │      │SignalProcessor │
    │     │ (Redis)        │    │      │ • Real-time    │
    │     │ • 5min TTL     │    │      │   events       │
    │     │ • Invalidation │    │      │ • Time decay   │
    │     │ • Warming      │    │      │   weights      │
    │     └────────────────┘    │      └────────────────┘
    │                            │
┌───▼─────────────┐   ┌─────────▼──────────┐   ┌──────────────────┐
│ Collaborative   │   │  ContentBased      │   │ TrendingService  │
│ Filter          │   │  Filter            │   │ • Time decay     │
│ • User-User CF  │   │  • Genre matching  │   │ • Genre-specific │
│ • Item-Item CF  │   │  • BPM similarity  │   │ • Regional       │
│ • Similarity    │   │  • Key/Mood match  │   │ • 15min refresh  │
│   matrix        │   │  • Tag overlap     │   └──────────────────┘
└───┬─────────────┘   └─────────┬──────────┘
    │                            │
    └──────────────┬─────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│                 PostgreSQL Database                               │
│  • User, Beat, BeatPlay, BeatFavorite, BeatPurchase, Follow     │
│  • Indexes on user_id, beat_id, created_at                       │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Description


#### **RecommendationService**
Main orchestration layer that:
- Routes incoming requests to appropriate sub-services
- Manages user authentication and context
- Applies hybrid scoring algorithms
- Enforces diversity constraints
- Handles pagination and response formatting
- Tracks performance metrics and logs

#### **CollaborativeFilter**
Implements collaborative filtering algorithms:
- **User-User CF**: Find similar users based on behavior overlap, recommend their favorites
- **Item-Item CF**: Find similar beats based on co-occurrence in user interactions
- Uses cosine similarity for user/item similarity calculation
- Pre-computes similarity matrices for top items to improve performance

#### **ContentBasedFilter**
Implements attribute-based filtering:
- Genre matching (40% weight)
- BPM similarity within ±10% range (20% weight)
- Musical key matching (15% weight)
- Mood matching (15% weight)
- Tag overlap (10% weight)
- Generates content vectors for beats and user preferences


#### **TrendingService**
Calculates and caches trending content:
- Aggregates engagement metrics (plays, purchases, favorites, shares)
- Applies time decay (50% weight reduction after 12 hours)
- Calculates trending scores: `plays(40%) + purchases(30%) + favorites(15%) + shares(15%)`
- Refreshes every 15 minutes via background job
- Supports genre-specific and regional trending

#### **CacheManager**
Redis-based caching layer:
- Stores recommendation results with 5-minute TTL
- Generates deterministic cache keys: `rec:{user_id}:{type}:{params_hash}`
- Invalidates cache on user behavior events (play, purchase, favorite)
- Implements cache warming for top 1000 active users every 4 minutes
- Tracks cache hit rates and alerts on < 80% hit rate
- Provides graceful fallback to database on cache failures

#### **SignalProcessor**
Real-time event processing:
- Processes user behavior events (plays, purchases, favorites) within 5 seconds
- Applies time-based weights:
  - Last 24 hours: 100% weight
  - 1-7 days: 50% weight
  - 7-30 days: 25% weight
  - >30 days: 10% weight
- Applies purchase recency boost (150% weight for 48 hours)
- Triggers cache invalidation


### 2.3 Data Flow

#### Personalized Beat Recommendations Flow
```
1. User requests recommendations
2. RecommendationService checks authentication
3. CacheManager checks for cached results
4. If cache miss:
   a. SignalProcessor retrieves user behavior with time weights
   b. CollaborativeFilter generates CF scores
   c. ContentBasedFilter generates CB scores
   d. RecommendationService applies hybrid scoring:
      - <5 interactions: CB(70%) + CF(30%)
      - ≥5 interactions: CF(60%) + CB(40%)
   e. Apply diversity constraints
   f. Apply quality filters (rating ≥3.0, active status)
   g. Exclude purchased beats
   h. Apply regional boosts (if applicable)
   i. CacheManager stores results (5min TTL)
5. Return top 20+ ranked results
```

#### Similar Beats Flow
```
1. User views beat detail page
2. ContentBasedFilter calculates attribute similarity
3. Apply personalization if authenticated (30% weight)
4. Apply same-artist boost (15%)
5. Exclude reference beat
6. Return top 8 similar beats
```


## 3. Data Models and Schemas

### 3.1 Existing Database Models (SQLAlchemy)

The recommendation engine leverages existing models:

```python
# Beat model - core content
class Beat(Base):
    id: String(36)
    producer_user_id: String(36)
    title: String(255)
    genre: String(100)
    bpm: Integer
    musical_key: String(10)
    mood: String(100)
    tags: Text  # Comma-separated
    play_count: Integer
    favorite_count: Integer
    purchase_count: Integer
    status: String(20)
    created_at: DateTime
    
# User behavior tracking
class BeatPlay(Base):
    id: String(36)
    beat_id: String(36)
    user_id: String(36)
    duration_played: Integer
    completed: Boolean
    created_at: DateTime

class BeatFavorite(Base):
    id: String(36)
    beat_id: String(36)
    user_id: String(36)
    created_at: DateTime

class BeatPurchase(Base):
    id: String(36)
    beat_id: String(36)
    buyer_user_id: String(36)
    created_at: DateTime

# Social graph
class Follow(Base):
    id: String(36)
    follower_id: String(36)
    following_id: String(36)
    created_at: DateTime
```


### 3.2 New Models for Recommendation Engine

```python
class UserPreferenceProfile(Base):
    """Aggregated user preference profile for faster recommendations"""
    __tablename__ = "user_preference_profiles"
    
    user_id = Column(String(36), primary_key=True)
    
    # Aggregated preferences (JSON)
    genre_weights = Column(JSON)  # {"Afrobeats": 0.35, "Hip-Hop": 0.25, ...}
    bpm_range = Column(JSON)  # {"min": 80, "max": 140, "preferred": 120}
    key_preferences = Column(JSON)  # ["C", "G", "D"]
    mood_preferences = Column(JSON)  # {"Energetic": 0.4, "Chill": 0.3, ...}
    
    # Interaction counts
    total_plays = Column(Integer, default=0)
    total_favorites = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    
    # Cold start indicator
    interaction_count = Column(Integer, default=0)
    
    # Regional preference
    region = Column(String(10))  # ISO country code
    
    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow)


class BeatSimilarityCache(Base):
    """Pre-computed similarity scores for popular beats"""
    __tablename__ = "beat_similarity_cache"
    
    source_beat_id = Column(String(36), primary_key=True)
    similar_beat_ids = Column(JSON)  # [{"beat_id": "...", "score": 0.85}, ...]
    algorithm = Column(String(20))  # "content", "collaborative"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


class TrendingBeatCache(Base):
    """Cached trending beats by genre and region"""
    __tablename__ = "trending_beat_cache"
    
    id = Column(String(36), primary_key=True)
    genre = Column(String(100), index=True)
    region = Column(String(10), index=True)  # "global" or ISO code
    
    beat_ids = Column(JSON)  # [{"beat_id": "...", "score": 0.92}, ...]
    
    # Calculation window
    window_start = Column(DateTime)
    window_end = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


class RecommendationLog(Base):
    """Logging and analytics for recommendations"""
    __tablename__ = "recommendation_logs"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), index=True)
    recommendation_type = Column(String(50), index=True)
    
    # Request details
    request_params = Column(JSON)
    response_time_ms = Column(Integer)
    cache_hit = Column(Boolean)
    
    # Returned recommendations
    beat_ids = Column(JSON)  # List of beat IDs returned
    
    # Engagement tracking
    clicked_beat_ids = Column(JSON)  # Updated when user clicks
    purchased_beat_ids = Column(JSON)  # Updated when user purchases
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
```


### 3.3 API Request/Response Schemas

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class RecommendationRequest(BaseModel):
    """Base recommendation request"""
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    region: Optional[str] = None  # ISO country code


class BeatRecommendation(BaseModel):
    """Individual beat recommendation"""
    beat_id: str
    title: str
    producer_name: str
    genre: str
    bpm: Optional[int]
    score: float = Field(ge=0.0, le=1.0)
    reason_codes: List[str]  # ["trending", "similar_genre", "followed_artist"]
    cover_art_url: Optional[str]


class RecommendationResponse(BaseModel):
    """Standard recommendation response"""
    recommendations: List[BeatRecommendation]
    total: int
    limit: int
    offset: int
    cache_hit: bool
    response_time_ms: int


class ArtistSuggestion(BaseModel):
    """Artist/producer suggestion"""
    user_id: str
    username: str
    full_name: str
    role: str
    follower_count: int
    beat_count: int
    score: float = Field(ge=0.0, le=1.0)
    reason_codes: List[str]
    profile_image_url: Optional[str]


class ArtistSuggestionResponse(BaseModel):
    """Artist suggestion response"""
    suggestions: List[ArtistSuggestion]
    total: int
    limit: int
    offset: int
```


## 4. Algorithm Specifications

### 4.1 Collaborative Filtering

#### User-User Collaborative Filtering

**Algorithm**: Cosine similarity between user behavior vectors

```python
def user_similarity(user_a: User, user_b: User) -> float:
    """Calculate cosine similarity between two users based on beat interactions"""
    # Build interaction vectors (beat_id -> interaction_score)
    vector_a = build_user_vector(user_a)
    vector_b = build_user_vector(user_b)
    
    # Interaction scores:
    # - Play: 1.0 (base)
    # - Favorite: 2.0
    # - Purchase: 5.0
    
    # Calculate cosine similarity
    dot_product = sum(vector_a[beat_id] * vector_b.get(beat_id, 0) 
                     for beat_id in vector_a)
    magnitude_a = sqrt(sum(v**2 for v in vector_a.values()))
    magnitude_b = sqrt(sum(v**2 for v in vector_b.values()))
    
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)


def user_user_recommendations(user: User, limit: int = 20) -> List[Beat]:
    """Generate recommendations using user-user CF"""
    # Find top 50 similar users
    similar_users = find_similar_users(user, limit=50)
    
    # Aggregate their favorites with similarity weights
    beat_scores = defaultdict(float)
    for similar_user, similarity in similar_users:
        for beat in similar_user.favorite_beats:
            if beat.id not in user.purchased_beats:
                beat_scores[beat.id] += similarity
    
    # Return top N beats
    return sorted(beat_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
```


#### Item-Item Collaborative Filtering

**Algorithm**: Co-occurrence based similarity

```python
def item_similarity(beat_a: Beat, beat_b: Beat) -> float:
    """Calculate similarity between two beats based on co-occurrence"""
    # Get users who interacted with beat_a
    users_a = set(get_beat_users(beat_a))
    
    # Get users who interacted with beat_b
    users_b = set(get_beat_users(beat_b))
    
    # Jaccard similarity
    intersection = len(users_a & users_b)
    union = len(users_a | users_b)
    
    if union == 0:
        return 0.0
    
    return intersection / union


def item_item_recommendations(user: User, limit: int = 20) -> List[Beat]:
    """Generate recommendations using item-item CF"""
    # Get user's recently interacted beats (last 10)
    recent_beats = get_user_recent_beats(user, limit=10)
    
    # For each beat, find similar beats
    beat_scores = defaultdict(float)
    for source_beat, interaction_weight in recent_beats:
        similar_beats = find_similar_beats(source_beat, limit=20)
        for beat, similarity in similar_beats:
            if beat.id not in user.purchased_beats:
                beat_scores[beat.id] += similarity * interaction_weight
    
    # Return top N beats
    return sorted(beat_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
```

### 4.2 Content-Based Filtering

```python
def calculate_content_similarity(beat: Beat, user_profile: UserPreferenceProfile) -> float:
    """Calculate content-based similarity between beat and user preferences"""
    score = 0.0
    
    # Genre matching (40% weight)
    if beat.genre in user_profile.genre_weights:
        genre_score = user_profile.genre_weights[beat.genre]
        score += 0.40 * genre_score
    
    # BPM similarity (20% weight)
    if user_profile.bpm_range:
        bpm_min = user_profile.bpm_range['min']
        bpm_max = user_profile.bpm_range['max']
        bpm_preferred = user_profile.bpm_range['preferred']
        
        if bpm_min <= beat.bpm <= bpm_max:
            # Within acceptable range
            bpm_distance = abs(beat.bpm - bpm_preferred)
            bpm_range = bpm_max - bpm_min
            bpm_score = 1.0 - (bpm_distance / bpm_range) if bpm_range > 0 else 1.0
            score += 0.20 * bpm_score
    
    # Key matching (15% weight)
    if beat.musical_key in user_profile.key_preferences:
        score += 0.15
    
    # Mood matching (15% weight)
    if beat.mood in user_profile.mood_preferences:
        mood_score = user_profile.mood_preferences[beat.mood]
        score += 0.15 * mood_score
    
    # Tag overlap (10% weight)
    beat_tags = set(beat.tags.split(',')) if beat.tags else set()
    user_tags = set(user_profile.tag_preferences.keys()) if hasattr(user_profile, 'tag_preferences') else set()
    if beat_tags and user_tags:
        tag_overlap = len(beat_tags & user_tags) / len(beat_tags | user_tags)
        score += 0.10 * tag_overlap
    
    return min(score, 1.0)  # Cap at 1.0
```


### 4.3 Hybrid Scoring Algorithm

```python
def calculate_hybrid_score(
    beat: Beat,
    user: User,
    cf_score: float,
    cb_score: float,
    user_profile: UserPreferenceProfile
) -> float:
    """Combine collaborative and content-based scores with adaptive weighting"""
    
    # Determine weights based on user interaction count
    if user_profile.interaction_count < 5:
        # Cold start: favor content-based
        cf_weight = 0.30
        cb_weight = 0.70
    else:
        # Established user: favor collaborative
        cf_weight = 0.60
        cb_weight = 0.40
    
    # Base hybrid score
    hybrid_score = (cf_weight * cf_score) + (cb_weight * cb_score)
    
    # Apply quality boosts/penalties
    if beat.play_through_rate > 0.70:
        hybrid_score *= 1.15  # 15% boost for high completion rate
    
    if beat.bounce_rate > 0.80:
        hybrid_score *= 0.80  # 20% penalty for high bounce rate
    
    # Apply diversity boost
    if is_underrepresented_genre(beat.genre, user_profile):
        hybrid_score *= 1.10  # 10% boost for diversity
    
    # Apply regional boost
    if user_profile.region in ['NG', 'GH', 'KE', 'ZA']:  # African countries
        if beat.genre in ['Afrobeats', 'Afropop', 'Amapiano']:
            hybrid_score *= 1.20  # 20% boost for regional content
    
    # Apply same-artist boost (for similar beats only)
    # This would be handled by the calling context
    
    return min(hybrid_score, 1.0)  # Cap at 1.0
```

### 4.4 Trending Score Calculation

```python
def calculate_trending_score(beat: Beat, window_hours: int = 24) -> float:
    """Calculate trending score with time decay"""
    now = datetime.utcnow()
    window_start = now - timedelta(hours=window_hours)
    
    # Get engagement metrics in time window
    plays = count_plays(beat, window_start, now)
    purchases = count_purchases(beat, window_start, now)
    favorites = count_favorites(beat, window_start, now)
    shares = count_shares(beat, window_start, now)
    
    # Apply time decay (50% reduction after 12 hours)
    decay_threshold = now - timedelta(hours=12)
    
    def apply_decay(events: List[Event]) -> float:
        score = 0.0
        for event in events:
            if event.created_at >= decay_threshold:
                score += 1.0  # Full weight
            else:
                score += 0.5  # 50% weight
        return score
    
    decayed_plays = apply_decay(plays)
    decayed_purchases = apply_decay(purchases)
    decayed_favorites = apply_decay(favorites)
    decayed_shares = apply_decay(shares)
    
    # Weighted trending score
    trending_score = (
        0.40 * decayed_plays +
        0.30 * decayed_purchases +
        0.15 * decayed_favorites +
        0.15 * decayed_shares
    )
    
    # Normalize by max possible score in window
    max_score = 100  # Assuming max engagement
    return min(trending_score / max_score, 1.0)
```


### 4.5 Diversity Enforcement

```python
def enforce_diversity_constraints(
    candidates: List[Tuple[Beat, float]],
    user: User,
    limit: int = 20
) -> List[Tuple[Beat, float]]:
    """Apply diversity constraints to recommendations"""
    
    # Track diversity metrics
    selected = []
    artist_counts = defaultdict(int)
    genre_counts = defaultdict(int)
    new_artist_count = 0
    
    # User's previously interacted artists
    known_artists = set(get_user_artists(user))
    
    # Sort candidates by score
    sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
    
    for beat, score in sorted_candidates:
        if len(selected) >= limit:
            break
        
        # Check artist representation (max 15%)
        max_per_artist = max(3, int(limit * 0.15))
        if artist_counts[beat.producer_user_id] >= max_per_artist:
            continue
        
        # Select the beat
        selected.append((beat, score))
        artist_counts[beat.producer_user_id] += 1
        genre_counts[beat.genre] += 1
        
        if beat.producer_user_id not in known_artists:
            new_artist_count += 1
    
    # Verify constraints
    assert len(selected) >= limit, "Not enough diverse candidates"
    assert new_artist_count >= int(limit * 0.40), "Insufficient new artist representation"
    assert len(genre_counts) >= 3 or len(selected) < 20, "Insufficient genre diversity"
    
    return selected
```

### 4.6 Time-Based Weighting for User Behavior

```python
def calculate_event_weight(event_date: datetime) -> float:
    """Calculate time-based weight for user behavior events"""
    now = datetime.utcnow()
    age_days = (now - event_date).days
    
    if age_days < 1:
        return 1.00  # Last 24 hours: 100%
    elif age_days <= 7:
        return 0.50  # 1-7 days: 50%
    elif age_days <= 30:
        return 0.25  # 7-30 days: 25%
    else:
        return 0.10  # >30 days: 10%


def calculate_purchase_weight(purchase_date: datetime) -> float:
    """Calculate weight for purchases with recency boost"""
    base_weight = calculate_event_weight(purchase_date)
    
    # Apply 150% boost for purchases within 48 hours
    now = datetime.utcnow()
    age_hours = (now - purchase_date).total_seconds() / 3600
    
    if age_hours <= 48:
        return base_weight * 1.50  # 150% of base weight
    
    return base_weight
```


## 5. Service Implementation Details

### 5.1 RecommendationService Class

```python
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

class RecommendationService:
    """Main orchestration service for recommendations"""
    
    def __init__(
        self,
        db: Session,
        cache_manager: CacheManager,
        collaborative_filter: CollaborativeFilter,
        content_filter: ContentBasedFilter,
        trending_service: TrendingService,
        signal_processor: SignalProcessor
    ):
        self.db = db
        self.cache = cache_manager
        self.cf = collaborative_filter
        self.cb = content_filter
        self.trending = trending_service
        self.signals = signal_processor
    
    async def get_beat_recommendations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        region: Optional[str] = None
    ) -> RecommendationResponse:
        """Get personalized beat recommendations"""
        start_time = time.time()
        
        # Check cache
        cache_key = f"rec:{user_id}:beats:{limit}:{offset}:{region}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Load user and profile
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = self._load_or_create_profile(user)
        
        # Get candidate beats
        cf_candidates = await self.cf.get_recommendations(user, profile, limit=100)
        cb_candidates = await self.cb.get_recommendations(user, profile, limit=100)
        
        # Calculate hybrid scores
        hybrid_scores = []
        for beat_id in set(cf_candidates.keys()) | set(cb_candidates.keys()):
            beat = self.db.query(Beat).filter(Beat.id == beat_id).first()
            if not beat or not self._passes_quality_filters(beat):
                continue
            
            cf_score = cf_candidates.get(beat_id, 0.0)
            cb_score = cb_candidates.get(beat_id, 0.0)
            
            score = calculate_hybrid_score(beat, user, cf_score, cb_score, profile)
            hybrid_scores.append((beat, score))
        
        # Apply diversity constraints
        diverse_results = enforce_diversity_constraints(hybrid_scores, user, limit)
        
        # Exclude purchased beats
        recommendations = [
            (beat, score) for beat, score in diverse_results
            if beat.id not in self._get_purchased_beat_ids(user)
        ][:limit]
        
        # Format response
        response = self._format_response(recommendations, start_time)
        
        # Cache results
        await self.cache.set(cache_key, response, ttl=300)  # 5 minutes
        
        return response
    
    def _passes_quality_filters(self, beat: Beat) -> bool:
        """Check if beat meets quality requirements"""
        # Exclude inactive/deleted
        if beat.status != "active":
            return False
        
        # Check rating (use platform average if <5 ratings)
        if beat.rating_count >= 5:
            if beat.average_rating < 3.0:
                return False
        
        # Exclude copyright flagged
        if getattr(beat, 'copyright_flagged', False):
            return False
        
        return True
```


### 5.2 CacheManager Class

```python
import redis
import json
from typing import Optional, Any

class CacheManager:
    """Redis-based caching for recommendations"""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutes
        self.hit_count = 0
        self.miss_count = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            value = self.redis.get(key)
            if value:
                self.hit_count += 1
                return json.loads(value)
            self.miss_count += 1
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.miss_count += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Set cached value with TTL"""
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user"""
        try:
            # Get all keys matching pattern
            pattern = f"rec:{user_id}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    async def warm_cache(self, user_ids: List[str]):
        """Pre-warm cache for active users"""
        for user_id in user_ids:
            try:
                # Generate recommendations without checking cache
                # This would call the service directly
                pass
            except Exception as e:
                logger.error(f"Cache warming error for user {user_id}: {e}")
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total
    
    def log_hit_rate(self):
        """Log cache hit rate and alert if low"""
        hit_rate = self.get_hit_rate()
        logger.info(f"Cache hit rate: {hit_rate:.2%}")
        
        if hit_rate < 0.80:
            logger.warning(f"Cache hit rate below 80%: {hit_rate:.2%}")
```

### 5.3 SignalProcessor Class

```python
from datetime import datetime, timedelta

class SignalProcessor:
    """Process real-time user behavior signals"""
    
    def __init__(self, db: Session, cache_manager: CacheManager):
        self.db = db
        self.cache = cache_manager
    
    async def process_play_event(self, user_id: str, beat_id: str, completed: bool):
        """Process beat play event"""
        # Create play record
        play = BeatPlay(
            id=str(uuid.uuid4()),
            user_id=user_id,
            beat_id=beat_id,
            completed=completed,
            created_at=datetime.utcnow()
        )
        self.db.add(play)
        self.db.commit()
        
        # Update user profile
        await self._update_user_profile(user_id)
        
        # Invalidate cache
        await self.cache.invalidate_user_cache(user_id)
    
    async def process_purchase_event(self, user_id: str, beat_id: str):
        """Process beat purchase event"""
        # Invalidate cache (purchases affect recommendations)
        await self.cache.invalidate_user_cache(user_id)
        
        # Update user profile with purchase boost
        await self._update_user_profile(user_id)
    
    def get_weighted_user_behavior(self, user_id: str) -> List[Tuple[str, float]]:
        """Get user behavior events with time-based weights"""
        events = []
        
        # Get plays
        plays = self.db.query(BeatPlay).filter(
            BeatPlay.user_id == user_id
        ).all()
        
        for play in plays:
            weight = calculate_event_weight(play.created_at)
            events.append((play.beat_id, weight * 1.0))  # Base play weight
        
        # Get favorites
        favorites = self.db.query(BeatFavorite).filter(
            BeatFavorite.user_id == user_id
        ).all()
        
        for fav in favorites:
            weight = calculate_event_weight(fav.created_at)
            events.append((fav.beat_id, weight * 2.0))  # 2x weight for favorites
        
        # Get purchases
        purchases = self.db.query(BeatPurchase).filter(
            BeatPurchase.buyer_user_id == user_id
        ).all()
        
        for purchase in purchases:
            weight = calculate_purchase_weight(purchase.created_at)
            events.append((purchase.beat_id, weight * 5.0))  # 5x base weight
        
        return events
```


## 6. API Endpoint Specifications

### 6.1 Personalized Beat Recommendations

```
GET /api/recommendations/beats
```

**Authentication**: Required

**Query Parameters**:
- `limit` (integer, optional): Number of results (default: 20, max: 100)
- `offset` (integer, optional): Pagination offset (default: 0)
- `region` (string, optional): ISO country code for regional preferences

**Response** (200 OK):
```json
{
  "recommendations": [
    {
      "beat_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Midnight Vibes",
      "producer_name": "DJ KayKay",
      "genre": "Afrobeats",
      "bpm": 128,
      "score": 0.92,
      "reason_codes": ["similar_genre", "followed_artist", "trending"],
      "cover_art_url": "https://..."
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0,
  "cache_hit": true,
  "response_time_ms": 45
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing authentication token
- `429 Too Many Requests`: Rate limit exceeded (10 req/min)

### 6.2 Artist Suggestions

```
GET /api/recommendations/artists
```

**Authentication**: Required

**Query Parameters**:
- `limit` (integer, optional): Number of results (default: 10, max: 50)
- `offset` (integer, optional): Pagination offset (default: 0)
- `region` (string, optional): ISO country code

**Response** (200 OK):
```json
{
  "suggestions": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "dj_kayway",
      "full_name": "DJ KayKay",
      "role": "producer",
      "follower_count": 1250,
      "beat_count": 45,
      "score": 0.88,
      "reason_codes": ["similar_taste", "trending_creator", "regional"],
      "profile_image_url": "https://..."
    }
  ],
  "total": 50,
  "limit": 10,
  "offset": 0
}
```


### 6.3 Similar Beats

```
GET /api/recommendations/similar/{beat_id}
```

**Authentication**: Optional (personalized if authenticated)

**Path Parameters**:
- `beat_id` (string, required): Beat identifier

**Query Parameters**:
- `limit` (integer, optional): Number of results (default: 8, max: 20)

**Response** (200 OK):
```json
{
  "recommendations": [
    {
      "beat_id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Urban Dreams",
      "producer_name": "ProducerX",
      "genre": "Afrobeats",
      "bpm": 125,
      "score": 0.89,
      "reason_codes": ["same_genre", "similar_bpm", "same_artist"],
      "cover_art_url": "https://..."
    }
  ],
  "total": 8,
  "limit": 8,
  "offset": 0,
  "cache_hit": false,
  "response_time_ms": 67
}
```

**Error Responses**:
- `404 Not Found`: Beat ID does not exist

### 6.4 Discover Feed

```
GET /api/recommendations/discover
```

**Authentication**: Required

**Query Parameters**:
- `limit` (integer, optional): Number of results (default: 50, max: 100)
- `offset` (integer, optional): Pagination offset
- `region` (string, optional): ISO country code

**Response** (200 OK):
```json
{
  "recommendations": [...],
  "composition": {
    "trending": 10,
    "followed_artists": 8,
    "collaborative": 20,
    "content_based": 12
  },
  "total": 200,
  "limit": 50,
  "offset": 0,
  "cache_hit": true,
  "response_time_ms": 52
}
```


### 6.5 Customers Also Bought

```
GET /api/recommendations/also-bought/{beat_id}
```

**Authentication**: Optional

**Path Parameters**:
- `beat_id` (string, required): Beat identifier

**Query Parameters**:
- `limit` (integer, optional): Number of results (default: 6, max: 20)

**Response** (200 OK):
```json
{
  "recommendations": [...],
  "fallback_to_similar": false,
  "purchase_count": 45,
  "total": 6,
  "limit": 6,
  "offset": 0
}
```

**Behavior**:
- If beat has <10 purchases, falls back to similar beats algorithm
- Sets `fallback_to_similar: true` in response

### 6.6 Trending Beats by Genre

```
GET /api/recommendations/trending/{genre}
```

**Authentication**: Optional

**Path Parameters**:
- `genre` (string, required): Genre name (e.g., "Afrobeats", "Hip-Hop")

**Query Parameters**:
- `limit` (integer, optional): Number of results (default: 20, max: 50)
- `region` (string, optional): ISO country code

**Response** (200 OK):
```json
{
  "recommendations": [...],
  "genre": "Afrobeats",
  "window": "24h",
  "regional_section": "Trending in Nigeria",
  "total": 20,
  "limit": 20,
  "offset": 0,
  "cache_hit": true,
  "response_time_ms": 38
}
```


## 7. Performance Optimization

### 7.1 Caching Strategy

**Three-Tier Caching**:

1. **Redis Cache** (L1):
   - TTL: 5 minutes for personalized recommendations
   - TTL: 15 minutes for trending beats
   - Keys: `rec:{user_id}:{type}:{params_hash}`
   - Invalidation: On user behavior events

2. **Database Materialized Views** (L2):
   - Pre-computed similarity matrices for top 10,000 beats
   - Pre-aggregated trending scores (refreshed every 15min)
   - User preference profiles (updated on events)

3. **In-Memory Cache** (L3):
   - Hot data: Top 1000 beats metadata
   - Genre mappings
   - Active user sessions

**Cache Warming**:
- Background job runs every 4 minutes
- Targets top 1000 active users (by recent activity)
- Pre-generates recommendations before cache expiry
- Prevents cache stampede during high traffic

### 7.2 Database Optimization

**Indexes**:
```sql
-- User behavior queries
CREATE INDEX idx_beat_plays_user_created ON beat_plays(user_id, created_at DESC);
CREATE INDEX idx_beat_favorites_user ON beat_favorites(user_id);
CREATE INDEX idx_beat_purchases_buyer ON beat_purchases(buyer_user_id);

-- Beat queries
CREATE INDEX idx_beats_genre_status ON beats(genre, status) WHERE status = 'active';
CREATE INDEX idx_beats_created ON beats(created_at DESC) WHERE status = 'active';

-- Collaborative filtering
CREATE INDEX idx_beat_plays_beat_user ON beat_plays(beat_id, user_id);
CREATE INDEX idx_beat_purchases_beat ON beat_purchases(beat_id) WHERE status = 'completed';

-- Trending calculations
CREATE INDEX idx_beat_plays_created ON beat_plays(created_at DESC) WHERE created_at > NOW() - INTERVAL '24 hours';
```

**Query Optimization**:
- Use `LIMIT` and `OFFSET` for pagination
- Fetch only required columns (avoid `SELECT *`)
- Use `JOIN` instead of N+1 queries
- Implement query timeouts (150ms threshold)


### 7.3 Load Shedding and Circuit Breaker

**Load Shedding**:
```python
class LoadShedder:
    def __init__(self, capacity_threshold: float = 0.80):
        self.threshold = capacity_threshold
    
    async def should_shed_load(self) -> bool:
        """Check if system is over capacity"""
        # Check CPU, memory, active connections
        system_load = await get_system_load()
        return system_load > self.threshold
    
    async def handle_request(self, request_fn):
        """Handle request with load shedding"""
        if await self.should_shed_load():
            # Prioritize cached results
            cached = await self.cache.get_any_cached_result()
            if cached:
                return cached
            # Or return fallback (trending beats)
            return await self.get_trending_fallback()
        
        return await request_fn()
```

**Circuit Breaker**:
```python
class CircuitBreaker:
    def __init__(self, failure_threshold: float = 0.50, window_seconds: int = 60):
        self.threshold = failure_threshold
        self.window = window_seconds
        self.failures = deque()
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, fn):
        """Execute function with circuit breaker"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = await fn()
            if self.state == "half-open":
                self.state = "closed"
                self.failures.clear()
            return result
        except Exception as e:
            self._record_failure()
            if self._should_trip():
                self.state = "open"
            raise
```

### 7.4 Rate Limiting

```python
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/recommendations/beats")
@limiter.limit("10/minute")
async def get_beat_recommendations(request: Request, ...):
    """Rate limited to 10 requests per user per minute"""
    pass
```


## 8. Error Handling and Resilience

### 8.1 Graceful Degradation

**Fallback Chain**:
1. Try Redis cache
2. If cache miss, compute recommendations
3. If database slow (>150ms), return cached fallback
4. If computation fails, return trending beats
5. If all fails, return empty results with error message

```python
async def get_recommendations_with_fallback(user_id: str):
    """Get recommendations with graceful degradation"""
    try:
        # Try cache
        cached = await cache.get(f"rec:{user_id}:beats")
        if cached:
            return cached
        
        # Try computation with timeout
        async with timeout(0.15):  # 150ms threshold
            recommendations = await compute_recommendations(user_id)
            return recommendations
    
    except asyncio.TimeoutError:
        # Database too slow, return cached fallback
        logger.warning(f"Timeout for user {user_id}, using fallback")
        return await get_cached_fallback(user_id)
    
    except Exception as e:
        # Computation failed, return trending
        logger.error(f"Recommendation failed for {user_id}: {e}")
        return await get_trending_fallback()
```

### 8.2 Error Response Format

```json
{
  "error": {
    "code": "COMPUTATION_TIMEOUT",
    "message": "Recommendation computation exceeded time limit",
    "fallback_used": true
  },
  "recommendations": [...],
  "total": 20,
  "limit": 20,
  "offset": 0
}
```

### 8.3 Monitoring and Alerting

**Metrics to Track**:
- Response time (p50, p95, p99)
- Cache hit rate
- Error rate
- Recommendation diversity metrics
- Database query times
- User engagement (CTR, conversion rate)

**Alert Conditions**:
- p95 response time > 200ms
- Cache hit rate < 80%
- Error rate > 5%
- Single-artist representation > 20%
- Database query time > 150ms

**Logging**:
```python
logger.info(
    "Recommendation request",
    extra={
        "user_id": user_id,
        "type": "beats",
        "response_time_ms": elapsed_ms,
        "cache_hit": cache_hit,
        "result_count": len(recommendations)
    }
)
```


## 9. Background Jobs

### 9.1 Trending Score Calculation Job

**Schedule**: Every 15 minutes

```python
from celery import Celery
from celery.schedules import crontab

@celery.task
def calculate_trending_scores():
    """Calculate trending scores for all genres and regions"""
    genres = ["Afrobeats", "Hip-Hop", "R&B", "Afropop", "Amapiano", "Trap"]
    regions = ["global", "NG", "GH", "KE", "ZA", "US", "GB"]
    
    for genre in genres:
        for region in regions:
            # Calculate trending beats
            trending_beats = calculate_genre_trending(genre, region, window_hours=24)
            
            # Store in cache
            cache_entry = TrendingBeatCache(
                id=str(uuid.uuid4()),
                genre=genre,
                region=region,
                beat_ids=trending_beats,
                window_start=datetime.utcnow() - timedelta(hours=24),
                window_end=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=15)
            )
            db.add(cache_entry)
    
    db.commit()
    logger.info("Trending scores calculated")
```

### 9.2 Cache Warming Job

**Schedule**: Every 4 minutes

```python
@celery.task
def warm_recommendation_cache():
    """Pre-warm cache for top active users"""
    # Get top 1000 active users (by recent activity)
    active_users = db.query(User).join(BeatPlay).filter(
        BeatPlay.created_at > datetime.utcnow() - timedelta(hours=24)
    ).group_by(User.id).order_by(
        func.count(BeatPlay.id).desc()
    ).limit(1000).all()
    
    for user in active_users:
        try:
            # Generate recommendations (will cache automatically)
            await recommendation_service.get_beat_recommendations(
                user_id=user.id,
                limit=20
            )
        except Exception as e:
            logger.error(f"Cache warming failed for user {user.id}: {e}")
    
    logger.info(f"Cache warmed for {len(active_users)} users")
```

### 9.3 User Profile Update Job

**Schedule**: Every 1 hour

```python
@celery.task
def update_user_profiles():
    """Update user preference profiles based on recent behavior"""
    # Get users with activity in last 7 days
    recent_users = db.query(User).join(BeatPlay).filter(
        BeatPlay.created_at > datetime.utcnow() - timedelta(days=7)
    ).distinct().all()
    
    for user in recent_users:
        profile = calculate_user_preference_profile(user)
        
        # Update or create profile
        existing = db.query(UserPreferenceProfile).filter(
            UserPreferenceProfile.user_id == user.id
        ).first()
        
        if existing:
            existing.genre_weights = profile.genre_weights
            existing.bpm_range = profile.bpm_range
            existing.key_preferences = profile.key_preferences
            existing.mood_preferences = profile.mood_preferences
            existing.interaction_count = profile.interaction_count
            existing.updated_at = datetime.utcnow()
        else:
            db.add(profile)
    
    db.commit()
    logger.info(f"Updated profiles for {len(recent_users)} users")
```


### 9.4 Similarity Matrix Pre-computation Job

**Schedule**: Daily at 3 AM

```python
@celery.task
def precompute_beat_similarities():
    """Pre-compute similarity scores for popular beats"""
    # Get top 10,000 most popular beats
    popular_beats = db.query(Beat).filter(
        Beat.status == "active",
        Beat.play_count > 100
    ).order_by(Beat.play_count.desc()).limit(10000).all()
    
    for beat in popular_beats:
        # Calculate item-item similarity
        similar_beats = calculate_item_similarities(beat, limit=50)
        
        # Store in cache
        cache_entry = BeatSimilarityCache(
            source_beat_id=beat.id,
            similar_beat_ids=similar_beats,
            algorithm="collaborative",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        db.merge(cache_entry)
    
    db.commit()
    logger.info(f"Pre-computed similarities for {len(popular_beats)} beats")
```

## 10. Testing Strategy

### 10.1 Unit Tests

Focus on pure functions and business logic:
- Similarity calculation functions
- Scoring algorithms
- Time decay functions
- Diversity enforcement logic
- Quality filtering rules

Example:
```python
def test_calculate_event_weight():
    """Test time-based event weighting"""
    now = datetime.utcnow()
    
    # Last 24 hours: 100%
    recent = now - timedelta(hours=12)
    assert calculate_event_weight(recent) == 1.0
    
    # 1-7 days: 50%
    week_old = now - timedelta(days=3)
    assert calculate_event_weight(week_old) == 0.5
    
    # 7-30 days: 25%
    month_old = now - timedelta(days=15)
    assert calculate_event_weight(month_old) == 0.25
    
    # >30 days: 10%
    old = now - timedelta(days=45)
    assert calculate_event_weight(old) == 0.1
```


### 10.2 Integration Tests

Test API endpoints and service integration:
- Authentication and authorization
- Request/response formats
- Error handling
- Cache behavior
- Database queries
- Rate limiting

Example:
```python
async def test_beat_recommendations_endpoint(client, auth_token):
    """Test beat recommendations API"""
    response = await client.get(
        "/api/recommendations/beats?limit=20",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["recommendations"]) >= 20
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert "response_time_ms" in data
    
    # Verify scores are in descending order
    scores = [r["score"] for r in data["recommendations"]]
    assert scores == sorted(scores, reverse=True)
```

### 10.3 Property-Based Tests

Test universal properties across many inputs:
- Recommendations always exclude purchased beats
- Diversity constraints are always satisfied
- Quality filters are always applied
- Scores are always in [0.0, 1.0] range
- No single artist exceeds 15% representation

Example using Hypothesis:
```python
from hypothesis import given, strategies as st

@given(
    user_interactions=st.lists(st.tuples(st.uuids(), st.floats(0, 1)), min_size=5),
    limit=st.integers(min_value=10, max_value=50)
)
def test_diversity_constraints(user_interactions, limit):
    """Test that diversity constraints are always satisfied"""
    recommendations = generate_recommendations(user_interactions, limit)
    
    # Count artists
    artist_counts = Counter(r.producer_user_id for r in recommendations)
    
    # No single artist should exceed 15%
    max_per_artist = int(limit * 0.15)
    for count in artist_counts.values():
        assert count <= max_per_artist
    
    # At least 3 different genres (if limit >= 20)
    if limit >= 20:
        genres = set(r.genre for r in recommendations)
        assert len(genres) >= 3
```


### 10.4 Performance Tests

Verify sub-200ms response times and concurrency handling:

```python
import asyncio
import time

async def test_response_time_under_load():
    """Test that response times stay under 200ms with 1000 concurrent users"""
    async def make_request():
        start = time.time()
        response = await client.get("/api/recommendations/beats")
        elapsed_ms = (time.time() - start) * 1000
        return elapsed_ms
    
    # Simulate 1000 concurrent requests
    tasks = [make_request() for _ in range(1000)]
    response_times = await asyncio.gather(*tasks)
    
    # Check p95 response time
    p95 = sorted(response_times)[int(len(response_times) * 0.95)]
    assert p95 < 200, f"P95 response time {p95}ms exceeds 200ms threshold"
    
    # Check average response time
    avg = sum(response_times) / len(response_times)
    assert avg < 100, f"Average response time {avg}ms is too high"
```

## 11. Deployment and Infrastructure

### 11.1 Infrastructure Requirements

**Application Servers**:
- 3+ FastAPI instances behind load balancer
- Horizontal auto-scaling based on CPU (>70%) or request rate
- Health check endpoint: `/health`

**Redis Cluster**:
- 3-node Redis cluster for high availability
- Persistent storage enabled (RDB snapshots)
- Memory: 8GB minimum per node
- Eviction policy: `allkeys-lru`

**Database**:
- PostgreSQL 14+ with replication
- Connection pooling (PgBouncer)
- Read replicas for analytics queries

**Background Workers**:
- Celery workers for background jobs
- Separate queues: `trending`, `cache_warming`, `profiles`
- 5+ worker instances

### 11.2 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/beatpush
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://host:6379/0
REDIS_MAX_CONNECTIONS=50

# Celery
CELERY_BROKER_URL=redis://host:6379/1
CELERY_RESULT_BACKEND=redis://host:6379/2

# Recommendation Settings
REC_CACHE_TTL_SECONDS=300
REC_TRENDING_TTL_SECONDS=900
REC_CACHE_WARMING_USERS=1000
REC_MAX_CONCURRENT_REQUESTS=1000

# Performance
REC_RESPONSE_TIMEOUT_MS=200
REC_DB_QUERY_TIMEOUT_MS=150
REC_RATE_LIMIT_PER_MINUTE=10

# Features
REC_ENABLE_REGIONAL_BOOST=true
REC_ENABLE_DIVERSITY_CONSTRAINTS=true
REC_NIGERIAN_BOOST_PERCENT=20
```


## 12. Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Recommendation Output Size and Ordering

*For any* authenticated user requesting beat recommendations, the system should return at least the requested number of beats (up to the limit), and all returned beats should be ordered by score in descending order.

**Validates: Requirements 1.1, 2.1, 3.1, 4.1, 5.3, 6.1, 7.2**

### Property 2: Purchased Beat Exclusion

*For any* authenticated user with purchase history, none of the recommended beats should be beats the user has already purchased.

**Validates: Requirements 1.4**

### Property 3: Followed Artist Exclusion

*For any* authenticated user requesting artist suggestions, none of the suggested artists should be artists the user already follows.

**Validates: Requirements 2.4**

### Property 4: Self-Reference Exclusion

*For any* beat used as a reference for similar beats or also-bought suggestions, that beat should never appear in its own recommendation list.

**Validates: Requirements 3.3, 5.4**

### Property 5: Quality Filter Enforcement

*For any* recommendation set, all beats should have an average rating of at least 3.0 stars (or use platform average if fewer than 5 ratings), be in active status, and not be flagged for copyright issues.

**Validates: Requirements 13.1, 13.2, 13.3**


### Property 6: Artist Diversity Constraint

*For any* recommendation set of 20 or more beats, no single artist should represent more than 15% of the results.

**Validates: Requirements 9.2**

### Property 7: New Artist Representation

*For any* authenticated user requesting beat recommendations, at least 40% of the recommended beats should be from artists the user has not previously interacted with.

**Validates: Requirements 9.1**

### Property 8: Genre Diversity Constraint

*For any* recommendation set of 20 or more beats, at least 3 different genres should be represented.

**Validates: Requirements 9.3**

### Property 9: Time-Based Event Weighting

*For any* user behavior event, the weight applied should match the specified time decay formula:
- Events <24 hours old: 100% weight
- Events 1-7 days old: 50% weight
- Events 7-30 days old: 25% weight
- Events >30 days old: 10% weight

**Validates: Requirements 10.2, 10.3, 10.4, 10.5**

### Property 10: Purchase Recency Boost

*For any* purchase event less than 48 hours old, the weight applied should be 150% of the base time-weighted value.

**Validates: Requirements 10.7**


### Property 11: Cache Invalidation on User Events

*For any* user behavior event (play, purchase, favorite, cart addition), the affected user's recommendation cache entries should be invalidated.

**Validates: Requirements 8.3**

### Property 12: Cache Key Determinism

*For any* user and recommendation type with identical parameters, the cache key generated should be identical and deterministic.

**Validates: Requirements 8.2**

### Property 13: Trending Score Time Decay

*For any* beat with engagement events, events older than 12 hours should receive 50% weight reduction in trending score calculation.

**Validates: Requirements 6.4**

### Property 14: Artist Score Ordering

*For any* list of artist suggestions, the artists should be ordered by recommendation score in descending order.

**Validates: Requirements 2.1**

### Property 15: Hybrid Scoring Weight Adaptation

*For any* user, if the user has fewer than 5 interactions, content-based filtering should contribute 70% and collaborative filtering 30% to the hybrid score; otherwise, collaborative filtering should contribute 60% and content-based 40%.

**Validates: Requirements 1.5, 1.6**

### Property 16: Score Range Constraint

*For any* recommendation score (beat or artist), the score should be in the range [0.0, 1.0].

**Validates: Requirements 1.2, 2.2**


### Property 17: Artist Taste Overlap Correlation

*For any* user requesting artist suggestions, artists with greater overlap between the user's favorite beats and the artist's catalog should receive higher recommendation scores than artists with less overlap.

**Validates: Requirements 2.2**

### Property 18: Collaborative Purchase Correlation

*For any* beat with sufficient purchase history (≥10 purchases), the "customers also bought" recommendations should be based on analyzing co-purchases from users who bought the reference beat.

**Validates: Requirements 5.2**

## 13. Integration Points

### 13.1 WebSocket Integration

**Real-time Recommendation Updates**:
```python
# When new recommendations are generated
async def broadcast_recommendation_update(user_id: str):
    """Send real-time recommendation updates via WebSocket"""
    await websocket_manager.send_personal_message(
        user_id=user_id,
        message={
            "type": "recommendations_updated",
            "data": {
                "refresh_discover_feed": True,
                "new_trending_available": True
            }
        }
    )
```

### 13.2 Analytics Service Integration

```python
class AnalyticsIntegration:
    """Track recommendation metrics in analytics service"""
    
    async def track_recommendation_served(
        self,
        user_id: str,
        recommendation_type: str,
        beat_ids: List[str],
        response_time_ms: int
    ):
        """Log recommendation serving event"""
        await analytics_service.log_event(
            event_type="recommendation_served",
            user_id=user_id,
            properties={
                "type": recommendation_type,
                "beat_count": len(beat_ids),
                "response_time_ms": response_time_ms
            }
        )
    
    async def track_recommendation_click(
        self,
        user_id: str,
        beat_id: str,
        recommendation_type: str,
        position: int
    ):
        """Track when user clicks a recommendation"""
        await analytics_service.log_event(
            event_type="recommendation_click",
            user_id=user_id,
            properties={
                "beat_id": beat_id,
                "type": recommendation_type,
                "position": position
            }
        )
```


### 13.3 Authentication Service Integration

```python
from app.core.auth import get_current_user, Optional

@router.get("/api/recommendations/similar/{beat_id}")
async def get_similar_beats(
    beat_id: str,
    limit: int = 8,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get similar beats with optional personalization"""
    # Personalize if user is authenticated
    return await recommendation_service.get_similar_beats(
        beat_id=beat_id,
        user_id=current_user.id if current_user else None,
        limit=limit
    )
```

## 14. Migration and Rollout Strategy

### 14.1 Phase 1: Infrastructure Setup (Week 1)

1. Deploy Redis cluster
2. Create new database tables (UserPreferenceProfile, BeatSimilarityCache, etc.)
3. Add database indexes
4. Set up Celery workers

### 14.2 Phase 2: Background Jobs (Week 2)

1. Deploy profile calculation job
2. Deploy trending score calculation job
3. Deploy similarity pre-computation job
4. Verify data quality

### 14.3 Phase 3: API Rollout (Week 3)

1. Deploy recommendation service (shadow mode)
2. A/B test with 10% of users
3. Monitor performance metrics
4. Gradually increase to 50%, then 100%

### 14.4 Phase 4: Optimization (Week 4)

1. Tune cache TTLs based on metrics
2. Adjust algorithm weights based on engagement
3. Optimize slow queries
4. Implement additional performance improvements


## 15. Security Considerations

### 15.1 Data Privacy

- **Personal Behavior Data**: User behavior data is used only for recommendation purposes
- **Data Retention**: User behavior older than 1 year is archived
- **Data Access**: Only authorized services can access recommendation data
- **GDPR Compliance**: Users can request deletion of their behavior data

### 15.2 Rate Limiting

- **Per-User Limits**: 10 requests per minute per user
- **IP-Based Limits**: 100 requests per minute per IP (for anonymous users)
- **Burst Protection**: Maximum 20 concurrent requests per user

### 15.3 Input Validation

```python
from pydantic import validator

class RecommendationRequest(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    region: Optional[str] = None
    
    @validator('region')
    def validate_region(cls, v):
        if v and len(v) != 2:
            raise ValueError('Region must be 2-letter ISO code')
        return v.upper() if v else None
```

### 15.4 SQL Injection Prevention

- All database queries use SQLAlchemy ORM with parameterized queries
- No raw SQL with user input
- Input sanitization for all user-provided parameters

## 16. Future Enhancements

### 16.1 Machine Learning Models

**Deep Learning Recommendations**:
- Neural collaborative filtering
- Embedding-based similarity
- Sequence models for session-based recommendations
- Multi-armed bandit for exploration/exploitation

### 16.2 Advanced Features

- **Context-Aware Recommendations**: Time of day, weather, user mood
- **Cross-Platform Signals**: Integrate Spotify, YouTube listening history
- **Social Recommendations**: "Friends are listening to..."
- **Playlist Generation**: Auto-generate playlists based on seed beats
- **Beat Bundles**: "Complete this collection" recommendations

### 16.3 Personalization Improvements

- **User Segmentation**: Identify user archetypes (casual listener, producer, curator)
- **Intent Detection**: Infer whether user wants similar or diverse recommendations
- **Multi-Objective Optimization**: Balance relevance, diversity, and novelty
- **Bandwagon Detection**: Avoid over-recommending viral content


## 17. Success Metrics

### 17.1 Performance Metrics

| Metric | Target | Current Baseline |
|--------|--------|------------------|
| P95 Response Time | <200ms | TBD |
| Cache Hit Rate | >80% | TBD |
| Concurrent Users | 1000+ | TBD |
| Error Rate | <1% | TBD |
| Database Query Time | <150ms | TBD |

### 17.2 Engagement Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Click-Through Rate (CTR) | >10% | Clicks / Impressions |
| Conversion Rate | >2% | Purchases / Recommendations |
| Discover Feed Engagement | >15% | Plays from Discover / Total Plays |
| Artist Discovery Rate | >30% | New Artists Clicked / Total Artists |
| Recommendation Satisfaction | >4.0/5.0 | User Feedback Survey |

### 17.3 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Genre Diversity | ≥3 genres per 20 recommendations | Automated Check |
| Artist Diversity | ≤15% per artist | Automated Check |
| New Artist Rate | ≥40% | Automated Check |
| Quality Filter Compliance | 100% | Automated Check |

### 17.4 Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Purchase Uplift | +20% | Purchases from Recommendations |
| User Retention | +15% | Return Rate with Recommendations |
| Time on Platform | +25% | Session Duration |
| Beat Discovery | +40% | Unique Beats Played |


## 18. Documentation and Developer Resources

### 18.1 API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

### 18.2 Code Examples

**Python Client Example**:
```python
import requests

# Get personalized beat recommendations
response = requests.get(
    "https://api.beatpush.com/api/recommendations/beats",
    headers={"Authorization": f"Bearer {access_token}"},
    params={"limit": 20, "region": "NG"}
)
recommendations = response.json()

for beat in recommendations["recommendations"]:
    print(f"{beat['title']} by {beat['producer_name']} (Score: {beat['score']:.2f})")
```

**Frontend Integration Example**:
```typescript
// React hook for recommendations
import { useQuery } from '@tanstack/react-query';

export function useRecommendations(limit = 20) {
  return useQuery({
    queryKey: ['recommendations', 'beats', limit],
    queryFn: async () => {
      const response = await fetch(
        `/api/recommendations/beats?limit=${limit}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes (matches cache TTL)
  });
}
```

### 18.3 Monitoring Dashboards

**Grafana Dashboard Panels**:
1. Response Time Distribution (p50, p95, p99)
2. Cache Hit Rate Over Time
3. Requests Per Second
4. Error Rate by Endpoint
5. Database Query Times
6. Recommendation CTR by Type
7. Diversity Metrics
8. Top Recommended Beats

**Alert Configuration**:
```yaml
alerts:
  - name: High Response Time
    condition: p95_response_time > 200ms for 5m
    severity: warning
  
  - name: Low Cache Hit Rate
    condition: cache_hit_rate < 0.80 for 10m
    severity: warning
  
  - name: High Error Rate
    condition: error_rate > 0.05 for 5m
    severity: critical
```

## 19. Conclusion

The BeatPush Recommendation Engine is designed as a scalable, high-performance system that delivers personalized music recommendations through a hybrid approach combining collaborative filtering and content-based filtering. The architecture prioritizes sub-200ms response times through aggressive caching, pre-computation, and graceful degradation strategies.

Key design decisions:
- **Hybrid scoring** adapts to user maturity (cold start vs established)
- **Diversity constraints** prevent filter bubbles and ensure exploration
- **Regional awareness** boosts Nigerian/African content for local users
- **Real-time signals** keep recommendations fresh and relevant
- **Quality filters** maintain high content standards
- **Graceful degradation** ensures reliability under high load

The system is designed for horizontal scalability, supporting 1000+ concurrent users while maintaining performance targets. Background jobs handle expensive computations (trending scores, similarity matrices, profile updates), keeping the API fast and responsive.

With comprehensive monitoring, A/B testing capabilities, and well-defined success metrics, the recommendation engine will continuously improve through data-driven optimization.

