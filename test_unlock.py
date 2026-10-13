#!/usr/bin/env python3
import sys
sys.path.append('backend')
from roadmap_agent import generate_roadmap, unlock_next_topic

def test_unlock():
    print("Testing unlock progression...")
    
    # Get beginner roadmap
    roadmap = generate_roadmap('Beginner')
    
    print(f"Initial state:")
    for i, node in enumerate(roadmap[:3]):
        print(f"  {i+1}. {node['title']}: {node['status']}")
    
    # Complete first topic
    first_id = roadmap[0]['id']
    updated = unlock_next_topic(roadmap, first_id)
    
    print(f"\nAfter completing '{roadmap[0]['title']}':")
    for i, node in enumerate(updated[:3]):
        print(f"  {i+1}. {node['title']}: {node['status']}")
    
    # Complete second topic
    second_id = updated[1]['id']
    updated2 = unlock_next_topic(updated, second_id)
    
    print(f"\nAfter completing '{updated[1]['title']}':")
    for i, node in enumerate(updated2[:3]):
        print(f"  {i+1}. {node['title']}: {node['status']}")

if __name__ == "__main__":
    test_unlock()