# Social Feed System - Design Document

## 1. Overview

The Social Feed system is the central content discovery and engagement hub for BeatPush. Users discover music, engage with creators, and build community through a personalized feed powered by a recommendation algorithm.

### 1.1 Design Goals

- Fast, responsive feed loading (< 2s initial load)
- Real-time updates for new content
- Scalable architecture for millions of posts
- Personalized content discovery
- Seamless integration with existing systems

### 1.2 Technology Stack

**Backend:**
- FastAPI (REST API)
- SQLAlchemy (ORM)
- PostgreSQL (database)
- Redis (caching)
- WebSocket (real-time updates)

**Frontend:**
- Next.js 14+ (React framework)
- TypeScript
- Tailwind CSS + Shadcn UI
- Zustand (state management)
- React Query (data fetching)

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────┐
│   Client    │
│  (Next.js)  │
└─────┬───────┘
      │
      │ REST API / WebSocket
      │
┌─────▼───────────────────────┐
│   FastAPI Backend           │
│  ┌───────────────────────┐  │
│  │  Feed Service         │  │
│  │  - Algorithm          │  │
│  │  - Ranking            │  │
│  └───────────────────────┘  │
│  ┌───────────────────────┐  │
│  │  Post Service         │  │
│  │  - CRUD operations    │  │
│  │  - Validation         │  │
│  └───────────────────────┘  │
│  ┌───────────────────────┐  │
│  │  Engagement Service   │  │
│  │  - Likes, Comments    │  │
│  │  - Shares, Saves      │  │
│  └───────────────────────┘  │
└─────┬───────────────────────┘
      │
      │
┌─────▼─────────────┐       ┌─────────────┐
│   PostgreSQL      │       │   Redis     │
│  - Posts          │       │  - Cache    │
│  - Likes          │       │  - Rankings │
│  - Comments       │       │             │
└───────────────────┘       └─────────────┘
```

### 2.2 Component Interaction

1. **Client requests feed** → FastAPI endpoint
2. **Feed Service** generates personalized feed using algorithm
3. **Algorithm** queries PostgreSQL + checks Redis cache
4. **Posts** retrieved with engagement data
5. **Response** returned with pagination cursor
6. **WebSocket** pushes new posts in real-time

## 3. Database Schema

### 3.1 Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────┐
│    users     │◄────────┤    posts     │
│              │  1:N    │              │
└──────────────┘         └──────┬───────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
            ┌───────────┐ ┌──────────┐ ┌──────────┐
            │post_likes │ │post_     │ │post_     │
            │           │ │comments  │ │shares    │
            └───────────┘ └──────────┘ └──────────┘
```

### 3.2 Table Definitions

#### 3.2.1 posts

Primary table storing all post content.

```python
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(PostType), nullable=False, default=PostType.TEXT)
    content = Column(Text, nullable=True)  # Text content, markdown supported
    
    # Media & attachments
    media_urls = Column(JSON, nullable=True)  # List of media URLs
    track_id = Column(String(36), ForeignKey("tracks.id", ondelete="SET NULL"), nullable=True)
    
    # Poll data (for poll posts)
    poll_options = Column(JSON, nullable=True)  # [{"id": "1", "text": "Option 1"}]
    poll_ends_at = Column(String(100), nullable=True)  # ISO timestamp
    
    # Event data (for event posts)
    event_data = Column(JSON, nullable=True)  # {title, date, location, link}
    
    # Visibility & status
    visibility = Column(Enum(PostVisibility), default=PostVisibility.PUBLIC)
    is_pinned = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Engagement counters (denormalized for performance)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(String(100), nullable=False)  # ISO timestamp
    updated_at = Column(String(100), nullable=False)  # ISO timestamp
    edited_at = Column(String(100), nullable=True)  # ISO timestamp (if edited)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    track = relationship("Track", back_populates="posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")
    shares = relationship("PostShare", back_populates="post", cascade="all, delete-orphan")
    saves = relationship("PostSave", back_populates="post", cascade="all, delete-orphan")
    reports = relationship("PostReport", back_populates="post", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_posts_user_created', 'user_id', 'created_at'),
        Index('idx_posts_type_created', 'type', 'created_at'),
        Index('idx_posts_visibility', 'visibility', 'is_deleted'),
    )
```

**Post Types Enum:**
```python
class PostType(str, enum.Enum):
    TEXT = "text"
    TRACK_SHARE = "track_share"
    MEDIA = "media"
    POLL = "poll"
    EVENT = "event"
    MILESTONE = "milestone"
```

