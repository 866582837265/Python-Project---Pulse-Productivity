#!/usr/bin/env python3
"""
Test script for the topic detail endpoint
Run this to verify the endpoint is working correctly
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpass123"

def test_topic_endpoint():
    """Test the topic detail endpoint"""
    print("🧪 Testing Topic Detail Endpoint")
    print("=" * 50)
    
    # Step 1: Login to get token
    print("1. Logging in...")
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        login_result = login_response.json()
        if not login_result.get("success"):
            print(f"❌ Login failed: {login_result.get('message')}")
            return False
        
        token = login_result.get("token")
        print(f"✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Get roadmap to find a topic ID
    print("2. Getting roadmap...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        roadmap_response = requests.get(f"{BASE_URL}/api/roadmap", headers=headers)
        if roadmap_response.status_code != 200:
            print(f"❌ Roadmap fetch failed: {roadmap_response.status_code}")
            print(f"Response: {roadmap_response.text}")
            return False
        
        roadmap_result = roadmap_response.json()
        if not roadmap_result.get("success"):
            print(f"❌ Roadmap fetch failed: {roadmap_result.get('error')}")
            return False
        
        roadmap = roadmap_result.get("roadmap", [])
        if not roadmap:
            print("❌ No roadmap topics found")
            return False
        
        # Get first topic ID
        first_topic = roadmap[0]
        topic_id = first_topic.get("id")
        topic_title = first_topic.get("title")
        print(f"✅ Found topic: {topic_title} (ID: {topic_id})")
        
    except Exception as e:
        print(f"❌ Roadmap error: {e}")
        return False
    
    # Step 3: Test topic detail endpoint
    print("3. Testing topic detail endpoint...")
    
    try:
        topic_response = requests.get(f"{BASE_URL}/api/roadmap/topic/{topic_id}", headers=headers)
        print(f"📡 Response status: {topic_response.status_code}")
        
        if topic_response.status_code != 200:
            print(f"❌ Topic detail failed: {topic_response.status_code}")
            print(f"Response: {topic_response.text}")
            return False
        
        topic_result = topic_response.json()
        print(f"📄 Response: {json.dumps(topic_result, indent=2)[:500]}...")
        
        if not topic_result.get("success"):
            print(f"❌ Topic detail failed: {topic_result.get('error')}")
            print(f"Details: {topic_result.get('details')}")
            return False
        
        # Validate response structure
        topic = topic_result.get("topic", {})
        coding_questions = topic_result.get("coding_questions", [])
        mcq_questions = topic_result.get("mcq_questions", [])
        
        print(f"✅ Topic detail successful:")
        print(f"   - Topic: {topic.get('title')}")
        print(f"   - Coding questions: {len(coding_questions)}")
        print(f"   - MCQ questions: {len(mcq_questions)}")
        
        if len(coding_questions) >= 5 and len(mcq_questions) >= 5:
            print("✅ Question counts are valid")
        else:
            print(f"⚠️ Question counts may be low")
        
        return True
        
    except Exception as e:
        print(f"❌ Topic detail error: {e}")
        return False
    
    # Step 4: Test the test_generate endpoint
    print("4. Testing test_generate endpoint...")
    
    try:
        test_gen_response = requests.get(f"{BASE_URL}/api/roadmap/topic/test_generate/{topic_id}", headers=headers)
        print(f"📡 Test generate response status: {test_gen_response.status_code}")
        
        if test_gen_response.status_code != 200:
            print(f"❌ Test generate failed: {test_gen_response.status_code}")
            print(f"Response: {test_gen_response.text}")
            return False
        
        test_gen_result = test_gen_response.json()
        
        if not test_gen_result.get("success"):
            print(f"❌ Test generate failed: {test_gen_result.get('error')}")
            return False
        
        print(f"✅ Test generate successful:")
        print(f"   - Topic: {test_gen_result.get('topic_title')}")
        print(f"   - Coding questions: {test_gen_result.get('coding_questions_count')}")
        print(f"   - MCQ questions: {test_gen_result.get('mcq_questions_count')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test generate error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Topic Endpoint Tests")
    print("Make sure the Flask backend is running on localhost:5000")
    print()
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Backend server is not responding")
            sys.exit(1)
        print("✅ Backend server is running")
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("Make sure to start the Flask backend first:")
        print("cd backend && python app.py")
        sys.exit(1)
    
    # Run tests
    success = test_topic_endpoint()
    
    print()
    print("=" * 50)
    if success:
        print("🎉 All tests passed! Topic endpoint is working correctly.")
        print()
        print("Next steps:")
        print("1. Try clicking a roadmap topic in the frontend")
        print("2. The topic detail page should load without 500 errors")
        print("3. You should see coding questions and MCQ questions")
    else:
        print("❌ Tests failed. Check the backend logs for more details.")
        print()
        print("Troubleshooting:")
        print("1. Make sure you have a test user registered")
        print("2. Make sure the user has completed the skill assessment")
        print("3. Check backend console for detailed error logs")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)