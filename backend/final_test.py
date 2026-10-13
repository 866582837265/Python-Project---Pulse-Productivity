#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, users_collection, in_memory_users
import json
import random

def cleanup_test_user():
    """Remove test user if exists"""
    test_email = "test@example.com"
    if users_collection is not None:
        users_collection.delete_one({"email": test_email})
    else:
        if test_email in in_memory_users:
            del in_memory_users[test_email]

def test_registration():
    with app.test_client() as client:
        # Use random email to avoid conflicts
        random_id = random.randint(1000, 9999)
        data = {
            "username": f"testuser{random_id}",
            "email": f"test{random_id}@example.com", 
            "password": "password123"
        }
        
        response = client.post('/api/auth/register', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        print(f"Registration Status: {response.status_code}")
        print(f"Registration Response: {response.get_json()}")
        return response.status_code == 201, data["email"]

def test_login(email):
    with app.test_client() as client:
        data = {
            "email": email,
            "password": "password123"
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(data), 
                             content_type='application/json')
        
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.get_json()}")
        return response.status_code == 200

if __name__ == "__main__":
    print("Testing registration and login endpoints...")
    
    reg_success, test_email = test_registration()
    if reg_success:
        print("[SUCCESS] Registration works")
        if test_login(test_email):
            print("[SUCCESS] Login works")
            print("\nAll tests passed!")
        else:
            print("[ERROR] Login failed")
    else:
        print("[ERROR] Registration failed")