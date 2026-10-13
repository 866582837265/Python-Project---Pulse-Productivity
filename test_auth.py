#!/usr/bin/env python3
"""
Simple test script to verify the authentication API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_registration():
    """Test user registration"""
    print("🧪 Testing Registration...")
    
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n🧪 Testing Login...")
    
    data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200 and result.get("success"):
            return result.get("token")
        return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_dashboard(token):
    """Test protected dashboard endpoint"""
    print("\n🧪 Testing Dashboard (Protected Route)...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_health():
    """Test health endpoint"""
    print("🧪 Testing Health Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Authentication API Tests\n")
    
    # Test health endpoint
    if not test_health():
        print("❌ Backend is not running or not responding")
        exit(1)
    
    # Test registration
    if not test_registration():
        print("❌ Registration test failed")
        exit(1)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login test failed")
        exit(1)
    
    # Test protected route
    if not test_dashboard(token):
        print("❌ Dashboard test failed")
        exit(1)
    
    print("\n✅ All tests passed! Authentication system is working correctly.")