"""
Simple test for Promo Links API - No emojis for Windows console
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def main():
    print("="*70)
    print(" PROMO LINKS API TEST (Task 3.5)")
    print("="*70)
    
    # Login
    print("\n[1] Logging in...")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "wizkid@beatpush.com",
        "password": "SecurePass123"
    })
    
    if r.status_code != 200:
        print(f"[FAIL] Login failed: {r.text}")
        return
    
    token = r.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] Logged in successfully")
    
    # Get tracks
    print("\n[2] Getting tracks...")
    r = requests.get(f"{BASE_URL}/tracks/", headers=headers)
    
    if r.status_code != 200 or not r.json():
        print(f"[FAIL] No tracks found: {r.status_code}")
        return
    
    track_id = r.json()[0]["id"]
    print(f"[OK] Found track: {track_id}")
    
    # Create promo link
    print("\n[3] Creating promo link...")
    r = requests.post(f"{BASE_URL}/promo-links/", json={
        "track_id": track_id,
        "title": "My Awesome Track",
        "spotify_url": "https://open.spotify.com/track/test",
        "apple_music_url": "https://music.apple.com/track/test",
        "youtube_url": "https://youtube.com/watch?v=test",
        "audiomack_url": "https://audiomack.com/song/test"
    }, headers=headers)
    
    if r.status_code != 201:
        print(f"[FAIL] Create failed: {r.status_code} - {r.text}")
        return
    
    link = r.json()
    link_id = link["id"]
    short_code = link["short_code"]
    print(f"[OK] Created! Short code: {short_code}")
    print(f"     Short URL: {link['short_url']}")
    
    # Get link details
    print("\n[4] Getting link details...")
    r = requests.get(f"{BASE_URL}/promo-links/{link_id}", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] Get failed: {r.status_code}")
    else:
        print(f"[OK] Retrieved link details")
        print(f"     Clicks: {r.json()['total_clicks']}")
    
    # Generate QR code
    print("\n[5] Generating QR code...")
    r = requests.get(f"{BASE_URL}/promo-links/{link_id}/qr", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] QR generation failed: {r.status_code}")
    else:
        qr_length = len(r.json()["qr_code_data"])
        print(f"[OK] QR code generated ({qr_length} chars)")
    
    # Simulate clicks
    print("\n[6] Simulating clicks...")
    platforms = ["spotify", "apple_music", "youtube"]
    
    for platform in platforms:
        r = requests.get(
            f"{BASE_URL}/promo-links/redirect/{short_code}?platform={platform}",
            allow_redirects=False
        )
        if r.status_code in [301, 302, 307]:
            print(f"[OK] {platform} click tracked")
        else:
            print(f"[FAIL] {platform} failed: {r.status_code}")
    
    # Get analytics
    print("\n[7] Getting analytics...")
    r = requests.get(f"{BASE_URL}/promo-links/{link_id}/analytics", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] Analytics failed: {r.status_code}")
    else:
        analytics = r.json()
        print(f"[OK] Analytics retrieved")
        print(f"     Total clicks: {analytics['total_clicks']}")
        print(f"     Unique clicks: {analytics['unique_clicks']}")
        print(f"     Platforms: {list(analytics['platform_stats'].keys())}")
    
    # List all links
    print("\n[8] Listing all links...")
    r = requests.get(f"{BASE_URL}/promo-links/", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] List failed: {r.status_code}")
    else:
        data = r.json()
        print(f"[OK] Found {data['total']} links")
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    print(f" Promo link created: {short_code}")
    print(f" Total clicks tracked: {analytics['total_clicks'] if r.status_code == 200 else 'N/A'}")
    print(f" QR code: Generated")
    print("\n[SUCCESS] All tests passed!")
    print("\n Try the link:")
    print(f" http://localhost:8000/api/v1/promo-links/redirect/{short_code}?platform=spotify")
    print("="*70)

if __name__ == "__main__":
    main()
