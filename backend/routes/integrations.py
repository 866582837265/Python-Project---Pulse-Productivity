# pulse/backend/routes/integrations.py
from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
import requests
from datetime import datetime, timedelta

integrations_bp = Blueprint('integrations', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(token, os.getenv('JWT_SECRET', 'fallback-secret-key'), algorithms=['HS256'])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token invalid'}), 401
        
        return f(*args, **kwargs)
    return decorated

@integrations_bp.route('/api/integrations/leetcode', methods=['GET', 'OPTIONS'])
@token_required
def get_leetcode_stats():
    """Get LeetCode stats for user"""
    try:
        from app import coding_tracker
        user_email = request.current_user["email"]
        username = request.args.get("username")
        
        if not username:
            return jsonify({"success": False, "error": "Username required"}), 400
        
        print(f"[LEETCODE API] Fetching stats for {username} (requested by {user_email})")
        
        # Use the enhanced tracker
        result = coding_tracker.get_enhanced_leetcode_stats(username)
        
        if result and result.get('success'):
            stats = {
                "problems_solved": result['solved_problems']['total'],
                "easy_solved": result['solved_problems']['easy'],
                "medium_solved": result['solved_problems']['medium'],
                "hard_solved": result['solved_problems']['hard'],
                "ranking": result.get('ranking', 0),
                "weekly_solved": result.get('weekly_solved', 0),
                "last_active": result.get('last_active'),
                "recent_activity": result.get('recent_activity', [])
            }
            
            print(f"[LEETCODE API] Success: {stats['problems_solved']} problems solved")
            
            return jsonify({
                "success": True,
                "stats": stats
            }), 200
        else:
            error_msg = result.get('error', 'Failed to fetch LeetCode stats') if result else 'API returned no data'
            print(f"[LEETCODE API] Failed: {error_msg}")
            
            return jsonify({
                "success": False,
                "error": error_msg
            }), 404
        
    except Exception as e:
        print(f"[LEETCODE API ERROR] {e}")
        return jsonify({"success": False, "error": "Failed to fetch LeetCode stats"}), 500

@integrations_bp.route('/api/integrations/hackerrank', methods=['GET', 'OPTIONS'])
@token_required
def get_hackerrank_stats():
    """Get HackerRank stats for user"""
    try:
        from app import coding_tracker
        user_email = request.current_user["email"]
        username = request.args.get("username")
        
        if not username:
            return jsonify({"success": False, "error": "Username required"}), 400
        
        print(f"[HACKERRANK API] Fetching stats for {username} (requested by {user_email})")
        
        # Use the enhanced tracker
        result = coding_tracker.get_enhanced_hackerrank_stats(username)
        
        if result and result.get('success'):
            stats = {
                "problems_solved": result['scores'].get('algorithms', 0) + result['scores'].get('data_structures', 0),
                "stars": result['scores'].get('total_score', 0) // 10,
                "badges": result.get('badge_count', 0),
                "certificates": result.get('certificates', 0),
                "total_score": result['scores'].get('total_score', 0),
                "badge_details": result.get('badges', [])
            }
            
            print(f"[HACKERRANK API] Success: {stats['stars']} stars, {stats['badges']} badges")
            
            return jsonify({
                "success": True,
                "stats": stats
            }), 200
        else:
            # Fallback with demo data for blocked APIs
            print(f"[HACKERRANK API] Using fallback data for {username}")
            
            stats = {
                "problems_solved": 45,
                "stars": 4,
                "badges": 8,
                "certificates": 2,
                "total_score": 40,
                "badge_details": [
                    {"name": "Problem Solving", "level": "Intermediate"},
                    {"name": "Algorithms", "level": "Basic"}
                ],
                "demo_data": True
            }
            
            return jsonify({
                "success": True,
                "stats": stats,
                "message": "Using demo data - API may be blocked"
            }), 200
        
    except Exception as e:
        print(f"[HACKERRANK API ERROR] {e}")
        
        # Return demo data on error
        stats = {
            "problems_solved": 25,
            "stars": 3,
            "badges": 5,
            "certificates": 1,
            "total_score": 30,
            "badge_details": [
                {"name": "Getting Started", "level": "Basic"}
            ],
            "demo_data": True
        }
        
        return jsonify({
            "success": True,
            "stats": stats,
            "message": "Using demo data due to API error"
        }), 200

@integrations_bp.route('/api/integrations/profiles', methods=['GET'])
@token_required
def get_coding_profiles():
    """Get user's coding platform profiles"""
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
        
        profiles = user.get("profile_links", {})
        
        return jsonify({
            "success": True,
            "profiles": profiles
        }), 200
        
    except Exception as e:
        print(f"Get coding profiles error: {e}")
        return jsonify({"success": False, "message": "Failed to retrieve profiles"}), 500

@integrations_bp.route('/api/integrations/sync', methods=['POST'])
@token_required
def sync_platform_data():
    """Sync data from coding platforms"""
    try:
        from app import users_collection, in_memory_users, coding_tracker
        user_email = request.current_user["email"]
        data = request.get_json()
        
        platform = data.get("platform")  # "leetcode", "hackerrank"
        username = data.get("username")
        
        if not platform or not username:
            return jsonify({"success": False, "message": "Platform and username required"}), 400
        
        print(f"[SYNC] Syncing {platform} data for {username}")
        
        # Fetch data from platform
        if platform == "leetcode":
            profile_data = coding_tracker.get_enhanced_leetcode_stats(username)
        elif platform == "hackerrank":
            profile_data = coding_tracker.get_enhanced_hackerrank_stats(username)
        else:
            return jsonify({"success": False, "message": f"Unsupported platform: {platform}"}), 400
        
        if not profile_data or not profile_data.get('success'):
            return jsonify({"success": False, "message": f"Failed to fetch data from {platform}"}), 400
        
        # Update user's coding profiles
        if users_collection:
            users_collection.update_one(
                {"email": user_email},
                {"$set": {f"platform_progress.{platform}": profile_data}}
            )
        else:
            user = in_memory_users.get(user_email)
            if not user:
                return jsonify({"success": False, "message": "User not found"}), 404
            
            if "platform_progress" not in user:
                user["platform_progress"] = {}
            user["platform_progress"][platform] = profile_data
        
        return jsonify({
            "success": True,
            "message": f"Successfully synced {platform} data",
            "profile": profile_data
        }), 200
        
    except Exception as e:
        print(f"Sync platform data error: {e}")
        return jsonify({"success": False, "message": "Failed to sync platform data"}), 500

@integrations_bp.route('/api/integrations/readiness', methods=['GET'])
@token_required
def get_readiness_level():
    """Calculate user's coding readiness based on platform stats"""
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
        
        platform_progress = user.get("platform_progress", {})
        readiness = calculate_readiness_score(platform_progress)
        
        return jsonify({
            "success": True,
            "readiness": readiness
        }), 200
        
    except Exception as e:
        print(f"Get readiness level error: {e}")
        return jsonify({"success": False, "message": "Failed to calculate readiness"}), 500

def calculate_readiness_score(platform_progress):
    """Calculate overall coding readiness score"""
    if not platform_progress:
        return {
            "overall_score": 0,
            "level": "Beginner",
            "strengths": [],
            "areas_to_improve": ["Start solving problems on coding platforms"],
            "recommendations": ["Create accounts on LeetCode and HackerRank"]
        }
    
    total_problems = 0
    total_rating = 0
    platforms_count = len(platform_progress)
    
    strengths = []
    areas_to_improve = []
    
    for platform, data in platform_progress.items():
        if platform == "leetcode":
            problems = data.get("solved", 0)
            total_problems += problems
            
            if problems > 100:
                strengths.append("Strong LeetCode problem solving")
            elif problems < 50:
                areas_to_improve.append("Solve more LeetCode problems")
        
        elif platform == "hackerrank":
            stars = data.get("stars", 0)
            if stars >= 4:
                strengths.append("Excellent HackerRank performance")
            elif stars < 3:
                areas_to_improve.append("Improve HackerRank star rating")
    
    # Calculate overall score (0-100)
    avg_problems = total_problems / platforms_count if platforms_count > 0 else 0
    score = min(100, (avg_problems / 200) * 100)  # Normalize to 100
    
    if score >= 80:
        level = "Expert"
    elif score >= 60:
        level = "Advanced"
    elif score >= 40:
        level = "Intermediate"
    else:
        level = "Beginner"
    
    recommendations = []
    if score < 40:
        recommendations.append("Focus on solving more easy problems daily")
        recommendations.append("Participate in weekly contests")
    elif score < 70:
        recommendations.append("Challenge yourself with medium difficulty problems")
        recommendations.append("Join coding communities for peer learning")
    else:
        recommendations.append("Focus on hard problems and system design")
        recommendations.append("Consider mentoring other developers")
    
    return {
        "overall_score": round(score, 1),
        "level": level,
        "total_problems_solved": total_problems,
        "platforms_active": platforms_count,
        "strengths": strengths,
        "areas_to_improve": areas_to_improve,
        "recommendations": recommendations
    }