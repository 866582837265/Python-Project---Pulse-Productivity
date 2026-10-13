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
from ml_skill_assessment import skill_predictor
from quiz_data import QUIZ_QUESTIONS, ROADMAPS, get_domain_id

# Load environment variables
load_dotenv()

# -------------------------------
# App Setup
# -------------------------------
app = Flask(__name__)
app.secret_key = os.getenv('JWT_SECRET', 'fallback-secret-key')
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# -------------------------------
# MongoDB Connection & Fallback Storage
# -------------------------------
mongo_db, users_collection, mongo_client = None, None, None
in_memory_users = {}  # Fallback storage for testing

try:
    mongodb_uri = os.getenv('MONGODB_URI', '')
    if mongodb_uri and mongodb_uri.strip():
        mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        mongo_db = mongo_client["pulseDB"]
        users_collection = mongo_db["users"]
        
        # Test the connection
        mongo_client.admin.command('ping')
        print("[SUCCESS] Connected to MongoDB")
    else:
        print("[WARNING] No MongoDB URI provided, using in-memory storage for testing")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    print("[WARNING] Falling back to in-memory storage for testing")
    mongo_db, users_collection, mongo_client = None, None, None

# Quiz collections
quiz_responses_collection = None
if mongo_db is not None:
    quiz_responses_collection = mongo_db["quiz_responses"]

# Initialize ML model
skill_predictor.load_model()

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

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

# -------------------------------
# Quiz and ML Routes
# -------------------------------
@app.route("/api/quiz/questions", methods=["GET", "OPTIONS"])
@token_required
def get_quiz_questions():
    """Get quiz questions for domain"""
    domain = request.args.get("domain", "programming").lower()
    
    if domain not in QUIZ_QUESTIONS:
        domain = "programming"  # Default fallback
    
    # Get 10 questions
    questions = QUIZ_QUESTIONS[domain][:10]
    
    # Remove correct answers
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
        "questions": quiz_questions
    }), 200

@app.route("/api/quiz/submit", methods=["POST", "OPTIONS"])
@token_required
def submit_quiz():
    """Submit quiz answers and get ML-predicted skill level with roadmap"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        user_id = request.current_user["user_id"]
        domain = data.get("domain", "programming").lower()
        answers = data.get("answers", [])
        
        if not answers:
            return jsonify({"success": False, "error": "Answers required"}), 400
        
        # Calculate quiz performance
        correct_answers = 0
        total_questions = len(answers)
        total_time = 0
        
        for answer in answers:
            question_id = answer.get("question_id")
            selected_answer = answer.get("selected_answer")
            time_taken = answer.get("time_taken", 30)
            
            # Find correct answer
            for q in QUIZ_QUESTIONS.get(domain, []):
                if q["id"] == question_id:
                    if selected_answer == q["correct"]:
                        correct_answers += 1
                    break
            
            total_time += time_taken
        
        # Calculate metrics
        avg_time = total_time / total_questions if total_questions > 0 else 30
        accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Predict skill level using ML
        domain_id = get_domain_id(domain)
        predicted_level = skill_predictor.predict_skill_level(
            correct_answers, total_questions, avg_time, domain_id
        )
        
        # Get roadmap
        roadmap = ROADMAPS.get(predicted_level, ROADMAPS["beginner"])
        
        # Store in database (optional)
        try:
            if quiz_responses_collection is not None:
                quiz_responses_collection.insert_one({
                    "user_id": user_id,
                    "domain": domain,
                    "correct_answers": correct_answers,
                    "total_questions": total_questions,
                    "predicted_level": predicted_level,
                    "timestamp": datetime.now(timezone.utc)
                })
        except:
            pass  # Don't fail if database storage fails
        
        return jsonify({
            "success": True,
            "domain": domain,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "accuracy": round(accuracy, 1),
            "skill_level": predicted_level,
            "roadmap": roadmap,
            "message": f"Assessment complete! Your {domain} skill level: {predicted_level}"
        }), 200
        
    except Exception as e:
        print(f"Quiz error: {e}")
        return jsonify({"success": False, "error": "Assessment failed"}), 500

@app.route("/api/roadmap/<skill_level>", methods=["GET", "OPTIONS"])
@token_required
def get_roadmap(skill_level):
    """Get roadmap for skill level"""
    if skill_level not in ROADMAPS:
        skill_level = "beginner"  # Default fallback
    
    roadmap = ROADMAPS[skill_level]
    
    return jsonify({
        "success": True,
        "skill_level": skill_level,
        "roadmap": roadmap
    }), 200

# -------------------------------
# Authentication Routes
# -------------------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user"""
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
        
        user_doc = {
            "email": email,
            "username": username,
            "password": hashed_password,
            "createdAt": datetime.now(timezone.utc),
            "skill_level": "Beginner",
            "problems_solved": 0,
            "streak": 0,
            "learning_style": "Balanced"
        }
        
        result = users_collection.insert_one(user_doc)
        user_id = result.inserted_id
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
            "learning_style": "Balanced"
        }
    
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
    """Login user"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    
    user = None
    if users_collection is not None:
        user = users_collection.find_one({"email": email})
    else:
        user = in_memory_users.get(email)
    
    if not user:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401
    
    token = generate_token(user["_id"], email)
    
    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user.get("username", "User")
        }
    }), 200

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, port=5000)