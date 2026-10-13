#!/usr/bin/env python3
"""
Test script to debug platform integration issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from coding_platforms import CodingPlatformTracker

def test_platform_integration():
    """Test platform integration with various usernames"""
    
    tracker = CodingPlatformTracker()
    
    # Test usernames - common ones that should exist
    test_usernames = [
        "leetcode",  # Official LeetCode account
        "admin",     # Common admin account
        "test",      # Common test account
        "user",      # Generic user
        "demo",      # Demo account
        "sample",    # Sample account
        "example",   # Example account
        "rajesh",    # Your username
        "rajes",     # Shortened version
    ]
    
    print("🔍 Testing LeetCode Integration:")
    print("=" * 50)
    
    for username in test_usernames:
        print(f"\n📊 Testing username: {username}")
        try:
            result = tracker.get_leetcode_stats(username)
            if result and result.get('success'):
                print(f"✅ SUCCESS: {username}")
                print(f"   Total problems: {result['solved_problems']['total']}")
                print(f"   Demo data: {result.get('demo_data', False)}")
                if not result.get('demo_data'):
                    print(f"   🎉 REAL DATA FOUND!")
                    break
            else:
                print(f"❌ FAILED: {username}")
        except Exception as e:
            print(f"💥 ERROR: {username} - {e}")
    
    print("\n🔍 Testing HackerRank Integration:")
    print("=" * 50)
    
    for username in test_usernames:
        print(f"\n📊 Testing username: {username}")
        try:
            result = tracker.get_hackerrank_stats(username)
            if result and result.get('success'):
                print(f"✅ SUCCESS: {username}")
                print(f"   Total score: {result['scores']['total_score']}")
                print(f"   Demo data: {result.get('demo_data', False)}")
                if not result.get('demo_data'):
                    print(f"   🎉 REAL DATA FOUND!")
                    break
            else:
                print(f"❌ FAILED: {username}")
        except Exception as e:
            print(f"💥 ERROR: {username} - {e}")

def test_specific_user():
    """Test with a specific user that should have data"""
    tracker = CodingPlatformTracker()
    
    # Test with a known LeetCode user
    known_users = [
        "awice",      # Known competitive programmer
        "lee215",     # Popular LeetCode user
        "votrubac",   # Active LeetCode user
        "StefanPochmann",  # Well-known user
    ]
    
    print("\n🎯 Testing with known active users:")
    print("=" * 50)
    
    for username in known_users:
        print(f"\n📊 Testing known user: {username}")
        try:
            result = tracker.get_leetcode_stats(username)
            if result and result.get('success'):
                print(f"✅ SUCCESS: {username}")
                print(f"   Total problems: {result['solved_problems']['total']}")
                print(f"   Easy: {result['solved_problems']['easy']}")
                print(f"   Medium: {result['solved_problems']['medium']}")
                print(f"   Hard: {result['solved_problems']['hard']}")
                print(f"   Demo data: {result.get('demo_data', False)}")
                if not result.get('demo_data'):
                    print(f"   🎉 REAL DATA FOUND FOR {username}!")
                    return username
            else:
                print(f"❌ FAILED: {username}")
        except Exception as e:
            print(f"💥 ERROR: {username} - {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 Starting Platform Integration Test")
    print("=" * 60)
    
    # Test basic integration
    test_platform_integration()
    
    # Test with known users
    working_user = test_specific_user()
    
    if working_user:
        print(f"\n🎉 SOLUTION FOUND!")
        print(f"✅ Working username: {working_user}")
        print(f"💡 Use this username in your profile to see real data!")
    else:
        print(f"\n⚠️  All tests returned demo data")
        print(f"💡 This is expected if APIs are blocked or rate-limited")
        print(f"🔧 The app will work with demo data for development")
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete")