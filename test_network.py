#!/usr/bin/env python3
"""
Test script to verify network connectivity and authentication endpoints
"""
import requests
import json
import time
import subprocess
import threading
import sys
import os

def start_backend():
    """Start the backend server"""
    try:
        os.chdir('backend')
        subprocess.run([sys.executable, 'app.py'], check=True)
    except Exception as e:
        print(f"Failed to start backend: {e}")

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("[PASS] Backend is running")
            return True
        else:
            print(f"[FAIL] Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Backend not accessible: {e}")
        return False

def test_register_endpoint():
    """Test registration endpoint"""
    try:
        test_user = {
            "username": "testuser",
            "email": "test@example.com", 
            "password": "testpass123"
        }
        
        response = requests.post('http://localhost:5000/api/auth/register', 
                               json=test_user, timeout=10)
        
        if response.status_code in [200, 201]:
            print("[PASS] Registration endpoint working")
            return True
        elif response.status_code == 400:
            data = response.json()
            if "already exists" in data.get('message', ''):
                print("[PASS] Registration endpoint working (user exists)")
                return True
        
        print(f"[FAIL] Registration failed: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        print(f"[FAIL] Registration test failed: {e}")
        return False

def test_login_endpoint():
    """Test login endpoint"""
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post('http://localhost:5000/api/auth/login',
                               json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('token'):
                print("[PASS] Login endpoint working")
                return True
        
        print(f"[FAIL] Login failed: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        print(f"[FAIL] Login test failed: {e}")
        return False

def main():
    print("[TEST] Testing Network Connectivity")
    print("=" * 40)
    
    # Test if backend is running
    if not test_backend_health():
        print("\n[ERROR] Backend is not running!")
        print("Please start the backend with: cd backend && python app.py")
        return False
    
    # Test endpoints
    tests = [
        ("Registration Endpoint", test_register_endpoint),
        ("Login Endpoint", test_login_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[TEST] Testing {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"[RESULT] {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All network tests passed!")
        print("\n[INFO] The login/register should work now.")
        return True
    else:
        print("[ERROR] Some network tests failed")
        return False

if __name__ == "__main__":
    main()