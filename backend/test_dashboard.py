#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import json
import random

def test_dashboard():
    with app.test_client() as client:
        # Register and login user
        random_id = random.randint(10000, 99999)
        reg_data = {
            "username": f"testuser{random_id}",
            "email": f"test{random_id}@example.com",
            "password": "password123"
        }
        
        # Register
        reg_response = client.post('/api/auth/register', 
                                 data=json.dumps(reg_data),
                                 content_type='application/json')
        
        if reg_response.status_code != 201:
            print(f"Registration failed: {reg_response.get_json()}")
            return False
        
        # Login
        login_data = {"email": reg_data["email"], "password": reg_data["password"]}
        login_response = client.post('/api/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.get_json()}")
            return False
        
        token = login_response.get_json()["token"]
        headers = {'Authorization': f'Bearer {token}'}
        
        print("Testing Dashboard Endpoint...")
        
        # Test dashboard
        dashboard_response = client.get('/api/dashboard', headers=headers)
        print(f"Dashboard Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            result = dashboard_response.get_json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            
            if 'user' in result:
                user = result['user']
                print(f"User ID: {user.get('id')}")
                print(f"Username: {user.get('username')}")
                print(f"Email: {user.get('email')}")
                print(f"Skill Level: {user.get('skill_level')}")
                print(f"Problems Solved: {user.get('problems_solved')}")
                print(f"Streak: {user.get('streak')}")
                
                print("\\n=== Dashboard Working! ===")
                return True
            else:
                print("ERROR: No user data in response")
        else:
            print(f"Dashboard failed: {dashboard_response.get_json()}")
        
        return False

if __name__ == "__main__":
    if test_dashboard():
        print("\\n[SUCCESS] Dashboard endpoint working correctly!")
    else:
        print("\\n[ERROR] Dashboard endpoint failed")