#!/usr/bin/env python3
"""
Test script to verify roadmap generation works correctly
"""

from roadmap_agent import roadmap_agent
import json

def test_roadmap_generation():
    """Test roadmap generation for all levels"""
    levels = ["Beginner", "Intermediate", "Expert"]
    
    print("[TEST] Testing Roadmap Generation")
    print("=" * 50)
    
    for level in levels:
        print(f"\n[TEST] Testing {level} level roadmap...")
        
        try:
            roadmap = roadmap_agent.generate_roadmap(level)
            
            if roadmap:
                print(f"[SUCCESS] {level} roadmap generated successfully!")
                print(f"   - Level: {roadmap.get('level')}")
                print(f"   - Total Topics: {roadmap.get('total_topics')}")
                print(f"   - Estimated Hours: {roadmap.get('estimated_total_hours')}")
                print(f"   - Topics Count: {len(roadmap.get('topics', []))}")
                
                # Check if roadmap is JSON serializable
                try:
                    json.dumps(roadmap)
                    print(f"   - JSON Serializable: [OK]")
                except Exception as e:
                    print(f"   - JSON Serializable: [ERROR] ({e})")
                
                # Show first topic as example
                topics = roadmap.get('topics', [])
                if topics:
                    first_topic = topics[0]
                    print(f"   - First Topic: {first_topic.get('title')}")
                    print(f"   - Status: {first_topic.get('status')}")
                
            else:
                print(f"[ERROR] {level} roadmap generation failed!")
                
        except Exception as e:
            print(f"[ERROR] {level} roadmap generation error: {e}")
    
    print("\n" + "=" * 50)
    print("[COMPLETE] Roadmap generation test completed!")

if __name__ == "__main__":
    test_roadmap_generation()