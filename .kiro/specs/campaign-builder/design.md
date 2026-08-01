# Technical Design Document: Campaign Builder

## 1. Overview

The Campaign Builder is a promotional campaign management system that enables music creators to create, manage, and prepare multi-platform promotional campaigns. It integrates with the existing AI Content Generation Service (Task 3.1) and prepares content for future social media posting (Task 3.3).

### 1.1 Architecture

- **Backend:** Python FastAPI
- **Database:** SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- **Authentication:** JWT tokens (existing)
- **AI Integration:** Existing AIService from Task 3.1
- **Background Tasks:** Python scheduled tasks (cron-like)

### 1.2 Key Components

1. **Campaign Model** - Core campaign data
2. **Campaign Content Model** - Platform-specific content
3. **Campaign Template Model** - Template definitions
4. **Campaign Activity Log** - Audit trail
5. **Campaign Service** - Business logic
6. **Campaign API** - RESTful endpoints
7. **Campaign Schemas** - Request/response validation
8. **Background Task** - Scheduled campaign activation

---

## 2. Database Schema

### 2.1 Campaigns Table

Main table storing campaign data.

```python
class CampaignStatus(str, enum.Enum):
    """Campaign status lifecycle"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Campaign(Base):
    """Campaign model"""
    __tablename__ = "campaigns"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    track_id = Column(String(36), ForeignKey("tracks.id"), nullable=False, index=True)
    template_id = Column(String(36), ForeignKey("campaign_templates.id"), nullable=True)
    
    # Campaign details
    name = Column(String(255), nullable=False)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False, index=True)
    
    # Platform selections (JSON array of platform names)
    platforms = Column(JSON, nullable=False)  # ["instagram", "tiktok", "twitter", "facebook"]
    
    # Scheduling
    scheduled_publish_time = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Performance metrics (placeholders for Task 3.3)
    engagement_count = Column(Integer, default=0)
    reach_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="campaigns")
    track = relationship("Track", backref="campaigns")
    template = relationship("CampaignTemplate", backref="campaigns")
    content = relationship("CampaignContent", back_populates="campaign", cascade="all, delete-orphan")
    activity_logs = relationship("CampaignActivityLog", back_populates="campaign", cascade="all, delete-orphan")
```

**Indexes:**
- `idx_campaigns_user_id` on `user_id`
- `idx_campaigns_track_id` on `track_id`
- `idx_campaigns_status` on `status`
- `idx_campaigns_scheduled_time` on `scheduled_publish_time`

---

### 2.2 Campaign Content Table

Stores platform-specific content for each campaign.

```python
class Platform(str, enum.Enum):
    """Supported platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"



class ContentType(str, enum.Enum):
    """Content type per platform"""
    INSTAGRAM_FEED = "instagram_feed"
    INSTAGRAM_STORY = "instagram_story"
    INSTAGRAM_REEL = "instagram_reel"
    TIKTOK_VIDEO = "tiktok_video"
    TWITTER_TWEET = "twitter_tweet"
    TWITTER_THREAD = "twitter_thread"
    FACEBOOK_POST = "facebook_post"
    FACEBOOK_STORY = "facebook_story"


class CampaignContent(Base):
    """Platform-specific campaign content"""
    __tablename__ = "campaign_content"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Foreign key
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Platform info
    platform = Column(SQLEnum(Platform), nullable=False)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    
    # Content data
    caption = Column(Text, nullable=True)  # Main text content
    hashtags = Column(JSON, nullable=True)  # Array of hashtags
    
    # Platform-specific fields (JSON for flexibility)
    platform_specific_data = Column(JSON, nullable=True)  # e.g., {"video_idea": "...", "thread_parts": [...]}
    
    # AI generation tracking
    ai_generated_caption = Column(Text, nullable=True)  # Original AI-generated caption
    caption_tone = Column(String(50), nullable=True)  # Tone used (e.g., "hype", "emotional")
    content_edited = Column(Boolean, default=False)  # Has user edited content?
    
    # Posting status (for Task 3.3 integration)
    posting_status = Column(String(50), default="pending")  # pending, posted, failed
    posted_at = Column(DateTime(timezone=True), nullable=True)
    post_url = Column(String(500), nullable=True)  # URL of posted content
    
    # Performance metrics per platform (placeholders)
    engagement_count = Column(Integer, default=0)
    reach_count = Column(Integer, default=0)
    clicks_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Timestamps
    content_generated_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    campaign = relationship("Campaign", back_populates="content")
```

