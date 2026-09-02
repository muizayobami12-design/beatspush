"""
API endpoints for Submit-to-DJ System

Allows producers to submit beats/tracks to DJs for playlisting,
collaboration, and remix opportunities.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.dj_submission_service import DJSubmissionService
from app.schemas.dj_submission import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionReview,
    SubmissionResponse,
    SubmissionResponseCreate,
    SubmissionListItem,
    SubmissionStats,
    DJSubmissionDashboard,
    ProducerSubmissionDashboard,
    SubmissionStatus,
    SubmissionType,
)

router = APIRouter(prefix="/api/v1/submissions", tags=["dj-submissions"])


# Producer Endpoints


@router.post("/", response_model=SubmissionResponse)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new submission to a DJ

    - **dj_id**: ID of DJ to submit to
    - **beat_id** or **track_id**: Content to submit
    - **submission_type**: Type of submission (playlist_pitch, collaboration, etc.)
    - **base_price**: Price if accepted (optional)
    """
    # Check if current user is producer
    if current_user.role not in ["producer", "artist", "dj"]:
        raise HTTPException(status_code=403, detail="Only producers can create submissions")

    try:
        submission = DJSubmissionService.create_submission(
            db, current_user.id, submission_data
        )
        
        # Populate relationships
        db.refresh(submission)
        
        return SubmissionResponse.from_orm(submission)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/submissions", response_model=ProducerSubmissionDashboard)
async def get_my_submissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get producer's submission dashboard with stats
    """
    if current_user.role not in ["producer", "artist"]:
        raise HTTPException(status_code=403, detail="Only producers can view submissions")

    submissions, _ = DJSubmissionService.get_producer_submissions(
        db, current_user.id, skip=0, limit=10
    )

    stats = DJSubmissionService.get_producer_stats(db, current_user.id)

    recent_submissions = [
        SubmissionListItem.from_orm(s) for s in submissions
    ]

    return ProducerSubmissionDashboard(
        total_submissions=stats.total_submissions,
        pending_reviews=stats.pending,
        accepted_tracks=stats.accepted,
        rejected_tracks=stats.rejected,
        featured_count=stats.featured,
        total_revenue=stats.total_revenue,
        recent_submissions=recent_submissions,
    )


@router.get("/me/submissions/{status}", response_model=List[SubmissionListItem])
async def get_submissions_by_status(
    status: SubmissionStatus,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get producer's submissions filtered by status"""
    if current_user.role not in ["producer", "artist"]:
        raise HTTPException(status_code=403, detail="Only producers can view submissions")

    submissions, _ = DJSubmissionService.get_producer_submissions(
        db, current_user.id, status=status, skip=skip, limit=limit
    )

    return [SubmissionListItem.from_orm(s) for s in submissions]


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get submission details"""
    submission = DJSubmissionService.get_submission(db, submission_id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check permission (producer or DJ can view)
    if current_user.id not in [submission.producer_id, submission.dj_id]:
        raise HTTPException(status_code=403, detail="Not authorized to view this submission")

    return SubmissionResponse.from_orm(submission)


@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: str,
    update_data: SubmissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update submission (only pending submissions can be updated)"""
    submission = DJSubmissionService.update_submission(
        db, submission_id, current_user.id, update_data
    )

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found or cannot be updated (only pending submissions can be modified)",
        )

    return SubmissionResponse.from_orm(submission)


