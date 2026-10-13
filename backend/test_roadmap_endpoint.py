#!/usr/bin/env python3
"""
Test the roadmap endpoint directly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, generate_adaptive_roadmap, in_memory_users
from roadmap_agent import roadmap_agent

def test_roadmap_endpoint():
    """Test roadmap endpoint functionality"""
    print("=== TESTING ROADMAP ENDPOINT ===")
    
    # Create a test user in memory
    test_email = "test@example.com"
    in_memory_users[test_email] = {
        "_id": "test_user_123",
        "email": test_email,
        "username": "Test User",
        "assessment_taken": False,
        "predicted_level": "Beginner"
    }
    
    print(f"Created test user: {test_email}")
    
    # Test roadmap generation
    print("Testing roadmap generation...")
    roadmap = generate_adaptive_roadmap(test_email, "Beginner")
    
    if roadmap:
        print(f"[SUCCESS] Generated roadmap with {roadmap.get('total_topics', 0)} topics")
        print(f"[INFO] Level: {roadmap.get('level')}")
        print(f"[INFO] Topics count: {len(roadmap.get('topics', []))}")
        
        if roadmap.get('topics'):
            first_topic = roadmap['topics'][0]
            print(f"[INFO] First topic: {first_topic.get('title')}")
            print(f"[INFO] First topic status: {first_topic.get('status')}")
        
        # Check if user now has roadmap
        user = in_memory_users.get(test_email)
        print(f"[DEBUG] User data keys: {list(user.keys()) if user else 'No user found'}")
        if user and user.get('roadmap'):
            print("[SUCCESS] Roadmap saved to user record")
            print(f"[INFO] User roadmap has {user['roadmap'].get('total_topics', 0)} topics")
        else:
            print("[ERROR] Roadmap not saved to user record")
            
    else:
        print("[ERROR] Failed to generate roadmap")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_roadmap_endpoint()