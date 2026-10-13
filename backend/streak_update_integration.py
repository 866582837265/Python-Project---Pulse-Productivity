# Complete Streak System Integration for Pulse App

from datetime import datetime, timedelta
import pytz
from pymongo.collection import Collection

# Asia/Kolkata timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_date():
    """Get current date in IST timezone as YYYY-MM-DD string"""
    return datetime.now(IST).strftime('%Y-%m-%d')

def get_ist_weekday():
    """Get current weekday in IST (0=Monday, 6=Sunday)"""
    return datetime.now(IST).weekday()

def parse_date(date_str):
    """Parse YYYY-MM-DD string to datetime object"""
    if not date_str:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d')

def is_consecutive_day(last_date_str, current_date_str):
    """Check if current date is exactly one day after last date"""
    if not last_date_str:
        return False
    
    last_date = parse_date(last_date_str)
    current_date = parse_date(current_date_str)
    
    return (current_date - last_date).days == 1

def is_new_week(last_date_str, current_date_str):
    """Check if we've moved to a new week (Monday-Sunday)"""
    if not last_date_str:
        return True
    
    last_date = parse_date(last_date_str)
    current_date = parse_date(current_date_str)
    
    # Get Monday of each week
    last_monday = last_date - timedelta(days=last_date.weekday())
    current_monday = current_date - timedelta(days=current_date.weekday())
    
    return last_monday != current_monday

def update_streak_on_login(user_email, storage):
    """
    Update user streak on login - core algorithm
    Returns updated streak data or None if error
    """
    try:
        current_date = get_ist_date()
        current_weekday = get_ist_weekday()
        
        # Get user from MongoDB or in-memory storage
        if isinstance(storage, Collection):
            user = storage.find_one({"email": user_email})
        else:
            user = storage.get(user_email)
        
        if not user:
            return None
        
        # Initialize streak if not exists
        streak = user.get("streak", {
            "current_streak": 0,
            "total_days": 0,
            "this_week": 0,
            "week_counts": [0, 0, 0, 0, 0, 0, 0],
            "weekly_summary_in_progress": True,
            "last_active_date": None,
            "last_login_date": None
        })
        
        last_login_date = streak.get("last_login_date")
        last_active_date = streak.get("last_active_date")
        
        # Skip if already logged in today
        if last_login_date == current_date:
            return streak
        
        # Check if new week started
        if is_new_week(last_active_date, current_date):
            streak["week_counts"] = [0, 0, 0, 0, 0, 0, 0]
            streak["this_week"] = 0
            streak["weekly_summary_in_progress"] = True
        
        # Update streak logic
        if is_consecutive_day(last_active_date, current_date):
            # Consecutive day - increment streak
            streak["current_streak"] += 1
        else:
            # Not consecutive - reset streak to 1
            streak["current_streak"] = 1
        
        # Update counters (only once per day)
        streak["total_days"] += 1
        streak["this_week"] += 1
        streak["week_counts"][current_weekday] = 1
        
        # Check if week is complete
        streak["weekly_summary_in_progress"] = sum(streak["week_counts"]) < 7
        
        # Update dates
        streak["last_active_date"] = current_date
        streak["last_login_date"] = current_date
        
        # Save to storage
        if isinstance(storage, Collection):
            storage.update_one(
                {"email": user_email},
                {"$set": {"streak": streak}}
            )
        else:
            storage[user_email]["streak"] = streak
        
        return streak
        
    except Exception as e:
        print(f"Streak update error: {e}")
        return None

# Integration with existing login endpoint
def integrate_with_login():
    """
    Example integration code for the login endpoint
    """
    example_code = '''
    # In your login endpoint, after successful authentication:
    
    # Update streak on successful login
    streak_data = update_streak_on_login(email, users_collection or in_memory_users)
    
    # Generate JWT token
    token = jwt.encode({
        'email': user['email'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    print(f"✅ Login successful for {email}")
    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "email": user["email"],
            "username": user["username"]
        },
        "streak": streak_data,  # Include streak data in response
        "message": "Login successful"
    }), 200
    '''
    return example_code

# Data model for users collection
USER_STREAK_SCHEMA = {
    "_id": "ObjectId",
    "email": "user@example.com",
    "username": "user123",
    "password": "hashed_password",
    "streak": {
        "current_streak": 0,           # Current consecutive days
        "total_days": 0,               # Total days ever logged in
        "this_week": 0,                # Days logged in this week (Mon-Sun)
        "week_counts": [0,0,0,0,0,0,0], # [Mon,Tue,Wed,Thu,Fri,Sat,Sun]
        "weekly_summary_in_progress": True,
        "last_active_date": "2024-01-15", # YYYY-MM-DD format
        "last_login_date": "2024-01-15"   # Track last login to avoid double counting
    },
    "createdAt": "datetime",
    # other user fields...
}

# API endpoint for getting streak data
def get_streak_endpoint():
    """
    Example API endpoint to get user streak data
    """
    example_code = '''
    @app.route("/api/user/streak", methods=["GET", "OPTIONS"])
    @token_required
    def get_user_streak_data():
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
            return jsonify({"success": False, "error": str(e)}), 500
    '''
    return example_code