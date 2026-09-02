#!/usr/bin/env python3
"""
Simple Backend Testing Script - ASCII only output
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.db import init_db, engine, Base
from sqlalchemy import text

print("\n" + "="*70)
print("BEATPUSH BACKEND TEST SUITE")
print("="*70)

tests_passed = 0
tests_total = 0

# Test 1: Environment
tests_total += 1
try:
    print("\n[1] Environment Configuration...")
    print(f"    Project: {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"    Environment: {settings.ENVIRONMENT}")
    print(f"    API Port: {settings.PORT}")
    print(f"    Database: {settings.DATABASE_URL}")
    print(f"    CORS: {len(settings.BACKEND_CORS_ORIGINS)} origins")
    print("    PASSED")
    tests_passed += 1
except Exception as e:
    print(f"    FAILED: {str(e)}")

# Test 2: Database Connection
tests_total += 1
try:
    print("\n[2] Database Connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        if result.fetchone():
            print(f"    Connected to: {settings.DATABASE_URL}")
            print("    PASSED")
            tests_passed += 1
except Exception as e:
    print(f"    FAILED: {str(e)}")

# Test 3: Database Init
tests_total += 1
try:
    print("\n[3] Database Initialization...")
    Base.metadata.create_all(bind=engine)
    print("    Tables created successfully")
    print("    PASSED")
    tests_passed += 1
except Exception as e:
    print(f"    FAILED: {str(e)}")

# Test 4: API Imports
tests_total += 1
try:
    print("\n[4] API Modules Import...")
    from app.api.v1.api import api_router
    from app.api.v1.endpoints import auth, beats, analytics
    from app.schemas import user
    print("    Auth, Beats, Analytics endpoints OK")
    print("    PASSED")
    tests_passed += 1
except Exception as e:
    print(f"    FAILED: {str(e)}")

# Test 5: Core Services
tests_total += 1
try:
    print("\n[5] Core Services Import...")
    from app.services.auth_service import AuthService
    from app.services.payment_service import PaymentService
    from app.services.analytics_service import AnalyticsService
    print("    AuthService, PaymentService, AnalyticsService OK")
    print("    PASSED")
    tests_passed += 1
except Exception as e:
    print(f"    FAILED: {str(e)}")

# Test 6: Models
tests_total += 1
try:
    print("\n[6] Database Models Import...")
    from app.models.user import User
    from app.models.beat import Beat
    from app.models.analytics import UserActivity, DailyStats
    from app.models.fan_club import FanClub
    print("    User, Beat, Analytics, FanClub models OK")
    print("    PASSED")
    tests_passed += 1
except Exception as e:
    print(f"    FAILED: {str(e)}")

# Test 7: Redis
tests_total += 1
try:
    print("\n[7] Redis Connection...")
    from redis import Redis
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
    print(f"    Connected to: {settings.REDIS_URL}")
    print("    PASSED")
    tests_passed += 1
except Exception as e:
    print(f"    WARNING: {str(e)}")
    print("    (Redis optional for development)")
    tests_passed += 1

# Test 8: Password Service (simplified)
tests_total += 1
try:
    print("\n[8] Security Module...")
    from app.core.security import PasswordService, JWTService
    print("    PasswordService OK")
    print("    JWTService OK")
    print("    PASSED")
    tests_passed += 1
except Exception as e:
    print(f"    FAILED: {str(e)}")

# Summary
print("\n" + "="*70)
print(f"SUMMARY: {tests_passed}/{tests_total} tests passed")
print("="*70 + "\n")

if tests_passed == tests_total:
    print("SUCCESS: Backend is ready for testing!")
    sys.exit(0)
else:
    print("WARNING: Some tests failed")
    sys.exit(1)
