"""
Verify AI endpoints are accessible via HTTP
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("="*80)
print("Verifying AI Endpoints Availability")
print("="*80)

# Check if server is up
print("\n1. Server status check...")
try:
    r = requests.get(f"{BASE_URL}/")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Server online: {data['message']}")
        print(f"   Version: {data['version']}")
    else:
        print(f"❌ Server returned {r.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")
    exit(1)

# Get OpenAPI schema
print("\n2. Fetching OpenAPI schema...")
try:
    r = requests.get(f"{BASE_URL}/openapi.json")
    if r.status_code == 200:
        openapi_data = r.json()
        print("✅ OpenAPI schema retrieved")
        
        # Extract all paths
        if 'paths' in openapi_data:
            all_paths = list(openapi_data['paths'].keys())
            print(f"   Total endpoints: {len(all_paths)}")
            
            # Find AI endpoints
            ai_paths = [p for p in all_paths if '/ai/' in p]
            print(f"   AI endpoints: {len(ai_paths)}")
            
            if ai_paths:
                print("\n✅ AI Endpoints registered:")
                for path in sorted(ai_paths):
                    methods = list(openapi_data['paths'][path].keys())
                    print(f"   {methods[0].upper():6} {path}")
            else:
                print("\n❌ No AI endpoints found!")
                print("   Checking all endpoints:")
                for path in sorted(all_paths):
                    print(f"   - {path}")
        else:
            print("❌ No 'paths' in OpenAPI schema")
            print(f"   Keys: {list(openapi_data.keys())}")
    else:
        print(f"❌ Cannot fetch OpenAPI: {r.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test health endpoint
print("\n3. Testing health endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/v1/health")
    if r.status_code == 200:
        print(f"✅ Health check: {r.json()}")
    else:
        print(f"⚠️  Health endpoint: {r.status_code}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test if AI endpoint exists (without auth)
print("\n4. Testing AI endpoint accessibility (no auth)...")
ai_test_endpoints = [
    "/api/v1/ai/generate-captions",
    "/api/v1/ai/generate-hashtags",
    "/api/v1/ai/generate-press-release",
    "/api/v1/ai/suggest-posting-times",
    "/api/v1/ai/generate-bio"
]

accessible = 0
for endpoint in ai_test_endpoints:
    try:
        r = requests.post(f"{BASE_URL}{endpoint}", json={})
        # We expect 401 (unauthorized) or 422 (validation error), not 404 (not found)
        if r.status_code in [401, 422]:
            print(f"✅ {endpoint} - Accessible (needs auth/data)")
            accessible += 1
        elif r.status_code == 404:
            print(f"❌ {endpoint} - Not found!")
        else:
            print(f"⚠️  {endpoint} - Status {r.status_code}")
    except Exception as e:
        print(f"❌ {endpoint} - Error: {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"✅ Server online and responding")
print(f"✅ {accessible}/5 AI endpoints are accessible")
if accessible == 5:
    print("\n🎉 All AI endpoints are properly registered and accessible!")
    print("   Ready for use once authentication is configured")
else:
    print(f"\n⚠️  {5-accessible} endpoints not accessible")
print("="*80)
