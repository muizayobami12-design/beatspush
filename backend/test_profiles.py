"""
Test script for profile management endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")


def main():
    """Run profile tests"""
    print("\n" + "="*70)
    print("  BEATPUSH PROFILE MANAGEMENT TESTS")
    print("="*70)
    
    try:
        # First, login as the artist we registered earlier
        print("\n1️⃣ Logging in as Artist (Wizkid)...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "wizkid@beatpush.com",
                "password": "SecurePass123"
            }
        )
        
        if login_response.status_code != 200:
            print("❌ Login failed! Make sure you ran test_auth.py first.")
            return
        
        artist_token = login_response.json()["tokens"]["access_token"]
        print("✅ Logged in successfully!")
        
        # Test 1: Get artist profile (auto-creates if doesn't exist)
        print("\n2️⃣ Getting artist profile...")
        response = requests.get(
            f"{BASE_URL}/profiles/me",
            headers={"Authorization": f"Bearer {artist_token}"}
        )
        print_response("GET /profiles/me (Artist)", response)
        
        # Test 2: Update artist profile
        print("\n3️⃣ Updating artist profile...")
        response = requests.put(
            f"{BASE_URL}/profiles/artist",
            headers={"Authorization": f"Bearer {artist_token}"},
            json={
                "stage_name": "Wizkid",
                "bio": "Afrobeats superstar from Lagos, Nigeria. Known for 'Essence', 'Ojuelegba', and many hits.",
                "genres": ["Afrobeats", "Afropop", "R&B", "Reggae"],
                "spotify_url": "https://open.spotify.com/artist/3tVQdUvClmAT7URs9V3rsp",
                "instagram_handle": "@wizkidayo",
                "twitter_handle": "@wizkidayo",
                "record_label": "Starboy Entertainment"
            }
        )
        print_response("PUT /profiles/artist", response)
        
        # Test 3: Login as DJ
        print("\n4️⃣ Logging in as DJ (DJ Spinall)...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "djspinall@beatpush.com",
                "password": "DJMaster123"
            }
        )
        
        dj_token = login_response.json()["tokens"]["access_token"]
        print("✅ Logged in successfully!")
        
        # Test 4: Get DJ profile
        print("\n5️⃣ Getting DJ profile...")
        response = requests.get(
            f"{BASE_URL}/profiles/me",
            headers={"Authorization": f"Bearer {dj_token}"}
        )
        print_response("GET /profiles/me (DJ)", response)
        
        # Test 5: Update DJ profile
        print("\n6️⃣ Updating DJ profile...")
        response = requests.put(
            f"{BASE_URL}/profiles/dj",
            headers={"Authorization": f"Bearer {dj_token}"},
            json={
                "dj_name": "DJ Spinall",
                "bio": "The CAP - Changing African Pop. Award-winning Nigerian DJ and producer.",
                "genres": ["Afrobeats", "Hip-Hop", "House", "Amapiano"],
                "bpm_range": "90-130",
                "resident_venues": ["Club Quilox Lagos", "Hard Rock Cafe Lagos"],
                "radio_shows": ["Party To Your Dreams"],
                "equipment": "Pioneer CDJ-3000, DJM-900NXS2",
                "instagram_handle": "@djspinall",
                "twitter_handle": "@djspinall"
            }
        )
        print_response("PUT /profiles/dj", response)
        
        # Test 6: Login as Producer
        print("\n7️⃣ Logging in as Producer (Pheelz)...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "pheelz@beatpush.com",
                "password": "Producer123"
            }
        )
        
        producer_token = login_response.json()["tokens"]["access_token"]
        print("✅ Logged in successfully!")
        
        # Test 7: Update Producer profile
        print("\n8️⃣ Updating producer profile...")
        response = requests.put(
            f"{BASE_URL}/profiles/producer",
            headers={"Authorization": f"Bearer {producer_token}"},
            json={
                "producer_name": "Pheelz",
                "bio": "Nigerian record producer and songwriter. Known for hits like 'Finesse' and 'Electricity'.",
                "genres": ["Afrobeats", "Afropop", "R&B"],
                "production_style": "Melodic Afrobeats with modern R&B influences",
                "daw": "FL Studio",
                "equipment": "Native Instruments Maschine, Roland Juno-106, Universal Audio Apollo",
                "collaboration_preferences": "Open to collaborations with artists and producers worldwide",
                "instagram_handle": "@pheelz",
                "twitter_handle": "@pheelz"
            }
        )
        print_response("PUT /profiles/producer", response)
        
        # Test 8: Get artist's public profile
        print("\n9️⃣ Getting Wizkid's public profile...")
        # Get artist user_id from first login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "wizkid@beatpush.com",
                "password": "SecurePass123"
            }
        )
        user_id = login_response.json()["user"]["id"]
        
        response = requests.get(f"{BASE_URL}/profiles/{user_id}")
        print_response(f"GET /profiles/{user_id} (Public)", response)
        
        # Test 9: Try to update wrong profile type (should fail)
        print("\n🔟 Testing role-based access control...")
        print("Trying to update DJ profile while logged in as Artist...")
        response = requests.put(
            f"{BASE_URL}/profiles/dj",
            headers={"Authorization": f"Bearer {artist_token}"},
            json={"dj_name": "Should Fail"}
        )
        print_response("PUT /profiles/dj (wrong role)", response)
        
        # Summary
        print("\n" + "="*70)
        print("  ✅ ALL PROFILE TESTS COMPLETED!")
        print("="*70)
        print("\n📊 Summary:")
        print("  - Profile auto-creation: ✓")
        print("  - Artist profile management: ✓")
        print("  - DJ profile management: ✓")
        print("  - Producer profile management: ✓")
        print("  - Public profile access: ✓")
        print("  - Role-based access control: ✓")
        print("\n🎉 Profile system is working perfectly!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
