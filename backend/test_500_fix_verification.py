#!/usr/bin/env python3
"""
Verification script to test the 500 error fix for topic detail endpoint
"""

import requests
import json
import sys

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpass123"

def test_endpoint(endpoint, method="GET", headers=None, data=None):
    """Test an endpoint and return response"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Testing {method} {endpoint}")
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
            return response.status_code, json_response
        except:
            print(f"Response (text): {response.text}")
            return response.status_code, response.text
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None, str(e)

def main():
    print("🚀 Starting 500 Error Fix Verification")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    status, response = test_endpoint("/api/health")
    if status != 200:
        print("❌ Health check failed - server may not be running")
        return False
    
    # Test 2: Test endpoint without authentication (should fail gracefully)
    print("\n2. Testing topic endpoint without auth...")
    status, response = test_endpoint("/api/roadmap/topic/test-topic-id")
    if status == 500:
        print("❌ Still getting 500 error without auth")
        return False
    elif status == 401:
        print("✅ Properly returns 401 for missing auth")
    
    # Test 3: Test with invalid topic ID (should fail gracefully)
    print("\n3. Testing with invalid topic ID...")
    headers = {"Authorization": "Bearer invalid-token"}
    status, response = test_endpoint("/api/roadmap/topic/invalid-topic", headers=headers)
    if status == 500:
        print("❌ Still getting 500 error with invalid token")
        return False
    elif status == 401:
        print("✅ Properly returns 401 for invalid token")
    
    # Test 4: Test debug endpoint
    print("\n4. Testing debug endpoint...")
    status, response = test_endpoint("/api/debug/check_topic/test-topic", headers=headers)
    if status == 500:
        print("❌ Debug endpoint still returns 500")
        return False
    elif status == 401:
        print("✅ Debug endpoint properly handles auth")
    
    # Test 5: Test test_generate endpoint
    print("\n5. Testing test_generate endpoint...")
    status, response = test_endpoint("/api/roadmap/topic/test_generate/test-topic", headers=headers)
    if status == 500:
        print("❌ Test generate endpoint still returns 500")
        return False
    elif status == 401:
        print("✅ Test generate endpoint properly handles auth")
    
    print("\n" + "=" * 50)
    print("✅ All endpoints properly handle errors without 500s!")
    print("🎉 500 Error Fix Verification PASSED")
    
    print("\n📋 Next Steps:")
    print("1. Start your backend server: python app.py")
    print("2. Test with a real user login and valid topic ID")
    print("3. Check that topic detail page loads without 500 errors")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)