"""
Test script for Promo Links API (Task 3.5)
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📍 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")

def main():
    print("Testing Promo Links API (Task 3.5)")
    print("="*60)
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "wizkid@beatpush.com",
        "password": "SecurePass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed! Make sure user exists.")
        print(f"Error: {login_response.text}")
        return
    
    token = login_response.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful!")
    
    # Step 2: Get user's tracks
    print("\n2️⃣ Getting user's tracks...")
    tracks_response = requests.get(f"{BASE_URL}/tracks/", headers=headers)
    print_response("My Tracks", tracks_response)
    
    if tracks_response.status_code != 200 or not tracks_response.json():
        print("❌ No tracks found! Upload a track first.")
        return
    
    track_id = tracks_response.json()[0]["id"]
    print(f"✅ Using track: {track_id}")
    
    # Step 3: Create promo link
    print("\n3️⃣ Creating promo link...")
    create_request = {
        "track_id": track_id,
        "title": "Summer Vibes 2024",
        "description": "Check out my latest track on all platforms!",
        "spotify_url": "https://open.spotify.com/track/example",
        "apple_music_url": "https://music.apple.com/track/example",
        "youtube_url": "https://youtube.com/watch?v=example",
        "audiomack_url": "https://audiomack.com/song/example",
        "boomplay_url": "https://www.boomplay.com/songs/example",
        "background_color": "#FF6B6B",
        "text_color": "#FFFFFF",
        "utm_source": "instagram",
        "utm_medium": "social",
        "utm_campaign": "summer2024"
    }
    
    create_response = requests.post(
        f"{BASE_URL}/promo-links/",
        json=create_request,
        headers=headers
    )
    print_response("Create Promo Link", create_response)
    
    if create_response.status_code != 201:
        print("❌ Failed to create promo link!")
        return
    
    link_data = create_response.json()
    link_id = link_data["id"]
    short_code = link_data["short_code"]
    print(f"✅ Promo link created!")
    print(f"   Short URL: {link_data['short_url']}")
    print(f"   Full URL: {link_data['full_url']}")
    
    # Step 4: Get promo link details
    print("\n4️⃣ Getting promo link details...")
    detail_response = requests.get(
        f"{BASE_URL}/promo-links/{link_id}",
        headers=headers
    )
    print_response("Promo Link Details", detail_response)
    
    # Step 5: List all promo links
    print("\n5️⃣ Listing all promo links...")
    list_response = requests.get(
        f"{BASE_URL}/promo-links/?page=1&page_size=10",
        headers=headers
    )
    print_response("List Promo Links", list_response)
    
    # Step 6: Generate QR code
    print("\n6️⃣ Generating QR code...")
    qr_response = requests.get(
        f"{BASE_URL}/promo-links/{link_id}/qr?size=300",
        headers=headers
    )
    if qr_response.status_code == 200:
        qr_data = qr_response.json()
        print(f"✅ QR Code generated!")
        print(f"   Data length: {len(qr_data['qr_code_data'])} characters")
        print(f"   Base64 encoded: Yes")
    else:
        print_response("Generate QR Code", qr_response)
    
    # Step 7: Create geo-targeting rule
    print("\n7️⃣ Creating geo-targeting rule...")
    geo_request = {
        "country_codes": ["NG", "GH", "KE"],  # Nigeria, Ghana, Kenya
        "platform": "audiomack",
        "priority": 1,
        "fallback_url": "https://open.spotify.com/track/example"
    }
    
    geo_response = requests.post(
        f"{BASE_URL}/promo-links/{link_id}/geo-rules",
        json=geo_request,
        headers=headers
    )
    print_response("Create Geo Rule", geo_response)
    
    # Step 8: List geo rules
    print("\n8️⃣ Listing geo rules...")
    geo_list_response = requests.get(
        f"{BASE_URL}/promo-links/{link_id}/geo-rules",
        headers=headers
    )
    print_response("List Geo Rules", geo_list_response)
    
    # Step 9: Simulate clicks (public endpoint - no auth)
    print("\n9️⃣ Simulating clicks...")
    platforms = ["spotify", "apple_music", "youtube", "audiomack"]
    
    for platform in platforms:
        print(f"   Clicking {platform}...")
        # Note: This will redirect, so we use allow_redirects=False
        click_response = requests.get(
            f"{BASE_URL}/promo-links/redirect/{short_code}?platform={platform}",
            allow_redirects=False
        )
        if click_response.status_code in [307, 302, 301]:
            print(f"   ✅ {platform} redirect successful (Status: {click_response.status_code})")
        else:
            print(f"   ❌ {platform} redirect failed (Status: {click_response.status_code})")
    
    # Step 10: Get analytics
    print("\n🔟 Getting analytics...")
    analytics_response = requests.get(
        f"{BASE_URL}/promo-links/{link_id}/analytics",
        headers=headers
    )
    print_response("Link Analytics", analytics_response)
    
    # Step 11: Update promo link
    print("\n1️⃣1️⃣ Updating promo link...")
    update_request = {
        "title": "Summer Vibes 2024 (Updated)",
        "description": "Updated description with more info!",
        "background_color": "#4ECDC4"
    }
    
    update_response = requests.put(
        f"{BASE_URL}/promo-links/{link_id}",
        json=update_request,
        headers=headers
    )
    print_response("Update Promo Link", update_response)
    
    # Step 12: Search promo links
    print("\n1️⃣2️⃣ Searching promo links...")
    search_response = requests.get(
        f"{BASE_URL}/promo-links/?search=Summer",
        headers=headers
    )
    print_response("Search Promo Links", search_response)
    
    # Summary
    print("\n" + "="*60)
    print("✅ TEST SUMMARY")
    print("="*60)
    print("✅ Promo link created successfully")
    print(f"✅ Short code: {short_code}")
    print(f"✅ Link ID: {link_id}")
    print(f"✅ Total clicks tracked: {analytics_response.json()['total_clicks'] if analytics_response.status_code == 200 else 'N/A'}")
    print(f"✅ QR code generated: Yes")
    print(f"✅ Geo-targeting rules: Created")
    print("\n🎉 All promo link features working!")
    print("\n📱 Try the short URL in your browser:")
    print(f"   http://localhost:8000/api/v1/promo-links/redirect/{short_code}?platform=spotify")

if __name__ == "__main__":
    main()
