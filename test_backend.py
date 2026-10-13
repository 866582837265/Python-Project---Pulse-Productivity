#!/usr/bin/env python3
"""
Simple test script to verify backend API endpoints are working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_roadmap_generation():
    """Test roadmap generation for different levels"""
    levels = ["Beginner", "Intermediate", "Expert"]
    
    for level in levels:
        try:
            response = requests.get(f"{BASE_URL}/api/roadmap/test/{level}")
            print(f"\nRoadmap test for {level}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Success: {data.get('success')}")
                print(f"Level: {data.get('level')}")
                print(f"Roadmap items: {data.get('count', 0)}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Roadmap test for {level} failed: {e}")

def main():
    print("Testing Pulse Backend API...")
    print("=" * 50)
    
    # Test health endpoint
    if test_health():
        print("✅ Backend is running")
    else:
        print("❌ Backend is not responding")
        return
    
    # Test roadmap generation
    print("\nTesting roadmap generation...")
    test_roadmap_generation()
    
    print("\n" + "=" * 50)
    print("Backend test completed!")

if __name__ == "__main__":
    main()