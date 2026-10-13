#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced streak tracking system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, timezone
from streak_service import StreakService

def test_streak_scenarios():
    """Test various streak scenarios"""
    
    print("🔥 Testing Enhanced Streak Tracking System")
    print("=" * 50)
    
    # Mock storage
    in_memory_users = {
        "test@example.com": {
            "current_streak": 0,
            "longest_streak": 0,
            "total_active_days": 0,
            "last_streak_activity": None,
            "streak_history": []
        }
    }
    
    user_email = "test@example.com"
    
    # Test 1: First time activity
    print("\n📅 Test 1: First time activity")
    result = StreakService.update_user_streak(None, in_memory_users, user_email, "login")
    print(f"Result: {result}")
    print(f"Current streak: {in_memory_users[user_email]['current_streak']}")
    
    # Test 2: Same day activity (should not increment)
    print("\n📅 Test 2: Same day activity (should not increment)")
    result = StreakService.update_user_streak(None, in_memory_users, user_email, "practice")
    print(f"Result: {result}")
    print(f"Current streak: {in_memory_users[user_email]['current_streak']}")
    
    # Test 3: Simulate yesterday's activity and today's activity
    print("\n📅 Test 3: Consecutive day activity")
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    in_memory_users[user_email]["last_streak_activity"] = yesterday.isoformat()
    in_memory_users[user_email]["current_streak"] = 1
    
    result = StreakService.update_user_streak(None, in_memory_users, user_email, "practice")
    print(f"Result: {result}")
    print(f"Current streak: {in_memory_users[user_email]['current_streak']}")
    
    # Test 4: Simulate gap in activity (streak should reset)
    print("\n📅 Test 4: Gap in activity (streak should reset)")
    three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
    in_memory_users[user_email]["last_streak_activity"] = three_days_ago.isoformat()
    in_memory_users[user_email]["current_streak"] = 5
    
    result = StreakService.update_user_streak(None, in_memory_users, user_email, "login")
    print(f"Result: {result}")
    print(f"Current streak: {in_memory_users[user_email]['current_streak']}")
    
    # Test 5: Get streak data
    print("\n📊 Test 5: Get comprehensive streak data")
    streak_data = StreakService.get_streak_data(None, in_memory_users, user_email)
    print(f"Streak data: {streak_data}")
    
    # Test 6: Test streak risk calculation
    print("\n⚠️ Test 6: Streak risk scenarios")
    
    # Low risk (active today)
    in_memory_users[user_email]["last_streak_activity"] = datetime.now(timezone.utc).isoformat()
    risk = StreakService._calculate_streak_risk(in_memory_users[user_email]["last_streak_activity"])
    print(f"Active today - Risk: {risk}")
    
    # Medium risk (active yesterday)
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    risk = StreakService._calculate_streak_risk(yesterday.isoformat())
    print(f"Active yesterday - Risk: {risk}")
    
    # High risk (inactive for 2+ days)
    two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)
    risk = StreakService._calculate_streak_risk(two_days_ago.isoformat())
    print(f"Inactive for 2 days - Risk: {risk}")
    
    print("\n✅ All tests completed!")
    print(f"Final user state: {in_memory_users[user_email]}")

def test_edge_cases():
    """Test edge cases and error handling"""
    
    print("\n🧪 Testing Edge Cases")
    print("=" * 30)
    
    in_memory_users = {}
    
    # Test with non-existent user
    result = StreakService.update_user_streak(None, in_memory_users, "nonexistent@example.com", "login")
    print(f"Non-existent user: {result}")
    
    # Test with invalid date format
    in_memory_users["test@example.com"] = {
        "current_streak": 1,
        "last_streak_activity": "invalid-date",
        "streak_history": []
    }
    
    result = StreakService.update_user_streak(None, in_memory_users, "test@example.com", "practice")
    print(f"Invalid date format: {result}")

if __name__ == "__main__":
    test_streak_scenarios()
    test_edge_cases()