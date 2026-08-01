"""Quick script to check tracks in database"""
import sqlite3

conn = sqlite3.connect('beatpush.db')
cursor = conn.cursor()

# Get all tracks
cursor.execute("SELECT id, title, artist_name, user_id FROM tracks")
tracks = cursor.fetchall()

print(f"📊 Total tracks: {len(tracks)}\n")

if tracks:
    for track in tracks:
        print(f"  - {track[1]} by {track[2]} (User: {track[3]})")
else:
    print("  ❌ No tracks found!")
    
    # Check if wizkid user exists
    cursor.execute("SELECT id, email, full_name FROM users WHERE email='wizkid@beatpush.com'")
    user = cursor.fetchone()
    
    if user:
        print(f"\n✅ Wizkid user exists (ID: {user[0]})")
        print("   But has no tracks created.")
    else:
        print("\n❌ Wizkid user not found!")

conn.close()
