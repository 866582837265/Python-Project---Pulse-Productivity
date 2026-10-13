# debug_api.py - Simple API debugging script
import requests
import json

def test_platform_apis():
    """Test the platform APIs directly"""
    
    # Test LeetCode API
    print("Testing LeetCode API...")
    try:
        url = "https://leetcode.com/graphql"
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                submitStats: submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
                profile {
                    ranking
                }
            }
        }
        """
        
        response = requests.post(url, json={
            'query': query,
            'variables': {'username': 'leetcode'}
        }, timeout=10)
        
        print(f"LeetCode API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"LeetCode Response: {json.dumps(data, indent=2)}")
        else:
            print(f"LeetCode Error: {response.text}")
            
    except Exception as e:
        print(f"LeetCode API Error: {e}")
    
    # Test HackerRank API
    print("\nTesting HackerRank API...")
    try:
        url = "https://www.hackerrank.com/rest/hackers/shashank21j/scores"
        response = requests.get(url, timeout=10)
        
        print(f"HackerRank API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"HackerRank Response: {json.dumps(data, indent=2)}")
        else:
            print(f"HackerRank Error: {response.text}")
            
    except Exception as e:
        print(f"HackerRank API Error: {e}")

if __name__ == "__main__":
    test_platform_apis()