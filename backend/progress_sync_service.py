# progress_sync_service.py
import schedule
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from coding_platforms import CodingPlatformTracker
import json
import os

class ProgressSyncService:
    def __init__(self, users_collection=None, in_memory_users=None):
        self.users_collection = users_collection
        self.in_memory_users = in_memory_users or {}
        self.tracker = CodingPlatformTracker()
        self.sync_history = {}
        self.is_running = False
        
    def start_service(self):
        """Start the background sync service"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Schedule different sync intervals
        schedule.every(30).minutes.do(self.sync_active_users)  # Active users every 30 min
        schedule.every(2).hours.do(self.sync_all_users)       # All users every 2 hours
        schedule.every().day.at("06:00").do(self.daily_sync)  # Daily comprehensive sync
        
        # Start scheduler thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("[SYNC SERVICE] Progress sync service started")
    
    def stop_service(self):
        """Stop the background sync service"""
        self.is_running = False
        schedule.clear()
        print("[SYNC SERVICE] Progress sync service stopped")
    
    def get_users_with_platforms(self) -> List[Dict]:
        """Get all users who have platform links configured"""
        users_with_platforms = []
        
        if self.users_collection is not None:
            # MongoDB users
            cursor = self.users_collection.find({
                "profile_links": {"$exists": True, "$ne": {}}
            })
            for user in cursor:
                profile_links = user.get("profile_links", {})
                if profile_links.get("leetcode") or profile_links.get("hackerrank"):
                    users_with_platforms.append({
                        "email": user["email"],
                        "profile_links": profile_links,
                        "last_updated": user.get("last_updated"),
                        "last_login_at": user.get("last_login_at")
                    })
        else:
            # In-memory users
            for email, user in self.in_memory_users.items():
                profile_links = user.get("profile_links", {})
                if profile_links.get("leetcode") or profile_links.get("hackerrank"):
                    users_with_platforms.append({
                        "email": email,
                        "profile_links": profile_links,
                        "last_updated": user.get("last_updated"),
                        "last_login_at": user.get("last_login_at")
                    })
        
        return users_with_platforms
    
    def is_user_active(self, user: Dict) -> bool:
        """Check if user has been active recently"""
        last_login = user.get("last_login_at")
        if not last_login:
            return False
        
        try:
            if isinstance(last_login, str):
                last_login_date = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
            else:
                last_login_date = last_login
            
            # Consider user active if logged in within last 24 hours
            return (datetime.now(timezone.utc) - last_login_date) < timedelta(hours=24)
        except:
            return False
    
    def sync_user_progress(self, user_email: str, profile_links: Dict, force: bool = False) -> bool:
        """Sync progress for a single user"""
        try:
            print(f"[SYNC] Syncing progress for {user_email}")
            
            # Check if sync is needed (avoid too frequent syncs)
            if not force and self.should_skip_sync(user_email):
                return False
            
            platform_progress = {}
            
            # Sync LeetCode
            if profile_links.get("leetcode"):
                try:
                    leetcode_stats = self.tracker.get_enhanced_leetcode_stats(profile_links["leetcode"])
                    if leetcode_stats.get('success'):
                        platform_progress["leetcode"] = {
                            "solved": leetcode_stats['solved_problems']['total'],
                            "easy": leetcode_stats['solved_problems']['easy'],
                            "medium": leetcode_stats['solved_problems']['medium'],
                            "hard": leetcode_stats['solved_problems']['hard'],
                            "ranking": leetcode_stats.get('ranking', 0),
                            "weekly_solved": leetcode_stats.get('weekly_solved', 0),
                            "last_active": leetcode_stats.get('last_active'),
                            "recent_activity": leetcode_stats.get('recent_activity', [])
                        }
                        print(f"[SYNC] LeetCode synced for {user_email}: {platform_progress['leetcode']['solved']} problems")
                except Exception as e:
                    print(f"[SYNC] LeetCode sync failed for {user_email}: {e}")
            
            # Sync HackerRank
            if profile_links.get("hackerrank"):
                try:
                    hackerrank_stats = self.tracker.get_enhanced_hackerrank_stats(profile_links["hackerrank"])
                    if hackerrank_stats.get('success'):
                        platform_progress["hackerrank"] = {
                            "stars": hackerrank_stats['scores'].get('total_score', 0) // 10,
                            "certificates": hackerrank_stats.get('certificates', 0),
                            "badges": hackerrank_stats.get('badge_count', 0),
                            "problems_solved": hackerrank_stats['scores'].get('algorithms', 0) + hackerrank_stats['scores'].get('data_structures', 0),
                            "badge_details": hackerrank_stats.get('badges', [])
                        }
                        print(f"[SYNC] HackerRank synced for {user_email}: {platform_progress['hackerrank']['stars']} stars")
                except Exception as e:
                    print(f"[SYNC] HackerRank sync failed for {user_email}: {e}")
            
            if not platform_progress:
                print(f"[SYNC] No progress data fetched for {user_email}")
                return False
            
            # Calculate overall score
            overall_score = self.calculate_overall_score(platform_progress)
            
            # Update user data
            update_data = {
                "platform_progress": platform_progress,
                "overall_score": overall_score,
                "last_updated": datetime.now(timezone.utc),
                "sync_count": self.get_sync_count(user_email) + 1
            }
            
            success = self.update_user_data(user_email, update_data)
            
            if success:
                # Record sync history
                self.sync_history[user_email] = {
                    "last_sync": datetime.now(timezone.utc),
                    "platforms_synced": list(platform_progress.keys()),
                    "overall_score": overall_score
                }
                print(f"[SYNC] Successfully synced {user_email}: Score {overall_score}")
                return True
            else:
                print(f"[SYNC] Failed to update database for {user_email}")
                return False
                
        except Exception as e:
            print(f"[SYNC] Error syncing {user_email}: {e}")
            return False
    
    def should_skip_sync(self, user_email: str) -> bool:
        """Check if sync should be skipped to avoid rate limiting"""
        if user_email not in self.sync_history:
            return False
        
        last_sync = self.sync_history[user_email].get("last_sync")
        if not last_sync:
            return False
        
        # Skip if synced within last 15 minutes
        return (datetime.now(timezone.utc) - last_sync) < timedelta(minutes=15)
    
    def get_sync_count(self, user_email: str) -> int:
        """Get current sync count for user"""
        if self.users_collection is not None:
            user = self.users_collection.find_one({"email": user_email})
            return user.get("sync_count", 0) if user else 0
        else:
            return self.in_memory_users.get(user_email, {}).get("sync_count", 0)
    
    def update_user_data(self, user_email: str, update_data: Dict) -> bool:
        """Update user data in database or memory"""
        try:
            if self.users_collection is not None:
                result = self.users_collection.update_one(
                    {"email": user_email},
                    {"$set": update_data}
                )
                return result.modified_count > 0
            else:
                if user_email in self.in_memory_users:
                    self.in_memory_users[user_email].update(update_data)
                    # Save to file if using file persistence
                    self.save_users_to_file()
                    return True
                return False
        except Exception as e:
            print(f"[SYNC] Database update error for {user_email}: {e}")
            return False
    
    def save_users_to_file(self):
        """Save in-memory users to file (if using file persistence)"""
        try:
            users_file = 'users_data.json'
            data_to_save = {}
            
            for email, user in self.in_memory_users.items():
                user_copy = user.copy()
                # Convert datetime objects to strings
                for key, value in user_copy.items():
                    if hasattr(value, 'isoformat'):
                        user_copy[key] = value.isoformat()
                data_to_save[email] = user_copy
            
            with open(users_file, 'w') as f:
                json.dump(data_to_save, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[SYNC] File save error: {e}")
    
    def calculate_overall_score(self, platform_progress: Dict) -> int:
        """Calculate overall coding score from all platforms"""
        try:
            total_score = 0
            platforms = 0
            
            if platform_progress.get("leetcode", {}).get("solved"):
                leetcode_score = min(platform_progress["leetcode"]["solved"] * 0.5, 50)
                total_score += leetcode_score
                platforms += 1
            
            if platform_progress.get("hackerrank", {}).get("stars"):
                hackerrank_score = platform_progress["hackerrank"]["stars"] * 10
                total_score += hackerrank_score
                platforms += 1
            
            return round(total_score / platforms) if platforms > 0 else 0
            
        except Exception as e:
            print(f"[SYNC] Score calculation error: {e}")
            return 0
    
    def sync_active_users(self):
        """Sync only recently active users"""
        try:
            users = self.get_users_with_platforms()
            active_users = [user for user in users if self.is_user_active(user)]
            
            print(f"[SYNC] Syncing {len(active_users)} active users")
            
            for user in active_users:
                self.sync_user_progress(user["email"], user["profile_links"])
                time.sleep(2)  # Rate limiting
                
        except Exception as e:
            print(f"[SYNC] Active users sync error: {e}")
    
    def sync_all_users(self):
        """Sync all users with platform links"""
        try:
            users = self.get_users_with_platforms()
            print(f"[SYNC] Syncing all {len(users)} users with platform links")
            
            for user in users:
                self.sync_user_progress(user["email"], user["profile_links"])
                time.sleep(5)  # Longer rate limiting for bulk sync
                
        except Exception as e:
            print(f"[SYNC] All users sync error: {e}")
    
    def daily_sync(self):
        """Comprehensive daily sync with insights generation"""
        try:
            print("[SYNC] Starting daily comprehensive sync")
            
            users = self.get_users_with_platforms()
            sync_results = {
                "total_users": len(users),
                "successful_syncs": 0,
                "failed_syncs": 0,
                "insights_generated": 0
            }
            
            for user in users:
                # Get previous stats for comparison
                previous_stats = self.get_user_previous_stats(user["email"])
                
                # Sync current stats
                success = self.sync_user_progress(user["email"], user["profile_links"], force=True)
                
                if success:
                    sync_results["successful_syncs"] += 1
                    
                    # Generate insights if we have previous data
                    if previous_stats:
                        current_stats = self.get_user_current_stats(user["email"])
                        insights = self.tracker.get_progress_insights(current_stats, previous_stats)
                        
                        if insights["trends"] or insights["achievements"]:
                            self.save_user_insights(user["email"], insights)
                            sync_results["insights_generated"] += 1
                else:
                    sync_results["failed_syncs"] += 1
                
                time.sleep(3)  # Rate limiting
            
            print(f"[SYNC] Daily sync completed: {sync_results}")
            
        except Exception as e:
            print(f"[SYNC] Daily sync error: {e}")
    
    def get_user_previous_stats(self, user_email: str) -> Optional[Dict]:
        """Get user's previous platform stats for comparison"""
        try:
            if self.users_collection is not None:
                user = self.users_collection.find_one({"email": user_email})
                return user.get("platform_progress") if user else None
            else:
                return self.in_memory_users.get(user_email, {}).get("platform_progress")
        except:
            return None
    
    def get_user_current_stats(self, user_email: str) -> Optional[Dict]:
        """Get user's current platform stats"""
        return self.get_user_previous_stats(user_email)  # Same method for current stats
    
    def save_user_insights(self, user_email: str, insights: Dict):
        """Save generated insights for user"""
        try:
            update_data = {
                "progress_insights": insights,
                "insights_generated_at": datetime.now(timezone.utc)
            }
            self.update_user_data(user_email, update_data)
            print(f"[SYNC] Insights saved for {user_email}")
        except Exception as e:
            print(f"[SYNC] Failed to save insights for {user_email}: {e}")
    
    def get_sync_status(self) -> Dict:
        """Get current sync service status"""
        return {
            "is_running": self.is_running,
            "total_users_tracked": len(self.get_users_with_platforms()),
            "recent_syncs": len(self.sync_history),
            "last_sync_times": {
                email: history["last_sync"].isoformat() 
                for email, history in self.sync_history.items()
            }
        }

# Global instance
progress_sync_service = None

def initialize_sync_service(users_collection=None, in_memory_users=None):
    """Initialize the global sync service"""
    global progress_sync_service
    progress_sync_service = ProgressSyncService(users_collection, in_memory_users)
    progress_sync_service.start_service()
    return progress_sync_service