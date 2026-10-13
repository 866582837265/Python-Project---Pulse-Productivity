# pulse/backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
import random
try:
    from ml_skill_assessment import skill_predictor
except ImportError:
    skill_predictor = None
    print("[WARNING] ml_skill_assessment not found")

try:
    from quiz_data import QUIZ_QUESTIONS, ROADMAPS, get_domain_id
except ImportError:
    QUIZ_QUESTIONS = {"programming": []}
    ROADMAPS = {}
    get_domain_id = lambda x: "programming"
    print("[WARNING] quiz_data not found")

try:
    from ml_predictor import predictor
except ImportError:
    class MockPredictor:
        def load_model(self): pass
        def predict_skill_level(self, correct, total, time):
            """Fixed ML level classification with proper thresholds"""
            percentage = (correct / total) * 100 if total > 0 else 0
            print(f"🔍 ML Prediction: {correct}/{total} = {percentage:.1f}%")
            
            # Corrected thresholds based on requirements
            if correct <= 2:  # 0-2 correct answers
                level = "Beginner"
            elif correct <= 4:  # 3-4 correct answers  
                level = "Intermediate"
            else:  # 5+ correct answers
                level = "Expert"
            
            print(f"✅ Level assigned: {level}")
            return level
    predictor = MockPredictor()
    print("[WARNING] ml_predictor not found, using corrected mock predictor")

try:
    from roadmap_generator import roadmap_generator
except ImportError:
    roadmap_generator = None
    print("[WARNING] roadmap_generator not found")

from roadmap_agent import generate_roadmap, unlock_next_topic
from coding_platforms import CodingPlatformTracker
from progress_sync_service import initialize_sync_service, progress_sync_service
from ml_progress_analyzer import progress_analyzer
from data_extraction_service import data_extractor
from data_update_strategy import initialize_update_strategy, data_update_strategy

try:
    from ai.gemini_service import gemini_service
except ImportError:
    class MockGeminiService:
        def generate_questions(self, topic, difficulty, count=10):
            return [{"id": f"q{i}", "question": f"Sample question {i} about {topic}", "options": ["A", "B", "C", "D"], "answer": 0, "explanation": "Sample explanation"} for i in range(count)]
    gemini_service = MockGeminiService()
    print("[WARNING] gemini_service not found, using mock")

try:
    from ai.enhanced_gemini_service import enhanced_gemini_service
except ImportError:
    class MockEnhancedGeminiService:
        def generate_topic_content(self, topic_name, difficulty):
            # Generate 5 coding problems and 5 MCQs per topic
            coding_questions = []
            mcq_questions = []
            
            # Generate 5 coding problems
            for i in range(1, 6):
                coding_questions.append({
                    "id": f"code_{i}",
                    "title": f"{topic_name} Problem {i}",
                    "description": f"Solve a {difficulty.lower()} level {topic_name} problem using Java. This problem focuses on {topic_name} concepts and algorithms.",
                    "difficulty": difficulty,
                    "sample_input": f"Input: Example data {i}",
                    "sample_output": f"Output: Expected result {i}",
                    "hints": [f"Consider {topic_name} properties", f"Think about {difficulty.lower()} level approaches", "Use Java best practices"],
                    "starter_code": "public class Main {\n    public static void main(String[] args) {\n        // Write your Java solution here\n        System.out.println(\"Hello, Java!\");\n    }\n}"
                })
            
            # Generate 5 MCQ questions
            for i in range(1, 6):
                mcq_questions.append({
                    "id": f"mcq_{i}",
                    "question": f"Question {i}: What is an important concept in {topic_name}?",
                    "options": [f"Correct answer for {topic_name}", f"Incorrect option A", f"Incorrect option B", f"Incorrect option C"],
                    "correct_answer": 0,
                    "explanation": f"This is a fundamental concept in {topic_name} that every developer should understand."
                })
            
            return {
                "coding_questions": coding_questions,
                "mcq_questions": mcq_questions
            }
    enhanced_gemini_service = MockEnhancedGeminiService()
    print("[WARNING] enhanced_gemini_service not found, using enhanced Java mock with 5+5 questions")

try:
    from ai.gemini_question_service import gemini_question_service
except ImportError:
    gemini_question_service = None
    print("[WARNING] gemini_question_service not found")

try:
    from ai.fixed_gemini_service import fixed_gemini_service
except ImportError:
    fixed_gemini_service = None
    print("[WARNING] fixed_gemini_service not found")

try:
    from dashboard_service import DashboardService, CodingPlatformService
except ImportError:
    class MockDashboardService:
        def __init__(self, *args): pass
    class MockCodingPlatformService:
        def __init__(self, *args): pass
        def fetch_leetcode_stats(self, username): return None
        def fetch_hackerrank_stats(self, username): return None
        def fetch_hackerearth_stats(self, username): return None
    DashboardService = MockDashboardService
    CodingPlatformService = MockCodingPlatformService
    print("[WARNING] dashboard_service not found, using mock")

# Load environment variables
load_dotenv()

# -------------------------------
# App Setup
# -------------------------------
app = Flask(__name__)
app.secret_key = os.getenv('JWT_SECRET', 'fallback-secret-key')
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"], methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# -------------------------------
# MongoDB Connection & Fallback Storage
# -------------------------------
mongo_db, users_collection, mongo_client = None, None, None
in_memory_users = {}  # Fallback storage for testing

# File-based persistence for development
import json
USERS_FILE = 'users_data.json'

def load_users_from_file():
    """Load users from JSON file"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                data = json.load(f)
                # Convert datetime strings back to datetime objects
                for email, user in data.items():
                    if 'createdAt' in user and isinstance(user['createdAt'], str):
                        user['createdAt'] = datetime.fromisoformat(user['createdAt'].replace('Z', '+00:00'))
                    if 'last_assessment_date' in user and isinstance(user['last_assessment_date'], str):
                        user['last_assessment_date'] = datetime.fromisoformat(user['last_assessment_date'].replace('Z', '+00:00'))
                return data
    except Exception as e:
        print(f"[WARNING] Failed to load users from file: {e}")
    return {}

def save_users_to_file():
    """Save users to JSON file"""
    try:
        # Convert datetime objects to strings for JSON serialization
        data_to_save = {}
        for email, user in in_memory_users.items():
            user_copy = user.copy()
            if 'createdAt' in user_copy and hasattr(user_copy['createdAt'], 'isoformat'):
                user_copy['createdAt'] = user_copy['createdAt'].isoformat()
            if 'last_assessment_date' in user_copy and hasattr(user_copy['last_assessment_date'], 'isoformat'):
                user_copy['last_assessment_date'] = user_copy['last_assessment_date'].isoformat()
            data_to_save[email] = user_copy
        
        with open(USERS_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=2, default=str)
        print(f"[INFO] Saved {len(data_to_save)} users to file")
    except Exception as e:
        print(f"[WARNING] Failed to save users to file: {e}")

try:
    mongodb_uri = os.getenv('MONGODB_URI', '')
    print(f"[DEBUG] MongoDB URI configured: {'Yes' if mongodb_uri else 'No'}")
    
    if mongodb_uri and mongodb_uri.strip():
        print("[INFO] Attempting MongoDB connection...")
        mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
        mongo_db = mongo_client["pulseDB"]
        users_collection = mongo_db["users"]
        
        # Test the connection
        mongo_client.admin.command('ping')
        print("[SUCCESS] Connected to MongoDB Atlas")
        
        # Test user count
        user_count = users_collection.count_documents({})
        print(f"[INFO] Found {user_count} existing users in database")
    else:
        print("[WARNING] No MongoDB URI provided, using in-memory storage for testing")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    print(f"[ERROR] Error details: {type(e).__name__}: {str(e)}")
    print("[WARNING] Falling back to file-based storage for testing")
    mongo_db, users_collection, mongo_client = None, None, None
    
    # Load existing users from file
    in_memory_users = load_users_from_file()
    print(f"[INFO] Loaded {len(in_memory_users)} users from file storage")

# Collections
quiz_responses_collection = None
roadmaps_collection = None
coding_profiles_collection = None
pomodoro_sessions_collection = None
question_packs_collection = None
topic_content_collection = None
if mongo_db is not None:
    quiz_responses_collection = mongo_db["quiz_responses"]
    roadmaps_collection = mongo_db["roadmaps"]
    coding_profiles_collection = mongo_db["coding_profiles"]
    pomodoro_sessions_collection = mongo_db["pomodoro_sessions"]
    question_packs_collection = mongo_db["question_packs"]
    topic_content_collection = mongo_db["topic_content"]
    print("[INFO] MongoDB collections initialized including question_packs")

# Initialize ML models
if skill_predictor:
    try:
        skill_predictor.load_model()
    except Exception as e:
        print(f"[WARNING] Failed to load skill_predictor: {e}")

if predictor:
    try:
        predictor.load_model()
    except Exception as e:
        print(f"[WARNING] Failed to load predictor: {e}")

# Initialize services
dashboard_service = DashboardService(users_collection, quiz_responses_collection)
coding_platform_service = CodingPlatformService(coding_profiles_collection)
coding_tracker = CodingPlatformTracker()

# Initialize automatic progress sync service
try:
    sync_service = initialize_sync_service(users_collection, in_memory_users)
    print("[SUCCESS] Progress sync service initialized")
except Exception as e:
    print(f"[WARNING] Failed to initialize sync service: {e}")
    sync_service = None

# Initialize ML progress analyzer
try:
    if not progress_analyzer.load_model():
        progress_analyzer.train_model()
        progress_analyzer.save_model()
    print("[SUCCESS] ML progress analyzer initialized")
except Exception as e:
    print(f"[WARNING] Failed to initialize ML analyzer: {e}")

# Initialize intelligent data update strategy
try:
    update_strategy = initialize_update_strategy(users_collection, in_memory_users)
    print("[SUCCESS] Intelligent data update strategy initialized")
except Exception as e:
    print(f"[WARNING] Failed to initialize update strategy: {e}")
    update_strategy = None

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"❌ Backend error: {e}")
    import traceback
    traceback.print_exc()
    return jsonify({"success": False, "error": str(e)}), 500

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# -------------------------------
# Helper Functions
# -------------------------------
def get_user_by_email(email):
    """Safely get user data by email with proper isolation"""
    if users_collection is not None:
        user = users_collection.find_one({"email": email})
        if user:
            print(f"[DB] Found user: {email} - Assessment: {user.get('assessment_taken', False)}")
        return user
    else:
        user = in_memory_users.get(email)
        if user:
            print(f"[MEMORY] Found user: {email} - Assessment: {user.get('assessment_taken', False)}")
        return user

def update_user_data(email, update_data):
    """Safely update user data with proper isolation"""
    if users_collection is not None:
        result = users_collection.update_one({"email": email}, {"$set": update_data})
        print(f"[DB] Updated user {email}: {result.modified_count} documents modified")
        return result.modified_count > 0
    else:
        if email in in_memory_users:
            in_memory_users[email].update(update_data)
            save_users_to_file()  # Persist to file
            print(f"[FILE] Updated user {email} in file storage")
            return True
        return False

def calculate_login_streak(login_dates):
    """Calculate consecutive login streak up to today"""
    if not login_dates:
        return 0
    
    from datetime import datetime, timedelta
    today = datetime.now(timezone.utc).date()
    dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in sorted(login_dates)]
    
    # Check if user logged in today or yesterday
    if dates[-1] < today - timedelta(days=1):
        return 0
    
    streak = 1
    for i in range(len(dates) - 2, -1, -1):
        if dates[i] == dates[i + 1] - timedelta(days=1):
            streak += 1
        else:
            break
    
    return streak

def get_daily_quote(user_id):
    """Get daily motivational quote based on user ID and date"""
    quotes = [
        "Every expert was once a beginner.",
        "Code is like humor. When you have to explain it, it's bad.",
        "The best time to plant a tree was 20 years ago. The second best time is now.",
        "Progress, not perfection.",
        "A year from now you may wish you had started today.",
        "The only way to do great work is to love what you do.",
        "Don't watch the clock; do what it does. Keep going.",
        "Success is the sum of small efforts repeated day in and day out.",
        "The expert in anything was once a beginner.",
        "Coding is not just about solving problems, it's about thinking differently.",
        "Every line of code is a step towards mastery.",
        "Debugging is twice as hard as writing the code in the first place.",
        "Programs must be written for people to read, and only incidentally for machines to execute.",
        "The most important property of a program is whether it accomplishes the intention of its user.",
        "Simplicity is the ultimate sophistication."
    ]
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    hash_input = f"{user_id}{today}"
    quote_index = hash(hash_input) % len(quotes)
    return quotes[quote_index]

def make_json_safe(obj):
    """Convert ObjectIds to strings for JSON serialization"""
    if isinstance(obj, list):
        return [make_json_safe(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
        return str(obj)
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return obj

# -------------------------------
# JWT Helper Functions
# -------------------------------
def generate_token(user_id, email):
    """Generate JWT token for user"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, app.secret_key, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"}), 200
            
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if payload is None:
            return jsonify({'success': False, 'error': 'Token is invalid or expired'}), 401
        
        # Defensive check for user_email
        if not payload.get('email'):
            return jsonify({'success': False, 'error': 'Invalid session'}), 401
        
        # Add user info to request context
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

# -------------------------------
# General Routes
# -------------------------------
@app.route("/")
def health():
    return jsonify({"app": "Pulse", "status": "ok", "db_connected": users_collection is not None})