@router.post("/{submission_id}/respond", response_model=dict)
async def respond_to_submission(
    submission_id: str,
    response_data: SubmissionResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Respond to a submission with feedback, counteroffer, or question

    Response types:
    - **feedback**: General feedback
    - **counteroffer**: Negotiate pricing
    - **question**: Ask clarifying question
    - **acceptance**: Accept the submission
    """
    response = DJSubmissionService.respond_to_submission(
        db, submission_id, current_user.id, response_data
    )

    if not response:
        raise HTTPException(status_code=404, detail="Submission not found")

    return {
        "success": True,
        "message": "Response recorded",
        "response_type": response.response_type,
    }


@router.delete("/{submission_id}")
async def archive_submission(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Archive a submission"""
    submission = DJSubmissionService.archive_submission(db, submission_id, current_user.id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found or no permission")

    return {"success": True, "message": "Submission archived"}


# DJ Endpoints


@router.get("/dj/dashboard", response_model=DJSubmissionDashboard)
async def get_dj_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get DJ's submission review dashboard

    Shows pending submissions, stats, and quick actions
    """
    if current_user.role != "dj":
        raise HTTPException(status_code=403, detail="Only DJs can access this")

    # Get pending submissions
    pending, _ = DJSubmissionService.get_dj_submissions(
        db, current_user.id, status=SubmissionStatus.PENDING, skip=0, limit=5
    )

    under_review, _ = DJSubmissionService.get_dj_submissions(
        db, current_user.id, status=SubmissionStatus.UNDER_REVIEW, skip=0, limit=5
    )

    # Get stats
    stats_data = DJSubmissionService.get_dj_stats(db, current_user.id)
    
    all_submissions, _ = DJSubmissionService.get_dj_submissions(
        db, current_user.id, skip=0, limit=100
    )

    # Calculate stats
    total = len(all_submissions)
    pending_count = len(pending)
    under_review_count = len(under_review)
    accepted = stats_data["total_accepted"]
    rejected = stats_data["total_rejected"]
    featured = stats_data["total_featured"]

    stats = SubmissionStats(
        total_submissions=total,
        pending=pending_count,
        under_review=under_review_count,
        accepted=accepted,
        rejected=rejected,
        featured=featured,
        acceptance_rate=stats_data["acceptance_rate"],
        average_price=sum(s.base_price for s in all_submissions) / total if total > 0 else 0,
        total_revenue=0,
    )

    submissions = [SubmissionListItem.from_orm(s) for s in (pending + under_review)[:10]]

    return DJSubmissionDashboard(
        total_pending=pending_count,
        total_under_review=under_review_count,
        total_this_week=stats_data["total_this_week"],
        submissions=submissions,
        stats=stats,
    )


@router.get("/dj/received", response_model=List[SubmissionListItem])
async def get_dj_submissions(
    status: Optional[SubmissionStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get submissions received by DJ"""
    if current_user.role != "dj":
        raise HTTPException(status_code=403, detail="Only DJs can access this")

    submissions, _ = DJSubmissionService.get_dj_submissions(
        db, current_user.id, status=status, skip=skip, limit=limit
    )

    return [SubmissionListItem.from_orm(s) for s in submissions]


@router.post("/{submission_id}/review", response_model=dict)
async def review_submission(
    submission_id: str,
    review_data: SubmissionReview,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Review a submission as DJ (accept, reject, or feature)

    Status options:
    - **accepted**: Accept for consideration
    - **featured**: Feature in your collection
    - **rejected**: Reject with optional reason
    """
    submission = DJSubmissionService.review_submission(
        db, submission_id, current_user.id, review_data
    )

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found or you are not the recipient DJ",
        )

    return {
        "success": True,
        "message": f"Submission {review_data.status.value}",
        "new_status": submission.status.value,
    }


@router.post("/{submission_id}/listened", response_model=dict)
async def mark_listened(
    submission_id: str,
    duration_seconds: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record that DJ has listened to a submission"""
    submission = DJSubmissionService.mark_listened(
        db, submission_id, duration_seconds
    )

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return {
        "success": True,
        "message": "Listen recorded",
        "listen_count": submission.listened_count,
    }


@router.get("/dj/search", response_model=List[SubmissionListItem])
async def search_submissions(
    genre: Optional[str] = None,
    submission_type: Optional[SubmissionType] = None,
    status: Optional[SubmissionStatus] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search submissions with advanced filters"""
    if current_user.role != "dj":
        raise HTTPException(status_code=403, detail="Only DJs can search submissions")

    submissions, _ = DJSubmissionService.search_submissions(
        db,
        current_user.id,
        genre=genre,
        submission_type=submission_type,
        status=status,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit,
    )

    return [SubmissionListItem.from_orm(s) for s in submissions]


@router.get("/{submission_id}/responses", response_model=List[dict])
async def get_responses(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all responses/negotiations for a submission"""
    submission = DJSubmissionService.get_submission(db, submission_id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Check permission
    if current_user.id not in [submission.producer_id, submission.dj_id]:
        raise HTTPException(status_code=403, detail="Not authorized")

    responses = DJSubmissionService.get_submission_responses(db, submission_id)

    return [
        {
            "id": r.id,
            "sender_id": r.sender_id,
            "message": r.message,
            "response_type": r.response_type,
            "counteroffer_price": r.counteroffer_price,
            "created_at": r.created_at,
        }
        for r in responses
    ]
