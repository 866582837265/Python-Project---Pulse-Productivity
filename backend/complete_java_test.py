#!/usr/bin/env python3
"""
Complete test including assessment and Java template verification
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def complete_test():
    print("Testing complete Java template flow...")
    
    # Test data
    reg_data = {
        "username": "javatest",
        "email": "javatest@example.com", 
        "password": "password123"
    }
    
    try:
        # 1. Register
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json=reg_data)
        if reg_response.status_code != 201:
            print(f"Registration failed: {reg_response.text}")
            return
        print("1. Registration successful")
        
        # 2. Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": reg_data["email"],
            "password": reg_data["password"]
        })
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
            
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("2. Login successful")
        
        # 3. Submit quiz to get assessment
        quiz_data = {
            "domain": "programming",
            "answers": [
                {"question_id": 1, "selected_answer": 0, "time_taken": 30},
                {"question_id": 2, "selected_answer": 1, "time_taken": 25},
                {"question_id": 3, "selected_answer": 2, "time_taken": 35},
                {"question_id": 4, "selected_answer": 0, "time_taken": 40},
                {"question_id": 5, "selected_answer": 1, "time_taken": 30}
            ]
        }
        
        quiz_response = requests.post(f"{BASE_URL}/api/quiz/submit", json=quiz_data, headers=headers)
        if quiz_response.status_code == 200:
            quiz_result = quiz_response.json()
            print(f"3. Quiz submitted - Level: {quiz_result.get('predicted_level')}")
        else:
            print(f"Quiz submission failed: {quiz_response.text}")
            return
        
        # 4. Get roadmap
        roadmap_response = requests.get(f"{BASE_URL}/api/roadmap", headers=headers)
        if roadmap_response.status_code == 200:
            roadmap_data = roadmap_response.json()
            if roadmap_data.get("success") and roadmap_data.get("roadmap"):
                first_topic_id = roadmap_data["roadmap"][0]["id"]
                print(f"4. Roadmap loaded - First topic ID: {first_topic_id}")
            else:
                print("No roadmap data found")
                return
        else:
            print(f"Roadmap request failed: {roadmap_response.text}")
            return
        
        # 5. Get topic details (this should generate Java templates)
        topic_response = requests.get(f"{BASE_URL}/api/roadmap/topic/{first_topic_id}", headers=headers)
        
        if topic_response.status_code == 200:
            data = topic_response.json()
            if data.get("success") and "topic" in data:
                coding_questions = data["topic"].get("coding_questions", [])
                if coding_questions:
                    starter_code = coding_questions[0].get("starter_code", "")
                    print(f"5. Generated starter code:")
                    print(starter_code)
                    print()
                    
                    # Check if it's Java or Python
                    if "public class Main" in starter_code:
                        print("SUCCESS: Java template detected!")
                        return True
                    elif "def solution" in starter_code or "pass" in starter_code:
                        print("FAILURE: Python template detected!")
                        print("The fix didn't work")
                        return False
                    else:
                        print("UNKNOWN: Template format not recognized")
                        return False
                else:
                    print("No coding questions found")
                    return False
            else:
                print(f"Topic request failed: {data}")
                return False
        else:
            print(f"Topic request failed with status {topic_response.status_code}")
            print(topic_response.text)
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = complete_test()
    if success:
        print("\nJava templates are working correctly!")
    else:
        print("\nJava templates are NOT working - still showing Python code")