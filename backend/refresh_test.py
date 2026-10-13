#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import json
import random

def test_health():
    with app.test_client() as client:
        response = client.get('/')
        print(f"Health Check: {response.status_code} - {response.get_json()}")
        return response.status_code == 200

def test_registration_and_login():
    with app.test_client() as client:
        # Test registration
        random_id = random.randint(10000, 99999)
        reg_data = {
            "username": f"user{random_id}",
            "email": f"user{random_id}@test.com",
            "password": "test123456"
        }
        
        reg_response = client.post('/api/auth/register', 
                                 data=json.dumps(reg_data),
                                 content_type='application/json')
        
        print(f"Registration: {reg_response.status_code} - {reg_response.get_json()}")
        
        if reg_response.status_code != 201:
            return False
        
        # Test login
        login_data = {
            "email": reg_data["email"],
            "password": reg_data["password"]
        }
        
        login_response = client.post('/api/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')
        
        print(f"Login: {login_response.status_code} - {login_response.get_json()}")
        
        if login_response.status_code != 200:
            return False
        
        # Test dashboard with token
        token = login_response.get_json()["token"]
        dashboard_response = client.get('/api/dashboard',
                                      headers={'Authorization': f'Bearer {token}'})
        
        print(f"Dashboard: {dashboard_response.status_code} - {dashboard_response.get_json()}")
        
        return dashboard_response.status_code == 200

if __name__ == "__main__":
    print("=== REFRESH TEST - Checking All Endpoints ===\n")
    
    if test_health():
        print("[OK] Server health check passed")
        
        if test_registration_and_login():
            print("[OK] Registration, Login, and Dashboard all working")
            print("\n=== ALL TESTS PASSED ===")
            print("Your server is working perfectly!")
        else:
            print("[ERROR] Authentication flow failed")
    else:
        print("[ERROR] Server health check failed")