"""Reset passwords for beat marketplace test users"""
import sqlite3

conn = sqlite3.connect('beatpush.db')
cursor = conn.cursor()

# Get existing password hash from a known user
cursor.execute("SELECT hashed_password FROM users WHERE email = 'djspinall@beatpush.com'")
result = cursor.fetchone()

if result:
    password_hash = result[0]
    
    # Update Pheelz (producer)
    cursor.execute("""
        UPDATE users 
        SET hashed_password = ?
        WHERE email = 'pheelz@beatpush.com'
    """, (password_hash,))
    
    # Update Wizkid (artist)
    cursor.execute("""
        UPDATE users 
        SET hashed_password = ?
        WHERE email = 'wizkid@beatpush.com'
    """, (password_hash,))
    
    conn.commit()
    print("✅ Passwords reset for test users")
    print("   - pheelz@beatpush.com")
    print("   - wizkid@beatpush.com")
else:
    print("❌ Could not get password hash")

conn.close()
