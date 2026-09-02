"""
Social Feed API Endpoints
Task 7.1: Social Feed

Endpoints for social feed, posts, comments, follows, etc.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.social_service import SocialService
from app.schemas.social import (
    PostCreate, PostUpdate, PostResponse, PostDetailResponse, FeedResponse,
    CommentCreate, CommentUpdate, CommentResponse,
    LikeResponse, ShareCreate, ShareResponse, BookmarkResponse,
    PollVoteCreate, PollVoteResponse,
    FollowResponse, FollowerResponse, FollowListResponse, FollowStatsResponse,
    MessageResponse, UserBasic, TrackBasic,
    # Task 7.3: Enhanced Follow System
    VerificationRequest, VerificationResponse, VerificationStatusResponse,
    NotificationResponse, NotificationListResponse, UnreadCountResponse,
    NotificationPreferenceUpdate, NotificationPreferenceResponse,
    FollowSuggestionsResponse, TrendingCreatorsResponse, SimilarArtistsResponse
)
from app.models.social import Post, PostComment, Follow
from app.models.track import Track
import json

router = APIRouter(prefix="/social", tags=["Social Feed"])


# ================== HELPER FUNCTIONS ==================

def post_to_response(post: Post, current_user_id: str, db: Session) -> PostResponse:
    """Convert Post model to PostResponse schema"""
    
    # Get user info
    user = UserBasic(
        id=post.user.id,
        full_name=post.user.full_name,
        username=post.user.username,
        role=post.user.role
    )
    
    # Get track info if track share
    track = None
    if post.track_id and post.track:
        track = TrackBasic(
            id=post.track.id,
            title=post.track.title,
            artist_name=post.track.artist_name,
            cover_art_url=post.track.cover_art_url
        )
    
    # Parse poll options
    poll_options = None
    if post.poll_options:
        poll_options = json.loads(post.poll_options)
    
    # Check user interactions
    is_liked = SocialService.is_post_liked(db, post.id, current_user_id)
    
    # Check if bookmarked
    from app.models.social import PostSave
    is_bookmarked = db.query(PostSave).filter(
        PostSave.post_id == post.id,
        PostSave.user_id == current_user_id
    ).first() is not None
    
    return PostResponse(
        id=post.id,
        user=user,
        post_type=post.type,
        content=post.content,
        media_url=post.media_urls[0] if post.media_urls else None,
        track=track,
        event_date=post.event_data.get("date") if post.event_data else None,
        poll_options=poll_options,
        poll_ends_at=post.poll_ends_at,
        like_count=post.like_count,
        comment_count=post.comment_count,
        share_count=post.share_count,
        is_liked=is_liked,
        is_bookmarked=is_bookmarked,
        visibility=post.visibility,
        is_pinned=post.is_pinned,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


# ================== MEDIA UPLOAD ENDPOINTS ==================

@router.post("/posts/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_post_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload media file for a post (image or video).
    
    **Supported Types:**
    - Images: jpg, jpeg, png, gif, webp (max 10MB)
    - Videos: mp4, mov, webm (max 100MB)
    
    **Returns:**
    - `media_url`: URL to use in the post's media_url field
    - `media_type`: 'image' or 'video'
    - `file_size`: File size in bytes
    """
    # Validate file type
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}
    MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    
    content_type = file.content_type or ""
    
    if content_type in ALLOWED_IMAGE_TYPES:
        media_type = "image"
        max_size = MAX_IMAGE_SIZE
    elif content_type in ALLOWED_VIDEO_TYPES:
        media_type = "video"
        max_size = MAX_VIDEO_SIZE
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {content_type}. Allowed: images (jpg, png, gif, webp) and videos (mp4, mov, webm)"
        )
    
    # Read and validate file size
    content = await file.read()
    file_size = len(content)
    
    if file_size > max_size:
        max_mb = max_size // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size for {media_type} is {max_mb}MB"
        )
    
    # Upload using existing file storage service
    try:
        from app.services.file_storage import FileStorageService
        import uuid
        
        storage_service = FileStorageService()
        file_ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "bin"
        storage_key = f"social/posts/{current_user.id}/{uuid.uuid4()}.{file_ext}"
        
        media_url = await storage_service.upload_bytes(
            data=content,
            key=storage_key,
            content_type=content_type
        )
        
        return {
            "media_url": media_url,
            "media_type": media_type,
            "file_size": file_size,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


# ================== POST ENDPOINTS ==================

@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new post.
    
    **Post Types:**
    - `status`: Regular status update
    - `track_share`: Share a track (requires track_id)
    - `event`: Event announcement (requires event_date)
    - `milestone`: Celebrate a milestone
    - `poll`: Create a poll (requires poll_options)
    
    **Visibility Options:**
    - `public`: Everyone can see
    - `followers`: Only followers can see
    - `private`: Only you can see
    """
    try:
        poll_options = post_data.poll_options
        
        post = SocialService.create_post(
            db=db,
            user_id=current_user.id,
            post_type=post_data.post_type,
            content=post_data.content,
            media_url=post_data.media_url,
            track_id=post_data.track_id,
            event_date=post_data.event_date,
            poll_options=poll_options,
            poll_duration_hours=post_data.poll_duration_hours,
            visibility=post_data.visibility
        )
        
        return post_to_response(post, current_user.id, db)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


@router.get("/feed", response_model=FeedResponse)
def get_feed(
    feed_type: str = Query("following", description="following, discover, or trending"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized feed.
    
    **Feed Types:**
    - `following`: Posts from users you follow
    - `discover`: Public posts from everyone
    - `trending`: Popular posts from last 24 hours
    """
    try:
        posts, total = SocialService.get_feed(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            feed_type=feed_type
        )
        
        post_responses = [post_to_response(post, current_user.id, db) for post in posts]
        
        return FeedResponse(
            posts=post_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feed: {str(e)}")


@router.get("/posts/{post_id}", response_model=PostDetailResponse)
def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific post with comments."""
    
    post = SocialService.get_post(db, post_id, current_user.id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get comments
    comments, _ = SocialService.get_post_comments(db, post_id)
    
    # Convert to response
    post_response = post_to_response(post, current_user.id, db)
    
    # Add comments
    comment_responses = []
    for comment in comments:
        user = UserBasic(
            id=comment.user.id,
            full_name=comment.user.full_name,
            username=comment.user.username,
            role=comment.user.role
        )
        
        # Get replies
        replies = SocialService.get_comment_replies(db, comment.id)
        reply_responses = []
        for reply in replies:
            reply_user = UserBasic(
                id=reply.user.id,
                full_name=reply.user.full_name,
                username=reply.user.username,
                role=reply.user.role
            )
            reply_responses.append(CommentResponse(
                id=reply.id,
                post_id=reply.post_id,
                user=reply_user,
                parent_comment_id=reply.parent_comment_id,
                content=reply.content,
                like_count=reply.like_count,
                is_edited=reply.is_edited,
                created_at=reply.created_at,
                updated_at=reply.updated_at,
                replies=[]
            ))
        
        comment_responses.append(CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            user=user,
            parent_comment_id=comment.parent_comment_id,
            content=comment.content,
            like_count=comment.like_count,
            is_edited=comment.is_edited,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=reply_responses
        ))
    
    # Get poll results if poll
    poll_results = None
    if post.post_type == "poll":
        poll_results = SocialService.get_poll_results(db, post_id)
    
    return PostDetailResponse(
        **post_response.dict(),
        comments=comment_responses,
        poll_results=poll_results
    )


@router.get("/users/{user_id}/posts", response_model=FeedResponse)
def get_user_posts(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get posts by a specific user."""
    
    try:
        posts, total = SocialService.get_user_posts(
            db=db,
            user_id=user_id,
            current_user_id=current_user.id,
            page=page,
            page_size=page_size
        )
        
        post_responses = [post_to_response(post, current_user.id, db) for post in posts]
        
        return FeedResponse(
            posts=post_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user posts: {str(e)}")


@router.put("/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: str,
    update_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a post."""
    
    try:
        updates = update_data.dict(exclude_unset=True)
        post = SocialService.update_post(db, post_id, current_user.id, **updates)
        return post_to_response(post, current_user.id, db)
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")


@router.delete("/posts/{post_id}", response_model=MessageResponse)
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a post."""
    
    try:
        SocialService.delete_post(db, post_id, current_user.id)
        return MessageResponse(message="Post deleted successfully")
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")


# ================== LIKE ENDPOINTS ==================

@router.post("/posts/{post_id}/like", response_model=LikeResponse)
def toggle_post_like(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Like or unlike a post."""
    
    try:
        is_liked, like_count = SocialService.toggle_post_like(db, post_id, current_user.id)
        return LikeResponse(
            success=True,
            is_liked=is_liked,
            like_count=like_count
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle like: {str(e)}")


# ================== COMMENT ENDPOINTS ==================

@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: str,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a comment on a post."""
    
    try:
        comment = SocialService.create_comment(
            db=db,
            post_id=post_id,
            user_id=current_user.id,
            content=comment_data.content,
            parent_comment_id=comment_data.parent_comment_id
        )
        
        user = UserBasic(
            id=comment.user.id,
            full_name=comment.user.full_name,
            username=comment.user.username,
            role=comment.user.role
        )
        
        return CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            user=user,
            parent_comment_id=comment.parent_comment_id,
            content=comment.content,
            like_count=comment.like_count,
            is_edited=comment.is_edited,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_post_comments(
    post_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comments for a post with threading support."""
    
    try:
        comments, total = SocialService.get_post_comments(db, post_id, page, page_size)
        
        comment_responses = []
        for comment in comments:
            user = UserBasic(
                id=comment.user.id,
                full_name=comment.user.full_name,
                username=comment.user.username,
                role=comment.user.role
            )
            
            # Get replies for top-level comments
            reply_responses = []
            if not comment.parent_comment_id:
                replies = SocialService.get_comment_replies(db, comment.id)
                for reply in replies:
                    reply_user = UserBasic(
                        id=reply.user.id,
                        full_name=reply.user.full_name,
                        username=reply.user.username,
                        role=reply.user.role
                    )
                    reply_responses.append(CommentResponse(
                        id=reply.id,
                        post_id=reply.post_id,
                        user=reply_user,
                        parent_comment_id=reply.parent_comment_id,
                        content=reply.content,
                        like_count=reply.like_count,
                        is_edited=reply.is_edited,
                        created_at=reply.created_at,
                        updated_at=reply.updated_at,
                        replies=[]
                    ))
            
            comment_responses.append(CommentResponse(
                id=comment.id,
                post_id=comment.post_id,
                user=user,
                parent_comment_id=comment.parent_comment_id,
                content=comment.content,
                like_count=comment.like_count,
                is_edited=comment.is_edited,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                replies=reply_responses
            ))
        
        return comment_responses
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: str,
    update_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a comment."""
    
    try:
        comment = SocialService.update_comment(db, comment_id, current_user.id, update_data.content)
        
        user = UserBasic(
            id=comment.user.id,
            full_name=comment.user.full_name,
            username=comment.user.username,
            role=comment.user.role
        )
        
        return CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            user=user,
            parent_comment_id=comment.parent_comment_id,
            content=comment.content,
            like_count=comment.like_count,
            is_edited=comment.is_edited,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")


@router.delete("/comments/{comment_id}", response_model=MessageResponse)
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment."""
    
    try:
        SocialService.delete_comment(db, comment_id, current_user.id)
        return MessageResponse(message="Comment deleted successfully")
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")


# ================== FOLLOW ENDPOINTS ==================

@router.post("/users/{user_id}/follow", response_model=FollowResponse)
def toggle_follow(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Follow or unfollow a user."""
    
    try:
        is_following, follower_count, following_count = SocialService.toggle_follow(
            db=db,
            follower_id=current_user.id,
            following_id=user_id
        )
        
        # Send notifications if following (not unfollowing)
        if is_following:
            from app.services.notification_service import NotificationService
            notif_service = NotificationService(db)
            
            # Notify user about new follower
            notif_service.notify_new_follower(
                user_id=user_id,
                follower_id=current_user.id
            )
            
            # Check if this creates a mutual follow
            is_mutual = SocialService.is_following(db, user_id, current_user.id)
            if is_mutual:
                # Notify both users about mutual follow
                notif_service.notify_mutual_follow(
                    user_id=user_id,
                    follower_id=current_user.id
                )
                notif_service.notify_mutual_follow(
                    user_id=current_user.id,
                    follower_id=user_id
                )
            
            # Check for follower milestones
            milestones = [100, 500, 1000, 5000, 10000, 50000, 100000]
            if follower_count in milestones:
                notif_service.notify_follower_milestone(
                    user_id=user_id,
                    milestone=follower_count
                )
        
        return FollowResponse(
            success=True,
            is_following=is_following,
            follower_count=follower_count,
            following_count=following_count
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle follow: {str(e)}")


@router.get("/users/{user_id}/followers", response_model=FollowListResponse)
def get_followers(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of followers."""
    
    followers, total = SocialService.get_followers(db, user_id, page, page_size)
    
    user_responses = []
    for follow in followers:
        user = UserBasic(
            id=follow.follower.id,
            full_name=follow.follower.full_name,
            username=follow.follower.username,
            role=follow.follower.role
        )
        
        is_following_back = SocialService.is_following(db, current_user.id, follow.follower_id)
        
        user_responses.append(FollowerResponse(
            user=user,
            followed_at=follow.created_at,
            is_following_back=is_following_back
        ))
    
    return FollowListResponse(
        users=user_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/users/{user_id}/following", response_model=FollowListResponse)
def get_following(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of users being followed."""
    
    following, total = SocialService.get_following(db, user_id, page, page_size)
    
    user_responses = []
    for follow in following:
        user = UserBasic(
            id=follow.following.id,
            full_name=follow.following.full_name,
            username=follow.following.username,
            role=follow.following.role
        )
        
        is_following_back = SocialService.is_following(db, follow.following_id, current_user.id)
        
        user_responses.append(FollowerResponse(
            user=user,
            followed_at=follow.created_at,
            is_following_back=is_following_back
        ))
    
    return FollowListResponse(
        users=user_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/users/{user_id}/follow-stats", response_model=FollowStatsResponse)
def get_follow_stats(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get follow statistics for a user."""
    
    stats = SocialService.get_follow_stats(db, user_id)
    return FollowStatsResponse(**stats)


# ================== BOOKMARK ENDPOINTS ==================

@router.post("/posts/{post_id}/bookmark", response_model=BookmarkResponse)
def toggle_bookmark(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bookmark or unbookmark a post."""
    
    try:
        is_bookmarked = SocialService.toggle_bookmark(db, post_id, current_user.id)
        return BookmarkResponse(
            success=True,
            is_bookmarked=is_bookmarked
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle bookmark: {str(e)}")


@router.get("/bookmarks", response_model=FeedResponse)
def get_bookmarks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bookmarked posts."""
    
    posts, total = SocialService.get_bookmarks(db, current_user.id, page, page_size)
    
    post_responses = [post_to_response(post, current_user.id, db) for post in posts]
    
    return FeedResponse(
        posts=post_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


# ================== POLL ENDPOINTS ==================

@router.post("/posts/{post_id}/vote", response_model=PollVoteResponse)
def vote_poll(
    post_id: str,
    vote_data: PollVoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vote on a poll."""
    
    try:
        results = SocialService.vote_poll(db, post_id, current_user.id, vote_data.option_index)
        return PollVoteResponse(
            success=True,
            message="Vote recorded successfully",
            poll_results=results
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to vote: {str(e)}")


# ==========================================
# TASK 7.3: ENHANCED FOLLOW SYSTEM ENDPOINTS
# ==========================================

# ========== Follow Suggestions ==========

@router.get("/suggestions/follow", response_model=FollowSuggestionsResponse)
async def get_follow_suggestions(
    type: str = "all",  # all, similar, trending, mutual, nearby
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized follow suggestions
    
    - **type**: Suggestion type (all, similar, trending, mutual)
    - **limit**: Number of suggestions (max 50)
    """
    if limit > 50:
        limit = 50
    
    suggestions = SocialService.get_follow_suggestions(
        db=db,
        user_id=current_user.id,
        suggestion_type=type,
        limit=limit
    )
    
    # Check if user is already following suggested users
    following_ids = set([
        f[0] for f in db.query(Follow.following_id).filter(
            Follow.follower_id == current_user.id
        ).all()
    ])
    
    # Format response
    suggestion_list = []
    for sugg in suggestions:
        user = sugg["user"]
        
        # Get avatar from profile if exists
        avatar_url = None
        if hasattr(user, 'artist_profile') and user.artist_profile:
            avatar_url = user.artist_profile.avatar_url
        elif hasattr(user, 'dj_profile') and user.dj_profile:
            avatar_url = user.dj_profile.avatar_url
        elif hasattr(user, 'producer_profile') and user.producer_profile:
            avatar_url = user.producer_profile.avatar_url
        elif hasattr(user, 'fan_profile') and user.fan_profile:
            avatar_url = user.fan_profile.avatar_url
        
        # Get follower count
        follower_count = db.query(Follow).filter(Follow.following_id == user.id).count()
        
        suggestion_list.append({
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "profile_type": user.role,
            "is_verified": getattr(user, 'is_verified', False),
            "avatar_url": avatar_url,
            "follower_count": follower_count,
            "mutual_followers": SocialService._count_mutual_followers(db, current_user.id, user.id),
            "reason": sugg["reason"],
            "type": sugg["type"],
            "score": sugg["score"],
            "is_following": user.id in following_ids
        })
    
    return {
        "suggestions": suggestion_list,
        "total": len(suggestion_list)
    }


@router.post("/suggestions/{user_id}/dismiss")
async def dismiss_follow_suggestion(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dismiss a follow suggestion
    
    - **user_id**: ID of the suggested user to dismiss
    """
    success = SocialService.dismiss_suggestion(
        db=db,
        user_id=current_user.id,
        suggested_user_id=user_id
    )
    
    if success:
        return {"message": "Suggestion dismissed"}
    else:
        raise HTTPException(status_code=400, detail="Failed to dismiss suggestion")


# ========== Trending Creators ==========

@router.get("/trending/creators", response_model=TrendingCreatorsResponse)
async def get_trending_creators(
    genre: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get trending creators
    
    - **genre**: Filter by genre (optional)
    - **location**: Filter by location (optional)
    - **limit**: Number of results (max 50)
    """
    if limit > 50:
        limit = 50
    
    trending = SocialService.get_trending_creators(
        db=db,
        genre=genre,
        location=location,
        limit=limit
    )
    
    # Format response
    trending_list = []
    for trend in trending:
        user = trend["user"]
        
        # Get avatar from profile
        avatar_url = None
        if hasattr(user, 'artist_profile') and user.artist_profile:
            avatar_url = user.artist_profile.avatar_url
        elif hasattr(user, 'dj_profile') and user.dj_profile:
            avatar_url = user.dj_profile.avatar_url
        elif hasattr(user, 'producer_profile') and user.producer_profile:
            avatar_url = user.producer_profile.avatar_url
        
        # Get follower count
        follower_count = db.query(Follow).filter(Follow.following_id == user.id).count()
        
        trending_item = {
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "profile_type": user.role,
            "is_verified": getattr(user, 'is_verified', False),
            "avatar_url": avatar_url,
            "follower_count": follower_count,
            "trending_score": trend["trending_score"],
            "follower_growth_rate": trend["follower_growth_rate"],
            "engagement_rate": trend["engagement_rate"],
            "recent_posts_count": trend["recent_posts_count"],
            "recent_track": None
        }
        
        # Add recent track if available
        if trend["recent_track"]:
            post = trend["recent_track"]
            if post.track_id:
                track = db.query(Track).filter(Track.id == post.track_id).first()
                if track:
                    trending_item["recent_track"] = {
                        "title": track.title,
                        "play_count": getattr(track, 'play_count', 0)
                    }
        
        trending_list.append(trending_item)
    
    return {
        "trending": trending_list,
        "period": "last_7_days",
        "total": len(trending_list)
    }


# ========== Similar Artists ==========

@router.get("/similar-artists/{user_id}", response_model=SimilarArtistsResponse)
async def get_similar_artists(
    user_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get artists similar to a specific user
    
    - **user_id**: Target user ID
    - **limit**: Number of results (max 50)
    """
    if limit > 50:
        limit = 50
    
    # Get target user
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    similar = SocialService.get_similar_artists(
        db=db,
        user_id=current_user.id,
        target_user_id=user_id,
        limit=limit
    )
    
    # Check if current user is following suggested users
    following_ids = set([
        f[0] for f in db.query(Follow.following_id).filter(
            Follow.follower_id == current_user.id
        ).all()
    ])
    
    # Format response
    similar_list = []
    for item in similar:
        user = item["user"]
        
        # Get avatar from profile
        avatar_url = None
        if hasattr(user, 'artist_profile') and user.artist_profile:
            avatar_url = user.artist_profile.avatar_url
        elif hasattr(user, 'dj_profile') and user.dj_profile:
            avatar_url = user.dj_profile.avatar_url
        elif hasattr(user, 'producer_profile') and user.producer_profile:
            avatar_url = user.producer_profile.avatar_url
        
        # Get follower count
        follower_count = db.query(Follow).filter(Follow.following_id == user.id).count()
        
        similar_list.append({
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "profile_type": user.role,
            "is_verified": getattr(user, 'is_verified', False),
            "avatar_url": avatar_url,
            "follower_count": follower_count,
            "similarity_score": item["similarity_score"],
            "reason": item["reason"],
            "is_following": user.id in following_ids
        })
    
    return {
        "similar_artists": similar_list,
        "target_user": target_user.username,
        "total": len(similar_list)
    }


# ========== Verification ==========

@router.post("/verification/request", response_model=VerificationResponse)
async def request_verification(
    request: VerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request account verification
    
    - **reason**: Reason for verification request
    - **social_links**: Social media profile links for verification
    """
    result = SocialService.request_verification(
        db=db,
        user_id=current_user.id,
        reason=request.reason,
        social_links=request.social_links
    )
    
    return result


@router.get("/verification/status", response_model=VerificationStatusResponse)
async def get_verification_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's verification status
    """
    status = SocialService.get_verification_status(db=db, user_id=current_user.id)
    return status


# ========== Notifications ==========

@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    type: Optional[str] = None,
    unread_only: bool = False,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's notifications
    
    - **type**: Filter by notification type (optional)
    - **unread_only**: Show only unread notifications
    - **page**: Page number
    - **page_size**: Items per page
    """
    from app.services.notification_service import NotificationService
    import json
    
    notif_service = NotificationService(db)
    result = notif_service.get_notifications(
        user_id=current_user.id,
        notification_type=type,
        unread_only=unread_only,
        page=page,
        page_size=page_size
    )
    
    # Format notifications
    notifications = []
    for notif in result["notifications"]:
        notifications.append({
            "id": notif.id,
            "type": notif.type,
            "title": notif.title,
            "message": notif.message,
            "data": json.loads(notif.data) if notif.data else None,
            "is_read": notif.is_read,
            "created_at": notif.created_at,
            "read_at": notif.read_at
        })
    
    return {
        "notifications": notifications,
        "total": result["total"],
        "unread_count": result["unread_count"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"]
    }


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unread notification count
    """
    from app.services.notification_service import NotificationService
    
    notif_service = NotificationService(db)
    count = notif_service.get_unread_count(current_user.id)
    
    return {"unread_count": count}


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read
    
    - **notification_id**: Notification ID
    """
    from app.services.notification_service import NotificationService
    
    notif_service = NotificationService(db)
    success = notif_service.mark_as_read(notification_id, current_user.id)
    
    if success:
        return {"message": "Notification marked as read"}
    else:
        raise HTTPException(status_code=404, detail="Notification not found")


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read
    
    - **type**: Notification type (optional, marks all types if not specified)
    """
    from app.services.notification_service import NotificationService
    
    notif_service = NotificationService(db)
    count = notif_service.mark_all_as_read(current_user.id, type)
    
    return {"message": f"Marked {count} notifications as read", "count": count}


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a notification
    
    - **notification_id**: Notification ID
    """
    from app.services.notification_service import NotificationService
    
    notif_service = NotificationService(db)
    success = notif_service.delete_notification(notification_id, current_user.id)
    
    if success:
        return {"message": "Notification deleted"}
    else:
        raise HTTPException(status_code=404, detail="Notification not found")


# ========== Notification Preferences ==========

@router.get("/notification-preferences", response_model=NotificationPreferenceResponse)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's notification preferences
    """
    from app.services.notification_service import NotificationService
    
    notif_service = NotificationService(db)
    prefs = notif_service.get_or_create_preferences(current_user.id)
    
    return {
        "new_follower": prefs.new_follower,
        "mutual_follow": prefs.mutual_follow,
        "verification_granted": prefs.verification_granted,
        "follow_suggestion": prefs.follow_suggestion,
        "follower_milestone": prefs.follower_milestone,
        "post_like": prefs.post_like,
        "post_comment": prefs.post_comment,
        "post_share": prefs.post_share,
        "updated_at": prefs.updated_at
    }


@router.put("/notification-preferences", response_model=NotificationPreferenceResponse)
async def update_notification_preferences(
    preferences: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update notification preferences
    
    - **preferences**: Preference settings to update
    """
    from app.services.notification_service import NotificationService
    
    notif_service = NotificationService(db)
    prefs = notif_service.update_preferences(
        user_id=current_user.id,
        preferences=preferences.dict(exclude_unset=True)
    )
    
    return {
        "new_follower": prefs.new_follower,
        "mutual_follow": prefs.mutual_follow,
        "verification_granted": prefs.verification_granted,
        "follow_suggestion": prefs.follow_suggestion,
        "follower_milestone": prefs.follower_milestone,
        "post_like": prefs.post_like,
        "post_comment": prefs.post_comment,
        "post_share": prefs.post_share,
        "updated_at": prefs.updated_at
    }