@app.route("/api/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint to verify server is working"""
    return jsonify({"message": "Server is working", "timestamp": datetime.now(timezone.utc).isoformat()})

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for frontend connectivity testing"""
    return jsonify({"status": "ok", "message": "Backend is healthy", "timestamp": datetime.now(timezone.utc).isoformat()}), 200

@app.route("/api/dashboard", methods=["GET", "OPTIONS"])
@token_required
def dashboard():
    """Enhanced dashboard with user-specific data isolation"""
    try:
        user_email = request.current_user["email"]
        user_id = request.current_user["user_id"]
        
        # Fresh database lookup for THIS user only
        user = None
        if users_collection is not None:
            user = users_collection.find_one({"email": user_email})
        else:
            user = in_memory_users.get(user_email)
        
        if not user:
            print(f"[ERROR] Dashboard: User not found - {user_email}")
            return jsonify({"success": False, "message": "User not found"}), 404
        
        print(f"[DASHBOARD] Loading data for user: {user_email} - Assessment: {user.get('assessment_taken', False)}")
        
        # Get today's sessions count for THIS user only
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if pomodoro_sessions_collection is not None:
            today_sessions = pomodoro_sessions_collection.count_documents({
                "userEmail": user_email,
                "date": today
            })
        else:
            today_sessions = 0
        
        # Calculate roadmap progress for THIS user only
        roadmap = user.get("roadmap", [])
        if roadmap and isinstance(roadmap, list):
            completed = len([t for t in roadmap if t.get("status") == "completed"])
            roadmap_progress_percent = round((completed / len(roadmap)) * 100, 1) if roadmap else 0
        else:
            roadmap_progress_percent = 0
        
        # Get platform progress for dashboard display
        platform_progress = user.get("platform_progress", {})
        coding_platform_stats = {
            "leetcode": {
                "solvedTotal": platform_progress.get("leetcode", {}).get("solved", 0),
                "solvedThisWeek": 0,  # This would need weekly tracking
                "contests": 0
            },
            "hackerrank": {
                "stars": platform_progress.get("hackerrank", {}).get("stars", 0),
                "certificates": platform_progress.get("hackerrank", {}).get("certificates", 0)
            }
        }
        
        return jsonify({
            "name": user.get("username", "User"),
            "username": user.get("username", "User"),  # Ensure username is available
            "predicted_level": user.get("predicted_level"),
            "assessment_taken": user.get("assessment_taken", False),
            "roadmap_progress_percent": roadmap_progress_percent,
            "pomodoro_count": user.get("pomodoro_count", 0),
            "today_sessions": today_sessions,
            "streak_days": user.get("login_streak_days", 0),
            "login_days_total": len(user.get("login_dates", [])),
            "last_login_at": user.get("last_login_at"),
            "motivational_quote": get_daily_quote(user_id),
            "coding_platform_stats": coding_platform_stats
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Dashboard error: {e}")
        return jsonify({"success": False, "message": "Failed to retrieve dashboard data"}), 500

@app.route("/api/user/profile", methods=["GET", "OPTIONS"])
@token_required
def get_user_profile():
    try:
        user_email = request.current_user["email"]
        
        # Fresh lookup for THIS user only
        user = get_user_by_email(user_email)
        
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Auto-fetch platform progress if links exist but progress is missing
        profile_links = user.get("profile_links", {})
        platform_progress = user.get("platform_progress", {})
        
        # If user has platform links but no cached progress, fetch it automatically
        if profile_links and not platform_progress:
            print(f"[PROFILE] Auto-fetching progress for {user_email}")
            try:
                if profile_links.get("leetcode"):
                    leetcode_stats = fetch_leetcode_stats(profile_links["leetcode"])
                    if leetcode_stats:
                        platform_progress["leetcode"] = leetcode_stats
                
                if profile_links.get("hackerrank"):
                    hackerrank_stats = fetch_hackerrank_stats(profile_links["hackerrank"])
                    if hackerrank_stats:
                        platform_progress["hackerrank"] = hackerrank_stats
                
                # Update user with fetched progress
                if platform_progress:
                    overall_score = calculate_overall_score(platform_progress)
                    update_user_data(user_email, {
                        "platform_progress": platform_progress,
                        "overall_score": overall_score
                    })
                    print(f"[PROFILE] Auto-updated progress for {user_email}")
            except Exception as fetch_error:
                print(f"[PROFILE] Auto-fetch failed: {fetch_error}")

        return jsonify({
            "name": user.get("username", "User"),
            "username": user.get("username", "User"),  # Ensure username is available
            "email": user_email,
            "skill_level": user.get("skill_level", "Beginner"),
            "avatar": user.get("avatar"),
            "join_date": user.get("createdAt", datetime.now(timezone.utc)).strftime("%Y-%m-%d") if user.get("createdAt") else "2024-01-15",
            "total_problems_solved": user.get("problems_solved", 0),
            "current_streak": user.get("streak", 0),
            "learning_style": user.get("learning_style", "Balanced"),
            "assessment_taken": user.get("assessment_taken", False),
            "predicted_level": user.get("predicted_level"),
            "profile_links": profile_links,
            "platform_progress": platform_progress,
            "overall_score": user.get("overall_score", 0)
        })
    except Exception as e:
        print(f"[ERROR] Profile error for {user_email}: {e}")
        return jsonify({"message": "Failed to retrieve profile"}), 500

@app.route("/api/user/progress", methods=["GET", "OPTIONS"])
@token_required
def get_user_progress():
    try:
        user_email = request.current_user["email"]
        
        user = None
        if users_collection is not None:
            user = users_collection.find_one({"email": user_email})
        else:
            user = in_memory_users.get(user_email)
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        return jsonify({
            "problems_solved": user.get("problems_solved", 0),
            "streak": user.get("streak", 0),
            "session_time": 35,
            "completion_rate": 0.78,
            "topics_completed": 8,
            "skill_level": user.get("skill_level", "Beginner"),
            "learning_style": user.get("learning_style", "Balanced"),
            "streak_risk": "Low"
        })
    except Exception as e:
        print(f"Progress error: {e}")
        return jsonify({"message": "Failed to retrieve progress"}), 500

# -------------------------------
# Roadmap Routes - FIXED
# -------------------------------
@app.route("/api/roadmap", methods=["GET", "OPTIONS"])
@token_required
def get_roadmap():
    """Get user's personalized Duolingo-style roadmap"""
    try:
        user_email = request.current_user["email"]
        print(f"Fetching roadmap for: {user_email}")
        
        # Fresh lookup for THIS user's data
        user = get_user_by_email(user_email)
        
        if not user:
            print(f"Roadmap error: User not found - {user_email}")
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Check THIS user's assessment state
        assessment_taken = user.get("assessment_taken", False)
        predicted_level = user.get("predicted_level")
        roadmap = user.get("roadmap", [])
        
        print(f"[ROADMAP] User {user_email} - Assessment: {assessment_taken}, Level: {predicted_level}, Roadmap items: {len(roadmap)}")
        
        # If user hasn't taken assessment, return LEVEL_NOT_SET
        if not assessment_taken or not predicted_level:
            print(f"Level not set for {user_email}")
            return jsonify({
                "success": False, 
                "code": "LEVEL_NOT_SET",
                "error": "Please take the skill assessment first to generate your personalized roadmap."
            }), 404
        
        # Check if THIS user has existing roadmap
        if roadmap and isinstance(roadmap, list) and len(roadmap) > 0:
            # Always return roadmap sorted by order
            roadmap.sort(key=lambda x: x.get("order", 0))
            print(f" Roadmap returned with {len(roadmap)} nodes")
            return jsonify({
                "success": True,
                "roadmap": roadmap,
                "level": predicted_level
            }), 200
        
        # Generate roadmap for THIS user with enhanced debugging
        print(f"🧠 User {user_email} predicted as {predicted_level}")
        print(f"🔍 Regenerating roadmap for level: {predicted_level}")
        try:
            from roadmap_agent import generate_roadmap as generate_duolingo_roadmap
            roadmap = generate_duolingo_roadmap(predicted_level)
            print(f"[ROADMAP] Generated roadmap type: {type(roadmap)}, length: {len(roadmap) if roadmap else 0}")
            
            if roadmap and isinstance(roadmap, list):
                topic_titles = [topic.get('title', 'Array Basics') for topic in roadmap]
                print(f"🗺️ Roadmap topics for {predicted_level}: {len(roadmap)} items")
                print(f"✅ Roadmap topics returned: {topic_titles}")
            else:
                print(f"❌ Roadmap is not a list or is empty")
                
        except Exception as gen_error:
            print(f"❌ Roadmap generation error: {gen_error}")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": f"Roadmap generation failed: {str(gen_error)}"}), 500
        
        if not roadmap:
            print(f"Failed to generate roadmap for {user_email}")
            return jsonify({"success": False, "error": "Failed to generate roadmap"}), 500
        
        # Ensure JSON serializable - convert any ObjectId to string
        roadmap = make_json_safe(roadmap)
        
        # Sort by order before saving
        roadmap.sort(key=lambda x: x.get("order", 0))
        
        # Save roadmap for THIS user only
        update_data = {
            "roadmap": roadmap, 
            "updatedAt": datetime.now(timezone.utc)
        }
        
        success = update_user_data(user_email, update_data)
        
        if success:
            print(f"✅ Roadmap stored successfully for {user_email}")
            print(f"🗺️ Roadmap topics for {predicted_level}: {len(roadmap)} items")
        else:
            print(f"❌ Failed to save roadmap for user: {user_email}")
        
        return jsonify({
            "success": True,
            "roadmap": roadmap,
            "level": predicted_level
        }), 200
        
    except Exception as e:
        print(f"Roadmap error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Failed to load roadmap"}), 500

@app.route("/api/roadmap/debug", methods=["GET", "OPTIONS"])
@token_required
def debug_roadmap():
    """Debug endpoint to inspect user's roadmap data"""
    try:
        user_email = request.current_user["email"]
        user = get_user_by_email(user_email)
        
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        roadmap = user.get("roadmap", [])
        
        debug_info = {
            "success": True,
            "user_email": user_email,
            "roadmap_count": len(roadmap),
            "topics": []
        }
        
        for topic in roadmap:
            debug_info["topics"].append({
                "id": topic.get("id"),
                "title": topic.get("title"),
                "status": topic.get("status"),
                "order": topic.get("order")
            })
        
        return jsonify(debug_info), 200
        
    except Exception as e:
        print(f"[ERROR] Debug roadmap failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/roadmap/test/<level>", methods=["GET"])
def test_roadmap(level):
    """Debug endpoint to test roadmap generation without DB write"""
    try:
        print(f"Testing roadmap generation for level: {level}")
        from roadmap_agent import generate_roadmap as generate_duolingo_roadmap
        roadmap = generate_duolingo_roadmap(level)
        
        if roadmap:
            print(f" Test roadmap generated: {len(roadmap)} nodes")
            return jsonify({
                "success": True,
                "level": level,
                "roadmap": roadmap,
                "count": len(roadmap),
                "debug": True
            }), 200
        else:
            print(f"Test roadmap generation returned None")
            return jsonify({"success": False, "error": "Roadmap generation returned None"}), 500
    except Exception as e:
        print(f"Test roadmap error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/roadmap/topic/<topic_id>/complete", methods=["POST", "OPTIONS"])
@token_required
def complete_roadmap_topic(topic_id):
    """Mark topic as completed and unlock next node"""
    try:
        user_email = request.current_user["email"]
        print(f"Topic completed: {topic_id} by {user_email}")
        
        user = get_user_by_email(user_email)
        if not user or not user.get("roadmap"):
            return jsonify({"success": False, "error": "Roadmap not found"}), 404
        
        roadmap = user["roadmap"]
        updated_roadmap = unlock_next_topic(roadmap, topic_id)
        
        # Sort by order to ensure proper sequence
        updated_roadmap.sort(key=lambda x: x.get("order", 0))
        
        # Recompute progress percentage
        completed_count = len([t for t in updated_roadmap if t.get("status") == "completed"])
        progress_percent = round((completed_count / len(updated_roadmap)) * 100, 1)
        
        update_data = {
            "roadmap": updated_roadmap,
            "roadmap_progress_percent": progress_percent,
            "updatedAt": datetime.now(timezone.utc)
        }
        
        success = update_user_data(user_email, update_data)
        
        if success:
            print(f"Topic completed: {topic_id} -> progress: {progress_percent}%")
            return jsonify({
                "success": True,
                "message": "Topic completed and next topic unlocked",
                "roadmap": updated_roadmap,
                "progress_percent": progress_percent
            }), 200
        else:
            return jsonify({"success": False, "error": "Failed to update progress"}), 500
        
    except Exception as e:
        print(f"[ERROR] Complete topic failed: {e}")
        return jsonify({"success": False, "error": "Failed to complete topic"}), 500

# -------------------------------
# Topic Detail & Practice Routes
# -------------------------------
@app.route("/api/roadmap/topic/<topic_id>", methods=["GET", "OPTIONS"])
@token_required
def get_topic_details(topic_id):
    """Get topic details with comprehensive 500 error prevention"""
    user_email = None
    try:
        # Handle OPTIONS preflight request
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"}), 200
        
        # 1. Validate request and authentication first
        if not topic_id or not str(topic_id).strip():
            return jsonify({"success": False, "error": "Topic ID is required"}), 400
        
        user_email = request.current_user.get("email")
        if not user_email or not str(user_email).strip():
            return jsonify({"success": False, "error": "Authentication required"}), 401
        
        print(f"🔍 Topic request for topic_id={topic_id} user={user_email}")
        
        # 2. Robust user lookup with validation
        user = get_user_by_email(user_email)
        if not user or not isinstance(user, dict):
            print(f"❌ User not found: {user_email}")
            return jsonify({"success": False, "error": "User not found"}), 404
        
        roadmap = user.get("roadmap", [])
        if not roadmap or not isinstance(roadmap, list) or len(roadmap) == 0:
            print(f"❌ No roadmap found for user: {user_email}")
            return jsonify({"success": False, "error": "Roadmap not found. Please complete the skill assessment first."}), 404
        
        # 3. Robust topic lookup logic with ObjectId conversion
        topic_info = None
        topic_id_str = str(topic_id).strip()
        
        # Strategy A: Exact ID match (stringified IDs)
        for topic in roadmap:
            if not isinstance(topic, dict):
                continue
            topic_id_from_roadmap = str(topic.get("id", "")).strip() if topic.get("id") is not None else ""
            if topic_id_from_roadmap and topic_id_from_roadmap == topic_id_str:
                topic_info = topic
                break
        
        # Strategy B: Fallback to case-insensitive title match
        if not topic_info:
            topic_id_lower = topic_id_str.lower()
            for topic in roadmap:
                if not isinstance(topic, dict):
                    continue
                topic_title = str(topic.get("title", "")).strip().lower()
                if topic_title and topic_title == topic_id_lower:
                    topic_info = topic
                    break
        
        if not topic_info or not isinstance(topic_info, dict):
            available_topics = []
            for t in roadmap[:3]:
                if isinstance(t, dict):
                    tid = str(t.get('id', 'no-id'))
                    title = str(t.get('title', 'no-title'))
                    available_topics.append(f"{tid}:{title}")
            print(f"❌ Topic {topic_id} not found. Available: {available_topics}")
            return jsonify({"success": False, "error": "Topic not found"}), 404
        
        print(f"✅ Topic found: {topic_info.get('title')} (order: {topic_info.get('order', 0)})")
        
        # 4. Ensure question pack retrieval is safe
        question_pack = None
        pack_id = None
        
        if question_packs_collection is not None:
            try:
                question_pack = question_packs_collection.find_one({
                    "user_email": user_email,
                    "topic_id": str(topic_info.get("id", ""))
                })
                if question_pack and isinstance(question_pack, dict):
                    pack_id = str(question_pack.get("_id", ""))
                    print(f"🔄 Found question_pack_id: {pack_id}")
                else:
                    question_pack = None
            except Exception as db_error:
                print(f"⚠️ Database lookup error (non-fatal): {db_error}")
                question_pack = None
        
        # 5. Generate or validate question pack with multiple fallbacks
        content = None
        
        if not question_pack:
            print(f"⚙️ No pack found, generating for {topic_info.get('title')}")
            try:
                content = generate_safe_question_pack(topic_info, user_email)
                if not content or not validate_question_pack_structure(content):
                    print(f"⚠️ Generated pack failed validation, using emergency fallback")
                    content = generate_emergency_fallback(topic_info)
            except Exception as gen_error:
                print(f"❌ Question generation failed: {gen_error}")
                content = generate_emergency_fallback(topic_info)
        else:
            # Validate existing pack structure
            try:
                coding_questions = question_pack.get("coding_questions", [])
                mcq_questions = question_pack.get("mcq_questions", [])
                
                # Validate that questions are lists and have required count
                if (not isinstance(coding_questions, list) or 
                    not isinstance(mcq_questions, list) or 
                    len(coding_questions) < 5 or 
                    len(mcq_questions) < 5):
                    print(f"⚙️ Incomplete pack found, regenerating")
                    content = generate_safe_question_pack(topic_info, user_email)
                    if not content or not validate_question_pack_structure(content):
                        print(f"⚠️ Regenerated pack failed validation, using emergency fallback")
                        content = generate_emergency_fallback(topic_info)
                else:
                    # Validate individual questions have required fields
                    valid_pack = True
                    for q in coding_questions[:5]:  # Check first 5
                        if not isinstance(q, dict) or not q.get('id') or not q.get('title'):
                            valid_pack = False
                            break
                    
                    for q in mcq_questions[:5]:  # Check first 5
                        if (not isinstance(q, dict) or not q.get('id') or 
                            not q.get('question') or not isinstance(q.get('options'), list) or
                            len(q.get('options', [])) != 4):
                            valid_pack = False
                            break
                    
                    if valid_pack:
                        content = {
                            "coding_questions": coding_questions,
                            "mcq_questions": mcq_questions
                        }
                    else:
                        print(f"⚙️ Pack validation failed, regenerating")
                        content = generate_safe_question_pack(topic_info, user_email)
                        if not content or not validate_question_pack_structure(content):
                            content = generate_emergency_fallback(topic_info)
            except Exception as validate_error:
                print(f"❌ Pack validation error: {validate_error}")
                content = generate_emergency_fallback(topic_info)
        
        # 6. Final content validation and JSON-safety
        if not content or not isinstance(content, dict):
            print(f"❌ No valid content generated, using emergency fallback")
            content = generate_emergency_fallback(topic_info)
        
        # Convert ObjectIds and ensure JSON serializable
        content = make_json_safe(content)
        
        # Final structure validation before returning
        if not validate_question_pack_structure(content):
            print(f"❌ Final validation failed, using emergency fallback")
            content = generate_emergency_fallback(topic_info)
            content = make_json_safe(content)
        
        # 7. Build canonical successful payload with safe field access
        try:
            topic_response = {
                "id": str(topic_info.get("id", "")),
                "title": str(topic_info.get("title", "Array Basics")),
                "description": str(topic_info.get("description", f"Master {topic_info.get('title', 'this topic')} with comprehensive practice")),
                "difficulty": str(topic_info.get("difficulty", "Beginner")),
                "order": int(topic_info.get("order", 0)) if topic_info.get("order") is not None else 0,
                "status": str(topic_info.get("status", "locked")),
                "resources": list(topic_info.get("resources", []))
            }
        except Exception as response_error:
            print(f"⚠️ Response building error: {response_error}")
            topic_response = {
                "id": str(topic_id),
                "title": "Array Basics",
                "description": "Practice topic",
                "difficulty": "Beginner",
                "order": 0,
                "status": "available",
                "resources": []
            }
        
        coding_count = len(content.get("coding_questions", []))
        mcq_count = len(content.get("mcq_questions", []))
        
        print(f"✅ Returning topic with {coding_count} coding questions and {mcq_count} mcqs")
        
        return jsonify({
            "success": True,
            "topic": topic_response,
            "coding_questions": content.get("coding_questions", []),
            "mcq_questions": content.get("mcq_questions", [])
        }), 200
        
    except Exception as e:
        error_msg = f"Topic load error for {user_email or 'unknown'}: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False, 
            "error": "Internal server error", 
            "details": str(e)
        }), 500

