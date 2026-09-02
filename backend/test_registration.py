"""
Test Registration Script
Simulates registration to see exact error
"""
import requests
import json

BASE_URL = "http://localhost:9000/api/v1"

print("=" * 60)
print("🧪 TESTING REGISTRATION")
print("=" * 60)

# Test data
test_user = {
    "email": "test@example.com",
    "password": "Password123!",
    "name": "Test User",
    "role": "artist",
    "turnstile_token": "test-token-bypass",  # For development
    "device_id": "test-device-123"
}

print(f"\n📝 Registration data:")
print(f"   Email: {test_user['email']}")
print(f"   Name: {test_user['name']}")
print(f"   Role: {test_user['role']}")

print(f"\n🚀 Sending registration request...")

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=test_user,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"\n📄 Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 201:
        print("\n✅ Registration successful!")
    else:
        print(f"\n❌ Registration failed!")
        print(f"   Error: {response.json().get('detail', 'Unknown error')}")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print(f"   Make sure backend is running on port 9000")

print("\n" + "=" * 60)
