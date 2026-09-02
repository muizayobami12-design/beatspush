"""
Background job scheduler for fan club system.

Uses APScheduler to run periodic jobs for:
- Subscription renewal
- Payment retry
- Engagement automation
- Cleanup tasks
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class SubscriptionScheduler:
    """
    Manages background jobs for subscription system.
    
    Jobs:
    - Daily renewal: 00:00 UTC
    - Hourly retry: Every hour
    - Daily reminders: 08:00 UTC
    - Trial cleanup: Daily 02:00 UTC
    """
    
    _scheduler: Optional[BackgroundScheduler] = None
    
    @classmethod
    def init_scheduler(cls):
        """Initialize APScheduler."""
        if cls._scheduler is not None:
            return cls._scheduler
        
        cls._scheduler = BackgroundScheduler(daemon=True)
        logger.info("SubscriptionScheduler initialized")
        return cls._scheduler
    
    @classmethod
    def start(cls):
        """Start the scheduler."""
        if cls._scheduler is None:
            cls.init_scheduler()
        
        if not cls._scheduler.running:
            cls._scheduler.start()
            logger.info("SubscriptionScheduler started")
    
    @classmethod
    def stop(cls):
        """Stop the scheduler."""
        if cls._scheduler is not None and cls._scheduler.running:
            cls._scheduler.shutdown(wait=True)
            logger.info("SubscriptionScheduler stopped")
    
    @classmethod
    def add_job(
        cls,
        func: Callable,
        trigger,
        id: str,
        name: str,
        misfire_grace_time: int = 60,
        coalesce: bool = True,
        max_instances: int = 1,
        **kwargs
    ):
        """
        Add a job to the scheduler.
        
        Args:
            func: Function to execute
            trigger: Trigger type (cron, interval, etc.)
            id: Unique job ID
            name: Human-readable job name
            misfire_grace_time: Grace period in seconds for missed jobs
            coalesce: Combine multiple misses into single execution
            max_instances: Max concurrent instances of this job
        """
        if cls._scheduler is None:
            cls.init_scheduler()
        
        # Check if job already exists
        existing_job = cls._scheduler.get_job(id)
        if existing_job:
            logger.debug(f"Job {id} already exists, updating...")
            existing_job.remove()
        
        job = cls._scheduler.add_job(
            func,
            trigger=trigger,
            id=id,
            name=name,
            misfire_grace_time=misfire_grace_time,
            coalesce=coalesce,
            max_instances=max_instances,
            **kwargs
        )
        
        logger.info(f"Added job: {name} (ID: {id})")
        return job
    
    @classmethod
    def get_job(cls, id: str):
        """Get job by ID."""
        if cls._scheduler is None:
            return None
        return cls._scheduler.get_job(id)
    
    @classmethod
    def list_jobs(cls):
        """List all scheduled jobs."""
        if cls._scheduler is None:
            return []
        return cls._scheduler.get_jobs()
    
    @classmethod
    def remove_job(cls, id: str):
        """Remove job by ID."""
        if cls._scheduler is None:
            return
        cls._scheduler.remove_job(id)
        logger.info(f"Removed job: {id}")


def schedule_subscription_jobs():
    """Schedule all subscription-related jobs."""
    from app.jobs.subscription_jobs import (
        process_subscription_renewals,
        retry_failed_payments,
        send_renewal_reminders,
        cancel_expired_trials
    )
    
    scheduler = SubscriptionScheduler.init_scheduler()
    
    # Daily renewal at 00:00 UTC
    SubscriptionScheduler.add_job(
        process_subscription_renewals,
        CronTrigger(hour=0, minute=0),
        id="subscription_renewal_daily",
        name="Daily Subscription Renewal",
        coalesce=True,
        max_instances=1
    )
    
    # Hourly payment retry at :00 minutes
    SubscriptionScheduler.add_job(
        retry_failed_payments,
        CronTrigger(minute=0),
        id="payment_retry_hourly",
        name="Hourly Payment Retry",
        coalesce=True,
        max_instances=1
    )
    
    # Daily reminders at 08:00 UTC
    SubscriptionScheduler.add_job(
        send_renewal_reminders,
        CronTrigger(hour=8, minute=0),
        id="renewal_reminders_daily",
        name="Daily Renewal Reminders",
        coalesce=True,
        max_instances=1
    )
    
    # Trial cleanup at 02:00 UTC
    SubscriptionScheduler.add_job(
        cancel_expired_trials,
        CronTrigger(hour=2, minute=0),
        id="trial_cleanup_daily",
        name="Daily Trial Cleanup",
        coalesce=True,
        max_instances=1
    )
    
    logger.info("All subscription jobs scheduled")


def log_job_execution(job_id: str, job_name: str, status: str, details: str = ""):
    """Log job execution for audit trail."""
    timestamp = datetime.utcnow().isoformat()
    message = f"[{timestamp}] {job_name} ({job_id}): {status}"
    if details:
        message += f" - {details}"
    
    if status == "error":
        logger.error(message)
    elif status == "warning":
        logger.warning(message)
    else:
        logger.info(message)
