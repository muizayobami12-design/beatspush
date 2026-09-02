# Implementation Plan: Social Feed System

## Overview

This implementation follows an MVP-First approach with three distinct phases:

**Phase 1 - Core MVP:** Text posts, basic feed (following activity), like/comment engagement, infinite scroll  
**Phase 2 - Enhanced Features:** Track shares, media posts, personalized algorithm (recommended + trending), share/save, real-time updates  
**Phase 3 - Polish:** Polls, events, milestones, advanced filters, performance optimizations, accessibility

Each phase delivers a working, testable feature set that builds on the previous phase.

## Tasks

### Phase 1: Core MVP - Text Posts & Basic Engagement

- [x] 1. Set up database models and migrations
  - [x] 1.1 Create Post model in backend/app/models/social.py
    - Implement Post model with fields: id, user_id, type, content, visibility, engagement counters, timestamps
    - Add PostType enum (TEXT, TRACK_SHARE, MEDIA, POLL, EVENT, MILESTONE)
    - Add PostVisibility enum (PUBLIC, FOLLOWERS, PRIVATE)
    - Include database indexes for performance
    - _Requirements: FR-1.1, FR-4.1, FR-7.2_
  
  - [x] 1.2 Create PostLike model in backend/app/models/social.py
    - Implement PostLike model with user_id, post_id, timestamp
    - Add unique constraint (user can like post only once)
    - Add indexes for efficient querying
    - _Requirements: FR-3.1_
  
  - [x] 1.3 Create PostComment model in backend/app/models/social.py
    - Implement PostComment with content, threading support (parent_comment_id)
    - Add like_count, is_deleted, is_edited fields
    - Limit threading to 1 level deep
    - Add indexes for post and user lookups
    - _Requirements: FR-3.2_
  
  - [x] 1.4 Create Alembic migration for Phase 1 models
    - Generate migration for Post, PostLike, PostComment tables
    - Include all indexes and constraints
    - Test migration up/down
    - _Requirements: FR-1.1, FR-3.1, FR-3.2_

- [x] 2. Implement core API endpoints for posts
  - [x] 2.1 Create POST /api/v1/social/posts endpoint
    - Implement post creation with text content validation (max 2000 chars)
    - Support markdown formatting
    - Parse @mentions and #hashtags
    - Return created post with user info
    - _Requirements: FR-1.1, FR-4.1_
  
  - [x] 2.2 Create GET /api/v1/social/feed endpoint
    - Implement basic feed query (posts from followed users)
    - Support pagination with cursor (20 posts per page)
    - Filter out deleted posts and blocked users
    - Return posts in chronological order (newest first)
    - Include engagement counts and user relationship data
    - _Requirements: FR-2.2, FR-5.1, 4.1_
  
  - [x] 2.3 Create GET /api/v1/social/posts/{post_id} endpoint
    - Retrieve single post with full details
    - Include author information and engagement data
    - Check visibility permissions
    - _Requirements: FR-1.1, FR-7.2_
  
  - [ ] 2.4 Create PUT /api/v1/social/posts/{post_id} endpoint
    - Allow editing text content within 15 minutes
    - Block edits if engagement > 10 likes/comments
    - Set edited_at timestamp and is_edited flag
    - _Requirements: FR-4.2_
  
  - [x] 2.5 Create DELETE /api/v1/social/posts/{post_id} endpoint
    - Implement soft delete (set is_deleted flag)
    - Verify user owns the post
    - Remove from feeds immediately
    - _Requirements: FR-4.3_

- [x] 3. Implement engagement endpoints
  - [x] 3.1 Create POST /api/v1/social/posts/{post_id}/like endpoint
    - Add like record with user_id and post_id
    - Increment post like_count atomically
    - Handle duplicate likes (idempotent)
    - Return updated like status
    - _Requirements: FR-3.1_
  
  - [x] 3.2 Create DELETE /api/v1/social/posts/{post_id}/like endpoint
    - Remove like record
    - Decrement post like_count atomically
    - Return updated like status
    - _Requirements: FR-3.1_
  
  - [x] 3.3 Create POST /api/v1/social/posts/{post_id}/comments endpoint
    - Add comment with content validation
    - Support parent_comment_id for replies
    - Limit to 1 level of threading
    - Increment post comment_count
    - Parse @mentions
    - _Requirements: FR-3.2_
  
  - [x] 3.4 Create GET /api/v1/social/posts/{post_id}/comments endpoint
    - Retrieve comments with pagination
    - Support sorting (newest, oldest, most liked)
    - Include nested replies
    - Return with author information
    - _Requirements: FR-3.2_
  
  - [x] 3.5 Create DELETE /api/v1/social/comments/{comment_id} endpoint
    - Soft delete comment (set is_deleted flag)
    - Verify user owns comment
    - Decrement post comment_count
    - _Requirements: FR-3.2_

