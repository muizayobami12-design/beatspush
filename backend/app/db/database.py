"""
Database connection and session management
Supports both SQLite (development) and PostgreSQL (production)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
# For SQLite, we'll use a local file
# For PostgreSQL, we'll use the DATABASE_URL from settings

# Determine database type from URL
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=settings.DATABASE_ECHO
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Database session dependency
    Use this in FastAPI endpoints to get a database session
    
    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    Call this on application startup
    """
    # Import all models here to ensure they're registered with Base
    from app.models import (  # noqa
        User, ArtistProfile, DJProfile, ProducerProfile, FanProfile, Track,
        Conversation, ConversationParticipant, Message, MessageReadReceipt,
        MessageAttachment, BlockedUser, MessageReport, UserMessageSettings,
        FanClub, MembershipTier, Subscription, SubscriptionPayment,
        ExclusiveContent, CreatorPayout,
        UserPreferenceProfile, BeatSimilarityCache, TrendingBeatCache, RecommendationLog
    )
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def check_db_connection():
    """
    Check if database connection is working
    Returns True if connection successful, False otherwise
    """
    try:
        db = SessionLocal()
        # Try to execute a simple query
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
