#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import json
import random

def test_quiz_with_roadmap():
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
        
        # Login
        login_data = {"email": reg_data["email"], "password": reg_data["password"]}
        login_response = client.post('/api/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')
        
        token = login_response.get_json()["token"]
        headers = {'Authorization': f'Bearer {token}'}
        
        print("Testing Quiz Submission with Roadmap Generation...")
        
        # Submit quiz with high performance (should get advanced level)
        high_performance_answers = [
            {"question_id": 1, "selected_answer": 1, "time_taken": 15},  # Correct
            {"question_id": 2, "selected_answer": 1, "time_taken": 12},  # Correct
            {"question_id": 3, "selected_answer": 2, "time_taken": 18},  # Correct
            {"question_id": 4, "selected_answer": 2, "time_taken": 10},  # Correct
            {"question_id": 5, "selected_answer": 1, "time_taken": 20},  # Correct
            {"question_id": 6, "selected_answer": 1, "time_taken": 8},   # Correct
            {"question_id": 7, "selected_answer": 1, "time_taken": 14},  # Correct
            {"question_id": 8, "selected_answer": 1, "time_taken": 16},  # Correct
        ]
        
        submit_data = {
            "domain": "programming",
            "answers": high_performance_answers
        }
        
        submit_response = client.post('/api/quiz/submit',
                                    data=json.dumps(submit_data),
                                    content_type='application/json',
                                    headers=headers)
        
        print(f"Status: {submit_response.status_code}")
        
        if submit_response.status_code == 200:
            result = submit_response.get_json()
            print(f"Success: {result['success']}")
            print(f"Correct: {result['correct_answers']}/{result['total_questions']}")
            print(f"Accuracy: {result['accuracy']}%")
            # print(f"Avg time: {result.get('avg_time_per_question', 'N/A')}s")  # Optional field
            print(f"Predicted Level: {result['skill_level']}")
            print(f"Roadmap included: {'roadmap' in result}")
            
            if 'roadmap' in result:
                roadmap = result['roadmap']
                print(f"Roadmap Title: {roadmap['title']}")
                print(f"Duration: {roadmap['duration']}")
                print(f"Milestones: {len(roadmap['milestones'])}")
                
                print("\\n=== Quiz with Roadmap Working! ===")
                return True
            else:
                print("ERROR: No roadmap in response")
        else:
            print(f"ERROR: {submit_response.get_json()}")
        
        return False

if __name__ == "__main__":
    if test_quiz_with_roadmap():
        print("\\n[SUCCESS] Quiz submission with roadmap generation working!")
    else:
        print("\\n[ERROR] Quiz submission failed")