- [x] 4. Build frontend post composer component
  - [x] 4.1 Create PostComposer component in frontend/src/components/features/social/
    - Build text input with markdown support
    - Add character counter (2000 max)
    - Implement @mention autocomplete
    - Add #hashtag suggestions
    - Include visibility selector (public/followers/private)
    - _Requirements: FR-1.1, FR-4.1, 5.2_
  
  - [x] 4.2 Integrate PostComposer with API
    - Connect to POST /api/v1/social/posts
    - Handle loading and error states
    - Show success message on post creation
    - Clear form after successful post
    - _Requirements: FR-4.1_

- [x] 5. Build frontend feed display
  - [x] 5.1 Create PostCard component in frontend/src/components/features/social/
    - Display post content with markdown rendering
    - Show user avatar, name, timestamp (relative time)
    - Display engagement counts (likes, comments, shares)
    - Add action buttons (like, comment, share)
    - Implement responsive card design
    - _Requirements: FR-1.1, FR-3.1, FR-3.2, 5.1_
  
  - [x] 5.2 Create Feed component with infinite scroll
    - Implement virtual scrolling for performance
    - Load posts in batches of 20
    - Add loading skeleton for smooth UX
    - Implement "Load more" fallback button
    - Handle empty state
    - _Requirements: FR-2.2, FR-5.1, 4.1_
  
  - [x] 5.3 Integrate Feed with API
    - Connect to GET /api/v1/social/feed
    - Implement cursor-based pagination
    - Handle loading and error states
    - Cache feed data with React Query
    - _Requirements: FR-2.2, FR-5.1, 4.1_

- [x] 6. Implement engagement UI interactions
  - [x] 6.1 Add like button interaction to PostCard
    - Implement animated heart icon
    - Toggle like/unlike on click
    - Optimistic UI updates
    - Show like count
    - _Requirements: FR-3.1_
  
  - [x] 6.2 Create CommentSection component
    - Display comments with threading (1 level)
    - Add reply button for comments
    - Show comment like counts
    - Implement comment sorting
    - _Requirements: FR-3.2_
  
  - [x] 6.3 Create CommentInput component
    - Text input for new comments/replies
    - Support @mentions
    - Add submit button
    - Show loading state
    - _Requirements: FR-3.2_

- [x] 7. Checkpoint - MVP Core Complete
  - Ensure all tests pass, ask the user if questions arise
  - Verify text posts can be created and displayed
  - Test like/comment functionality end-to-end
  - Confirm infinite scroll works smoothly

### Phase 2: Enhanced Features - Media, Algorithm, Real-Time

- [x] 8. Add media support to posts
  - [x] 8.1 Extend Post model for media attachments
    - Add media_urls JSON field
    - Add track_id foreign key for track shares
    - Update Alembic migration
    - _Requirements: FR-1.2, FR-1.3_
  
  - [x] 8.2 Create POST /api/v1/social/posts/upload endpoint
    - Accept image/video uploads (max 4 images, 1 video)
    - Validate file sizes (10MB images, 100MB videos)
    - Generate thumbnails for videos
    - Store media URLs in Post model
    - Integrate with existing upload service
    - _Requirements: FR-1.3_
  
  - [x] 8.3 Update POST /api/v1/social/posts endpoint for media
    - Accept media_urls in post creation
    - Accept track_id for track shares
    - Validate media references exist
    - _Requirements: FR-1.2, FR-1.3_
  
  - [x] 8.4 Add media upload to PostComposer
    - Image upload button with preview
    - Video upload with preview
    - Support multiple images (carousel)
    - Show upload progress
    - _Requirements: FR-1.3, 5.2_
  
  - [x] 8.5 Create MediaDisplay component for PostCard
    - Image carousel for multiple images
    - Video player with controls
    - Track player for track shares with waveform
    - Link to full track page
    - _Requirements: FR-1.2, FR-1.3_