**Indexes:**
- `idx_campaign_content_campaign_id` on `campaign_id`
- `idx_campaign_content_platform` on `platform`

---

### 2.3 Campaign Templates Table

Stores predefined campaign templates.

```python
class CampaignTemplate(Base):
    """Campaign template definitions"""
    __tablename__ = "campaign_templates"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Template info
    name = Column(String(100), nullable=False, unique=True)  # "New Release", "Pre-Release Teaser", etc.
    slug = Column(String(100), nullable=False, unique=True, index=True)  # "new-release", "pre-release-teaser"
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)  # Icon name for UI
    
    # AI prompt modifications (JSON)
    prompt_strategy = Column(JSON, nullable=False)  # Strategy for AI generation
    # Example: {
    #   "tone_emphasis": "excitement",
    #   "keywords": ["new", "available now", "streaming"],
    #   "call_to_action": "Listen now"
    # }
    
    # Recommended platforms
    recommended_platforms = Column(JSON, nullable=True)  # ["instagram", "tiktok"]
    
    # Usage stats
    usage_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Seed Data (6 templates):**
1. **New Release** - Emphasis on excitement and availability
2. **Pre-Release Teaser** - Build anticipation and mystery
3. **Behind The Scenes** - Focus on creative process and authenticity
4. **Fan Engagement** - Encourage interaction and questions
5. **Milestone Celebration** - Highlight achievements and gratitude
6. **Throwback Thursday** - Nostalgic content about older tracks

---

### 2.4 Campaign Activity Log Table

Audit trail for campaign actions.

```python
class CampaignActivityLog(Base):
    """Campaign activity audit log"""
    __tablename__ = "campaign_activity_log"
    
    # Primary key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Foreign keys
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Activity details
    action = Column(String(100), nullable=False)  # "created", "status_changed", "edited", "deleted", etc.
    details = Column(JSON, nullable=True)  # Action-specific details
    # Example: {"old_status": "draft", "new_status": "scheduled"}
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="activity_logs")
    user = relationship("User")
```

**Indexes:**
- `idx_activity_log_campaign_id` on `campaign_id`
- `idx_activity_log_created_at` on `created_at`

---

## 3. API Endpoints

All endpoints require authentication (JWT token). Base path: `/api/v1`

### 3.1 Campaign Management Endpoints

#### POST /campaigns
Create a new campaign (multi-step process).

**Request Body:**
```json
{
  "track_id": "uuid",
  "template_id": "uuid" (optional),
  "platforms": ["instagram", "tiktok"],
  "name": "My Campaign" (optional, auto-generated if not provided)
}
```

**Response:** `CampaignResponse` (201 Created)

---

#### GET /campaigns
List all campaigns for the authenticated user.

**Query Parameters:**
- `status` (optional): Filter by status
- `platform` (optional): Filter by platform
- `search` (optional): Search by name or track title
- `limit` (optional, default=20): Number of results
- `offset` (optional, default=0): Pagination offset

**Response:** `CampaignListResponse` (200 OK)

---

#### GET /campaigns/{campaign_id}
Get detailed campaign information.

**Response:** `CampaignDetailResponse` (200 OK)

---

#### PUT /campaigns/{campaign_id}
Update campaign (only allowed for DRAFT or SCHEDULED status).

**Request Body:**
```json
{
  "name": "Updated Name" (optional),
  "platforms": ["instagram", "facebook"] (optional),
  "scheduled_publish_time": "2024-02-15T10:00:00Z" (optional)
}
```

**Response:** `CampaignResponse` (200 OK)

---

#### DELETE /campaigns/{campaign_id}
Delete campaign (only DRAFT, CANCELLED, or COMPLETED).

**Response:** `MessageResponse` (200 OK)

---

#### POST /campaigns/{campaign_id}/duplicate
Duplicate an existing campaign.

**Response:** `CampaignResponse` (201 Created)

---

#### POST /campaigns/{campaign_id}/cancel
Cancel an active or scheduled campaign.

**Response:** `CampaignResponse` (200 OK)

---

#### POST /campaigns/{campaign_id}/complete
Mark active campaign as completed.

**Response:** `CampaignResponse` (200 OK)

---

### 3.2 Campaign Content Endpoints

#### POST /campaigns/{campaign_id}/generate-content
Generate AI content for selected platforms.

**Request Body:**
```json
{
  "platforms": ["instagram", "twitter"]
}
```

**Response:** `CampaignContentResponse` (200 OK)

---

#### GET /campaigns/{campaign_id}/content
Get all content for a campaign.

**Response:** `CampaignContentListResponse` (200 OK)

---

#### PUT /campaigns/{campaign_id}/content/{platform}
Update content for specific platform.

**Request Body:**
```json
{
  "caption": "Updated caption",
  "hashtags": ["#afrobeats", "#newmusic"],
  "caption_tone": "hype"
}
```

**Response:** `CampaignContentResponse` (200 OK)

---

### 3.3 Campaign Template Endpoints

#### GET /campaign-templates
List all available templates.

**Response:** `CampaignTemplateListResponse` (200 OK)

---

#### GET /campaign-templates/{template_id}
Get template details.

**Response:** `CampaignTemplateResponse` (200 OK)

---

### 3.4 Campaign Workflow Endpoints

#### POST /campaigns/{campaign_id}/schedule
Schedule campaign for future publication.

**Request Body:**
```json
{
  "scheduled_publish_time": "2024-02-15T10:00:00Z"
}
```

**Response:** `CampaignResponse` (200 OK)

---

#### POST /campaigns/{campaign_id}/publish
Publish campaign immediately.

**Response:** `CampaignResponse` (200 OK)

---

## 4. Pydantic Schemas

### 4.1 Request Schemas

```python
class CampaignCreateRequest(BaseModel):
    """Campaign creation request"""
    track_id: str = Field(..., description="Track UUID")
    template_id: Optional[str] = Field(None, description="Template UUID")
    platforms: List[str] = Field(..., min_items=1, description="List of platform names")
    name: Optional[str] = Field(None, max_length=255, description="Campaign name")


