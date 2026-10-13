# test_platform_integration.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coding_platforms import CodingPlatformTracker
from progress_sync_service import ProgressSyncService
import json

def test_leetcode_integration():
    """Test LeetCode API integration"""
    print("🔍 Testing LeetCode Integration...")
    
    tracker = CodingPlatformTracker()
    
    # Test with a known LeetCode username (you can replace with any public username)
    test_username = "leetcode"  # LeetCode's official account
    
    try:
        # Test basic stats
        basic_stats = tracker.get_leetcode_stats(test_username)
        print(f"✅ Basic LeetCode stats: {json.dumps(basic_stats, indent=2)}")
        
        # Test enhanced stats
        enhanced_stats = tracker.get_enhanced_leetcode_stats(test_username)
        print(f"✅ Enhanced LeetCode stats: {json.dumps(enhanced_stats, indent=2)}")
        
        return True
    except Exception as e:
        print(f"❌ LeetCode integration failed: {e}")
        return False

def test_hackerrank_integration():
    """Test HackerRank API integration"""
    print("\n🔍 Testing HackerRank Integration...")
    
    tracker = CodingPlatformTracker()
    
    # Test with a known HackerRank username
    test_username = "shashank21j"  # HackerRank CEO's account
    
    try:
        # Test basic stats
        basic_stats = tracker.get_hackerrank_stats(test_username)
        print(f"✅ Basic HackerRank stats: {json.dumps(basic_stats, indent=2)}")
        
        # Test enhanced stats
        enhanced_stats = tracker.get_enhanced_hackerrank_stats(test_username)
        print(f"✅ Enhanced HackerRank stats: {json.dumps(enhanced_stats, indent=2)}")
        
        return True
    except Exception as e:
        print(f"❌ HackerRank integration failed: {e}")
        return False

def test_combined_stats():
    """Test combined statistics from both platforms"""
    print("\n🔍 Testing Combined Statistics...")
    
    tracker = CodingPlatformTracker()
    
    try:
        combined_stats = tracker.get_combined_stats(
            leetcode_username="leetcode",
            hackerrank_username="shashank21j"
        )
        print(f"✅ Combined stats: {json.dumps(combined_stats, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Combined stats failed: {e}")
        return False

def test_progress_insights():
    """Test progress insights generation"""
    print("\n🔍 Testing Progress Insights...")
    
    tracker = CodingPlatformTracker()
    
    # Mock current and previous stats for testing
    current_stats = {
        "leetcode": {
            "solved": 150,
            "weekly_solved": 5
        },
        "hackerrank": {
            "stars": 4
        }
    }
    
    previous_stats = {
        "leetcode": {
            "solved": 140,
            "weekly_solved": 2
        },
        "hackerrank": {
            "stars": 3
        }
    }
    
    try:
        insights = tracker.get_progress_insights(current_stats, previous_stats)
        print(f"✅ Progress insights: {json.dumps(insights, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Progress insights failed: {e}")
        return False

def test_sync_service():
    """Test the progress sync service"""
    print("\n🔍 Testing Progress Sync Service...")
    
    try:
        # Create a mock sync service
        sync_service = ProgressSyncService()
        
        # Test sync status
        status = sync_service.get_sync_status()
        print(f"✅ Sync service status: {json.dumps(status, indent=2)}")
        
        return True
    except Exception as e:
        print(f"❌ Sync service test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Platform Integration Tests...\n")
    
    tests = [
        ("LeetCode Integration", test_leetcode_integration),
        ("HackerRank Integration", test_hackerrank_integration),
        ("Combined Statistics", test_combined_stats),
        ("Progress Insights", test_progress_insights),
        ("Sync Service", test_sync_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Platform integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)