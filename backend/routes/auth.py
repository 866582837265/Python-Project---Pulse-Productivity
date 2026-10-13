# ...existing code...
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from functools import wraps
from bson import ObjectId

# Use central DB initializer
from ..db import get_db, ping_db

auth_bp = Blueprint("auth", __name__)
JWT_SECRET = os.getenv('JWT_SECRET', 'fallback-secret-key')

# In-memory fallback
in_memory_users = {}

# Init users_collection from shared db module (if available)
_db = get_db()
users_collection = None
if _db is not None:
    try:
        users_collection = _db["users"]
        # ensure unique index exists; ignore if already present
        users_collection.create_index("email", unique=True)
        print("✅ Users collection ready (MongoDB)")
    except Exception as e:
        print(f"⚠️ Could not initialize users collection: {e}")
        users_collection = None
else:
    ok, msg = ping_db()
    print(f"⚠️ MongoDB not available: {msg}. Using in-memory users.")

def _to_bytes(value):
    """Ensure stored password is bytes for bcrypt comparison."""
    if value is None:
        return None
    if isinstance(value, bytes):
        return value
    try:
        return value.encode('utf-8')
    except Exception:
        return value

def generate_token(user_id, email):
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

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
        payload = verify_token(token)
        if payload is None:
            return jsonify({'success': False, 'message': 'Token is invalid or expired'}), 401
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        username = data.get("username", "").strip()
        fullName = data.get("fullName", "").strip() or username

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400
        if not username:
            return jsonify({"success": False, "message": "Username is required"}), 400
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters long"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Use MongoDB if available
        if users_collection:
            try:
                existing_user = users_collection.find_one({"email": email})
                if existing_user:
                    return jsonify({"success": False, "message": "User with this email already exists"}), 400

                user_doc = {
                    "email": email,
                    "username": username,
                    "fullName": fullName,
                    "name": username.split()[0] if username else "User",
                    "password": hashed_password,
                    "createdAt": datetime.utcnow(),
                    "skill_level": "Beginner",
                    "problems_solved": 0,
                    "streak": 0,
                    "learning_style": "Balanced"
                }
                result = users_collection.insert_one(user_doc)
                user_id = result.inserted_id
            except Exception as mongo_err:
                print(f"❌ MongoDB error during register: {mongo_err}")
                return jsonify({"success": False, "message": f"Database error: {str(mongo_err)}"}), 500
        else:
            # In-memory fallback
            if email in in_memory_users:
                return jsonify({"success": False, "message": "User with this email already exists"}), 400
            user_id = f"user_{len(in_memory_users) + 1}"
            in_memory_users[email] = {
                "_id": user_id,
                "email": email,
                "username": username,
                "fullName": fullName,
                "name": username.split()[0] if username else "User",
                "password": hashed_password,
                "createdAt": datetime.utcnow(),
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
                "username": username,
                "fullName": fullName
            }
        }), 201

    except Exception as e:
        print(f"❌ Registration error: {e}")
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        user = None
        if users_collection:
            try:
                user = users_collection.find_one({"email": email})
            except Exception as mongo_err:
                print(f"❌ MongoDB search error: {mongo_err}")
                return jsonify({"success": False, "message": f"Database error: {str(mongo_err)}"}), 500
        else:
            user = in_memory_users.get(email)

        if not user:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        stored_pw = _to_bytes(user.get("password"))
        if not stored_pw or not bcrypt.checkpw(password.encode('utf-8'), stored_pw):
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        token = generate_token(user["_id"], email)
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user.get("username", "User"),
                "fullName": user.get("fullName", user.get("username", "User"))
            }
        }), 200

    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"success": False, "message": f"Login failed: {str(e)}"}), 500

@auth_bp.route("/logout", methods=["POST"])
def logout():
    try:
        return jsonify({"success": True, "message": "Logged out successfully"}), 200
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({"success": False, "message": "Logout failed"}), 500

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user():
    try:
        user_email = request.current_user["email"]
        if users_collection:
            user = users_collection.find_one({"email": user_email})
        else:
            user = in_memory_users.get(user_email)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        return jsonify({
            "success": True,
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user.get("username", "User"),
                "fullName": user.get("fullName", user.get("username", "User"))
            }
        }), 200

    except Exception as e:
        print(f"Get current user error: {e}")
        return jsonify({"success": False, "message": "Failed to retrieve user"}), 500
# ...existing code...