class CampaignUpdateRequest(BaseModel):
    """Campaign update request"""
    name: Optional[str] = Field(None, max_length=255)
    platforms: Optional[List[str]] = Field(None, min_items=1)
    scheduled_publish_time: Optional[datetime] = None


class CampaignScheduleRequest(BaseModel):
    """Schedule campaign request"""
    scheduled_publish_time: datetime = Field(..., description="Future datetime")
    
    @validator('scheduled_publish_time')
    def validate_future_time(cls, v):
        if v <= datetime.now(timezone.utc):
            raise ValueError('Scheduled time must be in the future')
        return v


class ContentGenerateRequest(BaseModel):
    """Generate content request"""
    platforms: List[str] = Field(..., min_items=1)


class ContentUpdateRequest(BaseModel):
    """Update platform content request"""
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    caption_tone: Optional[str] = None
```

---

### 4.2 Response Schemas

```python
class CampaignContentResponse(BaseModel):
    """Campaign content response"""
    id: str
    campaign_id: str
    platform: str
    content_type: str
    caption: Optional[str]
    hashtags: Optional[List[str]]
    caption_tone: Optional[str]
    content_edited: bool
    posting_status: str
    engagement_count: int
    reach_count: int
    clicks_count: int
    shares_count: int
    content_generated_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CampaignResponse(BaseModel):
    """Campaign response"""
    id: str
    user_id: str
    track_id: str
    template_id: Optional[str]
    name: str
    status: str
    platforms: List[str]
    scheduled_publish_time: Optional[datetime]
    published_at: Optional[datetime]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    engagement_count: int
    reach_count: int
    clicks_count: int
    shares_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True



class CampaignDetailResponse(CampaignResponse):
    """Detailed campaign response with content"""
    track: Dict  # Track basic info
    template: Optional[Dict]  # Template basic info
    content: List[CampaignContentResponse]


class CampaignListResponse(BaseModel):
    """Campaign list response"""
    campaigns: List[CampaignResponse]
    total: int
    limit: int
    offset: int


class CampaignTemplateResponse(BaseModel):
    """Campaign template response"""
    id: str
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    recommended_platforms: Optional[List[str]]
    usage_count: int
    is_active: bool
    
    class Config:
        from_attributes = True


