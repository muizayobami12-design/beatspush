"""
Social Feed Schemas
Task 7.1: Social Feed

Pydantic schemas for social feed functionality
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ================== POST SCHEMAS ==================

class PostCreate(BaseModel):
    """Create a new post"""
    post_type: str = Field(..., description="status, track_share, event, milestone, poll")
    content: Optional[str] = Field(None, description="Post content/text")
    media_url: Optional[str] = Field(None, description="Image/video URL")
    track_id: Optional[str] = Field(None, description="Track ID if sharing a track")
    event_date: Optional[str] = Field(None, description="Event date for announcements")
    poll_options: Optional[List[str]] = Field(None, description="Poll options")
    poll_duration_hours: Optional[int] = Field(24, description="Poll duration in hours")
    visibility: str = Field("public", description="public, followers, private")


class PostUpdate(BaseModel):
    """Update a post"""
    content: Optional[str] = None
    visibility: Optional[str] = None
    is_pinned: Optional[bool] = None


class UserBasic(BaseModel):
    """Basic user info for posts"""
    id: str
    full_name: str
    username: str
    role: str
    
    class Config:
        from_attributes = True


class TrackBasic(BaseModel):
    """Basic track info for posts"""
    id: str
    title: str
    artist_name: str
    cover_art_url: Optional[str]
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Comment response"""
    id: str
    post_id: str
    user: UserBasic
    parent_comment_id: Optional[str]
    content: str
    like_count: int
    is_edited: bool
    created_at: str
    updated_at: str
    
    # For nested replies
    replies: List['CommentResponse'] = []
    
    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """Post response"""
    id: str
    user: UserBasic
    post_type: str
    content: Optional[str]
    media_url: Optional[str]
    track: Optional[TrackBasic]
    event_date: Optional[str]
    poll_options: Optional[List[str]]
    poll_ends_at: Optional[str]
    
    # Engagement
    like_count: int
    comment_count: int
    share_count: int
    
    # User interaction status
    is_liked: bool = False
    is_bookmarked: bool = False
    has_voted: bool = False
    
    # Visibility
    visibility: str
    is_pinned: bool
    
    # Timestamps
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class PostDetailResponse(PostResponse):
    """Detailed post response with comments"""
    comments: List[CommentResponse] = []
    
    # Poll results if applicable
    poll_results: Optional[List[dict]] = None


class FeedResponse(BaseModel):
    """Feed response with pagination"""
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# ================== COMMENT SCHEMAS ==================

class CommentCreate(BaseModel):
    """Create a comment"""
    content: str = Field(..., min_length=1, max_length=500)
    parent_comment_id: Optional[str] = Field(None, description="For nested replies")


class CommentUpdate(BaseModel):
    """Update a comment"""
    content: str = Field(..., min_length=1, max_length=500)


# ================== INTERACTION SCHEMAS ==================

class LikeResponse(BaseModel):
    """Like/unlike response"""
    success: bool
    is_liked: bool
    like_count: int


class ShareCreate(BaseModel):
    """Share a post"""
    share_type: str = Field(..., description="repost, quote, external")
    quote_text: Optional[str] = Field(None, description="For quote reposts")


class ShareResponse(BaseModel):
    """Share response"""
    id: str
    post_id: str
    user: UserBasic
    share_type: str
    quote_text: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class BookmarkResponse(BaseModel):
    """Bookmark response"""
    success: bool
    is_bookmarked: bool


class PollVoteCreate(BaseModel):
    """Vote on a poll"""
    option_index: int = Field(..., ge=0, description="Index of the option to vote for")


class PollVoteResponse(BaseModel):
    """Poll vote response"""
    success: bool
    message: str
    poll_results: List[dict]


# ================== FOLLOW SCHEMAS ==================

class FollowResponse(BaseModel):
    """Follow/unfollow response"""
    success: bool
    is_following: bool
    follower_count: int
    following_count: int


class FollowerResponse(BaseModel):
    """Follower/following list item"""
    user: UserBasic
    followed_at: str
    is_following_back: bool = False
    
    class Config:
        from_attributes = True


class FollowListResponse(BaseModel):
    """List of followers/following"""
    users: List[FollowerResponse]
    total: int
    page: int
    page_size: int


class FollowStatsResponse(BaseModel):
    """Follow statistics"""
    follower_count: int
    following_count: int
    mutual_followers: int


class FollowSuggestionResponse(BaseModel):
    """Follow suggestion"""
    user: UserBasic
    reason: str = Field(..., description="Why this user is suggested")
    mutual_followers: int = 0
    
    class Config:
        from_attributes = True


