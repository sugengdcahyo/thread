from flask_restx import Namespace, Resource, fields
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.extensions import db

auth_ns = Namespace("auth", description="Authentication related operations")

# Request Model
user_model = auth_ns.model("User", {
    "username": fields.String(required=True, description="Username of the user"),
    "email": fields.String(required=True, description="User email"),
    "password": fields.String(required=True, description="User password")
})

class RegisterUser(Resource):
    @auth_ns.expect(user_model)
    @auth_ns.response(201, "User registered successfully")
    def post(self):
        """Register a new user"""
        data = request.get_json()
        hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")
        new_user = User(username=data["username"], email=data["email"], password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User registered successfully"}, 201

class LoginUser(Resource):
    @auth_ns.expect(user_model, validate=True)
    def post(self):
        """Login a user and return a JWT token"""
        data = request.get_json()
        user = User.query.filter_by(email=data["email"]).first()
        if user and check_password_hash(user.password_hash, data["password"]):
            return {"token": "JWT_TOKEN_EXAMPLE"}, 200
        return {"message": "Invalid credentials"}, 401

# Register routes
auth_ns.add_resource(RegisterUser, "/register")
auth_ns.add_resource(LoginUser, "/login")
