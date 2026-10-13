import uuid
from datetime import datetime, timezone

def generate_roadmap(level: str) -> list:
    """Generate roadmap by user level"""
    topics = {
        "Beginner": ["Arrays", "Strings", "Recursion", "Sorting"],
        "Intermediate": ["Linked Lists", "Stacks & Queues", "Trees", "Graphs"],
        "Expert": ["Dynamic Programming", "Greedy", "Segment Trees", "Advanced Graphs"]
    }
    
    roadmap = []
    for i, topic in enumerate(topics.get(level, []), start=1):
        roadmap.append({
            "id": str(uuid.uuid4()),
            "title": topic,
            "order": i,
            "difficulty": level,
            "status": "unlocked" if i == 1 else "locked",
            "resources": [],
            "practice_questions": [],
            "questionPackId": None
        })
    return roadmap

# Keep the comprehensive roadmaps as backup
def generate_comprehensive_roadmap(level: str) -> list:
    """Generate comprehensive Duolingo-style progressive roadmap nodes"""
    
    roadmaps = {
        "Beginner": [
            {"id": str(uuid.uuid4()), "order": 1, "title": "Arrays Basics", "difficulty": "Beginner", 
             "description": "Learn array fundamentals and basic operations", 
             "resources": ["https://leetcode.com/tag/array/", "https://www.geeksforgeeks.org/array-data-structure/"], 
             "status": "unlocked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 2, "title": "String Manipulation", "difficulty": "Beginner", 
             "description": "Master string operations and pattern matching", 
             "resources": ["https://leetcode.com/tag/string/", "https://www.geeksforgeeks.org/string-data-structure/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 3, "title": "Basic Loops", "difficulty": "Beginner", 
             "description": "Understand iteration and loop patterns", 
             "resources": ["https://www.geeksforgeeks.org/loops-in-c-cpp/", "https://leetcode.com/tag/simulation/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 4, "title": "Simple Recursion", "difficulty": "Beginner", 
             "description": "Introduction to recursive thinking", 
             "resources": ["https://leetcode.com/tag/recursion/", "https://www.geeksforgeeks.org/recursion/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 5, "title": "Linear Search", "difficulty": "Beginner", 
             "description": "Basic searching algorithms", 
             "resources": ["https://www.geeksforgeeks.org/linear-search/", "https://leetcode.com/problems/search-insert-position/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 6, "title": "Bubble Sort", "difficulty": "Beginner", 
             "description": "Understanding basic sorting", 
             "resources": ["https://www.geeksforgeeks.org/bubble-sort/", "https://leetcode.com/problems/sort-colors/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 7, "title": "Two Pointers", "difficulty": "Beginner", 
             "description": "Efficient array traversal technique", 
             "resources": ["https://leetcode.com/tag/two-pointers/", "https://www.geeksforgeeks.org/two-pointers-technique/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 8, "title": "Hash Maps", "difficulty": "Beginner", 
             "description": "Key-value data structures", 
             "resources": ["https://leetcode.com/tag/hash-table/", "https://www.geeksforgeeks.org/hashing-data-structure/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 9, "title": "Stack Basics", "difficulty": "Beginner", 
             "description": "LIFO data structure fundamentals", 
             "resources": ["https://leetcode.com/tag/stack/", "https://www.geeksforgeeks.org/stack-data-structure/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 10, "title": "Queue Basics", "difficulty": "Beginner", 
             "description": "FIFO data structure fundamentals", 
             "resources": ["https://leetcode.com/tag/queue/", "https://www.geeksforgeeks.org/queue-data-structure/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 11, "title": "Binary Search", "difficulty": "Beginner", 
             "description": "Efficient searching in sorted arrays", 
             "resources": ["https://leetcode.com/tag/binary-search/", "https://www.geeksforgeeks.org/binary-search/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 12, "title": "Linked Lists", "difficulty": "Beginner", 
             "description": "Dynamic data structures", 
             "resources": ["https://leetcode.com/tag/linked-list/", "https://www.geeksforgeeks.org/data-structures/linked-list/"], 
             "status": "locked", "questionPackId": None}
        ],
        
        "Intermediate": [
            {"id": str(uuid.uuid4()), "order": 1, "title": "Advanced Recursion", "difficulty": "Intermediate", 
             "description": "Complex recursive patterns and backtracking", 
             "resources": ["https://leetcode.com/tag/backtracking/", "https://www.geeksforgeeks.org/backtracking-algorithms/"], 
             "status": "unlocked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 2, "title": "Binary Trees", "difficulty": "Intermediate", 
             "description": "Tree data structures and traversals", 
             "resources": ["https://leetcode.com/tag/binary-tree/", "https://www.geeksforgeeks.org/binary-tree-data-structure/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 3, "title": "Binary Search Trees", "difficulty": "Intermediate", 
             "description": "Ordered tree structures", 
             "resources": ["https://leetcode.com/tag/binary-search-tree/", "https://www.geeksforgeeks.org/binary-search-tree-data-structure/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 4, "title": "Heaps", "difficulty": "Intermediate", 
             "description": "Priority queue data structures", 
             "resources": ["https://leetcode.com/tag/heap-priority-queue/", "https://www.geeksforgeeks.org/heap-data-structure/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 5, "title": "Graph Basics", "difficulty": "Intermediate", 
             "description": "Graph representation and traversal", 
             "resources": ["https://leetcode.com/tag/graph/", "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 6, "title": "DFS & BFS", "difficulty": "Intermediate", 
             "description": "Graph traversal algorithms", 
             "resources": ["https://leetcode.com/tag/depth-first-search/", "https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 7, "title": "Dynamic Programming", "difficulty": "Intermediate", 
             "description": "Optimization using memoization", 
             "resources": ["https://leetcode.com/tag/dynamic-programming/", "https://www.geeksforgeeks.org/dynamic-programming/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 8, "title": "Greedy Algorithms", "difficulty": "Intermediate", 
             "description": "Local optimization strategies", 
             "resources": ["https://leetcode.com/tag/greedy/", "https://www.geeksforgeeks.org/greedy-algorithms/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 9, "title": "Sliding Window", "difficulty": "Intermediate", 
             "description": "Efficient subarray processing", 
             "resources": ["https://leetcode.com/tag/sliding-window/", "https://www.geeksforgeeks.org/window-sliding-technique/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 10, "title": "Merge Sort", "difficulty": "Intermediate", 
             "description": "Divide and conquer sorting", 
             "resources": ["https://www.geeksforgeeks.org/merge-sort/", "https://leetcode.com/problems/sort-an-array/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 11, "title": "Quick Sort", "difficulty": "Intermediate", 
             "description": "Efficient in-place sorting", 
             "resources": ["https://www.geeksforgeeks.org/quick-sort/", "https://leetcode.com/problems/kth-largest-element-in-an-array/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 12, "title": "Trie Data Structure", "difficulty": "Intermediate", 
             "description": "Prefix tree for string operations", 
             "resources": ["https://leetcode.com/tag/trie/", "https://www.geeksforgeeks.org/trie-insert-and-search/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 13, "title": "Union Find", "difficulty": "Intermediate", 
             "description": "Disjoint set data structure", 
             "resources": ["https://leetcode.com/tag/union-find/", "https://www.geeksforgeeks.org/union-find/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 14, "title": "Topological Sort", "difficulty": "Intermediate", 
             "description": "Ordering of directed graphs", 
             "resources": ["https://leetcode.com/tag/topological-sort/", "https://www.geeksforgeeks.org/topological-sorting/"], 
             "status": "locked", "questionPackId": None}
        ],
        
        "Expert": [
            {"id": str(uuid.uuid4()), "order": 1, "title": "Advanced DP", "difficulty": "Expert", 
             "description": "Complex dynamic programming patterns", 
             "resources": ["https://leetcode.com/tag/dynamic-programming/", "https://www.geeksforgeeks.org/advanced-dynamic-programming/"], 
             "status": "unlocked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 2, "title": "Segment Trees", "difficulty": "Expert", 
             "description": "Range query data structures", 
             "resources": ["https://leetcode.com/tag/segment-tree/", "https://www.geeksforgeeks.org/segment-tree-set-1-sum-of-given-range/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 3, "title": "Fenwick Tree", "difficulty": "Expert", 
             "description": "Binary indexed trees", 
             "resources": ["https://www.geeksforgeeks.org/binary-indexed-tree-or-fenwick-tree-2/", "https://leetcode.com/problems/range-sum-query-mutable/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 4, "title": "Advanced Graph", "difficulty": "Expert", 
             "description": "Shortest paths and MST", 
             "resources": ["https://leetcode.com/tag/shortest-path/", "https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 5, "title": "Network Flow", "difficulty": "Expert", 
             "description": "Maximum flow algorithms", 
             "resources": ["https://www.geeksforgeeks.org/max-flow-problem-introduction/", "https://leetcode.com/problems/maximum-flow/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 6, "title": "String Algorithms", "difficulty": "Expert", 
             "description": "KMP, Z-algorithm, suffix arrays", 
             "resources": ["https://www.geeksforgeeks.org/kmp-algorithm-for-pattern-searching/", "https://leetcode.com/tag/string-matching/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 7, "title": "Computational Geometry", "difficulty": "Expert", 
             "description": "Geometric algorithms", 
             "resources": ["https://www.geeksforgeeks.org/computational-geometry-set-1-orientation-of-an-ordered-triplet-of-points/", "https://leetcode.com/tag/geometry/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 8, "title": "Game Theory", "difficulty": "Expert", 
             "description": "Minimax and optimal strategies", 
             "resources": ["https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-1-introduction/", "https://leetcode.com/tag/game-theory/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 9, "title": "Number Theory", "difficulty": "Expert", 
             "description": "Prime numbers, modular arithmetic", 
             "resources": ["https://www.geeksforgeeks.org/mathematical-algorithms/", "https://leetcode.com/tag/math/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 10, "title": "Bit Manipulation", "difficulty": "Expert", 
             "description": "Advanced bitwise operations", 
             "resources": ["https://leetcode.com/tag/bit-manipulation/", "https://www.geeksforgeeks.org/bit-algorithms/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 11, "title": "Heavy-Light Decomposition", "difficulty": "Expert", 
             "description": "Tree decomposition techniques", 
             "resources": ["https://www.geeksforgeeks.org/heavy-light-decomposition-set-1-introduction/", "https://codeforces.com/blog/entry/22072"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 12, "title": "Suffix Data Structures", "difficulty": "Expert", 
             "description": "Suffix trees and arrays", 
             "resources": ["https://www.geeksforgeeks.org/suffix-tree-application-1-substring-check/", "https://leetcode.com/problems/shortest-superstring/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 13, "title": "Advanced Data Structures", "difficulty": "Expert", 
             "description": "Splay trees, treaps, persistent structures", 
             "resources": ["https://www.geeksforgeeks.org/splay-tree-set-1-insert/", "https://codeforces.com/blog/entry/15729"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 14, "title": "Approximation Algorithms", "difficulty": "Expert", 
             "description": "NP-hard problem approximations", 
             "resources": ["https://www.geeksforgeeks.org/approximation-algorithms/", "https://en.wikipedia.org/wiki/Approximation_algorithm"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 15, "title": "Randomized Algorithms", "difficulty": "Expert", 
             "description": "Monte Carlo and Las Vegas algorithms", 
             "resources": ["https://www.geeksforgeeks.org/randomized-algorithms/", "https://leetcode.com/problems/random-pick-index/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 16, "title": "Parallel Algorithms", "difficulty": "Expert", 
             "description": "Concurrent and parallel processing", 
             "resources": ["https://www.geeksforgeeks.org/parallel-algorithms/", "https://leetcode.com/problems/web-crawler-multithreaded/"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 17, "title": "Advanced Optimization", "difficulty": "Expert", 
             "description": "Linear programming, convex optimization", 
             "resources": ["https://www.geeksforgeeks.org/linear-programming/", "https://en.wikipedia.org/wiki/Convex_optimization"], 
             "status": "locked", "questionPackId": None},
            {"id": str(uuid.uuid4()), "order": 18, "title": "Competitive Programming", "difficulty": "Expert", 
             "description": "Contest strategies and advanced techniques", 
             "resources": ["https://codeforces.com/", "https://www.topcoder.com/"], 
             "status": "locked", "questionPackId": None}
        ]
    }
    
    return roadmaps.get(level, roadmaps["Beginner"])

def unlock_next_topic(roadmap, completed_topic_id):
    """Unlock next topic after completing current one"""
    if not isinstance(roadmap, list):
        return roadmap
    
    # Find completed topic and mark as completed
    for i, topic in enumerate(roadmap):
        if topic.get("id") == completed_topic_id:
            topic["status"] = "completed"
            # Unlock next topic if exists
            if i + 1 < len(roadmap):
                roadmap[i + 1]["status"] = "unlocked"
            break
    
    return roadmap