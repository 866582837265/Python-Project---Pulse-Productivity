from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

class StreakService:
    """Enhanced service for managing user streaks with dynamic tracking"""
    
    @staticmethod
    def calculate_streak(last_activity_date: Optional[str], current_streak: int = 0) -> Tuple[int, bool]:
        """
        Calculate streak based on last activity date with proper edge case handling
        Returns: (new_streak, should_update)

        Rules:
        - If last activity was yesterday: increment streak by 1
        - If last activity was today: do nothing (no update)
        - If last activity was before yesterday: reset streak to 1
        - If no previous activity: start streak at 1
        """
        today = datetime.now(timezone.utc).date()
        
        if not last_activity_date:
            # First time activity - start streak
            return 1, True
        
        try:
            # Parse last activity date
            if isinstance(last_activity_date, str):
                last_date = datetime.fromisoformat(last_activity_date.replace('Z', '+00:00')).date()
            else:
                last_date = last_activity_date.date()
            
            yesterday = today - timedelta(days=1)
            
            if last_date == today:
                # Already updated today - no change
                return current_streak, False
            elif last_date == yesterday:
                # Consecutive day - increment streak
                return current_streak + 1, True
            else:
                # Gap in activity - reset streak to 1
                return 1, True
                
        except Exception as e:
            print(f"Error calculating streak: {e}")
            # On error, start fresh
            return 1, True
    
    @staticmethod
    def update_user_streak(users_collection, in_memory_users, user_email: str, activity_type: str = "login") -> Dict:
        """
        Update user streak with enhanced tracking and persistence
        
        Args:
            users_collection: MongoDB collection or None
            in_memory_users: In-memory user storage dict
            user_email: User's email address
            activity_type: Type of activity ("login", "practice", "quiz")
        
        Returns:
            Dict with success status and streak information
        """
        try:
            today = datetime.now(timezone.utc)
            today_str = today.date().isoformat()
            
            # Get user data
            if users_collection:
                user = users_collection.find_one({"email": user_email})
                if not user:
                    return {"success": False, "error": "User not found"}
            else:
                user = in_memory_users.get(user_email)
                if not user:
                    return {"success": False, "error": "User not found"}
            
            # Get current streak data
            current_streak = user.get("current_streak", 0)
            last_activity = user.get("last_streak_activity")
            streak_history = user.get("streak_history", [])
            
            # Check if already updated today
            if streak_history and len(streak_history) > 0:
                last_entry = streak_history[-1]
                if last_entry.get("date") == today_str:
                    # Already updated today, just update activity type if different
                    if last_entry.get("activity_type") != activity_type:
                        last_entry["activity_type"] = f"{last_entry.get('activity_type', 'login')},{activity_type}"
                        StreakService._save_user_data(users_collection, in_memory_users, user_email, {"streak_history": streak_history})
                    
                    return {
                        "success": True,
                        "streak_updated": False,
                        "current_streak": current_streak,
                        "longest_streak": user.get("longest_streak", 0),
                        "message": "Streak already updated today"
                    }
            
            # Calculate new streak
            new_streak, should_update = StreakService.calculate_streak(last_activity, current_streak)
            
            if should_update:
                # Update streak data
                longest_streak = max(user.get("longest_streak", 0), new_streak)
                total_active_days = user.get("total_active_days", 0) + 1
                
                # Add to streak history
                streak_history.append({
                    "date": today_str,
                    "streak": new_streak,
                    "activity_type": activity_type,
                    "timestamp": today.isoformat()
                })
                
                # Keep only last 60 days of history for better visualization
                if len(streak_history) > 60:
                    streak_history = streak_history[-60:]
                
                update_data = {
                    "current_streak": new_streak,
                    "longest_streak": longest_streak,
                    "last_streak_activity": today.isoformat(),
                    "total_active_days": total_active_days,
                    "last_activity_type": activity_type,
                    "streak_history": streak_history,
                    "streak_updated_at": today.isoformat()
                }
                
                # Save to database/memory
                StreakService._save_user_data(users_collection, in_memory_users, user_email, update_data)
                
                return {
                    "success": True,
                    "streak_updated": True,
                    "current_streak": new_streak,
                    "longest_streak": longest_streak,
                    "total_active_days": total_active_days,
                    "activity_type": activity_type,
                    "message": f"🔥 {new_streak} day streak! Keep it up!"
                }
            else:
                return {
                    "success": True,
                    "streak_updated": False,
                    "current_streak": current_streak,
                    "longest_streak": user.get("longest_streak", 0),
                    "message": "Streak already updated today"
                }
                    
        except Exception as e:
            print(f"Error updating streak for {user_email}: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _save_user_data(users_collection, in_memory_users, user_email: str, update_data: Dict):
        """Helper method to save user data to appropriate storage"""
        if users_collection:
            users_collection.update_one(
                {"email": user_email},
                {"$set": update_data}
            )
        else:
            user = in_memory_users.get(user_email)
            if user:
                user.update(update_data)
                # Save to file if using file persistence
                try:
                    from app import save_users_to_file
                    save_users_to_file()
                except Exception as e:
                    print(f"Failed to save to file: {e}")
    
    @staticmethod
    def get_streak_data(users_collection, in_memory_users, user_email: str) -> Dict:
        """Get comprehensive streak data with automatic streak validation"""
        try:
            if users_collection:
                user = users_collection.find_one({"email": user_email})
            else:
                user = in_memory_users.get(user_email)
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get current streak data
            current_streak = user.get("current_streak", 0)
            last_activity = user.get("last_streak_activity")
            streak_history = user.get("streak_history", [])
            
            # Validate current streak against last activity
            if last_activity and current_streak > 0:
                try:
                    last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00')).date()
                    today = datetime.now(timezone.utc).date()
                    days_since_activity = (today - last_date).days
                    
                    # Reset streak if more than 1 day gap (streak broken)
                    if days_since_activity > 1:
                        print(f"Streak broken for {user_email}: {days_since_activity} days since last activity")
                        current_streak = 0
                        
                        # Update in database
                        reset_data = {
                            "current_streak": 0,
                            "streak_broken_at": datetime.now(timezone.utc).isoformat(),
                            "streak_broken_reason": f"Inactive for {days_since_activity} days"
                        }
                        StreakService._save_user_data(users_collection, in_memory_users, user_email, reset_data)
                        
                except Exception as e:
                    print(f"Error validating streak for {user_email}: {e}")
            
            # Calculate streak risk
            streak_risk = StreakService._calculate_streak_risk(last_activity)
            
            # Get recent activity summary
            recent_activity = StreakService._get_recent_activity_summary(streak_history)
            
            return {
                "success": True,
                "data": {
                    "current_streak": current_streak,
                    "longest_streak": user.get("longest_streak", 0),
                    "total_active_days": user.get("total_active_days", 0),
                    "last_activity": last_activity,
                    "last_activity_type": user.get("last_activity_type", "login"),
                    "streak_history": streak_history,
                    "streak_risk": streak_risk,
                    "recent_activity": recent_activity,
                    "streak_updated_at": user.get("streak_updated_at")
                }
            }
            
        except Exception as e:
            print(f"Error getting streak data for {user_email}: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _calculate_streak_risk(last_activity: Optional[str]) -> str:
        """Calculate risk of losing streak"""
        if not last_activity:
            return "High"
        
        try:
            last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00')).date()
            today = datetime.now(timezone.utc).date()
            days_since = (today - last_date).days
            
            if days_since == 0:
                return "Low"  # Active today
            elif days_since == 1:
                return "Medium"  # Need to be active today
            else:
                return "High"  # Streak already broken
                
        except:
            return "High"
    
    @staticmethod
    def _get_recent_activity_summary(streak_history: list) -> Dict:
        """Get summary of recent activity"""
        if not streak_history:
            return {"days_active_last_week": 0, "days_active_last_month": 0}
        
        today = datetime.now(timezone.utc).date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        days_active_last_week = 0
        days_active_last_month = 0
        
        for entry in streak_history:
            try:
                entry_date = datetime.fromisoformat(entry["date"]).date()
                if entry_date >= week_ago:
                    days_active_last_week += 1
                if entry_date >= month_ago:
                    days_active_last_month += 1
            except:
                continue
        
        return {
            "days_active_last_week": days_active_last_week,
            "days_active_last_month": days_active_last_month
        }
    
    @staticmethod
    def trigger_practice_streak(users_collection, in_memory_users, user_email: str) -> Dict:
        """Trigger streak update for practice activity"""
        return StreakService.update_user_streak(users_collection, in_memory_users, user_email, "practice")
    
    @staticmethod
    def trigger_login_streak(users_collection, in_memory_users, user_email: str) -> Dict:
        """Trigger streak update for login activity"""
        return StreakService.update_user_streak(users_collection, in_memory_users, user_email, "login")
    
    @staticmethod
    def trigger_quiz_streak(users_collection, in_memory_users, user_email: str) -> Dict:
        """Trigger streak update for quiz completion"""
        return StreakService.update_user_streak(users_collection, in_memory_users, user_email, "quiz")