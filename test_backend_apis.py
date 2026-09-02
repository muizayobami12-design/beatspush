#!/usr/bin/env python3
"""
BeatPush Backend API Test Script
Tests all critical endpoints to verify they're working
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:9000/api/v1"
TEST_USER_EMAIL = f"test_{datetime.now().timestamp()}@beatpush.com"
TEST_USER_PASSWORD = "Test1234!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}🧪 Testing: {name}{Colors.END}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

class BeatPushAPITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.test_post_id = None
        self.test_beat_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
    
    def test_health_check(self):
        """Test if backend is running"""
        print_test("Backend Health Check")
        try:
            response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
            if response.status_code == 200:
                print_success("Backend is running!")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Backend returned {response.status_code}")
                self.results["failed"] += 1
                return False
        except requests.exceptions.ConnectionError:
            print_error("Cannot connect to backend. Is it running on port 9000?")
            self.results["failed"] += 1
            return False
        except Exception as e:
            print_error(f"Health check failed: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        print_test("User Registration")
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": "Test User",
                "username": f"testuser{int(datetime.now().timestamp())}",
                "role": "artist"
            }
            
            response = requests.post(f"{BASE_URL}/auth/register", json=payload)
            
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("user", {}).get("id")
                self.token = data.get("access_token")
                print_success(f"User registered successfully! ID: {self.user_id}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Registration failed: {response.status_code} - {response.text}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Registration error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_user_login(self):
        """Test user login"""
        print_test("User Login")
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = requests.post(f"{BASE_URL}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print_success("Login successful! Token received.")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Login failed: {response.status_code} - {response.text}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Login error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_get_current_user(self):
        """Test getting current user info"""
        print_test("Get Current User")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"User info retrieved: {data.get('full_name')}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Get user failed: {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Get user error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_browse_beats(self):
        """Test browsing beats"""
        print_test("Browse Beats")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{BASE_URL}/beats/browse?page=1&page_size=10",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                beat_count = len(data.get("beats", []))
                print_success(f"Beats retrieved: {beat_count} beats found")
                self.results["passed"] += 1
                
                # Store first beat ID for later tests
                if beat_count > 0:
                    self.test_beat_id = data["beats"][0]["id"]
                
                return True
            else:
                print_error(f"Browse beats failed: {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Browse beats error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_get_profile(self):
        """Test getting user profile"""
        print_test("Get User Profile")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/profiles/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Profile retrieved: {data.get('user', {}).get('full_name')}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Get profile failed: {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Get profile error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_create_post(self):
        """Test creating a social post"""
        print_test("Create Social Post")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "post_type": "text",  # Changed from "status" to match enum
                "content": "Testing BeatPush social feed! 🎵",
                "visibility": "public"
            }
            
            response = requests.post(
                f"{BASE_URL}/social/posts",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                data = response.json()
                self.test_post_id = data.get("id")
                print_success(f"Post created successfully! ID: {self.test_post_id}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Create post failed: {response.status_code} - {response.text}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Create post error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_get_feed(self):
        """Test getting social feed"""
        print_test("Get Social Feed")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{BASE_URL}/social/feed?feed_type=following&page=1&page_size=20",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                post_count = len(data.get("posts", []))
                print_success(f"Feed retrieved: {post_count} posts")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Get feed failed: {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Get feed error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_like_post(self):
        """Test liking a post"""
        print_test("Like Post")
        if not self.test_post_id:
            print_warning("No post ID available, skipping")
            self.results["warnings"] += 1
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{BASE_URL}/social/posts/{self.test_post_id}/like",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                is_liked = data.get("is_liked", False)
                print_success(f"Post {'liked' if is_liked else 'unliked'} successfully!")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Like post failed: {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Like post error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_comment_on_post(self):
        """Test commenting on a post"""
        print_test("Comment on Post")
        if not self.test_post_id:
            print_warning("No post ID available, skipping")
            self.results["warnings"] += 1
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "content": "Great post! Testing comments feature 🎉"
            }
            
            response = requests.post(
                f"{BASE_URL}/social/posts/{self.test_post_id}/comments",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                data = response.json()
                print_success(f"Comment created! ID: {data.get('id')}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Comment failed: {response.status_code} - {response.text}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Comment error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def test_get_campaigns(self):
        """Test getting campaigns"""
        print_test("Get Campaigns")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/campaigns", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                campaign_count = len(data) if isinstance(data, list) else 0
                print_success(f"Campaigns retrieved: {campaign_count} campaigns")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Get campaigns failed: {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Get campaigns error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print(f"{Colors.BLUE}📊 TEST SUMMARY{Colors.END}")
        print("="*60)
        
        total = self.results["passed"] + self.results["failed"] + self.results["warnings"]
        
        print(f"{Colors.GREEN}✅ Passed:  {self.results['passed']}/{total}{Colors.END}")
        print(f"{Colors.RED}❌ Failed:  {self.results['failed']}/{total}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {self.results['warnings']}/{total}{Colors.END}")
        
        success_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if self.results["failed"] == 0:
            print(f"\n{Colors.GREEN}🎉 All tests passed! Backend is ready for testing.{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Check errors above.{Colors.END}")
        
        print("="*60 + "\n")

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}🚀 BeatPush Backend API Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Backend URL: {BASE_URL}")
    print(f"Test User: {TEST_USER_EMAIL}")
    print()
    
    tester = BeatPushAPITester()
    
    # Run tests in order
    if not tester.test_health_check():
        print_error("Backend is not running. Please start it with: cd backend && python main.py")
        return
    
    # Authentication tests
    tester.test_user_registration()
    tester.test_user_login()
    tester.test_get_current_user()
    
    # Feature tests
    tester.test_get_profile()
    tester.test_browse_beats()
    tester.test_create_post()
    tester.test_get_feed()
    tester.test_like_post()
    tester.test_comment_on_post()
    tester.test_get_campaigns()
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Tests interrupted by user{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test suite error: {str(e)}{Colors.END}\n")
