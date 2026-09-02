#!/usr/bin/env python
"""Create a test user for development"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole, UserTier
from app.core.security import PasswordService
from app.core.config import settings
from app.db.database import Base

# Create database connection
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
db = SessionLocal()

try:
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "testuser@example.com").first()
    if existing_user:
        print("✅ Test user already exists!")
        print(f"   Email: {existing_user.email}")
        print(f"   Role: {existing_user.role.value}")
        print(f"   Status: {'Active' if existing_user.is_active else 'Inactive'}")
        print("")
        print("You can now log in at: http://localhost:3000/login")
        print("   Email: testuser@example.com")
        print("   Password: TestPassword123!")
        sys.exit(0)
    
    # Create test user
    test_user = User(
        email="testuser@example.com",
        full_name="Test User",
        username="testuser",
        hashed_password=PasswordService.hash_password("TestPassword123!"),
        role=UserRole.ARTIST,
        tier=UserTier.FREE,
        is_active=True,
        email_verified=True
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print("✅ Test user created successfully!")
    print(f"   Email: {test_user.email}")
    print(f"   Password: TestPassword123!")
    print(f"   Role: {test_user.role.value}")
    print(f"   Tier: {test_user.tier.value}")
    print("")
    print("You can now log in at: http://localhost:3000/login")
    
except Exception as e:
    print(f"❌ Error creating test user: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    sys.exit(1)
finally:
    db.close()

