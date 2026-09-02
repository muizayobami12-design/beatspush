"""
Submit-to-DJ System Models

Allows producers to submit beats/tracks to DJs for potential playlisting,
collaboration, or remixing opportunities.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid

from app.db.database import Base


class SubmissionStatus(str, PyEnum):
    """Submission status enum"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FEATURED = "featured"
    ARCHIVED = "archived"


class SubmissionType(str, PyEnum):
    """Type of submission"""
    PLAYLIST_PITCH = "playlist_pitch"  # Submit for DJ playlist
    COLLABORATION = "collaboration"    # Request collaboration
    REMIX_REQUEST = "remix_request"    # Request remix
    FEATURE_REQUEST = "feature_request"  # Request feature on track
    SPONSORSHIP = "sponsorship"        # Sponsorship/partnership opportunity


class SubmissionCategory(str, PyEnum):
    """Submission category"""
    BEATS = "beats"
    TRACKS = "tracks"
    REMIXES = "remixes"
    COVERS = "covers"
    SAMPLES = "samples"


class DJSubmission(Base):
    """
    Model for producer submissions to DJs
    
    A producer can submit their beat/track to a DJ with a message and pricing.
    The DJ can review, accept, reject, or feature the submission.
    """
    __tablename__ = "dj_submissions"

    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign Keys
    producer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    dj_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    beat_id = Column(String(36), ForeignKey("beats.id"), nullable=True)
    track_id = Column(String(36), ForeignKey("tracks.id"), nullable=True)

    # Submission Details
    submission_type = Column(Enum(SubmissionType), default=SubmissionType.PLAYLIST_PITCH, nullable=False)
    category = Column(Enum(SubmissionCategory), default=SubmissionCategory.BEATS, nullable=False)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False, index=True)
    
    # Submission Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # Producer's pitch/message
    message = Column(Text, nullable=True)  # Personal note to DJ
    
    # Audio Details (cached from beat/track)
    audio_url = Column(String(500), nullable=True)
    genre = Column(String(50), nullable=True)
    bpm = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Pricing & Licensing
    base_price = Column(Float, default=0.0, nullable=False)  # Price if accepted
    exclusive = Column(Boolean, default=False)  # Exclusive rights or non-exclusive
    license_type = Column(String(50), nullable=True)  # lease, exclusive, royalty_share, etc.
    
    # Review Info
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)  # DJ reviewer
    
    # Response/Feedback
    review_status = Column(Enum(SubmissionStatus), nullable=True)
    review_feedback = Column(Text, nullable=True)
    rejection_reason = Column(String(255), nullable=True)
    
    # Engagement Metrics
    view_count = Column(Integer, default=0, nullable=False)
    listened_count = Column(Integer, default=0, nullable=False)  # How many times DJ heard it
    
    # Follow-up Actions
    featured = Column(Boolean, default=False)  # Was this featured by DJ?
    featured_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    
    # Payment Status (if accepted)
    payment_status = Column(String(50), default="pending")  # pending, completed, failed, held
    payment_id = Column(String(100), nullable=True)  # Stripe/Paystack transaction ID
    platform_fee = Column(Float, default=0.0)  # Platform takes cut
    creator_payout = Column(Float, default=0.0)  # Creator receives
    
    # Tags & Metadata
    tags = Column(Text, nullable=True)  # Comma-separated tags: "afrobeat,summer,2024"
    featured_reason = Column(String(255), nullable=True)  # Why was it featured?
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    producer = relationship("User", foreign_keys=[producer_id], backref="submissions_as_producer")
    dj = relationship("User", foreign_keys=[dj_id], backref="submissions_received")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    beat = relationship("Beat", foreign_keys=[beat_id])
    track = relationship("Track", foreign_keys=[track_id])

    def __repr__(self):
        return f"<DJSubmission(id={self.id}, producer={self.producer_id}, dj={self.dj_id}, status={self.status})>"


class SubmissionResponse(Base):
    """
    Model for DJ responses/counteroffers to submissions
    
    DJ can respond with modified pricing, negotiate, or provide feedback
    """
    __tablename__ = "submission_responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign Keys
    submission_id = Column(String(36), ForeignKey("dj_submissions.id"), nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Response Details
    message = Column(Text, nullable=False)
    response_type = Column(String(50), nullable=False)  # counteroffer, feedback, question, acceptance, rejection
    
    # Counteroffer Details (if negotiating)
    counteroffer_price = Column(Float, nullable=True)
    counteroffer_license = Column(String(50), nullable=True)
    counteroffer_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    submission = relationship("DJSubmission", backref="responses")
    sender = relationship("User", foreign_keys=[sender_id], backref="submission_responses_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="submission_responses_received")

    def __repr__(self):
        return f"<SubmissionResponse(id={self.id}, submission={self.submission_id})>"


class SubmissionAnalytics(Base):
    """
    Analytics tracking for submissions
    
    Track views, listens, acceptance rates, and DJ engagement
    """
    __tablename__ = "submission_analytics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign Keys
    submission_id = Column(String(36), ForeignKey("dj_submissions.id"), nullable=False, index=True)
    dj_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Viewing Stats
    viewed_at = Column(DateTime, default=datetime.utcnow)
    listen_duration_seconds = Column(Integer, default=0)  # How long DJ listened
    
    # Engagement
    showed_interest = Column(Boolean, default=False)
    shared_with_team = Column(Boolean, default=False)
    shared_count = Column(Integer, default=0)
    
    # Conversion
    converted_to_collaboration = Column(Boolean, default=False)
    collaboration_date = Column(DateTime, nullable=True)
    
    # Feedback Score (1-5)
    quality_score = Column(Integer, nullable=True)
    fit_score = Column(Integer, nullable=True)  # How well it fits DJ's style
    originality_score = Column(Integer, nullable=True)

    # Relationships
    submission = relationship("DJSubmission")
    dj = relationship("User", foreign_keys=[dj_id])

    def __repr__(self):
        return f"<SubmissionAnalytics(id={self.id}, submission={self.submission_id})>"
