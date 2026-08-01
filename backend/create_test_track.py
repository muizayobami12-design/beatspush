"""
Create a test track for promo link testing
"""

import sqlite3
import uuid
from datetime import datetime

def create_test_track():
    conn = sqlite3.connect('beatpush.db')
    cursor = conn.cursor()
    
    # Get user ID
    cursor.execute("SELECT id, email FROM users WHERE email = 'wizkid@beatpush.com'")
    user = cursor.fetchone()
    
    if not user:
        print("❌ User not found!")
        return
    
    user_id = user[0]
    print(f"✅ Found user: {user[1]} (ID: {user_id})")
    
    # Create test track
    track_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO tracks (
            id, user_id, title, artist_name, album,
            genre, duration, bpm, 
            status, visibility,
            play_count, like_count,
            created_at, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        track_id,
        user_id,
        "Essence (Remix)",
        "Wizkid ft. Tems",
        "Made in Lagos",
        "Afrobeats",
        240,  # 4 minutes
        102,  # BPM
        "PUBLISHED",  # Uppercase to match enum
        "PUBLIC",  # Uppercase to match enum
        0,  # play_count
        0,  # like_count
        now,
        now
    ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Test track created!")
    print(f"   Track ID: {track_id}")
    print(f"   Title: Essence (Remix)")
    print(f"   Artist: Wizkid ft. Tems")

if __name__ == "__main__":
    create_test_track()
