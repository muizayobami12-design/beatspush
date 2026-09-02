"""Fix test user - add missing fields"""
from sqlalchemy import text
from app.db.database import SessionLocal

db = SessionLocal()

try:
    # Update test user with missing fields
    db.execute(
        text("""
            UPDATE users 
            SET tier = 'FREE', 
                is_verified = TRUE 
            WHERE email = :email
        """),
        {"email": "test@beatpush.com"}
    )
    db.commit()
    
    # Verify the update
    result = db.execute(
        text("""
            SELECT email, username, tier, is_verified, email_verified, role 
            FROM users 
            WHERE email = :email
        """),
        {"email": "test@beatpush.com"}
    ).first()
    
    if result:
        print("✅ User fixed successfully!")
        print(f"\n📧 Email: {result[0]}")
        print(f"👤 Username: {result[1]}")
        print(f"💎 Tier: {result[2]}")
        print(f"✓ Is Verified: {result[3]}")
        print(f"✓ Email Verified: {result[4]}")
        print(f"🎵 Role: {result[5]}")
        print("\n🔑 Password: Test123!")
        print("\n" + "="*50)
        print("🚀 LOGIN AT: http://localhost:3000/auth/login")
        print("="*50)
    else:
        print("❌ User not found")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