**Visibility Enum:**
```python
class PostVisibility(str, enum.Enum):
    PUBLIC = "public"          # Everyone can see
    FOLLOWERS = "followers"    # Only followers
    PRIVATE = "private"        # Only mentioned users
```

#### 3.2.2 post_likes

Stores user likes on posts.

```python
class PostLike(Base):
    __tablename__ = "post_likes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(String(100), nullable=False)  # ISO timestamp
    
    # Relationships
    user = relationship("User", back_populates="post_likes")
    post = relationship("Post", back_populates="likes")
    
    # Unique constraint: user can like a post only once
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),
        Index('idx_post_likes_post', 'post_id', 'created_at'),
    )
```

#### 3.2.3 post_comments

Stores comments on posts with threading support.

```python
class PostComment(Base):
    __tablename__ = "post_comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    # Threading (1 level deep)
    parent_comment_id = Column(String(36), ForeignKey("post_comments.id", ondelete="CASCADE"), nullable=True)
    
    # Engagement
    like_count = Column(Integer, default=0)
    
    # Status
    is_deleted = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(String(100), nullable=False)  # ISO timestamp
    updated_at = Column(String(100), nullable=False)  # ISO timestamp
    
    # Relationships
    user = relationship("User", back_populates="post_comments")
    post = relationship("Post", back_populates="comments")
    parent_comment = relationship("PostComment", remote_side=[id], backref="replies")
    comment_likes = relationship("PostCommentLike", back_populates="comment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_post_comments_post', 'post_id', 'created_at'),
        Index('idx_post_comments_user', 'user_id', 'created_at'),
    )
```

#### 3.2.4 post_comment_likes

Stores likes on comments.

```python
class PostCommentLike(Base):
    __tablename__ = "post_comment_likes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    comment_id = Column(String(36), ForeignKey("post_comments.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String(100), nullable=False)
    
    # Relationships
    user = relationship("User")
    comment = relationship("PostComment", back_populates="comment_likes")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'comment_id', name='uq_user_comment_like'),
    )
```

#### 3.2.5 post_shares

Tracks post shares (reposts to feed).

```python
class PostShare(Base):
    __tablename__ = "post_shares"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    share_type = Column(Enum(ShareType), default=ShareType.REPOST)
    comment = Column(Text, nullable=True)  # Optional comment when sharing
    created_at = Column(String(100), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="post_shares")
    post = relationship("Post", back_populates="shares")
    
    # Indexes
    __table_args__ = (
        Index('idx_post_shares_user', 'user_id', 'created_at'),
        Index('idx_post_shares_post', 'post_id', 'created_at'),
    )
```

**ShareType Enum:**
```python
class ShareType(str, enum.Enum):
    REPOST = "repost"      # Share to own feed
    DM = "dm"              # Share via direct message
    EXTERNAL = "external"  # Share to external platform
```

#### 3.2.6 post_saves

Stores bookmarked/saved posts.

```python
class PostSave(Base):
    __tablename__ = "post_saves"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    collection_name = Column(String(100), nullable=True)  # Optional collection
    created_at = Column(String(100), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="post_saves")
    post = relationship("Post", back_populates="saves")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_user_post_save'),
        Index('idx_post_saves_user', 'user_id', 'created_at'),
    )
```

#### 3.2.7 poll_votes

Tracks user votes on poll posts.

```python
class PollVote(Base):
    __tablename__ = "poll_votes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    option_id = Column(String(36), nullable=False)  # References poll_options JSON
    created_at = Column(String(100), nullable=False)
    
    # Relationships
    user = relationship("User")
    post = relationship("Post")
    
    # Unique constraint: one vote per user per poll
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uq_user_poll_vote'),
    )
```

#### 3.2.8 post_reports

Content moderation reports.

```python
class PostReport(Base):
    __tablename__ = "post_reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    reporter_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Enum(ReportReason), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    created_at = Column(String(100), nullable=False)
    reviewed_at = Column(String(100), nullable=True)
    reviewed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    post = relationship("Post", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reporter_user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
```

**Enums:**
```python
class ReportReason(str, enum.Enum):
    SPAM = "spam"
    HARASSMENT = "harassment"
    EXPLICIT_CONTENT = "explicit_content"
    COPYRIGHT = "copyright"
    MISINFORMATION = "misinformation"
    OTHER = "other"

class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    ACTIONED = "actioned"
    DISMISSED = "dismissed"
```

### 3.3 Database Indexes

Critical indexes for performance:

```sql
-- Post retrieval
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at DESC);
CREATE INDEX idx_posts_visibility ON posts(visibility, is_deleted, created_at DESC);

-- Feed generation
CREATE INDEX idx_posts_created ON posts(created_at DESC) WHERE is_deleted = FALSE;
