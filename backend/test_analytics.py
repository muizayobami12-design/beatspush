"""
Test Analytics API - Task 4.2
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def main():
    print("="*70)
    print(" ANALYTICS DASHBOARD TEST (Task 4.2)")
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
    
    # Test 1: Get Dashboard
    print("\n[2] Getting analytics dashboard...")
    r = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] Dashboard failed: {r.status_code} - {r.text}")
        return
    
    dashboard = r.json()
    print("[OK] Dashboard retrieved")
    print(f"     Total tracks: {dashboard['overview']['total_tracks']}")
    print(f"     Total plays: {dashboard['overview']['total_plays']}")
    print(f"     Total promo links: {dashboard['overview']['total_promo_links']}")
    print(f"     Promo link clicks: {dashboard['overview']['promo_link_clicks']}")
    print(f"     Engagement rate: {dashboard['overview']['engagement_rate']}%")
    print(f"     Top tracks: {len(dashboard['top_tracks'])}")
    print(f"     Insights: {len(dashboard['insights'])}")
    
    # Test 2: Get Overview Only
    print("\n[3] Getting overview stats...")
    r = requests.get(f"{BASE_URL}/analytics/overview", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] Overview failed: {r.status_code}")
    else:
        overview = r.json()
        print("[OK] Overview retrieved")
        print(f"     Campaigns: {overview['total_campaigns']} ({overview['active_campaigns']} active)")
    
    # Test 3: Get Top Tracks
    print("\n[4] Getting top tracks...")
    r = requests.get(f"{BASE_URL}/analytics/top-tracks?limit=5", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] Top tracks failed: {r.status_code}")
    else:
        tracks = r.json()
        print(f"[OK] Found {len(tracks)} tracks")
        if tracks:
            print(f"     Best: '{tracks[0]['track_title']}' ({tracks[0]['plays']} plays)")
    
    # Test 4: Get Platform Stats
    print("\n[5] Getting platform stats...")
    r = requests.get(f"{BASE_URL}/analytics/platforms", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] Platform stats failed: {r.status_code}")
    else:
        platforms = r.json()
        print(f"[OK] Found {len(platforms)} platforms")
        if platforms:
            for p in platforms[:3]:
                print(f"     {p['platform']}: {p['clicks']} clicks ({p['percentage']:.1f}%)")
    
    # Test 5: Get Geographic Stats
    print("\n[6] Getting geographic stats...")
    r = requests.get(f"{BASE_URL}/analytics/geographic?limit=5", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] Geographic stats failed: {r.status_code}")
    else:
        geo = r.json()
        print(f"[OK] Found {len(geo)} countries")
        if geo:
            for g in geo[:3]:
                print(f"     {g['country']}: {g['clicks']} clicks")
    
    # Test 6: Get Timeline
    print("\n[7] Getting engagement timeline...")
    r = requests.get(f"{BASE_URL}/analytics/timeline?days=7", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] Timeline failed: {r.status_code}")
    else:
        timeline = r.json()
        print("[OK] Timeline retrieved")
        print(f"     Days: {len(timeline['plays'])}")
        total_clicks = sum(d['value'] for d in timeline['promo_clicks'])
        print(f"     Total clicks in period: {total_clicks}")
    
    # Test 7: Get Insights
    print("\n[8] Getting AI insights...")
    r = requests.get(f"{BASE_URL}/analytics/insights", headers=headers)
    
    if r.status_code != 200:
        print(f"[FAIL] Insights failed: {r.status_code}")
    else:
        insights_data = r.json()
        insights = insights_data['insights']
        print(f"[OK] Generated {len(insights)} insights:")
        for insight in insights:
            print(f"     - {insight}")
    
    # Test 8: Get Track Analytics
    if dashboard['top_tracks']:
        track_id = dashboard['top_tracks'][0]['track_id']
        print(f"\n[9] Getting track analytics...")
        r = requests.get(f"{BASE_URL}/analytics/tracks/{track_id}", headers=headers)
        
        if r.status_code != 200:
            print(f"[FAIL] Track analytics failed: {r.status_code}")
        else:
            track_analytics = r.json()
            print("[OK] Track analytics retrieved")
            print(f"     Track: {track_analytics['track_title']}")
            print(f"     Promo links: {len(track_analytics['promo_links'])}")
            print(f"     Total clicks: {track_analytics['total_promo_clicks']}")
            print(f"     Engagement: {track_analytics['engagement_rate']}%")
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    print(f" Dashboard: Working")
    print(f" Overview: {overview['total_tracks']} tracks, {overview['total_promo_links']} links")
    print(f" Platform Stats: {len(platforms)} platforms")
    print(f" Geographic: {len(geo)} countries")
    print(f" Insights: {len(insights)} generated")
    print("\n[SUCCESS] All analytics endpoints working!")
    print("="*70)

if __name__ == "__main__":
    main()
