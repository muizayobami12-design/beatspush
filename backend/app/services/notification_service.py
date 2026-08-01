"""
Notification Service
Task 7.3: Enhanced Follow System

Handles creating, fetching, and managing notifications
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid
import json

from app.models.social import Notification, NotificationPreference
from app.models.user import User


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================
    # Create Notifications
    # ==========================================
    
    def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict] = None
    ) -> Notification:
        """Create a new notification"""
        
        # Check if user has this notification type enabled
        prefs = self.get_or_create_preferences(user_id)
        type_key = notification_type.replace("_", "").lower()
        
        # Check preference (default to True if not found)
        is_enabled = getattr(prefs, type_key, True) if hasattr(prefs, type_key) else True
        
        if not is_enabled:
            return None  # User has disabled this notification type
        
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=json.dumps(data) if data else None,
            is_read=False,
            created_at=datetime.utcnow().isoformat()
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def notify_new_follower(self, user_id: str, follower_id: str) -> Optional[Notification]:
        """Notify user about new follower"""
        follower = self.db.query(User).filter(User.id == follower_id).first()
        if not follower:
            return None
        
        # Get avatar from profile if exists
        avatar_url = None
        if hasattr(follower, 'profile') and follower.profile:
            avatar_url = getattr(follower.profile, 'avatar_url', None)
        
        return self.create_notification(
            user_id=user_id,
            notification_type="new_follower",
            title="New Follower",
            message=f"@{follower.username} started following you",
            data={
                "user_id": follower_id,
                "username": follower.username,
                "full_name": follower.full_name,
                "avatar_url": avatar_url,
                "is_verified": getattr(follower, 'is_verified', False)
            }
        )
    
    def notify_mutual_follow(self, user_id: str, follower_id: str) -> Optional[Notification]:
        """Notify user about mutual follow"""
        follower = self.db.query(User).filter(User.id == follower_id).first()
        if not follower:
            return None
        
        # Get avatar from profile if exists
        avatar_url = None
        if hasattr(follower, 'profile') and follower.profile:
            avatar_url = getattr(follower.profile, 'avatar_url', None)
        
        return self.create_notification(
            user_id=user_id,
            notification_type="mutual_follow",
            title="You're Now Mutuals",
            message=f"You and @{follower.username} now follow each other",
            data={
                "user_id": follower_id,
                "username": follower.username,
                "full_name": follower.full_name,
                "avatar_url": avatar_url
            }
        )
    
    def notify_verification_granted(self, user_id: str) -> Notification:
        """Notify user that verification was granted"""
        return self.create_notification(
            user_id=user_id,
            notification_type="verification_granted",
            title="You're Verified!",
            message="Congratulations! Your account has been verified",
            data={"badge_type": "standard"}
        )
    
    def notify_follower_milestone(self, user_id: str, milestone: int) -> Notification:
        """Notify user about follower milestone"""
        return self.create_notification(
            user_id=user_id,
            notification_type="follower_milestone",
            title="Follower Milestone!",
            message=f"🎉 You've reached {milestone:,} followers!",
            data={"milestone": milestone}
        )
    
    def notify_post_like(self, user_id: str, liker_id: str, post_id: str) -> Optional[Notification]:
        """Notify user about post like"""
        liker = self.db.query(User).filter(User.id == liker_id).first()
        if not liker:
            return None
        
        return self.create_notification(
            user_id=user_id,
            notification_type="post_like",
            title="New Like",
            message=f"@{liker.username} liked your post",
            data={
                "user_id": liker_id,
                "username": liker.username,
                "post_id": post_id
            }
        )
    
    def notify_post_comment(self, user_id: str, commenter_id: str, post_id: str, comment_preview: str) -> Optional[Notification]:
        """Notify user about post comment"""
        commenter = self.db.query(User).filter(User.id == commenter_id).first()
        if not commenter:
            return None
        
        return self.create_notification(
            user_id=user_id,
            notification_type="post_comment",
            title="New Comment",
            message=f"@{commenter.username}: {comment_preview[:50]}{'...' if len(comment_preview) > 50 else ''}",
            data={
                "user_id": commenter_id,
                "username": commenter.username,
                "post_id": post_id,
                "comment_preview": comment_preview
            }
        )
    
    # ==========================================
    # Fetch Notifications
    # ==========================================
    
    def get_notifications(
        self,
        user_id: str,
        notification_type: Optional[str] = None,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """Get user's notifications with pagination"""
        
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        # Filter by type
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        
        # Filter by read status
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        # Get total count
        total = query.count()
        
        # Get unread count
        unread_count = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).count()
        
        # Pagination
        offset = (page - 1) * page_size
        notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(page_size).all()
        
        return {
            "notifications": notifications,
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        return self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).count()
    
    # ==========================================
    # Mark as Read
    # ==========================================
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        notification.read_at = datetime.utcnow().isoformat()
        self.db.commit()
        
        return True
    
    def mark_all_as_read(self, user_id: str, notification_type: Optional[str] = None) -> int:
        """Mark all notifications as read"""
        query = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        
        count = query.count()
        
        query.update({
            "is_read": True,
            "read_at": datetime.utcnow().isoformat()
        }, synchronize_session=False)
        
        self.db.commit()
        
        return count
    
    # ==========================================
    # Delete Notifications
    # ==========================================
    
    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if not notification:
            return False
        
        self.db.delete(notification)
        self.db.commit()
        
        return True
    
    def delete_all_read(self, user_id: str) -> int:
        """Delete all read notifications"""
        notifications = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == True
            )
        ).all()
        
        count = len(notifications)
        
        for notification in notifications:
            self.db.delete(notification)
        
        self.db.commit()
        
        return count
    
    # ==========================================
    # Notification Preferences
    # ==========================================
    
    def get_or_create_preferences(self, user_id: str) -> NotificationPreference:
        """Get or create notification preferences"""
        prefs = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if not prefs:
            prefs = NotificationPreference(
                id=str(uuid.uuid4()),
                user_id=user_id,
                new_follower=True,
                mutual_follow=True,
                verification_granted=True,
                follow_suggestion=True,
                follower_milestone=True,
                post_like=True,
                post_comment=True,
                post_share=True
            )
            self.db.add(prefs)
            self.db.commit()
            self.db.refresh(prefs)
        
        return prefs
    
    def update_preferences(self, user_id: str, preferences: Dict) -> NotificationPreference:
        """Update notification preferences"""
        prefs = self.get_or_create_preferences(user_id)
        
        # Update fields
        for key, value in preferences.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        
        prefs.updated_at = datetime.utcnow().isoformat()
        self.db.commit()
        self.db.refresh(prefs)
        
        return prefs
