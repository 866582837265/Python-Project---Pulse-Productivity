#!/usr/bin/env python3
"""
Test script to verify the topic lookup and question generation fixes
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_gemini_integration():
    """Test Gemini AI integration"""
    print("🧪 Testing Gemini AI Integration...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/test/gemini/Arrays")
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Gemini Test Passed:")
            print(f"   - API Configured: {data.get('gemini_api_configured')}")
            print(f"   - Coding Questions: {data['content_generated']['coding_questions']}")
            print(f"   - MCQ Questions: {data['content_generated']['mcq_questions']}")
            print(f"   - Total Questions: {data['content_generated']['total_questions']}")
            
            if data['content_generated']['total_questions'] >= 10:
                print("✅ Question count requirement met (5 coding + 5 MCQ)")
            else:
                print("⚠️ Question count below expected (should be 10 total)")
        else:
            print(f"❌ Gemini Test Failed: {data.get('error')}")
            print(f"   - API Configured: {data.get('gemini_api_configured')}")
            
    except Exception as e:
        print(f"❌ Gemini Test Error: {e}")

def test_topic_lookup():
    """Test topic lookup with different formats"""
    print("\n🔍 Testing Topic Lookup...")
    
    # You'll need to login first and get a token
    # This is just a demonstration of the endpoint
    test_topics = [
        "Arrays",
        "arrays", 
        "Arrays Basics",
        "arrays_basics",
        "arrays-basics"
    ]
    
    for topic in test_topics:
        print(f"   Testing topic: '{topic}'")
        # Note: This would require authentication token
        # response = requests.get(f"{BASE_URL}/api/roadmap/topic/{topic}", headers={"Authorization": f"Bearer {token}"})

def main():
    print("🚀 Testing Pulse Backend Fixes")
    print("=" * 50)
    
    # Test server health
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding")
            return
    except:
        print("❌ Cannot connect to backend server")
        print("   Make sure the Flask server is running on localhost:5000")
        return
    
    # Run tests
    test_gemini_integration()
    test_topic_lookup()
    
    print("\n📋 Next Steps:")
    print("1. Get a Gemini API key from https://makersuite.google.com/app/apikey")
    print("2. Add it to your .env file: GEMINI_API_KEY=your-key-here")
    print("3. Restart the Flask server")
    print("4. Test topic lookup by logging in and accessing a topic")

if __name__ == "__main__":
    main()