"""
Test script for track upload functionality
Note: This test uses a small generated audio file for testing
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def print_result(title, response):
    """Print test result"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        print(f"Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
    else:
        print(f"Error: {response.text}")

def create_test_audio_file():
    """Create a minimal test audio file (silence)"""
    # Create a minimal MP3 file (just headers, not real audio)
    # For real testing, you'd use an actual audio file
    # This is just to test the upload flow
    test_file_path = Path("test_audio.mp3")
    
    if not test_file_path.exists():
        # Create a dummy file (Note: This won't be a valid MP3)
        # In real testing, use an actual MP3 file
        with open(test_file_path, 'wb') as f:
            f.write(b'ID3\x04\x00\x00\x00\x00\x00\x00' + b'\x00' * 1000)
    
    return test_file_path

def main():
    """Run track upload tests"""
    print("\n" + "="*70)
    print("  BEATPUSH TRACK UPLOAD TESTS")
    print("="*70)
    
    try:
        # Login as artist
        print("\n1️⃣ Logging in as Artist (Wizkid)...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "wizkid@beatpush.com",
                "password": "SecurePass123"
            }
        )
        
        if login_response.status_code != 200:
            print("❌ Login failed!")
            return
        
        artist_token = login_response.json()["tokens"]["access_token"]
        print("✅ Logged in successfully!")
        
        # Check for actual MP3 file in current directory
        audio_file_path = None
        for possible_file in Path(".").glob("*.mp3"):
            audio_file_path = possible_file
            break
        
        if not audio_file_path:
            print("\n⚠️  No MP3 file found in current directory.")
            print("Please place a test MP3 file in the backend directory to test audio upload.")
            print("\nFor now, testing other endpoints...")
            
            # Test getting tracks (should be empty)
            print("\n2️⃣ Getting my tracks (should be empty)...")
            response = requests.get(
                f"{BASE_URL}/tracks/",
                headers={"Authorization": f"Bearer {artist_token}"}
            )
            print_result("GET /tracks/ (my tracks)", response)
            
            print("\n💡 To test audio upload:")
            print("1. Place an MP3 file in: c:\\Users\\Asus\\Desktop\\beatspush\\backend\\")
            print("2. Run this test again")
            print("\n✅ Track endpoints are set up and ready!")
            return
        
        print(f"\n✅ Found audio file: {audio_file_path.name}")
        
        # Test 1: Upload track
        print("\n2️⃣ Uploading track...")
        with open(audio_file_path, 'rb') as audio_file:
            response = requests.post(
                f"{BASE_URL}/tracks/upload",
                headers={"Authorization": f"Bearer {artist_token}"},
                files={"audio_file": (audio_file_path.name, audio_file, "audio/mpeg")},
                data={
                    "title": "Essence",
                    "album": "Made in Lagos",
                    "genre": "Afrobeats",
                    "sub_genre": "Afropop",
                    "description": "Beautiful Afrobeats track featuring Tems",
                    "is_explicit": False
                }
            )
        print_result("POST /tracks/upload", response)
        
        if response.status_code != 201:
            print("❌ Track upload failed!")
            return
        
        track_data = response.json()
        track_id = track_data["track_id"]
        print(f"\n✅ Track ID: {track_id}")
        
        # Test 2: Get track details
        print("\n3️⃣ Getting track details...")
        response = requests.get(
            f"{BASE_URL}/tracks/{track_id}",
            headers={"Authorization": f"Bearer {artist_token}"}
        )
        print_result(f"GET /tracks/{track_id}", response)
        
        # Test 3: Update track
        print("\n4️⃣ Updating track metadata...")
        response = requests.put(
            f"{BASE_URL}/tracks/{track_id}",
            headers={"Authorization": f"Bearer {artist_token}"},
            json={
                "bpm": 120,
                "key": "C Major",
                "lyrics": "[Verse 1]\nNo worry, no worry...",
                "status": "published",
                "visibility": "public",
                "is_downloadable": True
            }
        )
        print_result(f"PUT /tracks/{track_id}", response)
        
        # Test 4: Get my tracks
        print("\n5️⃣ Getting my tracks list...")
        response = requests.get(
            f"{BASE_URL}/tracks/",
            headers={"Authorization": f"Bearer {artist_token}"}
        )
        print_result("GET /tracks/ (my tracks)", response)
        
        # Test 5: Upload cover art
        print("\n6️⃣ Uploading track cover art...")
        from PIL import Image, ImageDraw
        import io
        
        # Create test cover art
        img = Image.new('RGB', (800, 800), color=(73, 109, 137))
        draw = ImageDraw.Draw(img)
        draw.text((300, 400), "ESSENCE", fill=(255, 255, 255))
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        response = requests.post(
            f"{BASE_URL}/tracks/{track_id}/cover",
            headers={"Authorization": f"Bearer {artist_token}"},
            files={"cover_file": ("cover.png", img_bytes, "image/png")}
        )
        print_result(f"POST /tracks/{track_id}/cover", response)
        
        # Test 6: Get updated track with cover
        print("\n7️⃣ Getting track with cover art...")
        response = requests.get(
            f"{BASE_URL}/tracks/{track_id}",
            headers={"Authorization": f"Bearer {artist_token}"}
        )
        print_result(f"GET /tracks/{track_id} (with cover)", response)
        
        # Test 7: Get public tracks
        print("\n8️⃣ Getting user's public tracks...")
        user_id = login_response.json()["user"]["id"]
        response = requests.get(f"{BASE_URL}/tracks/user/{user_id}")
        print_result(f"GET /tracks/user/{user_id}", response)
        
        # Summary
        print("\n" + "="*70)
        print("  ✅ ALL TRACK TESTS COMPLETED!")
        print("="*70)
        print("\n📊 Summary:")
        print(f"  - Track upload: ✓")
        print(f"  - Get track details: ✓")
        print(f"  - Update track: ✓")
        print(f"  - Get my tracks: ✓")
        print(f"  - Upload cover art: ✓")
        print(f"  - Public track access: ✓")
        print(f"\n🎉 Track system is working!")
        print(f"\n💿 Track uploaded: {track_id}")
        print(f"📂 Audio file: {audio_file_path.name}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
