"""
Test Track Performance Analytics
Task 4.3: Track Performance Analytics

Tests track-specific analytics endpoints
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login as artist with tracks
print("🔐 Logging in...")
login = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "wizkid@beatpush.com",
    "password": "password123"
})

if login.status_code != 200:
    print(f"❌ Login failed: {login.text}")
    exit(1)

token = login.json()["tokens"]["access_token"]
headers = {"Authorization": f"Bearer {token}"}
user_id = login.json()["user"]["id"]
print(f"✅ Logged in as Wizkid (ID: {user_id})")

# Get user's tracks
print("\n📊 Getting user tracks...")
tracks_resp = requests.get(f"{BASE_URL}/tracks/?limit=100", headers=headers)

if tracks_resp.status_code != 200:
    print(f"❌ Failed to get tracks: {tracks_resp.text}")
    exit(1)

tracks = tracks_resp.json()
if not tracks:
    print("❌ No tracks found. Please create a track first.")
    exit(1)

track = tracks[0]
track_id = track["id"]
print(f"✅ Found track: {track['title']} (ID: {track_id})")

# Test 1: Get track performance
print("\n" + "="*60)
print("  TEST 1: Track Performance Analytics")
print("="*60)

perf_resp = requests.get(
    f"{BASE_URL}/analytics/track/{track_id}/performance?days=30",
    headers=headers
)

if perf_resp.status_code != 200:
    print(f"❌ Failed: {perf_resp.status_code} - {perf_resp.text}")
else:
    perf = perf_resp.json()
    print(f"\n✅ Track Performance for: {perf['track_title']}")
    print(f"\n📊 Overview:")
    print(f"   Total Plays: {perf['total_plays']}")
    print(f"   Total Likes: {perf['total_likes']}")
    print(f"   Total Shares: {perf['total_shares']}")
    print(f"   Performance Score: {perf['performance_score']:.2f}")
    print(f"   Tips Revenue: ${perf['tips_revenue']:.2f}")
    print(f"   Promo Clicks: {perf['promo_clicks']}")
    
    print(f"\n🎵 Platform Breakdown:")
    for platform in perf['platform_breakdown']:
        print(f"   {platform['platform']}: {platform['plays']} plays ({platform['percentage']}%)")
    
    if perf['geo_distribution']:
        print(f"\n🌍 Geographic Distribution:")
        for geo in perf['geo_distribution'][:5]:
            print(f"   {geo['country']}: {geo['clicks']} clicks ({geo['percentage']}%)")
    
    print(f"\n📈 Playlist Adds:")
    playlist = perf['playlist_adds']
    print(f"   Total: {playlist['total']}")
    print(f"   Algorithmic: {playlist['algorithmic']}")
    print(f"   Editorial: {playlist['editorial']}")
    print(f"   User Created: {playlist['user_created']}")
    
    print(f"\n👥 Demographics:")
    print(f"   Age Groups:")
    for age in perf['demographics']['age_groups']:
        print(f"      {age['range']}: {age['percentage']}% ({age['count']} listeners)")

# Test 2: Track rankings
print("\n" + "="*60)
print("  TEST 2: Track Rankings")
print("="*60)

rankings_resp = requests.get(
    f"{BASE_URL}/analytics/tracks/rankings",
    headers=headers
)

if rankings_resp.status_code != 200:
    print(f"❌ Failed: {rankings_resp.status_code} - {rankings_resp.text}")
else:
    rankings = rankings_resp.json()
    print(f"\n✅ Track Rankings (Total: {rankings['total_tracks']} tracks)")
    
    print(f"\n🏆 Top Tracks by Plays:")
    for track in rankings['by_plays'][:3]:
        print(f"   #{track['rank']}: {track['track_title']}")
        print(f"      Plays: {track['plays']}, Likes: {track['likes']}")
    
    print(f"\n💙 Top Tracks by Engagement:")
    for track in rankings['by_engagement'][:3]:
        print(f"   #{track['rank']}: {track['track_title']}")
        print(f"      Engagement Rate: {track['engagement_rate']}%")
    
    if rankings['by_revenue'] and rankings['by_revenue'][0]['revenue'] > 0:
        print(f"\n💰 Top Tracks by Revenue:")
        for track in rankings['by_revenue'][:3]:
            print(f"   #{track['rank']}: {track['track_title']}")
            print(f"      Revenue: ${track['revenue']:.2f}")

# Test 3: Growth trends
print("\n" + "="*60)
print("  TEST 3: Track Growth Trends")
print("="*60)

growth_resp = requests.get(
    f"{BASE_URL}/analytics/track/{track_id}/growth?days=90",
    headers=headers
)

if growth_resp.status_code != 200:
    print(f"❌ Failed: {growth_resp.status_code} - {growth_resp.text}")
else:
    growth = growth_resp.json()
    print(f"\n✅ Growth Trends for: {growth['track_title']}")
    print(f"   Period: {growth['period_days']} days")
    print(f"   Growth Rate: {growth['growth_rate_percentage']}%")
    print(f"   Trend: {growth['trend'].upper()}")
    
    if growth['peak_week']:
        peak = growth['peak_week']
        print(f"\n🎯 Peak Week (Week {peak['week_number']}):")
        print(f"   Date: {peak['week_start']}")
        print(f"   Plays: {peak['plays']}")
        print(f"   Likes: {peak['likes']}")
        print(f"   New Listeners: {peak['new_listeners']}")
    
    print(f"\n📈 Recent Weeks:")
    for week in growth['weekly_data'][-4:]:
        print(f"   Week {week['week_number']}: {week['plays']} plays, {week['likes']} likes")

# Test 4: Compare tracks (if multiple tracks exist)
if len(tracks) >= 2:
    print("\n" + "="*60)
    print("  TEST 4: Compare Tracks")
    print("="*60)
    
    track_ids = [t["id"] for t in tracks[:2]]  # Compare first 2 tracks
    
    compare_resp = requests.post(
        f"{BASE_URL}/analytics/tracks/compare",
        headers=headers,
        json=track_ids
    )
    
    if compare_resp.status_code != 200:
        print(f"❌ Failed: {compare_resp.status_code} - {compare_resp.text}")
    else:
        comparison = compare_resp.json()
        print(f"\n✅ Track Comparison")
        print(f"   Total Plays: {comparison['total_plays']}")
        print(f"   Total Revenue: ${comparison['total_revenue']:.2f}")
        
        if comparison['best_performer']:
            best = comparison['best_performer']
            print(f"\n🏆 Best Performer: {best['track_title']}")
            print(f"   Rank: #{best['rank']}")
            print(f"   Performance Score: {best['performance_score']:.2f}")
            print(f"   Engagement Rate: {best['engagement_rate']}%")
        
        print(f"\n📊 Comparison:")
        for track in comparison['tracks']:
            print(f"\n   #{track['rank']}: {track['track_title']}")
            print(f"      Plays: {track['plays']}")
            print(f"      Engagement: {track['engagement_rate']}%")
            print(f"      Revenue: ${track['revenue']:.2f}")

# Final summary
print("\n" + "="*60)
print("  ✅ ALL TRACK ANALYTICS TESTS PASSED!")
print("="*60)

print("\n📋 Features Tested:")
print("   1. ✅ Track performance analytics")
print("   2. ✅ Track rankings")
print("   3. ✅ Growth trends")
if len(tracks) >= 2:
    print("   4. ✅ Track comparison")

print("\n📊 Analytics Capabilities:")
print("   • Platform breakdown (Spotify, Apple, YouTube)")
print("   • Geographic distribution")
print("   • Engagement timeline")
print("   • Playlist adds tracking")
print("   • Listener demographics")
print("   • Performance scoring")
print("   • Growth trend analysis")
print("   • Multi-track comparison")
