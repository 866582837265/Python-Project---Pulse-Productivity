#!/usr/bin/env python3
"""
Quick test to verify backend is running and endpoints are accessible
"""

import requests
import json

def quick_test():
    base_url = "http://localhost:5000"
    
    print("Quick API Test")
    print("=" * 30)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("Backend is running!")
            return True
        else:
            print("Backend returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("Backend is not running or not accessible")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if quick_test():
        print("\nBackend is ready for testing!")
    else:
        print("\nPlease start the backend first:")
        print("cd backend && python app.py")