- [x] 9. Implement share and save functionality
  - [x] 9.1 Create PostShare and PostSave models
    - Implement PostShare with user_id, post_id, share_type, comment
    - Implement PostSave with user_id, post_id, collection_name
    - Add ShareType enum (REPOST, DM, EXTERNAL)
    - Create Alembic migration
    - _Requirements: FR-3.3, FR-3.4_
  
  - [x] 9.2 Create POST /api/v1/social/posts/{post_id}/share endpoint
    - Handle repost to feed
    - Handle DM share (integrate with messaging)
    - Generate external share link
    - Increment post share_count
    - _Requirements: FR-3.3_
  
  - [x] 9.3 Create POST /api/v1/social/posts/{post_id}/save endpoint
    - Save post for user
    - Support optional collection name
    - Make idempotent
    - _Requirements: FR-3.4_
  
  - [x] 9.4 Create GET /api/v1/social/saved endpoint
    - Retrieve saved posts for user
    - Support filtering by collection
    - Include pagination
    - _Requirements: FR-3.4_
  
  - [x] 9.5 Add share and save buttons to PostCard
    - Share dropdown (repost, DM, copy link)
    - Save/bookmark button
    - Show saved indicator
    - _Requirements: FR-3.3, FR-3.4_

- [x] 10. Build personalized feed algorithm
  - [x] 10.1 Create feed algorithm service in backend/app/services/
    - Implement scoring algorithm with weights (50% following, 30% recommended, 15% trending, 5% sponsored)
    - Query posts from followed users
    - Query recommended posts based on genre preferences
    - Query trending posts (high engagement in 24hrs)
    - Merge and rank posts by score
    - _Requirements: FR-2.1, FR-2.3, FR-2.4_
  
  - [x] 10.2 Implement Redis caching for feed
    - Cache generated feeds per user
    - Set TTL to 5 minutes
    - Invalidate cache on new post
    - _Requirements: FR-2.1, 4.2_
  
  - [x] 10.3 Create GET /api/v1/social/feed/discover endpoint
    - Use algorithm to generate discover feed
    - Include posts from non-followed users
    - Filter by genre preferences
    - Support pagination
    - _Requirements: FR-2.3_
  
  - [x] 10.4 Create GET /api/v1/social/feed/trending endpoint
    - Calculate trending posts (24hr engagement)
    - Support genre-specific trending
    - Support location-specific trending
    - Update every 5 minutes
    - _Requirements: FR-2.4_
  
  - [x] 10.5 Add feed navigation tabs to frontend
    - Create tabs: For You, Following, Trending
    - Switch between feed endpoints
    - Maintain scroll position on tab change
    - _Requirements: FR-2.1, FR-2.2, FR-2.3, FR-2.4, 5.3_

- [x] 11. Implement real-time updates
  - [x] 11.1 Set up WebSocket endpoint for feed updates
    - Create WebSocket connection handler
    - Broadcast new posts to relevant users
    - Send engagement updates (likes, comments)
    - Integrate with existing WebSocket manager
    - _Requirements: FR-5.3_
  
  - [x] 11.2 Add real-time post notifications to frontend
    - Connect to WebSocket feed channel
    - Show "X new posts" notification banner
    - Load new posts on banner click
    - Implement pull-to-refresh gesture
    - _Requirements: FR-5.2, FR-5.3_

- [x] 12. Add notification integration
  - [x] 12.1 Implement post notification triggers
    - Send notification when followed user posts
    - Send notification on post like
    - Send notification on post comment
    - Send notification on @mention
    - Send notification on comment reply
    - Integrate with existing notification system
    - _Requirements: FR-6.1_
  
  - [x] 12.2 Create notification settings for posts
    - Add social feed notification preferences
    - Enable/disable per notification type
    - Support push/email/in-app options
    - _Requirements: FR-6.2_

- [x] 13. Checkpoint - Enhanced Features Complete
  - Ensure all tests pass, ask the user if questions arise
  - Verify media posts and track shares work
  - Test personalized algorithm with different user profiles
  - Confirm real-time updates are delivered
  - Validate notification integration

### Phase 3: Polish - Polls, Events, Optimizations