def generate_safe_question_pack(topic_info, user_email):
    """Generate question pack with comprehensive error handling"""
    try:
        topic_title = str(topic_info.get("title", "Programming"))
        difficulty = str(topic_info.get("difficulty", "Beginner"))
        
        print(f"🔄 Generating question pack for topic {topic_title}")
        
        # Try fixed Gemini service first
        if fixed_gemini_service and hasattr(fixed_gemini_service, 'generate_question_pack'):
            try:
                print(f"🤖 Attempting Gemini generation for {topic_title}")
                content = fixed_gemini_service.generate_question_pack(topic_title, difficulty)
                if content and validate_question_pack_structure(content):
                    print(f"✅ Gemini generation successful")
                    save_question_pack_to_db(content, topic_info, user_email)
                    return content
                else:
                    print(f"⚠️ Gemini generated invalid structure")
            except Exception as gemini_error:
                print(f"❌ Gemini generation failed: {gemini_error}")
        else:
            print(f"⚠️ Fixed Gemini service not available")
        
        # Fallback to quality questions
        print(f"🔄 Using quality fallback for {topic_title}")
        content = generate_quality_fallback(topic_info)
        if content and validate_question_pack_structure(content):
            save_question_pack_to_db(content, topic_info, user_email)
            return content
        else:
            print(f"⚠️ Quality fallback failed validation")
            return generate_emergency_fallback(topic_info)
        
    except Exception as e:
        print(f"❌ Question pack generation failed: {e}")
        return generate_emergency_fallback(topic_info)

