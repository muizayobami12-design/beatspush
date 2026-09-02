"""
Real-time Registration Monitoring Script
Watches backend logs and shows detailed registration flow
"""

import time
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "sqlite:///./beatpush.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_users():
    """Check current user count"""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        return count
    finally:
        db.close()

def get_latest_user():
    """Get latest registered user"""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT id, email, full_name, role, created_at, is_active
            FROM users
            ORDER BY created_at DESC
            LIMIT 1
        """))
        user = result.fetchone()
        return user
    finally:
        db.close()

def check_security_events():
    """Check latest security events"""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT event_type, user_id, ip_address, created_at
            FROM security_events
            ORDER BY created_at DESC
            LIMIT 5
        """))
        events = result.fetchall()
        return events
    finally:
        db.close()

def main():
    print("=" * 60)
    print("🔍 REGISTRATION MONITOR - ACTIVE")
    print("=" * 60)
    print()
    
    print("📊 Initial State:")
    user_count = check_users()
    print(f"   Users in database: {user_count}")
    print()
    
    print("🎯 Monitoring for registration attempts...")
    print("   (This will update when someone registers)")
    print()
    
    # Monitor loop
    last_count = user_count
    check_interval = 2  # Check every 2 seconds
    
    try:
        while True:
            current_count = check_users()
            
            if current_count > last_count:
                print("\n" + "=" * 60)
                print("🎉 NEW REGISTRATION DETECTED!")
                print("=" * 60)
                
                # Get latest user
                user = get_latest_user()
                if user:
                    print(f"\n✅ User Details:")
                    print(f"   ID: {user[0]}")
                    print(f"   Email: {user[1]}")
                    print(f"   Name: {user[2]}")
                    print(f"   Role: {user[3]}")
                    print(f"   Created: {user[4]}")
                    print(f"   Active: {user[5]}")
                
                # Get security events
                events = check_security_events()
                if events:
                    print(f"\n🔒 Latest Security Events:")
                    for event in events:
                        print(f"   - {event[0]} (User: {event[1]}, IP: {event[2]})")
                
                print(f"\n📊 Total Users: {current_count}")
                print("\n✅ REGISTRATION SUCCESSFUL!")
                print("=" * 60)
                
                last_count = current_count
            
            elif current_count < last_count:
                print("\n⚠️  User count decreased (database cleared?)")
                print(f"   Previous: {last_count} → Current: {current_count}")
                last_count = current_count
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")
        print(f"📊 Final count: {check_users()} users")

if __name__ == "__main__":
    main()