# ================== STATS SCHEMAS ==================

class PostStatsResponse(BaseModel):
    """Post statistics"""
    total_posts: int
    total_likes_received: int
    total_comments_received: int
    total_shares_received: int
    most_liked_post: Optional[PostResponse]
    most_commented_post: Optional[PostResponse]


class TrendingTopicResponse(BaseModel):
    """Trending topic"""
    topic: str
    post_count: int
    engagement_count: int


# ================== MESSAGE RESPONSE ==================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


# Enable forward references for recursive models
CommentResponse.model_rebuild()


# ==========================================
# TASK 7.3: Enhanced Follow System Schemas
# ==========================================

# ========== Verification Schemas ==========

class VerificationRequest(BaseModel):
    """Verification request input"""
    reason: str
    social_links: Dict[str, str]  # e.g., {"instagram": "url", "twitter": "url"}

class VerificationResponse(BaseModel):
    """Verification request response"""
    status: str  # submitted, pending, already_verified
    request_id: Optional[str] = None
    message: str
    estimated_review: Optional[str] = None
    submitted_at: Optional[str] = None

class VerificationStatusResponse(BaseModel):
    """Verification status response"""
    is_verified: bool
    verification_date: Optional[str] = None
    badge_type: Optional[str] = None
    has_request: Optional[bool] = None
    request_status: Optional[str] = None
    submitted_at: Optional[str] = None
    reviewed_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    can_apply: Optional[bool] = None

# ========== Notification Schemas ==========

class NotificationData(BaseModel):
    """Notification data"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: Optional[bool] = None
    post_id: Optional[str] = None
    comment_preview: Optional[str] = None
    milestone: Optional[int] = None
    badge_type: Optional[str] = None

class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    type: str
    title: str
    message: str
    data: Optional[Dict] = None
    is_read: bool
    created_at: str
    read_at: Optional[str] = None

class NotificationListResponse(BaseModel):
    """Notification list response"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
    total_pages: int

class UnreadCountResponse(BaseModel):
    """Unread notification count"""
    unread_count: int

class NotificationPreferenceUpdate(BaseModel):
    """Update notification preferences"""
    new_follower: Optional[bool] = None
    mutual_follow: Optional[bool] = None
    verification_granted: Optional[bool] = None
    follow_suggestion: Optional[bool] = None
    follower_milestone: Optional[bool] = None
    post_like: Optional[bool] = None
    post_comment: Optional[bool] = None
    post_share: Optional[bool] = None

class NotificationPreferenceResponse(BaseModel):
    """Notification preferences response"""
    new_follower: bool
    mutual_follow: bool
    verification_granted: bool
    follow_suggestion: bool
    follower_milestone: bool
    post_like: bool
    post_comment: bool
    post_share: bool
    updated_at: str

# ========== Follow Suggestion Schemas ==========

class FollowSuggestionUser(BaseModel):
    """User in follow suggestion"""
    user_id: str
    username: str
    full_name: str
    profile_type: str
    is_verified: bool
    avatar_url: Optional[str] = None
    follower_count: int
    mutual_followers: int
    reason: str
    type: str
    score: int
    is_following: bool

class FollowSuggestionsResponse(BaseModel):
    """Follow suggestions response"""
    suggestions: List[FollowSuggestionUser]
    total: int

# ========== Trending Creator Schemas ==========

class TrendingCreatorTrack(BaseModel):
    """Recent track info"""
    title: str
    play_count: int

class TrendingCreatorResponse(BaseModel):
    """Trending creator response"""
    user_id: str
    username: str
    full_name: str
    profile_type: str
    is_verified: bool
    avatar_url: Optional[str] = None
    follower_count: int
    trending_score: float
    follower_growth_rate: float
    engagement_rate: float
    recent_posts_count: int
    recent_track: Optional[TrendingCreatorTrack] = None

class TrendingCreatorsResponse(BaseModel):
    """Trending creators list response"""
    trending: List[TrendingCreatorResponse]
    period: str
    total: int

# ========== Similar Artists Schemas ==========

class SimilarArtistResponse(BaseModel):
    """Similar artist response"""
    user_id: str
    username: str
    full_name: str
    profile_type: str
    is_verified: bool
    avatar_url: Optional[str] = None
    follower_count: int
    similarity_score: int
    reason: str
    is_following: bool

class SimilarArtistsResponse(BaseModel):
    """Similar artists list response"""
    similar_artists: List[SimilarArtistResponse]
    target_user: str
    total: int
