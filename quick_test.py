#!/usr/bin/env python3
import requests
import json

def test_registration():
    try:
        url = "http://localhost:5000/api/auth/register"
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        print(f"Testing registration at {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("[PASS] Registration successful!")
        elif response.status_code == 400:
            print("[WARN] Registration failed - validation error")
        else:
            print("[FAIL] Registration failed - server error")
            
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")

def test_login():
    try:
        url = "http://localhost:5000/api/auth/login"
        data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        print(f"\nTesting login at {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("[PASS] Login successful!")
        else:
            print("[FAIL] Login failed")
            
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")

if __name__ == "__main__":
    print("[TEST] Quick Authentication Test")
    print("=" * 40)
    test_registration()
    test_login()