#!/usr/bin/env python3
"""
Quick test to verify Java templates are working
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_java_templates():
    print("Testing Java template generation...")
    
    # Test registration
    reg_data = {
        "username": "testjava",
        "email": "testjava@example.com", 
        "password": "password123"
    }
    
    try:
        # Register
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json=reg_data)
        if reg_response.status_code != 201:
            print(f"Registration failed: {reg_response.text}")
            return
        
        # Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": reg_data["email"],
            "password": reg_data["password"]
        })
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
            
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Clear cache first
        clear_response = requests.post(f"{BASE_URL}/api/user/clear-content-cache", headers=headers)
        print(f"Cache clear: {clear_response.status_code}")
        
        # Test topic content generation (this should trigger Java templates)
        topic_response = requests.get(f"{BASE_URL}/api/roadmap/topic/1", headers=headers)
        
        if topic_response.status_code == 200:
            data = topic_response.json()
            if data.get("success") and "topic" in data:
                coding_questions = data["topic"].get("coding_questions", [])
                if coding_questions:
                    starter_code = coding_questions[0].get("starter_code", "")
                    print(f"Generated starter code:")
                    print(starter_code)
                    print()
                    
                    # Check if it's Java or Python
                    if "public class Main" in starter_code:
                        print("SUCCESS: Java template detected!")
                    elif "def solution" in starter_code or "pass" in starter_code:
                        print("FAILURE: Python template detected!")
                        print("This means the fix didn't work")
                    else:
                        print("UNKNOWN: Template format not recognized")
                else:
                    print("No coding questions found")
            else:
                print(f"Topic request failed: {data}")
        else:
            print(f"Topic request failed with status {topic_response.status_code}")
            print(topic_response.text)
            
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    test_java_templates()