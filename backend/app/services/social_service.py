"""
Social Feed Service
Task 7.1: Social Feed

Business logic for social feed, posts, comments, follows, etc.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import json

from app.models.social import (
    Post, PostLike, PostComment, CommentLike, PostShare, 
    Follow, PostBookmark, PollVote
)
from app.models.user import User
from app.models.track import Track


class SocialService:
    """Service for social feed operations"""
    
    # ================== POST OPERATIONS ==================
    
    @staticmethod
    def create_post(
        db: Session,
        user_id: str,
        post_type: str,
        content: Optional[str] = None,
        media_url: Optional[str] = None,
        track_id: Optional[str] = None,
        event_date: Optional[str] = None,
        poll_options: Optional[List[str]] = None,
        poll_duration_hours: int = 24,
        visibility: str = "public"
    ) -> Post:
        """Create a new post"""
        
        # Validate post type
        valid_types = ["status", "track_share", "event", "milestone", "poll"]
        if post_type not in valid_types:
            raise ValueError(f"Invalid post type. Must be one of: {', '.join(valid_types)}")
        
        # Track share must have track_id
        if post_type == "track_share" and not track_id:
            raise ValueError("Track share posts must include a track_id")
        
        # Poll must have options
        if post_type == "poll" and not poll_options:
            raise ValueError("Poll posts must include poll_options")
        
        # Create post
        post = Post(
            id=str(uuid.uuid4()),
            user_id=user_id,
            post_type=post_type,
            content=content,
            media_url=media_url,
            track_id=track_id,
            event_date=event_date,
            visibility=visibility
        )
        
        # Handle poll
        if post_type == "poll" and poll_options:
            post.poll_options = json.dumps(poll_options)
            poll_ends = datetime.utcnow() + timedelta(hours=poll_duration_hours)
            post.poll_ends_at = poll_ends.isoformat()
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        return post
    
    @staticmethod
    def get_post(db: Session, post_id: str, current_user_id: Optional[str] = None) -> Optional[Post]:
        """Get a post by ID with visibility check"""
        
        post = db.query(Post).filter(Post.id == post_id).first()
        
        if not post:
            return None
        
        # Check visibility
        if post.visibility == "private" and post.user_id != current_user_id:
            return None
        
        if post.visibility == "followers":
            if current_user_id != post.user_id:
                # Check if current user follows the post author
                is_following = db.query(Follow).filter(
                    Follow.follower_id == current_user_id,
                    Follow.following_id == post.user_id
                ).first() is not None
                
                if not is_following:
                    return None
        
        return post
    
    @staticmethod
    def get_feed(
        db: Session,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        feed_type: str = "following"  # following, discover, trending
    ) -> Tuple[List[Post], int]:
        """Get personalized feed for user"""
        
        query = db.query(Post)
        
        if feed_type == "following":
            # Get posts from users that current user follows
            following_ids = db.query(Follow.following_id).filter(
                Follow.follower_id == user_id
            ).all()
            following_ids = [fid[0] for fid in following_ids]
            
            # Include own posts
            following_ids.append(user_id)
            
            query = query.filter(
                and_(
                    Post.user_id.in_(following_ids),
                    or_(
                        Post.visibility == "public",
                        Post.visibility == "followers"
                    )
                )
            )
        
        elif feed_type == "discover":
            # Public posts from everyone
            query = query.filter(Post.visibility == "public")
        
        elif feed_type == "trending":
            # Posts with high engagement in last 24 hours
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            query = query.filter(
                and_(
                    Post.visibility == "public",
                    Post.created_at >= yesterday
                )
            ).order_by(
                desc(Post.like_count + Post.comment_count * 2 + Post.share_count * 3)
            )
        
        # Count total
        total = query.count()
        
        # Order by created_at for following/discover, already ordered for trending
        if feed_type != "trending":
            query = query.order_by(desc(Post.created_at))
        
        # Paginate
        posts = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return posts, total
    
    @staticmethod
    def get_user_posts(
        db: Session,
        user_id: str,
        current_user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Post], int]:
        """Get posts by a specific user"""
        
        query = db.query(Post).filter(Post.user_id == user_id)
        
        # Filter by visibility
        if current_user_id == user_id:
            # Own posts - see all
            pass
        else:
            # Check if following
            is_following = db.query(Follow).filter(
                Follow.follower_id == current_user_id,
                Follow.following_id == user_id
            ).first() is not None
            
            if is_following:
                # Can see public and followers posts
                query = query.filter(
                    or_(
                        Post.visibility == "public",
                        Post.visibility == "followers"
                    )
                )
            else:
                # Only public posts
                query = query.filter(Post.visibility == "public")
        
        total = query.count()
        posts = query.order_by(desc(Post.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        
        return posts, total
    
    @staticmethod
    def update_post(db: Session, post_id: str, user_id: str, **updates) -> Post:
        """Update a post"""
        
        post = db.query(Post).filter(
            Post.id == post_id,
            Post.user_id == user_id
        ).first()
        
        if not post:
            raise ValueError("Post not found or access denied")
        
        for key, value in updates.items():
            if value is not None and hasattr(post, key):
                setattr(post, key, value)
        
        post.updated_at = datetime.utcnow().isoformat()
        
        db.commit()
        db.refresh(post)
        
        return post
    
    @staticmethod
    def delete_post(db: Session, post_id: str, user_id: str) -> bool:
        """Delete a post"""
        
        post = db.query(Post).filter(
            Post.id == post_id,
            Post.user_id == user_id
        ).first()
        
        if not post:
            raise ValueError("Post not found or access denied")
        
        db.delete(post)
        db.commit()
        
        return True
    
    # ================== LIKE OPERATIONS ==================
    
    @staticmethod
    def toggle_post_like(db: Session, post_id: str, user_id: str) -> Tuple[bool, int]:
        """Like or unlike a post. Returns (is_liked, like_count)"""
        
        # Check if already liked
        existing_like = db.query(PostLike).filter(
            PostLike.post_id == post_id,
            PostLike.user_id == user_id
        ).first()
        
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise ValueError("Post not found")
        
        if existing_like:
            # Unlike
            db.delete(existing_like)
            post.like_count = max(0, post.like_count - 1)
            is_liked = False
        else:
            # Like
            like = PostLike(
                id=str(uuid.uuid4()),
                post_id=post_id,
                user_id=user_id
            )
            db.add(like)
            post.like_count += 1
            is_liked = True
        
        db.commit()
        
        return is_liked, post.like_count
    
    @staticmethod
    def is_post_liked(db: Session, post_id: str, user_id: str) -> bool:
        """Check if user has liked a post"""
        
        like = db.query(PostLike).filter(
            PostLike.post_id == post_id,
            PostLike.user_id == user_id
        ).first()
        
        return like is not None
    
    # ================== COMMENT OPERATIONS ==================
    
    @staticmethod
    def create_comment(
        db: Session,
        post_id: str,
        user_id: str,
        content: str,
        parent_comment_id: Optional[str] = None
    ) -> PostComment:
        """Create a comment on a post"""
        
        # Verify post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise ValueError("Post not found")
        
        # Verify parent comment if provided
        if parent_comment_id:
            parent = db.query(PostComment).filter(PostComment.id == parent_comment_id).first()
            if not parent:
                raise ValueError("Parent comment not found")
        
        comment = PostComment(
            id=str(uuid.uuid4()),
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id
        )
        
        db.add(comment)
        
        # Update post comment count
        post.comment_count += 1
        
        db.commit()
        db.refresh(comment)
        
        return comment
    
    @staticmethod
    def get_post_comments(
        db: Session,
        post_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[PostComment], int]:
        """Get comments for a post (top-level only, use replies for nested)"""
        
        query = db.query(PostComment).filter(
            PostComment.post_id == post_id,
            PostComment.parent_comment_id.is_(None)
        )
        
        total = query.count()
        comments = query.order_by(desc(PostComment.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        
        return comments, total
    
    @staticmethod
    def get_comment_replies(db: Session, comment_id: str) -> List[PostComment]:
        """Get replies to a comment"""
        
        replies = db.query(PostComment).filter(
            PostComment.parent_comment_id == comment_id
        ).order_by(PostComment.created_at).all()
        
        return replies
    
    @staticmethod
    def update_comment(db: Session, comment_id: str, user_id: str, content: str) -> PostComment:
        """Update a comment"""
        
        comment = db.query(PostComment).filter(
            PostComment.id == comment_id,
            PostComment.user_id == user_id
        ).first()
        
        if not comment:
            raise ValueError("Comment not found or access denied")
        
        comment.content = content
        comment.is_edited = True
        comment.updated_at = datetime.utcnow().isoformat()
        
        db.commit()
        db.refresh(comment)
        
        return comment
    
    @staticmethod
    def delete_comment(db: Session, comment_id: str, user_id: str) -> bool:
        """Delete a comment"""
        
        comment = db.query(PostComment).filter(
            PostComment.id == comment_id,
            PostComment.user_id == user_id
        ).first()
        
        if not comment:
            raise ValueError("Comment not found or access denied")
        
        # Update post comment count
        post = db.query(Post).filter(Post.id == comment.post_id).first()
        if post:
            # Count all comments being deleted (including nested replies)
            def count_nested(comment_id):
                count = 1
                replies = db.query(PostComment).filter(PostComment.parent_comment_id == comment_id).all()
                for reply in replies:
                    count += count_nested(reply.id)
                return count
            
            deleted_count = count_nested(comment.id)
            post.comment_count = max(0, post.comment_count - deleted_count)
        
        db.delete(comment)
        db.commit()
        
        return True
    
    # ================== FOLLOW OPERATIONS ==================
    
    @staticmethod
    def toggle_follow(db: Session, follower_id: str, following_id: str) -> Tuple[bool, int, int]:
        """Follow or unfollow a user. Returns (is_following, follower_count, following_count)"""
        
        if follower_id == following_id:
            raise ValueError("Cannot follow yourself")
        
        # Check if already following
        existing_follow = db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        ).first()
        
        if existing_follow:
            # Unfollow
            db.delete(existing_follow)
            is_following = False
        else:
            # Follow
            follow = Follow(
                id=str(uuid.uuid4()),
                follower_id=follower_id,
                following_id=following_id
            )
            db.add(follow)
            is_following = True
        
        db.commit()
        
        # Get counts
        follower_count = db.query(func.count(Follow.id)).filter(
            Follow.following_id == following_id
        ).scalar() or 0
        
        following_count = db.query(func.count(Follow.id)).filter(
            Follow.follower_id == following_id
        ).scalar() or 0
        
        return is_following, follower_count, following_count
    
    @staticmethod
    def is_following(db: Session, follower_id: str, following_id: str) -> bool:
        """Check if user is following another user"""
        
        follow = db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        ).first()
        
        return follow is not None
    
    @staticmethod
    def get_followers(
        db: Session,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Follow], int]:
        """Get list of followers"""
        
        query = db.query(Follow).filter(Follow.following_id == user_id)
        total = query.count()
        followers = query.order_by(desc(Follow.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        
        return followers, total
    
    @staticmethod
    def get_following(
        db: Session,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Follow], int]:
        """Get list of users being followed"""
        
        query = db.query(Follow).filter(Follow.follower_id == user_id)
        total = query.count()
        following = query.order_by(desc(Follow.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        
        return following, total
    
    @staticmethod
    def get_follow_stats(db: Session, user_id: str) -> Dict[str, int]:
        """Get follow statistics"""
        
        follower_count = db.query(func.count(Follow.id)).filter(
            Follow.following_id == user_id
        ).scalar() or 0
        
        following_count = db.query(func.count(Follow.id)).filter(
            Follow.follower_id == user_id
        ).scalar() or 0
        
        # Get mutual followers (users who follow and are followed by this user)
        followers = db.query(Follow.follower_id).filter(Follow.following_id == user_id).all()
        following = db.query(Follow.following_id).filter(Follow.follower_id == user_id).all()
        
        follower_set = {f[0] for f in followers}
        following_set = {f[0] for f in following}
        mutual = len(follower_set & following_set)
        
        return {
            "follower_count": follower_count,
            "following_count": following_count,
            "mutual_followers": mutual
        }
    
    # ================== BOOKMARK OPERATIONS ==================
    
    @staticmethod
    def toggle_bookmark(db: Session, post_id: str, user_id: str) -> bool:
        """Bookmark or unbookmark a post. Returns is_bookmarked"""
        
        existing_bookmark = db.query(PostBookmark).filter(
            PostBookmark.post_id == post_id,
            PostBookmark.user_id == user_id
        ).first()
        
        if existing_bookmark:
            db.delete(existing_bookmark)
            is_bookmarked = False
        else:
            bookmark = PostBookmark(
                id=str(uuid.uuid4()),
                post_id=post_id,
                user_id=user_id
            )
            db.add(bookmark)
            is_bookmarked = True
        
        db.commit()
        
        return is_bookmarked
    
    @staticmethod
    def get_bookmarks(
        db: Session,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Post], int]:
        """Get user's bookmarked posts"""
        
        query = db.query(Post).join(PostBookmark).filter(
            PostBookmark.user_id == user_id
        )
        
        total = query.count()
        posts = query.order_by(desc(PostBookmark.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        
        return posts, total
    
    # ================== POLL OPERATIONS ==================
    
    @staticmethod
    def vote_poll(db: Session, post_id: str, user_id: str, option_index: int) -> Dict[str, Any]:
        """Vote on a poll"""
        
        post = db.query(Post).filter(Post.id == post_id).first()
        
        if not post or post.post_type != "poll":
            raise ValueError("Poll not found")
        
        # Check if poll has ended
        if post.poll_ends_at:
            poll_end = datetime.fromisoformat(post.poll_ends_at)
            if datetime.utcnow() > poll_end:
                raise ValueError("Poll has ended")
        
        # Parse poll options
        poll_options = json.loads(post.poll_options)
        
        if option_index < 0 or option_index >= len(poll_options):
            raise ValueError("Invalid option index")
        
        # Check if already voted
        existing_vote = db.query(PollVote).filter(
            PollVote.post_id == post_id,
            PollVote.user_id == user_id
        ).first()
        
        if existing_vote:
            # Update vote
            existing_vote.option_index = option_index
        else:
            # New vote
            vote = PollVote(
                id=str(uuid.uuid4()),
                post_id=post_id,
                user_id=user_id,
                option_index=option_index
            )
            db.add(vote)
        
        db.commit()
        
        # Return poll results
        return SocialService.get_poll_results(db, post_id)
    
    @staticmethod
    def get_poll_results(db: Session, post_id: str) -> List[Dict[str, Any]]:
        """Get poll results"""
        
        post = db.query(Post).filter(Post.id == post_id).first()
        
        if not post or post.post_type != "poll":
            return []
        
        poll_options = json.loads(post.poll_options)
        
        # Count votes for each option
        total_votes = db.query(func.count(PollVote.id)).filter(
            PollVote.post_id == post_id
        ).scalar() or 0
        
        results = []
        for i, option in enumerate(poll_options):
            vote_count = db.query(func.count(PollVote.id)).filter(
                PollVote.post_id == post_id,
                PollVote.option_index == i
            ).scalar() or 0
            
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            
            results.append({
                "option": option,
                "votes": vote_count,
                "percentage": round(percentage, 1)
            })
        
        return results


    # ==========================================
    # TASK 7.3: ENHANCED FOLLOW SYSTEM
    # ==========================================
    
    # ================== FOLLOW SUGGESTIONS ==================
    
    @staticmethod
    def get_follow_suggestions(
        db: Session,
        user_id: str,
        suggestion_type: str = "all",  # all, similar, trending, mutual, nearby
        limit: int = 10
    ) -> List[Dict]:
        """Get follow suggestions for a user"""
        
        # Get users already following or suggested
        following_ids = [f[0] for f in db.query(Follow.following_id).filter(Follow.follower_id == user_id).all()]
        following_ids.append(user_id)  # Don't suggest yourself
        
        # Get current user info
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return []
        
        suggestions = []
        
        if suggestion_type in ["all", "similar"]:
            # Suggest users with similar genres/profile type
            similar_users = db.query(User).filter(
                and_(
                    User.id.not_in(following_ids),
                    User.role == current_user.role
                )
            ).limit(5).all()
            
            for user in similar_users:
                suggestions.append({
                    "user": user,
                    "reason": f"Similar {user.role}",
                    "type": "similar",
                    "score": 75
                })
        
        if suggestion_type in ["all", "trending"]:
            # Suggest users with many followers
            # Get follower counts
            user_followers = db.query(
                User.id,
                func.count(Follow.id).label('follower_count')
            ).outerjoin(Follow, Follow.following_id == User.id).filter(
                User.id.not_in(following_ids)
            ).group_by(User.id).order_by(desc('follower_count')).limit(5).all()
            
            for user_id, follower_count in user_followers:
                if follower_count > 50:  # Only suggest if they have decent following
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        suggestions.append({
                            "user": user,
                            "reason": f"Popular {user.role}",
                            "type": "trending",
                            "score": 85
                        })
        
        if suggestion_type in ["all", "mutual"]:
            # Suggest mutual connections (friends of friends)
            mutual_query = db.query(User).join(
                Follow, Follow.following_id == User.id
            ).filter(
                and_(
                    Follow.follower_id.in_([f[0] for f in db.query(Follow.following_id).filter(Follow.follower_id == user_id).all()]),
                    User.id.not_in(following_ids)
                )
            ).limit(5).all()
            
            for user in mutual_query:
                mutual_count = SocialService._count_mutual_followers(db, user_id, user.id)
                suggestions.append({
                    "user": user,
                    "reason": f"{mutual_count} mutual connections",
                    "type": "mutual",
                    "score": 90
                })
        
        # Get verified users
        if suggestion_type in ["all"]:
            verified_users = db.query(User).filter(
                and_(
                    User.id.not_in(following_ids),
                    User.is_verified == True
                )
            ).limit(3).all()
            
            for user in verified_users:
                suggestions.append({
                    "user": user,
                    "reason": "Verified creator",
                    "type": "verified",
                    "score": 95
                })
        
        # Remove duplicates and sort by score
        seen_ids = set()
        unique_suggestions = []
        for sugg in suggestions:
            if sugg["user"].id not in seen_ids:
                seen_ids.add(sugg["user"].id)
                unique_suggestions.append(sugg)
        
        unique_suggestions.sort(key=lambda x: x["score"], reverse=True)
        
        return unique_suggestions[:limit]
    
    @staticmethod
    def _count_mutual_followers(db: Session, user1_id: str, user2_id: str) -> int:
        """Count mutual followers between two users"""
        user1_following = set([f[0] for f in db.query(Follow.following_id).filter(Follow.follower_id == user1_id).all()])
        user2_following = set([f[0] for f in db.query(Follow.following_id).filter(Follow.follower_id == user2_id).all()])
        return len(user1_following.intersection(user2_following))
    
    @staticmethod
    def dismiss_suggestion(db: Session, user_id: str, suggested_user_id: str) -> bool:
        """Dismiss a follow suggestion"""
        from app.models.social import FollowSuggestion
        
        # Check if suggestion exists
        suggestion = db.query(FollowSuggestion).filter(
            and_(
                FollowSuggestion.user_id == user_id,
                FollowSuggestion.suggested_user_id == suggested_user_id
            )
        ).first()
        
        if suggestion:
            suggestion.is_dismissed = True
            suggestion.dismissed_at = datetime.utcnow().isoformat()
        else:
            # Create dismissed suggestion record
            suggestion = FollowSuggestion(
                id=str(uuid.uuid4()),
                user_id=user_id,
                suggested_user_id=suggested_user_id,
                is_dismissed=True,
                dismissed_at=datetime.utcnow().isoformat()
            )
            db.add(suggestion)
        
        db.commit()
        return True
    
    # ================== TRENDING CREATORS ==================
    
    @staticmethod
    def get_trending_creators(
        db: Session,
        genre: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get trending creators based on recent activity"""
        
        # Calculate trending score based on:
        # - Follower count
        # - Recent post engagement
        # - Follower growth (simulated for now)
        
        # Get users with follower counts
        user_followers = db.query(
            User.id,
            func.count(Follow.id).label('follower_count')
        ).outerjoin(Follow, Follow.following_id == User.id).group_by(User.id).having(
            func.count(Follow.id) > 10
        ).order_by(desc('follower_count')).limit(limit * 2).all()
        
        # Get users with their recent activity
        trending = []
        for user_id, follower_count in user_followers:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                continue
            # Calculate engagement from recent posts
            recent_posts = db.query(Post).filter(
                and_(
                    Post.user_id == user.id,
                    Post.created_at >= (datetime.utcnow() - timedelta(days=7)).isoformat()
                )
            ).all()
            
            total_engagement = sum(
                post.like_count + post.comment_count + (post.share_count * 2)
                for post in recent_posts
            )
            
            # Calculate trending score
            follower_score = min(follower_count / 10, 100)  # Cap at 100
            engagement_score = min(total_engagement, 100)  # Cap at 100
            post_frequency_score = min(len(recent_posts) * 10, 100)  # Cap at 100
            
            trending_score = (
                follower_score * 0.4 +
                engagement_score * 0.4 +
                post_frequency_score * 0.2
            )
            
            # Simulated growth rate (in production, calculate from historical data)
            growth_rate = min((follower_count / 100) * 5, 50)  # 0-50%
            
            trending.append({
                "user": user,
                "trending_score": round(trending_score, 2),
                "follower_growth_rate": round(growth_rate, 1),
                "engagement_rate": round((total_engagement / max(follower_count, 1)) * 100, 1),
                "recent_posts_count": len(recent_posts),
                "recent_track": recent_posts[0] if recent_posts and recent_posts[0].post_type == "track_share" else None
            })
        
        # Sort by trending score
        trending.sort(key=lambda x: x["trending_score"], reverse=True)
        
        return trending[:limit]
    
    # ================== SIMILAR ARTISTS ==================
    
    @staticmethod
    def get_similar_artists(
        db: Session,
        user_id: str,
        target_user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get artists similar to a target user"""
        
        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            return []
        
        # Get users already following
        following_ids = [f[0] for f in db.query(Follow.following_id).filter(Follow.follower_id == user_id).all()]
        following_ids.append(user_id)
        following_ids.append(target_user_id)
        
        # Find users with same profile type
        similar = db.query(User).filter(
            and_(
                User.role == target_user.role,
                User.id.not_in(following_ids)
            )
        ).limit(limit).all()
        
        results = []
        for user in similar:
            # Calculate similarity score
            similarity_score = 70  # Base score
            
            # Get follower counts for comparison
            user_follower_count = db.query(func.count(Follow.id)).filter(
                Follow.following_id == user.id
            ).scalar() or 0
            
            target_follower_count = db.query(func.count(Follow.id)).filter(
                Follow.following_id == target_user_id
            ).scalar() or 0
            
            # Bonus if similar follower count
            follower_diff = abs(user_follower_count - target_follower_count)
            if follower_diff < 100:
                similarity_score += 15
            elif follower_diff < 500:
                similarity_score += 10
            
            # Bonus for verified users
            if getattr(user, 'is_verified', False):
                similarity_score += 10
            
            results.append({
                "user": user,
                "similarity_score": min(similarity_score, 100),
                "reason": f"Similar to @{target_user.username}"
            })
        
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return results
    
    # ================== USER VERIFICATION ==================
    
    @staticmethod
    def request_verification(
        db: Session,
        user_id: str,
        reason: str,
        social_links: Dict[str, str]
    ) -> Dict:
        """Request account verification"""
        from app.models.social import UserVerification
        
        # Check if user already verified
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if getattr(user, 'is_verified', False):
            return {
                "status": "already_verified",
                "message": "Your account is already verified"
            }
        
        # Check if there's a pending request
        pending = db.query(UserVerification).filter(
            and_(
                UserVerification.user_id == user_id,
                UserVerification.status == "pending"
            )
        ).first()
        
        if pending:
            return {
                "status": "pending",
                "request_id": pending.id,
                "message": "You already have a pending verification request",
                "submitted_at": pending.submitted_at
            }
        
        # Create new verification request
        verification_request = UserVerification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            status="pending",
            reason=reason,
            social_links=json.dumps(social_links),
            submitted_at=datetime.utcnow().isoformat()
        )
        
        db.add(verification_request)
        db.commit()
        db.refresh(verification_request)
        
        return {
            "status": "submitted",
            "request_id": verification_request.id,
            "message": "Verification request submitted successfully",
            "estimated_review": "2-5 business days"
        }
    
    @staticmethod
    def get_verification_status(db: Session, user_id: str) -> Dict:
        """Get user's verification status"""
        from app.models.social import UserVerification
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if verified
        if getattr(user, 'is_verified', False):
            return {
                "is_verified": True,
                "verification_date": getattr(user, 'verification_date', None),
                "badge_type": getattr(user, 'verification_badge_type', 'standard')
            }
        
        # Check for pending request
        request = db.query(UserVerification).filter(
            UserVerification.user_id == user_id
        ).order_by(desc(UserVerification.submitted_at)).first()
        
        if request:
            return {
                "is_verified": False,
                "has_request": True,
                "request_status": request.status,
                "submitted_at": request.submitted_at,
                "reviewed_at": request.reviewed_at,
                "rejection_reason": request.rejection_reason if request.status == "rejected" else None
            }
        
        return {
            "is_verified": False,
            "has_request": False,
            "can_apply": True
        }
