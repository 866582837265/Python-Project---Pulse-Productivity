#!/usr/bin/env python3
"""
Backend API Test Script
Tests all critical endpoints to ensure they return proper JSON responses
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"Testing {method} {endpoint}...")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "OPTIONS":
            response = requests.options(url, headers=headers, timeout=10)
        
        print(f"  Status: {response.status_code}")
        
        # Check if response is JSON
        try:
            json_data = response.json()
            print(f"  JSON: ✅ Valid")
            if "success" in json_data:
                print(f"  Success: {json_data['success']}")
            if "error" in json_data:
                print(f"  Error: {json_data['error']}")
        except:
            print(f"  JSON: ❌ Invalid - Response: {response.text[:100]}")
            return False
        
        return response.status_code == expected_status
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Network Error: {e}")
        return False

def main():
    print("🔍 Testing Flask Backend API Endpoints\n")
    
    # Test basic endpoints
    tests = [
        ("GET", "/", None, None, 200),
        ("GET", "/api/health", None, None, 200),
        ("GET", "/api/test", None, None, 200),
    ]
    
    # Test endpoints that require authentication (should return 401)
    auth_tests = [
        ("GET", "/api/dashboard", None, None, 401),
        ("GET", "/api/roadmap", None, None, 401),
        ("POST", "/api/quiz/submit", {"score": 3}, None, 401),
    ]
    
    # Test CORS preflight
    cors_tests = [
        ("OPTIONS", "/api/quiz/submit", None, {"Origin": "http://localhost:3000"}, 200),
        ("OPTIONS", "/api/roadmap", None, {"Origin": "http://localhost:3000"}, 200),
    ]
    
    all_passed = True
    
    print("📋 Basic Endpoints:")
    for method, endpoint, data, headers, expected in tests:
        if not test_endpoint(method, endpoint, data, headers, expected):
            all_passed = False
        print()
    
    print("🔐 Authentication Required Endpoints (should return 401):")
    for method, endpoint, data, headers, expected in auth_tests:
        if not test_endpoint(method, endpoint, data, headers, expected):
            all_passed = False
        print()
    
    print("🌐 CORS Preflight Tests:")
    for method, endpoint, data, headers, expected in cors_tests:
        if not test_endpoint(method, endpoint, data, headers, expected):
            all_passed = False
        print()
    
    if all_passed:
        print("✅ All tests passed! Backend is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the backend configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())