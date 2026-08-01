"""Test getting tracks"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
print("🔐 Logging in...")
login = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "wizkid@beatpush.com",
    "password": "password123"
})

print(f"Login status: {login.status_code}")
print(f"Response: {login.json()}")

token = login.json()["tokens"]["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get tracks
print("\n📊 Getting tracks...")
tracks_resp = requests.get(f"{BASE_URL}/tracks/my", headers=headers)

print(f"Status: {tracks_resp.status_code}")
print(f"Response: {tracks_resp.text}")
