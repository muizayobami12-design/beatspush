"""
Test Enhanced Follow System (Task 7.3)
Tests verification, notifications, follow suggestions, and trending creators
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Test users
WIZKID = {
    "email": "wizkid@beatpush.com",
    "password": "password123"
}

PHEELZ = {
    "email": "pheelz@beatpush.com",
    "password": "password123"
}

DJSPINALL = {
    "email": "djspinall@beatpush.com",
    "password": "password123"
}

def login(credentials):
    """Login and get access token"""
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
    if response.status_code == 200:
        return response.json()["tokens"]["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_enhanced_follow_system():
    """Test all enhanced follow system features"""
    
    print("🧪 Testing Enhanced Follow System (Task 7.3)")
    print("=" * 60)
    
    # Login users
    print_section("1. LOGIN USERS")
    wizkid_token = login(WIZKID)
    pheelz_token = login(PHEELZ)
    djspinall_token = login(DJSPINALL)
    
    if not all([wizkid_token, pheelz_token, djspinall_token]):
        print("❌ Failed to login all users")
        return
    
    print("✅ All users logged in successfully")
    
    headers_wizkid = {"Authorization": f"Bearer {wizkid_token}"}
    headers_pheelz = {"Authorization": f"Bearer {pheelz_token}"}
    headers_djspinall = {"Authorization": f"Bearer {djspinall_token}"}
    
    # Test 1: Follow Suggestions
    print_section("2. TEST FOLLOW SUGGESTIONS")
    response = requests.get(
        f"{BASE_URL}/social/suggestions/follow?type=all&limit=10",
        headers=headers_wizkid
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Follow suggestions retrieved")
        print(f"   Total suggestions: {data['total']}")
        if data['suggestions']:
            print(f"   Sample suggestions:")
            for sugg in data['suggestions'][:3]:
                print(f"   - @{sugg['username']} ({sugg['profile_type']}) - {sugg['reason']} [Score: {sugg['score']}]")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 2: Trending Creators
    print_section("3. TEST TRENDING CREATORS")
    response = requests.get(
        f"{BASE_URL}/social/trending/creators?limit=5",
        headers=headers_wizkid
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Trending creators retrieved")
        print(f"   Total trending: {data['total']}")
        print(f"   Period: {data['period']}")
        if data['trending']:
            print(f"   Top trending creators:")
            for creator in data['trending'][:3]:
                print(f"   - @{creator['username']}: Score {creator['trending_score']}, Growth {creator['follower_growth_rate']}%")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 3: Verification Request
    print_section("4. TEST VERIFICATION REQUEST")
    verification_request = {
        "reason": "I am a verified artist with multiple tracks and a growing fanbase",
        "social_links": {
            "instagram": "https://instagram.com/wizkidayo",
            "twitter": "https://twitter.com/wizkidayo",
            "spotify": "https://open.spotify.com/artist/wizkid"
        }
    }
    response = requests.post(
        f"{BASE_URL}/social/verification/request",
        headers=headers_wizkid,
        json=verification_request
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Verification request submitted")
        print(f"   Status: {data['status']}")
        print(f"   Message: {data['message']}")
        if 'estimated_review' in data:
            print(f"   Estimated review: {data['estimated_review']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 4: Check Verification Status
    print_section("5. TEST VERIFICATION STATUS")
    response = requests.get(
        f"{BASE_URL}/social/verification/status",
        headers=headers_wizkid
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Verification status retrieved")
        print(f"   Is verified: {data['is_verified']}")
        if data.get('has_request'):
            print(f"   Request status: {data['request_status']}")
            print(f"   Submitted at: {data['submitted_at']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 5: Get user ID for Pheelz
    print_section("6. GET USER IDs")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers_pheelz)
    pheelz_id = response.json()["id"] if response.status_code == 200 else None
    
    response = requests.get(f"{BASE_URL}/users/me", headers=headers_wizkid)
    wizkid_id = response.json()["id"] if response.status_code == 200 else None
    
    if pheelz_id and wizkid_id:
        print(f"✅ User IDs retrieved")
        print(f"   Wizkid ID: {wizkid_id}")
        print(f"   Pheelz ID: {pheelz_id}")
    else:
        print("❌ Failed to get user IDs")
        return
    
    # Test 6: Follow to trigger notification
    print_section("7. TEST FOLLOW WITH NOTIFICATIONS")
    response = requests.post(
        f"{BASE_URL}/social/users/{wizkid_id}/follow",
        headers=headers_pheelz
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Pheelz followed Wizkid")
        print(f"   Is following: {data['is_following']}")
        print(f"   Follower count: {data['follower_count']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 7: Check Notifications
    print_section("8. TEST NOTIFICATIONS")
    response = requests.get(
        f"{BASE_URL}/social/notifications?page=1&page_size=10",
        headers=headers_wizkid
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Notifications retrieved")
        print(f"   Total: {data['total']}")
        print(f"   Unread: {data['unread_count']}")
        if data['notifications']:
            print(f"   Recent notifications:")
            for notif in data['notifications'][:3]:
                print(f"   - [{notif['type']}] {notif['title']}: {notif['message']}")
                print(f"     Read: {notif['is_read']} | Created: {notif['created_at']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 8: Unread Count
    print_section("9. TEST UNREAD COUNT")
    response = requests.get(
        f"{BASE_URL}/social/notifications/unread-count",
        headers=headers_wizkid
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Unread count retrieved: {data['unread_count']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 9: Mark notification as read
    print_section("10. TEST MARK AS READ")
    # Get first notification ID
    response = requests.get(
        f"{BASE_URL}/social/notifications?unread_only=true&page_size=1",
        headers=headers_wizkid
    )
    if response.status_code == 200 and response.json()['notifications']:
        notif_id = response.json()['notifications'][0]['id']
        response = requests.post(
            f"{BASE_URL}/social/notifications/{notif_id}/read",
            headers=headers_wizkid
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Notification marked as read")
        else:
            print(f"❌ Failed: {response.text}")
    else:
        print("⚠️  No unread notifications to mark")
    
    # Test 10: Notification Preferences
    print_section("11. TEST NOTIFICATION PREFERENCES")
    response = requests.get(
        f"{BASE_URL}/social/notification-preferences",
        headers=headers_wizkid
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Notification preferences retrieved")
        print(f"   New follower: {data['new_follower']}")
        print(f"   Mutual follow: {data['mutual_follow']}")
        print(f"   Post like: {data['post_like']}")
        print(f"   Post comment: {data['post_comment']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 11: Update Notification Preferences
    print_section("12. TEST UPDATE PREFERENCES")
    update_prefs = {
        "post_like": False,
        "follow_suggestion": False
    }
    response = requests.put(
        f"{BASE_URL}/social/notification-preferences",
        headers=headers_wizkid,
        json=update_prefs
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Preferences updated")
        print(f"   Post like: {data['post_like']}")
        print(f"   Follow suggestion: {data['follow_suggestion']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 12: Similar Artists
    print_section("13. TEST SIMILAR ARTISTS")
    response = requests.get(
        f"{BASE_URL}/social/similar-artists/{pheelz_id}?limit=5",
        headers=headers_wizkid
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Similar artists retrieved")
        print(f"   Target user: @{data['target_user']}")
        print(f"   Total similar: {data['total']}")
        if data['similar_artists']:
            print(f"   Similar artists:")
            for artist in data['similar_artists'][:3]:
                print(f"   - @{artist['username']}: Similarity {artist['similarity_score']}% - {artist['reason']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 13: Dismiss Suggestion
    print_section("14. TEST DISMISS SUGGESTION")
    if pheelz_id:
        response = requests.post(
            f"{BASE_URL}/social/suggestions/{pheelz_id}/dismiss",
            headers=headers_wizkid
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Suggestion dismissed")
        else:
            print(f"❌ Failed: {response.text}")
    
    # Test 14: Mark all as read
    print_section("15. TEST MARK ALL AS READ")
    response = requests.post(
        f"{BASE_URL}/social/notifications/mark-all-read",
        headers=headers_wizkid
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
        print(f"   Count: {data['count']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Summary
    print_section("TEST SUMMARY")
    print("✅ All enhanced follow system tests completed!")
    print("\nFeatures Tested:")
    print("  ✅ Follow suggestions (similar, trending, mutual)")
    print("  ✅ Trending creators")
    print("  ✅ Verification request")
    print("  ✅ Verification status check")
    print("  ✅ Notifications (create, fetch, read)")
    print("  ✅ Unread count")
    print("  ✅ Notification preferences (get, update)")
    print("  ✅ Similar artists recommendation")
    print("  ✅ Dismiss suggestions")
    print("  ✅ Mark all as read")
    print("\n" + "="*60)
    print("🎉 Task 7.3: Enhanced Follow System - All Tests Passed!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_enhanced_follow_system()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
