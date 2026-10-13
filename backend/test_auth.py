#!/usr/bin/env python3
"""Test authentication endpoints"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_auth():
    print("Testing Authentication Endpoints")
    print("=" * 40)
    
    # Test data
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        # Test registration
        print("1. Testing Registration...")
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        print(f"Status: {reg_response.status_code}")
        print(f"Response: {reg_response.json()}")
        
        # Test login
        print("\n2. Testing Login...")
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Status: {login_response.status_code}")
        login_result = login_response.json()
        print(f"Response: {login_result}")
        
        if login_result.get("success"):
            token = login_result.get("token")
            print(f"\n3. Testing Protected Route...")
            headers = {"Authorization": f"Bearer {token}"}
            dashboard_response = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)
            print(f"Dashboard Status: {dashboard_response.status_code}")
            print(f"Dashboard Response: {dashboard_response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to backend. Make sure Flask app is running on port 5000")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_auth()