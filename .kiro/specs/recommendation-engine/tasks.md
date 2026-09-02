# Implementation Plan: BeatPush Recommendation Engine

## Overview

This implementation plan breaks down the BeatPush Recommendation Engine into discrete, parallelizable tasks following the architecture defined in the design document. The system consists of a FastAPI backend with 6 API endpoints, 4 background jobs (Celery), Redis caching, and sophisticated recommendation algorithms combining collaborative filtering, content-based filtering, and trending analysis.

**Technology Stack:**
- Backend: Python 3.10+ with FastAPI
- Database: PostgreSQL with SQLAlchemy ORM
- Cache: Redis
- Background Jobs: Celery with Redis broker
- Testing: pytest, pytest-asyncio, Hypothesis (property-based testing)

**Key Architecture Components:**
1. RecommendationService (orchestration layer)
2. CollaborativeFilter (user-user and item-item CF)
3. ContentBasedFilter (attribute-based matching)
4. TrendingService (time-decay weighted trending)
5. CacheManager (Redis-based caching with invalidation)
6. SignalProcessor (real-time event processing)

## Tasks

- [ ] 1. Database Schema and Models
  - [ ] 1.1 Create new database models for recommendation engine
    - Create SQLAlchemy models: UserPreferenceProfile, BeatSimilarityCache, TrendingBeatCache, RecommendationLog
    - Add JSON field support for storing preference weights and beat lists
    - Include appropriate indexes (user_id, created_at, genre, region)
    - Add validation constraints (scores 0.0-1.0, region ISO codes)
    - _Requirements: 8.2, 8.4, 14.1, 14.2_
    - _Estimated Time: 2-3 hours_
  
  - [ ] 1.2 Create database migration scripts
    - Generate Alembic migration for new tables
    - Add indexes: user_id, beat_id, created_at on existing behavior tables
    - Add composite indexes for collaborative filtering queries (beat_id, user_id)
    - Add time-window indexes for trending calculations
    - Test migration up and down
    - _Requirements: 11.3, 14.1_
    - _Estimated Time: 1-2 hours_
  
  - [x] 1.3 Add database query optimization utilities
    - Create helper functions for common queries (user behavior with time filters)
    - Implement query timeout handling (150ms threshold)
    - Add query result caching decorators
    - Create database connection pooling configuration
    - _Requirements: 11.3, 11.5_
    - _Estimated Time: 2 hours_

