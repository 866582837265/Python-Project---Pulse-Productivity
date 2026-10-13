#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_registration():
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        print(f"Registration Status: {response.status_code}")
        print(f"Registration Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Registration Error: {e}")
        return False

def test_login():
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Login Error: {e}")
        return False

def test_health():
    url = f"{BASE_URL}/"
    try:
        response = requests.get(url, timeout=5)
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing endpoints...")
    
    if test_health():
        print("✓ Server is running")
        
        if test_registration():
            print("✓ Registration works")
            
            if test_login():
                print("✓ Login works")
                print("\nAll tests passed!")
            else:
                print("✗ Login failed")
        else:
            print("✗ Registration failed")
    else:
        print("✗ Server is not running or not responding")