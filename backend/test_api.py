#!/usr/bin/env python3
"""
Test script to verify Flask API endpoints work correctly
"""

import requests
import json

def test_roadmap_api():
    """Test the roadmap API endpoint"""
    base_url = "http://localhost:5000"
    
    print("[TEST] Testing Flask API Endpoints")
    print("=" * 50)
    
    # Test health endpoint
    print("\n[TEST] Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("[SUCCESS] Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"[ERROR] Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Health endpoint error: {e}")
    
    # Test roadmap test endpoint
    print("\n[TEST] Testing roadmap test endpoint...")
    for level in ["Beginner", "Intermediate", "Expert"]:
        try:
            response = requests.get(f"{base_url}/api/roadmap/test/{level}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('roadmap'):
                    roadmap = data['roadmap']
                    print(f"[SUCCESS] {level} test endpoint working")
                    print(f"   Topics: {roadmap.get('total_topics', 0)}")
                    print(f"   Hours: {roadmap.get('estimated_total_hours', 0)}")
                else:
                    print(f"[ERROR] {level} test endpoint returned invalid data")
            else:
                print(f"[ERROR] {level} test endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {level} test endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("[COMPLETE] API endpoint test completed!")
    print("\nTo test the protected /api/roadmap endpoint:")
    print("1. Start the Flask server: python app.py")
    print("2. Register/login through the frontend")
    print("3. Use the JWT token to access /api/roadmap")

if __name__ == "__main__":
    test_roadmap_api()