- [ ] 2. Core Algorithm Services
  - [ ] 2.1 Implement ContentBasedFilter service
    - Create ContentBasedFilter class in `app/services/recommendations/content_filter.py`
    - Implement `calculate_content_similarity()` with weighted scoring (genre 40%, BPM 20%, key 15%, mood 15%, tags 10%)
    - Implement `build_user_preference_vector()` from user behavior history
    - Implement `get_recommendations()` to rank beats by content similarity
    - Add BPM range matching (±10% tolerance)
    - Add tag overlap calculation using Jaccard similarity
    - _Requirements: 1.5, 3.2, 12.5_
    - _Estimated Time: 3-4 hours_
  
  - [ ]* 2.2 Write property test for ContentBasedFilter
    - **Property 16: Score Range Constraint** - All scores should be in [0.0, 1.0]
    - **Validates: Requirements 1.2, 2.2**
    - Use Hypothesis to generate random user profiles and beat attributes
    - Verify scores never exceed range bounds
    - Verify genre weight contribution is correctly capped at 0.40
    - _Estimated Time: 1 hour_
  
  - [ ] 2.3 Implement CollaborativeFilter service
    - Create CollaborativeFilter class in `app/services/recommendations/collaborative_filter.py`
    - Implement `user_similarity()` using cosine similarity on interaction vectors
    - Implement `item_similarity()` using Jaccard similarity on user overlap
    - Implement `user_user_recommendations()` (find top 50 similar users, aggregate favorites)
    - Implement `item_item_recommendations()` (find similar beats from recent interactions)
    - Weight interactions: play=1.0, favorite=2.0, purchase=5.0
    - _Requirements: 1.2, 1.6, 5.2_
    - _Estimated Time: 4-5 hours_
  
  - [ ]* 2.4 Write property test for CollaborativeFilter
    - **Property 16: Score Range Constraint** - All scores should be in [0.0, 1.0]
    - **Property 17: Artist Taste Overlap Correlation** - Higher overlap should yield higher scores
    - **Validates: Requirements 1.2, 2.2**
    - Test similarity calculations with various interaction patterns
    - Verify symmetry of user-user similarity
    - _Estimated Time: 1-2 hours_
  
  - [ ] 2.5 Implement SignalProcessor service
    - Create SignalProcessor class in `app/services/recommendations/signal_processor.py`
    - Implement `calculate_event_weight()` with time decay (24h=100%, 1-7d=50%, 7-30d=25%, >30d=10%)
    - Implement `calculate_purchase_weight()` with 150% boost for 48-hour window
    - Implement `get_weighted_user_behavior()` to retrieve and weight all user events
    - Implement `process_play_event()`, `process_purchase_event()`, `process_favorite_event()`
    - Add cache invalidation triggers on events
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.7_
    - _Estimated Time: 3 hours_
  
  - [ ]* 2.6 Write property test for SignalProcessor time decay
    - **Property 9: Time-Based Event Weighting** - Verify correct time decay weights
    - **Property 10: Purchase Recency Boost** - Verify 150% boost within 48 hours
    - **Validates: Requirements 10.2, 10.3, 10.4, 10.5, 10.7**
    - Use Hypothesis to generate events with various timestamps
    - Verify weight calculations match specification exactly
    - _Estimated Time: 1 hour_
  
  - [ ] 2.7 Implement TrendingService
    - Create TrendingService class in `app/services/recommendations/trending_service.py`
    - Implement `calculate_trending_score()` with weighted metrics (plays 40%, purchases 30%, favorites 15%, shares 15%)
    - Apply time decay (50% reduction for events >12 hours old)
    - Implement `get_trending_by_genre()` with genre filtering
    - Implement `get_regional_trending()` with region parameter
    - Add 24-hour rolling window aggregation
    - _Requirements: 6.2, 6.4, 6.6_
    - _Estimated Time: 3 hours_
  
  - [ ]* 2.8 Write property test for TrendingService
    - **Property 13: Trending Score Time Decay** - Events >12 hours get 50% weight
    - **Validates: Requirements 6.4**
    - Test with events distributed across 24-hour window
    - Verify decay boundary at 12-hour mark
    - _Estimated Time: 1 hour_

- [ ] 3. Cache Management System
  - [ ] 3.1 Implement CacheManager service
    - Create CacheManager class in `app/services/recommendations/cache_manager.py`
    - Initialize Redis connection with connection pooling
    - Implement `get()` and `set()` with TTL support (default 5 minutes)
    - Implement deterministic cache key generation: `rec:{user_id}:{type}:{params_hash}`
    - Implement `invalidate_user_cache()` with pattern matching deletion
    - Add cache hit/miss tracking and hit rate calculation
    - Add graceful fallback on Redis connection failures
    - Log warning when hit rate falls below 80%
    - _Requirements: 8.1, 8.2, 8.3, 8.6_
    - _Estimated Time: 3 hours_
  
  - [ ]* 3.2 Write property test for cache key determinism
    - **Property 12: Cache Key Determinism** - Same params should produce same key
    - **Validates: Requirements 8.2**
    - Test with identical and different parameters
    - Verify hash consistency across invocations
    - _Estimated Time: 30 minutes_
  
  - [ ] 3.3 Implement cache warming functionality
    - Add `warm_cache()` method to CacheManager
    - Add query to identify top 1000 active users (by 24-hour play count)
    - Implement batch cache warming with error handling per user
    - Add timing and success rate logging
    - _Requirements: 8.4_
    - _Estimated Time: 2 hours_

- [ ] 4. Checkpoint - Core Services Complete
  - Ensure all core algorithm services are implemented
  - Run unit tests for ContentBasedFilter, CollaborativeFilter, SignalProcessor, TrendingService
  - Verify CacheManager connects to Redis and performs basic operations
  - Ask the user if questions arise