- [x] 14. Implement poll posts
  - [x] 14.1 Create PollVote model
    - Implement with post_id, user_id, option_id
    - Add unique constraint (one vote per poll)
    - Create Alembic migration
    - _Requirements: FR-1.4_
  
  - [x] 14.2 Add poll support to Post model
    - Add poll_options JSON field
    - Add poll_ends_at timestamp
    - Update existing posts endpoint
    - _Requirements: FR-1.4_
  
  - [x] 14.3 Create POST /api/v1/social/posts/{post_id}/vote endpoint
    - Record user vote
    - Validate poll is active (not expired)
    - Ensure one vote per user
    - Return updated vote counts
    - _Requirements: FR-1.4_
  
  - [x] 14.4 Create GET /api/v1/social/posts/{post_id}/results endpoint
    - Calculate vote percentages
    - Show total vote count
    - Indicate user's vote
    - _Requirements: FR-1.4_
  
  - [x] 14.5 Create PollPost component for frontend
    - Display poll options
    - Show vote percentages
    - Highlight user's vote
    - Show poll countdown
    - Disable voting after expiry
    - _Requirements: FR-1.4, 5.2_
  
  - [x] 14.6 Add poll creation to PostComposer
    - Poll option input (2-4 options)
    - Duration selector (1hr to 7 days)
    - Real-time preview
    - _Requirements: FR-1.4, 5.2_

- [x] 15. Implement event posts
  - [x] 15.1 Add event support to Post model
    - Add event_data JSON field (title, date, time, location, link)
    - Update posts endpoint for event creation
    - _Requirements: FR-1.5_
  
  - [x] 15.2 Create EventPost component
    - Display event details
    - Show countdown timer
    - Add RSVP/ticket link button
    - Calendar integration button
    - _Requirements: FR-1.5, 5.2_
  
  - [x] 15.3 Add event creation to PostComposer
    - Event details form
    - Date/time picker
    - Location autocomplete
    - Ticket link input
    - _Requirements: FR-1.5, 5.2_

- [x] 16. Implement milestone posts
  - [x] 16.1 Create milestone post generator service
    - Detect milestone events (stream counts, followers, first track)
    - Auto-generate milestone posts
    - Add celebratory design templates
    - _Requirements: FR-1.6_
  
  - [x] 16.2 Add milestone post types to frontend
    - Create MilestonePost component
    - Add badges and confetti animation
    - Show milestone details
    - _Requirements: FR-1.6_
  
  - [x] 16.3 Add user settings for milestone posts
    - Enable/disable auto-generation
    - Select which milestones to celebrate
    - _Requirements: FR-1.6_

- [x] 17. Add content moderation
  - [x] 17.1 Create PostReport model
    - Implement with post_id, reporter_user_id, reason, status
    - Add ReportReason enum (SPAM, HARASSMENT, EXPLICIT_CONTENT, COPYRIGHT, etc.)
    - Add ReportStatus enum (PENDING, REVIEWED, ACTIONED, DISMISSED)
    - Create Alembic migration
    - _Requirements: FR-3.5, FR-7.1_
  
  - [x] 17.2 Create POST /api/v1/social/posts/{post_id}/report endpoint
    - Submit report with reason and details
    - Add to moderation queue
    - Hide reported post from reporter's feed
    - _Requirements: FR-3.5_
  
  - [x] 17.3 Implement automatic content filters
    - Add profanity filter for post content
    - Implement spam detection
    - Add rate limiting (100 posts/day)
    - _Requirements: FR-7.1, 4.4_
  
  - [x] 17.4 Create admin moderation interface
    - Review queue for reported posts
    - Action buttons (dismiss, warn, remove)
    - Filter by report reason
    - _Requirements: FR-7.1_

- [x] 18. Implement advanced feed features
  - [x] 18.1 Add post pinning functionality
    - Create pin/unpin endpoint
    - Limit to 1 pinned post per user
    - Show pinned badge on post
    - Display pinned post at top of profile
    - _Requirements: FR-4.4_
  
  - [x] 18.2 Create feed filter system
    - Filter by post type (all, tracks, events, media, etc.)
    - Filter by media type (with media, videos only)
    - Filter by date range
    - Save filter preferences per user
    - _Requirements: FR-5.4_
  
  - [x] 18.3 Add "who liked" functionality
    - Create GET /api/v1/social/posts/{post_id}/likes endpoint
    - Show list of users who liked post
    - Include pagination
    - Display in modal on frontend
    - _Requirements: FR-3.1_

