# Streak API Endpoints for Flask App

from flask import jsonify, request
from datetime import datetime, timezone
from streak_system import update_streak_on_login, get_user_streak

def add_streak_routes(app, token_required, get_user_by_email, users_collection, in_memory_users):
    """Add streak-related routes to Flask app"""
    
    @app.route("/api/user/streak", methods=["GET", "OPTIONS"])
    @token_required
    def get_user_streak_data():
        """Get current user's streak data"""
        try:
            user_email = request.current_user["email"]
            
            user = get_user_by_email(user_email)
            if not user:
                return jsonify({"success": False, "error": "User not found"}), 404
            
            streak_data = user.get("streak", {
                "current_streak": 0,
                "total_days": 0,
                "this_week": 0,
                "week_counts": [0, 0, 0, 0, 0, 0, 0],
                "weekly_summary_in_progress": True,
                "last_active_date": None,
                "last_login_date": None
            })
            
            return jsonify({
                "success": True,
                "streak": streak_data
            }), 200
            
        except Exception as e:
            print(f"Get streak error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/user/streak/update", methods=["POST", "OPTIONS"])
    @token_required
    def manual_streak_update():
        """Manually trigger streak update (for testing)"""
        try:
            user_email = request.current_user["email"]
            
            streak_data = update_streak_on_login(user_email, users_collection or in_memory_users)
            
            if streak_data:
                return jsonify({
                    "success": True,
                    "message": "Streak updated successfully",
                    "streak": streak_data
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to update streak"
                }), 500
                
        except Exception as e:
            print(f"Manual streak update error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/user/streak/reset", methods=["POST", "OPTIONS"])
    @token_required
    def reset_user_streak():
        """Reset user's streak data (for testing)"""
        try:
            user_email = request.current_user["email"]
            
            reset_streak = {
                "current_streak": 0,
                "total_days": 0,
                "this_week": 0,
                "week_counts": [0, 0, 0, 0, 0, 0, 0],
                "weekly_summary_in_progress": True,
                "last_active_date": None,
                "last_login_date": None
            }
            
            if users_collection is not None:
                users_collection.update_one(
                    {"email": user_email},
                    {"$set": {"streak": reset_streak}}
                )
            else:
                if user_email in in_memory_users:
                    in_memory_users[user_email]["streak"] = reset_streak
            
            return jsonify({
                "success": True,
                "message": "Streak reset successfully",
                "streak": reset_streak
            }), 200
            
        except Exception as e:
            print(f"Reset streak error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500