class CampaignTemplateListResponse(BaseModel):
    """Template list response"""
    templates: List[CampaignTemplateResponse]


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
```

---

## 5. Service Layer

### 5.1 CampaignService

Business logic for campaign operations.

```python
class CampaignService:
    """Campaign business logic"""
    
    @staticmethod
    def create_campaign(
        db: Session,
        user: User,
        campaign_data: CampaignCreateRequest
    ) -> Campaign:
        """Create a new campaign"""
        # 1. Validate track ownership
        # 2. Validate template exists (if provided)
        # 3. Generate campaign name if not provided
        # 4. Create campaign record with DRAFT status
        # 5. Log activity
        pass
    
    @staticmethod
    def generate_content(
        db: Session,
        campaign: Campaign,
        platforms: List[str]
    ) -> List[CampaignContent]:
        """Generate AI content for platforms"""
        # 1. Get track info
        # 2. Get template strategy (if applicable)
        # 3. For each platform:
        #    - Call AIService.generate_social_captions()
        #    - Call AIService.generate_hashtags()
        #    - Create CampaignContent record
        # 4. Log activity
        pass
    
    @staticmethod
    def update_campaign(
        db: Session,
        campaign: Campaign,
        update_data: CampaignUpdateRequest
    ) -> Campaign:
        """Update campaign details"""
        # 1. Validate status (only DRAFT or SCHEDULED)
        # 2. Update fields
        # 3. If platforms added, generate new content
        # 4. Log activity
        pass
    
    @staticmethod
    def schedule_campaign(
        db: Session,
        campaign: Campaign,
        scheduled_time: datetime
    ) -> Campaign:
        """Schedule campaign for future publication"""
        # 1. Validate scheduled time is future
        # 2. Update status to SCHEDULED
        # 3. Set scheduled_publish_time
        # 4. Log activity
        pass
    
    @staticmethod
    def publish_campaign(
        db: Session,
        campaign: Campaign
    ) -> Campaign:
        """Publish campaign immediately"""
        # 1. Update status to ACTIVE
        # 2. Set published_at timestamp
        # 3. Log activity
        # Note: Actual social media posting is Task 3.3
        pass
    
    @staticmethod
    def cancel_campaign(
        db: Session,
        campaign: Campaign
    ) -> Campaign:
        """Cancel active or scheduled campaign"""
        # 1. Update status to CANCELLED
        # 2. Set cancelled_at timestamp
        # 3. Log activity
        pass
    
    @staticmethod
    def complete_campaign(
        db: Session,
        campaign: Campaign
    ) -> Campaign:
        """Mark campaign as completed"""
        # 1. Update status to COMPLETED
        # 2. Set completed_at timestamp
        # 3. Log activity
        pass
    
    @staticmethod
    def delete_campaign(
        db: Session,
        campaign: Campaign
    ) -> None:
        """Delete campaign (cascade deletes content and logs)"""
        # 1. Validate deletable status
        # 2. Delete campaign (cascade handles content and logs)
        # 3. Log deletion in separate audit table if needed
        pass
    
    @staticmethod
    def duplicate_campaign(
        db: Session,
        user: User,
        source_campaign: Campaign
    ) -> Campaign:
        """Duplicate existing campaign"""
        # 1. Create new campaign with DRAFT status
        # 2. Copy platforms and template
        # 3. Name as "{original_name} (Copy)"
        # 4. Do NOT copy track or content
        # 5. Log activity
        pass
    
    @staticmethod
    def get_user_campaigns(
        db: Session,
        user_id: str,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Campaign], int]:
        """Get filtered list of user's campaigns"""
        # 1. Build query with filters
        # 2. Apply search on name and track title
        # 3. Return campaigns and total count
        pass
    
    @staticmethod
    def update_content(
        db: Session,
        content: CampaignContent,
        update_data: ContentUpdateRequest
    ) -> CampaignContent:
        """Update platform content"""
        # 1. Update caption/hashtags
        # 2. Set content_edited = True
        # 3. Update timestamp
        pass
    
    @staticmethod
    def generate_campaign_name(
        track_title: str,
        template_name: Optional[str] = None
    ) -> str:
        """Generate campaign name"""
        # Format: "{Template} - {Track}" or "Campaign - {Track}"
        # Truncate if > 100 chars
        pass
    
    @staticmethod
    def log_activity(
        db: Session,
        campaign_id: str,
        user_id: str,
        action: str,
        details: Optional[Dict] = None
    ) -> None:
        """Log campaign activity"""
        # Create activity log record
        pass
