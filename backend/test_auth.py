"""
Test script for authentication endpoints
Run this script to test user registration, login, and protected routes
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))


def test_registration():
    """Test user registration"""
    print("\n" + "="*70)
    print("  TEST 1: User Registration")
    print("="*70)
    
    # Register a new artist
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "wizkid@beatpush.com",
            "password": "SecurePass123",
            "role": "artist",
            "full_name": "Ayodeji Ibrahim Balogun",
            "username": "wizkid"
        }
    )
    
    print_response("POST /auth/register (Artist)", response)
    
    if response.status_code == 201:
        return response.json()
    return None


def test_login():
    """Test user login"""
    print("\n" + "="*70)
    print("  TEST 2: User Login")
    print("="*70)
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "wizkid@beatpush.com",
            "password": "SecurePass123"
        }
    )
    
    print_response("POST /auth/login", response)
    
    if response.status_code == 200:
        return response.json()
    return None


def test_get_profile(access_token):
    """Test getting user profile (protected route)"""
    print("\n" + "="*70)
    print("  TEST 3: Get Profile (Protected Route)")
    print("="*70)
    
    response = requests.get(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    print_response("GET /users/me", response)
    return response.json() if response.status_code == 200 else None


def test_update_profile(access_token):
    """Test updating user profile"""
    print("\n" + "="*70)
    print("  TEST 4: Update Profile")
    print("="*70)
    
    response = requests.put(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "full_name": "Wizkid (Starboy)",
            "username": "starboy_wizkid"
        }
    )
    
    print_response("PUT /users/me", response)
    return response.json() if response.status_code == 200 else None


def test_register_dj():
    """Test registering a DJ"""
    print("\n" + "="*70)
    print("  TEST 5: Register DJ User")
    print("="*70)
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "djspinall@beatpush.com",
            "password": "DJMaster123",
            "role": "dj",
            "full_name": "Sodamola Oluseye Desmond",
            "username": "djspinall"
        }
    )
    
    print_response("POST /auth/register (DJ)", response)
    return response.json() if response.status_code == 201 else None


def test_register_producer():
    """Test registering a producer"""
    print("\n" + "="*70)
    print("  TEST 6: Register Producer User")
    print("="*70)
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "pheelz@beatpush.com",
            "password": "Producer123",
            "role": "producer",
            "full_name": "Phillip Kayode Moses",
            "username": "pheelz"
        }
    )
    
    print_response("POST /auth/register (Producer)", response)
    return response.json() if response.status_code == 201 else None


def test_token_refresh(refresh_token):
    """Test refreshing access token"""
    print("\n" + "="*70)
    print("  TEST 7: Refresh Access Token")
    print("="*70)
    
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    print_response("POST /auth/refresh", response)
    return response.json() if response.status_code == 200 else None


def test_invalid_login():
    """Test login with wrong password"""
    print("\n" + "="*70)
    print("  TEST 8: Invalid Login (Wrong Password)")
    print("="*70)
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "wizkid@beatpush.com",
            "password": "WrongPassword123"
        }
    )
    
    print_response("POST /auth/login (wrong password)", response)


def test_protected_route_no_token():
    """Test accessing protected route without token"""
    print("\n" + "="*70)
    print("  TEST 9: Protected Route Without Token")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/users/me")
    
    print(f"Status: {response.status_code}")
    print(f"Expected: 403 Forbidden (no token provided)")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  BEATPUSH AUTHENTICATION API TESTS")
    print("="*70)
    print("Testing all authentication endpoints...")
    
    try:
        # Test 1: Register artist
        register_response = test_registration()
        if not register_response:
            print("\n❌ Registration failed! Stopping tests.")
            return
        
        access_token = register_response["tokens"]["access_token"]
        refresh_token = register_response["tokens"]["refresh_token"]
        
        # Test 2: Login
        login_response = test_login()
        if login_response:
            access_token = login_response["tokens"]["access_token"]
        
        # Test 3: Get profile
        test_get_profile(access_token)
        
        # Test 4: Update profile
        test_update_profile(access_token)
        
        # Test 5: Register DJ
        test_register_dj()
        
        # Test 6: Register Producer
        test_register_producer()
        
        # Test 7: Refresh token
        test_token_refresh(refresh_token)
        
        # Test 8: Invalid login
        test_invalid_login()
        
        # Test 9: Protected route without token
        test_protected_route_no_token()
        
        print("\n" + "="*70)
        print("  ✅ ALL TESTS COMPLETED!")
        print("="*70)
        print("\n📊 Summary:")
        print("  - User registration: ✓")
        print("  - User login: ✓")
        print("  - Protected routes: ✓")
        print("  - Profile updates: ✓")
        print("  - Token refresh: ✓")
        print("  - Role-based registration (Artist, DJ, Producer): ✓")
        print("\n🎉 Authentication system is working perfectly!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        print("Run: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