- [ ] 5. User Profile Management
  - [ ] 5.1 Implement user preference profile builder
    - Create `build_user_preference_profile()` function in `app/services/recommendations/profile_builder.py`
    - Aggregate genre preferences from user's play/favorite/purchase history with frequency weights
    - Calculate BPM range (min, max, preferred) from user's listened beats
    - Extract key preferences (top 3 most common keys)
    - Extract mood preferences with frequency weights
    - Calculate interaction_count for cold-start detection
    - Store profile in UserPreferenceProfile table
    - _Requirements: 1.5, 1.6, 12.1, 12.2, 12.3, 12.4_
    - _Estimated Time: 3 hours_
  
  - [ ] 5.2 Implement profile loading and caching
    - Add `load_or_create_profile()` helper in RecommendationService
    - Cache profiles in memory with LRU eviction (top 1000 users)
    - Add automatic profile refresh on user behavior events
    - Handle cold-start users (interaction_count < 5)
    - _Requirements: 12.1, 12.4_
    - _Estimated Time: 2 hours_

- [ ] 6. Hybrid Scoring and Diversity
  - [ ] 6.1 Implement hybrid scoring algorithm
    - Create `calculate_hybrid_score()` function in `app/services/recommendations/scoring.py`
    - Implement adaptive weight calculation (cold-start: CB 70% + CF 30%, established: CF 60% + CB 40%)
    - Apply quality boosts: play-through >70% gets 15% boost
    - Apply quality penalties: bounce >80% gets 20% penalty
    - Apply diversity boost: underrepresented genres get 10% boost
    - Apply regional boost: Nigerian/African users get 20% boost for Afrobeats/Afropop/Amapiano
    - Clamp final score to [0.0, 1.0] range
    - _Requirements: 1.2, 1.5, 1.6, 2.6, 9.4, 13.5, 13.6_
    - _Estimated Time: 2-3 hours_
  
  - [ ]* 6.2 Write property test for hybrid scoring weights
    - **Property 15: Hybrid Scoring Weight Adaptation** - Verify weight switching at 5-interaction threshold
    - **Validates: Requirements 1.5, 1.6**
    - Test with users having <5 and ≥5 interactions
    - Verify weight contributions match specification
    - _Estimated Time: 1 hour_
  
  - [ ] 6.3 Implement diversity enforcement
    - Create `enforce_diversity_constraints()` function in `app/services/recommendations/diversity.py`
    - Enforce max 15% per-artist representation (max 3 beats from same artist in 20-beat list)
    - Enforce 40% new-artist requirement (artists user hasn't interacted with)
    - Enforce 3+ genre requirement for lists of 20+ beats
    - Track and log diversity metrics
    - Alert when single-artist representation exceeds 20%
    - _Requirements: 9.1, 9.2, 9.3, 9.5_
    - _Estimated Time: 3 hours_
  
  - [ ]* 6.4 Write property test for diversity constraints
    - **Property 6: Artist Diversity Constraint** - No artist >15% in 20+ beat lists
    - **Property 7: New Artist Representation** - At least 40% from new artists
    - **Property 8: Genre Diversity Constraint** - At least 3 genres in 20+ beat lists
    - **Validates: Requirements 9.1, 9.2, 9.3**
    - Test with various candidate sets
    - Verify constraints are always satisfied
    - _Estimated Time: 1-2 hours_

- [ ] 7. Quality Filtering
  - [ ] 7.1 Implement quality filters
    - Create `passes_quality_filters()` function in `app/services/recommendations/filters.py`
    - Filter out beats with rating <3.0 (or platform average if <5 ratings)
    - Filter out beats with copyright flags
    - Filter out inactive/deleted beats
    - Calculate and cache platform average rating
    - _Requirements: 13.1, 13.2, 13.3, 13.4_
    - _Estimated Time: 2 hours_
  
  - [ ]* 7.2 Write property test for quality filters
    - **Property 5: Quality Filter Enforcement** - All recommendations should pass quality checks
    - **Validates: Requirements 13.1, 13.2, 13.3**
    - Generate beats with various quality attributes
    - Verify filtered results all meet criteria
    - _Estimated Time: 1 hour_

- [ ] 8. Checkpoint - Algorithm Pipeline Complete
  - Test complete pipeline: profile → CF/CB → hybrid scoring → diversity → quality filters
  - Verify all property tests pass
  - Test with sample user data
  - Ask the user if questions arise

- [ ] 9. Main RecommendationService Orchestration
  - [ ] 9.1 Implement RecommendationService class skeleton
    - Create RecommendationService class in `app/services/recommendation_service.py`
    - Initialize with dependencies (db, cache, CF, CB, trending, signals)
    - Add helper methods: `_load_or_create_profile()`, `_get_purchased_beat_ids()`, `_format_response()`
    - Add performance timing decorator
    - Add request logging with metrics
    - _Requirements: 14.1, 14.5, 11.5_
    - _Estimated Time: 2 hours_
  
  - [ ] 9.2 Implement personalized beat recommendations
    - Implement `get_beat_recommendations()` method
    - Check cache first, return if hit
    - Load user profile
    - Get CF and CB candidates (top 100 each)
    - Calculate hybrid scores for union of candidates
    - Apply quality filters
    - Apply diversity constraints
    - Exclude purchased beats
    - Apply pagination (limit/offset)
    - Cache results with 5-minute TTL
    - Return formatted response with timing
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 8.1, 8.2_
    - _Estimated Time: 3-4 hours_
  
  - [ ]* 9.3 Write property test for beat recommendations
    - **Property 1: Recommendation Output Size and Ordering** - Return requested count, descending score order
    - **Property 2: Purchased Beat Exclusion** - No purchased beats in results
    - **Validates: Requirements 1.1, 1.4**
    - Test with various user purchase histories
    - Verify ordering is strictly descending
    - _Estimated Time: 1 hour_
  
  - [ ] 9.4 Implement artist suggestions
    - Implement `get_artist_suggestions()` method
    - Find artists with catalog overlap with user's favorites
    - Calculate overlap score (favorite beats ∩ artist catalog)
    - Include social signals (follows, likes) with 30% weight
    - Apply regional boost (20% for Nigerian/African artists to Nigerian users)
    - Exclude already-followed artists
    - Sort by score descending
    - Cache results with 5-minute TTL
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
    - _Estimated Time: 3 hours_
  
  - [ ]* 9.5 Write property test for artist suggestions
    - **Property 3: Followed Artist Exclusion** - No already-followed artists
    - **Property 14: Artist Score Ordering** - Descending score order
    - **Validates: Requirements 2.4, 2.1**
    - Test with various follow histories
    - _Estimated Time: 1 hour_
  
  - [ ] 9.6 Implement similar beats
    - Implement `get_similar_beats()` method
    - Calculate content similarity (genre 40%, BPM 20%, key 15%, mood 15%, tags 10%)
    - Apply same-artist boost (15%)
    - Apply user personalization if authenticated (30% weight)
    - Exclude reference beat
    - Sort by score descending
    - Cache results with 5-minute TTL
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
    - _Estimated Time: 2-3 hours_
  
  - [ ]* 9.7 Write property test for similar beats
    - **Property 4: Self-Reference Exclusion** - Reference beat never in results
    - **Validates: Requirements 3.3, 5.4**
    - Test with various reference beats
    - _Estimated Time: 30 minutes_
  
  - [ ] 9.8 Implement personalized discover feed
    - Implement `get_discover_feed()` method
    - Compose feed: 20% trending, 15% followed-artist releases, 40% collaborative, 25% content-based
    - Retrieve each component separately
    - Merge and interleave results to maintain composition percentages
    - Apply quality filters and diversity
    - Return at least 50 beats
    - Cache results with 5-minute TTL
    - Check cache age; use cached if <5 minutes old
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
    - _Estimated Time: 3-4 hours_
  
  - [ ] 9.9 Implement purchase-based suggestions (also-bought)
    - Implement `get_also_bought()` method
    - Check if reference beat has ≥10 purchases
    - If yes: find users who purchased reference beat, aggregate their other purchases
    - Calculate correlation frequency, return top 6
    - If <10 purchases: fallback to similar beats algorithm
    - Set `fallback_to_similar` flag in response
    - Exclude reference beat
    - Cache results with 5-minute TTL
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
    - _Estimated Time: 3 hours_
  
  - [ ]* 9.10 Write property test for also-bought
    - **Property 18: Collaborative Purchase Correlation** - Use co-purchase analysis when sufficient data
    - **Validates: Requirements 5.2**
    - Test correlation calculation
    - _Estimated Time: 1 hour_
  
  - [ ] 9.11 Implement trending beats by genre
    - Implement `get_trending_by_genre()` method
    - Call TrendingService with genre filter
    - Apply regional filtering if region parameter provided
    - Include "Trending in Nigeria" section for Nigerian users
    - Cache results with 15-minute TTL
    - Check cache age; use cached if <15 minutes old
    - Return at least 20 beats
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_
    - _Estimated Time: 2 hours_
  
  - [ ] 9.12 Implement anonymous user recommendations
    - Implement `get_anonymous_recommendations()` method
    - If genre preferences provided: filter beats by selected genres
    - If no preferences: return global trending beats
    - Track anonymous session interactions in session storage
    - Apply regional preference (40% weight to Afrobeats/Afropop/Amapiano for Nigerian users)
    - Return at least 20 beats
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_
    - _Estimated Time: 2-3 hours_

- [ ] 10. Checkpoint - RecommendationService Complete
  - Test all RecommendationService methods with sample data
  - Verify cache behavior (hits, misses, invalidation)
  - Run all property tests
  - Check performance with timing logs
  - Ask the user if questions arise

- [ ] 11. FastAPI Endpoints
  - [ ] 11.1 Create recommendations router
    - Create router in `app/api/v1/recommendations.py`
    - Set up dependency injection for RecommendationService
    - Add authentication dependency using `get_current_user`
    - Add optional authentication for public endpoints
    - Set up rate limiting (10 requests/minute per user)
    - _Requirements: 15.1-15.10, 11.4_
    - _Estimated Time: 2 hours_
  
  - [ ] 11.2 Implement GET /api/recommendations/beats endpoint
    - Add endpoint with authentication required
    - Parse query params: limit (default 20, max 100), offset (default 0), region
    - Call `recommendation_service.get_beat_recommendations()`
    - Return RecommendationResponse schema
    - Handle 401 Unauthorized for invalid tokens
    - Handle 429 Too Many Requests for rate limit
    - _Requirements: 15.1, 15.7, 15.8, 15.9_
    - _Estimated Time: 1 hour_
  
  - [ ] 11.3 Implement GET /api/recommendations/artists endpoint
    - Add endpoint with authentication required
    - Parse query params: limit (default 10, max 50), offset, region
    - Call `recommendation_service.get_artist_suggestions()`
    - Return ArtistSuggestionResponse schema
    - _Requirements: 15.2, 15.7, 15.8, 15.9_
    - _Estimated Time: 1 hour_
  
  - [ ] 11.4 Implement GET /api/recommendations/similar/{beat_id} endpoint
    - Add endpoint with optional authentication
    - Parse path param: beat_id
    - Parse query param: limit (default 8, max 20)
    - Call `recommendation_service.get_similar_beats()`
    - Handle 404 Not Found for invalid beat_id
    - Return RecommendationResponse schema
    - _Requirements: 15.3, 15.7, 15.10_
    - _Estimated Time: 1 hour_
  
  - [ ] 11.5 Implement GET /api/recommendations/discover endpoint
    - Add endpoint with authentication required
    - Parse query params: limit (default 50, max 100), offset, region
    - Call `recommendation_service.get_discover_feed()`
    - Return RecommendationResponse with composition breakdown
    - _Requirements: 15.4, 15.7, 15.8_
    - _Estimated Time: 1 hour_
  
  - [ ] 11.6 Implement GET /api/recommendations/also-bought/{beat_id} endpoint
    - Add endpoint with optional authentication
    - Parse path param: beat_id
    - Parse query param: limit (default 6, max 20)
    - Call `recommendation_service.get_also_bought()`
    - Return response with fallback flag
    - _Requirements: 15.5, 15.7_
    - _Estimated Time: 1 hour_
  
  - [ ] 11.7 Implement GET /api/recommendations/trending/{genre} endpoint
    - Add endpoint with optional authentication
    - Parse path param: genre
    - Parse query params: limit (default 20, max 50), region
    - Call `recommendation_service.get_trending_by_genre()`
    - Return RecommendationResponse with window and regional info
    - _Requirements: 15.6, 15.7_
    - _Estimated Time: 1 hour_
  
  - [ ]* 11.8 Write integration tests for all API endpoints
    - Test authentication requirements
    - Test query parameter validation
    - Test response schemas
    - Test error responses (401, 404, 429)
    - Test rate limiting
    - Test pagination
    - _Estimated Time: 3 hours_

- [ ] 12. Checkpoint - API Layer Complete
  - Test all endpoints with Postman or curl
  - Verify authentication and authorization
  - Test rate limiting behavior
  - Verify response formats match schemas
  - Ask the user if questions arise

- [ ] 13. Background Jobs (Celery Tasks)
  - [ ] 13.1 Set up Celery configuration
    - Create Celery app in `app/core/celery_app.py`
    - Configure Redis broker and result backend
    - Set up task queues: `trending`, `cache_warming`, `profiles`, `similarity`
    - Configure task routing
    - Add worker logging
    - _Requirements: 8.4, 6.3_
    - _Estimated Time: 2 hours_
  
  - [ ] 13.2 Implement trending score calculation job
    - Create task `calculate_trending_scores` in `app/tasks/trending.py`
    - Schedule: every 15 minutes (crontab)
    - Calculate for all genres: Afrobeats, Hip-Hop, R&B, Afropop, Amapiano, Trap
    - Calculate for regions: global, NG, GH, KE, ZA, US, GB
    - Aggregate engagement (plays 40%, purchases 30%, favorites 15%, shares 15%)
    - Apply time decay (50% for >12 hours)
    - Store results in TrendingBeatCache table
    - Set expiry at 15 minutes
    - _Requirements: 6.2, 6.3, 6.4, 6.7_
    - _Estimated Time: 3-4 hours_
  
  - [ ] 13.3 Implement cache warming job
    - Create task `warm_recommendation_cache` in `app/tasks/cache_warming.py`
    - Schedule: every 4 minutes
    - Query top 1000 active users (24-hour play count)
    - For each user, call `get_beat_recommendations()` (will auto-cache)
    - Add error handling per user (continue on failure)
    - Log success rate and timing
    - _Requirements: 8.4_
    - _Estimated Time: 2 hours_
  
  - [ ] 13.4 Implement user profile update job
    - Create task `update_user_profiles` in `app/tasks/profiles.py`
    - Schedule: every 1 hour
    - Query users with activity in last 7 days
    - For each user, call `build_user_preference_profile()`
    - Update or create UserPreferenceProfile record
    - Set updated_at timestamp
    - Log count of updated profiles
    - _Requirements: 12.1, 12.2, 12.3, 12.4_
    - _Estimated Time: 2-3 hours_
  
  - [ ] 13.5 Implement similarity pre-computation job
    - Create task `precompute_beat_similarities` in `app/tasks/similarity.py`
    - Schedule: daily at 3 AM
    - Query top 10,000 beats by play_count (>100 plays)
    - For each beat, calculate item-item similarity (top 50 similar)
    - Store in BeatSimilarityCache table
    - Set expiry at 24 hours
    - Log completion and count
    - _Requirements: 3.2, 5.2_
    - _Estimated Time: 3 hours_
  
  - [ ]* 13.6 Write unit tests for background jobs
    - Test trending calculation logic
    - Test cache warming logic
    - Test profile update logic
    - Mock database and cache dependencies
    - _Estimated Time: 2 hours_

- [ ] 14. Checkpoint - Background Jobs Complete
  - Run each Celery task manually to verify functionality
  - Verify tasks write to database correctly
  - Check task scheduling and queue routing
  - Monitor task execution times
  - Ask the user if questions arise

- [ ] 15. Error Handling and Resilience
  - [ ] 15.1 Implement graceful degradation
    - Create fallback chain in RecommendationService
    - Try cache → Try computation with timeout → Try cached fallback → Return trending
    - Implement async timeout (150ms for DB queries, 200ms total)
    - Add error response format with `fallback_used` flag
    - _Requirements: 11.3_
    - _Estimated Time: 2-3 hours_
  
  - [ ] 15.2 Implement circuit breaker pattern
    - Create CircuitBreaker class in `app/core/circuit_breaker.py`
    - Track failures with 60-second sliding window
    - Trip at 50% error threshold
    - Implement states: closed, open, half-open
    - Add automatic reset after cool-down period
    - _Requirements: 11.6_
    - _Estimated Time: 2 hours_
  
  - [ ] 15.3 Implement load shedding
    - Create LoadShedder class in `app/core/load_shedder.py`
    - Monitor system load (CPU, memory, connections)
    - Prioritize cached results when load >80%
    - Return trending fallback under extreme load
    - Log load-shedding events
    - _Requirements: 11.2, 11.3_
    - _Estimated Time: 2 hours_
  
  - [ ]* 15.4 Write integration tests for resilience
    - Test fallback chain with simulated failures
    - Test circuit breaker state transitions
    - Test load shedding under simulated high load
    - _Estimated Time: 2 hours_

- [ ] 16. Performance Monitoring and Logging
  - [ ] 16.1 Implement recommendation logging
    - Create logging service in `app/services/recommendation_logger.py`
    - Log every recommendation request to RecommendationLog table
    - Include: user_id, type, params, response_time_ms, cache_hit, beat_ids
    - Add async logging to avoid blocking requests
    - _Requirements: 14.1_
    - _Estimated Time: 2 hours_
  
  - [ ] 16.2 Implement engagement tracking
    - Add endpoint POST /api/recommendations/track-click
    - Update RecommendationLog with clicked_beat_ids
    - Add endpoint POST /api/recommendations/track-purchase
    - Update RecommendationLog with purchased_beat_ids
    - Calculate click-through rate (CTR)
    - Calculate conversion rate
    - _Requirements: 14.2, 14.3_
    - _Estimated Time: 2-3 hours_
  
  - [ ] 16.3 Implement metrics API endpoints
    - Add GET /api/recommendations/metrics/summary endpoint
    - Return: total recommendations served, cache hit rate, avg response time, engagement metrics
    - Add GET /api/recommendations/metrics/by-type endpoint
    - Return CTR and conversion rate per recommendation type
    - Require admin authentication
    - _Requirements: 14.5, 14.7_
    - _Estimated Time: 2 hours_
  
  - [ ] 16.4 Implement alerting logic
    - Add alert check for p95 response time >200ms
    - Add alert check for cache hit rate <80%
    - Add alert check for CTR <5% per type
    - Add alert check for single-artist representation >20%
    - Log alerts to dedicated logging channel
    - _Requirements: 11.5, 8.6, 14.6, 9.5_
    - _Estimated Time: 2 hours_

- [ ] 17. Integration with Existing Systems
  - [ ] 17.1 Integrate with WebSocket system
    - Add `broadcast_recommendation_update()` function
    - Send WebSocket message on cache invalidation
    - Include flags: `refresh_discover_feed`, `new_trending_available`
    - Call from SignalProcessor on user events
    - _Requirements: 10.1, 10.6_
    - _Estimated Time: 1-2 hours_
  
  - [ ] 17.2 Integrate with analytics service
    - Create AnalyticsIntegration class
    - Add `track_recommendation_served()` event
    - Add `track_recommendation_click()` event
    - Call from RecommendationService and tracking endpoints
    - _Requirements: 14.1, 14.2_
    - _Estimated Time: 1-2 hours_
  
  - [ ] 17.3 Add cache invalidation hooks to existing user event handlers
    - Find existing play event handler, add cache invalidation call
    - Find existing purchase event handler, add cache invalidation call
    - Find existing favorite event handler, add cache invalidation call
    - Test that user actions trigger cache invalidation
    - _Requirements: 8.3, 10.1_
    - _Estimated Time: 2 hours_

- [ ] 18. Final Testing and Quality Assurance
  - [ ]* 18.1 Run comprehensive integration tests
    - Test complete user flows: register → interact → receive recommendations
    - Test cold-start scenarios (new users, new beats)
    - Test diversity constraints across many requests
    - Test caching behavior (hits, misses, invalidation)
    - Test background job execution
    - _Estimated Time: 3-4 hours_
  
  - [ ]* 18.2 Run performance tests
    - Test response time under 1000 concurrent requests
    - Verify p95 response time <200ms
    - Verify p99 response time <500ms
    - Test cache hit rate under load
    - Test database query performance
    - _Requirements: 11.1, 11.2, 11.5_
    - _Estimated Time: 2-3 hours_
  
  - [ ]* 18.3 Run all property-based tests
    - Execute all Hypothesis property tests
    - Verify 100+ random test cases per property
    - Fix any discovered edge cases
    - Document property test coverage
    - _Estimated Time: 1-2 hours_
  
  - [ ] 18.4 Create deployment documentation
    - Document environment variables and configuration
    - Document database migration steps
    - Document Celery worker deployment
    - Document Redis setup and configuration
    - Document monitoring and alerting setup
    - _Estimated Time: 2 hours_

- [ ] 19. Final Checkpoint - System Ready for Deployment
  - All tests passing (unit, integration, property-based, performance)
  - All 6 API endpoints functional and tested
  - All 4 background jobs running on schedule
  - Cache hit rate >80%
  - Response times consistently <200ms
  - Documentation complete
  - Ask the user for final review and approval

## Notes

- **Optional Test Tasks**: Tasks marked with `*` are optional property-based and integration tests. They provide high confidence in correctness but can be skipped for faster MVP delivery. All core implementation tasks (non-test) should be completed.

- **Wave-Based Execution**: Tasks are organized into waves for parallel execution (see dependency graph below). Tasks within the same wave can be executed concurrently.

- **Estimated Time**: Each task includes a time estimate for planning purposes. Total implementation time is approximately 120-140 hours (3-4 weeks for a single developer, 1-2 weeks for a team).

- **Requirements Traceability**: Each task explicitly references the requirements it validates for full traceability.

- **Testing Strategy**: The implementation includes three levels of testing:
  1. Unit tests for individual functions
  2. Property-based tests (Hypothesis) for universal correctness properties
  3. Integration tests for API endpoints and service interactions

- **Performance Focus**: All tasks include performance considerations (caching, query optimization, timeouts) to meet the sub-200ms response time requirement.

- **Technology Stack**: Python 3.10+ with FastAPI, PostgreSQL with SQLAlchemy, Redis for caching, Celery for background jobs.

## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["1.1", "1.2"]
    },
    {
      "id": 1,
      "tasks": ["1.3", "2.1", "2.3", "2.5", "2.7", "3.1"]
    },
    {
      "id": 2,
      "tasks": ["2.2", "2.4", "2.6", "2.8", "3.2", "3.3", "5.1"]
    },
    {
      "id": 3,
      "tasks": ["5.2", "6.1", "7.1"]
    },
    {
      "id": 4,
      "tasks": ["6.2", "6.3", "7.2"]
    },
    {
      "id": 5,
      "tasks": ["6.4", "9.1"]
    },
    {
      "id": 6,
      "tasks": ["9.2", "9.4", "9.6", "9.8", "9.9", "9.11", "9.12"]
    },
    {
      "id": 7,
      "tasks": ["9.3", "9.5", "9.7", "9.10"]
    },
    {
      "id": 8,
      "tasks": ["11.1"]
    },
    {
      "id": 9,
      "tasks": ["11.2", "11.3", "11.4", "11.5", "11.6", "11.7"]
    },
    {
      "id": 10,
      "tasks": ["11.8", "13.1"]
    },
    {
      "id": 11,
      "tasks": ["13.2", "13.3", "13.4", "13.5"]
    },
    {
      "id": 12,
      "tasks": ["13.6", "15.1", "15.2", "15.3", "16.1", "16.2"]
    },
    {
      "id": 13,
      "tasks": ["15.4", "16.3", "16.4"]
    },
    {
      "id": 14,
      "tasks": ["17.1", "17.2", "17.3"]
    },
    {
      "id": 15,
      "tasks": ["18.1", "18.2", "18.3", "18.4"]
    }
  ]
}
```
