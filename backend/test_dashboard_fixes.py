#!/usr/bin/env python3
"""
Test script to verify dashboard fixes and roadmap loading
"""

import requests
import json
from dashboard_service import DashboardService, CodingPlatformService
from roadmap_agent import roadmap_agent

def test_roadmap_generation():
    """Test roadmap generation"""
    print("[TEST] Testing roadmap generation...")
    
    for level in ["Beginner", "Intermediate", "Expert"]:
        try:
            roadmap = roadmap_agent.generate_roadmap(level)
            
            if roadmap and isinstance(roadmap, dict):
                print(f"[SUCCESS] {level} roadmap generated")
                print(f"   - Topics: {roadmap.get('total_topics', 0)}")
                print(f"   - Hours: {roadmap.get('estimated_total_hours', 0)}")
                
                # Test JSON serialization
                json.dumps(roadmap)
                print(f"   - JSON serializable: OK")
            else:
                print(f"[ERROR] {level} roadmap generation failed")
                
        except Exception as e:
            print(f"[ERROR] {level} roadmap error: {e}")

def test_dashboard_service():
    """Test dashboard service calculations"""
    print("\n[TEST] Testing dashboard service...")
    
    # Test with None collections (fallback mode)
    service = DashboardService(None, None)
    
    # Test Pomodoro calculation
    pomodoro = service.calculate_pomodoro_stats("test@example.com")
    print(f"[SUCCESS] Pomodoro stats: {pomodoro}")
    
    # Test streak calculation
    streak = service.calculate_streak("test@example.com")
    print(f"[SUCCESS] Streak stats: {streak}")
    
    # Test roadmap progress
    progress = service.calculate_roadmap_progress("test@example.com")
    print(f"[SUCCESS] Roadmap progress: {progress}")

def test_coding_platform_service():
    """Test coding platform service"""
    print("\n[TEST] Testing coding platform service...")
    
    service = CodingPlatformService(None)
    
    # Test simulated data
    hackerrank = service.fetch_hackerrank_stats("testuser")
    print(f"[SUCCESS] HackerRank stats: {hackerrank}")
    
    hackerearth = service.fetch_hackerearth_stats("testuser")
    print(f"[SUCCESS] HackerEarth stats: {hackerearth}")

def test_api_endpoints():
    """Test API endpoints if server is running"""
    print("\n[TEST] Testing API endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("[SUCCESS] Health endpoint working")
        else:
            print(f"[ERROR] Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"[INFO] Server not running: {e}")
        return
    
    # Test roadmap test endpoints
    for level in ["Beginner", "Intermediate", "Expert"]:
        try:
            response = requests.get(f"{base_url}/api/roadmap/test/{level}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('roadmap'):
                    print(f"[SUCCESS] {level} test endpoint working")
                else:
                    print(f"[ERROR] {level} test endpoint returned invalid data")
            else:
                print(f"[ERROR] {level} test endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {level} test endpoint error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("DASHBOARD FIXES VERIFICATION TEST")
    print("=" * 60)
    
    test_roadmap_generation()
    test_dashboard_service()
    test_coding_platform_service()
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
    print("\nTo test the full system:")
    print("1. Start Flask server: python app.py")
    print("2. Start React frontend: npm run dev")
    print("3. Register/login and test dashboard features")