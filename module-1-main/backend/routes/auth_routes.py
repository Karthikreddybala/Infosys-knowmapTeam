"""
Auth routes — JWT-based register & login
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me      (protected)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from backend.extensions import db, bcrypt
from backend.models import User, UserProfile

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ── REGISTER ──────────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return jsonify({
            "message": "Fusion Graph Registration API. Use POST to register a new operative.",
            "endpoint": "/api/auth/register",
            "method_required": "POST",
            "required_fields": ["username", "email", "password"]
        }), 200

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email    = (data.get("email")    or "").strip() or None
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already exists"}), 409
    if email and User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=username, email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    # Automatically provision AI_cybersecurity UserProfile per milestone requirements
    profile = UserProfile(user_id=user.id)
    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "Account created successfully", "user": user.to_dict()}), 201


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return jsonify({
            "message": "Fusion Graph Authentication API. Use POST to authenticate.",
            "endpoint": "/api/auth/login",
            "method_required": "POST",
            "required_fields": ["username/email", "password"]
        }), 200

    data = request.get_json(silent=True) or {}
    identifier = (data.get("username") or data.get("email") or "").strip()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"error": "username/email and password are required"}), 400

    # Accept login by username OR email
    if "@" in identifier:
        user = User.query.filter_by(email=identifier).first()
    else:
        user = User.query.filter_by(username=identifier).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username/email or password"}), 401

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    }), 200


# ── REFRESH TOKEN ─────────────────────────────────────────────────────────────
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200


# ── ME (current user) ─────────────────────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200

# ── PROFILE AND INTERESTS ─────────────────────────────────────────────────────
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    import json
    user_id = int(get_jwt_identity())
    profile = db.session.get(UserProfile, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return jsonify(profile.to_dict()), 200

@auth_bp.route("/profile/interests", methods=["POST"])
@jwt_required()
def update_interests():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    interests = data.get("interests", [])
    
    profile = db.session.get(UserProfile, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
        
    profile.interests = ",".join(interests)
    db.session.commit()
    return jsonify({"message": "Interests saved", "profile": profile.to_dict()}), 200

@auth_bp.route("/profile/saved_graphs", methods=["POST"])
@jwt_required()
def update_saved_graphs():
    import json
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    graphs = data.get("saved_graphs", [])
    
    profile = db.session.get(UserProfile, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
        
    profile.saved_graphs = json.dumps(graphs)
    db.session.commit()
    return jsonify({"message": "Saved graphs updated", "profile": profile.to_dict()}), 200
