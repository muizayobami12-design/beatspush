"""
Admin Service for Dashboard & Moderation

Manages admin operations, content moderation, user management, and analytics.
"""

from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from datetime import datetime, timedelta
from app.models.admin import (
    AdminUser,
    ContentReport,
    UserModeration,
    AuditLog,
    PlatformMetrics,
    ModerationStatus,
    ReportType,
    AdminRole,
)
from app.models.user import User
from app.schemas.admin import (
    ReportStats,
    UserStats,
    AdminRole as SchemaAdminRole,
)


class AdminService:
    """Service for admin operations and moderation"""

    # Admin Management
    @staticmethod
    def create_admin(
        db: Session, user_id: str, role: AdminRole, appointed_by_id: str
    ) -> AdminUser:
        """Create new admin user"""
        admin = AdminUser(
            user_id=user_id,
            role=role,
            appointed_by=appointed_by_id,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def get_admin(db: Session, admin_id: str) -> Optional[AdminUser]:
        """Get admin by ID"""
        return db.query(AdminUser).filter(AdminUser.id == admin_id).first()

    @staticmethod
    def is_admin(db: Session, user_id: str) -> bool:
        """Check if user is admin"""
        admin = db.query(AdminUser).filter(
            and_(AdminUser.user_id == user_id, AdminUser.is_active == True)
        ).first()
        return admin is not None

    @staticmethod
    def has_permission(
        db: Session, user_id: str, permission: str
    ) -> bool:
        """Check if admin has specific permission"""
        admin = db.query(AdminUser).filter(
            and_(AdminUser.user_id == user_id, AdminUser.is_active == True)
        ).first()

        if not admin:
            return False

        permission_map = {
            "review_content": admin.can_review_content,
            "suspend_users": admin.can_suspend_users,
            "manage_payments": admin.can_manage_payments,
            "manage_admins": admin.can_manage_admins,
            "view_analytics": admin.can_view_analytics,
        }

        return permission_map.get(permission, False)

    # Content Reporting & Moderation
    @staticmethod
    def create_report(
        db: Session,
        reporter_id: str,
        report_type: ReportType,
        content_type: str,
        content_id: str,
        content_owner_id: str,
        description: Optional[str] = None,
    ) -> ContentReport:
        """Create content report"""
        report = ContentReport(
            reporter_id=reporter_id,
            report_type=report_type,
            content_type=content_type,
            content_id=content_id,
            content_owner_id=content_owner_id,
            description=description,
            status=ModerationStatus.PENDING,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_report(db: Session, report_id: str) -> Optional[ContentReport]:
        """Get report by ID"""
        return db.query(ContentReport).filter(ContentReport.id == report_id).first()

    @staticmethod
    def get_pending_reports(
        db: Session, skip: int = 0, limit: int = 20
    ) -> Tuple[List[ContentReport], int]:
        """Get pending reports for review"""
        query = db.query(ContentReport).filter(
            ContentReport.status == ModerationStatus.PENDING
        )
        total = query.count()
        reports = query.order_by(desc(ContentReport.reported_at)).offset(skip).limit(limit).all()
        return reports, total

    @staticmethod
    def review_report(
        db: Session,
        report_id: str,
        admin_id: str,
        status: ModerationStatus,
        action_taken: Optional[str] = None,
        action_notes: Optional[str] = None,
    ) -> Optional[ContentReport]:
        """Review and action a content report"""
        report = AdminService.get_report(db, report_id)
        if not report:
            return None

        report.status = status
        report.reviewed_by = admin_id
        report.reviewed_at = datetime.utcnow()
        report.action_taken = action_taken
        report.action_notes = action_notes

        # Log action
        AdminService.log_action(
            db, admin_id, "reviewed_report", "report", report_id, action_notes
        )

        db.commit()
        db.refresh(report)
        return report

    # User Moderation
    @staticmethod
    def get_user_moderation(db: Session, user_id: str) -> Optional[UserModeration]:
        """Get user's moderation record"""
        return db.query(UserModeration).filter(
            UserModeration.user_id == user_id
        ).first()

    @staticmethod
    def update_user_moderation(
        db: Session,
        user_id: str,
        admin_id: str,
        status: ModerationStatus = None,
        is_suspended: bool = None,
        is_banned: bool = None,
        reason: Optional[str] = None,
        suspended_until: Optional[datetime] = None,
    ) -> Optional[UserModeration]:
        """Update user moderation status"""
        moderation = AdminService.get_user_moderation(db, user_id)

        if not moderation:
            moderation = UserModeration(user_id=user_id)
            db.add(moderation)

        if status is not None:
            moderation.status = status
        if is_suspended is not None:
            moderation.is_suspended = is_suspended
            if is_suspended:
                moderation.suspended_at = datetime.utcnow()
            moderation.suspended_until = suspended_until
        if is_banned is not None:
            moderation.is_banned = is_banned
        if reason is not None:
            moderation.reason = reason

        moderation.action_by = admin_id
        moderation.action_at = datetime.utcnow()

        # Log action
        action = "suspended_user" if is_suspended else "banned_user" if is_banned else "updated_moderation"
        AdminService.log_action(db, admin_id, action, "user", user_id, reason)

        db.commit()
        db.refresh(moderation)
        return moderation

    @staticmethod
    def warn_user(db: Session, user_id: str, admin_id: str, reason: str) -> Optional[UserModeration]:
        """Issue warning to user"""
        moderation = AdminService.get_user_moderation(db, user_id)

        if not moderation:
            moderation = UserModeration(user_id=user_id)
            db.add(moderation)

        moderation.warning_count = (moderation.warning_count or 0) + 1
        moderation.last_warning_at = datetime.utcnow()
        moderation.action_by = admin_id
        moderation.action_at = datetime.utcnow()

        AdminService.log_action(db, admin_id, "warned_user", "user", user_id, reason)

        db.commit()
        db.refresh(moderation)
        return moderation

    # Analytics & Statistics
    @staticmethod
    def get_report_stats(db: Session) -> ReportStats:
        """Get report statistics"""
        all_reports = db.query(ContentReport).all()

        stats = ReportStats(
            total_reports=len(all_reports),
            pending=len([r for r in all_reports if r.status == ModerationStatus.PENDING]),
            under_review=len([r for r in all_reports if r.status == ModerationStatus.UNDER_REVIEW]),
            approved=len([r for r in all_reports if r.status == ModerationStatus.APPROVED]),
            rejected=len([r for r in all_reports if r.status == ModerationStatus.REJECTED]),
            by_type={},
            by_content_type={},
        )

        # Count by type
        for report_type in ReportType:
            count = len([r for r in all_reports if r.report_type == report_type])
            if count > 0:
                stats.by_type[report_type.value] = count

        # Count by content type
        for report in all_reports:
            key = report.content_type.value if hasattr(report.content_type, 'value') else report.content_type
            stats.by_content_type[key] = stats.by_content_type.get(key, 0) + 1

        return stats

    @staticmethod
    def get_user_stats(db: Session) -> UserStats:
        """Get user moderation statistics"""
        total_users = db.query(User).count()
        
        moderations = db.query(UserModeration).all()

        return UserStats(
            total_users=total_users,
            active_users=total_users - len([m for m in moderations if m.is_suspended or m.is_banned]),
            suspended_users=len([m for m in moderations if m.is_suspended]),
            banned_users=len([m for m in moderations if m.is_banned]),
            warned_users=len([m for m in moderations if m.warning_count > 0]),
            avg_warning_count=sum(m.warning_count for m in moderations) / len(moderations) if moderations else 0,
            new_warnings_today=len(
                [
                    m
                    for m in moderations
                    if m.last_warning_at and m.last_warning_at > datetime.utcnow() - timedelta(days=1)
                ]
            ),
        )

    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict:
        """Get all stats for admin dashboard"""
        users_today = (
            db.query(User).filter(
                User.created_at > datetime.utcnow() - timedelta(days=1)
            ).count()
        )

        suspensions_today = (
            db.query(UserModeration).filter(
                and_(
                    UserModeration.action_at > datetime.utcnow() - timedelta(days=1),
                    UserModeration.is_suspended == True,
                )
            ).count()
        )

        report_stats = AdminService.get_report_stats(db)
        user_stats = AdminService.get_user_stats(db)

        return {
            "total_users": user_stats.total_users,
            "new_signups_today": users_today,
            "suspended_count": user_stats.suspended_users,
            "banned_count": user_stats.banned_users,
            "pending_reports": report_stats.pending,
            "reports_today": len(
                [
                    r
                    for r in db.query(ContentReport).all()
                    if r.reported_at > datetime.utcnow() - timedelta(days=1)
                ]
            ),
            "report_stats": report_stats,
        }

    # Audit Logging
    @staticmethod
    def log_action(
        db: Session,
        admin_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[str] = None,
    ) -> AuditLog:
        """Log admin action for audit trail"""
        log_entry = AuditLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def get_audit_logs(
        db: Session, skip: int = 0, limit: int = 50
    ) -> Tuple[List[AuditLog], int]:
        """Get audit logs"""
        query = db.query(AuditLog)
        total = query.count()
        logs = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
        return logs, total

    # Metrics
    @staticmethod
    def record_metrics(
        db: Session,
        metric_date: datetime,
        metric_type: str,
        data: Dict,
    ) -> PlatformMetrics:
        """Record platform metrics"""
        metrics = PlatformMetrics(
            metric_date=metric_date,
            metric_type=metric_type,
            active_users=data.get("active_users", 0),
            new_signups=data.get("new_signups", 0),
            new_beats=data.get("new_beats", 0),
            revenue_sales=data.get("revenue_sales", 0),
            reports_submitted=data.get("reports_submitted", 0),
        )
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        return metrics

    @staticmethod
    def get_recent_metrics(
        db: Session, days: int = 7
    ) -> List[PlatformMetrics]:
        """Get recent platform metrics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(PlatformMetrics).filter(
            PlatformMetrics.metric_date >= cutoff_date
        ).order_by(desc(PlatformMetrics.metric_date)).all()
