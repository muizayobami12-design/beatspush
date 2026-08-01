"""Reset passwords for test users"""
import sqlite3
import sys
sys.path.insert(0, '.')

from app.core.security import hash_password

conn = sqlite3.connect('beatpush.db')
cursor = conn.cursor()

# Hash password123
new_password_hash = hash_password("password123")

# Update DJ Spinall
cursor.execute("""
    UPDATE users 
    SET hashed_password = ?
    WHERE email = 'djspinall@beatpush.com'
""", (new_password_hash,))

# Update Fan
cursor.execute("""
    UPDATE users 
    SET hashed_password = ?
    WHERE email = 'fantest@beatpush.com'
""", (new_password_hash,))

conn.commit()
conn.close()

print("✅ Passwords reset to: password123")
print("   - djspinall@beatpush.com")
print("   - fantest@beatpush.com")
