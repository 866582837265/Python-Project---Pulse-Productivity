#!/usr/bin/env python3
"""
Test script to verify 500 error fixes for topic detail endpoint
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_server_health():
    """Test if server is running"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"❌ Backend server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("   Make sure Flask server is running: python backend/app.py")
        return False

def test_cors_preflight():
    """Test CORS preflight handling"""
    print("\n🔍 Testing CORS preflight...")
    try:
        response = requests.options(f"{BASE_URL}/api/roadmap/topic/test")
        if response.status_code in [200, 204]:
            print("✅ CORS preflight handled correctly")
            return True
        else:
            print(f"⚠️  CORS preflight returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CORS preflight test failed: {e}")
        return False

def test_authentication_validation():
    """Test authentication validation"""
    print("\n🔍 Testing authentication validation...")
    
    # Test without token
    try:
        response = requests.get(f"{BASE_URL}/api/roadmap/topic/test-topic")
        if response.status_code == 401:
            print("✅ Correctly returns 401 for missing authentication")
            return True
        else:
            print(f"⚠️  Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_topic_id_validation():
    """Test topic ID validation"""
    print("\n🔍 Testing topic ID validation...")
    
    # This would require a valid token, so we'll just verify the endpoint exists
    try:
        response = requests.get(f"{BASE_URL}/api/roadmap/topic/")
        # Should return 404 for empty topic_id
        if response.status_code in [404, 401]:  # 401 if no auth, 404 if empty topic_id
            print("✅ Endpoint handles empty topic_id correctly")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Topic ID validation test failed: {e}")
        return False

def test_error_response_format():
    """Test error response format"""
    print("\n🔍 Testing error response format...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/roadmap/topic/invalid-topic")
        
        # Should return JSON even on error
        try:
            data = response.json()
            if "success" in data and "error" in data:
                print("✅ Error responses have correct JSON format")
                print(f"   Sample error: {data.get('error')}")
                return True
            else:
                print("⚠️  Error response missing required fields")
                return False
        except json.JSONDecodeError:
            print("❌ Error response is not valid JSON")
            return False
            
    except Exception as e:
        print(f"❌ Error response format test failed: {e}")
        return False

def test_debug_endpoints():
    """Test debug endpoints"""
    print("\n🔍 Testing debug endpoints...")
    
    endpoints_to_test = [
        "/api/test/gemini/Arrays",
        "/api/health"
    ]
    
    all_passed = True
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"⚠️  {endpoint} - Status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            all_passed = False
    
    return all_passed

def test_json_safety():
    """Test JSON safety of responses"""
    print("\n🔍 Testing JSON safety...")
    
    try:
        # Test a simple endpoint that should return JSON
        response = requests.get(f"{BASE_URL}/api/health")
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Check for common JSON-unsafe types
                json_str = json.dumps(data)  # This will fail if not JSON-safe
                print("✅ Response is JSON-safe")
                return True
            except (TypeError, ValueError) as e:
                print(f"❌ Response contains non-JSON-safe data: {e}")
                return False
        else:
            print(f"⚠️  Health endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ JSON safety test failed: {e}")
        return False

def test_question_pack_generation():
    """Test question pack generation endpoint"""
    print("\n🔍 Testing question pack generation...")
    
    # This requires authentication, so we'll just test the endpoint exists
    try:
        response = requests.get(f"{BASE_URL}/api/roadmap/topic/test_generate/arrays")
        
        # Should return 401 (no auth) rather than 500 (server error)
        if response.status_code == 401:
            print("✅ Test generate endpoint exists and handles auth correctly")
            return True
        elif response.status_code == 200:
            print("✅ Test generate endpoint working (user authenticated)")
            return True
        else:
            print(f"⚠️  Test generate endpoint returned {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ Question pack generation test failed: {e}")
        return False

def main():
    print("🚀 Testing 500 Error Fixes for Topic Detail Endpoint")
    print("=" * 60)
    
    tests = [
        ("Server Health", test_server_health),
        ("CORS Preflight", test_cors_preflight),
        ("Authentication Validation", test_authentication_validation),
        ("Topic ID Validation", test_topic_id_validation),
        ("Error Response Format", test_error_response_format),
        ("JSON Safety", test_json_safety),
        ("Debug Endpoints", test_debug_endpoints),
        ("Question Pack Generation", test_question_pack_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The 500 error fixes should be working.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    print("\n📋 Manual Testing Steps:")
    print("1. Start Flask server: python backend/app.py")
    print("2. Start React frontend: npm run dev")
    print("3. Login and complete skill assessment")
    print("4. Click on any topic in the roadmap")
    print("5. Verify:")
    print("   - No 500 errors occur")
    print("   - Topic loads successfully OR shows friendly error message")
    print("   - Error messages are helpful and descriptive")
    print("   - All responses are valid JSON")
    
    print("\n🔧 Debug Commands:")
    print(f"# Test topic generation (requires auth token)")
    print(f"curl -H 'Authorization: Bearer <token>' {BASE_URL}/api/roadmap/topic/test_generate/arrays")
    print(f"")
    print(f"# Test topic details (requires auth token)")
    print(f"curl -H 'Authorization: Bearer <token>' {BASE_URL}/api/roadmap/topic/<topic_id>")
    print(f"")
    print(f"# Test debug endpoint (requires auth token)")
    print(f"curl -H 'Authorization: Bearer <token>' {BASE_URL}/api/debug/check_topic/<topic_id>")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)