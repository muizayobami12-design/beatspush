"""
Pydantic schemas for Submit-to-DJ System
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubmissionType(str, Enum):
    PLAYLIST_PITCH = "playlist_pitch"
    COLLABORATION = "collaboration"
    REMIX_REQUEST = "remix_request"
    FEATURE_REQUEST = "feature_request"
    SPONSORSHIP = "sponsorship"


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FEATURED = "featured"
    ARCHIVED = "archived"


class SubmissionCategory(str, Enum):
    BEATS = "beats"
    TRACKS = "tracks"
    REMIXES = "remixes"
    COVERS = "covers"
    SAMPLES = "samples"


class SubmissionCreate(BaseModel):
    """Schema for creating a new submission"""
    dj_id: str = Field(..., description="ID of DJ to submit to")
    submission_type: SubmissionType = Field(default=SubmissionType.PLAYLIST_PITCH)
    category: SubmissionCategory = Field(default=SubmissionCategory.BEATS)
    
    beat_id: Optional[str] = Field(None, description="Beat to submit")
    track_id: Optional[str] = Field(None, description="Track to submit")
    
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    message: Optional[str] = Field(None, max_length=2000, description="Personal note to DJ")
    
    # Pricing
    base_price: float = Field(default=0.0, ge=0, description="Price if accepted")
    exclusive: bool = Field(default=False)
    license_type: Optional[str] = Field(None)
    
    # Tags
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    
    @validator('beat_id', 'track_id', pre=True, always=True)
    def at_least_one_content(cls, v, values):
        """Ensure at least beat_id or track_id is provided"""
        if not v and not values.get('beat_id') and not values.get('track_id'):
            raise ValueError('Either beat_id or track_id must be provided')
        return v

    class Config:
        schema_extra = {
            "example": {
                "dj_id": "dj123",
                "beat_id": "beat456",
                "submission_type": "playlist_pitch",
                "title": "Summer Vibes Afrobeat",
                "message": "Hey! I think this track would fit your summer playlist perfectly.",
                "base_price": 50.0,
                "exclusive": False,
                "tags": "afrobeat,summer,chill"
            }
        }


class SubmissionUpdate(BaseModel):
    """Schema for updating a submission"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    message: Optional[str] = Field(None, max_length=2000)
    base_price: Optional[float] = Field(None, ge=0)
    exclusive: Optional[bool] = None
    license_type: Optional[str] = None
    tags: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "base_price": 75.0,
                "message": "Updated: Now offering exclusive rights!"
            }
        }


class SubmissionReview(BaseModel):
    """Schema for DJ to review a submission"""
    status: SubmissionStatus = Field(..., description="Accept, reject, or feature")
    feedback: Optional[str] = Field(None, max_length=1000)
    rejection_reason: Optional[str] = Field(None, max_length=500)
    featured_reason: Optional[str] = Field(None, max_length=500, description="If featuring")
    quality_score: Optional[int] = Field(None, ge=1, le=5)
    fit_score: Optional[int] = Field(None, ge=1, le=5)

    class Config:
        schema_extra = {
            "example": {
                "status": "accepted",
                "feedback": "Great track! Love the production quality.",
                "quality_score": 5,
                "fit_score": 4
            }
        }


class SubmissionResponseCreate(BaseModel):
    """Schema for responding to a submission"""
    message: str = Field(..., max_length=2000)
    response_type: str = Field(...)  # counteroffer, feedback, question, acceptance, rejection
    counteroffer_price: Optional[float] = Field(None, ge=0)
    counteroffer_license: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "message": "I can offer ₦30,000 for non-exclusive rights.",
                "response_type": "counteroffer",
                "counteroffer_price": 30000,
                "counteroffer_license": "non-exclusive"
            }
        }


class ProducerInfo(BaseModel):
    """Basic producer info for submissions"""
    id: str
    full_name: str
    profile_image_url: Optional[str]
    is_verified: bool

    class Config:
        from_attributes = True


class DJInfo(BaseModel):
    """Basic DJ info for submissions"""
    id: str
    full_name: str
    profile_image_url: Optional[str]
    is_verified: bool
    follower_count: int

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    """Complete submission response"""
    id: str
    producer_id: str
    dj_id: str
    beat_id: Optional[str]
    track_id: Optional[str]
    
    submission_type: SubmissionType
    category: SubmissionCategory
    status: SubmissionStatus
    
    title: str
    description: Optional[str]
    message: Optional[str]
    
    genre: Optional[str]
    bpm: Optional[int]
    duration_seconds: Optional[int]
    
    base_price: float
    exclusive: bool
    license_type: Optional[str]
    
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    view_count: int
    listened_count: int
    
    featured: bool
    featured_at: Optional[datetime]
    accepted_at: Optional[datetime]
    
    payment_status: Optional[str]
    creator_payout: float
    
    producer: ProducerInfo
    dj: DJInfo
    
    tags: Optional[List[str]]

    class Config:
        from_attributes = True


class SubmissionListItem(BaseModel):
    """Simplified submission for lists"""
    id: str
    title: str
    producer_id: str
    submission_type: SubmissionType
    status: SubmissionStatus
    submitted_at: datetime
    view_count: int
    base_price: float
    featured: bool

    class Config:
        from_attributes = True


class SubmissionStats(BaseModel):
    """Submission statistics"""
    total_submissions: int
    pending: int
    under_review: int
    accepted: int
    rejected: int
    featured: int
    
    acceptance_rate: float  # 0-1
    average_price: float
    total_revenue: float

    class Config:
        schema_extra = {
            "example": {
                "total_submissions": 25,
                "pending": 5,
                "under_review": 3,
                "accepted": 12,
                "rejected": 5,
                "featured": 1,
                "acceptance_rate": 0.48,
                "average_price": 50.0,
                "total_revenue": 600.0
            }
        }


class SubmissionAnalyticsResponse(BaseModel):
    """Submission analytics data"""
    submission_id: str
    view_count: int
    listen_count: int
    average_listen_duration: int  # seconds
    shared_count: int
    quality_score: Optional[int]
    fit_score: Optional[int]
    originality_score: Optional[int]
    converted_to_collaboration: bool

    class Config:
        from_attributes = True


class DJSubmissionDashboard(BaseModel):
    """Dashboard view for DJ reviewing submissions"""
    total_pending: int
    total_under_review: int
    total_this_week: int
    
    submissions: List[SubmissionListItem]
    
    stats: SubmissionStats

    class Config:
        schema_extra = {
            "example": {
                "total_pending": 15,
                "total_under_review": 8,
                "total_this_week": 12,
                "submissions": [],
                "stats": {
                    "total_submissions": 100,
                    "pending": 15,
                    "acceptance_rate": 0.45
                }
            }
        }


class ProducerSubmissionDashboard(BaseModel):
    """Dashboard view for producer managing submissions"""
    total_submissions: int
    pending_reviews: int
    accepted_tracks: int
    rejected_tracks: int
    featured_count: int
    total_revenue: float
    
    recent_submissions: List[SubmissionListItem]

    class Config:
        schema_extra = {
            "example": {
                "total_submissions": 50,
                "pending_reviews": 10,
                "accepted_tracks": 15,
                "rejected_tracks": 20,
                "featured_count": 2,
                "total_revenue": 2500.0,
                "recent_submissions": []
            }
        }
