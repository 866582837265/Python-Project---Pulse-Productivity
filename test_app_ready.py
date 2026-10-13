#!/usr/bin/env python3
"""
Test script to verify if the Pulse app is ready to run
"""
import sys
import os
import requests
import time
import subprocess
import threading

def test_backend_import():
    """Test if backend can be imported without errors"""
    try:
        sys.path.append('backend')
        import app
        print("[PASS] Backend imports successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Backend import failed: {e}")
        return False

def test_backend_routes():
    """Test if backend has required routes"""
    try:
        sys.path.append('backend')
        import app
        
        # Check if app has required routes
        routes = []
        for rule in app.app.url_map.iter_rules():
            routes.append(str(rule))
        
        required_routes = [
            '/api/auth/register',
            '/api/auth/login', 
            '/api/dashboard',
            '/api/user/profile'
        ]
        
        missing_routes = []
        for route in required_routes:
            if not any(route in r for r in routes):
                missing_routes.append(route)
        
        if missing_routes:
            print(f"[FAIL] Missing routes: {missing_routes}")
            return False
        else:
            print("[PASS] All required routes are available")
            return True
            
    except Exception as e:
        print(f"[FAIL] Route check failed: {e}")
        return False

def test_frontend_build():
    """Test if frontend can build"""
    try:
        os.chdir('frontend')
        result = subprocess.run(['npm', 'run', 'build'], 
                              capture_output=True, text=True, timeout=60)
        os.chdir('..')
        
        if result.returncode == 0:
            print("[PASS] Frontend builds successfully")
            return True
        else:
            print(f"[FAIL] Frontend build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[FAIL] Frontend build test failed: {e}")
        return False

def main():
    print("[TEST] Testing Pulse App Readiness")
    print("=" * 40)
    
    tests = [
        ("Backend Import", test_backend_import),
        ("Backend Routes", test_backend_routes),
        ("Frontend Build", test_frontend_build)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[TEST] Testing {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"[RESULT] Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] Application is ready to run!")
        print("\n[INFO] To start the application:")
        print("1. Backend: cd backend && python app.py")
        print("2. Frontend: cd frontend && npm run dev")
        return True
    else:
        print("[ERROR] Application has issues that need to be fixed")
        return False

if __name__ == "__main__":
    main()