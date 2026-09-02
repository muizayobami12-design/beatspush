"""
Admin Dashboard API Endpoints

Provides endpoints for admin users to manage content, users, and view analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.admin_service import AdminService
from app.schemas.admin import (
    ContentReportCreate,
    ContentReportReview,
    ContentReportResponse,
    UserModerationUpdate,
    UserModerationResponse,
    AdminDashboard,
    ModerationQueue,
    AuditLogResponse,
    ReportType,
    ContentType,
    ModerationStatus,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def check_admin(current_user: User, permission: str = "review_content"):
    """Dependency to check if user is admin with required permission"""
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    # TODO: Verify permission in database
    return current_user


@router.get("/dashboard", response_model=AdminDashboard)
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get admin dashboard with overview stats and recent activity

    Shows:
    - User counts and new signups
    - Pending reports and report stats
    - Recent moderation actions
    - Revenue tracking
    """
    # Check admin access
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    stats = AdminService.get_dashboard_stats(db)
    
    # Get recent reports
    recent_reports, _ = AdminService.get_pending_reports(db, skip=0, limit=5)
    report_list = [ContentReportResponse.from_orm(r) for r in recent_reports]

    # Get recent audit logs
    audit_logs, _ = AdminService.get_audit_logs(db, skip=0, limit=10)

    return AdminDashboard(
        total_users=stats["total_users"],
        new_signups_today=stats["new_signups_today"],
        suspended_count=stats["suspended_count"],
        banned_count=stats["banned_count"],
        pending_reports=stats["pending_reports"],
        reports_today=stats["reports_today"],
        report_stats=stats["report_stats"],
        recent_reports=report_list,
        recent_moderation_actions=[
            {
                "admin_id": log.admin_id,
                "action": log.action,
                "resource": f"{log.resource_type}:{log.resource_id}",
                "timestamp": log.created_at,
            }
            for log in audit_logs
        ],
        daily_revenue=0.0,  # TODO: Calculate from transactions
        monthly_revenue=0.0,  # TODO: Calculate from transactions
        platform_metrics=None,
    )


@router.get("/moderation-queue", response_model=ModerationQueue)
async def get_moderation_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get moderation queue sorted by urgency

    Urgent: New reports, flagged content
    Routine: Standard review queue
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    pending_reports, _ = AdminService.get_pending_reports(db, skip=0, limit=50)

    # Categorize by urgency (newest first = urgent)
    urgent = []
    routine = []

    for report in pending_reports:
        if len(urgent) < 10:
            urgent.append(report)
        else:
            routine.append(report)

    # Get completed today
    from datetime import datetime, timedelta
    completed_today = 0  # TODO: Get from audit logs

    urgent_responses = [ContentReportResponse.from_orm(r) for r in urgent]
    routine_responses = [ContentReportResponse.from_orm(r) for r in routine]

    return ModerationQueue(
        urgent_reports=urgent_responses,
        routine_reports=routine_responses,
        completed_today=completed_today,
        average_review_time=12.5,  # TODO: Calculate from audit logs
    )


@router.get("/reports", response_model=List[ContentReportResponse])
async def get_reports(
    status: Optional[ModerationStatus] = None,
    report_type: Optional[ReportType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get content reports with filtering"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    reports, _ = AdminService.get_pending_reports(db, skip=skip, limit=limit)

    return [ContentReportResponse.from_orm(r) for r in reports]


@router.post("/reports", response_model=ContentReportResponse)
async def create_report(
    report_data: ContentReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create content report (user-facing)"""
    report = AdminService.create_report(
        db,
        current_user.id,
        report_data.report_type,
        report_data.content_type,
        report_data.content_id,
        report_data.content_owner_id,
        report_data.description,
    )

    return ContentReportResponse.from_orm(report)


@router.get("/reports/{report_id}", response_model=ContentReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get report details"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    report = AdminService.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ContentReportResponse.from_orm(report)


@router.post("/reports/{report_id}/review", response_model=dict)
async def review_report(
    report_id: str,
    review_data: ContentReportReview,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Review and take action on a report"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    report = AdminService.review_report(
        db,
        report_id,
        current_user.id,
        review_data.status,
        review_data.action_taken,
        review_data.action_notes,
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "success": True,
        "message": f"Report marked as {review_data.status.value}",
        "action_taken": review_data.action_taken,
    }


# User Moderation Endpoints


@router.get("/users/{user_id}/moderation", response_model=UserModerationResponse)
async def get_user_moderation(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's moderation record"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    moderation = AdminService.get_user_moderation(db, user_id)
    if not moderation:
        raise HTTPException(status_code=404, detail="User moderation record not found")

    return UserModerationResponse.from_orm(moderation)


@router.put("/users/{user_id}/moderation", response_model=dict)
async def update_user_moderation(
    user_id: str,
    update_data: UserModerationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user moderation status"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    moderation = AdminService.update_user_moderation(
        db,
        user_id,
        current_user.id,
        status=update_data.status,
        is_suspended=update_data.is_suspended,
        is_banned=update_data.is_banned,
        reason=update_data.reason,
        suspended_until=update_data.suspended_until,
    )

    return {
        "success": True,
        "message": f"User moderation updated to {update_data.status.value}",
        "user_id": user_id,
    }


@router.post("/users/{user_id}/warn", response_model=dict)
async def warn_user(
    user_id: str,
    reason: str = Query(..., min_length=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Issue warning to user"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    moderation = AdminService.warn_user(db, user_id, current_user.id, reason)

    if not moderation:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "success": True,
        "message": f"Warning issued. Total warnings: {moderation.warning_count}",
        "warning_count": moderation.warning_count,
    }


# Analytics Endpoints


@router.get("/analytics/reports", response_model=dict)
async def get_report_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get report statistics and trends"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    stats = AdminService.get_report_stats(db)

    return {
        "success": True,
        "data": stats.dict(),
    }


@router.get("/analytics/users", response_model=dict)
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user moderation analytics"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    stats = AdminService.get_user_stats(db)

    return {
        "success": True,
        "data": stats.dict(),
    }


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get audit logs of admin actions"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    logs, _ = AdminService.get_audit_logs(db, skip=skip, limit=limit)

    return [AuditLogResponse.from_orm(log) for log in logs]


@router.get("/metrics", response_model=dict)
async def get_platform_metrics(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get platform metrics for the last N days"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    metrics = AdminService.get_recent_metrics(db, days=days)

    return {
        "success": True,
        "data": [
            {
                "date": m.metric_date,
                "active_users": m.active_users,
                "new_signups": m.new_signups,
                "new_beats": m.new_beats,
                "revenue": m.revenue_sales + m.revenue_tips + m.revenue_subscriptions,
            }
            for m in metrics
        ],
    }
