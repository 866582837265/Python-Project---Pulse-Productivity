#!/usr/bin/env python3
import requests
import json

def test_cors_options():
    """Test CORS OPTIONS requests"""
    base_url = "http://127.0.0.1:5000"
    
    # Test OPTIONS request to quiz submit endpoint
    try:
        response = requests.options(f"{base_url}/api/quiz/submit", 
                                  headers={
                                      'Origin': 'http://localhost:5173',
                                      'Access-Control-Request-Method': 'POST',
                                      'Access-Control-Request-Headers': 'Content-Type,Authorization'
                                  })
        print(f"OPTIONS /api/quiz/submit: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        # Test actual POST request
        token = "test-token"  # This will fail but should show CORS is working
        post_response = requests.post(f"{base_url}/api/quiz/submit",
                                    headers={
                                        'Content-Type': 'application/json',
                                        'Authorization': f'Bearer {token}',
                                        'Origin': 'http://localhost:5173'
                                    },
                                    json={"domain": "programming", "answers": []})
        
        print(f"POST /api/quiz/submit: {post_response.status_code}")
        print(f"Response: {post_response.json()}")
        
        return True
        
    except Exception as e:
        print(f"CORS test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing CORS configuration...")
    print("Make sure the Flask server is running on port 5000")
    print()
    
    if test_cors_options():
        print("\\nCORS test completed")
    else:
        print("\\nCORS test failed")