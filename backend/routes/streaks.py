from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt
import os
from streak_service import StreakService

streaks_bp = Blueprint('streaks', __name__)

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

@streaks_bp.route('/api/streaks', methods=['GET'])
@token_required
def get_streaks():
    """Get user's comprehensive streak data"""
    try:
        from app import users_collection, in_memory_users
        user_email = request.current_user["email"]
        
        result = StreakService.get_streak_data(users_collection, in_memory_users, user_email)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
        
    except Exception as e:
        print(f"Get streaks error: {e}")
        return jsonify({"success": False, "message": "Failed to retrieve streaks"}), 500

@streaks_bp.route('/api/streaks/update', methods=['POST'])
@token_required
def update_streak():
    """Manually update user's daily streak"""
    try:
        from app import users_collection, in_memory_users
        user_email = request.current_user["email"]
        data = request.get_json() or {}
        activity_type = data.get("activity_type", "practice")
        
        result = StreakService.update_user_streak(
            users_collection, in_memory_users, user_email, activity_type
        )
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        print(f"Update streak error: {e}")
        return jsonify({"success": False, "message": "Failed to update streak"}), 500

@streaks_bp.route('/api/streaks/login', methods=['POST'])
@token_required
def update_login_streak():
    """Update streak on user login (called automatically)"""
    try:
        from app import users_collection, in_memory_users
        user_email = request.current_user["email"]
        
        result = StreakService.update_user_streak(
            users_collection, in_memory_users, user_email, "login"
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Login streak error: {e}")
        return jsonify({"success": False, "message": "Failed to update login streak"}), 500

@streaks_bp.route('/api/streaks/practice', methods=['POST'])
@token_required
def update_practice_streak():
    """Update streak on practice activity"""
    try:
        from app import users_collection, in_memory_users
        user_email = request.current_user["email"]
        
        result = StreakService.update_user_streak(
            users_collection, in_memory_users, user_email, "practice"
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Practice streak error: {e}")
        return jsonify({"success": False, "message": "Failed to update practice streak"}), 500

@streaks_bp.route('/api/streaks/history', methods=['GET'])
@token_required
def get_streak_history():
    """Get user's streak history for visualization"""
    try:
        from app import users_collection, in_memory_users
        user_email = request.current_user["email"]
        
        if users_collection:
            user = users_collection.find_one({"email": user_email})
        else:
            user = in_memory_users.get(user_email)
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        streak_history = user.get("streak_history", [])
        
        # Generate last 30 days data for visualization
        today = datetime.now(timezone.utc).date()
        history_data = []
        
        for i in range(29, -1, -1):  # Last 30 days
            date = today - timedelta(days=i)
            date_str = date.isoformat()
            
            # Find activity for this date
            day_activity = next((h for h in streak_history if h["date"] == date_str), None)
            
            history_data.append({
                "date": date_str,
                "has_activity": day_activity is not None,
                "streak": day_activity["streak"] if day_activity else 0,
                "activity_type": day_activity["activity_type"] if day_activity else None
            })
        
        return jsonify({
            "success": True,
            "history": history_data
        }), 200
        
    except Exception as e:
        print(f"Get streak history error: {e}")
        return jsonify({"success": False, "message": "Failed to get streak history"}), 500