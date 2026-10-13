#!/usr/bin/env python3
"""
Test script for API integration debugging
"""

import requests
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    """Test the API endpoints for debugging"""
    
    base_url = "http://localhost:5000"
    
    print("Testing API Integration Endpoints")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Test user registration (for getting a token)
    print("\n2. Testing user registration...")
    test_user = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=test_user)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Test user login
    print("\n3. Testing user login...")
    login_data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    token = None
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if result.get("success") and result.get("token"):
            token = result["token"]
            print(f"   Token obtained: {token[:20]}...")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    if not token:
        print("Cannot proceed without token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 4: Test profile update
    print("\n4. Testing profile links update...")
    profile_data = {
        "leetcode": "testuser123",
        "hackerrank": "testuser456"
    }
    
    try:
        response = requests.post(f"{base_url}/api/profile/update_links", 
                               json=profile_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Test progress fetching
    print("\n5. Testing progress fetching...")
    try:
        response = requests.get(f"{base_url}/api/profile/progress", headers=headers)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Test LeetCode API directly
    print("\n6. Testing LeetCode API directly...")
    try:
        response = requests.get(f"{base_url}/api/integrations/leetcode?username=testuser123", 
                               headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 7: Test HackerRank API directly
    print("\n7. Testing HackerRank API directly...")
    try:
        response = requests.get(f"{base_url}/api/integrations/hackerrank?username=testuser456", 
                               headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 8: Test sync progress
    print("\n8. Testing progress sync...")
    try:
        response = requests.post(f"{base_url}/api/profile/sync-progress", 
                                json={}, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("API Integration Test Complete")

def test_coding_tracker():
    """Test the coding tracker directly"""
    print("\nTesting Coding Tracker Directly")
    print("=" * 50)
    
    try:
        from coding_platforms import CodingPlatformTracker
        
        tracker = CodingPlatformTracker()
        
        # Test LeetCode
        print("\n1. Testing LeetCode tracker...")
        result = tracker.get_leetcode_stats("testuser")
        print(f"   Result: {result}")
        
        # Test HackerRank
        print("\n2. Testing HackerRank tracker...")
        result = tracker.get_hackerrank_stats("testuser")
        print(f"   Result: {result}")
        
        # Test Enhanced LeetCode
        print("\n3. Testing Enhanced LeetCode tracker...")
        result = tracker.get_enhanced_leetcode_stats("testuser")
        print(f"   Result: {result}")
        
        # Test Enhanced HackerRank
        print("\n4. Testing Enhanced HackerRank tracker...")
        result = tracker.get_enhanced_hackerrank_stats("testuser")
        print(f"   Result: {result}")
        
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting API Integration Tests")
    
    # Test the coding tracker first
    test_coding_tracker()
    
    # Then test the API endpoints
    test_api_endpoints()
    
    print("\nAll tests completed!")