"""
Comprehensive Security Features Test
Tests all Day 1-3 security implementations
"""

import asyncio
import sys
from datetime import datetime

# Test results tracking
test_results = []

def log_test(name: str, passed: bool, message: str = ""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results.append({
        "name": name,
        "passed": passed,
        "message": message
    })
    print(f"{status} - {name}")
    if message:
        print(f"   {message}")


async def test_turnstile_service():
    """Test Cloudflare Turnstile service"""
    print("\n🔐 Testing Turnstile Service...")
    
    try:
        from app.services.turnstile_service import turnstile_service
        
        # Test 1: Service initialization
        log_test(
            "Turnstile service initialized",
            turnstile_service is not None,
            "Service instance created"
        )
        
        # Test 2: Development mode bypass
        result = await turnstile_service.verify_token("test_token", "127.0.0.1")
        log_test(
            "Turnstile development mode",
            result.get("success") or result.get("bypass"),
            "Development bypass or verification works"
        )
        
        return True
    except Exception as e:
        log_test("Turnstile service", False, f"Error: {str(e)}")
        return False


async def test_fraud_detection():
    """Test fraud detection service"""
    print("\n🕵️ Testing Fraud Detection...")
    
    try:
        from app.services.fraud_detection_service import fraud_detector
        
        # Test 1: Registration scoring
        result = await fraud_detector.score_registration(
            email="test@example.com",
            ip_address="127.0.0.1",
            device_id="test_device_123",
            country="NG",
            db=None
        )
        
        log_test(
            "Fraud detection - registration",
            "risk_score" in result and "decision" in result,
            f"Risk score: {result.get('risk_score')}, Decision: {result.get('decision')}"
        )
        
        # Test 2: Login scoring
        user_data = {
            "last_login_at": None,
            "last_login_ip": None,
            "device_id": None,
            "failed_login_attempts": 0
        }
        
        result = await fraud_detector.score_login(
            user_id="test_user",
            ip_address="127.0.0.1",
            device_id="test_device_123",
            user_data=user_data,
            db=None
        )
        
        log_test(
            "Fraud detection - login",
            "risk_score" in result and "action" in result,
            f"Risk score: {result.get('risk_score')}, Action: {result.get('action')}"
        )
        
        # Test 3: Transaction scoring
        result = await fraud_detector.score_transaction(
            user_id="test_user",
            amount=5000.0,
            payment_method="paystack",
            user_data={"account_age_days": 10, "avg_transaction_amount": 2000},
            db=None
        )
        
        log_test(
            "Fraud detection - transaction",
            "risk_score" in result and "decision" in result,
            f"Risk score: {result.get('risk_score')}, Decision: {result.get('decision')}"
        )
        
        return True
    except Exception as e:
        log_test("Fraud detection", False, f"Error: {str(e)}")
        return False


async def test_rate_limiter():
    """Test rate limiting service"""
    print("\n⏱️ Testing Rate Limiter...")
    
    try:
        from redis import Redis
        from app.services.rate_limiter import RateLimiter, get_rate_limit_config
        from app.core.config import settings
        
        # Initialize Redis
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        rate_limiter = RateLimiter(redis_client)
        
        # Test 1: Check rate limit (should pass)
        identifier = f"test_{datetime.now().timestamp()}"
        allowed, remaining = await rate_limiter.check_rate_limit(
            identifier=identifier,
            action="test",
            max_requests=5,
            window_seconds=60
        )
        
        log_test(
            "Rate limiter - first request",
            allowed is True and remaining == 4,
            f"Allowed: {allowed}, Remaining: {remaining}"
        )
        
        # Test 2: Multiple requests
        for i in range(4):
            allowed, remaining = await rate_limiter.check_rate_limit(
                identifier=identifier,
                action="test",
                max_requests=5,
                window_seconds=60
            )
        
        log_test(
            "Rate limiter - multiple requests",
            remaining == 0,
            f"After 5 requests, remaining: {remaining}"
        )
        
        # Test 3: Exceed limit
        allowed, remaining = await rate_limiter.check_rate_limit(
            identifier=identifier,
            action="test",
            max_requests=5,
            window_seconds=60
        )
        
        log_test(
            "Rate limiter - limit exceeded",
            allowed is False,
            f"6th request blocked: {not allowed}"
        )
        
        # Cleanup
        rate_limiter.clear_rate_limit(identifier, "test")
        
        return True
    except Exception as e:
        log_test("Rate limiter", False, f"Error: {str(e)}")
        print(f"   Note: Make sure Redis is running on {settings.REDIS_URL}")
        return False


async def test_sms_service():
    """Test SMS/OTP service"""
    print("\n📱 Testing SMS Service...")
    
    try:
        from app.services.sms_service import sms_service
        
        # Test 1: Send OTP (development mode)
        result = await sms_service.send_otp("+2348012345678")
        
        log_test(
            "SMS service - send OTP",
            result.get("success") is True,
            f"OTP sent: {result.get('mock_otp', 'N/A')} (dev mode)"
        )
        
        # Test 2: Verify OTP token
        if result.get("success"):
            from app.core.security import verify_otp_token
            otp_token = result.get("otp_token")
            mock_otp = result.get("mock_otp", "123456")
            
            verified = verify_otp_token(otp_token, mock_otp)
            
            log_test(
                "SMS service - verify OTP",
                verified is not None,
                f"OTP verified: {verified is not None}"
            )
        
        return True
    except Exception as e:
        log_test("SMS service", False, f"Error: {str(e)}")
        return False


async def test_security_utilities():
    """Test security utility functions"""
    print("\n🔧 Testing Security Utilities...")
    
    try:
        from app.core.security import (
            hash_password,
            verify_password,
            create_access_token,
            create_refresh_token,
            decode_token,
            create_token_pair,
            generate_otp,
            get_cookie_settings
        )
        
        # Test 1: Password hashing
        password = "test_password_123"
        hashed = hash_password(password)
        verified = verify_password(password, hashed)
        
        log_test(
            "Password hashing",
            verified is True,
            "Hash and verify working"
        )
        
        # Test 2: Token creation
        token_data = {"sub": "user123", "email": "test@example.com", "role": "artist"}
        access_token = create_access_token(token_data)
        
        log_test(
            "Access token creation",
            len(access_token) > 50,
            f"Token length: {len(access_token)}"
        )
        
        # Test 3: Token decoding
        decoded = decode_token(access_token)
        
        log_test(
            "Token decoding",
            decoded is not None and decoded.get("sub") == "user123",
            f"Decoded user: {decoded.get('sub') if decoded else 'None'}"
        )
        
        # Test 4: Token pair creation
        access, refresh = create_token_pair("user123", "test@example.com", "artist")
        
        log_test(
            "Token pair creation",
            len(access) > 50 and len(refresh) > 50,
            f"Access: {len(access)} chars, Refresh: {len(refresh)} chars"
        )
        
        # Test 5: OTP generation
        otp = generate_otp()
        
        log_test(
            "OTP generation",
            len(otp) == 6 and otp.isdigit(),
            f"OTP: {otp}"
        )
        
        # Test 6: Cookie settings
        cookie_settings = get_cookie_settings()
        
        log_test(
            "Cookie settings",
            cookie_settings.get("httponly") is True,
            f"HttpOnly: {cookie_settings.get('httponly')}"
        )
        
        return True
    except Exception as e:
        log_test("Security utilities", False, f"Error: {str(e)}")
        return False


async def test_database_schema():
    """Test database schema for security features"""
    print("\n💾 Testing Database Schema...")
    
    try:
        import sqlite3
        
        conn = sqlite3.connect('beatpush.db')
        cursor = conn.cursor()
        
        # Test 1: Check users table has security columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = [
            'device_id',
            'device_info',
            'last_login_ip',
            'last_login_country',
            'failed_login_attempts'
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        log_test(
            "Users table - security columns",
            len(missing_columns) == 0,
            f"All security columns present" if not missing_columns else f"Missing: {missing_columns}"
        )
        
        # Test 2: Check security_events table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='security_events'
        """)
        
        table_exists = cursor.fetchone() is not None
        
        log_test(
            "Security events table",
            table_exists,
            "Table exists" if table_exists else "Table missing"
        )
        
        # Test 3: Check indexes
        cursor.execute("PRAGMA index_list(users)")
        indexes = cursor.fetchall()
        has_device_index = any('device_id' in str(idx) for idx in indexes)
        
        log_test(
            "Database indexes",
            has_device_index or len(indexes) > 0,
            f"Found {len(indexes)} indexes"
        )
        
        conn.close()
        return True
    except Exception as e:
        log_test("Database schema", False, f"Error: {str(e)}")
        return False


def test_configuration():
    """Test configuration and environment setup"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from app.core.config import settings
        
        # Test 1: Check critical settings
        log_test(
            "Config - SECRET_KEY",
            len(settings.SECRET_KEY) > 10,
            "Secret key configured"
        )
        
        log_test(
            "Config - JWT_SECRET_KEY",
            len(settings.JWT_SECRET_KEY) > 10,
            "JWT secret key configured"
        )
        
        log_test(
            "Config - DATABASE_URL",
            settings.DATABASE_URL is not None,
            f"Database: {settings.DATABASE_URL[:30]}..."
        )
        
        log_test(
            "Config - REDIS_URL",
            settings.REDIS_URL is not None,
            f"Redis: {settings.REDIS_URL}"
        )
        
        # Test 2: Check security keys
        log_test(
            "Config - Turnstile keys",
            settings.TURNSTILE_SECRET_KEY is not None and settings.TURNSTILE_SITE_KEY is not None,
            "Turnstile configured"
        )
        
        log_test(
            "Config - Termii key",
            settings.TERMII_API_KEY is not None,
            "Termii configured"
        )
        
        # Test 3: Check environment
        log_test(
            "Config - Environment",
            settings.ENVIRONMENT in ["development", "production"],
            f"Environment: {settings.ENVIRONMENT}"
        )
        
        return True
    except Exception as e:
        log_test("Configuration", False, f"Error: {str(e)}")
        return False


async def run_all_tests():
    """Run all security tests"""
    print("=" * 70)
    print("🧪 BEATPUSH SECURITY FEATURES TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    tests = [
        ("Configuration", test_configuration),
        ("Database Schema", test_database_schema),
        ("Security Utilities", test_security_utilities),
        ("Turnstile Service", test_turnstile_service),
        ("Fraud Detection", test_fraud_detection),
        ("Rate Limiter", test_rate_limiter),
        ("SMS Service", test_sms_service),
    ]
    
    results = []
    for name, test_func in tests:
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results.append(result)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in test_results if r["passed"])
    failed = sum(1 for r in test_results if not r["passed"])
    total = len(test_results)
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for result in test_results:
            if not result["passed"]:
                print(f"   - {result['name']}: {result['message']}")
    
    print("\n" + "=" * 70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
