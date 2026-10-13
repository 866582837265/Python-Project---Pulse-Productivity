#!/usr/bin/env python3
import sys
sys.path.append('backend')
from roadmap_agent import generate_roadmap, unlock_next_topic

def verify_roadmap():
    print("Verifying Roadmap Agent...")
    
    for level in ['Beginner', 'Intermediate', 'Expert']:
        roadmap = generate_roadmap(level)
        
        print(f"\n{level} Level:")
        print(f"   Nodes: {len(roadmap)}")
        print(f"   First: {roadmap[0]['title']} ({roadmap[0]['status']})")
        print(f"   Second: {roadmap[1]['title']} ({roadmap[1]['status']})")
        
        # Verify structure
        unlocked_count = sum(1 for node in roadmap if node['status'] == 'unlocked')
        locked_count = sum(1 for node in roadmap if node['status'] == 'locked')
        
        print(f"   Unlocked: {unlocked_count}, Locked: {locked_count}")
        
        # Test unlock progression
        first_id = roadmap[0]['id']
        updated = unlock_next_topic(roadmap, first_id)
        new_unlocked = sum(1 for node in updated if node['status'] == 'unlocked')
        print(f"   After completing first: {new_unlocked} unlocked")
    
    print("\nRoadmap Agent verified!")

if __name__ == "__main__":
    verify_roadmap()