"""
BeatPush - Main Application Entry Point
FastAPI application with AI-powered music promotion features
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db import init_db, check_db_connection
from app.api.v1.api import api_router
from pathlib import Path
import logging

# APScheduler imports for background jobs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.jobs.subscription_jobs import (
    process_subscription_renewals,
    retry_failed_payments,
    send_renewal_reminders,
    cancel_expired_trials,
    send_welcome_messages,
    send_engagement_messages
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Music Promotion Platform for African Creators",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Mount static files (for serving uploaded images)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Initialize APScheduler for background jobs
scheduler = AsyncIOScheduler()


def setup_background_jobs():
    """Configure and start background jobs."""
    logger.info("⏰ Setting up background jobs...")
    
    # Daily subscription renewals - 2:00 AM UTC
    scheduler.add_job(
        process_subscription_renewals,
        trigger=CronTrigger(hour=2, minute=0),
        id="process_subscription_renewals",
        name="Process Subscription Renewals",
        replace_existing=True
    )
    
    # Retry failed payments - 10:00 AM UTC daily
    scheduler.add_job(
        retry_failed_payments,
        trigger=CronTrigger(hour=10, minute=0),
        id="retry_failed_payments",
        name="Retry Failed Payments",
        replace_existing=True
    )
    
    # Send renewal reminders - 9:00 AM UTC daily
    scheduler.add_job(
        send_renewal_reminders,
        trigger=CronTrigger(hour=9, minute=0),
        id="send_renewal_reminders",
        name="Send Renewal Reminders",
        replace_existing=True
    )
    
    # Cancel expired trials - 3:00 AM UTC daily
    scheduler.add_job(
        cancel_expired_trials,
        trigger=CronTrigger(hour=3, minute=0),
        id="cancel_expired_trials",
        name="Cancel Expired Trials",
        replace_existing=True
    )
    
    # Send welcome messages - Every hour
    scheduler.add_job(
        send_welcome_messages,
        trigger=CronTrigger(minute=0),  # Run at the top of every hour
        id="send_welcome_messages",
        name="Send Welcome Messages",
        replace_existing=True
    )
    
    # Send engagement messages - 11:00 AM UTC daily
    scheduler.add_job(
        send_engagement_messages,
        trigger=CronTrigger(hour=11, minute=0),
        id="send_engagement_messages",
        name="Send Engagement Messages",
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("✅ Background jobs configured and started")
    logger.info(f"📅 Active jobs: {len(scheduler.get_jobs())}")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name} (ID: {job.id})")



@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "Welcome to BeatPush API",
        "version": settings.VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "database": "connected" if check_db_connection() else "disconnected"
    }


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup"""
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting up...")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 CORS Origins: {settings.BACKEND_CORS_ORIGINS}")
    
    # Check database connection
    print("🔍 Checking database connection...")
    if check_db_connection():
        print("✅ Database connection successful!")
    else:
        print("⚠️  Database connection failed - will try to initialize...")
    
    # Initialize database (create tables)
    print("📊 Initializing database tables...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    # Start background jobs
    try:
        setup_background_jobs()
    except Exception as e:
        print(f"⚠️  Background jobs warning: {e}")
    
    print(f"✅ Application ready!")



@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on application shutdown"""
    print(f"👋 {settings.PROJECT_NAME} shutting down...")
    
    # Shutdown scheduler
    if scheduler.running:
        scheduler.shutdown()
        print("⏰ Background jobs stopped")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
