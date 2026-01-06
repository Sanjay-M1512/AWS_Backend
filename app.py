from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# MongoDB connection
client = MongoClient(app.config["MONGO_URI"])
db = client.aws_backend
users = db.users

# JWT setup
jwt = JWTManager(app)


# ===============================
# HEALTH CHECK
# ===============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "AWS Mongo Backend Running"}), 200


# ===============================
# REGISTER API (USERNAME + EMAIL + PASSWORD)
# ===============================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"msg": "Username, email and password required"}), 400

    if users.find_one({"email": email}):
        return jsonify({"msg": "User already exists"}), 409

    users.insert_one({
        "username": username,
        "email": email,
        "password": password   # ❌ plain text (as requested)
    })

    return jsonify({"msg": "User registered successfully"}), 201


# ===============================
# LOGIN API (EMAIL + PASSWORD)
# ===============================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = users.find_one({
        "email": email,
        "password": password
    })

    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401

    # Store email in JWT instead of user id
    access_token = create_access_token(identity=user["email"])

    return jsonify({
        "msg": "Login successful",
        "access_token": access_token
    }), 200


# ===============================
# PROTECTED ROUTE (RETURN EMAIL + USERNAME)
# ===============================
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    email = get_jwt_identity()

    user = users.find_one({"email": email}, {"_id": 0, "password": 0})

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({
        "msg": "Profile fetched successfully",
        "user": {
            "username": user["username"],
            "email": user["email"]
        }
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
