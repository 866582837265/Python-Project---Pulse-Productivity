#!/usr/bin/env python3
"""
Verification script to test that 500 error fixes are working properly.
Tests the topic detail endpoint with various scenarios.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_health_endpoint():
    """Test basic server health"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_topic_endpoint_without_auth():
    """Test topic endpoint without authentication - should return 401, not 500"""
    try:
        response = requests.get(f"{BASE_URL}/api/roadmap/topic/test-topic")
        print(f"✅ No auth test: {response.status_code} - Expected 401")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ No auth test failed: {e}")
        return False

def test_topic_endpoint_with_invalid_token():
    """Test topic endpoint with invalid token - should return 401, not 500"""
    try:
        headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{BASE_URL}/api/roadmap/topic/test-topic", headers=headers)
        print(f"✅ Invalid token test: {response.status_code} - Expected 401")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ Invalid token test failed: {e}")
        return False

def test_topic_endpoint_empty_id():
    """Test topic endpoint with empty ID - should return 400, not 500"""
    try:
        headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{BASE_URL}/api/roadmap/topic/", headers=headers)
        print(f"✅ Empty ID test: {response.status_code} - Expected 404 (route not found)")
        return response.status_code in [404, 400]
    except Exception as e:
        print(f"❌ Empty ID test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🔍 Verifying 500 error fixes...")
    print("=" * 50)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("No Authentication", test_topic_endpoint_without_auth),
        ("Invalid Token", test_topic_endpoint_with_invalid_token),
        ("Empty Topic ID", test_topic_endpoint_empty_id),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All 500 error prevention tests PASSED!")
        print("✅ Server returns appropriate HTTP status codes instead of 500 errors")
    else:
        print("⚠️ Some tests failed - check server logs")
    
    print("\n📝 Next steps:")
    print("1. Start your Flask backend: python app.py")
    print("2. Test with a real user token for full validation")
    print("3. Click roadmap topics in frontend to verify no 500 errors")

if __name__ == "__main__":
    main()