- [ ] 19. Performance optimizations
  - [x] 19.1 Optimize database queries
    - Add composite indexes for common queries
    - Implement query result caching
    - Use database read replicas for feed queries
    - Analyze slow queries with EXPLAIN
    - _Requirements: 4.1, 4.2_
  
  - [x] 19.2 Implement CDN for media content
    - Configure CDN for image/video delivery
    - Add cache headers
    - Implement lazy loading for images
    - _Requirements: 4.2_
  
  - [x] 19.3 Add feed preloading and caching
    - Preload next page of posts
    - Cache feed responses in Redis
    - Implement stale-while-revalidate pattern
    - _Requirements: 4.1, 4.2_
  
  - [x] 19.4 Optimize frontend bundle size
    - Code split feed components
    - Lazy load media viewer
    - Optimize image sizes
    - _Requirements: 4.1_

- [x] 20. Accessibility improvements
  - [x] 20.1 Add screen reader support
    - Add ARIA labels to all interactive elements
    - Implement proper heading hierarchy
    - Add alt text to images
    - Announce feed updates to screen readers
    - _Requirements: 4.5_
  
  - [x] 20.2 Implement keyboard navigation
    - Tab through posts and actions
    - Arrow keys to navigate feed
    - Keyboard shortcuts (L for like, C for comment)
    - Focus management for modals
    - _Requirements: 4.5_
  
  - [x] 20.3 Add high contrast mode support
    - Test with high contrast themes
    - Ensure sufficient color contrast ratios
    - Add focus indicators
    - _Requirements: 4.5_

- [x] 21. Integration with analytics
  - [x] 21.1 Track post impressions
    - Log when post enters viewport
    - Send impression events to analytics
    - Aggregate by post and user
    - _Requirements: 6.3_
  
  - [x] 21.2 Create post insights dashboard
    - Show engagement rates per post
    - Display reach and impressions
    - Compare performance across post types
    - Export insights data
    - _Requirements: 6.3_

- [x] 22. Final checkpoint - Complete system test
  - Ensure all tests pass, ask the user if questions arise
  - Verify all post types (text, media, track, poll, event, milestone)
  - Test all engagement features (like, comment, share, save, report)
  - Confirm feed algorithm personalizes correctly
  - Validate real-time updates work across tabs
  - Test accessibility with screen readers
  - Performance test with large data sets
  - Security test (rate limiting, input sanitization, permissions)

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation between phases
- Phase 1 (tasks 1-7) delivers a working MVP with core engagement
- Phase 2 (tasks 8-13) adds media, algorithms, and real-time features
- Phase 3 (tasks 14-22) adds advanced features and polish
- Backend uses FastAPI + SQLAlchemy + PostgreSQL + Redis
- Frontend uses Next.js + TypeScript + Tailwind + Shadcn UI
- Integrates with existing authentication, messaging, notification systems
- All engagement counters are denormalized for performance
- Database indexes are critical for feed query performance
- Real-time updates use existing WebSocket infrastructure

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["1.4"] },
    { "id": 2, "tasks": ["2.1", "2.2", "2.3", "2.4", "2.5", "3.1", "3.2", "3.3", "3.4", "3.5"] },
    { "id": 3, "tasks": ["4.1", "5.1"] },
    { "id": 4, "tasks": ["4.2", "5.2", "6.1", "6.2", "6.3"] },
    { "id": 5, "tasks": ["5.3"] },
    { "id": 6, "tasks": ["8.1"] },
    { "id": 7, "tasks": ["8.2", "8.3"] },
    { "id": 8, "tasks": ["8.4", "9.1"] },
    { "id": 9, "tasks": ["8.5", "9.2", "9.3", "9.4"] },
    { "id": 10, "tasks": ["9.5", "10.1"] },
    { "id": 11, "tasks": ["10.2", "10.3", "10.4"] },
    { "id": 12, "tasks": ["10.5", "11.1", "12.1"] },
    { "id": 13, "tasks": ["11.2", "12.2"] },
    { "id": 14, "tasks": ["14.1", "14.2", "15.1"] },
    { "id": 15, "tasks": ["14.3", "14.4", "15.2", "16.1"] },
    { "id": 16, "tasks": ["14.5", "15.3", "16.2", "17.1"] },
    { "id": 17, "tasks": ["14.6", "16.3", "17.2", "17.3"] },
    { "id": 18, "tasks": ["17.4", "18.1", "18.2"] },
    { "id": 19, "tasks": ["18.3", "19.1", "19.2", "19.3", "21.1"] },
    { "id": 20, "tasks": ["19.4", "20.1", "20.2", "20.3", "21.2"] }
  ]
}
```