```

---

### 5.2 Integration with AIService

The `CampaignService` will use the existing `AIService` from Task 3.1:

```python
# In generate_content method
from app.ai.ai_service import AIService

ai_service = AIService()

# Generate captions for each platform
for platform in platforms:
    captions = ai_service.generate_social_captions(
        track_title=track.title,
        artist_name=track.artist_name,
        genre=track.genre,
        mood=track.mood_tags[0] if track.mood_tags else None,
        platform=platform
    )
    
    # Generate hashtags (once per campaign)
    if not hashtags_generated:
        hashtags_data = ai_service.generate_hashtags(
            track_title=track.title,
            artist_name=track.artist_name,
            genre=track.genre,
            location=user_location  # From user profile
        )
        hashtags_generated = True
    
    # Apply template strategy if exists
    if campaign.template:
        # Modify prompt/selection based on template.prompt_strategy
        pass
    
    # Create content record
    content = CampaignContent(
        campaign_id=campaign.id,
        platform=platform,
        caption=selected_caption,
        hashtags=hashtags,
        # ... other fields
    )
```

---

## 6. Background Tasks

### 6.1 Scheduled Campaign Activation

A background task that checks for scheduled campaigns ready to activate.

```python
# app/tasks/campaign_scheduler.py

from datetime import datetime, timezone
from app.db.database import SessionLocal
from app.models.campaign import Campaign, CampaignStatus

def activate_scheduled_campaigns():
    """Check and activate scheduled campaigns"""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        
        # Find campaigns ready to activate
        campaigns = db.query(Campaign).filter(
            Campaign.status == CampaignStatus.SCHEDULED,
            Campaign.scheduled_publish_time <= now
        ).all()
        
        for campaign in campaigns:
            try:
                CampaignService.publish_campaign(db, campaign)
                print(f"✅ Activated campaign {campaign.id}")
            except Exception as e:
                campaign.status = CampaignStatus.FAILED
                campaign.error_message = str(e)
                print(f"❌ Failed to activate campaign {campaign.id}: {e}")
        
        db.commit()
    finally:
        db.close()
