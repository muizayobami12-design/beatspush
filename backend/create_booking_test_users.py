"""
Create test users for booking system testing
"""

import sqlite3
import uuid
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users():
    """Create test users if they don't exist"""
    conn = sqlite3.connect('beatpush.db')
    cursor = conn.cursor()
    
    # Check if djspinall exists
    cursor.execute("SELECT id FROM users WHERE email = 'djspinall@beatpush.com'")
    dj_exists = cursor.fetchone()
    
    # Check if fantest exists
    cursor.execute("SELECT id FROM users WHERE email = 'fantest@beatpush.com'")
    fan_exists = cursor.fetchone()
    
    password_hash = pwd_context.hash("password123")
    now = datetime.utcnow().isoformat()
    
    if not dj_exists:
        dj_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO users (id, email, hashed_password, role, full_name, username, is_active, is_verified, email_verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (dj_id, "djspinall@beatpush.com", password_hash, "dj", "DJ Spinall", "djspinall", True, True, True, now, now))
        
        # Create DJ profile
        cursor.execute("""
            INSERT INTO dj_profiles (id, user_id, stage_name, bio, genres, bpm_range_min, bpm_range_max)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), dj_id, "DJ Spinall", "Professional DJ from Lagos", "Afrobeats,Hip-Hop", 110, 140))
        
        print("✅ Created DJ Spinall user")
    else:
        print("✓ DJ Spinall user already exists")
    
    if not fan_exists:
        fan_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO users (id, email, hashed_password, role, full_name, username, is_active, is_verified, email_verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fan_id, "fantest@beatpush.com", password_hash, "fan", "Test Fan", "testfan", True, True, True, now, now))
        
        # Create Fan profile
        cursor.execute("""
            INSERT INTO fan_profiles (id, user_id, display_name, favorite_genres, location)
            VALUES (?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), fan_id, "Test Fan", "Afrobeats,Hip-Hop", "Lagos, Nigeria"))
        
        print("✅ Created Test Fan user")
    else:
        print("✓ Test Fan user already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Test users ready!")
    print("   Email: djspinall@beatpush.com | Password: password123")
    print("   Email: fantest@beatpush.com | Password: password123")

if __name__ == "__main__":
    create_test_users()