def generate_quality_fallback(topic_info):
    """Generate high-quality fallback questions using predefined topic questions"""
    topic_title = str(topic_info.get("title", "Programming"))
    print(f"🔍 Generating questions for topic: '{topic_title}'")
    
    # Direct mapping for known topics
    topic_questions = {
        "Arrays Basics": {
            "mcq_questions": [
                {"id": "arrays_mcq_1", "question": "Which of the following best describes an array?", "options": ["A group of unrelated values", "A list of items stored in continuous memory", "A file containing numbers", "A random collection of data"], "answer_index": 1, "explanation": "Arrays store elements in continuous memory locations."},
                {"id": "arrays_mcq_2", "question": "Array indexing starts from:", "options": ["-1", "0", "1", "Depends on language"], "answer_index": 1, "explanation": "Most programming languages use 0-based indexing."},
                {"id": "arrays_mcq_3", "question": "Accessing an element in an array by index takes:", "options": ["Constant time", "Logarithmic time", "Linear time", "Complex time"], "answer_index": 0, "explanation": "Array access by index is O(1) operation."},
                {"id": "arrays_mcq_4", "question": "Which operation is fastest in arrays?", "options": ["Insert at beginning", "Delete middle element", "Access using index", "Reverse array"], "answer_index": 2, "explanation": "Random access is the fastest array operation."},
                {"id": "arrays_mcq_5", "question": "Which structure stores elements of the same type?", "options": ["Stack", "Array", "Queue", "Tree"], "answer_index": 1, "explanation": "Arrays store elements of the same data type."}
            ],
            "coding_questions": [
                {"id": "arrays_code_1", "title": "Find Largest Element", "description": "Find the largest element in an array of integers.", "sample_input": "arr = [3, 7, 1, 9, 2]", "sample_output": "9", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int findLargest(int[] arr) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "arrays_code_2", "title": "Count Occurrences", "description": "Count how many times a given number appears in an array.", "sample_input": "arr = [1, 2, 3, 2, 2, 4], target = 2", "sample_output": "3", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int countOccurrences(int[] arr, int target) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "arrays_code_3", "title": "Reverse Array", "description": "Print all elements of an array in reverse order.", "sample_input": "arr = [1, 2, 3, 4, 5]", "sample_output": "[5, 4, 3, 2, 1]", "difficulty": "beginner", "starter_code": "public class Solution {\n    public void printReverse(int[] arr) {\n        // Write your solution here\n    }\n}"},
                {"id": "arrays_code_4", "title": "Array Sum", "description": "Find the sum of all elements in an array.", "sample_input": "arr = [1, 2, 3, 4, 5]", "sample_output": "15", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int arraySum(int[] arr) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "arrays_code_5", "title": "Second Largest", "description": "Find the second largest number in an array.", "sample_input": "arr = [3, 7, 1, 9, 2]", "sample_output": "7", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int secondLargest(int[] arr) {\n        // Write your solution here\n        return 0;\n    }\n}"}
            ]
        },
        "String Manipulation": {
            "mcq_questions": [
                {"id": "strings_mcq_1", "question": "A string is a sequence of:", "options": ["Numbers", "Characters", "Functions", "Variables"], "answer_index": 1, "explanation": "Strings are sequences of characters."},
                {"id": "strings_mcq_2", "question": "Which operation gives string length?", "options": ["size()", "count()", "length()", "range()"], "answer_index": 2, "explanation": "The length() method returns character count."},
                {"id": "strings_mcq_3", "question": "'racecar' is special because it is a:", "options": ["Loop", "Palindrome", "Array", "Pattern"], "answer_index": 1, "explanation": "Palindromes read the same forwards and backwards."},
                {"id": "strings_mcq_4", "question": "Joining strings together is called:", "options": ["Combining", "Rewriting", "Concatenation", "Mapping"], "answer_index": 2, "explanation": "String concatenation joins strings together."},
                {"id": "strings_mcq_5", "question": "Which structure is used to store words?", "options": ["Array", "String", "Queue", "Graph"], "answer_index": 1, "explanation": "Strings store sequences of characters."}
            ],
            "coding_questions": [
                {"id": "strings_code_1", "title": "Count Vowels", "description": "Count the number of vowels in a string.", "sample_input": "str = 'hello world'", "sample_output": "3", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int countVowels(String str) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "strings_code_2", "title": "Remove Spaces", "description": "Remove all spaces from a string.", "sample_input": "str = 'hello world'", "sample_output": "'helloworld'", "difficulty": "beginner", "starter_code": "public class Solution {\n    public String removeSpaces(String str) {\n        // Write your solution here\n        return \"\";\n    }\n}"},
                {"id": "strings_code_3", "title": "Check Palindrome", "description": "Check if a string is a palindrome.", "sample_input": "str = 'racecar'", "sample_output": "true", "difficulty": "beginner", "starter_code": "public class Solution {\n    public boolean isPalindrome(String str) {\n        // Write your solution here\n        return false;\n    }\n}"},
                {"id": "strings_code_4", "title": "First Non-Repeating Character", "description": "Find the first non-repeating character in a string.", "sample_input": "str = 'abccba'", "sample_output": "'No non-repeating character'", "difficulty": "beginner", "starter_code": "public class Solution {\n    public char firstNonRepeating(String str) {\n        // Write your solution here\n        return ' ';\n    }\n}"},
                {"id": "strings_code_5", "title": "Reverse String", "description": "Reverse a string without using built-in functions.", "sample_input": "str = 'hello'", "sample_output": "'olleh'", "difficulty": "beginner", "starter_code": "public class Solution {\n    public String reverseString(String str) {\n        // Write your solution here\n        return \"\";\n    }\n}"}
            ]
        },
        "Basic Loops": {
            "mcq_questions": [
                {"id": "loops_mcq_1", "question": "A loop helps in:", "options": ["Repeating tasks", "Stopping code", "Storing data", "Sorting files"], "answer_index": 0, "explanation": "Loops repeat code blocks multiple times."},
                {"id": "loops_mcq_2", "question": "Which loop runs a fixed number of times?", "options": ["while", "do-while", "for", "repeat"], "answer_index": 2, "explanation": "For loops run for predetermined iterations."},
                {"id": "loops_mcq_3", "question": "A loop stops when:", "options": ["The condition becomes false", "It feels tired", "Code ends", "User presses a key"], "answer_index": 0, "explanation": "Loops stop when their condition becomes false."},
                {"id": "loops_mcq_4", "question": "Infinite loops happen when:", "options": ["Condition never becomes false", "No elements exist", "Loop gets skipped", "Code is correct"], "answer_index": 0, "explanation": "Infinite loops occur when condition stays true."},
                {"id": "loops_mcq_5", "question": "Loop iteration means:", "options": ["Resetting", "One complete run", "Copying code", "Pausing"], "answer_index": 1, "explanation": "Each iteration is one loop execution."}
            ],
            "coding_questions": [
                {"id": "loops_code_1", "title": "Print Numbers 1 to N", "description": "Print numbers from 1 to N using a loop.", "sample_input": "n = 5", "sample_output": "1 2 3 4 5", "difficulty": "beginner", "starter_code": "public class Solution {\n    public void printNumbers(int n) {\n        // Write your solution here\n    }\n}"},
                {"id": "loops_code_2", "title": "Count Digits", "description": "Count the number of digits in a number using a loop.", "sample_input": "num = 12345", "sample_output": "5", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int countDigits(int num) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "loops_code_3", "title": "Factorial", "description": "Find factorial of a number using loops.", "sample_input": "n = 5", "sample_output": "120", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int factorial(int n) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "loops_code_4", "title": "Sum of Natural Numbers", "description": "Find sum of first N natural numbers.", "sample_input": "n = 5", "sample_output": "15", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int sumNatural(int n) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "loops_code_5", "title": "Count Even Numbers", "description": "Count even numbers in a given range.", "sample_input": "start = 1, end = 10", "sample_output": "5", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int countEven(int start, int end) {\n        // Write your solution here\n        return 0;\n    }\n}"}
            ]
        },
        "Simple Recursion": {
            "mcq_questions": [
                {"id": "recursion_mcq_1", "question": "Recursion is when a function:", "options": ["Calls another function", "Calls itself", "Stops suddenly", "Repeats loops"], "answer_index": 1, "explanation": "Recursion occurs when a function calls itself."},
                {"id": "recursion_mcq_2", "question": "Every recursive function needs a:", "options": ["Print statement", "Input value", "Base case", "Loop"], "answer_index": 2, "explanation": "Base case prevents infinite recursion."},
                {"id": "recursion_mcq_3", "question": "Recursion ends when:", "options": ["Base case is reached", "Code restarts", "Memory runs out", "Program closes"], "answer_index": 0, "explanation": "Base case stops the recursive calls."},
                {"id": "recursion_mcq_4", "question": "Recursion breaks problems into:", "options": ["Bigger problems", "Completely random parts", "Smaller versions of same problem", "Separate programs"], "answer_index": 2, "explanation": "Recursion divides problems into smaller subproblems."},
                {"id": "recursion_mcq_5", "question": "Without a base case recursion leads to:", "options": ["Faster code", "Infinite calls", "No output", "Loop errors"], "answer_index": 1, "explanation": "Missing base case causes stack overflow."}
            ],
            "coding_questions": [
                {"id": "recursion_code_1", "title": "Factorial", "description": "Find factorial using recursion.", "sample_input": "n = 5", "sample_output": "120", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int factorial(int n) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "recursion_code_2", "title": "Print N to 1", "description": "Print numbers from N to 1 using recursion.", "sample_input": "n = 5", "sample_output": "5 4 3 2 1", "difficulty": "beginner", "starter_code": "public class Solution {\n    public void printReverse(int n) {\n        // Write your solution here\n    }\n}"},
                {"id": "recursion_code_3", "title": "Fibonacci", "description": "Find Nth Fibonacci number.", "sample_input": "n = 6", "sample_output": "8", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int fibonacci(int n) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "recursion_code_4", "title": "Sum of Digits", "description": "Sum of digits using recursion.", "sample_input": "num = 123", "sample_output": "6", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int sumDigits(int num) {\n        // Write your solution here\n        return 0;\n    }\n}"},
                {"id": "recursion_code_5", "title": "Count Array Elements", "description": "Count number of elements in an array recursively.", "sample_input": "arr = [1, 2, 3, 4, 5]", "sample_output": "5", "difficulty": "beginner", "starter_code": "public class Solution {\n    public int countElements(int[] arr, int index) {\n        // Write your solution here\n        return 0;\n    }\n}"}
            ]
        }
    }
    
    # Check if we have predefined questions for this topic
    if topic_title in topic_questions:
        print(f"✅ Using predefined questions for '{topic_title}'")
        return {
            "coding_questions": topic_questions[topic_title]["coding_questions"],
            "mcq_questions": topic_questions[topic_title]["mcq_questions"]
        }
    
    # Try the complete database
    from all_topics_questions import get_topic_questions_complete
    complete_questions = get_topic_questions_complete(topic_title)
    if complete_questions.get("mcqs") and complete_questions.get("coding_questions"):
        print(f"✅ Using complete database questions for '{topic_title}'")
        # Convert format to match expected structure
        mcq_questions = []
        for i, mcq in enumerate(complete_questions["mcqs"]):
            mcq_questions.append({
                "id": f"mcq_{i+1}",
                "question": mcq["question"],
                "options": mcq["options"],
                "answer_index": mcq["options"].index(mcq["correct_answer"]),
                "explanation": f"The correct answer is: {mcq['correct_answer']}"
            })
        
        coding_questions = []
        for i, code in enumerate(complete_questions["coding_questions"]):
            coding_questions.append({
                "id": f"code_{i+1}",
                "title": code["title"],
                "description": code["problem_statement"],
                "sample_input": code["input_format"],
                "sample_output": code["output_format"],
                "difficulty": "beginner",
                "starter_code": f"public class Solution {{\n    // Solve: {code['title']}\n    // {code['problem_statement']}\n    public void solve() {{\n        // Write your solution here\n    }}\n}}"
            })
        
        return {
            "coding_questions": coding_questions,
            "mcq_questions": mcq_questions
        }
    
    # Fallback to generic questions if no predefined ones exist
    print(f"⚠️ No predefined questions for '{topic_title}', using generic fallback")
    difficulty = str(topic_info.get("difficulty", "Beginner"))
    
    coding_questions = []
    for i in range(1, 6):
        coding_questions.append({
            "id": f"code_{i}",
            "title": f"{topic_title} Challenge {i}",
            "description": f"Implement a solution for this {topic_title} problem. Apply {difficulty.lower()} level concepts and focus on clean, efficient code.",
            "sample_input": f"arr = [1, 2, 3, 4, 5], target = {i + 5}",
            "sample_output": f"result = {i * 2}",
            "difficulty": difficulty.lower(),
            "starter_code": f"public class Solution {{\n    public int solve{i}(int[] arr, int target) {{\n        // Implement your {topic_title} solution here\n        return 0;\n    }}\n}}"
        })
    
    mcq_questions = []
    mcq_templates = [
        (f"What is the primary characteristic of {topic_title}?", ["Efficiency", "Simplicity", "Flexibility", "Complexity"], 0),
        (f"Which approach works best for {topic_title} problems?", ["Iterative", "Recursive", "Dynamic", "Greedy"], 0),
        (f"What is the typical time complexity for {topic_title} operations?", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 2),
        (f"In {topic_title}, what should you optimize for?", ["Time", "Space", "Readability", "All of the above"], 3),
        (f"What is a common pitfall in {topic_title} implementation?", ["Off-by-one errors", "Memory leaks", "Infinite loops", "Stack overflow"], 0)
    ]
    
    for i, (question, options, answer_idx) in enumerate(mcq_templates):
        mcq_questions.append({
            "id": f"mcq_{i + 1}",
            "question": question,
            "options": options,
            "answer_index": answer_idx,
            "explanation": f"This is a fundamental aspect of {topic_title} that affects implementation quality."
        })
    
    return {
        "coding_questions": coding_questions,
        "mcq_questions": mcq_questions
    }

def generate_emergency_fallback(topic_info):
    """Emergency fallback when all else fails - guaranteed to work"""
    topic_title = str(topic_info.get("title", "Programming"))
    difficulty = str(topic_info.get("difficulty", "Beginner")).lower()
    
    print(f"🚨 Using emergency fallback for {topic_title}")
    
    # Generate 5 basic but valid coding questions
    coding_questions = []
    for i in range(1, 6):
        coding_questions.append({
            "id": f"code_{i}",
            "title": f"{topic_title} Problem {i}",
            "description": f"Solve this {difficulty} level {topic_title} problem. Focus on understanding the core concepts and implementing a clean solution.",
            "sample_input": f"nums = [1, 2, 3, 4, 5], k = {i}",
            "sample_output": f"result = {i + 1}",
            "difficulty": difficulty,
            "starter_code": f"public class Solution {{\n    public int solve{i}(int[] nums, int k) {{\n        // Implement your {topic_title} solution here\n        // Consider edge cases and optimize for clarity\n        return 0;\n    }}\n}}"
        })
    
    # Generate 5 basic but educational MCQ questions
    mcq_questions = []
    mcq_templates = [
        (f"What is a key characteristic of {topic_title}?", ["Efficiency and clarity", "Complexity only", "Memory usage only", "Speed only"], 0),
        (f"When working with {topic_title}, what should you prioritize?", ["Correctness first", "Speed only", "Memory only", "Code length"], 0),
        (f"What is the typical approach for {topic_title} problems?", ["Understand, plan, implement", "Code immediately", "Guess and check", "Copy solutions"], 0),
        (f"In {topic_title}, what helps with debugging?", ["Clear variable names", "Short code", "Complex logic", "No comments"], 0),
        (f"What makes {topic_title} solutions maintainable?", ["Good structure and comments", "Minimal code", "Complex algorithms", "No documentation"], 0)
    ]
    
    for i, (question, options, answer_idx) in enumerate(mcq_templates):
        mcq_questions.append({
            "id": f"mcq_{i + 1}",
            "question": question,
            "options": options,
            "answer_index": answer_idx,
            "explanation": f"This represents a fundamental principle in {topic_title} that helps create better solutions."
        })
    
    return {
        "coding_questions": coding_questions,
        "mcq_questions": mcq_questions
    }

def validate_question_pack_structure(content):
    """Validate question pack has required structure with detailed logging"""
    if not isinstance(content, dict):
        print(f"❌ Validation failed: content is not a dict, got {type(content)}")
        return False
    
    coding_questions = content.get("coding_questions", [])
    mcq_questions = content.get("mcq_questions", [])
    
    if not isinstance(coding_questions, list) or not isinstance(mcq_questions, list):
        print(f"❌ Validation failed: questions are not lists. Coding: {type(coding_questions)}, MCQ: {type(mcq_questions)}")
        return False
    
    if len(coding_questions) < 5 or len(mcq_questions) < 5:
        print(f"❌ Validation failed: insufficient questions. Coding: {len(coding_questions)}, MCQ: {len(mcq_questions)}")
        return False
    
    # Validate coding questions have required fields
    for i, q in enumerate(coding_questions):
        if not isinstance(q, dict):
            print(f"❌ Validation failed: coding question {i} is not a dict")
            return False
        required_fields = ['id', 'title', 'description', 'sample_input', 'sample_output', 'starter_code']
        for field in required_fields:
            if not q.get(field):
                print(f"❌ Validation failed: coding question {i} missing field '{field}'")
                return False
    
    # Validate MCQ questions have required fields
    for i, q in enumerate(mcq_questions):
        if not isinstance(q, dict):
            print(f"❌ Validation failed: MCQ question {i} is not a dict")
            return False
        if not q.get('id') or not q.get('question'):
            print(f"❌ Validation failed: MCQ question {i} missing id or question")
            return False
        if not isinstance(q.get('options'), list):
            print(f"❌ Validation failed: MCQ question {i} options is not a list")
            return False
        if len(q.get('options', [])) != 4:
            print(f"❌ Validation failed: MCQ question {i} has {len(q.get('options', []))} options, need 4")
            return False
        if q.get('answer_index') not in [0, 1, 2, 3]:
            print(f"❌ Validation failed: MCQ question {i} has invalid answer_index: {q.get('answer_index')}")
            return False
    
    print(f"✅ Validation passed: {len(coding_questions)} coding + {len(mcq_questions)} MCQ questions")
    return True

def save_question_pack_to_db(content, topic_info, user_email):
    """Save question pack to database with error handling"""
    if question_packs_collection is None:
        return None
    
    try:
        pack_doc = {
            "user_email": user_email,
            "topic_id": str(topic_info.get("id")),
            "topic_title": str(topic_info.get("title")),
            "coding_questions": content["coding_questions"],
            "mcq_questions": content["mcq_questions"],
            "createdAt": datetime.now(timezone.utc)
        }
        result = question_packs_collection.insert_one(pack_doc)
        pack_id = str(result.inserted_id)
        print(f"Saved question pack {pack_id}")
        return pack_id
    except Exception as e:
        print(f"Failed to save question pack: {e}")
        return None

# Helper functions moved above - keeping this space for any additional utilities

@app.route("/api/topic/<topic_id>/run-code", methods=["POST", "OPTIONS"])
@token_required
def run_code(topic_id):
    """Execute user code for a coding problem - defaults to Java"""
    try:
        user_email = request.current_user["email"]
        data = request.get_json()
        
        if not data or "code" not in data:
            return jsonify({"success": False, "error": "Code required"}), 400
        
        code = data["code"]
        language = data.get("language", "java").lower()  # Default to Java
        problem_id = data.get("problem_id", "")
        
        print(f"Running {language} code for {user_email} - Problem: {problem_id}")
        
        # Execute code based on language
        try:
            if language == "java":
                result = execute_java_code(code)
            elif language == "python":
                result = execute_python_code(code)
            else:
                result = f"Language '{language}' not supported. Supported: java, python"
            
            # No additional error handling needed for online execution
            
            return jsonify({
                "success": True,
                "output": result,
                "status": "success" if not result.startswith("Error") else "error",
                "language": language
            }), 200
            
        except Exception as exec_error:
            return jsonify({
                "success": True,
                "output": f"Error: {str(exec_error)}",
                "status": "error",
                "language": language
            }), 200
        
    except Exception as e:
        print(f"Code execution failed: {e}")
        return jsonify({"success": False, "error": "Code execution failed"}), 500

def execute_java_code_online(code):
    """Execute Java code using online compiler API"""
    import requests
    import json
    
    try:
        # JDoodle API for online code execution
        url = "https://api.jdoodle.com/v1/execute"
        
        # You can get free API key from https://www.jdoodle.com/compiler-api
        # For demo purposes, using a basic payload
        payload = {
            "clientId": "your_client_id",  # Replace with actual client ID
            "clientSecret": "your_client_secret",  # Replace with actual secret
            "script": code,
            "language": "java",
            "versionIndex": "4"  # Java 17
        }
        
        # Fallback to mock execution if no API credentials
        if payload["clientId"] == "your_client_id":
            return execute_java_code_mock(code)
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("error"):
                return f"Error: {result['error']}"
            return result.get("output", "Code executed successfully (no output)")
        else:
            return f"API Error: {response.status_code}"
            
    except requests.RequestException as e:
        return f"Network Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def execute_java_code_mock(code):
    """Mock Java execution for demonstration"""
    try:
        # Basic syntax validation
        if "public class Main" not in code:
            return "Compilation Error: Main class not found"
        
        if "public static void main" not in code:
            return "Compilation Error: main method not found"
        
        import re
        output_lines = []
        
        # Extract string literals from print statements
        string_patterns = [
            r'System\.out\.println\("([^"]*?)"\)',
            r"System\.out\.println\('([^']*?)'\)",
            r'System\.out\.print\("([^"]*?)"\)',
            r"System\.out\.print\('([^']*?)'\)"
        ]
        
        for pattern in string_patterns:
            matches = re.findall(pattern, code)
            output_lines.extend(matches)
        
        # Handle simple variable declarations and println
        var_declarations = {}
        
        # Extract variable declarations
        int_vars = re.findall(r'int\s+(\w+)\s*=\s*(\d+)', code)
        for var_name, value in int_vars:
            var_declarations[var_name] = value
        
        string_vars = re.findall(r'String\s+(\w+)\s*=\s*"([^"]*?)"', code)
        for var_name, value in string_vars:
            var_declarations[var_name] = value
        
        # Extract println with variables
        var_prints = re.findall(r'System\.out\.println\((\w+)\)', code)
        for var_name in var_prints:
            if var_name in var_declarations:
                output_lines.append(str(var_declarations[var_name]))
            else:
                output_lines.append(f"[{var_name} value]")
        
        # Handle simple expressions
        expr_prints = re.findall(r'System\.out\.println\((\d+\s*[+\-*/]\s*\d+)\)', code)
        for expr in expr_prints:
            try:
                result = eval(expr.replace(' ', ''))
                output_lines.append(str(result))
            except:
                output_lines.append(f"[{expr}]")
        
        # Return collected output
        if output_lines:
            return "\n".join(output_lines)
        
        # Fallback for any println
        if "System.out.println" in code or "System.out.print" in code:
            return "Code executed successfully"
        
        return "Code compiled and executed successfully (no output)"
            
    except Exception as e:
        return f"Mock execution error: {str(e)}"

def execute_java_code(code):
    """Execute Java code using online compiler (no local JDK required)"""
    return execute_java_code_online(code)

def execute_python_code(code):
    """Execute Python code safely"""
    try:
        # Create a safe execution environment
        exec_globals = {"__builtins__": {"print": print, "len": len, "range": range, "list": list, "str": str, "int": int}}
        exec_locals = {}
        
        # Execute the code
        exec(code, exec_globals, exec_locals)
        
        # Try to get the solution function result
        if "solution" in exec_locals:
            return "Code executed successfully. Function 'solution' is defined."
        else:
            return "Code executed successfully."
            
    except Exception as exec_error:
        return f"Error: {str(exec_error)}"

@app.route("/api/topic/<topic_id>/submit-mcq", methods=["POST", "OPTIONS"])
@token_required
def submit_mcq(topic_id):
    """Submit MCQ answers and get results"""
    try:
        user_email = request.current_user["email"]
        data = request.get_json()
        
        if not data or "answers" not in data:
            return jsonify({"success": False, "error": "Answers required"}), 400
        
        answers = data["answers"]  # {question_id: selected_option}
        
        # Get the correct answers from stored content
        if topic_content_collection is not None:
            content = topic_content_collection.find_one({
                "user_email": user_email,
                "topic_id": topic_id
            })
            
            if not content:
                return jsonify({"success": False, "error": "Topic content not found"}), 404
            
            mcq_questions = content.get("mcq_questions", [])
            
            # Score the answers
            results = []
            correct_count = 0
            
            for question in mcq_questions:
                question_id = question["id"]
                correct_answer = question["correct_answer"]
                user_answer = answers.get(question_id)
                
                is_correct = user_answer == correct_answer
                if is_correct:
                    correct_count += 1
                
                results.append({
                    "question_id": question_id,
                    "correct": is_correct,
                    "correct_answer": correct_answer,
                    "user_answer": user_answer,
                    "explanation": question.get("explanation", "")
                })
            
            score_percentage = (correct_count / len(mcq_questions)) * 100 if mcq_questions else 0
            
            return jsonify({
                "success": True,
                "score": correct_count,
                "total": len(mcq_questions),
                "percentage": round(score_percentage, 1),
                "results": results
            }), 200
        
        return jsonify({"success": False, "error": "Database not available"}), 500
        
    except Exception as e:
        print(f"MCQ submission failed: {e}")
        return jsonify({"success": False, "error": "MCQ submission failed"}), 500

@app.route("/api/practice/<topic_id>", methods=["GET", "OPTIONS"])
@token_required
def get_practice_questions(topic_id):
    """Get practice questions for a topic"""
    try:
        user_email = request.current_user["email"]
        
        # Find topic in user's roadmap
        user = get_user_by_email(user_email)
        if not user or not user.get("roadmap"):
            return jsonify({"success": False, "error": "Roadmap not found"}), 404
        
        topic_info = None
        for topic in user["roadmap"]:
            if topic.get("id") == topic_id:
                topic_info = topic
                break
        
        if not topic_info:
            return jsonify({"success": False, "error": "Topic not found"}), 404
        
        if topic_info.get("status") == "locked":
            return jsonify({"success": False, "error": "Topic is locked"}), 403
        
        # Generate questions using Gemini
        questions = gemini_service.generate_questions(
            topic_info["title"], 
            topic_info["difficulty"], 
            count=5
        )
        
        return jsonify({
            "success": True,
            "topic": topic_info["title"],
            "difficulty": topic_info["difficulty"],
            "questions": questions
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Practice questions failed: {e}")
        return jsonify({"success": False, "error": "Failed to get practice questions"}), 500

# -------------------------------
# Question Generation Routes
# -------------------------------
@app.route("/api/questions/generate", methods=["POST", "OPTIONS"])
@token_required
def generate_questions():
    """Generate questions for a topic using Gemini AI"""
    try:
        user_email = request.current_user["email"]
        user_id = request.current_user["user_id"]
        data = request.get_json()
        
        if not data or "topicId" not in data:
            return jsonify({"success": False, "error": "Topic ID required"}), 400
        
        topic_id = data["topicId"]
        
        # Get user's roadmap to find topic details
        user = get_user_by_email(user_email)
        if not user or not user.get("roadmap"):
            return jsonify({"success": False, "error": "Roadmap not found"}), 404
        
        # Find topic in roadmap
        topic_info = None
        for topic in user["roadmap"]:
            if topic.get("id") == topic_id:
                topic_info = topic
                break
        
        if not topic_info:
            return jsonify({"success": False, "error": "Topic not found"}), 404
        
        # Check if question pack already exists
        if question_packs_collection is not None:
            existing_pack = question_packs_collection.find_one({
                "userId": user_id,
                "topicId": topic_id
            })
            
            if existing_pack:
                # Update roadmap node with packId
                for topic in user["roadmap"]:
                    if topic.get("id") == topic_id:
                        topic["questionPackId"] = str(existing_pack["_id"])
                        break
                update_user_data(user_email, {"roadmap": user["roadmap"]})
                
                return jsonify({
                    "success": True,
                    "packId": str(existing_pack["_id"]),
                    "questions": existing_pack["items"]
                }), 200
        
        # Generate new questions
        from ai.gemini_service import gemini_service
        questions = gemini_service.generate_questions(
            topic_info["title"], 
            topic_info["difficulty"], 
            count=10
        )
        
        # Create question pack
        pack_data = {
            "userId": user_id,
            "userEmail": user_email,
            "topicId": topic_id,
            "topicTitle": topic_info["title"],
            "difficulty": topic_info["difficulty"],
            "items": questions,
            "createdAt": datetime.now(timezone.utc)
        }
        
        if question_packs_collection is not None:
            result = question_packs_collection.insert_one(pack_data)
            pack_id = str(result.inserted_id)
            
            # Update roadmap node with packId
            for topic in user["roadmap"]:
                if topic.get("id") == topic_id:
                    topic["questionPackId"] = pack_id
                    break
            update_user_data(user_email, {"roadmap": user["roadmap"]})
        else:
            import uuid
            pack_id = str(uuid.uuid4())
        
        print(f"Gemini generated Qs for topic {topic_info['title']}: {len(questions)}")
        
        return jsonify({
            "success": True,
            "packId": pack_id,
            "questions": questions
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Question generation failed: {e}")
        return jsonify({"success": False, "error": "Failed to generate questions"}), 500

@app.route("/api/questions/<pack_id>", methods=["GET", "OPTIONS"])
@token_required
def get_questions(pack_id):
    """Get questions from a question pack"""
    try:
        user_email = request.current_user["email"]
        
        if question_packs_collection is not None:
            from bson import ObjectId
            pack = question_packs_collection.find_one({
                "_id": ObjectId(pack_id),
                "userEmail": user_email
            })
            
            if pack:
                return jsonify({
                    "success": True,
                    "questions": pack["items"],
                    "topicTitle": pack["topicTitle"],
                    "difficulty": pack["difficulty"]
                }), 200
        
        return jsonify({"success": False, "error": "Question pack not found"}), 404
        
    except Exception as e:
        print(f"[ERROR] Get questions failed: {e}")
        return jsonify({"success": False, "error": "Failed to get questions"}), 500

@app.route("/api/questions/<pack_id>/submit", methods=["POST", "OPTIONS"])
@token_required
def submit_questions(pack_id):
    """Submit answers and score server-side, complete topic if passed"""
    try:
        user_email = request.current_user["email"]
        data = request.get_json()
        
        if not data or "answers" not in data:
            return jsonify({"success": False, "error": "Answers required"}), 400
        
        answers = data["answers"]
        
        # Get question pack
        if question_packs_collection is not None:
            from bson import ObjectId
            pack = question_packs_collection.find_one({
                "_id": ObjectId(pack_id),
                "userEmail": user_email
            })
            
            if not pack:
                return jsonify({"success": False, "error": "Question pack not found"}), 404
        else:
            return jsonify({"success": False, "error": "Question pack not found"}), 404
        
        # Score answers server-side
        correct_count = 0
        total_questions = len(pack["items"])
        
        for answer in answers:
            question_id = answer.get("id")
            selected = answer.get("selected")
            
            # Find question in pack and check answer
            for q in pack["items"]:
                if q["id"] == question_id:
                    if q["answer"] == selected:
                        correct_count += 1
                    break
        
        score_percent = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        passed = score_percent >= 70  # 70% pass threshold
        
        # If passed, mark topic completed and unlock next
        updated_roadmap = None
        if passed:
            user = get_user_by_email(user_email)
            if user and user.get("roadmap"):
                updated_roadmap = unlock_next_topic(user["roadmap"], pack["topicId"])
                updated_roadmap.sort(key=lambda x: x.get("order", 0))
                
                # Recompute progress
                completed_count = len([t for t in updated_roadmap if t.get("status") == "completed"])
                progress_percent = round((completed_count / len(updated_roadmap)) * 100, 1)
                
                update_user_data(user_email, {
                    "roadmap": updated_roadmap,
                    "roadmap_progress_percent": progress_percent
                })
                
                # Update practice streak
                try:
                    from streak_service import StreakService
                    StreakService.update_user_streak(users_collection, in_memory_users, user_email, "practice")
                except Exception as e:
                    print(f"Failed to update practice streak: {e}")
                
                print(f"Topic completed: {pack['topicId']} -> unlocked next")
        
        return jsonify({
            "success": True,
            "score": correct_count,
            "total": total_questions,
            "percentage": round(score_percent, 1),
            "passed": passed,
            "updatedRoadmap": updated_roadmap
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Submit questions failed: {e}")
        return jsonify({"success": False, "error": "Failed to submit answers"}), 500

# -------------------------------
# Pomodoro Routes - NEW
# -------------------------------
@app.route("/api/pomodoro/complete", methods=["POST", "OPTIONS"])
@token_required
def complete_pomodoro():
    """Complete a Pomodoro session with user isolation"""
    try:
        user_email = request.current_user["email"]
        user_id = request.current_user["user_id"]
        data = request.get_json()
        
        duration_minutes = data.get("durationMinutes", 25)
        topic_id = data.get("topicId")
        
        # Get current date
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        print(f"[POMODORO] Completing session for user: {user_email}")
        
        # Update THIS user's pomodoro count
        if users_collection is not None:
            result = users_collection.update_one(
                {"email": user_email},
                {"$inc": {"pomodoro_count": 1}}
            )
            
            # Get updated user data for THIS user
            user = users_collection.find_one({"email": user_email})
            pomodoro_count = user.get("pomodoro_count", 1) if user else 1
        else:
            if user_email not in in_memory_users:
                in_memory_users[user_email] = {"pomodoro_count": 0}
            current_count = in_memory_users[user_email].get("pomodoro_count", 0)
            in_memory_users[user_email]["pomodoro_count"] = current_count + 1
            pomodoro_count = current_count + 1
        
        # Save session for THIS user only
        session_data = {
            "userId": user_id,
            "userEmail": user_email,
            "date": today,
            "durationMinutes": duration_minutes,
            "topicId": topic_id,
            "createdAt": datetime.now(timezone.utc)
        }
        
        if pomodoro_sessions_collection is not None:
            pomodoro_sessions_collection.insert_one(session_data)
        
        # Count today's sessions for THIS user only
        if pomodoro_sessions_collection is not None:
            today_sessions = pomodoro_sessions_collection.count_documents({
                "userEmail": user_email,
                "date": today
            })
        else:
            today_sessions = 1  # Fallback
        
        # Update practice streak for Pomodoro completion
        try:
            from streak_service import StreakService
            pomodoro_streak_result = StreakService.trigger_practice_streak(users_collection, in_memory_users, user_email)
            print(f"[POMODORO STREAK] {user_email}: {pomodoro_streak_result.get('message', 'Updated')}")
        except Exception as e:
            print(f"Failed to update Pomodoro streak: {e}")
        
        print(f"[POMODORO] Session completed for {user_email} - Total: {pomodoro_count}, Today: {today_sessions}")
        
        return jsonify({
            "success": True,
            "pomodoro_count": pomodoro_count,
            "today_sessions": today_sessions,
            "streak_days": 1  # Will be calculated properly in streaks section
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Pomodoro complete failed for {user_email}: {e}")
        return jsonify({"success": False, "error": "Failed to complete Pomodoro"}), 500

@app.route("/api/pomodoro/summary", methods=["GET", "OPTIONS"])
@token_required
def get_pomodoro_summary():
    """Get Pomodoro session summary"""
    try:
        user_email = request.current_user["email"]
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Get user's total count
        if users_collection is not None:
            user = users_collection.find_one({"email": user_email})
            total_sessions = user.get("pomodoro_count", 0) if user else 0
        else:
            total_sessions = in_memory_users.get(user_email, {}).get("pomodoro_count", 0)
        
        # Get today's sessions and total minutes
        if pomodoro_sessions_collection is not None:
            today_sessions = pomodoro_sessions_collection.count_documents({
                "userEmail": user_email,
                "date": today
            })
            
            # Calculate total minutes
            pipeline = [
                {"$match": {"userEmail": user_email}},
                {"$group": {"_id": None, "total_minutes": {"$sum": "$durationMinutes"}}}
            ]
            result = list(pomodoro_sessions_collection.aggregate(pipeline))
            total_minutes = result[0]["total_minutes"] if result else 0
        else:
            today_sessions = 0
            total_minutes = total_sessions * 25  # Estimate
        
        return jsonify({
            "total_sessions": total_sessions,
            "total_minutes": total_minutes,
            "today_sessions": today_sessions,
            "streak_days": 1  # Will be calculated in streaks
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Pomodoro summary failed: {e}")
        return jsonify({"success": False, "error": "Failed to get summary"}), 500

# -------------------------------
# Profile Management Routes
# -------------------------------
@app.route("/api/profile/update_links", methods=["POST", "OPTIONS"])
@token_required
def update_profile_links():
    """Update user's coding platform profile links and trigger immediate progress sync"""
    try:
        user_email = request.current_user["email"]
        data = request.get_json()
        
        print(f"[PROFILE] Updating links for user: {user_email}")
        print(f"[PROFILE] Data received: {data}")
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        profile_links = {
            "leetcode": data.get("leetcode", "").strip(),
            "hackerrank": data.get("hackerrank", "").strip()
        }
        
        # Remove empty links
        profile_links = {k: v for k, v in profile_links.items() if v}
        
        print(f"[PROFILE] Processed links: {profile_links}")
        
        # Update user document
        update_data = {
            "profile_links": profile_links,
            "updatedAt": datetime.now(timezone.utc)
        }
        
        success = update_user_data(user_email, update_data)
        
        if success:
            print(f"[PROFILE] Updated profile links for {user_email}")
            
            # Immediately fetch progress for the updated links
            platform_progress = {}
            
            if profile_links.get("leetcode"):
                try:
                    print(f"[PROFILE] Fetching LeetCode stats for: {profile_links['leetcode']}")
                    leetcode_stats = fetch_leetcode_stats(profile_links["leetcode"])
                    if leetcode_stats:
                        platform_progress["leetcode"] = leetcode_stats
                        print(f"[PROFILE] Immediate LeetCode sync: {leetcode_stats}")
                except Exception as e:
                    print(f"[PROFILE] Immediate LeetCode sync failed: {e}")
            
            if profile_links.get("hackerrank"):
                try:
                    print(f"[PROFILE] Fetching HackerRank stats for: {profile_links['hackerrank']}")
                    hackerrank_stats = fetch_hackerrank_stats(profile_links["hackerrank"])
                    if hackerrank_stats:
                        platform_progress["hackerrank"] = hackerrank_stats
                        print(f"[PROFILE] Immediate HackerRank sync: {hackerrank_stats}")
                except Exception as e:
                    print(f"[PROFILE] Immediate HackerRank sync failed: {e}")
            
            # Update progress in database
            if platform_progress:
                overall_score = calculate_overall_score(platform_progress)
                progress_data = {
                    "platform_progress": platform_progress,
                    "overall_score": overall_score,
                    "last_updated": datetime.now(timezone.utc)
                }
                update_user_data(user_email, progress_data)
                print(f"[PROFILE] Progress synced immediately for {user_email}")
            
            return jsonify({
                "success": True, 
                "message": "Profile links updated and progress synced",
                "platform_progress": platform_progress
            }), 200
        else:
            return jsonify({"success": False, "error": "Failed to update profile links"}), 500
        
    except Exception as e:
        print(f"[ERROR] Update profile links failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Failed to update profile links"}), 500

@app.route("/api/profile/sync-progress", methods=["POST", "OPTIONS"])
@token_required
def sync_platform_progress():
    """Enhanced sync progress from coding platforms with automatic scheduling"""
    try:
        user_email = request.current_user["email"]
        print(f"[SYNC] Manual sync requested for user: {user_email}")
        
        user = get_user_by_email(user_email)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        profile_links = user.get("profile_links", {})
        if not profile_links:
            return jsonify({"success": False, "error": "No platform links configured"}), 400
        
        # Use the sync service for enhanced syncing
        if sync_service:
            success = sync_service.sync_user_progress(user_email, profile_links, force=True)
            
            if success:
                # Get updated user data
                updated_user = get_user_by_email(user_email)
                platform_progress = updated_user.get("platform_progress", {})
                overall_score = updated_user.get("overall_score", 0)
                
                return jsonify({
                    "success": True,
                    "message": "Progress synced successfully with enhanced tracking",
                    "platform_progress": platform_progress,
                    "overall_score": overall_score,
                    "sync_count": updated_user.get("sync_count", 0),
                    "last_updated": updated_user.get("last_updated", datetime.now(timezone.utc)).isoformat()
                }), 200
            else:
                return jsonify({"success": False, "error": "Failed to sync progress"}), 500
        else:
            # Fallback to basic sync if service not available
            platform_progress = {}
            
            # Sync LeetCode
            if profile_links.get("leetcode"):
                leetcode_stats = fetch_leetcode_stats(profile_links["leetcode"])
                if leetcode_stats:
                    platform_progress["leetcode"] = leetcode_stats
            
            # Sync HackerRank
            if profile_links.get("hackerrank"):
                hackerrank_stats = fetch_hackerrank_stats(profile_links["hackerrank"])
                if hackerrank_stats:
                    platform_progress["hackerrank"] = hackerrank_stats
            
            # Calculate overall score
            overall_score = calculate_overall_score(platform_progress)
            
            # Update user progress
            update_data = {
                "platform_progress": platform_progress,
                "overall_score": overall_score,
                "last_updated": datetime.now(timezone.utc)
            }
            
            success = update_user_data(user_email, update_data)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Progress synced successfully",
                    "platform_progress": platform_progress,
                    "overall_score": overall_score
                }), 200
            else:
                return jsonify({"success": False, "error": "Failed to update progress"}), 500
        
    except Exception as e:
        print(f"[ERROR] Sync progress failed: {e}")
        return jsonify({"success": False, "error": "Failed to sync progress"}), 500

@app.route("/api/profile/progress", methods=["GET", "OPTIONS"])
@token_required
def get_profile_progress():
    """Fetch and aggregate progress from external coding platforms"""
    try:
        user_email = request.current_user["email"]
        print(f"[PROFILE] Fetching progress for user: {user_email}")
        
        user = get_user_by_email(user_email)
        if not user:
            print(f"[PROFILE] User not found: {user_email}")
            return jsonify({"success": False, "error": "User not found"}), 404
        
        profile_links = user.get("profile_links", {})
        print(f"[PROFILE] Profile links: {profile_links}")
        
        if not profile_links.get("leetcode") and not profile_links.get("hackerrank"):
            print(f"[PROFILE] No profile links found for {user_email}")
            return jsonify({
                "success": True,
                "platform_progress": {},
                "overall_score": 0,
                "message": "No platform links configured"
            }), 200
        
        platform_progress = {}
        
        # Fetch LeetCode stats
        if profile_links.get("leetcode"):
            print(f"[PROFILE] Fetching LeetCode stats for: {profile_links['leetcode']}")
            try:
                leetcode_stats = fetch_leetcode_stats(profile_links["leetcode"])
                if leetcode_stats:
                    platform_progress["leetcode"] = leetcode_stats
                    print(f"[PROFILE] LeetCode stats fetched: {leetcode_stats}")
                else:
                    print(f"[PROFILE] No LeetCode stats returned")
            except Exception as e:
                print(f"[PROFILE] LeetCode fetch failed: {e}")
        
        # Fetch HackerRank stats
        if profile_links.get("hackerrank"):
            print(f"[PROFILE] Fetching HackerRank stats for: {profile_links['hackerrank']}")
            try:
                hackerrank_stats = fetch_hackerrank_stats(profile_links["hackerrank"])
                if hackerrank_stats:
                    platform_progress["hackerrank"] = hackerrank_stats
                    print(f"[PROFILE] HackerRank stats fetched: {hackerrank_stats}")
                else:
                    print(f"[PROFILE] No HackerRank stats returned")
            except Exception as e:
                print(f"[PROFILE] HackerRank fetch failed: {e}")
        
        # Calculate overall score
        overall_score = calculate_overall_score(platform_progress)
        print(f"[PROFILE] Overall score calculated: {overall_score}")
        
        # Cache the results in user document
        cache_data = {
            "platform_progress": platform_progress,
            "overall_score": overall_score,
            "last_updated": datetime.now(timezone.utc)
        }
        
        success = update_user_data(user_email, cache_data)
        if success:
            print(f"[PROFILE] Progress cached for user: {user_email}")
        
        return jsonify({
            "success": True,
            "platform_progress": platform_progress,
            "overall_score": overall_score,
            "last_updated": cache_data["last_updated"].isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get profile progress failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Failed to fetch progress"}), 500

# -------------------------------
# External API Integration Functions
# -------------------------------
def fetch_leetcode_stats(username):
    """Fetch LeetCode statistics with robust error handling and fallback"""
    try:
        print(f"[API] Fetching LeetCode stats for: {username}")
        result = coding_tracker.get_leetcode_stats(username)
        
        if result and result.get('success'):
            stats = {
                "solved": result['solved_problems']['total'],
                "easy": result['solved_problems']['easy'],
                "medium": result['solved_problems']['medium'],
                "hard": result['solved_problems']['hard'],
                "ranking": result.get('ranking', 0),
                "weekly_solved": 0,  # Will be enhanced later
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "demo_data": result.get('demo_data', False)
            }
            print(f"[API] LeetCode {'demo' if result.get('demo_data') else 'live'} data: {stats['solved']} problems solved")
            return stats
        else:
            print(f"[API] LeetCode failed: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"[ERROR] LeetCode API failed: {e}")
        return None

def fetch_hackerrank_stats(username):
    """Fetch HackerRank statistics with fallback for blocked API"""
    try:
        print(f"[API] Fetching HackerRank stats for: {username}")
        result = coding_tracker.get_hackerrank_stats(username)
        
        if result and result.get('success'):
            stats = {
                "stars": result['scores'].get('total_score', 0) // 10,
                "certificates": result.get('certificates', 3),
                "badges": result.get('badges', 12),
                "problems_solved": result['scores'].get('algorithms', 0) + result['scores'].get('data_structures', 0),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "demo_data": result.get('demo_data', False)
            }
            print(f"[API] HackerRank {'demo' if result.get('demo_data') else 'live'} data: {stats['stars']} stars")
            return stats
        else:
            print(f"[API] HackerRank failed, returning None")
            return None
            
    except Exception as e:
        print(f"[ERROR] HackerRank API failed: {e}")
        return None



def calculate_overall_score(platform_progress):
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
        print(f"[ERROR] Calculate overall score failed: {e}")
        return 0

# -------------------------------
# Legacy Integrations Route (for backward compatibility)
# -------------------------------
@app.route("/api/integrations", methods=["POST", "OPTIONS"])
@token_required
def save_integrations():
    """Save coding platform integrations (legacy endpoint)"""
    try:
        user_email = request.current_user["email"]
        data = request.get_json()
        
        # Convert legacy format to new format
        profile_links = {
            "leetcode": data.get("leetcodeUser", data.get("leetcode_username", "")).strip(),
            "hackerrank": data.get("hackerrankUser", data.get("hackerrank_username", "")).strip()
        }
        
        update_data = {
            "profile_links": profile_links,
            "updatedAt": datetime.now(timezone.utc)
        }
        
        success = update_user_data(user_email, update_data)
        
        if success:
            return jsonify({"success": True, "message": "Integrations saved"}), 200
        else:
            return jsonify({"success": False, "error": "Failed to save integrations"}), 500
        
    except Exception as e:
        print(f"[ERROR] Save integrations failed: {e}")
        return jsonify({"success": False, "error": "Failed to save integrations"}), 500

@app.route("/api/profile/update_avatar", methods=["POST", "OPTIONS"])
@token_required
def update_avatar():
    """Update user's avatar"""
    try:
        user_email = request.current_user["email"]
        data = request.get_json()
        
        if not data or "avatar" not in data:
            return jsonify({"success": False, "error": "Avatar data required"}), 400
        
        avatar_data = data["avatar"]
        
        update_data = {
            "avatar": avatar_data,
            "updatedAt": datetime.now(timezone.utc)
        }
        
        success = update_user_data(user_email, update_data)
        
        if success:
            return jsonify({"success": True, "message": "Avatar updated successfully"}), 200
        else:
            return jsonify({"success": False, "error": "Failed to update avatar"}), 500
        
    except Exception as e:
        print(f"[ERROR] Update avatar failed: {e}")
        return jsonify({"success": False, "error": "Failed to update avatar"}), 500

@app.route("/api/profile/badges", methods=["GET", "OPTIONS"])
@token_required
def get_user_badges():
    """Get user's earned badges"""
    try:
        user_email = request.current_user["email"]
        user = get_user_by_email(user_email)
        
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Calculate and update badges
        badges = calculate_user_badges(user)
        
        # Update user with new badges
        update_user_data(user_email, {"badges": badges})
        
        return jsonify({
            "success": True,
            "badges": badges
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get badges failed: {e}")
        return jsonify({"success": False, "error": "Failed to get badges"}), 500

def calculate_user_badges(user):
    """Calculate badges based on user activity"""
    badges = []
    
    # Getting Started badge - always earned
    badges.append({
        "id": "getting_started",
        "name": "Getting Started",
        "description": "Welcome to Pulse!",
        "icon": "🚀",
        "color": "#10b981"
    })
    
    # Consistent Coder badge - login streak > 5
    login_streak = user.get("login_streak_days", 0)
    if login_streak >= 5:
        badges.append({
            "id": "consistent_coder",
            "name": "Consistent Coder",
            "description": f"Maintained {login_streak} day streak!",
            "icon": "🔥",
            "color": "#f59e0b"
        })
    
    # Problem Solver badge - LeetCode solved > 100
    platform_progress = user.get("platform_progress", {})
    leetcode_solved = platform_progress.get("leetcode", {}).get("solved", 0)
    if leetcode_solved >= 100:
        badges.append({
            "id": "problem_solver",
            "name": "Problem Solver",
            "description": f"Solved {leetcode_solved} LeetCode problems!",
            "icon": "💻",
            "color": "#3b82f6"
        })
    
    # Rank Climber badge - HackerRank stars >= 3
    hackerrank_stars = platform_progress.get("hackerrank", {}).get("stars", 0)
    if hackerrank_stars >= 3:
        badges.append({
            "id": "rank_climber",
            "name": "Rank Climber",
            "description": f"Earned {hackerrank_stars} HackerRank stars!",
            "icon": "⭐",
            "color": "#8b5cf6"
        })
    
    # Assessment Master badge - completed assessment
    if user.get("assessment_taken", False):
        badges.append({
            "id": "assessment_master",
            "name": "Assessment Master",
            "description": "Completed skill assessment!",
            "icon": "🎯",
            "color": "#ef4444"
        })
    
    return badges

@app.route("/api/user/streak-data", methods=["GET", "OPTIONS"])
@token_required
def get_streak_data():
    try:
        user_email = request.current_user["email"]
        
        user = None
        if users_collection is not None:
            user = users_collection.find_one({"email": user_email})
        else:
            user = in_memory_users.get(user_email)
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        return jsonify({
            "current_streak": user.get("streak", 0),
            "avg_daily_sessions": 2.5,
            "session_completion_rate": 0.78,
            "last_7_days_active": 6,
            "weekend_activity": 0.6,
            "stress_level": 3,
            "motivation_score": 8
        })
    except Exception as e:
        print(f"Streak data error: {e}")
        return jsonify({"message": "Failed to retrieve streak data"}), 500

# -------------------------------
# Duolingo-Style Roadmap Agent
# -------------------------------
def generate_adaptive_roadmap(user_email, predicted_level):
    """Generate adaptive DSA roadmap using the roadmap agent"""
    try:
        print(f"[AGENT] Roadmap agent triggered for {user_email}")
        
        # Generate roadmap using the agent
        roadmap = roadmap_agent.generate_roadmap(predicted_level)
        
        if not roadmap:
            print(f"[ERROR] Roadmap generation returned None for {user_email}")
            return None
        
        # Ensure roadmap is JSON serializable
        if isinstance(roadmap, dict):
            # Convert any datetime objects to ISO strings
            for key, value in roadmap.items():
                if hasattr(value, 'isoformat'):
                    roadmap[key] = value.isoformat()
            
            # Ensure topics list exists and is serializable
            if 'topics' in roadmap and isinstance(roadmap['topics'], list):
                for topic in roadmap['topics']:
                    if isinstance(topic, dict):
                        for topic_key, topic_value in topic.items():
                            if hasattr(topic_value, 'isoformat'):
                                topic[topic_key] = topic_value.isoformat()
        
        print(f"[SUCCESS] Generated roadmap with {roadmap.get('total_topics', 0)} topics")
        return roadmap
        
    except Exception as e:
        print(f"[ERROR] Roadmap agent failed: {e}")
        import traceback
        traceback.print_exc()
        return None

# -------------------------------
# Quiz and ML Routes
# -------------------------------
@app.route("/api/quiz/questions", methods=["GET", "OPTIONS"])
@token_required
def get_quiz_questions():
    """Get quiz questions for domain with user isolation"""
    try:
        user_email = request.current_user["email"]
        
        # Fresh lookup for THIS user's assessment state
        user = get_user_by_email(user_email)
        
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Check if THIS user already took assessment
        assessment_taken = user.get("assessment_taken", False)
        print(f"[QUIZ] User {user_email} requesting questions - Assessment taken: {assessment_taken}")
        
        if assessment_taken:
            return jsonify({
                "success": False,
                "error": "Assessment already taken. Please continue with your roadmap topics.",
                "assessment_taken": True
            }), 400
        
        domain = request.args.get("domain", "programming").lower()
        
        if domain not in QUIZ_QUESTIONS:
            domain = "programming"
        
        questions = QUIZ_QUESTIONS[domain][:10]
        
        quiz_questions = []
        for q in questions:
            quiz_questions.append({
                "id": q["id"],
                "question": q["question"],
                "options": q["options"]
            })
        
        return jsonify({
            "success": True,
            "domain": domain,
            "questions": quiz_questions,
            "assessment_taken": False
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Quiz questions error: {e}")
        return jsonify({"success": False, "error": "Failed to get questions"}), 500

@app.route("/api/quiz/submit", methods=["POST", "OPTIONS"])
@token_required
def submit_quiz():
    """FIXED: Submit quiz with robust error handling and proper validation"""
    user_email = None
    try:
        # 1. AUTHENTICATION CHECK
        if not hasattr(request, 'current_user') or not request.current_user:
            print("❌ [QUIZ] No user authentication found")
            return jsonify({"success": False, "error": "User not authenticated"}), 401
        
        user_email = request.current_user.get("email")
        user_id = request.current_user.get("user_id")
        
        if not user_email:
            print("❌ [QUIZ] No user email in session")
            return jsonify({"success": False, "error": "User not authenticated"}), 401
        
        print(f"✅ [QUIZ] Processing submission for user: {user_email}")
        
        # 2. REQUEST PARSING
        data = request.get_json()
        if not data:
            print(f"❌ [QUIZ] No data provided by {user_email}")
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # 3. USER VALIDATION
        user = get_user_by_email(user_email)
        if not user:
            print(f"❌ [QUIZ] User not found: {user_email}")
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # 4. ASSESSMENT STATE CHECK
        assessment_taken = user.get("assessment_taken", False)
        if assessment_taken:
            print(f"⚠️ [QUIZ] Assessment already taken by {user_email}")
            return jsonify({
                "success": False,
                "error": "Assessment already taken. Please continue with your roadmap topics.",
                "assessment_taken": True
            }), 400
        
        # 5. EXTRACT QUIZ DATA
        # Support both simple score format and detailed answers format
        score = data.get("score")
        answers = data.get("answers", [])
        
        if score is not None:
            # Simple format: {"score": 3}
            correct_answers = int(score)
            total_questions = 5  # Default total
            print(f"✅ [QUIZ] Simple format - Score: {correct_answers}/{total_questions}")
        elif answers:
            # Detailed format: {"answers": [{"question_id": 1, "selected_answer": 0}, ...]}
            correct_answers = 0
            total_questions = len(answers)
            domain = data.get("domain", "programming").lower()
            
            for answer in answers:
                question_id = answer.get("question_id")
                selected_answer = answer.get("selected_answer")
                
                for q in QUIZ_QUESTIONS.get(domain, []):
                    if q["id"] == question_id:
                        if q["correct"] == selected_answer:
                            correct_answers += 1
                        break
            
            print(f"✅ [QUIZ] Detailed format - Score: {correct_answers}/{total_questions}")
        else:
            print(f"❌ [QUIZ] No score or answers provided by {user_email}")
            return jsonify({"success": False, "error": "Score or answers required"}), 400
        
        # 6. LEVEL PREDICTION
        print(f"🔍 [QUIZ] Predicting level for {user_email}: {correct_answers}/{total_questions}")
        predicted_level = predictor.predict_skill_level(correct_answers, total_questions, 30)
        print(f"🧠 User {user_email} predicted as {predicted_level}")
        
        # 7. ROADMAP GENERATION
        print(f"🗺️ [QUIZ] Generating roadmap for level: {predicted_level}")
        roadmap = generate_roadmap(predicted_level)
        
        if not roadmap or not isinstance(roadmap, list):
            print(f"⚠️ [QUIZ] Roadmap generation failed, using empty roadmap")
            roadmap = []
        else:
            topic_titles = [topic.get('title', 'Unknown') for topic in roadmap]
            print(f"✅ [QUIZ] Generated {len(roadmap)} topics: {topic_titles}")
        
        # 8. SAVE USER DATA
        percentage = round((correct_answers / total_questions) * 100, 1) if total_questions > 0 else 0
        
        update_data = {
            "assessment_taken": True,
            "predicted_level": predicted_level,
            "skill_level": predicted_level,
            "quiz_score": correct_answers,
            "quiz_total": total_questions,
            "quiz_percentage": percentage,
            "roadmap": roadmap,
            "last_assessment_date": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        
        print(f"💾 [QUIZ] Saving data for {user_email}: Level={predicted_level}, Score={correct_answers}/{total_questions}")
        
        success = update_user_data(user_email, update_data)
        if not success:
            print(f"❌ [QUIZ] Failed to save user data for {user_email}")
            return jsonify({"success": False, "error": "Failed to save assessment data"}), 500
        
        # 9. STORE QUIZ RESPONSE (OPTIONAL)
        if quiz_responses_collection is not None:
            try:
                quiz_result = {
                    "user_id": user_id,
                    "user_email": user_email,
                    "score": correct_answers,
                    "total_questions": total_questions,
                    "percentage": percentage,
                    "predicted_level": predicted_level,
                    "timestamp": datetime.now(timezone.utc)
                }
                quiz_responses_collection.insert_one(quiz_result)
                print(f"✅ [QUIZ] Stored quiz response for {user_email}")
            except Exception as store_error:
                print(f"⚠️ [QUIZ] Failed to store quiz response: {store_error}")
                # Don't fail the entire request for this
        
        # 10. SUCCESS RESPONSE
        print(f"🎉 [QUIZ COMPLETE] {user_email}: {predicted_level} level, {correct_answers}/{total_questions} ({percentage}%)")
        
        return jsonify({
            "success": True,
            "message": "Quiz submitted successfully",
            "assessment_completed": True,
            "assessment_taken": True,
            "score": correct_answers,
            "total_questions": total_questions,
            "percentage": percentage,
            "predicted_level": predicted_level,
            "roadmap_generated": len(roadmap) > 0,
            "user_email": user_email
        }), 200
        
    except Exception as e:
        error_msg = f"Quiz submission error for {user_email or 'unknown'}: {str(e)}"
        print(f"❌ [QUIZ ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False, 
            "error": "Quiz submission failed",
            "details": str(e) if user_email else "Authentication error"
        }), 500

@app.route("/api/model/predict", methods=["POST", "OPTIONS"])
@token_required
def predict_skill_level():
    """FIXED: Predict skill level with robust error handling"""
    user_email = None
    try:
        # 1. AUTHENTICATION CHECK
        if not hasattr(request, 'current_user') or not request.current_user:
            return jsonify({"success": False, "error": "User not authenticated"}), 401
        
        user_email = request.current_user.get("email")
        if not user_email:
            return jsonify({"success": False, "error": "User not authenticated"}), 401
        
        # 2. REQUEST PARSING
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # 3. USER VALIDATION
        user = get_user_by_email(user_email)
        if user and user.get("assessment_taken", False):
            return jsonify({
                "success": False,
                "error": "Assessment already taken. Please continue with your roadmap topics."
            }), 400
        
        # 4. EXTRACT PREDICTION DATA
        correct_answers = int(data.get("correct_answers", 0))
        total_questions = int(data.get("total_questions", 5))
        avg_time = data.get("avg_time", 30)
        
        print(f"🔍 [PREDICT] ML Prediction for {user_email}: {correct_answers}/{total_questions}")
        
        # 5. LEVEL PREDICTION
        predicted_level = predictor.predict_skill_level(correct_answers, total_questions, avg_time)
        print(f"🧠 User {user_email} predicted as {predicted_level}")
        
        # 6. ROADMAP GENERATION
        print(f"🗺️ [PREDICT] Generating roadmap for level: {predicted_level}")
        roadmap = generate_roadmap(predicted_level)
        
        if not roadmap or not isinstance(roadmap, list):
            roadmap = []
        
        # 7. SAVE DATA
        update_data = {
            "assessment_taken": True,
            "predicted_level": predicted_level,
            "skill_level": predicted_level,
            "last_assessment_date": datetime.now(timezone.utc),
            "roadmap": roadmap
        }
        
        success = update_user_data(user_email, update_data)
        if not success:
            return jsonify({"success": False, "error": "Failed to save prediction data"}), 500
        
        print(f"✅ [PREDICT] Saved prediction for {user_email}: {predicted_level}")
        
        return jsonify({
            "success": True,
            "message": "Skill level predicted successfully",
            "predicted_level": predicted_level,
            "assessment_taken": True,
            "roadmap_generated": len(roadmap) > 0,
            "roadmap": roadmap
        }), 200
        
    except Exception as e:
        error_msg = f"ML prediction failed for {user_email or 'unknown'}: {str(e)}"
        print(f"❌ [PREDICT ERROR] {error_msg}")
        return jsonify({"success": False, "error": "Prediction failed"}), 500



@app.route("/api/roadmap/test/<level>", methods=["GET"])
def test_roadmap_generation(level):
    """VALIDATION: Test endpoint to verify roadmap agent generates distinct content per level"""
    try:
        print(f"🔍 [VALIDATION] Testing roadmap generation for level: {level}")
        from roadmap_agent import generate_roadmap as test_generate_roadmap
        roadmap = test_generate_roadmap(level)
        
        if roadmap and isinstance(roadmap, list):
            topic_titles = [topic.get('title', 'Unknown') for topic in roadmap]
            print(f"🗺️ Roadmap topics for {level}: {len(roadmap)} items")
            print(f"✅ Test roadmap topics returned: {topic_titles}")
            print(f"[SUCCESS] Test roadmap generated successfully with {len(roadmap)} topics")
            
            # Validate distinct content per level
            validation_result = validate_level_content(level, topic_titles)
            
            return jsonify({
                "success": True,
                "level": level,
                "roadmap": roadmap,
                "topic_count": len(roadmap),
                "topic_titles": topic_titles,
                "validation": validation_result,
                "message": f"✅ Test roadmap generated for {level} level - {validation_result['status']}"
            }), 200
        else:
            print(f"❌ [ERROR] Test roadmap generation failed or returned invalid format")
            return jsonify({
                "success": False,
                "error": "Roadmap generation failed or returned invalid format"
            }), 500
        
    except Exception as e:
        print(f"❌ [ERROR] Test roadmap generation failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def validate_level_content(level, topics):
    """Validate that each level returns distinct, appropriate content"""
    expected_content = {
        "Beginner": ["Arrays", "Strings", "Recursion", "Sorting"],
        "Intermediate": ["Linked Lists", "Stacks", "Trees", "Graphs"],
        "Expert": ["Dynamic Programming", "Greedy", "Segment Trees", "Advanced"]
    }
    
    expected = expected_content.get(level, [])
    matches = sum(1 for topic in topics if any(exp.lower() in topic.lower() for exp in expected))
    
    if matches >= len(expected) // 2:  # At least half the expected topics
        return {"status": "VALID", "matches": matches, "expected": expected}
    else:
        return {"status": "INVALID", "matches": matches, "expected": expected}

@app.route("/api/test/level-prediction/<int:score>/<int:total>", methods=["GET"])
def test_level_prediction(score, total):
    """VALIDATION: Test endpoint to verify level prediction logic with all scenarios"""
    try:
        print(f"🔍 [VALIDATION] Testing level prediction for score: {score}/{total}")
        predicted_level = predictor.predict_skill_level(score, total, 30)
        
        # Validate the prediction is correct
        expected_level = "Beginner" if score <= 2 else "Intermediate" if score <= 4 else "Expert"
        is_correct = predicted_level == expected_level
        
        print(f"🧠 Predicted: {predicted_level}, Expected: {expected_level}, Correct: {is_correct}")
        
        return jsonify({
            "success": True,
            "score": score,
            "total": total,
            "percentage": round((score/total)*100, 1),
            "predicted_level": predicted_level,
            "expected_level": expected_level,
            "validation_passed": is_correct,
            "message": f"Score {score}/{total} = {predicted_level} level {'✅' if is_correct else '❌'}"
        }), 200
        
    except Exception as e:
        print(f"❌ Level prediction test failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/test/complete-validation", methods=["GET"])
def complete_validation():
    """VALIDATION: Complete test of all scenarios - User A, B, C"""
    try:
        print(f"🔍 [COMPLETE VALIDATION] Testing all user scenarios")
        
        test_cases = [
            {"name": "User A", "score": 1, "total": 5, "expected_level": "Beginner"},
            {"name": "User B", "score": 3, "total": 5, "expected_level": "Intermediate"},
            {"name": "User C", "score": 5, "total": 5, "expected_level": "Expert"}
        ]
        
        results = []
        
        for case in test_cases:
            # Test level prediction
            predicted_level = predictor.predict_skill_level(case["score"], case["total"], 30)
            level_correct = predicted_level == case["expected_level"]
            
            # Test roadmap generation
            from roadmap_agent import generate_roadmap
            roadmap = generate_roadmap(predicted_level)
            roadmap_valid = roadmap and isinstance(roadmap, list) and len(roadmap) > 0
            
            topic_titles = [topic.get('title', 'Array Basics') for topic in roadmap] if roadmap else []
            
            print(f"🧠 {case['name']}: score={case['score']}/{case['total']} → {predicted_level} → {len(topic_titles)} topics")
            print(f"🗺️ Topics: {topic_titles}")
            
            results.append({
                "user": case["name"],
                "score": f"{case['score']}/{case['total']}",
                "predicted_level": predicted_level,
                "expected_level": case["expected_level"],
                "level_prediction_correct": level_correct,
                "roadmap_generated": roadmap_valid,
                "topic_count": len(topic_titles),
                "topics": topic_titles,
                "status": "✅ PASS" if level_correct and roadmap_valid else "❌ FAIL"
            })
        
        all_passed = all(r["level_prediction_correct"] and r["roadmap_generated"] for r in results)
        
        print(f"🎯 [VALIDATION COMPLETE] All tests passed: {all_passed}")
        
        return jsonify({
            "success": True,
            "validation_passed": all_passed,
            "test_results": results,
            "summary": {
                "total_tests": len(test_cases),
                "passed": sum(1 for r in results if r["status"] == "✅ PASS"),
                "failed": sum(1 for r in results if r["status"] == "❌ FAIL")
            },
            "message": f"Complete validation {'✅ PASSED' if all_passed else '❌ FAILED'}"
        }), 200
        
    except Exception as e:
        print(f"❌ Complete validation failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/roadmap/complete-topic", methods=["POST", "OPTIONS"])
@token_required
def complete_topic():
    """Mark topic as completed and unlock next one"""
    try:
        user_email = request.current_user["email"]
        data = request.get_json()
        
        if not data or "topic_id" not in data:
            return jsonify({"success": False, "error": "Topic ID required"}), 400
        
        topic_id = data["topic_id"]
        
        # Get user's roadmap
        user = None
        if users_collection is not None:
            user = users_collection.find_one({"email": user_email})
        else:
            user = in_memory_users.get(user_email)
        
        if not user or not user.get("roadmap"):
            return jsonify({"success": False, "error": "Roadmap not found"}), 404
        
        # Update roadmap progress
        roadmap = user["roadmap"]
        updated_roadmap = roadmap_agent.unlock_next_topic(roadmap, topic_id)
        
        # Save updated roadmap
        if users_collection is not None:
            users_collection.update_one(
                {"email": user_email},
                {"$set": {"roadmap": updated_roadmap}}
            )
        else:
            if user_email in in_memory_users:
                in_memory_users[user_email]["roadmap"] = updated_roadmap
        
        return jsonify({
            "success": True,
            "message": "Topic completed and next topic unlocked",
            "progress": updated_roadmap["progress"]
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Complete topic failed: {e}")
        return jsonify({"success": False, "error": "Failed to complete topic"}), 500

# -------------------------------
# Pomodoro Timer Routes
# -------------------------------
@app.route("/api/pomodoro/start", methods=["POST", "OPTIONS"])
@token_required
def start_pomodoro():
    """Start a new Pomodoro session"""
    try:
        user_email = request.current_user["email"]
        data = request.get_json() or {}
        
        session_data = {
            "user_email": user_email,
            "duration_minutes": data.get("duration", 25),
            "task_name": data.get("task", "Focus Session"),
            "started_at": datetime.now(timezone.utc),
            "status": "active"
        }
        
        if pomodoro_sessions_collection is not None:
            result = pomodoro_sessions_collection.insert_one(session_data)
            session_id = str(result.inserted_id)
        else:
            session_id = f"session_{len(in_memory_users.get(user_email, {}).get('pomodoro_sessions', []))}_{int(datetime.now().timestamp())}"
            if user_email not in in_memory_users:
                in_memory_users[user_email] = {}
            if 'pomodoro_sessions' not in in_memory_users[user_email]:
                in_memory_users[user_email]['pomodoro_sessions'] = []
            session_data['_id'] = session_id
            in_memory_users[user_email]['pomodoro_sessions'].append(session_data)
        
        print(f"[POMODORO] Started session {session_id} for {user_email}")
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "duration": session_data["duration_minutes"],
            "task": session_data["task_name"],
            "started_at": session_data["started_at"].isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Start Pomodoro failed: {e}")
        return jsonify({"success": False, "error": "Failed to start Pomodoro session"}), 500



@app.route("/api/pomodoro/stats", methods=["GET", "OPTIONS"])
@token_required
def get_pomodoro_stats():
    """Get user's Pomodoro statistics"""
    try:
        user_email = request.current_user["email"]
        
        # Get completed sessions count
        if pomodoro_sessions_collection is not None:
            total_sessions = pomodoro_sessions_collection.count_documents({
                "user_email": user_email,
                "status": "completed"
            })
            today_sessions = pomodoro_sessions_collection.count_documents({
                "user_email": user_email,
                "status": "completed",
                "completed_at": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)}
            })
        else:
            sessions = in_memory_users.get(user_email, {}).get('pomodoro_sessions', [])
            total_sessions = len([s for s in sessions if s.get('status') == 'completed'])
            today = datetime.now(timezone.utc).date()
            today_sessions = len([s for s in sessions if s.get('status') == 'completed' and s.get('completed_at', datetime.min).date() == today])
        
        return jsonify({
            "success": True,
            "total_sessions": total_sessions,
            "sessions_today": today_sessions,
            "avg_session_time": 25,
            "focus_score": min(85 + (total_sessions * 2), 100)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Pomodoro stats failed: {e}")
        return jsonify({"success": False, "error": "Failed to get Pomodoro stats"}), 500

# -------------------------------
# Coding Platform Integration Routes
# -------------------------------


@app.route("/api/integrations/leetcode", methods=["GET", "OPTIONS"])
@token_required
def get_leetcode_stats():
    """Get LeetCode stats for user"""
    try:
        user_email = request.current_user["email"]
        username = request.args.get("username")
        
        if not username:
            return jsonify({"success": False, "error": "Username required"}), 400
        
        stats = coding_platform_service.fetch_leetcode_stats(username)
        
        if stats:
            return jsonify({
                "success": True,
                "stats": stats
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to fetch LeetCode stats"
            }), 404
        
    except Exception as e:
        print(f"[ERROR] LeetCode stats fetch failed: {e}")
        return jsonify({"success": False, "error": "Failed to fetch LeetCode stats"}), 500

@app.route("/api/integrations/hackerrank", methods=["GET", "OPTIONS"])
@token_required
def get_hackerrank_stats():
    """Get HackerRank stats for user"""
    try:
        user_email = request.current_user["email"]
        username = request.args.get("username")
        
        if not username:
            return jsonify({"success": False, "error": "Username required"}), 400
        
        stats = coding_platform_service.fetch_hackerrank_stats(username)
        
        if stats:
            return jsonify({
                "success": True,
                "stats": stats
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to fetch HackerRank stats"
            }), 404
        
    except Exception as e:
        print(f"[ERROR] HackerRank stats fetch failed: {e}")
        return jsonify({"success": False, "error": "Failed to fetch HackerRank stats"}), 500

@app.route("/api/integrations/hackerearth", methods=["GET", "OPTIONS"])
@token_required
def get_hackerearth_stats():
    """Get HackerEarth stats for user"""
    try:
        user_email = request.current_user["email"]
        username = request.args.get("username")
        
        if not username:
            return jsonify({"success": False, "error": "Username required"}), 400
        
        stats = coding_platform_service.fetch_hackerearth_stats(username)
        
        if stats:
            return jsonify({
                "success": True,
                "stats": stats
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to fetch HackerEarth stats"
            }), 404
        
    except Exception as e:
        print(f"[ERROR] HackerEarth stats fetch failed: {e}")
        return jsonify({"success": False, "error": "Failed to fetch HackerEarth stats"}), 500

# -------------------------------
# Enhanced Progress Tracking Routes
# -------------------------------
@app.route("/api/profile/progress-insights", methods=["GET", "OPTIONS"])
@token_required
def get_progress_insights():
    """Get user's progress insights and trends"""
    try:
        user_email = request.current_user["email"]
        
        user = get_user_by_email(user_email)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Get stored insights
        insights = user.get("progress_insights", {
            "trends": [],
            "achievements": [],
            "recommendations": []
        })
        
        # Get recent activity if available
        platform_progress = user.get("platform_progress", {})
        recent_activity = {
            "leetcode_weekly": platform_progress.get("leetcode", {}).get("weekly_solved", 0),
            "last_active": platform_progress.get("leetcode", {}).get("last_active"),
            "total_problems": (
                platform_progress.get("leetcode", {}).get("solved", 0) +
                platform_progress.get("hackerrank", {}).get("problems_solved", 0)
            )
        }
        
        return jsonify({
            "success": True,
            "insights": insights,
            "recent_activity": recent_activity,
            "insights_generated_at": user.get("insights_generated_at", "").isoformat() if user.get("insights_generated_at") else None
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Progress insights failed: {e}")
        return jsonify({"success": False, "error": "Failed to get progress insights"}), 500

@app.route("/api/profile/recent-activity", methods=["GET", "OPTIONS"])
@token_required
def get_recent_activity():
    """Get user's recent coding activity across platforms"""
    try:
        user_email = request.current_user["email"]
        
        user = get_user_by_email(user_email)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        profile_links = user.get("profile_links", {})
        platform_progress = user.get("platform_progress", {})
        
        activity_data = {
            "leetcode": {
                "recent_submissions": platform_progress.get("leetcode", {}).get("recent_activity", []),
                "weekly_solved": platform_progress.get("leetcode", {}).get("weekly_solved", 0),
                "last_active": platform_progress.get("leetcode", {}).get("last_active")
            },
            "hackerrank": {
                "badges": platform_progress.get("hackerrank", {}).get("badge_details", []),
                "certificates": platform_progress.get("hackerrank", {}).get("certificates", 0)
            },
            "summary": {
                "total_weekly_problems": platform_progress.get("leetcode", {}).get("weekly_solved", 0),
                "platforms_active": len([p for p in ["leetcode", "hackerrank"] if profile_links.get(p)]),
                "last_sync": user.get("last_updated", "").isoformat() if user.get("last_updated") else None
            }
        }
        
        return jsonify({
            "success": True,
            "activity": activity_data
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Recent activity failed: {e}")
        return jsonify({"success": False, "error": "Failed to get recent activity"}), 500

@app.route("/api/admin/sync-status", methods=["GET", "OPTIONS"])
@token_required
def get_sync_status():
    """Get sync service status (admin endpoint)"""
    try:
        if sync_service:
            status = sync_service.get_sync_status()
            return jsonify({
                "success": True,
                "sync_service": status
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Sync service not available"
            }), 503
        
    except Exception as e:
        print(f"[ERROR] Sync status failed: {e}")
        return jsonify({"success": False, "error": "Failed to get sync status"}), 500

@app.route("/api/profile/enable-auto-sync", methods=["POST", "OPTIONS"])
@token_required
def enable_auto_sync():
    """Enable automatic progress sync for user"""
    try:
        user_email = request.current_user["email"]
        
        user = get_user_by_email(user_email)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        profile_links = user.get("profile_links", {})
        if not profile_links.get("leetcode") and not profile_links.get("hackerrank"):
            return jsonify({"success": False, "error": "No platform links configured"}), 400
        
        # Enable auto-sync flag
        update_data = {
            "auto_sync_enabled": True,
            "auto_sync_enabled_at": datetime.now(timezone.utc)
        }
        
        success = update_user_data(user_email, update_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Automatic progress sync enabled",
                "auto_sync_enabled": True
            }), 200
        else:
            return jsonify({"success": False, "error": "Failed to enable auto-sync"}), 500
        
    except Exception as e:
        print(f"[ERROR] Enable auto-sync failed: {e}")
        return jsonify({"success": False, "error": "Failed to enable auto-sync"}), 500

@app.route("/api/profile/ml-progress-analysis", methods=["GET", "OPTIONS"])
@token_required
def get_ml_progress_analysis():
    """Get ML-based progress analysis and score"""
    try:
        user_email = request.current_user["email"]
        
        user = get_user_by_email(user_email)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        profile_links = user.get("profile_links", {})
        if not profile_links:
            return jsonify({"success": False, "error": "No platform links configured"}), 400
        
        # Extract fresh data using enhanced extractor
        leetcode_data = None
        hackerrank_data = None
        
        if profile_links.get("leetcode"):
            leetcode_data = data_extractor.extract_leetcode_data(profile_links["leetcode"])
        
        if profile_links.get("hackerrank"):
            hackerrank_data = data_extractor.extract_hackerrank_data(profile_links["hackerrank"])
        
        # Get historical data for better analysis
        historical_data = user.get("progress_history", [])
        
        # Generate ML-based analysis
        analysis = progress_analyzer.predict_progress_score(
            leetcode_data, hackerrank_data, historical_data
        )
        
        # Store analysis results
        update_data = {
            "ml_analysis": analysis,
            "ml_analysis_date": datetime.now(timezone.utc),
            "enhanced_platform_data": {
                "leetcode": leetcode_data,
                "hackerrank": hackerrank_data
            }
        }
        
        update_user_data(user_email, update_data)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] ML progress analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Failed to analyze progress"}), 500

@app.route("/api/profile/detailed-extraction", methods=["POST", "OPTIONS"])
@token_required
def get_detailed_extraction():
    """Get detailed data extraction from platforms"""
    try:
        user_email = request.current_user["email"]
        
        user = get_user_by_email(user_email)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        profile_links = user.get("profile_links", {})
        
        # Extract comprehensive data
        extraction_result = data_extractor.extract_combined_data(
            leetcode_username=profile_links.get("leetcode"),
            hackerrank_username=profile_links.get("hackerrank")
        )
        
        # Store detailed extraction
        update_data = {
            "detailed_extraction": extraction_result,
            "last_detailed_extraction": datetime.now(timezone.utc)
        }
        
        update_user_data(user_email, update_data)
        
        return jsonify({
            "success": True,
            "extraction": extraction_result
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Detailed extraction failed: {e}")
        return jsonify({"success": False, "error": "Failed to extract detailed data"}), 500

# -------------------------------
# Authentication Routes
# -------------------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user with proper initialization"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    username = data.get("username", "").strip()
    
    if not email or not password or not username:
        return jsonify({"success": False, "message": "Email, password, and username are required"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long"}), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    if users_collection is not None:
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return jsonify({"success": False, "message": "User with this email already exists"}), 400
        
        # Initialize new user with proper default values for isolation
        user_doc = {
            "email": email,
            "username": username,
            "password": hashed_password,
            "createdAt": datetime.now(timezone.utc),
            "skill_level": "Beginner",
            "problems_solved": 0,
            "streak": 0,
            "learning_style": "Balanced",
            # Assessment state - user-specific
            "assessment_taken": False,
            "predicted_level": None,
            "roadmap": [],
            # Streak and activity - user-specific
            "login_dates": [],
            "login_streak_days": 0,
            "pomodoro_count": 0,
            # Quiz data - user-specific
            "quiz_score": None,
            "quiz_total": None,
            "quiz_percentage": None,
            "last_assessment_date": None
        }
        
        result = users_collection.insert_one(user_doc)
        user_id = result.inserted_id
        print(f"[REGISTER] New user created: {email} with ID: {user_id}")
    else:
        if email in in_memory_users:
            return jsonify({"success": False, "message": "User with this email already exists"}), 400
        
        user_id = f"user_{len(in_memory_users) + 1}"
        in_memory_users[email] = {
            "_id": user_id,
            "email": email,
            "username": username,
            "password": hashed_password,
            "createdAt": datetime.now(timezone.utc),
            "skill_level": "Beginner",
            "problems_solved": 0,
            "streak": 0,
            "learning_style": "Balanced",
            # Assessment state - user-specific
            "assessment_taken": False,
            "predicted_level": None,
            "roadmap": [],
            # Streak and activity - user-specific
            "login_dates": [],
            "login_streak_days": 0,
            "pomodoro_count": 0,
            # Quiz data - user-specific
            "quiz_score": None,
            "quiz_total": None,
            "quiz_percentage": None,
            "last_assessment_date": None
        }
        save_users_to_file()  # Persist to file
        print(f"[REGISTER] New user created in file storage: {email}")
    
    return jsonify({
        "success": True,
        "message": "Registration successful. Please login to continue.",
        "user": {
            "id": str(user_id),
            "email": email,
            "username": username
        }
    }), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login user with proper session isolation"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    
    # Fresh database lookup for this specific user
    user = None
    if users_collection is not None:
        user = users_collection.find_one({"email": email})
    else:
        user = in_memory_users.get(email)
    
    if not user:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401
    
    print(f"[LOGIN] User {email} logging in - Assessment taken: {user.get('assessment_taken', False)}")
    
    # Update login tracking for THIS user only
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    login_dates = user.get("login_dates", [])
    
    # Add today if not present
    if today not in login_dates:
        login_dates.append(today)
        login_dates.sort()
    
    # Calculate login streak for THIS user
    login_streak_days = calculate_login_streak(login_dates)
    
    # Update streak automatically on login using enhanced service
    streak_result = None
    try:
        from streak_service import StreakService
        streak_result = StreakService.trigger_login_streak(users_collection, in_memory_users, email)
        print(f"[LOGIN STREAK] {email}: {streak_result.get('message', 'Updated')}")
    except Exception as e:
        print(f"Failed to update login streak: {e}")
    
    # Update user document with user-specific data
    update_data = {
        "last_login_at": datetime.now(timezone.utc).isoformat(),
        "login_dates": login_dates,
        "login_streak_days": login_streak_days
    }
    
    if users_collection is not None:
        users_collection.update_one({"email": email}, {"$set": update_data})
    else:
        if email in in_memory_users:
            in_memory_users[email].update(update_data)
            save_users_to_file()  # Persist to file
    
    # Generate JWT token with user-specific data
    token = generate_token(user["_id"], email)
    
    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user.get("username", "User"),
            "assessment_taken": user.get("assessment_taken", False),
            "predicted_level": user.get("predicted_level")
        }
    }), 200

@app.route("/api/auth/logout", methods=["POST", "OPTIONS"])
@token_required
def logout():
    """Logout user and clear session"""
    try:
        user_email = request.current_user["email"]
        print(f"[LOGOUT] User {user_email} logging out")
        
        # Note: JWT tokens are stateless, so we can't invalidate them server-side
        # The frontend should remove the token from localStorage
        return jsonify({
            "success": True,
            "message": "Logout successful"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Logout failed: {e}")
        return jsonify({"success": False, "error": "Logout failed"}), 500

@app.route("/api/user/assessment-status", methods=["GET", "OPTIONS"])
@token_required
def get_assessment_status():
    """Get current user's assessment status"""
    try:
        user_email = request.current_user["email"]
        
        # Fresh lookup for THIS user's assessment state
        user = get_user_by_email(user_email)
        
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        assessment_taken = user.get("assessment_taken", False)
        predicted_level = user.get("predicted_level")
        
        print(f"[ASSESSMENT STATUS] User {user_email} - Taken: {assessment_taken}, Level: {predicted_level}")
        
        return jsonify({
            "success": True,
            "assessment_taken": assessment_taken,
            "predicted_level": predicted_level,
            "can_take_quiz": not assessment_taken,
            "can_access_roadmap": assessment_taken and predicted_level is not None,
            "user_email": user_email  # For frontend verification
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Assessment status error for {user_email}: {e}")
        return jsonify({"success": False, "error": "Failed to get assessment status"}), 500

@app.route("/api/user/reset-assessment", methods=["POST", "OPTIONS"])
@token_required
def reset_assessment():
    """Reset assessment for current user (for testing purposes)"""
    try:
        user_email = request.current_user["email"]
        
        print(f"[RESET] Resetting assessment for user: {user_email}")
        
        # Reset assessment data for THIS user only
        reset_data = {
            "assessment_taken": False,
            "predicted_level": None,
            "roadmap": [],
            "quiz_score": None,
            "quiz_total": None,
            "quiz_percentage": None,
            "last_assessment_date": None,
            "updatedAt": datetime.now(timezone.utc)
        }
        
        success = update_user_data(user_email, reset_data)
        
        # Also clear cached topic content for this user
        if topic_content_collection is not None:
            result = topic_content_collection.delete_many({"user_email": user_email})
            print(f"[RESET] Cleared {result.deleted_count} cached topic content entries")
        
        if success:
            print(f"[RESET] Successfully reset assessment for user: {user_email}")
            return jsonify({
                "success": True,
                "message": "Assessment reset successfully",
                "user_email": user_email
            }), 200
        else:
            return jsonify({"success": False, "error": "Failed to reset assessment"}), 500
        
    except Exception as e:
        print(f"[ERROR] Reset assessment error for {user_email}: {e}")
        return jsonify({"success": False, "error": "Failed to reset assessment"}), 500

@app.route("/api/user/clear-content-cache", methods=["POST", "OPTIONS"])
@token_required
def clear_content_cache():
    """Clear cached topic content for current user"""
    try:
        user_email = request.current_user["email"]
        
        if topic_content_collection is not None:
            result = topic_content_collection.delete_many({"user_email": user_email})
            print(f"[CACHE CLEAR] Cleared {result.deleted_count} cached topic content entries for {user_email}")
            
            return jsonify({
                "success": True,
                "message": f"Cleared {result.deleted_count} cached content entries",
                "cleared_count": result.deleted_count
            }), 200
        else:
            return jsonify({
                "success": True,
                "message": "No database cache to clear",
                "cleared_count": 0
            }), 200
        
    except Exception as e:
        print(f"[ERROR] Clear cache error for {user_email}: {e}")
        return jsonify({"success": False, "error": "Failed to clear cache"}), 500

# -------------------------------
# Test Routes for Platform Integration
# -------------------------------
@app.route("/api/test/platforms/<username>", methods=["GET"])
def test_platform_integration(username):
    """Test endpoint to verify platform integration is working"""
    try:
        print(f"[TEST] Testing platform integration for: {username}")
        
        # Test LeetCode
        leetcode_result = coding_tracker.get_leetcode_stats(username)
        print(f"[TEST] LeetCode result: {leetcode_result}")
        
        # Test HackerRank
        hackerrank_result = coding_tracker.get_hackerrank_stats(username)
        print(f"[TEST] HackerRank result: {hackerrank_result}")
        
        # Test the app-level functions
        leetcode_stats = fetch_leetcode_stats(username)
        hackerrank_stats = fetch_hackerrank_stats(username)
        
        return jsonify({
            "success": True,
            "username": username,
            "raw_results": {
                "leetcode": leetcode_result,
                "hackerrank": hackerrank_result
            },
            "processed_stats": {
                "leetcode": leetcode_stats,
                "hackerrank": hackerrank_stats
            },
            "message": "Platform integration test completed"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Platform test failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/test/gemini/<topic>", methods=["GET"])
def test_gemini_integration(topic):
    """Test endpoint to verify Gemini AI integration is working"""
    try:
        print(f"[TEST] Testing Gemini integration for topic: {topic}")
        
        # Test enhanced Gemini service
        content = enhanced_gemini_service.generate_topic_content(topic, "Beginner")
        
        coding_count = len(content.get("coding_questions", []))
        mcq_count = len(content.get("mcq_questions", []))
        
        # Check if Gemini API is configured
        gemini_configured = os.getenv('GEMINI_API_KEY') is not None
        
        return jsonify({
            "success": True,
            "topic": topic,
            "gemini_api_configured": gemini_configured,
            "content_generated": {
                "coding_questions": coding_count,
                "mcq_questions": mcq_count,
                "total_questions": coding_count + mcq_count
            },
            "sample_content": {
                "first_coding_question": content["coding_questions"][0] if content["coding_questions"] else None,
                "first_mcq_question": content["mcq_questions"][0] if content["mcq_questions"] else None
            },
            "message": f"Generated {coding_count} coding + {mcq_count} MCQ questions for {topic}"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Gemini test failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "gemini_api_configured": os.getenv('GEMINI_API_KEY') is not None
        }), 500

@app.route("/api/roadmap/topic/test_generate/<topic_id>", methods=["GET", "OPTIONS"])
@token_required
def test_generate_topic_questions(topic_id):
    """Force-generate a question pack and return the newly created pack JSON"""
    user_email = None
    try:
        # Validate request
        if not topic_id or not topic_id.strip():
            return jsonify({"success": False, "error": "Topic ID is required"}), 400
        
        user_email = request.current_user.get("email")
        if not user_email:
            return jsonify({"success": False, "error": "Authentication required"}), 401
        
        print(f"🔍 Topic test_generate request for topic_id={topic_id} user={user_email}")
        
        # Find topic in roadmap
        user = get_user_by_email(user_email)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        roadmap = user.get("roadmap", [])
        if not roadmap:
            return jsonify({"success": False, "error": "No roadmap found"}), 404
        
        topic_info = None
        for topic in roadmap:
            if str(topic.get("id")) == str(topic_id):
                topic_info = topic
                break
        
        if not topic_info:
            available_topics = [f"{str(t.get('id'))}:{t.get('title', 'Array Basics')}" for t in roadmap[:3]]
            return jsonify({
                "success": False, 
                "error": "Topic not found in roadmap",
                "available_topics": available_topics
            }), 404
        
        print(f"✅ Topic found: {topic_info.get('title')} (order: {topic_info.get('order', 0)})")
        
        # Delete existing question pack
        if question_packs_collection is not None:
            try:
                deleted_count = question_packs_collection.delete_many({
                    "user_email": user_email,
                    "topic_id": str(topic_info.get("id"))
                }).deleted_count
                print(f"⚙️ Deleted {deleted_count} existing question packs")
            except Exception as delete_error:
                print(f"⚠️ Delete error (non-fatal): {delete_error}")
        
        # Generate new question pack
        print(f"⚙️ Force generating new pack for {topic_info.get('title')}")
        content = generate_safe_question_pack(topic_info, user_email)
        
        # Validate generated content
        if not validate_question_pack_structure(content):
            return jsonify({
                "success": False, 
                "error": "Generated question pack failed validation"
            }), 500
        
        # Make JSON-safe
        content = make_json_safe(content)
        
        coding_count = len(content.get("coding_questions", []))
        mcq_count = len(content.get("mcq_questions", []))
        
        print(f"✅ Test generate complete: {coding_count} coding + {mcq_count} MCQ questions")
        
        return jsonify({
            "success": True,
            "message": f"Successfully generated question pack for {topic_info.get('title')}",
            "topic_title": str(topic_info.get("title")),
            "topic_id": str(topic_info.get("id")),
            "coding_questions_count": coding_count,
            "mcq_questions_count": mcq_count,
            "coding_questions": content["coding_questions"],
            "mcq_questions": content["mcq_questions"]
        }), 200
        
    except Exception as e:
        error_msg = f"Test generate failed for {user_email or 'unknown'}: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False, 
            "error": "Internal server error", 
            "details": str(e)
        }), 500

@app.route("/api/debug/check_topic/<topic_id>", methods=["GET", "OPTIONS"])
@token_required
def get_topic_explanation(topic_name):
    """Generate beginner-friendly explanation for any topic"""
    topic_name = topic_name.lower().strip()
    
    explanations = {
        "variables": "Variables are like boxes that store information in your program. You can put different types of data in them like numbers or text. They help you remember and use information later in your code.",
        "loops": "Loops are a way to repeat the same action many times without writing the same code over and over. They save time and make your programs shorter. You use them when you want to do something multiple times.",
        "arrays": "Arrays are like a list that can hold many items of the same type. Think of it as a row of boxes where each box has a number. You can quickly find and change any item by using its position number.",
        "functions": "Functions are like mini-programs inside your main program. They do one specific job and can be used many times. They help organize your code and make it easier to understand and fix.",
        "conditionals": "Conditionals help your program make decisions. They check if something is true or false, then do different things based on the answer. It's like asking a yes or no question in your code.",
        "strings": "Strings are pieces of text that your program can work with. They can be words, sentences, or any characters. You use them to display messages or store text information.",
        "recursion": "Recursion is when a function calls itself to solve a problem. It breaks big problems into smaller, similar pieces. It's like looking in a mirror that reflects another mirror.",
        "sorting": "Sorting puts things in order, like arranging numbers from smallest to biggest. It helps organize data so you can find things faster. Most programs need to sort information at some point.",
        "searching": "Searching helps you find specific information in a collection of data. It's like looking for a particular book in a library. Different search methods work better for different situations."
    }
    
    return explanations.get(topic_name, f"{topic_name.title()} is an important programming concept that helps you write better code. It's a fundamental skill that makes your programs more efficient and easier to understand.")

@app.route("/api/roadmap/topic/<topic_id>/explanation", methods=["GET", "OPTIONS"])
@token_required
def get_topic_simple_explanation(topic_id):
    """Get beginner-friendly explanation for a topic"""
    try:
        user_email = request.current_user["email"]
        user = get_user_by_email(user_email)
        
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Find topic in roadmap
        roadmap = user.get("roadmap", [])
        topic_info = None
        
        for topic in roadmap:
            if str(topic.get("id")) == str(topic_id):
                topic_info = topic
                break
        
        if not topic_info:
            return jsonify({"success": False, "error": "Topic not found"}), 404
        
        topic_title = topic_info.get("title", "")
        explanation = get_topic_explanation(topic_title)
        
        return jsonify({
            "success": True,
            "topic_title": topic_title,
            "explanation": explanation
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Topic explanation failed: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route("/api/debug/check_topic/<topic_id>", methods=["GET", "OPTIONS"])
@token_required
def debug_check_topic(topic_id):
    """Debug endpoint to check topic status"""
    try:
        user_email = request.current_user["email"]
        
        # Find user and roadmap
        user = get_user_by_email(user_email)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        roadmap = user.get("roadmap", [])
        topic_info = None
        
        for topic in roadmap:
            if str(topic.get("id")) == str(topic_id):
                topic_info = topic
                break
        
        if not topic_info:
            return jsonify({
                "topic_exists": False,
                "error": "Topic not found in roadmap",
                "available_topics": [str(t.get("id")) + ":" + t.get("title", "No title") for t in roadmap[:5]]
            }), 404
        
        # Check for question pack
        question_pack = None
        if question_packs_collection is not None:
            question_pack = question_packs_collection.find_one({
                "user_email": user_email,
                "topic_id": str(topic_info.get("id"))
            })
        
        coding_count = 0
        mcq_count = 0
        
        if question_pack:
            coding_count = len(question_pack.get("coding_questions", []))
            mcq_count = len(question_pack.get("mcq_questions", []))
        
        return jsonify({
            "topic_exists": True,
            "topic_title": topic_info.get("title"),
            "topic_id": str(topic_info.get("id")),
            "difficulty": topic_info.get("difficulty"),
            "status": topic_info.get("status"),
            "has_question_pack": question_pack is not None,
            "coding_questions_count": coding_count,
            "mcq_questions_count": mcq_count,
            "gemini_service_available": fixed_gemini_service is not None,
            "mongodb_available": question_packs_collection is not None
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Debug check failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/tutor/explain/<topic_name>", methods=["GET"])
def tutor_explain_topic(topic_name):
    """Public endpoint for topic explanations (no auth required)"""
    try:
        explanation = get_topic_explanation(topic_name)
        return jsonify({
            "success": True,
            "topic": topic_name.title(),
            "explanation": explanation
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------------------
# Streak Routes Integration
# -------------------------------
from streak_system import update_streak_on_login, get_user_streak

# Streak API Endpoints
@app.route("/api/me/streak", methods=["GET", "OPTIONS"])
@token_required
def get_streak():
    """Get current user's streak data"""
    try:
        user_email = request.current_user["email"]
        user = get_user_by_email(user_email)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        streak_data = user.get("streak", {
            "current_streak": 0,
            "total_days": 0,
            "this_week": 0,
            "week_counts": [0, 0, 0, 0, 0, 0, 0],
            "weekly_summary_in_progress": True,
            "last_active_date": None,
            "last_login_date": None
        })
        
        return jsonify({"streak": streak_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/me/streak/refresh", methods=["POST", "OPTIONS"])
@token_required
def refresh_streak():
    """Force streak update for authenticated user"""
    try:
        user_email = request.current_user["email"]
        new_streak = update_streak_on_login(user_email, users_collection or in_memory_users)
        if new_streak:
            return jsonify({"streak": new_streak}), 200
        else:
            return jsonify({"error": "Failed to update streak"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from routes.streaks import streaks_bp
app.register_blueprint(streaks_bp)

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='localhost', port=5000)