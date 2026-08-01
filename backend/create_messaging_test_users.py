"""
Create test users for messaging system testing
"""
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password
import uuid

def create_test_users():
    """Create two test users for messaging tests"""
    db = SessionLocal()
    
    try:
        # Check if users already exist
        user1 = db.query(User).filter(User.email == "artist@test.com").first()
        user2 = db.query(User).filter(User.email == "dj@test.com").first()
        
        if user1:
            print("✅ User 1 (artist@test.com) already exists")
        else:
            user1 = User(
                id=str(uuid.uuid4()),
                email="artist@test.com",
                username="test_artist",
                full_name="Test Artist",
                hashed_password=hash_password("testpass123"),
                role=UserRole.ARTIST,
                is_active=True,
                is_verified=False
            )
            db.add(user1)
            print("✅ Created User 1 (artist@test.com)")
        
        if user2:
            print("✅ User 2 (dj@test.com) already exists")
        else:
            user2 = User(
                id=str(uuid.uuid4()),
                email="dj@test.com",
                username="test_dj",
                full_name="Test DJ",
                hashed_password=hash_password("testpass123"),
                role=UserRole.DJ,
                is_active=True,
                is_verified=False
            )
            db.add(user2)
            print("✅ Created User 2 (dj@test.com)")
        
        db.commit()
        
        print("\n✅ Test users ready!")
        print(f"   User 1: artist@test.com / testpass123")
        print(f"   User 2: dj@test.com / testpass123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
