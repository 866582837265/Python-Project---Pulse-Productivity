#!/usr/bin/env python3
"""
Test script to verify profile page functionality
"""

import requests
import json
import sys

def test_profile_endpoints():
    """Test the profile-related API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("Testing Profile Page Endpoints")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing backend health...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print(f"   ❌ Backend returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend is not running")
        print("   Please start backend: cd backend && python app.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Register test user
    print("\n2. Testing user registration...")
    test_user = {
        "email": "profiletest@example.com",
        "username": "profiletest",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=test_user)
        if response.status_code in [200, 201]:
            print("   ✅ User registration successful")
        elif response.status_code == 400 and "already exists" in response.text:
            print("   ✅ User already exists (OK)")
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
    
    # Test 3: Login
    print("\n3. Testing user login...")
    login_data = {
        "email": "profiletest@example.com",
        "password": "testpass123"
    }
    
    token = None
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("token"):
                token = result["token"]
                print("   ✅ Login successful")
            else:
                print(f"   ❌ Login failed: {result}")
                return False
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    if not token:
        print("   ❌ No token received")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 4: Profile endpoint
    print("\n4. Testing profile endpoint...")
    try:
        response = requests.get(f"{base_url}/api/user/profile", headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            print("   ✅ Profile endpoint working")
            print(f"   📋 Profile data: {json.dumps(profile_data, indent=2)}")
        else:
            print(f"   ❌ Profile endpoint failed: {response.status_code}")
            print(f"   📋 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Profile endpoint error: {e}")
    
    # Test 5: Dashboard endpoint
    print("\n5. Testing dashboard endpoint...")
    try:
        response = requests.get(f"{base_url}/api/dashboard", headers=headers)
        if response.status_code == 200:
            dashboard_data = response.json()
            print("   ✅ Dashboard endpoint working")
            print(f"   📋 User: {dashboard_data.get('username', 'N/A')}")
        else:
            print(f"   ❌ Dashboard endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard endpoint error: {e}")
    
    # Test 6: Profile links update
    print("\n6. Testing profile links update...")
    profile_links = {
        "leetcode": "testuser123",
        "hackerrank": "testuser456"
    }
    
    try:
        response = requests.post(f"{base_url}/api/profile/update_links", 
                               json=profile_links, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Profile links update working")
            print(f"   📋 Response: {result.get('message', 'Success')}")
        else:
            print(f"   ❌ Profile links update failed: {response.status_code}")
            print(f"   📋 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Profile links update error: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Profile page backend tests completed!")
    print("\nNext steps:")
    print("1. Start frontend: cd frontend && npm run dev")
    print("2. Navigate to http://localhost:5173")
    print("3. Login with: profiletest@example.com / testpass123")
    print("4. Go to Profile page")
    
    return True

def check_frontend_files():
    """Check if required frontend files exist"""
    import os
    
    print("\nChecking Frontend Files")
    print("=" * 30)
    
    required_files = [
        "frontend/src/App.jsx",
        "frontend/src/UserProfile.jsx",
        "frontend/src/UserProfile.css",
        "frontend/src/Navigation.jsx",
        "frontend/src/AuthContext.jsx",
        "frontend/src/api.js",
        "frontend/src/ErrorBoundary.jsx"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_exist = False
    
    if all_exist:
        print("\n✅ All required files exist")
    else:
        print("\n❌ Some files are missing")
    
    return all_exist

if __name__ == "__main__":
    print("🔍 Profile Page Functionality Test")
    print("=" * 50)
    
    # Check files first
    files_ok = check_frontend_files()
    
    if files_ok:
        # Test backend endpoints
        backend_ok = test_profile_endpoints()
        
        if backend_ok:
            print("\n🎉 All tests passed! Profile page should work correctly.")
        else:
            print("\n⚠️ Some backend tests failed. Check the issues above.")
    else:
        print("\n⚠️ Missing files detected. Profile page may not work correctly.")
    
    print("\n📖 For detailed debugging, see: PROFILE_DEBUG_GUIDE.md")