```

**Scheduling:** Run every 5 minutes using:
- Python `schedule` library
- Systemd timer (Linux)
- Windows Task Scheduler
- Or Celery Beat (if Celery is added later)

---

## 7. Technical Considerations

### 7.1 Validation Rules

1. **Campaign Creation:**
   - Track must exist and belong to user
   - Track status must be "published"
   - At least one platform must be selected
   - Template must exist if provided

2. **Campaign Editing:**
   - Only DRAFT or SCHEDULED campaigns can be edited
   - Scheduled time must be in the future
   - User must own the campaign

3. **Campaign Deletion:**
   - Only DRAFT, CANCELLED, or COMPLETED campaigns can be deleted
   - Cascade delete content and activity logs

4. **Content Updates:**
   - Respect platform character limits:
     - Instagram: 2,200 characters
     - Twitter: 280 characters
     - TikTok: 150 characters  
     - Facebook: 63,206 characters

5. **Status Transitions:**
   - DRAFT → SCHEDULED (when scheduled_time set)
   - DRAFT → ACTIVE (when published immediately)
   - SCHEDULED → ACTIVE (when scheduled_time reached)
   - ACTIVE → COMPLETED (manually or after duration)
   - ACTIVE → CANCELLED (manual cancellation)
   - SCHEDULED → CANCELLED (manual cancellation)
   - Any → FAILED (on error)

---

### 7.2 Error Handling

1. **AI Service Errors:**
   - Return 503 Service Unavailable if AIService fails
   - Store error message in campaign.error_message
   - Allow retry functionality
   - Log all AI service errors

2. **Database Errors:**
   - Wrap operations in try-except blocks
   - Rollback transactions on error
   - Return appropriate HTTP status codes (400, 404, 500)

3. **Authorization Errors:**
   - Return 403 Forbidden for unauthorized access
   - Verify user owns campaign before operations
   - Check user role (Artist, DJ, Producer only)

4. **Validation Errors:**
   - Return 422 Unprocessable Entity
   - Include detailed validation messages
   - Use Pydantic validation

---

### 7.3 Performance Optimizations

1. **Database Queries:**
   - Index on frequently queried fields (user_id, status, scheduled_publish_time)
   - Use eager loading for relationships when needed
   - Implement pagination for list endpoints

2. **AI Content Generation:**
   - Generate content asynchronously if possible
   - Cache AI responses for similar requests (future enhancement)
   - Batch process multiple platforms

3. **Background Tasks:**
   - Run scheduler efficiently (5-minute intervals)
   - Batch process multiple scheduled campaigns
   - Use database transactions properly

---

### 7.4 Security Considerations

1. **Authentication:**
   - All endpoints require JWT token
   - Validate token on every request

2. **Authorization:**
   - Users can only access their own campaigns
   - Admin role can view all campaigns (for moderation)
   - Verify user role for campaign creation

3. **Input Validation:**
   - Sanitize all user inputs
   - Validate UUIDs format
   - Check platform names against enum
   - Validate datetime formats

4. **Data Privacy:**
   - Don't expose sensitive user data in responses
   - Log personally identifiable information carefully
   - Follow GDPR principles for data retention

---

### 7.5 Future Extensibility

Design considerations for Task 3.3 (Social Media Integration):

1. **Posting Status Fields:**
   - `CampaignContent.posting_status` ready for "pending", "posted", "failed"
   - `CampaignContent.posted_at` timestamp field
   - `CampaignContent.post_url` for social media URLs

2. **Performance Metrics:**
   - Placeholder fields in Campaign and CampaignContent
   - Ready to receive real data from social media APIs
   - Structure supports platform-specific metrics

3. **Platform-Specific Data:**
   - `platform_specific_data` JSON field for flexibility
   - Can store Instagram reel IDs, Twitter thread IDs, etc.

4. **OAuth Integration:**
   - Future: Store social media tokens per user
   - Future: Implement posting service layer
   - Current: Content is generated and stored locally

---

## 8. File Structure

```
backend/app/
├── models/
│   ├── campaign.py              # Campaign, CampaignContent, CampaignTemplate, CampaignActivityLog
│   └── __init__.py
├── schemas/
│   ├── campaign.py              # All Pydantic schemas
│   └── __init__.py
├── services/
│   ├── campaign_service.py      # CampaignService class
│   └── __init__.py
├── api/v1/endpoints/
│   ├── campaigns.py             # Campaign API endpoints
│   └── __init__.py
├── tasks/
│   ├── campaign_scheduler.py    # Background task
│   └── __init__.py
└── core/
    ├── dependencies.py          # Add campaign-specific dependencies
    └── __init__.py
```

---

## 9. Database Migration

Using Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Add campaign tables"

# Run migration
alembic upgrade head
```

Migration will create:
- campaigns table
- campaign_content table
- campaign_templates table
- campaign_activity_log table
- All indexes and foreign keys

---

## 10. Testing Strategy

### 10.1 Unit Tests

Test individual service methods:
- Campaign creation
- Content generation
- Status transitions
- Campaign deletion
- Name generation

### 10.2 Integration Tests

Test API endpoints:
- POST /campaigns (create)
- GET /campaigns (list with filters)
- PUT /campaigns/{id} (update)
- DELETE /campaigns/{id} (delete)
- POST /campaigns/{id}/generate-content
- POST /campaigns/{id}/schedule
- POST /campaigns/{id}/publish

### 10.3 Background Task Tests

- Test scheduled campaign activation
- Test multiple campaigns at same time
- Test error handling in activation

### 10.4 Edge Cases

- Future scheduled time validation
- Invalid platform names
- Non-existent track IDs
- Unauthorized access attempts
- Status transition restrictions

---

## 11. Implementation Order

Recommended implementation sequence:

1. **Database Models** (campaign.py)
2. **Pydantic Schemas** (campaign.py schemas)
3. **Service Layer** (campaign_service.py)
4. **API Endpoints** (campaigns.py)
5. **Template Seed Data**
6. **Background Task** (campaign_scheduler.py)
7. **Integration Testing**
8. **Documentation**

---

## 12. Summary

The Campaign Builder design provides:

✅ Complete database schema with 4 tables
✅ 15 RESTful API endpoints
✅ Comprehensive service layer
✅ Integration with existing AI Service
✅ Background task for campaign activation
✅ Performance metrics placeholders for Task 3.3
✅ Secure, scalable, and maintainable architecture

The system is ready for implementation and prepared for future social media posting integration.
