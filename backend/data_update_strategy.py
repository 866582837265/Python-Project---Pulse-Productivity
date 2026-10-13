# data_update_strategy.py
import schedule
import time
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from ml_progress_analyzer import progress_analyzer
from data_extraction_service import data_extractor
import json

class DataUpdateStrategy:
    def __init__(self, users_collection=None, in_memory_users=None):
        self.users_collection = users_collection
        self.in_memory_users = in_memory_users or {}
        self.update_history = {}
        self.is_running = False
        
        # Update frequencies (in minutes)
        self.frequencies = {
            'high_activity': 15,    # Very active users
            'medium_activity': 60,  # Moderately active users
            'low_activity': 240,    # Less active users
            'inactive': 1440        # Daily for inactive users
        }
    
    def start_strategy(self):
        """Start the intelligent data update strategy"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Schedule different update strategies
        schedule.every(5).minutes.do(self.update_high_priority_users)
        schedule.every(30).minutes.do(self.update_medium_priority_users)
        schedule.every(2).hours.do(self.update_low_priority_users)
        schedule.every().day.at("02:00").do(self.daily_comprehensive_update)
        schedule.every().day.at("06:00").do(self.retrain_ml_model)
        
        # Start scheduler thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("[UPDATE STRATEGY] Intelligent data update strategy started")
    
    def stop_strategy(self):
        """Stop the update strategy"""
        self.is_running = False
        schedule.clear()
        print("[UPDATE STRATEGY] Data update strategy stopped")
    
    def classify_user_activity(self, user: Dict) -> str:
        """Classify user activity level for update frequency"""
        try:
            # Check recent login activity
            last_login = user.get('last_login_at')
            if not last_login:
                return 'inactive'
            
            if isinstance(last_login, str):
                last_login_date = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
            else:
                last_login_date = last_login
            
            hours_since_login = (datetime.now(timezone.utc) - last_login_date).total_seconds() / 3600
            
            # Check platform activity
            platform_progress = user.get('platform_progress', {})
            weekly_activity = 0
            
            if platform_progress.get('leetcode'):
                weekly_activity += platform_progress['leetcode'].get('weekly_solved', 0)
            
            # Classification logic
            if hours_since_login <= 2 and weekly_activity >= 5:
                return 'high_activity'
            elif hours_since_login <= 24 and weekly_activity >= 2:
                return 'medium_activity'
            elif hours_since_login <= 168:  # 1 week
                return 'low_activity'
            else:
                return 'inactive'
                
        except Exception as e:
            print(f"[UPDATE STRATEGY] Error classifying user activity: {e}")
            return 'low_activity'
    
    def should_update_user(self, user_email: str, activity_level: str) -> bool:
        """Determine if user should be updated based on activity and last update"""
        try:
            last_update = self.update_history.get(user_email, {}).get('last_update')
            if not last_update:
                return True
            
            minutes_since_update = (datetime.now(timezone.utc) - last_update).total_seconds() / 60
            required_frequency = self.frequencies[activity_level]
            
            return minutes_since_update >= required_frequency
            
        except Exception as e:
            print(f"[UPDATE STRATEGY] Error checking update requirement: {e}")
            return True
    
    def update_user_data(self, user_email: str, profile_links: Dict) -> bool:
        """Update user data with ML analysis"""
        try:
            print(f"[UPDATE STRATEGY] Updating data for {user_email}")
            
            # Extract fresh data
            leetcode_data = None
            hackerrank_data = None
            
            if profile_links.get('leetcode'):
                leetcode_data = data_extractor.extract_leetcode_data(profile_links['leetcode'])
                time.sleep(2)  # Rate limiting
            
            if profile_links.get('hackerrank'):
                hackerrank_data = data_extractor.extract_hackerrank_data(profile_links['hackerrank'])
                time.sleep(2)  # Rate limiting
            
            # Get historical data for ML analysis
            user = self.get_user_by_email(user_email)
            historical_data = user.get('progress_history', []) if user else []
            
            # Generate ML analysis
            ml_analysis = progress_analyzer.predict_progress_score(
                leetcode_data, hackerrank_data, historical_data
            )
            
            # Update progress history
            current_progress = {
                'date': datetime.now(timezone.utc).isoformat(),
                'problems_solved': ml_analysis['features']['total_problems'],
                'weekly_activity': ml_analysis['features']['weekly_activity'],
                'overall_score': ml_analysis['overall_score']
            }
            
            # Keep last 90 days of history
            if historical_data:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
                historical_data = [
                    h for h in historical_data 
                    if datetime.fromisoformat(h['date'].replace('Z', '+00:00')) > cutoff_date
                ]
            
            historical_data.append(current_progress)
            
            # Prepare update data
            update_data = {
                'enhanced_platform_data': {
                    'leetcode': leetcode_data,
                    'hackerrank': hackerrank_data
                },
                'ml_analysis': ml_analysis,
                'progress_history': historical_data,
                'last_ml_update': datetime.now(timezone.utc),
                'update_count': user.get('update_count', 0) + 1 if user else 1
            }
            
            # Update database
            success = self.update_user_database(user_email, update_data)
            
            if success:
                # Record update history
                self.update_history[user_email] = {
                    'last_update': datetime.now(timezone.utc),
                    'success': True,
                    'ml_score': ml_analysis['overall_score']
                }
                print(f"[UPDATE STRATEGY] Successfully updated {user_email} - Score: {ml_analysis['overall_score']}")
                return True
            else:
                print(f"[UPDATE STRATEGY] Failed to update database for {user_email}")
                return False
                
        except Exception as e:
            print(f"[UPDATE STRATEGY] Error updating {user_email}: {e}")
            self.update_history[user_email] = {
                'last_update': datetime.now(timezone.utc),
                'success': False,
                'error': str(e)
            }
            return False
    
    def get_user_by_email(self, email: str):
        """Get user data by email"""
        if self.users_collection is not None:
            return self.users_collection.find_one({"email": email})
        else:
            return self.in_memory_users.get(email)
    
    def update_user_database(self, email: str, update_data: Dict) -> bool:
        """Update user data in database"""
        try:
            if self.users_collection is not None:
                result = self.users_collection.update_one(
                    {"email": email},
                    {"$set": update_data}
                )
                return result.modified_count > 0
            else:
                if email in self.in_memory_users:
                    self.in_memory_users[email].update(update_data)
                    return True
                return False
        except Exception as e:
            print(f"[UPDATE STRATEGY] Database update error: {e}")
            return False
    
    def get_users_with_platforms(self) -> List[Dict]:
        """Get users with platform links"""
        users = []
        
        if self.users_collection is not None:
            cursor = self.users_collection.find({
                "profile_links": {"$exists": True, "$ne": {}}
            })
            for user in cursor:
                profile_links = user.get("profile_links", {})
                if profile_links.get("leetcode") or profile_links.get("hackerrank"):
                    users.append({
                        "email": user["email"],
                        "profile_links": profile_links,
                        "last_login_at": user.get("last_login_at"),
                        "platform_progress": user.get("platform_progress", {})
                    })
        else:
            for email, user in self.in_memory_users.items():
                profile_links = user.get("profile_links", {})
                if profile_links.get("leetcode") or profile_links.get("hackerrank"):
                    users.append({
                        "email": email,
                        "profile_links": profile_links,
                        "last_login_at": user.get("last_login_at"),
                        "platform_progress": user.get("platform_progress", {})
                    })
        
        return users
    
    def update_high_priority_users(self):
        """Update high activity users"""
        try:
            users = self.get_users_with_platforms()
            high_priority_users = []
            
            for user in users:
                activity_level = self.classify_user_activity(user)
                if activity_level == 'high_activity' and self.should_update_user(user['email'], activity_level):
                    high_priority_users.append(user)
            
            print(f"[UPDATE STRATEGY] Updating {len(high_priority_users)} high priority users")
            
            for user in high_priority_users[:5]:  # Limit to 5 users per batch
                self.update_user_data(user['email'], user['profile_links'])
                time.sleep(3)  # Rate limiting
                
        except Exception as e:
            print(f"[UPDATE STRATEGY] High priority update error: {e}")
    
    def update_medium_priority_users(self):
        """Update medium activity users"""
        try:
            users = self.get_users_with_platforms()
            medium_priority_users = []
            
            for user in users:
                activity_level = self.classify_user_activity(user)
                if activity_level == 'medium_activity' and self.should_update_user(user['email'], activity_level):
                    medium_priority_users.append(user)
            
            print(f"[UPDATE STRATEGY] Updating {len(medium_priority_users)} medium priority users")
            
            for user in medium_priority_users[:10]:  # Limit to 10 users per batch
                self.update_user_data(user['email'], user['profile_links'])
                time.sleep(5)  # Rate limiting
                
        except Exception as e:
            print(f"[UPDATE STRATEGY] Medium priority update error: {e}")
    
    def update_low_priority_users(self):
        """Update low activity users"""
        try:
            users = self.get_users_with_platforms()
            low_priority_users = []
            
            for user in users:
                activity_level = self.classify_user_activity(user)
                if activity_level in ['low_activity', 'inactive'] and self.should_update_user(user['email'], activity_level):
                    low_priority_users.append(user)
            
            print(f"[UPDATE STRATEGY] Updating {len(low_priority_users)} low priority users")
            
            for user in low_priority_users[:20]:  # Limit to 20 users per batch
                self.update_user_data(user['email'], user['profile_links'])
                time.sleep(10)  # Longer rate limiting
                
        except Exception as e:
            print(f"[UPDATE STRATEGY] Low priority update error: {e}")
    
    def daily_comprehensive_update(self):
        """Daily comprehensive update with data validation"""
        try:
            print("[UPDATE STRATEGY] Starting daily comprehensive update")
            
            users = self.get_users_with_platforms()
            update_stats = {
                'total_users': len(users),
                'successful_updates': 0,
                'failed_updates': 0,
                'data_quality_issues': 0
            }
            
            for user in users:
                try:
                    # Force update regardless of frequency
                    success = self.update_user_data(user['email'], user['profile_links'])
                    
                    if success:
                        update_stats['successful_updates'] += 1
                        
                        # Validate data quality
                        updated_user = self.get_user_by_email(user['email'])
                        if self.validate_data_quality(updated_user):
                            print(f"[UPDATE STRATEGY] Data quality validated for {user['email']}")
                        else:
                            update_stats['data_quality_issues'] += 1
                            print(f"[UPDATE STRATEGY] Data quality issues for {user['email']}")
                    else:
                        update_stats['failed_updates'] += 1
                    
                    time.sleep(15)  # Conservative rate limiting for comprehensive update
                    
                except Exception as user_error:
                    print(f"[UPDATE STRATEGY] Error updating {user['email']}: {user_error}")
                    update_stats['failed_updates'] += 1
            
            print(f"[UPDATE STRATEGY] Daily update completed: {update_stats}")
            
        except Exception as e:
            print(f"[UPDATE STRATEGY] Daily comprehensive update error: {e}")
    
    def validate_data_quality(self, user: Dict) -> bool:
        """Validate data quality for a user"""
        try:
            if not user:
                return False
            
            ml_analysis = user.get('ml_analysis')
            if not ml_analysis:
                return False
            
            # Check if ML analysis has required fields
            required_fields = ['overall_score', 'breakdown', 'features', 'level']
            for field in required_fields:
                if field not in ml_analysis:
                    return False
            
            # Check if score is reasonable (0-100)
            score = ml_analysis.get('overall_score', 0)
            if not (0 <= score <= 100):
                return False
            
            # Check if features are reasonable
            features = ml_analysis.get('features', {})
            if features.get('total_problems', 0) < 0:
                return False
            
            return True
            
        except Exception as e:
            print(f"[UPDATE STRATEGY] Data validation error: {e}")
            return False
    
    def retrain_ml_model(self):
        """Retrain ML model with latest data"""
        try:
            print("[UPDATE STRATEGY] Starting ML model retraining")
            
            # Retrain the model with fresh synthetic data
            train_score, test_score = progress_analyzer.train_model()
            
            # Save the updated model
            progress_analyzer.save_model()
            
            print(f"[UPDATE STRATEGY] ML model retrained - Train: {train_score:.3f}, Test: {test_score:.3f}")
            
        except Exception as e:
            print(f"[UPDATE STRATEGY] ML model retraining error: {e}")
    
    def get_update_statistics(self) -> Dict:
        """Get update strategy statistics"""
        total_updates = len(self.update_history)
        successful_updates = sum(1 for h in self.update_history.values() if h.get('success'))
        
        return {
            'total_updates': total_updates,
            'successful_updates': successful_updates,
            'success_rate': (successful_updates / total_updates * 100) if total_updates > 0 else 0,
            'is_running': self.is_running,
            'recent_updates': list(self.update_history.keys())[-10:]  # Last 10 updated users
        }

# Global instance
data_update_strategy = None

def initialize_update_strategy(users_collection=None, in_memory_users=None):
    """Initialize the global update strategy"""
    global data_update_strategy
    data_update_strategy = DataUpdateStrategy(users_collection, in_memory_users)
    data_update_strategy.start_strategy()
    return data_update_strategy