"""
Submit-to-DJ Service

Manages beat/track submissions from producers to DJs for playlisting,
collaboration, and other opportunities.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
from app.models.dj_submission import (
    DJSubmission,
    SubmissionResponse,
    SubmissionAnalytics,
    SubmissionStatus,
    SubmissionType,
    SubmissionCategory,
)
from app.models.user import User
from app.models.beat import Beat
from app.models.track import Track
from app.schemas.dj_submission import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionReview,
    SubmissionResponseCreate,
    SubmissionStats,
)


class DJSubmissionService:
    """Service for managing DJ submissions"""

    @staticmethod
    def create_submission(
        db: Session,
        producer_id: str,
        submission_data: SubmissionCreate,
    ) -> DJSubmission:
        """
        Create a new submission from producer to DJ

        Args:
            db: Database session
            producer_id: ID of producer submitting
            submission_data: Submission details

        Returns:
            Created DJSubmission object
        """
        # Get beat/track details if provided
        beat = None
        track = None
        audio_url = None
        genre = None
        bpm = None
        duration_seconds = None

        if submission_data.beat_id:
            beat = db.query(Beat).filter(Beat.id == submission_data.beat_id).first()
            if beat:
                audio_url = beat.audio_url
                genre = beat.genre
                bpm = beat.tempo
                duration_seconds = beat.duration

        if submission_data.track_id:
            track = db.query(Track).filter(Track.id == submission_data.track_id).first()
            if track:
                audio_url = track.audio_url
                genre = track.genre
                duration_seconds = track.duration

        # Create submission
        submission = DJSubmission(
            producer_id=producer_id,
            dj_id=submission_data.dj_id,
            beat_id=submission_data.beat_id,
            track_id=submission_data.track_id,
            submission_type=submission_data.submission_type,
            category=submission_data.category,
            title=submission_data.title,
            description=submission_data.description,
            message=submission_data.message,
            audio_url=audio_url,
            genre=genre,
            bpm=bpm,
            duration_seconds=duration_seconds,
            base_price=submission_data.base_price,
            exclusive=submission_data.exclusive,
            license_type=submission_data.license_type,
            tags=submission_data.tags,
        )

        db.add(submission)
        db.commit()
        db.refresh(submission)

        return submission

    @staticmethod
    def get_submission(db: Session, submission_id: str) -> Optional[DJSubmission]:
        """Get a submission by ID"""
        submission = db.query(DJSubmission).filter(
            DJSubmission.id == submission_id
        ).first()

        if submission:
            submission.view_count += 1
            db.commit()

        return submission

    @staticmethod
    def update_submission(
        db: Session,
        submission_id: str,
        producer_id: str,
        update_data: SubmissionUpdate,
    ) -> Optional[DJSubmission]:
        """
        Update a submission (only pending submissions can be updated)

        Args:
            db: Database session
            submission_id: ID of submission to update
            producer_id: ID of producer (for permission check)
            update_data: Updated fields

        Returns:
            Updated submission or None if not found
        """
        submission = db.query(DJSubmission).filter(
            and_(
                DJSubmission.id == submission_id,
                DJSubmission.producer_id == producer_id,
                DJSubmission.status == SubmissionStatus.PENDING,
            )
        ).first()

        if not submission:
            return None

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(submission, key):
                setattr(submission, key, value)

        submission.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(submission)

        return submission

    @staticmethod
    def get_producer_submissions(
        db: Session,
        producer_id: str,
        status: Optional[SubmissionStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[DJSubmission], int]:
        """Get all submissions from a producer"""
        query = db.query(DJSubmission).filter(DJSubmission.producer_id == producer_id)

        if status:
            query = query.filter(DJSubmission.status == status)

        total = query.count()
        submissions = query.order_by(desc(DJSubmission.submitted_at)).offset(skip).limit(
            limit
        ).all()

        return submissions, total

    @staticmethod
    def get_dj_submissions(
        db: Session,
        dj_id: str,
        status: Optional[SubmissionStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[DJSubmission], int]:
        """Get all submissions received by a DJ"""
        query = db.query(DJSubmission).filter(DJSubmission.dj_id == dj_id)

        if status:
            query = query.filter(DJSubmission.status == status)

        total = query.count()
        submissions = query.order_by(desc(DJSubmission.submitted_at)).offset(skip).limit(
            limit
        ).all()

        return submissions, total

    @staticmethod
    def review_submission(
        db: Session,
        submission_id: str,
        dj_id: str,
        review_data: SubmissionReview,
    ) -> Optional[DJSubmission]:
        """
        DJ reviews a submission (accept, reject, or feature)

        Args:
            db: Database session
            submission_id: ID of submission
            dj_id: ID of DJ (for permission check)
            review_data: Review details

        Returns:
            Updated submission or None if not found
        """
        submission = db.query(DJSubmission).filter(
            and_(DJSubmission.id == submission_id, DJSubmission.dj_id == dj_id)
        ).first()

        if not submission:
            return None

        # Update status
        submission.status = review_data.status
        submission.review_status = review_data.status
        submission.review_feedback = review_data.feedback
        submission.rejection_reason = review_data.rejection_reason
        submission.reviewed_at = datetime.utcnow()
        submission.reviewed_by = dj_id

        # Handle acceptance
        if review_data.status == SubmissionStatus.ACCEPTED:
            submission.accepted_at = datetime.utcnow()
            submission.payment_status = "pending"
            # Calculate payout (90% to creator, 10% platform fee)
            submission.creator_payout = submission.base_price * 0.9
            submission.platform_fee = submission.base_price * 0.1

        # Handle featured
        if review_data.status == SubmissionStatus.FEATURED:
            submission.featured = True
            submission.featured_at = datetime.utcnow()
            submission.featured_reason = review_data.featured_reason
            submission.accepted_at = datetime.utcnow()
            submission.creator_payout = submission.base_price * 0.9
            submission.platform_fee = submission.base_price * 0.1

        # Add scores if provided
        if review_data.quality_score:
            analytics = db.query(SubmissionAnalytics).filter(
                SubmissionAnalytics.submission_id == submission_id
            ).first()
            if analytics:
                analytics.quality_score = review_data.quality_score
            else:
                analytics = SubmissionAnalytics(
                    submission_id=submission_id,
                    dj_id=dj_id,
                    quality_score=review_data.quality_score,
                    fit_score=review_data.fit_score,
                )
                db.add(analytics)

        db.commit()
        db.refresh(submission)

        return submission

    @staticmethod
    def respond_to_submission(
        db: Session,
        submission_id: str,
        sender_id: str,
        response_data: SubmissionResponseCreate,
    ) -> Optional[SubmissionResponse]:
        """
        Add a response/comment to a submission (negotiation, feedback, etc.)

        Args:
            db: Database session
            submission_id: ID of submission
            sender_id: ID of user responding (producer or DJ)
            response_data: Response details

        Returns:
            Created SubmissionResponse or None if submission not found
        """
        submission = db.query(DJSubmission).filter(
            DJSubmission.id == submission_id
        ).first()

        if not submission:
            return None

        # Determine recipient
        recipient_id = submission.dj_id if sender_id == submission.producer_id else submission.producer_id

        response = SubmissionResponse(
            submission_id=submission_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message=response_data.message,
            response_type=response_data.response_type,
            counteroffer_price=response_data.counteroffer_price,
            counteroffer_license=response_data.counteroffer_license,
        )

        # Update submission status if needed
        if response_data.response_type == "counteroffer" and submission.status == SubmissionStatus.PENDING:
            submission.status = SubmissionStatus.UNDER_REVIEW

        db.add(response)
        db.commit()
        db.refresh(response)

        return response

    @staticmethod
    def get_submission_responses(
        db: Session, submission_id: str
    ) -> List[SubmissionResponse]:
        """Get all responses to a submission"""
        return db.query(SubmissionResponse).filter(
            SubmissionResponse.submission_id == submission_id
        ).order_by(SubmissionResponse.created_at).all()

    @staticmethod
    def get_producer_stats(db: Session, producer_id: str) -> SubmissionStats:
        """Get submission statistics for a producer"""
        submissions = db.query(DJSubmission).filter(
            DJSubmission.producer_id == producer_id
        ).all()

        total = len(submissions)
        pending = len([s for s in submissions if s.status == SubmissionStatus.PENDING])
        under_review = len([s for s in submissions if s.status == SubmissionStatus.UNDER_REVIEW])
        accepted = len([s for s in submissions if s.status == SubmissionStatus.ACCEPTED])
        rejected = len([s for s in submissions if s.status == SubmissionStatus.REJECTED])
        featured = len([s for s in submissions if s.status == SubmissionStatus.FEATURED])

        acceptance_rate = (accepted + featured) / total if total > 0 else 0
        average_price = sum(s.base_price for s in submissions) / total if total > 0 else 0
        total_revenue = sum(s.creator_payout for s in submissions if s.payment_status == "completed")

        return SubmissionStats(
            total_submissions=total,
            pending=pending,
            under_review=under_review,
            accepted=accepted,
            rejected=rejected,
            featured=featured,
            acceptance_rate=acceptance_rate,
            average_price=average_price,
            total_revenue=total_revenue,
        )

    @staticmethod
    def get_dj_stats(db: Session, dj_id: str) -> dict:
        """Get submission statistics for a DJ"""
        submissions = db.query(DJSubmission).filter(DJSubmission.dj_id == dj_id).all()

        total_received = len(submissions)
        total_accepted = len([s for s in submissions if s.status == SubmissionStatus.ACCEPTED])
        total_featured = len([s for s in submissions if s.status == SubmissionStatus.FEATURED])
        total_rejected = len([s for s in submissions if s.status == SubmissionStatus.REJECTED])

        # This week
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        this_week = len(
            [
                s
                for s in submissions
                if s.submitted_at > one_week_ago
            ]
        )

        acceptance_rate = (total_accepted + total_featured) / total_received if total_received > 0 else 0

        return {
            "total_received": total_received,
            "total_this_week": this_week,
            "total_accepted": total_accepted,
            "total_featured": total_featured,
            "total_rejected": total_rejected,
            "acceptance_rate": acceptance_rate,
        }

    @staticmethod
    def mark_listened(
        db: Session, submission_id: str, duration_seconds: int = 0
    ) -> Optional[DJSubmission]:
        """
        Record that DJ has listened to a submission

        Args:
            db: Database session
            submission_id: ID of submission
            duration_seconds: How long they listened

        Returns:
            Updated submission
        """
        submission = db.query(DJSubmission).filter(
            DJSubmission.id == submission_id
        ).first()

        if submission:
            submission.listened_count += 1
            
            # Update analytics
            analytics = db.query(SubmissionAnalytics).filter(
                SubmissionAnalytics.submission_id == submission_id
            ).first()

            if analytics:
                analytics.listen_duration_seconds += duration_seconds
            else:
                analytics = SubmissionAnalytics(
                    submission_id=submission_id,
                    dj_id=submission.dj_id,
                    listen_duration_seconds=duration_seconds,
                )
                db.add(analytics)

            db.commit()
            db.refresh(submission)

        return submission

    @staticmethod
    def archive_submission(
        db: Session, submission_id: str, user_id: str
    ) -> Optional[DJSubmission]:
        """Archive a submission (soft delete)"""
        submission = db.query(DJSubmission).filter(
            and_(
                DJSubmission.id == submission_id,
                or_(
                    DJSubmission.producer_id == user_id,
                    DJSubmission.dj_id == user_id,
                ),
            )
        ).first()

        if submission:
            submission.status = SubmissionStatus.ARCHIVED
            db.commit()
            db.refresh(submission)

        return submission

    @staticmethod
    def search_submissions(
        db: Session,
        dj_id: str,
        genre: Optional[str] = None,
        submission_type: Optional[SubmissionType] = None,
        status: Optional[SubmissionStatus] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[DJSubmission], int]:
        """Search submissions with filters"""
        query = db.query(DJSubmission).filter(DJSubmission.dj_id == dj_id)

        if genre:
            query = query.filter(DJSubmission.genre.ilike(f"%{genre}%"))
        if submission_type:
            query = query.filter(DJSubmission.submission_type == submission_type)
        if status:
            query = query.filter(DJSubmission.status == status)
        if min_price is not None:
            query = query.filter(DJSubmission.base_price >= min_price)
        if max_price is not None:
            query = query.filter(DJSubmission.base_price <= max_price)

        total = query.count()
        results = query.order_by(desc(DJSubmission.submitted_at)).offset(skip).limit(
            limit
        ).all()

        return results, total
