# pulse/backend/routes/roadmap.py
from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os

roadmap_bp = Blueprint('roadmap', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(token, os.getenv('JWT_SECRET', 'fallback-secret-key'), algorithms=['HS256'])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalid'}), 401
        
        return f(*args, **kwargs)
    return decorated

@roadmap_bp.route('/api/roadmap', methods=['GET'])
@token_required
def get_roadmap():
    """Get user's personalized roadmap"""
    try:
        from app import users_collection, in_memory_users
        user_email = request.current_user["email"]
        
        user = None
        if users_collection:
            user = users_collection.find_one({"email": user_email})
        else:
            user = in_memory_users.get(user_email)
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        skill_level = user.get("skill_level", "Beginner")
        
        # Generate roadmap using ML model
        try:
            from ml_routes import get_personalized_roadmap
            roadmap = get_personalized_roadmap(skill_level)
        except Exception as e:
            print(f"ML roadmap generation failed: {e}")
            # Fallback roadmap
            roadmap = get_default_roadmap(skill_level)
        
        return jsonify({
            "success": True,
            "roadmap": roadmap,
            "skill_level": skill_level
        }), 200
        
    except Exception as e:
        print(f"Get roadmap error: {e}")
        return jsonify({"success": False, "message": "Failed to retrieve roadmap"}), 500

@roadmap_bp.route('/api/roadmap/progress', methods=['POST'])
@token_required
def update_roadmap_progress():
    """Update progress on a roadmap topic"""
    try:
        from app import users_collection, in_memory_users
        user_email = request.current_user["email"]
        data = request.get_json()
        
        topic_id = data.get("topic_id")
        progress = data.get("progress", 0)  # 0-100
        completed = data.get("completed", False)
        
        if not topic_id:
            return jsonify({"success": False, "message": "Topic ID required"}), 400
        
        if users_collection:
            # Update MongoDB
            users_collection.update_one(
                {"email": user_email},
                {"$set": {f"roadmap_progress.{topic_id}": {"progress": progress, "completed": completed}}}
            )
        else:
            # Update in-memory storage
            user = in_memory_users.get(user_email)
            if not user:
                return jsonify({"success": False, "message": "User not found"}), 404
            
            if "roadmap_progress" not in user:
                user["roadmap_progress"] = {}
            user["roadmap_progress"][topic_id] = {"progress": progress, "completed": completed}
        
        return jsonify({
            "success": True,
            "message": "Progress updated successfully"
        }), 200
        
    except Exception as e:
        print(f"Update roadmap progress error: {e}")
        return jsonify({"success": False, "message": "Failed to update progress"}), 500

def get_default_roadmap(skill_level):
    """Fallback roadmap when ML model is unavailable"""
    roadmaps = {
        "Beginner": [
            {
                "id": 1,
                "title": "Arrays & Strings",
                "description": "Master fundamental data structures",
                "topics": ["Two Pointers", "Sliding Window", "Basic Operations"],
                "difficulty": "Beginner",
                "estimated_time": "2-3 weeks",
                "priority": "high"
            },
            {
                "id": 2,
                "title": "Basic Algorithms",
                "description": "Introduction to algorithmic thinking",
                "topics": ["Linear Search", "Simple Sorting", "Basic Recursion"],
                "difficulty": "Beginner",
                "estimated_time": "2-3 weeks",
                "priority": "medium"
            }
        ],
        "Learning": [
            {
                "id": 1,
                "title": "Advanced Arrays",
                "description": "Complex array manipulation techniques",
                "topics": ["Prefix Sum", "Binary Search", "Advanced Two Pointers"],
                "difficulty": "Intermediate",
                "estimated_time": "3-4 weeks",
                "priority": "high"
            },
            {
                "id": 2,
                "title": "Trees & Graphs",
                "description": "Hierarchical and network data structures",
                "topics": ["Binary Trees", "DFS/BFS", "Tree Traversals"],
                "difficulty": "Intermediate",
                "estimated_time": "4-5 weeks",
                "priority": "high"
            }
        ],
        "Expert": [
            {
                "id": 1,
                "title": "Dynamic Programming",
                "description": "Advanced optimization techniques",
                "topics": ["1D DP", "2D DP", "State Machines"],
                "difficulty": "Advanced",
                "estimated_time": "4-6 weeks",
                "priority": "high"
            },
            {
                "id": 2,
                "title": "Advanced Algorithms",
                "description": "Complex problem-solving techniques",
                "topics": ["Greedy", "Backtracking", "Divide & Conquer"],
                "difficulty": "Advanced",
                "estimated_time": "3-4 weeks",
                "priority": "medium"
            }
        ]
    }
    
    return roadmaps.get(skill_level, roadmaps["Beginner"])