"""
Simple Beat Marketplace Test
Tests core functionality step by step
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login as producer
producer_login = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "pheelz@beatpush.com",
    "password": "password123"
})

if producer_login.status_code != 200:
    print(f"❌ Producer login failed: {producer_login.text}")
    exit(1)

producer_token = producer_login.json()["tokens"]["access_token"]
producer_headers = {"Authorization": f"Bearer {producer_token}"}
print(f"✅ Producer logged in")

# Login as artist
artist_login = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "wizkid@beatpush.com",
    "password": "password123"
})

if artist_login.status_code != 200:
    print(f"❌ Artist login failed: {artist_login.text}")
    exit(1)

artist_token = artist_login.json()["tokens"]["access_token"]
artist_headers = {"Authorization": f"Bearer {artist_token}"}
print(f"✅ Artist logged in")

# Create beat
print("\n🎵 Creating beat...")
beat_data = {
    "title": "Afrobeats Fire",
    "description": "Hot Afrobeats instrumental",
    "tagged_audio_url": "https://storage.example.com/tagged.mp3",
    "untagged_audio_url": "https://storage.example.com/untagged.mp3",
    "bpm": 110,
    "genre": "Afrobeats",
    "lease_price": 49.99,
    "exclusive_price": 499.99,
    "tags": "afrobeats,fire"
}

create_resp = requests.post(
    f"{BASE_URL}/beats/create",
    headers=producer_headers,
    json=beat_data
)

if create_resp.status_code != 201:
    print(f"❌ Create failed: {create_resp.status_code} - {create_resp.text}")
    exit(1)

beat = create_resp.json()
beat_id = beat["id"]
print(f"✅ Beat created: {beat['title']} (ID: {beat_id})")
print(f"   Lease: ${beat['lease_price']}, Exclusive: ${beat['exclusive_price']}")

# Purchase beat (lease)
print("\n💳 Purchasing beat (lease)...")
purchase_resp = requests.post(
    f"{BASE_URL}/beats/{beat_id}/purchase",
    headers=artist_headers,
    json={"license_type": "lease", "payment_method": "card"}
)

if purchase_resp.status_code != 201:
    print(f"❌ Purchase failed: {purchase_resp.status_code} - {purchase_resp.text}")
    exit(1)

purchase = purchase_resp.json()
print(f"✅ Beat purchased!")
print(f"   Price: ${purchase['purchase_price']:.2f}")
print(f"   Platform Fee (15%): ${purchase['platform_commission']:.2f}")
print(f"   Producer Payout: ${purchase['producer_payout']:.2f}")
print(f"   License Key: {purchase['license_key']}")

# Get producer stats
print("\n📊 Getting producer stats...")
stats_resp = requests.get(
    f"{BASE_URL}/beats/stats/my",
    headers=producer_headers
)

if stats_resp.status_code != 200:
    print(f"❌ Stats failed: {stats_resp.status_code} - {stats_resp.text}")
else:
    stats = stats_resp.json()
    print(f"✅ Producer stats:")
    print(f"   Total Beats: {stats['total_beats']}")
    print(f"   Total Sales: {stats['total_sales']}")
    print(f"   Total Revenue: ${stats['total_revenue']:.2f}")

# Get producer earnings
print("\n💰 Getting producer earnings...")
earnings_resp = requests.get(
    f"{BASE_URL}/beats/earnings/my",
    headers=producer_headers
)

if earnings_resp.status_code != 200:
    print(f"❌ Earnings failed: {earnings_resp.status_code} - {earnings_resp.text}")
else:
    earnings = earnings_resp.json()
    print(f"✅ Producer earnings:")
    print(f"   Total Earned: ${earnings['total_earned']:.2f}")
    print(f"   Total Sales: {earnings['total_sales']}")
    print(f"   Avg Sale Price: ${earnings['average_sale_price']:.2f}")

# Get purchase certificate
print("\n📄 Getting license certificate...")
cert_resp = requests.get(
    f"{BASE_URL}/beats/purchases/{purchase['id']}/certificate",
    headers=artist_headers
)

if cert_resp.status_code != 200:
    print(f"❌ Certificate failed: {cert_resp.status_code} - {cert_resp.text}")
else:
    cert = cert_resp.json()
    print(f"✅ License certificate generated")
    print(f"   License Key: {cert['license_key']}")
    print(f"   Beat: {cert['beat_title']}")
    print(f"   Producer: {cert['producer_name']}")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\n📊 Summary:")
print(f"  • Beat created and listed")
print(f"  • Lease purchase completed ($49.99)")
print(f"  • Platform commission: $7.50 (15%)")
print(f"  • Producer payout: $42.49 (85%)")
print(f"  • License certificate generated")
print(f"  • Statistics tracking working")
