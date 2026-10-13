import requests
import json

# Test quiz submission endpoint
def test_quiz_submit():
    # First login to get token
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        # Register user first
        register_response = requests.post("http://127.0.0.1:5000/api/auth/register", 
                                        json={
                                            "email": "test@example.com",
                                            "username": "testuser",
                                            "password": "password123"
                                        })
        print(f"Register: {register_response.status_code}")
        
        # Login
        login_response = requests.post("http://127.0.0.1:5000/api/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json()["token"]
            print(f"Token received: {token[:20]}...")
            
            # Test quiz submission
            quiz_data = {
                "domain": "programming",
                "answers": [
                    {"question_id": 1, "selected_answer": "A", "time_taken": 25},
                    {"question_id": 2, "selected_answer": "B", "time_taken": 30},
                    {"question_id": 3, "selected_answer": "C", "time_taken": 20}
                ]
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            
            submit_response = requests.post("http://127.0.0.1:5000/api/quiz/submit", 
                                         json=quiz_data, headers=headers)
            
            print(f"Quiz Submit Status: {submit_response.status_code}")
            print(f"Quiz Submit Response: {submit_response.text}")
            
        else:
            print(f"Login failed: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure Flask server is running on port 5000")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_quiz_submit()