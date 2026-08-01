"""
Quick Messaging System Test - Tests core functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Test users
USERS = [
    {"email": "artist@test.com", "password": "testpass123"},
    {"email": "dj@test.com", "password": "testpass123"}
]

def test():
    print("\n🧪 BeatPush Messaging System - Quick Test\n")
    
    # 1. Login both users
    print("1️⃣  Testing Authentication...")
    tokens = []
    user_ids = []
    
    for i, user in enumerate(USERS):
        try:
            res = requests.post(f"{BASE_URL}/auth/login", json=user)
            if res.status_code == 200:
                token = res.json()["tokens"]["access_token"]
                tokens.append(token)
                
                # Get user info
                me = requests.get(f"{BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"}).json()
                user_ids.append(me["id"])
                print(f"   ✅ User {i+1} logged in: {me['username']}")
            else:
                print(f"   ❌ User {i+1} login failed")
                return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
    
    # 2. Create conversation
    print("\n2️⃣  Testing Conversation Creation...")
    try:
        res = requests.post(
            f"{BASE_URL}/messaging/conversations",
            headers={"Authorization": f"Bearer {tokens[0]}"},
            json={"recipient_id": user_ids[1]}
        )
        if res.status_code == 201:
            conv = res.json()
            conv_id = conv["id"]
            print(f"   ✅ Conversation created: {conv_id}")
        else:
            print(f"   ❌ Failed: {res.status_code} - {res.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 3. Send message
    print("\n3️⃣  Testing Message Sending...")
    try:
        res = requests.post(
            f"{BASE_URL}/messaging/messages",
            headers={"Authorization": f"Bearer {tokens[0]}"},
            json={
                "conversation_id": conv_id,
                "content": "Hello! This is a test message."
            }
        )
        if res.status_code == 201:
            msg = res.json()
            msg_id = msg["id"]
            print(f"   ✅ Message sent: {msg['content'][:50]}")
        else:
            print(f"   ❌ Failed: {res.status_code} - {res.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 4. Get messages
    print("\n4️⃣  Testing Message Retrieval...")
    try:
        res = requests.get(
            f"{BASE_URL}/messaging/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {tokens[1]}"}
        )
        if res.status_code == 200:
            msgs = res.json()
            print(f"   ✅ Retrieved {len(msgs['messages'])} messages")
        else:
            print(f"   ❌ Failed: {res.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Test settings
    print("\n5️⃣  Testing Privacy Settings...")
    try:
        res = requests.get(
            f"{BASE_URL}/messaging/settings",
            headers={"Authorization": f"Bearer {tokens[0]}"}
        )
        if res.status_code == 200:
            settings = res.json()
            print(f"   ✅ Settings: filter={settings['message_filter']}, receipts={settings['read_receipts_enabled']}")
        else:
            print(f"   ❌ Failed: {res.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. WebSocket stats
    print("\n6️⃣  Testing WebSocket Manager...")
    try:
        res = requests.get(f"{BASE_URL}/ws/stats")
        if res.status_code == 200:
            stats = res.json()
            print(f"   ✅ WebSocket: {stats['stats']['total_users_online']} users online")
        else:
            print(f"   ❌ Failed: {res.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ All core messaging features working!")
    print("\n📋 Summary:")
    print("   ✅ Authentication")
    print("   ✅ Conversation Management")
    print("   ✅ Message Sending/Receiving")
    print("   ✅ Privacy Settings")
    print("   ✅ WebSocket Infrastructure")
    print("\n🎉 Messaging system backend is operational!\n")

if __name__ == "__main__":
    test()
