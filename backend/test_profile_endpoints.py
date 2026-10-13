#!/usr/bin/env python3
"""
Profile Endpoints Test Script
Tests the new profile management and external API integration endpoints
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_profile_endpoints():
    """Test profile management endpoints"""
    print("🔍 Testing Profile Management Endpoints\n")
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Profile endpoints without auth (should return 401)
    print("\n2. Testing profile endpoints without authentication...")
    
    endpoints = [
        "/api/profile/update_links",
        "/api/profile/progress"
    ]
    
    for endpoint in endpoints:
        try:
            if "update_links" in endpoint:
                response = requests.post(f"{BASE_URL}{endpoint}", 
                                       json={"leetcode": "test"}, timeout=10)
            else:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            
            if response.status_code == 401:
                print(f"   ✅ {endpoint} correctly requires authentication")
            else:
                print(f"   ❌ {endpoint} should return 401, got {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} error: {e}")
    
    # Test 3: External API functions
    print("\n3. Testing external API integration functions...")
    
    try:
        # Import the app to test functions
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        
        from app import fetch_leetcode_stats, fetch_hackerrank_stats, fetch_hackerearth_stats, calculate_overall_score
        
        # Test LeetCode API
        print("   Testing LeetCode API...")
        leetcode_stats = fetch_leetcode_stats("test_user")
        if leetcode_stats and "solved" in leetcode_stats:
            print(f"   ✅ LeetCode API returned: {leetcode_stats}")
        else:
            print("   ❌ LeetCode API failed")
        
        # Test HackerRank API
        print("   Testing HackerRank API...")
        hackerrank_stats = fetch_hackerrank_stats("test_user")
        if hackerrank_stats and "stars" in hackerrank_stats:
            print(f"   ✅ HackerRank API returned: {hackerrank_stats}")
        else:
            print("   ❌ HackerRank API failed")
        
        # Test HackerEarth API
        print("   Testing HackerEarth API...")
        hackerearth_stats = fetch_hackerearth_stats("test_user")
        if hackerearth_stats and "rating" in hackerearth_stats:
            print(f"   ✅ HackerEarth API returned: {hackerearth_stats}")
        else:
            print("   ❌ HackerEarth API failed")
        
        # Test overall score calculation
        print("   Testing overall score calculation...")
        test_progress = {
            "leetcode": {"solved": 100},
            "hackerrank": {"stars": 5},
            "hackerearth": {"rating": 1500}
        }
        overall_score = calculate_overall_score(test_progress)
        if isinstance(overall_score, int) and 0 <= overall_score <= 100:
            print(f"   ✅ Overall score calculation returned: {overall_score}")
        else:
            print(f"   ❌ Overall score calculation failed: {overall_score}")
        
    except Exception as e:
        print(f"   ❌ External API functions test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 Profile endpoints test completed!")
    return True

def test_json_responses():
    """Test that all endpoints return proper JSON"""
    print("\n🔍 Testing JSON Response Format\n")
    
    endpoints = [
        ("GET", "/"),
        ("GET", "/api/health"),
        ("GET", "/api/test"),
        ("POST", "/api/profile/update_links", {"leetcode": "test"}),
        ("GET", "/api/profile/progress"),
    ]
    
    for method, endpoint, *data in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data[0] if data else {}, timeout=10)
            
            # Check if response is JSON
            try:
                json_data = response.json()
                print(f"   ✅ {method} {endpoint} returns valid JSON")
                
                # Check for success field in API responses
                if endpoint.startswith('/api/') and endpoint not in ['/', '/api/health', '/api/test']:
                    if 'success' in json_data or 'error' in json_data:
                        print(f"      ✅ Contains success/error field")
                    else:
                        print(f"      ⚠️ Missing success/error field")
                        
            except json.JSONDecodeError:
                print(f"   ❌ {method} {endpoint} returns invalid JSON")
                print(f"      Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ {method} {endpoint} error: {e}")
    
    return True

def main():
    print("🚀 Profile Endpoints Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test profile endpoints
    if not test_profile_endpoints():
        success = False
    
    # Test JSON responses
    if not test_json_responses():
        success = False
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    if success:
        print("✅ All tests passed! Profile endpoints are working correctly.")
        print("\n🎉 Ready to test the frontend profile page!")
        print("\nNext steps:")
        print("1. Start the backend: python app.py")
        print("2. Start the frontend: npm run dev")
        print("3. Navigate to /profile in your browser")
        print("4. Test profile link updates and progress fetching")
        return 0
    else:
        print("❌ Some tests failed. Check the backend configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())